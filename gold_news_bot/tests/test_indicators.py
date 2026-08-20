"""Indicator maths, checked against cases whose answer is known by hand."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import indicators  # noqa: E402

START = datetime(2026, 8, 20, tzinfo=timezone.utc)


def candles_from(closes, spread=1.0):
    return [
        indicators.Candle(START + timedelta(minutes=15 * i), c, c + spread, c - spread, c)
        for i, c in enumerate(closes)
    ]


class TestMovingAverages:
    def test_sma_of_known_window(self):
        assert indicators.sma([1, 2, 3, 4, 5], 5) == 3

    def test_sma_uses_only_the_last_window(self):
        assert indicators.sma([100, 100, 1, 2, 3], 3) == 2

    def test_too_few_values(self):
        assert indicators.sma([1, 2], 5) is None
        assert indicators.ema([1, 2], 5) is None

    def test_ema_of_a_flat_series_is_that_value(self):
        assert indicators.ema([7.0] * 40, 10) == 7.0

    def test_ema_tracks_a_rise_without_overshooting(self):
        values = [1.0] * 20 + [2.0] * 20
        result = indicators.ema(values, 10)
        assert 1.0 < result < 2.0

    def test_ema_series_is_aligned_and_padded(self):
        series = indicators.ema_series([1.0] * 10, 4)
        assert len(series) == 10
        assert series[:3] == [None, None, None]
        assert series[3] == 1.0


class TestRsi:
    def test_only_gains_pins_at_100(self):
        assert indicators.rsi(list(range(1, 40))) == 100.0

    def test_only_losses_pins_at_zero(self):
        assert indicators.rsi(list(range(40, 1, -1))) == 0.0

    def test_balanced_moves_sit_near_the_middle(self):
        values = [10 + (1 if i % 2 else 0) for i in range(60)]
        assert 40 < indicators.rsi(values) < 60

    def test_needs_more_than_one_period(self):
        assert indicators.rsi([1, 2, 3], 14) is None


class TestMacd:
    def test_flat_series_has_no_momentum(self):
        macd_line, signal, histogram = indicators.macd([5.0] * 80)
        assert abs(macd_line) < 1e-9 and abs(signal) < 1e-9 and abs(histogram) < 1e-9

    def test_rising_series_is_positive(self):
        assert indicators.macd([float(i) for i in range(80)])[0] > 0

    def test_short_series_returns_none(self):
        assert indicators.macd([1.0] * 10) is None


class TestAtr:
    def test_constant_range_is_that_range(self):
        atr = indicators.atr(candles_from([100.0] * 40, spread=2.0), 14)
        assert abs(atr - 4.0) < 1e-9  # high-low = 2*spread

    def test_needs_more_candles_than_the_period(self):
        assert indicators.atr(candles_from([1.0] * 5), 14) is None

    def test_widening_ranges_raise_it(self):
        calm = indicators.atr(candles_from([100.0] * 40, spread=1.0), 14)
        wild = indicators.atr(candles_from([100.0] * 40, spread=5.0), 14)
        assert wild > calm


class TestSwingLevels:
    def test_returns_window_extremes(self):
        high, low = indicators.swing_levels(candles_from([10, 20, 15], spread=1.0), lookback=50)
        assert (high, low) == (21, 9)

    def test_empty_input(self):
        assert indicators.swing_levels([]) is None
