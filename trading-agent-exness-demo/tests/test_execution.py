"""Unit tests verifying that order execution is hard-disabled in Milestone M0-M1."""

from __future__ import annotations

import pytest

from app.config import RiskConfig
from app.mt5.execution import DemoExecutionAdapter, ReadOnlyExecutionError
from app.mt5.market_data import SymbolSpec
from app.strategies.base import StrategySignal


class DummyAppConfig:
    def __init__(self, risk_pct: float = 0.25) -> None:
        self.execution_mode = "demo_auto"
        self.risk = RiskConfig(
            risk_per_trade_pct=risk_pct,
            max_total_open_risk_pct=0.50,
            max_daily_loss_pct=1.0,
            max_drawdown_pct=5.0,
            max_positions_per_symbol=1,
        )


def test_execution_adapter_blocks_all_order_operations_in_m0_m1() -> None:
    adapter = DemoExecutionAdapter()
    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.place_order(symbol="EURUSDm", volume=0.01)

    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.modify_order(ticket=12345, sl=1.0700)

    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.close_position(ticket=12345)


def test_calculate_lot_size_gold_xauusd() -> None:
    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25))
    # Balance: $100,000 -> 0.25% risk = $250 cash risk
    signal = StrategySignal(
        symbol="XAUUSD",
        timeframe="M15",
        strategy_id="baseline",
        strategy_version="1.0",
        direction="BUY",
        entry_price=2700.0,
        stop_loss=2690.0,  # $10 stop distance
        take_profit=2720.0,
        reason="Test Gold",
    )
    # Gold contract size: 100 oz. 100 oz * $10 stop dist = $1,000 risk per lot.
    # $250 / $1000 = 0.25 lots!
    spec = SymbolSpec(
        base_symbol="XAUUSD",
        broker_symbol="XAUUSDm",
        description="Gold vs US Dollar",
        currency_base="XAU",
        currency_profit="USD",
        currency_margin="USD",
        digits=2,
        point=0.01,
        tick_size=0.01,
        tick_value=1.0,
        contract_size=100.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=15,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    lots = adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
    assert lots == 0.25


def test_calculate_lot_size_forex_eurusd() -> None:
    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25))
    # Balance: $100,000 -> 0.25% risk = $250 cash risk
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="M15",
        strategy_id="baseline",
        strategy_version="1.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,  # 25 pips = 0.00250 dist
        take_profit=1.08500,
        reason="Test EUR",
    )
    # EURUSD contract size: 100,000 EUR. 100,000 * 0.00250 = $250 risk per lot.
    # $250 / $250 = 1.00 lots!
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="Euro vs US Dollar",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    lots = adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
    assert lots == 1.00


def test_calculate_lot_size_fails_closed_when_stop_loss_missing() -> None:
    from app.mt5.execution import ExecutionSafetyError

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25))
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=None,  # Missing!
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="explicit entry_price and stop_loss"):
        adapter.calculate_lot_size(signal, spec, account_balance=100000.0)


def test_calculate_lot_size_strictly_rounds_down() -> None:
    # Set risk budget such that raw_lots is 0.259
    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.259))
    signal = StrategySignal(
        symbol="XAUUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=2700.0,
        stop_loss=2690.0,  # $10 stop dist
        take_profit=2720.0,
    )
    spec = SymbolSpec(
        base_symbol="XAUUSD",
        broker_symbol="XAUUSDm",
        description="Gold",
        currency_base="XAU",
        currency_profit="USD",
        currency_margin="USD",
        digits=2,
        point=0.01,
        tick_size=0.01,
        tick_value=1.0,
        contract_size=100.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=15,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    # Balance: 100k -> 0.259% risk = $259. Cash risk per lot = $1,000. Raw lots = 0.259.
    # Round down (floor) must yield 0.25, NOT 0.26!
    lots = adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
    assert lots == 0.25


def test_calculate_lot_size_rejects_order_if_min_vol_exceeds_risk_budget() -> None:
    from app.mt5.execution import ExecutionSafetyError

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25))
    # Balance $1,000 -> 0.25% risk = $2.50 max budget
    # Stop distance = 100 pips on EURUSD -> 0.01 lot risks $10.00
    # $10.00 > $2.50 budget -> MUST REJECT, NOT inflate!
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07000,  # 100 pips dist
        take_profit=1.10000,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="Risk limit rejected"):
        adapter.calculate_lot_size(signal, spec, account_balance=1000.0)


def test_ensure_can_execute_fails_when_trade_not_allowed() -> None:
    from app.mt5.connection import AccountMetadata
    from app.mt5.execution import ExecutionSafetyError

    class MockConn:
        is_connected = True
        backend = object()

        def read_account_metadata(self) -> AccountMetadata:
            return AccountMetadata(
                login=464160066,
                server="Exness-MT5Trial17",
                trade_mode=0,
                trade_mode_label="DEMO",
                currency="USD",
                balance=100000.0,
                equity=100000.0,
                margin=0.0,
                margin_free=100000.0,
                margin_mode=2,
                leverage=500,
                trade_allowed=False,  # Blocked!
                trade_expert=True,
                is_verified_demo=True,
            )

    adapter = DemoExecutionAdapter(config=DummyAppConfig(), connection=MockConn())
    with pytest.raises(ExecutionSafetyError, match="Trade is not allowed"):
        adapter._ensure_can_execute()


def test_ensure_can_execute_fails_when_trade_expert_disabled() -> None:
    from app.mt5.connection import AccountMetadata
    from app.mt5.execution import ExecutionSafetyError

    class MockConn:
        is_connected = True
        backend = object()

        def read_account_metadata(self) -> AccountMetadata:
            return AccountMetadata(
                login=464160066,
                server="Exness-MT5Trial17",
                trade_mode=0,
                trade_mode_label="DEMO",
                currency="USD",
                balance=100000.0,
                equity=100000.0,
                margin=0.0,
                margin_free=100000.0,
                margin_mode=2,
                leverage=500,
                trade_allowed=True,
                trade_expert=False,  # Expert Advisors / Algo trading disabled!
                is_verified_demo=True,
            )

    adapter = DemoExecutionAdapter(config=DummyAppConfig(), connection=MockConn())
    with pytest.raises(ExecutionSafetyError, match="Automated trading"):
        adapter._ensure_can_execute()


def test_calculate_lot_size_ratchets_down_when_order_calc_profit_exceeds_budget() -> None:
    class MockMT5BackendWithProfitCalc:
        def symbol_info(self, symbol: str):
            from types import SimpleNamespace
            return SimpleNamespace(
                volume_min=0.01,
                volume_max=10.0,
                volume_step=0.01,
                trade_tick_size=0.00001,
                trade_tick_value=1.0,
                digits=5,
            )

        def order_calc_profit(self, action: int, symbol: str, volume: float, price_open: float, price_close: float) -> float:
            # Simulate a scenario where broker pricing causes $270 loss for 1.00 lot instead of $250
            return -270.0 * (volume / 1.00)

    class MockConn:
        is_connected = True
        backend = MockMT5BackendWithProfitCalc()

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25), connection=MockConn())
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    # Risk budget is $250. 1.00 lot would lose $270.
    # The ratchet loop will decrement lots step by step until volume loss <= $250 (i.e. 0.92 lot = -$248.40)
    lots = adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
    assert lots < 1.00
    assert lots == 0.92


def test_calculate_lot_size_fails_closed_when_order_calc_profit_returns_none() -> None:
    from app.mt5.execution import ExecutionSafetyError

    class MockMT5BackendNoneProfit:
        def symbol_info(self, symbol: str):
            from types import SimpleNamespace
            return SimpleNamespace(
                volume_min=0.01,
                volume_max=10.0,
                volume_step=0.01,
                trade_tick_size=0.00001,
                trade_tick_value=1.0,
                digits=5,
            )

        def order_calc_profit(self, action: int, symbol: str, volume: float, price_open: float, price_close: float) -> float | None:
            return None  # Terminal desynced or calculation failed

    class MockConn:
        is_connected = True
        backend = MockMT5BackendNoneProfit()

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25), connection=MockConn())
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="order_calc_profit returned None"):
        adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
