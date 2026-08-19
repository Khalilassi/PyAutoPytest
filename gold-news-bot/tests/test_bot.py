"""Unit tests for the filtering / dedupe logic (no network involved)."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bot  # noqa: E402

NOW = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
KEYWORDS = ["gold", "inflation", "nfp", "ذهب"]


def make_item(uid="1", title="Gold rises", link="https://example.com/a", published=NOW, summary=""):
    return bot.NewsItem(uid=uid, title=title, link=link, source="Test", published=published, summary=summary)


class TestCanonicalLink:
    def test_strips_tracking_params_and_fragment(self):
        link = "https://example.com/news/?utm_source=rss&id=7#top"
        assert bot.canonical_link(link) == "https://example.com/news?id=7"

    def test_empty_link(self):
        assert bot.canonical_link("") == ""


class TestKeywordMatching:
    def test_matches_in_title_case_insensitive(self):
        assert bot.matches_keywords(make_item(title="GOLD hits record"), KEYWORDS)

    def test_matches_in_summary(self):
        item = make_item(title="Weekly wrap", summary="US inflation came in hot")
        assert bot.matches_keywords(item, KEYWORDS)

    def test_matches_arabic_keyword(self):
        assert bot.matches_keywords(make_item(title="الذهب يصعد"), KEYWORDS)

    def test_rejects_unrelated_news(self):
        assert not bot.matches_keywords(make_item(title="Tech stocks rally"), KEYWORDS)


class TestRecency:
    def test_recent_item_passes(self):
        assert bot.is_recent(make_item(published=NOW - timedelta(hours=2)), 6, now=NOW)

    def test_old_item_rejected(self):
        assert not bot.is_recent(make_item(published=NOW - timedelta(hours=9)), 6, now=NOW)

    def test_undated_item_passes(self):
        assert bot.is_recent(make_item(published=None), 6, now=NOW)

    def test_zero_disables_the_window(self):
        assert bot.is_recent(make_item(published=NOW - timedelta(days=30)), 0, now=NOW)


class TestSelectNew:
    def test_skips_already_seen(self):
        items = [make_item(uid="a"), make_item(uid="b", link="https://example.com/b")]
        picked = bot.select_new(items, KEYWORDS, {"a": NOW.isoformat()}, 6, 10, now=NOW)
        assert [i.uid for i in picked] == ["b"]

    def test_deduplicates_same_story_from_two_feeds(self):
        items = [make_item(uid="a"), make_item(uid="a")]
        assert len(bot.select_new(items, KEYWORDS, {}, 6, 10, now=NOW)) == 1

    def test_newest_first(self):
        old = make_item(uid="old", published=NOW - timedelta(hours=4))
        new = make_item(uid="new", published=NOW - timedelta(minutes=5))
        picked = bot.select_new([old, new], KEYWORDS, {}, 6, 10, now=NOW)
        assert [i.uid for i in picked] == ["new", "old"]

    def test_caps_items_per_run(self):
        items = [make_item(uid=str(n), published=NOW - timedelta(minutes=n)) for n in range(20)]
        assert len(bot.select_new(items, KEYWORDS, {}, 6, 5, now=NOW)) == 5

    def test_filters_out_non_matching(self):
        items = [make_item(uid="a", title="Tech stocks rally")]
        assert bot.select_new(items, KEYWORDS, {}, 6, 10, now=NOW) == []


class TestState:
    def test_roundtrip(self, tmp_path):
        path = tmp_path / "state" / "seen.json"
        bot.save_state(path, {"a": NOW.isoformat()})
        assert bot.load_state(path) == {"a": NOW.isoformat()}

    def test_missing_file_is_empty(self, tmp_path):
        assert bot.load_state(tmp_path / "nope.json") == {}

    def test_corrupt_file_is_empty(self, tmp_path):
        path = tmp_path / "seen.json"
        path.write_text("{not json", encoding="utf-8")
        assert bot.load_state(path) == {}

    def test_prune_drops_expired_entries(self):
        seen = {
            "fresh": (NOW - timedelta(days=1)).isoformat(),
            "stale": (NOW - timedelta(days=30)).isoformat(),
            "broken": "not-a-date",
        }
        assert bot.prune_state(seen, 7, now=NOW) == {"fresh": seen["fresh"]}


class TestMessage:
    def test_escapes_html_in_title(self):
        text = make_item(title="Gold <b>up</b> & away").as_message()
        assert "&lt;b&gt;" in text and "&amp;" in text

    def test_includes_link_and_source(self):
        text = make_item().as_message()
        assert "https://example.com/a" in text and "Test" in text


class TestConfig:
    def test_loads_shipped_config(self):
        feeds, keywords = bot.load_config(Path(__file__).resolve().parents[1] / "feeds.yml")
        assert len(feeds) >= 5
        assert "gold" in keywords

    def test_rejects_empty_config(self, tmp_path):
        path = tmp_path / "feeds.yml"
        path.write_text("feeds: []\nkeywords: []\n", encoding="utf-8")
        with pytest.raises(ValueError):
            bot.load_config(path)
