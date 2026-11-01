"""Unit tests for Milestone M2: BaselineMultiSymbolStrategy and BacktestEvaluator (IS/OOS + Cost Model)."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from app.evaluation.performance import BacktestCostModel, BacktestEvaluator
from app.mt5.market_data import CandleBar
from app.strategies.baseline import BaselineMultiSymbolStrategy
from app.strategies.trend_pullback import TrendFollowingPullbackStrategy


def _synthetic_wave_candles(count: int = 300, symbol: str = "XAUUSDm") -> list[CandleBar]:
    bars: list[CandleBar] = []
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    for i in range(count):
        # Smooth sine wave + slight trend to trigger both bullish and bearish EMA crossovers
        base = 2600.0 + 35.0 * math.sin(i / 9.0) + i * 0.05
        bars.append(
            CandleBar(
                symbol=symbol,
                timeframe="M15",
                open_time_utc=start + timedelta(minutes=15 * i),
                open=round(base - 1.0, 2),
                high=round(base + 6.0, 2),
                low=round(base - 6.0, 2),
                close=round(base + 1.0, 2),
                tick_volume=200,
                spread=20,
                real_volume=0,
            )
        )
    return bars


def test_baseline_strategy_returns_flat_on_insufficient_warmup() -> None:
    strat = BaselineMultiSymbolStrategy()
    candles = _synthetic_wave_candles(count=20)
    sig = strat.generate_signal(candles)
    assert sig.direction == "FLAT"
    assert "Insufficient warmup" in sig.reason


def test_backtest_evaluator_separates_in_sample_and_out_of_sample_with_costs() -> None:
    strat = BaselineMultiSymbolStrategy(fast_ema_period=10, slow_ema_period=25, atr_period=10)
    cost_model = BacktestCostModel(
        point_size=0.01,
        contract_size=100.0,
        volume_lots=0.01,
        slippage_points_per_side=2,
        commission_per_lot_roundtrip_usd=7.0,
        swap_per_lot_per_bar_usd=0.05,
    )
    evaluator = BacktestEvaluator(strategy=strat, cost_model=cost_model, initial_equity_usd=10_000.0)
    candles = _synthetic_wave_candles(count=320)
    report = evaluator.run_in_and_out_of_sample(candles, in_sample_ratio=0.70)

    assert report.symbol == "XAUUSDm"
    assert report.in_sample.segment == "IN_SAMPLE"
    assert report.out_of_sample.segment == "OUT_OF_SAMPLE"
    assert report.in_sample.total_trades > 0
    assert report.out_of_sample.total_trades > 0


def test_trend_pullback_strategy_insufficient_warmup() -> None:
    strat = TrendFollowingPullbackStrategy()
    h4 = _synthetic_wave_candles(count=20, symbol="EURUSDm")
    h1 = _synthetic_wave_candles(count=20, symbol="EURUSDm")
    sig = strat.evaluate("EURUSD", h4, h1)
    assert sig.direction == "FLAT"
    assert "Insufficient warmup" in sig.reason


def test_trend_pullback_strategy_regime_filtering() -> None:
    strat = TrendFollowingPullbackStrategy(adx_threshold=20.0)
    h4 = _synthetic_wave_candles(count=100, symbol="EURUSDm")
    h1 = _synthetic_wave_candles(count=100, symbol="EURUSDm")
    sig = strat.evaluate("EURUSD", h4, h1)
    assert sig.symbol == "EURUSD"
    assert sig.timeframe == "H1"
    assert sig.direction in ("BUY", "SELL", "FLAT")


def test_wilder_adx_filters_choppy_consolidation() -> None:
    from app.strategies.trend_pullback import compute_adx

    # Oscillating chop with no net movement
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    chop_candles: list[CandleBar] = []
    for i in range(80):
        val = 1.0800 + 0.0010 * math.sin(i * 1.5)
        chop_candles.append(
            CandleBar(
                symbol="EURUSDm",
                timeframe="H4",
                open_time_utc=start + timedelta(hours=4 * i),
                open=round(val, 5),
                high=round(val + 0.0008, 5),
                low=round(val - 0.0008, 5),
                close=round(val + 0.0001, 5),
                tick_volume=100,
                spread=15,
                real_volume=0,
            )
        )
    adx_chop = compute_adx(chop_candles, 14)
    assert adx_chop < 18.0, f"Expected chop ADX < 18.0, got {adx_chop}"

    # Clear monotonic trending market
    trend_candles: list[CandleBar] = []
    for i in range(80):
        val = 1.0800 + 0.0005 * i
        trend_candles.append(
            CandleBar(
                symbol="EURUSDm",
                timeframe="H4",
                open_time_utc=start + timedelta(hours=4 * i),
                open=round(val - 0.0002, 5),
                high=round(val + 0.0005, 5),
                low=round(val - 0.0003, 5),
                close=round(val + 0.0003, 5),
                tick_volume=100,
                spread=15,
                real_volume=0,
            )
        )
    adx_trend = compute_adx(trend_candles, 14)
    assert adx_trend > 40.0, f"Expected trend ADX > 40.0, got {adx_trend}"


def test_pinbar_requires_dominant_lower_wick_and_small_opposite_wick() -> None:
    strat = TrendFollowingPullbackStrategy(adx_threshold=15.0)

    # Construct candles where H4 is in strong uptrend and H1 pulls back to EMA 21
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    h4 = [
        CandleBar(
            symbol="EURUSDm",
            timeframe="H4",
            open_time_utc=start + timedelta(hours=4 * i),
            open=round(1.0500 + i * 0.0008, 5),
            high=round(1.0510 + i * 0.0008, 5),
            low=round(1.0490 + i * 0.0008, 5),
            close=round(1.0508 + i * 0.0008, 5),
            tick_volume=100,
            spread=15,
            real_volume=0,
        )
        for i in range(80)
    ]

    # Non-pinbar: equal wicks and large body
    h1_bad = [
        CandleBar(
            symbol="EURUSDm",
            timeframe="H1",
            open_time_utc=start + timedelta(hours=i),
            open=round(1.1000 + i * 0.0002, 5),
            high=round(1.1010 + i * 0.0002, 5),
            low=round(1.0990 + i * 0.0002, 5),
            close=round(1.1008 + i * 0.0002, 5),
            tick_volume=100,
            spread=15,
            real_volume=0,
        )
        for i in range(80)
    ]
    sig_bad = strat.evaluate("EURUSD", h4, h1_bad)
    # Shouldn't trigger a buy because no pinbar or engulfing at value zone
    assert sig_bad.direction == "FLAT"
