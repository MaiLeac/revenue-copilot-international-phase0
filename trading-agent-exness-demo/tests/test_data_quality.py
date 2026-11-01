"""Unit tests for Data Quality Gate: stale ticks, missing candles, excessive spread, and corrupted OHLC."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.config import load_config
from app.data.quality_gate import DataQualityError, DataQualityGate
from app.mt5.market_data import CandleBar, TickSnapshot


def _gate() -> DataQualityGate:
    repo_root = Path(__file__).resolve().parents[1]
    cfg = load_config(repo_root / "config" / "demo.yaml", env_override={"DEMO_ONLY": "true"})
    return DataQualityGate(cfg)


def _make_candles(
    now: datetime,
    count: int = 60,
    step_sec: int = 900,
    symbol: str = "EURUSDm",
    timeframe: str = "M15",
) -> list[CandleBar]:
    bars: list[CandleBar] = []
    start = now - timedelta(seconds=(count - 1) * step_sec)
    for i in range(count):
        t = start + timedelta(seconds=i * step_sec)
        bars.append(
            CandleBar(
                symbol=symbol,
                timeframe=timeframe,
                open_time_utc=t,
                open=1.0800,
                high=1.0820,
                low=1.0790,
                close=1.0810,
                tick_volume=100,
                spread=10,
                real_volume=0,
            )
        )
    return bars


def test_valid_tick_and_candles_pass() -> None:
    gate = _gate()
    now = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
    tick = TickSnapshot(
        symbol="EURUSDm",
        timestamp_utc=now - timedelta(seconds=10),
        bid=1.08000,
        ask=1.08012,
        last=1.08005,
        volume=1.0,
        spread_price=0.00012,
        spread_points=12,
    )
    candles = _make_candles(now=now, count=60, step_sec=900)
    report = gate.evaluate("EURUSD", "M15", tick, candles, now_utc=now)
    assert report.passed is True
    assert report.current_spread_points == 12


def test_stale_tick_is_rejected() -> None:
    gate = _gate()
    now = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
    stale_tick = TickSnapshot(
        symbol="EURUSDm",
        timestamp_utc=now - timedelta(seconds=180),  # > 60s max_tick_age_seconds
        bid=1.08000,
        ask=1.08010,
        last=1.08005,
        volume=1.0,
        spread_price=0.00010,
        spread_points=10,
    )
    with pytest.raises(DataQualityError, match="Stale tick"):
        gate.validate_tick("EURUSD", stale_tick, now_utc=now)


def test_excessive_spread_is_rejected() -> None:
    gate = _gate()
    now = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
    wide_tick = TickSnapshot(
        symbol="EURUSDm",
        timestamp_utc=now - timedelta(seconds=5),
        bid=1.08000,
        ask=1.08080,
        last=1.08040,
        volume=1.0,
        spread_price=0.00080,
        spread_points=80,  # > 30 max_spread_points for EURUSD
    )
    with pytest.raises(DataQualityError, match="Excessive spread"):
        gate.validate_tick("EURUSD", wide_tick, now_utc=now)


def test_missing_intra_session_candle_gap_is_rejected() -> None:
    gate = _gate()
    now = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
    candles = _make_candles(now=now, count=60, step_sec=900)
    # Remove one candle in the middle to simulate a missing M15 bar
    del candles[30]
    with pytest.raises(DataQualityError, match="Missing candles detected"):
        gate.validate_candles("EURUSD", "M15", candles, now_utc=now)


def test_stale_candle_series_is_rejected() -> None:
    gate = _gate()
    now = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
    old_now = now - timedelta(hours=3)
    candles = _make_candles(now=old_now, count=60, step_sec=900)
    with pytest.raises(DataQualityError, match="Stale candle data"):
        gate.validate_candles("EURUSD", "M15", candles, now_utc=now)
