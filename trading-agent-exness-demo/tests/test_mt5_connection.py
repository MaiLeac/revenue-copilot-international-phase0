"""Unit tests for MT5 connection manager, account verification, and symbol discovery using mocked MT5."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.config import load_config
from app.main import run_diagnostic
from app.mt5.connection import (
    ACCOUNT_TRADE_MODE_DEMO,
    ACCOUNT_TRADE_MODE_REAL,
    LiveAccountBlockedError,
    MT5ConnectionError,
    MT5ConnectionManager,
)
from app.mt5.market_data import (
    MarketDataError,
    MT5MarketDataReader,
    SymbolValidationError,
)


class MockMT5Backend:
    """Deterministic mock of the MetaTrader5 Python package."""

    def __init__(
        self,
        init_ok: bool = True,
        trade_mode: int = ACCOUNT_TRADE_MODE_DEMO,
        server: str = "Exness-MT5Trial9",
        symbols: list[str] | None = None,
    ) -> None:
        self.init_ok = init_ok
        self.trade_mode = trade_mode
        self.server = server
        self.shutdown_called = False
        self.symbol_names = symbols if symbols is not None else ["XAUUSDm", "XAGUSDm", "EURUSDm"]
        self.now_ts = int(datetime.now(timezone.utc).timestamp())

    def initialize(self, **kwargs: Any) -> bool:
        return self.init_ok

    def shutdown(self) -> None:
        self.shutdown_called = True

    def last_error(self) -> tuple[int, str]:
        return (-1, "Mock terminal error")

    def terminal_info(self) -> SimpleNamespace:
        return SimpleNamespace(connected=True, trade_allowed=False)

    def account_info(self) -> SimpleNamespace:
        return SimpleNamespace(
            login=12345678,
            server=self.server,
            trade_mode=self.trade_mode,
            currency="USD",
            balance=10000.0,
            equity=10000.0,
            margin=0.0,
            margin_free=10000.0,
            margin_mode=2,
            leverage=200,
            trade_allowed=True,
            trade_expert=True,
        )

    def symbols_get(self) -> list[SimpleNamespace]:
        return [SimpleNamespace(name=n) for n in self.symbol_names]

    def symbol_select(self, symbol: str, enable: bool) -> bool:
        return symbol in self.symbol_names

    def symbol_info(self, symbol: str) -> SimpleNamespace | None:
        if symbol not in self.symbol_names:
            return None
        is_fx = symbol.startswith("EURUSD")
        return SimpleNamespace(
            name=symbol,
            description=f"Mock {symbol}",
            currency_base=symbol[:3],
            currency_profit="USD",
            currency_margin=symbol[:3],
            digits=5 if is_fx else 2,
            point=0.00001 if is_fx else 0.01,
            trade_tick_size=0.00001 if is_fx else 0.01,
            trade_tick_value=1.0,
            trade_contract_size=100000.0 if is_fx else 100.0,
            volume_min=0.01,
            volume_max=100.0,
            volume_step=0.01,
            trade_stops_level=10,
            spread=12 if is_fx else 180,
            spread_float=True,
            trade_mode=4,
            visible=True,
        )

    def symbol_info_tick(self, symbol: str) -> SimpleNamespace | None:
        if symbol not in self.symbol_names:
            return None
        if symbol.startswith("EURUSD"):
            return SimpleNamespace(
                time=self.now_ts - 5,
                bid=1.08500,
                ask=1.08512,
                last=1.08505,
                volume=10.0,
            )
        return SimpleNamespace(
            time=self.now_ts - 5,
            bid=2750.00,
            ask=2751.80,
            last=2750.90,
            volume=5.0,
        )

    def copy_rates_from_pos(
        self, symbol: str, timeframe: int, start_pos: int, count: int
    ) -> list[dict[str, Any]]:
        step = 900 if timeframe == 15 else 3600
        bars: list[dict[str, Any]] = []
        base_time = self.now_ts - (count - 1) * step
        for i in range(count):
            bars.append(
                {
                    "time": base_time + i * step,
                    "open": 100.0 + i * 0.1,
                    "high": 100.5 + i * 0.1,
                    "low": 99.5 + i * 0.1,
                    "close": 100.2 + i * 0.1,
                    "tick_volume": 150,
                    "spread": 15,
                    "real_volume": 0,
                }
            )
        return bars


def _load_test_cfg() -> Any:
    repo_root = Path(__file__).resolve().parents[1]
    return load_config(repo_root / "config" / "demo.yaml", env_override={"DEMO_ONLY": "true"})


def test_unavailable_terminal_raises_clear_error() -> None:
    cfg = _load_test_cfg()
    mock_mt5 = MockMT5Backend(init_ok=False)
    conn = MT5ConnectionManager(cfg, mt5_backend=mock_mt5)
    with pytest.raises(MT5ConnectionError, match="unavailable or initialization failed"):
        conn.connect()


def test_real_account_trade_mode_is_rejected() -> None:
    cfg = _load_test_cfg()
    mock_mt5 = MockMT5Backend(trade_mode=ACCOUNT_TRADE_MODE_REAL, server="Exness-MT5Trial9")
    conn = MT5ConnectionManager(cfg, mt5_backend=mock_mt5)
    with pytest.raises(LiveAccountBlockedError, match="SAFETY LOCK TRIPPED"):
        conn.connect()
    assert mock_mt5.shutdown_called is True


def test_real_server_name_is_rejected_even_if_trade_mode_demo() -> None:
    cfg = _load_test_cfg()
    mock_mt5 = MockMT5Backend(trade_mode=ACCOUNT_TRADE_MODE_DEMO, server="Exness-MT5Real14")
    conn = MT5ConnectionManager(cfg, mt5_backend=mock_mt5)
    with pytest.raises(LiveAccountBlockedError, match="live/real indicator"):
        conn.connect()
    assert mock_mt5.shutdown_called is True


def test_symbol_discovery_and_invalid_symbol_error() -> None:
    cfg = _load_test_cfg()
    mock_mt5 = MockMT5Backend(symbols=["XAUUSDm", "EURUSDm"])  # Missing XAGUSD
    conn = MT5ConnectionManager(cfg, mt5_backend=mock_mt5)
    conn.connect()
    reader = MT5MarketDataReader(conn, cfg)

    spec = reader.read_symbol_spec("XAUUSD")
    assert spec.broker_symbol == "XAUUSDm"
    assert spec.contract_size == 100.0

    with pytest.raises(SymbolValidationError, match="Could not discover any broker symbol"):
        reader.read_symbol_spec("XAGUSD")

    with pytest.raises(SymbolValidationError, match="not in the configured allowlist"):
        reader.read_symbol_spec("GBPUSD")


def test_missing_candles_from_mt5_raises_error() -> None:
    cfg = _load_test_cfg()
    mock_mt5 = MockMT5Backend()
    mock_mt5.copy_rates_from_pos = lambda *a, **kw: []  # type: ignore[method-assign]
    conn = MT5ConnectionManager(cfg, mt5_backend=mock_mt5)
    conn.connect()
    reader = MT5MarketDataReader(conn, cfg)

    with pytest.raises(MarketDataError, match="Missing candles"):
        reader.read_candles("EURUSD", "M15", count=60)


def test_full_diagnostic_runner_passes_with_mock_demo_terminal() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    mock_mt5 = MockMT5Backend()
    summary = run_diagnostic(
        config_path=str(repo_root / "config" / "demo.yaml"),
        mt5_backend=mock_mt5,
    )
    assert summary["account"]["is_verified_demo"] is True
    assert set(summary["symbols"].keys()) == {"XAGUSD", "EURUSD", "XAUUSD"}
    assert len(summary["quality_reports"]) == 6  # 3 symbols * 2 timeframes (M15, H1)
    assert summary["kill_switch_tripped"] is False
