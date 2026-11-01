"""Baseline multi-symbol trend/pullback strategy (Milestone M2 — Decision 7A).

Runs a single deterministic rule set across whitelisted symbols (XAGUSD, EURUSD, XAUUSD):
- Trend filter: fast EMA(20) vs slow EMA(50)
- Volatility-scaled stops: ATR(14) stop-loss and take-profit
- Zero LLM involvement; pure deterministic calculation over closed CandleBar series.
"""

from __future__ import annotations

from app.mt5.market_data import CandleBar
from app.strategies.base import StrategySignal


class BaselineMultiSymbolStrategy:
    """Single baseline strategy evaluated uniformly across whitelisted symbols (Decision 7A)."""

    strategy_id = "ema20_50_atr14_baseline"
    version = "0.2.0"

    def __init__(
        self,
        fast_ema_period: int = 20,
        slow_ema_period: int = 50,
        atr_period: int = 14,
        sl_atr_mult: float = 1.5,
        tp_atr_mult: float = 2.5,
    ) -> None:
        if fast_ema_period <= 1 or slow_ema_period <= fast_ema_period or atr_period <= 1:
            raise ValueError("Invalid EMA/ATR period parameters.")
        if sl_atr_mult <= 0 or tp_atr_mult <= 0:
            raise ValueError("Stop-loss and take-profit ATR multipliers must be positive.")
        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period
        self.atr_period = atr_period
        self.sl_atr_mult = sl_atr_mult
        self.tp_atr_mult = tp_atr_mult

    def generate_signal(self, candles: list[CandleBar]) -> StrategySignal:
        """Evaluate closed candles and return BUY, SELL, or FLAT with deterministic SL/TP."""
        min_bars = max(self.slow_ema_period + 2, self.atr_period + 2)
        if len(candles) < min_bars:
            sym = candles[-1].symbol if candles else "UNKNOWN"
            tf = candles[-1].timeframe if candles else "UNKNOWN"
            return StrategySignal(
                symbol=sym,
                timeframe=tf,
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                direction="FLAT",
                reason=f"Insufficient warmup bars ({len(candles)} < {min_bars})",
            )

        closes = [c.close for c in candles]
        fast_ema = self._compute_ema_series(closes, self.fast_ema_period)
        slow_ema = self._compute_ema_series(closes, self.slow_ema_period)
        atr = self._compute_atr(candles, self.atr_period)

        last_bar = candles[-1]
        if atr <= 0:
            return StrategySignal(
                symbol=last_bar.symbol,
                timeframe=last_bar.timeframe,
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                direction="FLAT",
                reason="Zero ATR volatility",
            )

        # Crossover on the most recently closed bar vs previous bar
        prev_diff = fast_ema[-2] - slow_ema[-2]
        curr_diff = fast_ema[-1] - slow_ema[-1]
        entry = last_bar.close

        if prev_diff <= 0 and curr_diff > 0:
            sl = round(entry - self.sl_atr_mult * atr, 5)
            tp = round(entry + self.tp_atr_mult * atr, 5)
            return StrategySignal(
                symbol=last_bar.symbol,
                timeframe=last_bar.timeframe,
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                direction="BUY",
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp,
                reason=f"Bullish EMA({self.fast_ema_period}/{self.slow_ema_period}) crossover",
            )

        if prev_diff >= 0 and curr_diff < 0:
            sl = round(entry + self.sl_atr_mult * atr, 5)
            tp = round(entry - self.tp_atr_mult * atr, 5)
            return StrategySignal(
                symbol=last_bar.symbol,
                timeframe=last_bar.timeframe,
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                direction="SELL",
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp,
                reason=f"Bearish EMA({self.fast_ema_period}/{self.slow_ema_period}) crossover",
            )

        return StrategySignal(
            symbol=last_bar.symbol,
            timeframe=last_bar.timeframe,
            strategy_id=self.strategy_id,
            strategy_version=self.version,
            direction="FLAT",
            reason="No crossover on closed bar",
        )

    @staticmethod
    def _compute_ema_series(values: list[float], period: int) -> list[float]:
        k = 2.0 / (period + 1)
        ema_val = sum(values[:period]) / period
        result = [ema_val] * period
        for price in values[period:]:
            ema_val = price * k + ema_val * (1.0 - k)
            result.append(ema_val)
        return result

    @staticmethod
    def _compute_atr(candles: list[CandleBar], period: int) -> float:
        trs: list[float] = []
        for i in range(1, len(candles)):
            high = candles[i].high
            low = candles[i].low
            prev_close = candles[i - 1].close
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            trs.append(tr)
        if len(trs) < period:
            return 0.0
        return sum(trs[-period:]) / period
