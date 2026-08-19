"""Economic calendar alerts.

Looks ahead instead of behind: pulls this week's economic calendar, keeps the
high-impact releases for the currencies you care about, and sends a heads-up
roughly half an hour before each one — with the forecast, the previous print,
and the instruments that release actually moves.

It deliberately does NOT tell you what to trade or in which direction. Nobody
knows where price goes after a release until it is out; what is knowable in
advance is *when* it lands, *what* is expected, and *which* instruments react.

Environment (shares the Telegram credentials with bot.py):
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID   required
    CALENDAR_FILE       config (default: calendar.yml next to this file)
    CALENDAR_STATE_FILE dedupe state (default: state/calendar.json)
    LEAD_MINUTES        override the config lead time
"""

from __future__ import annotations

import argparse
import hashlib
import html
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

import requests
import yaml

from bot import REQUEST_TIMEOUT, USER_AGENT, load_state, prune_state, save_state, send_message

LOGGER = logging.getLogger("calendar_bot")

DEFAULT_CALENDAR_FILE = Path(__file__).with_name("calendar.yml")
DEFAULT_STATE_FILE = Path("state/calendar.json")

FLAGS = {
    "USD": "\U0001f1fa\U0001f1f8",
    "EUR": "\U0001f1ea\U0001f1fa",
    "GBP": "\U0001f1ec\U0001f1e7",
    "JPY": "\U0001f1ef\U0001f1f5",
    "CHF": "\U0001f1e8\U0001f1ed",
    "CAD": "\U0001f1e8\U0001f1e6",
    "AUD": "\U0001f1e6\U0001f1fa",
    "NZD": "\U0001f1f3\U0001f1ff",
    "CNY": "\U0001f1e8\U0001f1f3",
}


@dataclass(frozen=True)
class Event:
    title: str
    currency: str
    when: datetime
    impact: str
    forecast: str = ""
    previous: str = ""

    @property
    def uid(self) -> str:
        basis = f"{self.currency}|{self.title}|{self.when.isoformat()}".lower()
        return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:32]


def load_config(path: Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    if not raw.get("source_url"):
        raise ValueError(f"source_url missing in {path}")
    return raw


def parse_events(payload: list[dict]) -> list[Event]:
    """Turn the calendar JSON into events, skipping anything undated."""
    events: list[Event] = []
    for row in payload:
        title = (row.get("title") or "").strip()
        stamp = (row.get("date") or "").strip()
        if not title or not stamp:
            continue
        try:
            when = datetime.fromisoformat(stamp)
        except ValueError:
            LOGGER.debug("unparsable date %r on %s", stamp, title)
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        events.append(
            Event(
                title=title,
                currency=(row.get("country") or "").strip().upper(),
                when=when.astimezone(timezone.utc),
                impact=(row.get("impact") or "").strip(),
                forecast=(row.get("forecast") or "").strip(),
                previous=(row.get("previous") or "").strip(),
            )
        )
    return events


def fetch_events(url: str) -> list[Event]:
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        LOGGER.error("calendar fetch failed: %s", exc)
        return []
    if not isinstance(payload, list):
        LOGGER.error("calendar returned %s, expected a list", type(payload).__name__)
        return []
    events = parse_events(payload)
    LOGGER.info("calendar: %d events this week", len(events))
    return events


def due_soon(
    events: Sequence[Event],
    impacts: Sequence[str],
    currencies: Sequence[str],
    lead_minutes: int,
    now: datetime | None = None,
) -> list[Event]:
    """Events that are about to land inside the lead window, soonest first."""
    now = now or datetime.now(timezone.utc)
    horizon = now + timedelta(minutes=lead_minutes)
    wanted_impacts = {i.lower() for i in impacts}
    wanted_currencies = {c.upper() for c in currencies}

    picked = [
        event
        for event in events
        if now <= event.when <= horizon
        and event.impact.lower() in wanted_impacts
        and event.currency in wanted_currencies
    ]
    return sorted(picked, key=lambda e: e.when)


def build_message(event: Event, config: dict, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    minutes = max(0, round((event.when - now).total_seconds() / 60))
    flag = FLAGS.get(event.currency, "\U0001f4c5")
    instruments = config.get("instruments", {}).get(event.currency, [])

    lines = [
        f"⏰ <b>بعد ~{minutes} دقيقة</b>",
        f"{flag} {html.escape(event.currency)} · <b>{html.escape(event.title)}</b> · تأثير عالي",
        f"\U0001f552 {event.when.strftime('%H:%M')} UTC",
    ]

    if event.forecast or event.previous:
        forecast = html.escape(event.forecast) if event.forecast else "—"
        previous = html.escape(event.previous) if event.previous else "—"
        lines.append(f"المتوقع: <b>{forecast}</b> | السابق: {previous}")

    if instruments:
        lines.append("الأدوات الأكتر تأثرًا: " + " · ".join(html.escape(i) for i in instruments))

    if is_gold_mover(event, config):
        lines.append("\U0001f7e1 ده من الأخبار اللي بتحرّك الذهب بقوة.")

    lines.append(
        "⚠️ لحظة الصدور: السبريد بيتوسع والتنفيذ بينزلق (slippage)، "
        "والسكالبينج في أول 1–5 دقايق أعلى مخاطرة بكتير."
    )
    lines.append("<i>تنبيه بموعد خبر — مش توصية بيع أو شراء.</i>")
    return "\n".join(lines)


def is_gold_mover(event: Event, config: dict) -> bool:
    title = event.title.lower()
    return any(marker.lower() in title for marker in config.get("gold_movers", []))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alert before high-impact economic releases.")
    parser.add_argument("--dry-run", action="store_true", help="print instead of sending")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--state", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args(argv)

    config_file = args.config or Path(os.getenv("CALENDAR_FILE", DEFAULT_CALENDAR_FILE))
    state_file = args.state or Path(os.getenv("CALENDAR_STATE_FILE", DEFAULT_STATE_FILE))

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not args.dry_run and not (token and chat_id):
        LOGGER.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (or use --dry-run)")
        return 2

    config = load_config(config_file)
    lead_minutes = int(os.getenv("LEAD_MINUTES", config.get("lead_minutes", 35)))

    seen = prune_state(load_state(state_file), ttl_days=7)
    events = fetch_events(config["source_url"])

    now = datetime.now(timezone.utc)
    upcoming = [e for e in due_soon(events, config.get("impacts", ["High"]), config.get("currencies", ["USD"]), lead_minutes, now=now) if e.uid not in seen]
    LOGGER.info("%d event(s) due within %d minutes", len(upcoming), lead_minutes)

    now_iso = now.isoformat()
    for event in upcoming:
        text = build_message(event, config, now=now)
        if args.dry_run:
            print(text, end="\n\n")
            seen[event.uid] = now_iso
            continue
        if send_message(token, chat_id, text):
            seen[event.uid] = now_iso
            time.sleep(1)
        else:
            LOGGER.warning("not marking %s as alerted, will retry next run", event.title[:60])

    save_state(state_file, seen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
