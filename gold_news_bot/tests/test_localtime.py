"""Every user-facing time is rendered in Riyadh time."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import localtime  # noqa: E402

UTC_NOON = datetime(2026, 8, 20, 12, 30, tzinfo=timezone.utc)


class TestRiyadhRendering:
    def test_shifts_utc_by_three_hours(self):
        assert localtime.format_time(UTC_NOON) == "15:30"

    def test_full_datetime(self):
        assert localtime.format_datetime(UTC_NOON) == "2026-08-20 15:30"

    def test_arabic_day_name(self):
        assert localtime.format_day(UTC_NOON) == "الخميس 20 أغسطس"

    def test_naive_input_is_treated_as_utc(self):
        assert localtime.format_time(datetime(2026, 8, 20, 12, 30)) == "15:30"

    def test_rolls_over_to_the_next_day(self):
        late = datetime(2026, 8, 20, 22, 0, tzinfo=timezone.utc)
        assert localtime.format_day(late) == "الجمعة 21 أغسطس"
        assert localtime.format_time(late) == "01:00"

    def test_other_offsets_are_converted_too(self):
        newyork = datetime(2026, 8, 20, 8, 30, tzinfo=timezone(timedelta(hours=-4)))
        assert localtime.format_time(newyork) == "15:30"

    def test_label_names_riyadh(self):
        assert "الرياض" in localtime.TZ_LABEL
