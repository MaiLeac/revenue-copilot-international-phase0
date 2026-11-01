"""Deterministic Backtest & Performance Evaluator with Spread, Commission, Swap, Slippage, and IS/OOS Split (Milestone M2)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.mt5.market_data import CandleBar
from app.strategies.baseline import BaselineMultiSymbolStrategy


@dataclass(frozen=True)
class BacktestCostModel:
    point_size: float = 0.01
    contract_size: float = 100.0
    volume_lots: float = 0.01
    spread_points_override: int | None = None
    slippage_points_per_side: int = 2
    commission_per_lot_roundtrip_usd: float = 7.0
    swap_per_lot_per_bar_usd: float = 0.0


@dataclass(frozen=True)
class SimulatedTrade:
    direction: Literal["BUY", "SELL"]
    entry_index: int
    exit_index: int
    entry_price_effective: float
    exit_price_effective: float
    gross_pnl_usd: float
    total_cost_usd: float
    net_pnl_usd: float
    exit_reason: str


@dataclass(frozen=True)
class PerformanceMetrics:
    segment: str  # FULL, IN_SAMPLE, OUT_OF_SAMPLE
    total_trades: int
    win_rate_pct: float
    gross_profit_usd: float
    gross_loss_usd: float
    net_profit_usd: float
    profit_factor: float
    expectancy_per_trade_usd: float
    max_drawdown_pct: float


@dataclass(frozen=True)
class SplitBacktestReport:
    symbol: str
    timeframe: str
    strategy_id: str
    strategy_version: str
    split_ratio: float
    in_sample: PerformanceMetrics
    out_of_sample: PerformanceMetrics


class BacktestEvaluator:
    """Reproducible, non-leaking bar-by-bar backtester with explicit transaction cost deductions."""

    def __init__(
        self,
        strategy: BaselineMultiSymbolStrategy,
        cost_model: BacktestCostModel | None = None,
        initial_equity_usd: float = 10_000.0,
    ) -> None:
        self.strategy = strategy
        self.cost_model = cost_model or BacktestCostModel()
        self.initial_equity_usd = initial_equity_usd

    def run_in_and_out_of_sample(
        self,
        candles: list[CandleBar],
        in_sample_ratio: float = 0.70,
    ) -> SplitBacktestReport:
        if not (0.2 <= in_sample_ratio <= 0.9):
            raise ValueError("in_sample_ratio must be between 0.2 and 0.9.")
        min_needed = (self.strategy.slow_ema_period + 10) * 2
        if len(candles) < min_needed:
            raise ValueError(
                f"Need at least {min_needed} candles for separate In-Sample and Out-of-Sample evaluation."
            )

        split_idx = int(len(candles) * in_sample_ratio)
        is_candles = candles[:split_idx]
        oos_candles = candles[split_idx:]

        is_trades = self.simulate_segment(is_candles)
        oos_trades = self.simulate_segment(oos_candles)

        return SplitBacktestReport(
            symbol=candles[0].symbol,
            timeframe=candles[0].timeframe,
            strategy_id=self.strategy.strategy_id,
            strategy_version=self.strategy.version,
            split_ratio=in_sample_ratio,
            in_sample=self.compute_metrics("IN_SAMPLE", is_trades),
            out_of_sample=self.compute_metrics("OUT_OF_SAMPLE", oos_trades),
        )

    def simulate_segment(self, candles: list[CandleBar]) -> list[SimulatedTrade]:
        trades: list[SimulatedTrade] = []
        warmup = max(self.strategy.slow_ema_period + 2, self.strategy.atr_period + 2)
        active_pos: dict[str, float | int | str] | None = None
        cm = self.cost_model

        for i in range(warmup, len(candles)):
            bar = candles[i]
            spread_pts = (
                cm.spread_points_override
                if cm.spread_points_override is not None
                else max(0, bar.spread)
            )
            half_spread_Plus_slip = (spread_pts * 0.5 + cm.slippage_points_per_side) * cm.point_size

            # 1. Check SL/TP on active position using current bar high/low
            if active_pos is not None:
                direction = str(active_pos["direction"])
                sl = float(active_pos["sl"])
                tp = float(active_pos["tp"])
                entry_idx = int(active_pos["entry_index"])
                entry_px = float(active_pos["entry_price"])
                exit_px: float | None = None
                exit_reason = ""

                if direction == "BUY":
                    if bar.low <= sl:
                        exit_px = sl - cm.slippage_points_per_side * cm.point_size
                        exit_reason = "STOP_LOSS"
                    elif bar.high >= tp:
                        exit_px = tp - cm.slippage_points_per_side * cm.point_size
                        exit_reason = "TAKE_PROFIT"
                else:
                    if bar.high >= sl:
                        exit_px = sl + cm.slippage_points_per_side * cm.point_size
                        exit_reason = "STOP_LOSS"
                    elif bar.low <= tp:
                        exit_px = tp + cm.slippage_points_per_side * cm.point_size
                        exit_reason = "TAKE_PROFIT"

                if exit_px is not None:
                    trades.append(
                        self._close_trade(
                            direction=direction,  # type: ignore[arg-type]
                            entry_index=entry_idx,
                            exit_index=i,
                            entry_price_effective=entry_px,
                            exit_price_effective=exit_px,
                            exit_reason=exit_reason,
                        )
                    )
                    active_pos = None

            # 2. If flat at the start of bar i, evaluate signal on closed bars up to i-1 and execute at bar i open
            elif active_pos is None:
                sig = self.strategy.generate_signal(candles[:i])
                if sig.direction in {"BUY", "SELL"} and sig.stop_loss is not None and sig.take_profit is not None:
                    raw_open = bar.open
                    price_diff = raw_open - ( sig.entry_price or raw_open )
                    if sig.direction == "BUY":
                        eff_entry = raw_open + half_spread_Plus_slip
                    else:
                        eff_entry = raw_open - half_spread_Plus_slip
                    active_pos = {
                        "direction": sig.direction,
                        "entry_index": i,
                        "entry_price": eff_entry,
                        "sl": sig.stop_loss + price_diff,
                        "tp": sig.take_profit + price_diff,
                    }

        return trades

    def _close_trade(
        self,
        direction: Literal["BUY", "SELL"],
        entry_index: int,
        exit_index: int,
        entry_price_effective: float,
        exit_price_effective: float,
        exit_reason: str,
    ) -> SimulatedTrade:
        cm = self.cost_model
        bars_held = max(1, exit_index - entry_index)
        price_move = (
            (exit_price_effective - entry_price_effective)
            if direction == "BUY"
            else (entry_price_effective - exit_price_effective)
        )
        gross_pnl = price_move * cm.contract_size * cm.volume_lots
        commission = cm.commission_per_lot_roundtrip_usd * cm.volume_lots
        swap_cost = cm.swap_per_lot_per_bar_usd * cm.volume_lots * bars_held
        total_cost = round(commission + swap_cost, 4)
        net_pnl = round(gross_pnl - total_cost, 4)

        return SimulatedTrade(
            direction=direction,
            entry_index=entry_index,
            exit_index=exit_index,
            entry_price_effective=round(entry_price_effective, 5),
            exit_price_effective=round(exit_price_effective, 5),
            gross_pnl_usd=round(gross_pnl, 4),
            total_cost_usd=total_cost,
            net_pnl_usd=net_pnl,
            exit_reason=exit_reason,
        )

    def compute_metrics(self, segment: str, trades: list[SimulatedTrade]) -> PerformanceMetrics:
        if not trades:
            return PerformanceMetrics(
                segment=segment,
                total_trades=0,
                win_rate_pct=0.0,
                gross_profit_usd=0.0,
                gross_loss_usd=0.0,
                net_profit_usd=0.0,
                profit_factor=0.0,
                expectancy_per_trade_usd=0.0,
                max_drawdown_pct=0.0,
            )

        wins = [t.net_pnl_usd for t in trades if t.net_pnl_usd > 0]
        losses = [abs(t.net_pnl_usd) for t in trades if t.net_pnl_usd <= 0]
        gross_profit = round(sum(wins), 2)
        gross_loss = round(sum(losses), 2)
        net_profit = round(sum(t.net_pnl_usd for t in trades), 2)
        win_rate = round((len(wins) / len(trades)) * 100.0, 2)
        pf = round(gross_profit / gross_loss, 3) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)
        expectancy = round(net_profit / len(trades), 2)

        equity = self.initial_equity_usd
        peak = equity
        max_dd_pct = 0.0
        for t in trades:
            equity += t.net_pnl_usd
            if equity > peak:
                peak = equity
            dd_pct = ((peak - equity) / peak) * 100.0 if peak > 0 else 0.0
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct

        return PerformanceMetrics(
            segment=segment,
            total_trades=len(trades),
            win_rate_pct=win_rate,
            gross_profit_usd=gross_profit,
            gross_loss_usd=gross_loss,
            net_profit_usd=net_profit,
            profit_factor=pf,
            expectancy_per_trade_usd=expectancy,
            max_drawdown_pct=round(max_dd_pct, 2),
        )
