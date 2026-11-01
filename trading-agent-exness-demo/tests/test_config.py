"""Unit tests for configuration loading and fail-closed safety rules."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from app.config import (
    ConfigValidationError,
    load_config,
    load_env_config,
    validate_raw_config,
)


def _valid_raw() -> dict[str, Any]:
    return {
        "platform": "mt5",
        "account_mode": "demo_only",
        "execution_mode": "read_only",
        "symbols": {
            "allowed": ["XAGUSD", "EURUSD", "XAUUSD"],
            "enabled": [],
        },
        "timeframes": ["M15", "H1"],
        "risk": {
            "risk_per_trade_pct": 0.25,
            "max_total_open_risk_pct": 0.50,
            "max_daily_loss_pct": 1.0,
            "max_drawdown_pct": 5.0,
            "max_positions_per_symbol": 1,
        },
        "safety": {
            "require_stop_loss": True,
            "reject_stale_data": True,
            "reject_excessive_spread": True,
            "block_live_accounts": True,
            "kill_switch": True,
        },
    }


def test_load_default_demo_yaml() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    cfg = load_config(repo_root / "config" / "demo.yaml", env_override={"DEMO_ONLY": "true"})
    assert cfg.platform == "mt5"
    assert cfg.account_mode == "demo_only"
    assert cfg.symbols.allowed == ["XAGUSD", "EURUSD", "XAUUSD"]
    assert cfg.symbols.enabled == ["EURUSD"]
    assert cfg.safety.block_live_accounts is True


def test_reject_demo_only_false_in_env() -> None:
    with pytest.raises(ConfigValidationError, match="DEMO_ONLY"):
        load_env_config(env_override={"DEMO_ONLY": "false"})


def test_reject_live_account_mode() -> None:
    raw = _valid_raw()
    raw["account_mode"] = "live"
    with pytest.raises(ConfigValidationError, match="demo_only"):
        validate_raw_config(raw, load_env_config({"DEMO_ONLY": "true"}))


def test_reject_disabled_live_account_blocker() -> None:
    raw = _valid_raw()
    raw["safety"]["block_live_accounts"] = False
    with pytest.raises(ConfigValidationError, match="block_live_accounts"):
        validate_raw_config(raw, load_env_config({"DEMO_ONLY": "true"}))


def test_reject_enabled_symbols_in_m0_m1() -> None:
    raw = copy.deepcopy(_valid_raw())
    raw["symbols"]["enabled"] = ["EURUSD"]
    with pytest.raises(ConfigValidationError, match="symbols.enabled must be empty"):
        validate_raw_config(raw, load_env_config({"DEMO_ONLY": "true"}))


def test_reject_enabled_symbol_not_in_allowlist() -> None:
    raw = copy.deepcopy(_valid_raw())
    raw["symbols"]["enabled"] = ["BTCUSD"]
    with pytest.raises(ConfigValidationError, match="not in symbols.allowed"):
        validate_raw_config(raw, load_env_config({"DEMO_ONLY": "true"}))
