"""Technical indicators, computed from candles — no third-party TA library.

Every function here is pure: same candles in, same numbers out. That is the
point of computing them ourselves instead of quoting someone else's "signal" —
you can re-run any number on your own chart and check it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence


@dataclass(frozen=True)
class Candle:
    when: datetime
    open: float
    high: float
    low: float
    close: float


def closes(candles: Sequence[Candle]) -> list[float]:
    return [c.close for c in candles]


def sma(values: Sequence[float], period: int) -> float | None:
    if period <= 0 or len(values) < period:
        return None
    return sum(values[-period:]) / period


def ema(values: Sequence[float], period: int) -> float | None:
    """Seeded with the SMA of the first `period` values, then smoothed."""
    if period <= 0 or len(values) < period:
        return None
    multiplier = 2 / (period + 1)
    current = sum(values[:period]) / period
    for value in values[period:]:
        current = (value - current) * multiplier + current
    return current


def ema_series(values: Sequence[float], period: int) -> list[float | None]:
    """EMA aligned to `values`, with None until the first full window."""
    out: list[float | None] = [None] * len(values)
    if period <= 0 or len(values) < period:
        return out
    multiplier = 2 / (period + 1)
    current = sum(values[:period]) / period
    out[period - 1] = current
    for index in range(period, len(values)):
        current = (values[index] - current) * multiplier + current
        out[index] = current
    return out


def rsi(values: Sequence[float], period: int = 14) -> float | None:
    """Wilder's RSI."""
    if len(values) <= period:
        return None

    gains = 0.0
    losses = 0.0
    for previous, current in zip(values[:period], values[1 : period + 1]):
        change = current - previous
        gains += max(change, 0.0)
        losses += max(-change, 0.0)
    avg_gain = gains / period
    avg_loss = losses / period

    for previous, current in zip(values[period:-1], values[period + 1 :]):
        change = current - previous
        avg_gain = (avg_gain * (period - 1) + max(change, 0.0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-change, 0.0)) / period

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(values: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[float, float, float] | None:
    """Returns (macd, signal, histogram)."""
    if len(values) < slow + signal:
        return None
    fast_line = ema_series(values, fast)
    slow_line = ema_series(values, slow)
    macd_line = [
        f - s for f, s in zip(fast_line, slow_line) if f is not None and s is not None
    ]
    if len(macd_line) < signal:
        return None
    signal_line = ema(macd_line, signal)
    if signal_line is None:
        return None
    return macd_line[-1], signal_line, macd_line[-1] - signal_line


def atr(candles: Sequence[Candle], period: int = 14) -> float | None:
    """Wilder's Average True Range."""
    if len(candles) <= period:
        return None
    true_ranges = []
    for previous, current in zip(candles, candles[1:]):
        true_ranges.append(
            max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )
        )
    value = sum(true_ranges[:period]) / period
    for true_range in true_ranges[period:]:
        value = (value * (period - 1) + true_range) / period
    return value


def swing_levels(candles: Sequence[Candle], lookback: int = 50) -> tuple[float, float] | None:
    """Highest high and lowest low of the recent window: nearest obvious levels."""
    window = candles[-lookback:]
    if not window:
        return None
    return max(c.high for c in window), min(c.low for c in window)
