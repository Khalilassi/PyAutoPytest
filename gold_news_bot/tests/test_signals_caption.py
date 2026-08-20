"""The caption must never hide which instrument the number came from."""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import analysis  # noqa: E402
import signals_bot  # noqa: E402

NOW = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)


def snapshot(source="XAUUSD=X"):
    return analysis.Snapshot(
        name="XAUUSD", digits=2, last=4480.25, change_pct=0.2, rsi=55.0,
        ema_fast=4470.0, ema_slow=4400.0, macd_hist=0.5, atr=12.0,
        swing_high=4520.0, swing_low=4410.0, candle_time=NOW, trend="UP",
        bias="BUY", source=source,
    )


class TestCaption:
    def test_names_the_source_symbol(self):
        assert "XAUUSD=X" in signals_bot.build_caption(snapshot(), None, NOW)

    def test_warns_when_the_data_is_futures_not_spot(self):
        caption = signals_bot.build_caption(snapshot(source="GC=F"), None, NOW)
        assert "عقود آجلة" in caption

    def test_no_futures_warning_on_spot(self):
        assert "عقود آجلة" not in signals_bot.build_caption(snapshot(), None, NOW)

    def test_states_the_age(self):
        assert "آخر شمعة" in signals_bot.build_caption(snapshot(), None, NOW)

    def test_wait_says_there_is_no_ticket(self):
        assert "استنى" in signals_bot.build_caption(snapshot(), None, NOW)


class TestFingerprint:
    def test_changing_source_forces_a_resend(self):
        assert signals_bot.state_fingerprint(snapshot()) != signals_bot.state_fingerprint(snapshot(source="GC=F"))
