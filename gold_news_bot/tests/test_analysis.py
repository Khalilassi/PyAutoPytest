"""The rules that turn indicator readings into a ticket."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import analysis  # noqa: E402
import indicators  # noqa: E402

NOW = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)
RULES = {
    "rsi_period": 14,
    "atr_period": 14,
    "fast_ema": 5,
    "slow_ema": 20,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "stop_atr_multiple": 1.5,
    "reward_risk": 2.0,
}
RISK = {"account_balance": 1000, "risk_percent": 1.0}


def snapshot(bias="BUY", last=2000.0, atr=10.0, digits=2, trend="UP"):
    return analysis.Snapshot(
        name="XAUUSD", digits=digits, last=last, change_pct=0.1, rsi=55.0,
        ema_fast=1990.0, ema_slow=1950.0, macd_hist=0.5, atr=atr,
        swing_high=2050.0, swing_low=1900.0, candle_time=NOW, trend=trend, bias=bias,
    )


class TestTrendAndBias:
    def test_fast_above_slow_is_up(self):
        assert analysis.classify_trend(10, 5) == "UP"

    def test_fast_below_slow_is_down(self):
        assert analysis.classify_trend(5, 10) == "DOWN"

    def test_missing_averages_are_unknown(self):
        assert analysis.classify_trend(None, 5) == "UNKNOWN"

    def test_uptrend_gives_buy(self):
        assert analysis.classify_bias("UP", 55, RULES) == analysis.BUY

    def test_overbought_uptrend_waits(self):
        assert analysis.classify_bias("UP", 75, RULES) == analysis.WAIT

    def test_downtrend_gives_sell(self):
        assert analysis.classify_bias("DOWN", 45, RULES) == analysis.SELL

    def test_oversold_downtrend_waits(self):
        assert analysis.classify_bias("DOWN", 25, RULES) == analysis.WAIT

    def test_unknown_trend_waits(self):
        assert analysis.classify_bias("UNKNOWN", 55, RULES) == analysis.WAIT


class TestTicket:
    def test_buy_places_stop_below_and_target_above(self):
        ticket = analysis.build_ticket(snapshot(), RULES, RISK, 100)
        assert ticket.side == "BUY"
        assert ticket.stop < ticket.entry < ticket.target

    def test_sell_mirrors_the_levels(self):
        ticket = analysis.build_ticket(snapshot(bias="SELL", trend="DOWN"), RULES, RISK, 100)
        assert ticket.target < ticket.entry < ticket.stop

    def test_reward_is_the_configured_multiple_of_risk(self):
        ticket = analysis.build_ticket(snapshot(), RULES, RISK, 100)
        risk = ticket.entry - ticket.stop
        assert abs((ticket.target - ticket.entry) / risk - 2.0) < 0.01

    def test_stop_distance_follows_atr(self):
        ticket = analysis.build_ticket(snapshot(atr=10.0), RULES, RISK, 100)
        assert abs((ticket.entry - ticket.stop) - 15.0) < 0.01  # 1.5 x ATR

    def test_lot_sizes_the_risk_percentage(self):
        # risk $10, stop 15.0 wide, $100 per point -> 10 / (15 * 100)
        ticket = analysis.build_ticket(snapshot(atr=10.0), RULES, RISK, 100)
        assert ticket.risk_amount == 10.0
        assert ticket.lot == round(10 / (15.0 * 100), 2)

    def test_wait_produces_no_ticket(self):
        assert analysis.build_ticket(snapshot(bias="WAIT"), RULES, RISK, 100) is None

    def test_missing_atr_produces_no_ticket(self):
        assert analysis.build_ticket(snapshot(atr=None), RULES, RISK, 100) is None


class TestTicketUrl:
    def test_parameters_ride_in_the_fragment(self):
        url = analysis.ticket_url("https://example.com/t.html", snapshot(), analysis.build_ticket(snapshot(), RULES, RISK, 100))
        assert "#" in url and "?" not in url
        assert "symbol=XAUUSD" in url and "side=BUY" in url

    def test_no_base_url_means_no_button(self):
        assert analysis.ticket_url("", snapshot(), analysis.build_ticket(snapshot(), RULES, RISK, 100)) is None


class TestAge:
    def test_fresh_reading(self):
        assert analysis.age_text(NOW, NOW) == "دلوقتي حالًا"

    def test_minutes(self):
        assert analysis.age_text(NOW - timedelta(minutes=17), NOW) == "من 17 دقيقة"

    def test_hours_and_minutes(self):
        assert analysis.age_text(NOW - timedelta(hours=2, minutes=5), NOW) == "من 2 ساعة و5 دقيقة"

    def test_days(self):
        assert analysis.age_text(NOW - timedelta(days=3), NOW) == "من 3 يوم"

    def test_age_never_goes_negative(self):
        assert analysis.age_minutes(NOW + timedelta(minutes=30), NOW) == 0


class TestSnapshot:
    def test_built_from_candles(self):
        closes = [100 + i * 0.5 for i in range(120)]
        candles = [
            indicators.Candle(NOW - timedelta(minutes=15 * (120 - i)), c, c + 1, c - 1, c)
            for i, c in enumerate(closes)
        ]
        snap = analysis.build_snapshot(candles, "TEST", 2, RULES)
        assert snap.trend == "UP"
        assert snap.last == closes[-1]
        assert snap.candle_time == candles[-1].when


class TestSourceIsCarried:
    def test_snapshot_records_which_symbol_fed_it(self):
        closes = [100 + i * 0.5 for i in range(60)]
        candles = [
            indicators.Candle(NOW - timedelta(minutes=15 * (60 - i)), c, c + 1, c - 1, c)
            for i, c in enumerate(closes)
        ]
        snap = analysis.build_snapshot(candles, "XAUUSD", 2, RULES, source="GC=F")
        assert snap.source == "GC=F"


class TestValuePerPoint:
    def test_dollar_quoted_pair_uses_the_contract_size(self):
        assert analysis.resolve_value_per_point({"value_per_point": 100000}, 1.09) == 100000

    def test_gold_uses_ounces_per_lot(self):
        assert analysis.resolve_value_per_point({"value_per_point": 100}, 4480.0) == 100

    def test_auto_derives_from_price_for_usd_base_pairs(self):
        # USDJPY at 150: one lot of 100,000 USD moves 100,000 JPY per 1.0,
        # which is 100000/150 dollars
        value = analysis.resolve_value_per_point({"value_per_point": "auto", "contract_size": 100000}, 150.0)
        assert abs(value - 666.67) < 0.01

    def test_auto_tracks_the_rate(self):
        low = analysis.resolve_value_per_point({"value_per_point": "auto"}, 100.0)
        high = analysis.resolve_value_per_point({"value_per_point": "auto"}, 200.0)
        assert low > high

    def test_zero_price_does_not_divide_by_zero(self):
        assert analysis.resolve_value_per_point({"value_per_point": "auto"}, 0.0) == 0.0

    def test_missing_value_is_zero(self):
        assert analysis.resolve_value_per_point({}, 1.0) == 0.0


class TestUsdJpyLotSizing:
    def test_lot_uses_the_derived_value_not_a_fixed_one(self):
        snap = analysis.Snapshot(
            name="USDJPY", digits=3, last=150.0, change_pct=0.0, rsi=55.0,
            ema_fast=149.0, ema_slow=145.0, macd_hist=0.1, atr=0.5,
            swing_high=152.0, swing_low=148.0, candle_time=NOW, trend="UP",
            bias="BUY", source="USDJPY=X",
        )
        value = analysis.resolve_value_per_point({"value_per_point": "auto", "contract_size": 100000}, snap.last)
        ticket = analysis.build_ticket(snap, RULES, RISK, value)
        stop_distance = snap.atr * RULES["stop_atr_multiple"]
        assert ticket.lot == round(10 / (stop_distance * value), 2)
