"""Kill Switch state machine: halts operation when safety, connection, or risk checks fail."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class KillSwitchEvent:
    triggered_at_utc: datetime
    reason: str
    source: str


class KillSwitch:
    """Fail-closed kill switch that blocks any further operation once tripped."""

    def __init__(self, enabled: bool = True) -> None:
        if not enabled:
            raise ValueError("Safety violation: KillSwitch cannot be initialized as disabled.")
        self._tripped = False
        self._event: KillSwitchEvent | None = None

    @property
    def is_tripped(self) -> bool:
        return self._tripped

    @property
    def last_event(self) -> KillSwitchEvent | None:
        return self._event

    def trip(self, reason: str, source: str = "system") -> KillSwitchEvent:
        """Trip the kill switch and record the root cause."""
        if not self._tripped:
            self._tripped = True
            self._event = KillSwitchEvent(
                triggered_at_utc=datetime.now(timezone.utc),
                reason=reason,
                source=source,
            )
        assert self._event is not None
        return self._event

    def assert_healthy(self) -> None:
        """Raise RuntimeError if the kill switch has been tripped."""
        if self._tripped and self._event is not None:
            raise RuntimeError(
                f"KILL SWITCH ACTIVE [{self._event.source} @ {self._event.triggered_at_utc.isoformat()}]: "
                f"{self._event.reason}"
            )
