"""Unit tests for KillSwitch and Risk safety locks."""

from __future__ import annotations

import pytest

from app.risk.kill_switch import KillSwitch


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
