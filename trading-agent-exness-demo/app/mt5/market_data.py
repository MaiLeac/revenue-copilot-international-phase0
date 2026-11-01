"""Symbol discovery, contract specification reader, and candle/tick market data reader."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.config import AppConfig
from app.mt5.connection import MT5ConnectionError, MT5ConnectionManager


class SymbolValidationError(ValueError):
    """Raised when an allowed symbol cannot be discovered or has invalid contract specs."""


class MarketDataError(RuntimeError):
    """Raised when candle or tick data cannot be retrieved from MT5."""


TIMEFRAME_MAP: dict[str, int] = {
    "M1": 1,
    "M5": 5,
    "M15": 15,
    "M30": 30,
    "H1": 16385,
    "H4": 16388,
    "D1": 16408,
}

# Common Exness suffixes (Standard: m, Raw/Zero: z, Pro: p or none, micro: c)
COMMON_EXNESS_SUFFIXES = ("", "m", "c", "z", "i", ".a", "_i")


@dataclass(frozen=True)
class SymbolSpec:
    base_symbol: str
    broker_symbol: str
    description: str
    currency_base: str
    currency_profit: str
    currency_margin: str
    digits: int
    point: float
    tick_size: float
    tick_value: float
    contract_size: float
    volume_min: float
    volume_max: float
    volume_step: float
    stops_level: int
    spread_points: int
    spread_float: bool
    trade_mode: int
    visible: bool


@dataclass(frozen=True)
class TickSnapshot:
    symbol: str
    timestamp_utc: datetime
    bid: float
    ask: float
    last: float
    volume: float
    spread_price: float
    spread_points: int


@dataclass(frozen=True)
class CandleBar:
    symbol: str
    timeframe: str
    open_time_utc: datetime
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    spread: int
    real_volume: int


class MT5MarketDataReader:
    """Read-only adapter for discovering broker symbols, contract specs, ticks, and candles."""

    def __init__(self, connection: MT5ConnectionManager, config: AppConfig) -> None:
        self._conn = connection
        self._config = config
        self._mt5 = connection.backend

    def discover_broker_symbol(self, base_symbol: str) -> str:
        """Discover the exact broker symbol name for a base allowlist symbol (e.g. XAUUSD -> XAUUSDm)."""
        self._ensure_connected()
        clean_base = base_symbol.strip().upper()
        if clean_base not in self._config.symbols.allowed:
            raise SymbolValidationError(
                f"Symbol '{clean_base}' is not in the configured allowlist: {self._config.symbols.allowed}"
            )

        all_symbols = self._mt5.symbols_get()
        if not all_symbols:
            raise SymbolValidationError(
                f"MT5 symbols_get() returned no symbols while looking up '{clean_base}'."
            )

        available_names = {str(getattr(s, "name", "")): s for s in all_symbols}

        # 1. Try exact match and standard Exness suffix candidates in priority order
        for suffix in COMMON_EXNESS_SUFFIXES:
            candidate = f"{clean_base}{suffix}"
            if candidate in available_names:
                return candidate

        # 2. Case-insensitive prefix fallback only if unambiguous
        prefix_matches = [
            name for name in available_names if name.upper().startswith(clean_base)
        ]
        if len(prefix_matches) == 1:
            return prefix_matches[0]
        if len(prefix_matches) > 1:
            raise SymbolValidationError(
                f"Ambiguous broker symbols for '{clean_base}': {sorted(prefix_matches)}. "
                "Configure exact broker symbol in allowlist."
            )

        raise SymbolValidationError(
            f"Could not discover any broker symbol matching allowlist symbol '{clean_base}'."
        )

    def read_symbol_spec(self, base_symbol: str) -> SymbolSpec:
        """Discover, select in MarketWatch, and validate contract specifications for a symbol."""
        self._ensure_connected()
        broker_symbol = self.discover_broker_symbol(base_symbol)

        selected = self._mt5.symbol_select(broker_symbol, True)
        if not selected:
            raise SymbolValidationError(
                f"Failed to select symbol '{broker_symbol}' in MT5 MarketWatch."
            )

        info = self._mt5.symbol_info(broker_symbol)
        if info is None:
            raise SymbolValidationError(
                f"MT5 symbol_info('{broker_symbol}') returned None."
            )

        point = float(getattr(info, "point", 0.0))
        tick_size = float(getattr(info, "trade_tick_size", 0.0))
        tick_value = float(getattr(info, "trade_tick_value", 0.0))
        contract_size = float(getattr(info, "trade_contract_size", 0.0))
        volume_min = float(getattr(info, "volume_min", 0.0))
        volume_max = float(getattr(info, "volume_max", 0.0))
        volume_step = float(getattr(info, "volume_step", 0.0))

        # Fail closed if contract specifications are invalid or zero
        if point <= 0 or tick_size <= 0 or contract_size <= 0:
            raise SymbolValidationError(
                f"Invalid contract specifications for '{broker_symbol}': "
                f"point={point}, tick_size={tick_size}, contract_size={contract_size}"
            )
        if volume_min <= 0 or volume_step <= 0 or volume_max < volume_min:
            raise SymbolValidationError(
                f"Invalid volume specifications for '{broker_symbol}': "
                f"min={volume_min}, max={volume_max}, step={volume_step}"
            )

        return SymbolSpec(
            base_symbol=base_symbol.strip().upper(),
            broker_symbol=broker_symbol,
            description=str(getattr(info, "description", "")),
            currency_base=str(getattr(info, "currency_base", "")),
            currency_profit=str(getattr(info, "currency_profit", "")),
            currency_margin=str(getattr(info, "currency_margin", "")),
            digits=int(getattr(info, "digits", 0)),
            point=point,
            tick_size=tick_size,
            tick_value=tick_value,
            contract_size=contract_size,
            volume_min=volume_min,
            volume_max=volume_max,
            volume_step=volume_step,
            stops_level=int(getattr(info, "trade_stops_level", 0)),
            spread_points=int(getattr(info, "spread", 0)),
            spread_float=bool(getattr(info, "spread_float", True)),
            trade_mode=int(getattr(info, "trade_mode", 0)),
            visible=bool(getattr(info, "visible", True)),
        )

    def read_tick(self, base_symbol: str) -> TickSnapshot:
        """Read latest tick and compute current spread in price and points."""
        spec = self.read_symbol_spec(base_symbol)
        tick = self._mt5.symbol_info_tick(spec.broker_symbol)
        if tick is None:
            raise MarketDataError(
                f"MT5 symbol_info_tick('{spec.broker_symbol}') returned None."
            )

        bid = float(getattr(tick, "bid", 0.0))
        ask = float(getattr(tick, "ask", 0.0))
        time_sec = int(getattr(tick, "time", 0))
        if bid <= 0 or ask <= 0 or ask < bid or time_sec <= 0:
            raise MarketDataError(
                f"Invalid tick data for '{spec.broker_symbol}': bid={bid}, ask={ask}, time={time_sec}"
            )

        spread_price = round(ask - bid, spec.digits)
        spread_points = int(round((ask - bid) / spec.point))

        return TickSnapshot(
            symbol=spec.broker_symbol,
            timestamp_utc=datetime.fromtimestamp(time_sec, tz=timezone.utc),
            bid=bid,
            ask=ask,
            last=float(getattr(tick, "last", 0.0)),
            volume=float(getattr(tick, "volume", 0.0)),
            spread_price=spread_price,
            spread_points=spread_points,
        )

    def read_candles(
        self, base_symbol: str, timeframe: str, count: int = 100
    ) -> list[CandleBar]:
        """Read historical candles for an allowed symbol and timeframe."""
        tf_clean = timeframe.strip().upper()
        if tf_clean not in TIMEFRAME_MAP:
            raise ValueError(f"Unsupported timeframe '{tf_clean}'.")
        if count <= 0:
            raise ValueError("Candle count must be positive.")

        spec = self.read_symbol_spec(base_symbol)
        mt5_tf = getattr(self._mt5, f"TIMEFRAME_{tf_clean}", TIMEFRAME_MAP[tf_clean])

        rates = self._mt5.copy_rates_from_pos(spec.broker_symbol, mt5_tf, 0, count)
        if rates is None or len(rates) == 0:
            raise MarketDataError(
                f"Missing candles: copy_rates_from_pos('{spec.broker_symbol}', '{tf_clean}', {count}) returned empty."
            )

        candles: list[CandleBar] = []
        for row in rates:
            # Supports both numpy structured rows (dict/index access) and object attributes
            t_sec = int(self._field(row, "time"))
            candles.append(
                CandleBar(
                    symbol=spec.broker_symbol,
                    timeframe=tf_clean,
                    open_time_utc=datetime.fromtimestamp(t_sec, tz=timezone.utc),
                    open=float(self._field(row, "open")),
                    high=float(self._field(row, "high")),
                    low=float(self._field(row, "low")),
                    close=float(self._field(row, "close")),
                    tick_volume=int(self._field(row, "tick_volume")),
                    spread=int(self._field(row, "spread")),
                    real_volume=int(self._field(row, "real_volume", 0)),
                )
            )
        return candles

    def _ensure_connected(self) -> None:
        if not self._conn.is_connected:
            raise MT5ConnectionError("MT5 connection is not active.")

    @staticmethod
    def _field(row: Any, key: str, default: Any = None) -> Any:
        if isinstance(row, dict):
            return row.get(key, default)
        try:
            return row[key]
        except Exception:
            return getattr(row, key, default)
