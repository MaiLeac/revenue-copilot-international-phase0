"""Data Quality Gate: detects stale ticks, missing/gap candles, invalid OHLC, and excessive spreads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.config import AppConfig
from app.mt5.market_data import CandleBar, TickSnapshot

TIMEFRAME_SECONDS: dict[str, int] = {
    "M1": 60,
    "M5": 300,
    "M15": 900,
    "M30": 1800,
    "H1": 3600,
    "H4": 14400,
    "D1": 86400,
}


class DataQualityError(ValueError):
    """Raised when market data fails freshness, completeness, or integrity checks."""


@dataclass(frozen=True)
class DataQualityReport:
    base_symbol: str
    broker_symbol: str
    timeframe: str
    candle_count: int
    latest_candle_time_utc: datetime
    latest_tick_time_utc: datetime
    current_spread_points: int
    max_allowed_spread_points: int
    passed: bool


class DataQualityGate:
    """Enforces strict fail-closed validation on ticks and candle series."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def validate_tick(
        self,
        base_symbol: str,
        tick: TickSnapshot,
        now_utc: datetime | None = None,
    ) -> None:
        """Check tick validity, staleness, and excessive spread."""
        now = now_utc or datetime.now(timezone.utc)
        if tick.bid <= 0 or tick.ask <= 0 or tick.ask < tick.bid:
            raise DataQualityError(
                f"Invalid tick prices for {tick.symbol}: bid={tick.bid}, ask={tick.ask}"
            )

        age_sec = (now - tick.timestamp_utc).total_seconds()
        max_tick_age = self._config.data_quality.max_tick_age_seconds
        if self._config.safety.reject_stale_data and age_sec > max_tick_age:
            raise DataQualityError(
                f"Stale tick for {tick.symbol}: age={age_sec:.1f}s exceeds max_tick_age_seconds={max_tick_age}s"
            )

        max_spread = self._config.data_quality.get_max_spread(base_symbol.upper())
        if self._config.safety.reject_excessive_spread and tick.spread_points > max_spread:
            raise DataQualityError(
                f"Excessive spread for {tick.symbol}: spread_points={tick.spread_points} "
                f"exceeds max_spread_points={max_spread}"
            )

    def validate_candles(
        self,
        base_symbol: str,
        timeframe: str,
        candles: list[CandleBar],
        now_utc: datetime | None = None,
    ) -> None:
        """Check candle count, ordering, OHLC integrity, staleness, and unexpected intra-week gaps."""
        now = now_utc or datetime.now(timezone.utc)
        tf_clean = timeframe.strip().upper()
        min_count = self._config.data_quality.min_candle_count

        if not candles or len(candles) < min_count:
            actual = 0 if not candles else len(candles)
            raise DataQualityError(
                f"Insufficient candles for {base_symbol} ({tf_clean}): got {actual}, require >= {min_count}"
            )

        expected_step = TIMEFRAME_SECONDS.get(tf_clean, 900)
        prev_time: datetime | None = None

        for idx, bar in enumerate(candles):
            if bar.open <= 0 or bar.high <= 0 or bar.low <= 0 or bar.close <= 0:
                raise DataQualityError(
                    f"Non-positive OHLC price at index {idx} ({bar.open_time_utc.isoformat()}) for {bar.symbol}"
                )
            if bar.high < bar.low or bar.open > bar.high or bar.open < bar.low or bar.close > bar.high or bar.close < bar.low:
                raise DataQualityError(
                    f"Corrupted OHLC bounds at index {idx} ({bar.open_time_utc.isoformat()}) for {bar.symbol}: "
                    f"O={bar.open} H={bar.high} L={bar.low} C={bar.close}"
                )
            if prev_time is not None:
                delta = (bar.open_time_utc - prev_time).total_seconds()
                if delta <= 0:
                    raise DataQualityError(
                        f"Non-monotonic candle timestamps for {bar.symbol} at {bar.open_time_utc.isoformat()}"
                    )
                # Reject intra-session missing candles (ignore weekend closures >= 48h)
                if delta > expected_step and delta < 48 * 3600:
                    missing_bars = int(delta // expected_step) - 1
                    raise DataQualityError(
                        f"Missing candles detected for {bar.symbol} ({tf_clean}): gap of {delta:.0f}s "
                        f"(~{missing_bars} missing bars) between {prev_time.isoformat()} and {bar.open_time_utc.isoformat()}"
                    )
            prev_time = bar.open_time_utc

        latest_bar = candles[-1]
        candle_age = (now - latest_bar.open_time_utc).total_seconds()
        max_candle_age = self._config.data_quality.get_max_candle_age(tf_clean)
        if self._config.safety.reject_stale_data and candle_age > max_candle_age:
            raise DataQualityError(
                f"Stale candle data for {latest_bar.symbol} ({tf_clean}): "
                f"latest bar {latest_bar.open_time_utc.isoformat()} is {candle_age:.0f}s old "
                f"(max allowed {max_candle_age}s)"
            )

    def evaluate(
        self,
        base_symbol: str,
        timeframe: str,
        tick: TickSnapshot,
        candles: list[CandleBar],
        now_utc: datetime | None = None,
    ) -> DataQualityReport:
        """Run full tick and candle quality checks and return a structured report."""
        self.validate_tick(base_symbol=base_symbol, tick=tick, now_utc=now_utc)
        self.validate_candles(
            base_symbol=base_symbol, timeframe=timeframe, candles=candles, now_utc=now_utc
        )
        return DataQualityReport(
            base_symbol=base_symbol.upper(),
            broker_symbol=tick.symbol,
            timeframe=timeframe.upper(),
            candle_count=len(candles),
            latest_candle_time_utc=candles[-1].open_time_utc,
            latest_tick_time_utc=tick.timestamp_utc,
            current_spread_points=tick.spread_points,
            max_allowed_spread_points=self._config.data_quality.get_max_spread(
                base_symbol.upper()
            ),
            passed=True,
        )
