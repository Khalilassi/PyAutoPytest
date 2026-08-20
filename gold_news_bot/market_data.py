"""Candle download.

One provider today (the free Yahoo chart endpoint, no API key). It is isolated
behind parse_chart/fetch_candles so a blocked or changed endpoint is a config
change, not a rewrite — the RSS side already taught us feeds move.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Sequence

import requests

from bot import REQUEST_TIMEOUT, USER_AGENT
from indicators import Candle

LOGGER = logging.getLogger("market_data")

CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


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


def fetch_candles(symbol: str, interval: str = "15m", lookback: str = "1mo") -> list[Candle]:
    """Download candles for one symbol. Raises MarketDataError on any failure."""
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
    LOGGER.info("%s: %d candles, last %s", symbol, len(candles), candles[-1].when.isoformat())
    return candles
