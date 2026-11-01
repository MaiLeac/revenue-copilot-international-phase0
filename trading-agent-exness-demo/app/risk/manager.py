"""Risk Manager interface (scheduled for full implementation in Milestone M3)."""

from __future__ import annotations

from app.config import AppConfig
from app.risk.kill_switch import KillSwitch


class RiskManager:
    """Deterministic risk gatekeeper. Cannot be bypassed by LLM or Strategy Engine."""

    def __init__(self, config: AppConfig, kill_switch: KillSwitch) -> None:
        self._config = config
        self._kill_switch = kill_switch
