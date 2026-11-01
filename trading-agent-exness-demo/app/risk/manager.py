"""Risk Manager: continuous monitoring of account equity, daily loss, and drawdown limits.

Persists state to disk to survive unexpected crashes and daemon restarts.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from app.config import AppConfig
from app.risk.kill_switch import KillSwitch

logger = logging.getLogger("trading_agent.risk.manager")


@dataclass
class RiskState:
    current_day: date
    day_start_equity: float
    peak_equity: float
    current_equity: float
    daily_pnl_pct: float
    drawdown_pct: float


class RiskManager:
    """Deterministic risk gatekeeper. Enforces hard daily loss and peak-to-trough drawdown limits with disk persistence."""

    def __init__(
        self,
        config: AppConfig,
        kill_switch: KillSwitch,
        state_file: Path | None = None,
    ) -> None:
        self.config = config
        self.kill_switch = kill_switch
        self._state_file = state_file
        self._current_day: date = datetime.now(timezone.utc).date()
        self._day_start_equity: float | None = None
        self._peak_equity: float | None = None

        # Load persisted risk metrics across restarts
        if self._state_file and self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                saved_day = date.fromisoformat(data["current_day"])
                today = datetime.now(timezone.utc).date()
                if saved_day == today:
                    self._current_day = saved_day
                    self._day_start_equity = float(data["day_start_equity"])
                    self._peak_equity = float(data["peak_equity"])
                    logger.info(
                        f"RiskManager restored today's state: start_equity={self._day_start_equity:.2f}, "
                        f"peak_equity={self._peak_equity:.2f}"
                    )
                else:
                    # New calendar day, keep peak equity but reset day start
                    self._peak_equity = float(data.get("peak_equity", 0.0)) or None
            except Exception as e:
                logger.warning(f"Could not load RiskManager state from {self._state_file}: {e}")

    def _persist(self, current_equity: float) -> None:
        if not self._state_file:
            return
        try:
            payload = {
                "current_day": self._current_day.isoformat(),
                "day_start_equity": self._day_start_equity,
                "peak_equity": self._peak_equity,
                "last_equity": current_equity,
                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            tmp = self._state_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp.replace(self._state_file)
        except Exception as e:
            logger.error(f"Failed to persist RiskManager state to {self._state_file}: {e}")

    def evaluate_equity(self, current_equity: float) -> RiskState:
        """Evaluate account equity against daily loss and maximum drawdown thresholds."""
        today = datetime.now(timezone.utc).date()

        # Day rollover reset
        if today != self._current_day or self._day_start_equity is None:
            self._current_day = today
            self._day_start_equity = current_equity
            logger.info(
                f"RiskManager: Day start initialized for {today} with equity={self._day_start_equity:.2f}"
            )

        if self._peak_equity is None or current_equity > self._peak_equity:
            self._peak_equity = current_equity

        # Daily loss calculation
        daily_loss_cash = self._day_start_equity - current_equity
        daily_loss_pct = round((daily_loss_cash / self._day_start_equity) * 100.0, 4) if self._day_start_equity > 0 else 0.0

        # Drawdown calculation from peak
        drawdown_cash = self._peak_equity - current_equity
        drawdown_pct = round((drawdown_cash / self._peak_equity) * 100.0, 4) if self._peak_equity > 0 else 0.0

        state = RiskState(
            current_day=self._current_day,
            day_start_equity=self._day_start_equity,
            peak_equity=self._peak_equity,
            current_equity=current_equity,
            daily_pnl_pct=-daily_loss_pct,
            drawdown_pct=drawdown_pct,
        )

        self._persist(current_equity)

        # Enforce max daily loss
        if daily_loss_pct >= self.config.risk.max_daily_loss_pct:
            reason = (
                f"Max daily loss exceeded: current daily drop = {daily_loss_pct:.2f}% "
                f"(limit: {self.config.risk.max_daily_loss_pct:.2f}%)"
            )
            logger.critical(reason)
            self.kill_switch.trip(reason=reason, source="RiskManager.DailyLoss")
            self.kill_switch.assert_healthy()

        # Enforce max peak-to-trough drawdown
        if drawdown_pct >= self.config.risk.max_drawdown_pct:
            reason = (
                f"Max drawdown limit exceeded: current drawdown = {drawdown_pct:.2f}% "
                f"(limit: {self.config.risk.max_drawdown_pct:.2f}%)"
            )
            logger.critical(reason)
            self.kill_switch.trip(reason=reason, source="RiskManager.MaxDrawdown")
            self.kill_switch.assert_healthy()

        return state
