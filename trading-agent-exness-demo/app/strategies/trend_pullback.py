"""H4/H1 Trend-Following Pullback Strategy (Milestone M2 Implementation).

Per STRATEGY_SPEC.md v2.0:
- Tier 1: H4 Market Regime (EMA 50 vs EMA 200, ADX 14 >= 20).
- Tier 2: H1 Setup Selection (Pullback to Value Zone between EMA 21 and EMA 50).
- Tier 3: Trigger Bar Confirmation (Rejection Pinbar or Engulfing).
- Tier 4: Structural SL with ATR buffer, Target R:R >= 1:2.0.
"""

from __future__ import annotations

import logging
from typing import Sequence

from app.mt5.market_data import CandleBar
from app.strategies.base import StrategySignal

logger = logging.getLogger("trading_agent.strategies.trend_pullback")


def compute_ema(series: list[float], period: int) -> list[float]:
    """Compute Exponential Moving Average recursively."""
    if len(series) < period:
        return [series[-1] if series else 0.0] * len(series)
    
    alpha = 2.0 / (period + 1)
    ema = [sum(series[:period]) / period]
    for price in series[period:]:
        ema.append(price * alpha + ema[-1] * (1.0 - alpha))
    
    # Pad leading values to match length
    padding = [ema[0]] * (len(series) - len(ema))
    return padding + ema


def compute_atr(candles: Sequence[CandleBar], period: int = 14) -> float:
    """Compute Average True Range for recent candles."""
    if len(candles) < 2:
        return 0.0010
    trs = []
    for i in range(1, len(candles)):
        h = candles[i].high
        l = candles[i].low
        prev_c = candles[i - 1].close
        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        trs.append(tr)
    recent_trs = trs[-period:] if len(trs) >= period else trs
    return sum(recent_trs) / len(recent_trs) if recent_trs else 0.0010


def compute_adx(candles: Sequence[CandleBar], period: int = 14) -> float:
    """Compute Directional Movement Index (ADX) using Wilder's Smoothing (RMA).
    
    Adheres strictly to Wilder's original recursive formula to prevent rolling-window spike artifacts.
    """
    if len(candles) < period + 1:
        return 20.0  # Default neutral trend strength if warmup short

    tr_list: list[float] = []
    dm_plus_list: list[float] = []
    dm_minus_list: list[float] = []

    for i in range(1, len(candles)):
        h, l, prev_c = candles[i].high, candles[i].low, candles[i - 1].close
        prev_h, prev_l = candles[i - 1].high, candles[i - 1].low

        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        up_move = h - prev_h
        down_move = prev_l - l

        dm_plus = up_move if up_move > down_move and up_move > 0 else 0.0
        dm_minus = down_move if down_move > up_move and down_move > 0 else 0.0

        tr_list.append(tr)
        dm_plus_list.append(dm_plus)
        dm_minus_list.append(dm_minus)

    if len(tr_list) < period:
        return 20.0

    # Wilder's Smoothing initialization (first period is simple sum)
    smooth_tr = sum(tr_list[:period])
    smooth_dmp = sum(dm_plus_list[:period])
    smooth_dmm = sum(dm_minus_list[:period])

    dx_list: list[float] = []

    def _calc_dx(tr_val: float, dmp_val: float, dmm_val: float) -> float:
        if tr_val <= 0:
            return 0.0
        di_plus = (dmp_val / tr_val) * 100.0
        di_minus = (dmm_val / tr_val) * 100.0
        denom = di_plus + di_minus
        return (abs(di_plus - di_minus) / denom * 100.0) if denom > 0 else 0.0

    dx_list.append(_calc_dx(smooth_tr, smooth_dmp, smooth_dmm))

    # Wilder's recursive smoothing: S_t = S_{t-1} - (S_{t-1} / period) + X_t
    for i in range(period, len(tr_list)):
        smooth_tr = smooth_tr - (smooth_tr / period) + tr_list[i]
        smooth_dmp = smooth_dmp - (smooth_dmp / period) + dm_plus_list[i]
        smooth_dmm = smooth_dmm - (smooth_dmm / period) + dm_minus_list[i]
        dx_list.append(_calc_dx(smooth_tr, smooth_dmp, smooth_dmm))

    if len(dx_list) < period:
        return sum(dx_list) / len(dx_list)

    # First ADX is simple average of first period DX values
    adx = sum(dx_list[:period]) / period
    for i in range(period, len(dx_list)):
        adx = (adx * (period - 1) + dx_list[i]) / period

    return adx


class TrendFollowingPullbackStrategy:
    """Quantitative implementation of H4/H1 Trend-Following Pullback."""

    strategy_id = "trend_pullback"
    version = "2.0"

    def __init__(self, adx_threshold: float = 20.0, target_rr: float = 2.0) -> None:
        self.adx_threshold = adx_threshold
        self.target_rr = target_rr

    def evaluate(
        self,
        symbol: str,
        h4_candles: Sequence[CandleBar],
        h1_candles: Sequence[CandleBar],
    ) -> StrategySignal:
        """Evaluate market regime on H4 and pullback trigger on H1."""
        if len(h4_candles) < 50 or len(h1_candles) < 50:
            return StrategySignal(
                symbol=symbol,
                timeframe="H1",
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                direction="FLAT",
                reason="Insufficient warmup bars (<50 bars on H4 or H1)",
            )

        # ---------------------------------------------------------
        # TIER 1: H4 MARKET REGIME
        # ---------------------------------------------------------
        h4_closes = [c.close for c in h4_candles]
        h4_ema50 = compute_ema(h4_closes, 50)
        h4_ema200 = compute_ema(h4_closes, 200)
        h4_adx = compute_adx(h4_candles, 14)

        current_h4_c = h4_closes[-1]
        is_uptrend = (h4_ema50[-1] > h4_ema200[-1]) and (current_h4_c > h4_ema50[-1]) and (h4_adx >= self.adx_threshold)
        is_downtrend = (h4_ema50[-1] < h4_ema200[-1]) and (current_h4_c < h4_ema50[-1]) and (h4_adx >= self.adx_threshold)

        if not is_uptrend and not is_downtrend:
            return StrategySignal(
                symbol=symbol,
                timeframe="H1",
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                direction="FLAT",
                reason=f"Regime Stand-Down: H4 ADX={h4_adx:.1f} (thresh={self.adx_threshold}) or EMAs tangled",
            )

        # ---------------------------------------------------------
        # TIER 2 & 3: H1 PULLBACK TO VALUE ZONE & TRIGGER CONFIRMATION
        # ---------------------------------------------------------
        h1_closes = [c.close for c in h1_candles]
        h1_ema21 = compute_ema(h1_closes, 21)
        h1_ema50 = compute_ema(h1_closes, 50)
        atr_h1 = compute_atr(h1_candles, 14)

        last_bar = h1_candles[-1]
        candle_range = last_bar.high - last_bar.low
        if candle_range <= 0:
            candle_range = 0.0001

        # UPTREND BUY SETUP
        if is_uptrend:
            # Check if pulled back into Value Zone (between EMA 21 and EMA 50)
            in_value_zone = (last_bar.low <= max(h1_ema21[-1], h1_ema50[-1])) and (last_bar.low >= min(h1_ema21[-1], h1_ema50[-1]) - atr_h1)
            
            # Stringent Rejection Pinbar:
            # 1. Lower wick >= 60% of candle range
            # 2. Lower wick >= 2x body
            # 3. Upper wick <= 25% of candle range
            body = abs(last_bar.close - last_bar.open)
            lower_wick = min(last_bar.open, last_bar.close) - last_bar.low
            upper_wick = last_bar.high - max(last_bar.open, last_bar.close)

            is_pinbar = (
                (lower_wick / candle_range >= 0.60)
                and (lower_wick >= 2.0 * body)
                and (upper_wick / candle_range <= 0.25)
            )

            # Forex-adapted Bullish Engulfing:
            # Current candle is bullish, previous candle was bearish.
            # Current body engulfs previous body AND current close breaks above previous high
            prev_bar = h1_candles[-2]
            is_engulfing = (
                (last_bar.close > last_bar.open)
                and (prev_bar.close < prev_bar.open)
                and (last_bar.close >= prev_bar.high)
                and (last_bar.open <= prev_bar.close)
            )

            if in_value_zone and (is_pinbar or is_engulfing):
                # Structural SL below recent swing low with ATR buffer
                recent_lows = [c.low for c in h1_candles[-5:]]
                swing_low = min(recent_lows)
                stop_loss = swing_low - (1.0 * atr_h1)
                entry_price = last_bar.close
                risk_dist = entry_price - stop_loss
                if risk_dist > 0:
                    take_profit = entry_price + (self.target_rr * risk_dist)
                    return StrategySignal(
                        symbol=symbol,
                        timeframe="H1",
                        strategy_id=self.strategy_id,
                        strategy_version=self.version,
                        direction="BUY",
                        entry_price=round(entry_price, 5),
                        stop_loss=round(stop_loss, 5),
                        take_profit=round(take_profit, 5),
                        reason=f"H4 Uptrend (ADX={h4_adx:.1f}) + H1 Value Pullback + Trigger ({'Pinbar' if is_pinbar else 'Engulfing'})",
                    )

        # DOWNTREND SELL SETUP
        if is_downtrend:
            # Check if pulled back up into Value Zone
            in_value_zone = (last_bar.high >= min(h1_ema21[-1], h1_ema50[-1])) and (last_bar.high <= max(h1_ema21[-1], h1_ema50[-1]) + atr_h1)

            # Stringent Bearish Rejection Pinbar:
            body = abs(last_bar.close - last_bar.open)
            upper_wick = last_bar.high - max(last_bar.open, last_bar.close)
            lower_wick = min(last_bar.open, last_bar.close) - last_bar.low

            is_pinbar = (
                (upper_wick / candle_range >= 0.60)
                and (upper_wick >= 2.0 * body)
                and (lower_wick / candle_range <= 0.25)
            )

            # Forex-adapted Bearish Engulfing:
            prev_bar = h1_candles[-2]
            is_engulfing = (
                (last_bar.close < last_bar.open)
                and (prev_bar.close > prev_bar.open)
                and (last_bar.close <= prev_bar.low)
                and (last_bar.open >= prev_bar.close)
            )

            if in_value_zone and (is_pinbar or is_engulfing):
                recent_highs = [c.high for c in h1_candles[-5:]]
                swing_high = max(recent_highs)
                stop_loss = swing_high + (1.0 * atr_h1)
                entry_price = last_bar.close
                risk_dist = stop_loss - entry_price
                if risk_dist > 0:
                    take_profit = entry_price - (self.target_rr * risk_dist)
                    return StrategySignal(
                        symbol=symbol,
                        timeframe="H1",
                        strategy_id=self.strategy_id,
                        strategy_version=self.version,
                        direction="SELL",
                        entry_price=round(entry_price, 5),
                        stop_loss=round(stop_loss, 5),
                        take_profit=round(take_profit, 5),
                        reason=f"H4 Downtrend (ADX={h4_adx:.1f}) + H1 Value Pullback + Trigger ({'Pinbar' if is_pinbar else 'Engulfing'})",
                    )

        return StrategySignal(
            symbol=symbol,
            timeframe="H1",
            strategy_id=self.strategy_id,
            strategy_version=self.version,
            direction="FLAT",
            reason="No pullback setup or trigger confirmed on H1",
        )
