"""Unit tests verifying that order execution is hard-disabled in Milestone M0-M1."""

from __future__ import annotations

import pytest

from app.mt5.execution import DemoExecutionAdapter, ReadOnlyExecutionError


def test_execution_adapter_blocks_all_order_operations_in_m0_m1() -> None:
    adapter = DemoExecutionAdapter()
    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.place_order(symbol="EURUSDm", volume=0.01)

    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.modify_order(ticket=12345, sl=1.0700)

    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.close_position(ticket=12345)
