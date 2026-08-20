"""Chart payload parsing — the shape the provider actually returns."""

import sys
from datetime import timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import market_data  # noqa: E402


def payload(timestamps, opens, highs, lows, closes):
    return {
        "chart": {
            "error": None,
            "result": [
                {
                    "meta": {"symbol": "GC=F"},
                    "timestamp": timestamps,
                    "indicators": {"quote": [{"open": opens, "high": highs, "low": lows, "close": closes}]},
                }
            ],
        }
    }


class TestParseChart:
    def test_builds_candles_in_utc(self):
        candles = market_data.parse_chart(payload([1755000000], [2400.0], [2405.0], [2395.0], [2402.0]))
        assert len(candles) == 1
        assert candles[0].when.tzinfo == timezone.utc
        assert (candles[0].open, candles[0].high, candles[0].low, candles[0].close) == (2400.0, 2405.0, 2395.0, 2402.0)

    def test_skips_holes_left_over_market_closes(self):
        candles = market_data.parse_chart(
            payload([1, 2, 3], [1.0, None, 3.0], [1.0, None, 3.0], [1.0, None, 3.0], [1.0, None, 3.0])
        )
        assert len(candles) == 2

    def test_stops_when_the_arrays_disagree_in_length(self):
        candles = market_data.parse_chart(payload([1, 2, 3], [1.0, 2.0], [1.0, 2.0], [1.0, 2.0], [1.0, 2.0]))
        assert len(candles) == 2

    def test_provider_error_raises(self):
        with pytest.raises(market_data.MarketDataError):
            market_data.parse_chart({"chart": {"error": {"code": "Not Found"}, "result": None}})

    def test_empty_result_raises(self):
        with pytest.raises(market_data.MarketDataError):
            market_data.parse_chart({"chart": {"result": []}})

    def test_all_holes_raises_rather_than_returning_nothing(self):
        with pytest.raises(market_data.MarketDataError):
            market_data.parse_chart(payload([1, 2], [None, None], [None, None], [None, None], [None, None]))

    def test_unexpected_payload_raises(self):
        with pytest.raises(market_data.MarketDataError):
            market_data.parse_chart({})


class TestSourceFallback:
    def test_uses_the_first_source_that_answers(self, monkeypatch):
        calls = []

        def fake(symbol, interval="15m", lookback="1mo"):
            calls.append(symbol)
            if symbol == "XAUUSD=X":
                raise market_data.MarketDataError("404")
            return ["candle"]

        monkeypatch.setattr(market_data, "fetch_candles", fake)
        source, candles = market_data.fetch_first_available(["XAUUSD=X", "GC=F"])
        assert source == "GC=F"
        assert candles == ["candle"]
        assert calls == ["XAUUSD=X", "GC=F"]

    def test_stops_at_the_preferred_source(self, monkeypatch):
        monkeypatch.setattr(market_data, "fetch_candles", lambda s, **k: [s])
        source, _ = market_data.fetch_first_available(["XAUUSD=X", "GC=F"])
        assert source == "XAUUSD=X"

    def test_all_sources_failing_raises(self, monkeypatch):
        def fake(symbol, **kwargs):
            raise market_data.MarketDataError(f"{symbol} down")

        monkeypatch.setattr(market_data, "fetch_candles", fake)
        with pytest.raises(market_data.MarketDataError):
            market_data.fetch_first_available(["a", "b"])

    def test_no_sources_raises(self):
        with pytest.raises(market_data.MarketDataError):
            market_data.fetch_first_available([])
