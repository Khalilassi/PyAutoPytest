"""Technical state cards, sent to Telegram as images.

For each configured instrument: download candles, compute the indicators, draw a
card, and send it with a caption saying how old the reading is and — when the
rules produce one — a button opening a pre-filled order ticket.

What this is not: a signal service. Nothing here predicts direction. The card
shows what the indicators read right now, the ticket applies the rules printed
on the card, and both carry the timestamp of the candle they came from so a
stale reading is obvious instead of silently looking fresh.

Environment (shares the Telegram credentials with bot.py):
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID   required
    SIGNALS_FILE        config (default: signals.yml next to this file)
    SIGNALS_STATE_FILE  dedupe state (default: state/signals.json)
    CARD_DIR            where PNGs are written (default: cards/)
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import yaml

import analysis
from analysis import Snapshot, Ticket
from bot import load_state, save_state, send_photo
from card import render_card
from localtime import TZ_LABEL, format_datetime
from market_data import MarketDataError, fetch_first_available

LOGGER = logging.getLogger("signals_bot")

DEFAULT_CONFIG = Path(__file__).with_name("signals.yml")
DEFAULT_STATE_FILE = Path("state/signals.json")
DEFAULT_CARD_DIR = Path("cards")

# Futures trade at a premium to spot, so a card fed by one must say so — the
# number is right for the instrument and wrong for the platform you trade on.
FUTURES_SOURCES = {"GC=F", "SI=F", "CL=F", "NQ=F", "ES=F"}

SIDE_LABELS = {"BUY": "شراء", "SELL": "بيع", "WAIT": "انتظار"}
TREND_LABELS = {"UP": "صاعد", "DOWN": "هابط", "FLAT": "عرضي", "UNKNOWN": "غير محدد"}


def load_config(path: Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not config.get("instruments"):
        raise ValueError(f"no instruments configured in {path}")
    return config


def build_caption(snapshot: Snapshot, ticket: Ticket | None, now: datetime) -> str:
    """The Arabic half of the message — the card itself stays English."""
    age = analysis.age_text(snapshot.candle_time, now)
    lines = [
        f"<b>{snapshot.name}</b> · {snapshot.price(snapshot.last)} ({snapshot.change_pct:+.2f}%)",
        f"الاتجاه: {TREND_LABELS.get(snapshot.trend, snapshot.trend)}"
        + (f" · RSI {snapshot.rsi:.0f}" if snapshot.rsi is not None else ""),
        f"\U0001f552 آخر شمعة: {format_datetime(snapshot.candle_time)} {TZ_LABEL} — <b>{age}</b>",
        f"\U0001f4e1 المصدر: <code>{snapshot.source}</code>",
    ]

    if snapshot.source in FUTURES_SOURCES:
        lines.append(
            "\u26a0\ufe0f ده سعر <b>عقود آجلة</b> مش سبوت — بيفرق عن منصتك بعشرات الدولارات."
        )

    if ticket:
        lines += [
            "",
            f"<b>تكيت {SIDE_LABELS[ticket.side]}</b> (حسب القواعد المكتوبة على الكارت)",
            f"دخول {snapshot.price(ticket.entry)} · وقف {snapshot.price(ticket.stop)} · هدف {snapshot.price(ticket.target)}",
            f"لوت مقترح {ticket.lot:g} على مخاطرة ${ticket.risk_amount:g}",
        ]
    else:
        lines += ["", "القواعد بتقول <b>استنى</b> دلوقتي — مفيش تكيت."]

    lines += ["", "<i>حالة فنية محسوبة من الأسعار — مش توصية بيع أو شراء.</i>"]
    return "\n".join(lines)


def state_fingerprint(snapshot: Snapshot) -> str:
    """What must change before the same instrument is worth re-sending."""
    return f"{snapshot.source}|{snapshot.trend}|{snapshot.bias}|{snapshot.candle_time.isoformat()}"


def process_instrument(instrument: dict, config: dict, now: datetime, card_dir: Path):
    """Returns (snapshot, ticket, card path) or None when data is unusable."""
    sources = instrument.get("sources") or [instrument["symbol"]]
    name = instrument.get("name") or sources[0]
    try:
        source, candles = fetch_first_available(
            sources,
            interval=config.get("interval", "15m"),
            lookback=config.get("lookback", "1mo"),
        )
    except MarketDataError as exc:
        LOGGER.warning("skipping %s: %s", name, exc)
        return None

    if source != sources[0]:
        LOGGER.warning("%s is on the fallback source %s, prices will differ from %s", name, source, sources[0])

    rules = config.get("rules", {})
    snapshot = analysis.build_snapshot(candles, name, int(instrument.get("digits", 2)), rules, source=source)
    ticket = analysis.build_ticket(
        snapshot, rules, config.get("risk", {}), float(instrument.get("value_per_point", 0))
    )

    card_path = render_card(
        candles,
        snapshot,
        ticket,
        card_dir / f"{name}.png",
        rules,
        analysis.age_minutes(snapshot.candle_time, now),
    )
    return snapshot, ticket, card_path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send technical state cards to Telegram.")
    parser.add_argument("--dry-run", action="store_true", help="render the cards but do not send them")
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--state", type=Path, default=None)
    parser.add_argument("--card-dir", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = parse_args(argv)

    config_file = args.config or Path(os.getenv("SIGNALS_FILE", DEFAULT_CONFIG))
    state_file = args.state or Path(os.getenv("SIGNALS_STATE_FILE", DEFAULT_STATE_FILE))
    card_dir = args.card_dir or Path(os.getenv("CARD_DIR", DEFAULT_CARD_DIR))

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not args.dry_run and not (token and chat_id):
        LOGGER.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (or use --dry-run)")
        return 2

    config = load_config(config_file)
    # one entry per instrument, so this never grows — no pruning needed, and the
    # value is a fingerprint rather than a timestamp
    seen = load_state(state_file)
    only_on_change = bool(config.get("send_only_on_change", False))
    base_url = (config.get("ticket_base_url") or "").strip()

    now = datetime.now(timezone.utc)
    sent = 0

    for instrument in config["instruments"]:
        result = process_instrument(instrument, config, now, card_dir)
        if result is None:
            continue
        snapshot, ticket, card_path = result

        key = f"card-{snapshot.name}"
        fingerprint = state_fingerprint(snapshot)
        if only_on_change and seen.get(key) == fingerprint:
            LOGGER.info("%s unchanged, not re-sending", snapshot.name)
            continue

        caption = build_caption(snapshot, ticket, now)
        buttons = None
        if ticket:
            url = analysis.ticket_url(base_url, snapshot, ticket)
            if url:
                buttons = [[{"text": "\U0001f4dd افتح تكيت الصفقة", "url": url}]]

        if args.dry_run:
            print(f"--- {snapshot.name} -> {card_path}")
            print(caption)
            print()
            seen[key] = fingerprint
            sent += 1
            continue

        if send_photo(token, chat_id, card_path, caption, buttons):
            seen[key] = fingerprint
            sent += 1
            time.sleep(1)
        else:
            LOGGER.warning("card for %s not sent, will retry next run", snapshot.name)

    save_state(state_file, seen)
    LOGGER.info("sent %d card(s)", sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
