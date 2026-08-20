"""Candle download.

Two providers, chosen per symbol by prefix:

    EURUSD=X       the free Yahoo chart endpoint, no key — fine for FX
    td:XAU/USD     Twelve Data, needs TWELVEDATA_API_KEY — has spot metals

Yahoo carries no spot gold at all (XAUUSD=X and XAU=X both 404; it only lists
the futures contract), which is why a second provider exists rather than a
longer list of Yahoo symbols.

Investing.com is deliberately not here: no public API, terms that forbid
automated extraction, and bot protection that blocks CI runners — a scraper
against it would be both a violation and a source that breaks within days.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Sequence

import requests

from bot import REQUEST_TIMEOUT, USER_AGENT
from indicators import Candle

LOGGER = logging.getLogger("market_data")

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
TWELVEDATA_URL = "https://api.twelvedata.com/time_series"
TWELVEDATA_PREFIX = "td:"

# Twelve Data spells intervals out; ours follow Yahoo's shorthand.
TWELVEDATA_INTERVALS = {
    "1m": "1min",
    "5m": "5min",
    "15m": "15min",
    "30m": "30min",
    "60m": "1h",
    "1h": "1h",
    "1d": "1day",
}


class MarketDataError(RuntimeError):
    """The provider answered, but not with candles we can use."""


def parse_chart(payload: dict) -> list[Candle]:
    """Turn a chart response into candles, dropping the gaps the feed leaves."""
    chart = payload.get("chart") or {}
    if chart.get("error"):
        raise MarketDataError(str(chart["error"]))

    results = chart.get("result") or []
    if not results:
        raise MarketDataError("no result in payload")

    result = results[0]
    stamps: Sequence[int] = result.get("timestamp") or []
    quotes = (result.get("indicators") or {}).get("quote") or [{}]
    quote = quotes[0]

    opens, highs, lows, closes_ = (
        quote.get("open") or [],
        quote.get("high") or [],
        quote.get("low") or [],
        quote.get("close") or [],
    )

    candles: list[Candle] = []
    for index, stamp in enumerate(stamps):
        try:
            o, h, l, c = opens[index], highs[index], lows[index], closes_[index]
        except IndexError:
            break
        if None in (o, h, l, c):
            continue  # the feed leaves holes over market closes
        candles.append(
            Candle(
                when=datetime.fromtimestamp(stamp, tz=timezone.utc),
                open=float(o),
                high=float(h),
                low=float(l),
                close=float(c),
            )
        )

    if not candles:
        raise MarketDataError("payload carried no usable candles")
    return candles


def parse_twelvedata(payload: dict) -> list[Candle]:
    """Turn a Twelve Data time_series response into candles, oldest first."""
    if payload.get("status") == "error":
        raise MarketDataError(payload.get("message", "provider returned an error"))

    values = payload.get("values")
    if not values:
        raise MarketDataError("payload carried no values")

    candles: list[Candle] = []
    for row in values:
        try:
            when = datetime.fromisoformat(row["datetime"])
            candle = Candle(
                when=when.replace(tzinfo=timezone.utc) if when.tzinfo is None else when,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
            )
        except (KeyError, TypeError, ValueError):
            continue
        candles.append(candle)

    if not candles:
        raise MarketDataError("payload carried no usable candles")
    candles.sort(key=lambda c: c.when)  # the provider returns newest first
    return candles


def fetch_twelvedata(symbol: str, interval: str, size: int = 500) -> list[Candle]:
    """Spot metals and FX from Twelve Data. Needs TWELVEDATA_API_KEY."""
    api_key = os.getenv("TWELVEDATA_API_KEY", "").strip()
    if not api_key:
        raise MarketDataError(f"{symbol}: TWELVEDATA_API_KEY is not set")

    try:
        response = requests.get(
            TWELVEDATA_URL,
            params={
                "symbol": symbol,
                "interval": TWELVEDATA_INTERVALS.get(interval, interval),
                "outputsize": size,
                "timezone": "UTC",
                "apikey": api_key,
            },
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise MarketDataError(f"{symbol}: {exc}") from exc

    candles = parse_twelvedata(payload)
    LOGGER.info(
        "%s: %d candles, last %s at %s",
        symbol,
        len(candles),
        candles[-1].close,
        candles[-1].when.isoformat(),
    )
    return candles


def fetch_candles(symbol: str, interval: str = "15m", lookback: str = "1mo") -> list[Candle]:
    """Download candles for one symbol. Raises MarketDataError on any failure."""
    if symbol.startswith(TWELVEDATA_PREFIX):
        return fetch_twelvedata(symbol[len(TWELVEDATA_PREFIX) :], interval)

    try:
        response = requests.get(
            CHART_URL.format(symbol=symbol),
            params={"interval": interval, "range": lookback},
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise MarketDataError(f"{symbol}: {exc}") from exc

    candles = parse_chart(payload)
    LOGGER.info(
        "%s: %d candles, last %s at %s",
        symbol,
        len(candles),
        candles[-1].close,
        candles[-1].when.isoformat(),
    )
    return candles


def fetch_first_available(
    sources: Sequence[str], interval: str = "15m", lookback: str = "1mo"
) -> tuple[str, list[Candle]]:
    """Try each source in order; return the first that answers with candles.

    Sources are ordered most-correct first, so falling through means falling
    back to a *different instrument* (spot -> futures, say). The caller is told
    which one answered precisely so that substitution can be shown to the reader
    instead of hiding behind the display name.
    """
    problems = []
    for symbol in sources:
        try:
            return symbol, fetch_candles(symbol, interval=interval, lookback=lookback)
        except MarketDataError as exc:
            LOGGER.warning("source %s unusable: %s", symbol, exc)
            problems.append(str(exc))
    raise MarketDataError("; ".join(problems) or "no sources configured")
