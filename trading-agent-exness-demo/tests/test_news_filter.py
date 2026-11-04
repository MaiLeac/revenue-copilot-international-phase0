"""Unit tests for NewsBlackoutFilter (P0 Safety)."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import pytest

from app.config import NewsFilterConfig
from app.risk.news_filter import NewsBlackoutFilter, NewsEvent


@pytest.fixture
def temp_cache_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test_calendar_cache.json"


def test_clear_when_no_events(temp_cache_file):
    filter_ = NewsBlackoutFilter(
        config=NewsFilterConfig(enabled=True, blackout_minutes_before=30, blackout_minutes_after=30),
        cache_file=temp_cache_file,
        auto_fetch=False,
    )
    is_blocked, reason = filter_.is_blackout("EURUSD", datetime.now(timezone.utc))
    assert not is_blocked
    assert "Clear" in reason


def test_blackout_window_trigger(temp_cache_file):
    filter_ = NewsBlackoutFilter(
        config=NewsFilterConfig(enabled=True, blackout_minutes_before=30, blackout_minutes_after=30),
        cache_file=temp_cache_file,
        auto_fetch=False,
    )
    event_time = datetime(2026, 11, 4, 13, 30, tzinfo=timezone.utc)
    event = NewsEvent(
        title="US CPI m/m",
        country="USD",
        date_utc=event_time,
        impact="High",
    )
    filter_.inject_events([event])

    # 15 mins before: must be blocked
    t_15m_before = event_time - timedelta(minutes=15)
    blocked, reason = filter_.is_blackout("EURUSD", t_15m_before)
    assert blocked
    assert "US CPI m/m" in reason

    # Exact time: must be blocked
    blocked, _ = filter_.is_blackout("EURUSD", event_time)
    assert blocked

    # 25 mins after: must be blocked
    t_25m_after = event_time + timedelta(minutes=25)
    blocked, _ = filter_.is_blackout("EURUSD", t_25m_after)
    assert blocked

    # 35 mins before: clear
    t_35m_before = event_time - timedelta(minutes=35)
    blocked, _ = filter_.is_blackout("EURUSD", t_35m_before)
    assert not blocked

    # 35 mins after: clear
    t_35m_after = event_time + timedelta(minutes=35)
    blocked, _ = filter_.is_blackout("EURUSD", t_35m_after)
    assert not blocked


def test_commodity_gold_affected_by_usd_news(temp_cache_file):
    filter_ = NewsBlackoutFilter(
        config=NewsFilterConfig(enabled=True, blackout_minutes_before=30, blackout_minutes_after=30),
        cache_file=temp_cache_file,
        auto_fetch=False,
    )
    event_time = datetime(2026, 11, 4, 14, 0, tzinfo=timezone.utc)
    event = NewsEvent(
        title="FOMC Statement & Fed Rate Decision",
        country="USD",
        date_utc=event_time,
        impact="High",
    )
    filter_.inject_events([event])

    # XAUUSD must be blocked on USD event
    blocked, reason = filter_.is_blackout("XAUUSD", event_time)
    assert blocked
    assert "FOMC Statement" in reason


def test_medium_low_impact_ignored_when_high_required(temp_cache_file):
    filter_ = NewsBlackoutFilter(
        config=NewsFilterConfig(enabled=True, min_impact="HIGH"),
        cache_file=temp_cache_file,
        auto_fetch=False,
    )
    event_time = datetime(2026, 11, 4, 14, 0, tzinfo=timezone.utc)
    event = NewsEvent(
        title="Crude Oil Inventories",
        country="USD",
        date_utc=event_time,
        impact="Medium",
    )
    filter_.inject_events([event])

    blocked, _ = filter_.is_blackout("EURUSD", event_time)
    assert not blocked


def test_cache_serialization_and_restore(temp_cache_file):
    filter1 = NewsBlackoutFilter(
        config=NewsFilterConfig(enabled=True),
        cache_file=temp_cache_file,
        auto_fetch=False,
    )
    event = NewsEvent(
        title="Non-Farm Employment Change",
        country="USD",
        date_utc=datetime(2026, 11, 6, 13, 30, tzinfo=timezone.utc),
        impact="High",
        forecast="180K",
        previous="223K",
    )
    filter1.inject_events([event])
    filter1._save_cache()

    # Create fresh instance pointing to same cache file
    filter2 = NewsBlackoutFilter(
        config=NewsFilterConfig(enabled=True),
        cache_file=temp_cache_file,
        auto_fetch=False,
    )
    assert len(filter2._events) == 1
    assert filter2._events[0].title == "Non-Farm Employment Change"
    assert filter2._events[0].impact == "High"
