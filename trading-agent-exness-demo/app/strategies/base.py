"""Strategy interface definitions (Milestone M2 foundation)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

SignalDirection = Literal["BUY", "SELL", "FLAT"]


@dataclass(frozen=True)
class StrategySignal:
    symbol: str
    timeframe: str
    strategy_id: str
    strategy_version: str
    direction: SignalDirection
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    reason: str = ""


class StrategyProtocol(Protocol):
    """Deterministic strategy interface (single baseline across multiple symbols per Decision 7A)."""

    @property
    def strategy_id(self) -> str: ...

    @property
    def version(self) -> str: ...
