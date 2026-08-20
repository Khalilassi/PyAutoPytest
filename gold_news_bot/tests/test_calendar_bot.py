"""Unit tests for the economic-calendar alerts (no network involved)."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import calendar_bot  # noqa: E402

NOW = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)

CONFIG = {
    "source_url": "https://example.com/calendar.json",
    "lead_minutes": 35,
    "impacts": ["High"],
    "currencies": ["USD", "EUR"],
    "instruments": {"USD": ["XAUUSD", "EURUSD", "DXY"]},
    "gold_movers": ["cpi", "non-farm"],
}

PAYLOAD = [
    {
        "title": "Core CPI m/m",
        "country": "USD",
        "date": "2026-08-20T12:30:00+00:00",
        "impact": "High",
        "forecast": "0.3%",
        "previous": "0.2%",
    },
    {
        "title": "Flash Manufacturing PMI",
        "country": "EUR",
        "date": "2026-08-20T14:00:00+00:00",
        "impact": "Medium",
        "forecast": "49.1",
        "previous": "48.8",
    },
    {"title": "Bank Holiday", "country": "JPY", "date": "", "impact": "Holiday"},
]


def make_event(title="Core CPI m/m", currency="USD", minutes=25, impact="High", forecast="0.3%", previous="0.2%"):
    return calendar_bot.Event(
        title=title,
        currency=currency,
        when=NOW + timedelta(minutes=minutes),
        impact=impact,
        forecast=forecast,
        previous=previous,
    )


class TestParsing:
    def test_parses_rows_and_skips_undated(self):
        events = calendar_bot.parse_events(PAYLOAD)
        assert [e.title for e in events] == ["Core CPI m/m", "Flash Manufacturing PMI"]

    def test_normalises_to_utc(self):
        events = calendar_bot.parse_events(
            [{"title": "NFP", "country": "USD", "date": "2026-08-20T08:30:00-04:00", "impact": "High"}]
        )
        assert events[0].when == datetime(2026, 8, 20, 12, 30, tzinfo=timezone.utc)

    def test_skips_unparsable_date(self):
        assert calendar_bot.parse_events([{"title": "X", "country": "USD", "date": "soon"}]) == []

    def test_uid_is_stable_and_distinct(self):
        assert make_event().uid == make_event().uid
        assert make_event().uid != make_event(title="NFP").uid


class TestDueSoon:
    def test_picks_event_inside_the_window(self):
        assert len(calendar_bot.due_soon([make_event(minutes=25)], ["High"], ["USD"], 35, now=NOW)) == 1

    def test_ignores_event_beyond_the_window(self):
        assert calendar_bot.due_soon([make_event(minutes=90)], ["High"], ["USD"], 35, now=NOW) == []

    def test_ignores_event_already_past(self):
        assert calendar_bot.due_soon([make_event(minutes=-5)], ["High"], ["USD"], 35, now=NOW) == []

    def test_ignores_low_impact(self):
        assert calendar_bot.due_soon([make_event(impact="Medium")], ["High"], ["USD"], 35, now=NOW) == []

    def test_ignores_other_currencies(self):
        assert calendar_bot.due_soon([make_event(currency="NZD")], ["High"], ["USD"], 35, now=NOW) == []

    def test_soonest_first(self):
        events = [make_event(title="late", minutes=30), make_event(title="early", minutes=10)]
        picked = calendar_bot.due_soon(events, ["High"], ["USD"], 35, now=NOW)
        assert [e.title for e in picked] == ["early", "late"]


class TestMessage:
    def test_contains_countdown_forecast_and_instruments(self):
        text = calendar_bot.build_message(make_event(minutes=28), CONFIG, now=NOW)
        assert "بعد ~28 دقيقة" in text
        assert "0.3%" in text and "0.2%" in text
        assert "XAUUSD" in text and "DXY" in text
        assert "15:28 بتوقيت الرياض" in text

    def test_flags_gold_movers(self):
        assert "بتحرّك الذهب" in calendar_bot.build_message(make_event(), CONFIG, now=NOW)

    def test_does_not_flag_ordinary_events(self):
        text = calendar_bot.build_message(make_event(title="Housing Starts"), CONFIG, now=NOW)
        assert "بتحرّك الذهب" not in text

    def test_always_carries_the_not_a_signal_note(self):
        assert "مش توصية" in calendar_bot.build_message(make_event(), CONFIG, now=NOW)

    def test_handles_missing_forecast(self):
        text = calendar_bot.build_message(make_event(forecast="", previous=""), CONFIG, now=NOW)
        assert "المتوقع" not in text

    def test_escapes_html(self):
        text = calendar_bot.build_message(make_event(title="CPI <b>x</b>"), CONFIG, now=NOW)
        assert "&lt;b&gt;" in text


class TestConfig:
    def test_loads_shipped_config(self):
        config = calendar_bot.load_config(Path(__file__).resolve().parents[1] / "calendar.yml")
        assert config["source_url"].startswith("https://")
        assert "USD" in config["instruments"]

    def test_rejects_config_without_source(self, tmp_path):
        path = tmp_path / "calendar.yml"
        path.write_text("impacts: [High]\n", encoding="utf-8")
        with pytest.raises(ValueError):
            calendar_bot.load_config(path)


class TestDigest:
    def test_lists_events_grouped_by_day(self):
        events = [
            make_event(title="Core CPI m/m", minutes=270),
            make_event(title="FOMC Member Speaks", minutes=1200, impact="Medium", forecast="", previous=""),
        ]
        text = calendar_bot.build_digest(events, CONFIG)
        assert "أخبار الـ24 ساعة الجاية" in text
        assert "Core CPI m/m" in text and "FOMC Member Speaks" in text
        assert text.count("<b>الخميس") + text.count("<b>الجمعة") == 2

    def test_says_so_when_nothing_is_scheduled(self):
        text = calendar_bot.build_digest([], CONFIG)
        assert "مفيش أخبار مؤثرة" in text

    def test_times_are_riyadh_not_utc(self):
        # 12:30 UTC lands at 15:30 in Riyadh
        text = calendar_bot.build_digest([make_event(minutes=30)], CONFIG)
        assert "15:30" in text and "12:30" not in text

    def test_marks_impact_with_an_icon(self):
        text = calendar_bot.build_digest([make_event(), make_event(title="PMI", impact="Medium")], CONFIG)
        assert "\U0001f534" in text and "\U0001f7e0" in text

    def test_carries_the_not_a_signal_note(self):
        assert "مش توصية" in calendar_bot.build_digest([make_event()], CONFIG)

    def test_window_covers_a_full_day(self):
        inside = make_event(title="inside", minutes=23 * 60)
        outside = make_event(title="outside", minutes=25 * 60)
        picked = calendar_bot.due_within([inside, outside], ["High"], ["USD"], 24, now=NOW)
        assert [e.title for e in picked] == ["inside"]


class TestAlertTiming:
    def test_alert_time_is_riyadh(self):
        text = calendar_bot.build_message(make_event(minutes=30), CONFIG, now=NOW)
        assert "15:30" in text
        assert "الرياض" in text
        assert "UTC" not in text
