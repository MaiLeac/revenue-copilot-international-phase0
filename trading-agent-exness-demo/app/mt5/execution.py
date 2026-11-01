"""Execution adapter guard for Milestone M0-M1 (Strictly Read-Only)."""

from __future__ import annotations

from typing import Any


class ReadOnlyExecutionError(PermissionError):
    """Raised on any attempt to place, modify, or close orders during M0-M1."""


class DemoExecutionAdapter:
    """Hard-locked execution adapter for Milestone M0-M1.

    In M0-M1, order placement, modification, and closing are strictly prohibited.
    """

    def place_order(self, *args: Any, **kwargs: Any) -> None:
        raise ReadOnlyExecutionError(
            "SAFETY LOCK: Order placement is disabled in Milestone M0-M1 (Read-Only Connector)."
        )

    def modify_order(self, *args: Any, **kwargs: Any) -> None:
        raise ReadOnlyExecutionError(
            "SAFETY LOCK: Order modification is disabled in Milestone M0-M1 (Read-Only Connector)."
        )

    def close_position(self, *args: Any, **kwargs: Any) -> None:
        raise ReadOnlyExecutionError(
            "SAFETY LOCK: Position closing is disabled in Milestone M0-M1 (Read-Only Connector)."
        )
