"""Gold / Forex news bot.

Reads a set of RSS feeds, keeps only the items that mention gold, the Fed,
inflation or the US jobs data, and pushes the new ones to Telegram.

Runs anywhere, but it is meant to be driven by the GitHub Actions workflow in
.github/workflows/news-bot.yml (cron every 15 minutes).

Configuration comes from the environment:
    TELEGRAM_BOT_TOKEN  (required)  token from @BotFather
    TELEGRAM_CHAT_ID    (required)  your chat id from @userinfobot
    FEEDS_FILE          feeds/keywords config (default: feeds.yml next to bot.py)
    STATE_FILE          dedupe state (default: state/seen.json)
    MAX_AGE_HOURS       ignore items older than this (default: 6)
    MAX_ITEMS_PER_RUN   flood guard (default: 10)
    STATE_TTL_DAYS      how long an item stays in the seen list (default: 7)
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import feedparser
import requests
import yaml

from localtime import TZ_LABEL, format_datetime

LOGGER = logging.getLogger("gold_news_bot")

DEFAULT_FEEDS_FILE = Path(__file__).with_name("feeds.yml")
DEFAULT_STATE_FILE = Path(__file__).parent / "state" / "seen.json"

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
USER_AGENT = "gold-news-bot/1.0"
REQUEST_TIMEOUT = 20

# Query parameters that only carry tracking noise; dropping them keeps the
# dedupe key stable when a source re-publishes the same link.
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "oc",
    "ved",
}


@dataclass(frozen=True)
class NewsItem:
    """One feed entry, already normalised."""

    uid: str
    title: str
    link: str
    source: str
    published: datetime | None
    summary: str = ""

    @property
    def match_text(self) -> str:
        return f"{self.title}\n{self.summary}".lower()

    def as_message(self) -> str:
        parts = [f"\U0001f7e1 <b>{html.escape(self.title)}</b>"]
        meta = html.escape(self.source)
        if self.published:
            meta += f" · {format_datetime(self.published)} {TZ_LABEL}"
        parts.append(meta)
        parts.append(html.escape(self.link))
        return "\n".join(parts)


# --------------------------------------------------------------------------- #
# configuration
# --------------------------------------------------------------------------- #
def load_config(path: Path) -> tuple[list[dict], list[str]]:
    """Return (feeds, keywords) from the YAML config."""
    with open(path, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    feeds = [f for f in raw.get("feeds", []) if f.get("url")]
    keywords = [str(k).strip().lower() for k in raw.get("keywords", []) if str(k).strip()]
    if not feeds:
        raise ValueError(f"no feeds configured in {path}")
    if not keywords:
        raise ValueError(f"no keywords configured in {path}")
    return feeds, keywords


# --------------------------------------------------------------------------- #
# fetching / normalising
# --------------------------------------------------------------------------- #
def canonical_link(link: str) -> str:
    """Strip tracking parameters and fragments so the same story hashes equal."""
    if not link:
        return ""
    parts = urlsplit(link.strip())
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k.lower() not in TRACKING_PARAMS]
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), urlencode(query), ""))


def item_uid(entry: dict, link: str, title: str) -> str:
    """Stable id for an entry: prefer the feed guid, fall back to link/title."""
    basis = (entry.get("id") or entry.get("guid") or canonical_link(link) or title).strip().lower()
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:32]


def entry_published(entry: dict) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            return datetime(*parsed[:6], tzinfo=timezone.utc)
    return None


def fetch_feed(name: str, url: str) -> list[NewsItem]:
    """Download and parse one feed. A broken source never breaks the run."""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
    except requests.RequestException as exc:
        LOGGER.warning("feed %s failed: %s", name, exc)
        return []

    parsed = feedparser.parse(response.content)
    if parsed.bozo and not parsed.entries:
        LOGGER.warning("feed %s returned no usable entries (%s)", name, parsed.get("bozo_exception"))
        return []

    items: list[NewsItem] = []
    for entry in parsed.entries:
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        if not title or not link:
            continue
        items.append(
            NewsItem(
                uid=item_uid(entry, link, title),
                title=title,
                link=link,
                source=name,
                published=entry_published(entry),
                summary=(entry.get("summary") or "").strip(),
            )
        )
    LOGGER.info("feed %s: %d entries", name, len(items))
    return items


def collect_items(feeds: Sequence[dict]) -> list[NewsItem]:
    items: list[NewsItem] = []
    for feed in feeds:
        items.extend(fetch_feed(feed.get("name", feed["url"]), feed["url"]))
    return items


# --------------------------------------------------------------------------- #
# filtering
# --------------------------------------------------------------------------- #
def matches_keywords(item: NewsItem, keywords: Iterable[str]) -> bool:
    text = item.match_text
    return any(keyword in text for keyword in keywords)


def is_recent(item: NewsItem, max_age_hours: int, now: datetime | None = None) -> bool:
    if max_age_hours <= 0:
        return True
    if item.published is None:
        # No date on the entry: let it through, dedupe still protects us.
        return True
    now = now or datetime.now(timezone.utc)
    return item.published >= now - timedelta(hours=max_age_hours)


def select_new(
    items: Sequence[NewsItem],
    keywords: Sequence[str],
    seen: dict[str, str],
    max_age_hours: int,
    max_items: int,
    now: datetime | None = None,
) -> list[NewsItem]:
    """Keyword match + age window + dedupe, newest first, capped."""
    picked: dict[str, NewsItem] = {}
    for item in items:
        if item.uid in seen or item.uid in picked:
            continue
        if not matches_keywords(item, keywords):
            continue
        if not is_recent(item, max_age_hours, now=now):
            continue
        picked[item.uid] = item

    ordered = sorted(
        picked.values(),
        key=lambda i: i.published or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return ordered[:max_items] if max_items > 0 else ordered


# --------------------------------------------------------------------------- #
# state
# --------------------------------------------------------------------------- #
def load_state(path: Path) -> dict[str, str]:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    seen = data.get("seen", {})
    return seen if isinstance(seen, dict) else {}


def prune_state(seen: dict[str, str], ttl_days: int, now: datetime | None = None) -> dict[str, str]:
    if ttl_days <= 0:
        return dict(seen)
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=ttl_days)
    kept: dict[str, str] = {}
    for uid, stamp in seen.items():
        try:
            when = datetime.fromisoformat(stamp)
        except (TypeError, ValueError):
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        if when >= cutoff:
            kept[uid] = stamp
    return kept


def save_state(path: Path, seen: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"updated_at": datetime.now(timezone.utc).isoformat(), "seen": seen}
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
    tmp.replace(path)


# --------------------------------------------------------------------------- #
# telegram
# --------------------------------------------------------------------------- #
def send_message(token: str, chat_id: str, text: str) -> bool:
    try:
        response = requests.post(
            TELEGRAM_API.format(token=token),
            timeout=REQUEST_TIMEOUT,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
        )
    except requests.RequestException as exc:
        LOGGER.error("telegram request failed: %s", exc)
        return False

    if response.status_code == 429:
        retry_after = int(response.json().get("parameters", {}).get("retry_after", 5))
        LOGGER.warning("rate limited by telegram, sleeping %ss", retry_after)
        time.sleep(retry_after)
        return send_message(token, chat_id, text)

    if not response.ok:
        LOGGER.error("telegram rejected the message: %s %s", response.status_code, response.text[:300])
        return False
    return True


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #
def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        LOGGER.warning("%s is not a number, using %s", name, default)
        return default


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send filtered gold/forex headlines to Telegram.")
    parser.add_argument("--dry-run", action="store_true", help="print what would be sent, do not call Telegram")
    parser.add_argument("--feeds", type=Path, default=None, help="path to feeds.yml")
    parser.add_argument("--state", type=Path, default=None, help="path to the dedupe state file")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args(argv)

    feeds_file = args.feeds or Path(os.getenv("FEEDS_FILE", DEFAULT_FEEDS_FILE))
    state_file = args.state or Path(os.getenv("STATE_FILE", DEFAULT_STATE_FILE))
    max_age_hours = env_int("MAX_AGE_HOURS", 6)
    max_items = env_int("MAX_ITEMS_PER_RUN", 10)
    ttl_days = env_int("STATE_TTL_DAYS", 7)

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not args.dry_run and not (token and chat_id):
        LOGGER.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (or use --dry-run)")
        return 2

    feeds, keywords = load_config(feeds_file)
    seen = prune_state(load_state(state_file), ttl_days)
    LOGGER.info("state: %d remembered items", len(seen))

    items = collect_items(feeds)
    fresh = select_new(items, keywords, seen, max_age_hours, max_items)
    LOGGER.info("%d entries fetched, %d new matches", len(items), len(fresh))

    now_iso = datetime.now(timezone.utc).isoformat()
    sent = 0
    for item in fresh:
        if args.dry_run:
            print(item.as_message(), end="\n\n")
            seen[item.uid] = now_iso
            sent += 1
            continue
        if send_message(token, chat_id, item.as_message()):
            seen[item.uid] = now_iso
            sent += 1
            time.sleep(1)  # stay under Telegram's ~30 msg/s limit with room to spare
        else:
            LOGGER.warning("not marking %s as seen, will retry next run", item.title[:60])

    save_state(state_file, seen)
    LOGGER.info("sent %d message(s)", sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
