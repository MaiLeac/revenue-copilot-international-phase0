"""Kill Switch state machine: halts operation when safety, connection, or risk checks fail.

Persists state to disk to prevent crash-restart bypasses.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("trading_agent.risk.kill_switch")


class KillSwitchTrippedError(RuntimeError):
    """Raised when KillSwitch fails to persist or is asserted while active."""
    pass


@dataclass(frozen=True)
class KillSwitchEvent:
    triggered_at_utc: datetime
    reason: str
    source: str


class KillSwitch:
    """Fail-closed kill switch that blocks any further operation once tripped and persists across restarts."""

    def __init__(self, enabled: bool = True, state_file: Path | None = None) -> None:
        if not enabled:
            raise ValueError("Safety violation: KillSwitch cannot be initialized as disabled.")
        self._state_file = state_file
        self._tripped = False
        self._event: KillSwitchEvent | None = None

        # Load persisted state from disk if present
        if self._state_file and self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                if data.get("tripped"):
                    self._tripped = True
                    evt = data.get("event") or {}
                    self._event = KillSwitchEvent(
                        triggered_at_utc=datetime.fromisoformat(evt["triggered_at_utc"]),
                        reason=evt.get("reason", "Unknown persisted reason"),
                        source=evt.get("source", "persisted"),
                    )
                    logger.warning(
                        f"KillSwitch restored TRIPPED state from {self._state_file}: {self._event.reason}"
                    )
            except Exception as e:
                logger.error(f"Failed to load KillSwitch state from {self._state_file}: {e}")
                # Fail-closed: assume tripped if state file is corrupted
                self._tripped = True
                self._event = KillSwitchEvent(
                    triggered_at_utc=datetime.now(timezone.utc),
                    reason=f"State file corrupted, fail-closed: {e}",
                    source="state_file_error",
                )

    @property
    def is_tripped(self) -> bool:
        return self._tripped

    @property
    def last_event(self) -> KillSwitchEvent | None:
        return self._event

    def _persist(self) -> None:
        if not self._state_file:
            return
        try:
            state_data = {
                "tripped": self._tripped,
                "event": {
                    "triggered_at_utc": self._event.triggered_at_utc.isoformat(),
                    "reason": self._event.reason,
                    "source": self._event.source,
                }
                if self._event
                else None,
            }
            tmp = self._state_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
            tmp.replace(self._state_file)
        except Exception as e:
            err_msg = f"CRITICAL: Could not persist KillSwitch state to {self._state_file}: {e}. Failing closed."
            logger.critical(err_msg)
            raise KillSwitchTrippedError(err_msg) from e

    def trip(self, reason: str, source: str = "system") -> KillSwitchEvent:
        """Trip the kill switch, persist to disk, and record the root cause."""
        if not self._tripped:
            self._tripped = True
            self._event = KillSwitchEvent(
                triggered_at_utc=datetime.now(timezone.utc),
                reason=reason,
                source=source,
            )
            self._persist()
        assert self._event is not None
        return self._event

    def reset_state(self, reason: str, operator: str = "operator") -> None:
        """Explicit manual reset by human operator."""
        logger.warning(f"Manual KillSwitch RESET by {operator}: {reason}")
        self._tripped = False
        self._event = None
        if self._state_file and self._state_file.exists():
            try:
                self._state_file.unlink()
            except Exception as e:
                logger.error(f"Could not remove KillSwitch state file: {e}")

    def assert_healthy(self) -> None:
        """Raise KillSwitchTrippedError if the kill switch has been tripped."""
        if self._tripped and self._event is not None:
            raise KillSwitchTrippedError(
                f"KILL SWITCH ACTIVE [{self._event.source} @ {self._event.triggered_at_utc.isoformat()}]: "
                f"{self._event.reason}"
            )
