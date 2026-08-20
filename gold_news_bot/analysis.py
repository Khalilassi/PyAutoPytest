"""Turning candles into a readable technical state, and into a trade ticket.

The rules are deliberately few and printed on the card itself, so what you see
can be checked against your own chart. This is a rules engine, not a forecast:
it says what the indicators are doing right now and what a ticket built from
those rules would look like. Whether to send it is your call.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlencode

import indicators
from indicators import Candle

WAIT = "WAIT"
BUY = "BUY"
SELL = "SELL"


@dataclass(frozen=True)
class Snapshot:
    name: str
    digits: int
    last: float
    change_pct: float
    rsi: float | None
    ema_fast: float | None
    ema_slow: float | None
    macd_hist: float | None
    atr: float | None
    swing_high: float | None
    swing_low: float | None
    candle_time: datetime
    trend: str
    bias: str

    def price(self, value: float | None) -> str:
        return "—" if value is None else f"{value:,.{self.digits}f}"


@dataclass(frozen=True)
class Ticket:
    side: str
    entry: float
    stop: float
    target: float
    lot: float
    risk_amount: float


def build_snapshot(candles: list[Candle], name: str, digits: int, rules: dict) -> Snapshot:
    """Read the current technical state off the candles."""
    values = indicators.closes(candles)
    last = values[-1]
    previous = values[-2] if len(values) > 1 else last

    ema_fast = indicators.ema(values, rules.get("fast_ema", 50))
    ema_slow = indicators.ema(values, rules.get("slow_ema", 200))
    rsi_value = indicators.rsi(values, rules.get("rsi_period", 14))
    macd_value = indicators.macd(values)
    atr_value = indicators.atr(candles, rules.get("atr_period", 14))
    levels = indicators.swing_levels(candles)

    trend = classify_trend(ema_fast, ema_slow)
    bias = classify_bias(trend, rsi_value, rules)

    return Snapshot(
        name=name,
        digits=digits,
        last=last,
        change_pct=((last - previous) / previous * 100) if previous else 0.0,
        rsi=rsi_value,
        ema_fast=ema_fast,
        ema_slow=ema_slow,
        macd_hist=macd_value[2] if macd_value else None,
        atr=atr_value,
        swing_high=levels[0] if levels else None,
        swing_low=levels[1] if levels else None,
        candle_time=candles[-1].when,
        trend=trend,
        bias=bias,
    )


def classify_trend(ema_fast: float | None, ema_slow: float | None) -> str:
    if ema_fast is None or ema_slow is None:
        return "UNKNOWN"
    if ema_fast > ema_slow:
        return "UP"
    if ema_fast < ema_slow:
        return "DOWN"
    return "FLAT"


def classify_bias(trend: str, rsi_value: float | None, rules: dict) -> str:
    """Trend decides the side; RSI vetoes entering into an exhausted move."""
    if rsi_value is None or trend not in ("UP", "DOWN"):
        return WAIT
    if trend == "UP":
        return WAIT if rsi_value >= rules.get("rsi_overbought", 70) else BUY
    return WAIT if rsi_value <= rules.get("rsi_oversold", 30) else SELL


def build_ticket(snapshot: Snapshot, rules: dict, risk: dict, value_per_point: float) -> Ticket | None:
    """A ticket from the stated rules, or None when the rules say wait."""
    if snapshot.bias == WAIT or snapshot.atr in (None, 0):
        return None

    stop_distance = snapshot.atr * rules.get("stop_atr_multiple", 1.5)
    if stop_distance <= 0:
        return None
    reward = stop_distance * rules.get("reward_risk", 2.0)

    if snapshot.bias == BUY:
        stop, target = snapshot.last - stop_distance, snapshot.last + reward
    else:
        stop, target = snapshot.last + stop_distance, snapshot.last - reward

    risk_amount = float(risk.get("account_balance", 0)) * float(risk.get("risk_percent", 0)) / 100
    lot = 0.0
    if risk_amount > 0 and value_per_point > 0:
        lot = round(risk_amount / (stop_distance * value_per_point), 2)

    return Ticket(
        side=snapshot.bias,
        entry=round(snapshot.last, snapshot.digits),
        stop=round(stop, snapshot.digits),
        target=round(target, snapshot.digits),
        lot=lot,
        risk_amount=round(risk_amount, 2),
    )


def ticket_url(base_url: str, snapshot: Snapshot, ticket: Ticket) -> str | None:
    """Trade parameters ride in the fragment, so they never hit a server log."""
    if not base_url:
        return None
    params = urlencode(
        {
            "symbol": snapshot.name,
            "side": ticket.side,
            "entry": ticket.entry,
            "sl": ticket.stop,
            "tp": ticket.target,
            "lot": ticket.lot,
            "risk": ticket.risk_amount,
            "digits": snapshot.digits,
            "at": snapshot.candle_time.isoformat(),
        }
    )
    return f"{base_url}#{params}"


def age_minutes(candle_time: datetime, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    return max(0, int((now - candle_time).total_seconds() // 60))


def age_text(candle_time: datetime, now: datetime | None = None) -> str:
    """How stale the reading is, in words — the number that decides if it counts."""
    minutes = age_minutes(candle_time, now)
    if minutes < 1:
        return "دلوقتي حالًا"
    if minutes < 60:
        return f"من {minutes} دقيقة"
    hours = minutes // 60
    if hours < 24:
        rest = minutes % 60
        return f"من {hours} ساعة" + (f" و{rest} دقيقة" if rest else "")
    days = hours // 24
    return f"من {days} يوم"
