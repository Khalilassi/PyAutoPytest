"""Display timezone for every message the bots send.

One place decides how a moment is rendered, so headlines, alerts and the daily
digest can never disagree about what time it is.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

try:  # tzdata is present on the Actions runner; the fallback keeps local runs working
    from zoneinfo import ZoneInfo

    def _zone(name: str):
        return ZoneInfo(name)
except ImportError:  # pragma: no cover - only on exotic builds
    def _zone(name: str):
        raise KeyError(name)

DEFAULT_TZ_NAME = "Asia/Riyadh"
RIYADH_FALLBACK = timezone(timedelta(hours=3), "الرياض")
TZ_LABEL = "بتوقيت الرياض"

ARABIC_DAYS = {
    0: "الاثنين",
    1: "الثلاثاء",
    2: "الأربعاء",
    3: "الخميس",
    4: "الجمعة",
    5: "السبت",
    6: "الأحد",
}

ARABIC_MONTHS = {
    1: "يناير",
    2: "فبراير",
    3: "مارس",
    4: "أبريل",
    5: "مايو",
    6: "يونيو",
    7: "يوليو",
    8: "أغسطس",
    9: "سبتمبر",
    10: "أكتوبر",
    11: "نوفمبر",
    12: "ديسمبر",
}


def display_tz():
    """The timezone every message is rendered in (DISPLAY_TZ overrides it)."""
    name = os.getenv("DISPLAY_TZ", DEFAULT_TZ_NAME).strip() or DEFAULT_TZ_NAME
    try:
        return _zone(name)
    except Exception:
        return RIYADH_FALLBACK


def to_local(moment: datetime) -> datetime:
    """Move an aware datetime into the display timezone."""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(display_tz())


def format_time(moment: datetime) -> str:
    """15:30"""
    return to_local(moment).strftime("%H:%M")


def format_datetime(moment: datetime) -> str:
    """2026-08-20 15:30"""
    return to_local(moment).strftime("%Y-%m-%d %H:%M")


def format_day(moment: datetime) -> str:
    """الخميس 21 أغسطس"""
    local = to_local(moment)
    return f"{ARABIC_DAYS[local.weekday()]} {local.day} {ARABIC_MONTHS[local.month]}"
