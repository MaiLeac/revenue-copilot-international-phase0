"""Structured logging setup with automatic credential scrubbing."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

SENSITIVE_KEYS = {"password", "mt5_password", "secret", "token", "api_key"}


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as single-line structured JSON with secret redaction."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra_data = getattr(record, "structured_data", None)
        if isinstance(extra_data, dict):
            payload["data"] = self._scrub(extra_data)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)

    def _scrub(self, data: dict[str, Any]) -> dict[str, Any]:
        scrubbed: dict[str, Any] = {}
        for k, v in data.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                scrubbed[k] = "***REDACTED***"
            elif isinstance(v, dict):
                scrubbed[k] = self._scrub(v)
            else:
                scrubbed[k] = v
        return scrubbed


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure root logger with structured output."""
    logger = logging.getLogger("trading_agent")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger
