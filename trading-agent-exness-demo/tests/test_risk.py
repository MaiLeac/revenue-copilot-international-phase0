"""Unit tests for KillSwitch and Risk safety locks."""

from __future__ import annotations

import pytest

from app.config import RiskConfig
from app.risk.kill_switch import KillSwitch
from app.risk.manager import RiskManager


def test_kill_switch_cannot_be_disabled() -> None:
    with pytest.raises(ValueError, match="cannot be initialized as disabled"):
        KillSwitch(enabled=False)


def test_kill_switch_trips_and_blocks_operations() -> None:
    ks = KillSwitch(enabled=True)
    assert ks.is_tripped is False
    ks.assert_healthy()

    event = ks.trip(reason="Stale M15 candle on XAUUSDm", source="DataQualityGate")
    assert ks.is_tripped is True
    assert event.source == "DataQualityGate"

    with pytest.raises(RuntimeError, match="KILL SWITCH ACTIVE"):
        ks.assert_healthy()


class DummyConfig:
    def __init__(self, daily_loss_pct: float = 1.0, drawdown_pct: float = 5.0) -> None:
        self.risk = RiskConfig(
            risk_per_trade_pct=0.25,
            max_total_open_risk_pct=0.50,
            max_daily_loss_pct=daily_loss_pct,
            max_drawdown_pct=drawdown_pct,
            max_positions_per_symbol=1,
        )


def test_risk_manager_healthy_under_limits() -> None:
    cfg = DummyConfig(daily_loss_pct=1.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)
    rm = RiskManager(config=cfg, kill_switch=ks)

    state = rm.evaluate_equity(100000.0)
    assert state.daily_pnl_pct == 0.0
    assert state.drawdown_pct == 0.0
    assert not ks.is_tripped

    state = rm.evaluate_equity(99500.0)  # -0.5% daily drop
    assert state.daily_pnl_pct == -0.5
    assert not ks.is_tripped


def test_risk_manager_trips_on_daily_loss_limit() -> None:
    cfg = DummyConfig(daily_loss_pct=1.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)
    rm = RiskManager(config=cfg, kill_switch=ks)

    rm.evaluate_equity(100000.0)  # Day start = 100k
    with pytest.raises(RuntimeError, match="Max daily loss exceeded"):
        rm.evaluate_equity(98900.0)  # -1.1% daily drop -> trips!

    assert ks.is_tripped
    assert "DailyLoss" in ks.last_event.source


def test_risk_manager_trips_on_max_drawdown() -> None:
    cfg = DummyConfig(daily_loss_pct=10.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)
    rm = RiskManager(config=cfg, kill_switch=ks)

    rm.evaluate_equity(100000.0)
    rm.evaluate_equity(110000.0)  # Peak = 110k
    with pytest.raises(RuntimeError, match="Max drawdown limit exceeded"):
        rm.evaluate_equity(104000.0)  # Drop from 110k to 104k = 5.45% drawdown -> trips!

    assert ks.is_tripped
    assert "MaxDrawdown" in ks.last_event.source
