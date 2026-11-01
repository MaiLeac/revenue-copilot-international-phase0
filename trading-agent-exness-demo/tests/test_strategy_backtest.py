"""Unit tests for Milestone M2: BaselineMultiSymbolStrategy and BacktestEvaluator (IS/OOS + Cost Model)."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from app.evaluation.performance import BacktestCostModel, BacktestEvaluator
from app.mt5.market_data import CandleBar
from app.strategies.baseline import BaselineMultiSymbolStrategy


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
