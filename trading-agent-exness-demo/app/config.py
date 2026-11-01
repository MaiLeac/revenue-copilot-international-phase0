"""Configuration loading and fail-closed safety validation."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


class ConfigValidationError(ValueError):
    """Raised when configuration violates safety or schema rules."""


SUPPORTED_TIMEFRAMES = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"}


@dataclass(frozen=True)
class SymbolsConfig:
    allowed: list[str]
    enabled: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DataQualityConfig:
    max_candle_age_seconds: dict[str, int]
    max_tick_age_seconds: int = 60
    min_candle_count: int = 50
    max_spread_points: dict[str, int] = field(default_factory=lambda: {"default": 100})

    def get_max_spread(self, base_symbol: str) -> int:
        return self.max_spread_points.get(
            base_symbol, self.max_spread_points.get("default", 100)
        )

    def get_max_candle_age(self, timeframe: str) -> int:
        return self.max_candle_age_seconds.get(timeframe, 3600)


@dataclass(frozen=True)
class RiskConfig:
    risk_per_trade_pct: float
    max_total_open_risk_pct: float
    max_daily_loss_pct: float
    max_drawdown_pct: float
    max_positions_per_symbol: int


@dataclass(frozen=True)
class SafetyConfig:
    require_stop_loss: bool
    reject_stale_data: bool
    reject_excessive_spread: bool
    block_live_accounts: bool
    kill_switch: bool


@dataclass(frozen=True)
class MT5EnvConfig:
    demo_only: bool
    terminal_path: str | None = None
    login: int | None = None
    password: str | None = None
    server: str | None = None
    timeout_ms: int = 10000


@dataclass(frozen=True)
class AppConfig:
    platform: str
    account_mode: str
    execution_mode: str
    symbols: SymbolsConfig
    timeframes: list[str]
    data_quality: DataQualityConfig
    risk: RiskConfig
    safety: SafetyConfig
    mt5_env: MT5EnvConfig


def load_env_config(env_override: dict[str, str] | None = None) -> MT5EnvConfig:
    """Load and validate environment variables. Fail closed if DEMO_ONLY is not true."""
    load_dotenv()
    env = dict(os.environ)
    if env_override is not None:
        env.update(env_override)

    demo_only_raw = env.get("DEMO_ONLY", "true").strip().lower()
    if demo_only_raw != "true":
        raise ConfigValidationError(
            f"Safety violation: DEMO_ONLY environment variable must be 'true', got '{demo_only_raw}'."
        )

    login_raw = env.get("MT5_LOGIN", "").strip()
    login: int | None = None
    if login_raw:
        try:
            login = int(login_raw)
        except ValueError as exc:
            raise ConfigValidationError(
                f"MT5_LOGIN must be an integer account number, got '{login_raw}'."
            ) from exc

    timeout_raw = env.get("MT5_TIMEOUT_MS", "10000").strip()
    try:
        timeout_ms = int(timeout_raw)
        if timeout_ms <= 0:
            raise ValueError
    except ValueError as exc:
        raise ConfigValidationError(
            f"MT5_TIMEOUT_MS must be a positive integer, got '{timeout_raw}'."
        ) from exc

    return MT5EnvConfig(
        demo_only=True,
        terminal_path=env.get("MT5_TERMINAL_PATH", "").strip() or None,
        login=login,
        password=env.get("MT5_PASSWORD", "").strip() or None,
        server=env.get("MT5_SERVER", "").strip() or None,
        timeout_ms=timeout_ms,
    )


def validate_raw_config(raw: dict[str, Any], env_config: MT5EnvConfig | None = None) -> AppConfig:
    """Validate raw YAML dictionary and return strongly-typed AppConfig."""
    if not isinstance(raw, dict):
        raise ConfigValidationError("Configuration root must be a YAML mapping/dict.")

    platform = str(raw.get("platform", "")).strip().lower()
    if platform != "mt5":
        raise ConfigValidationError(f"Unsupported platform '{platform}'. Only 'mt5' is supported.")

    account_mode = str(raw.get("account_mode", "")).strip().lower()
    if account_mode != "demo_only":
        raise ConfigValidationError(
            f"Safety violation: account_mode must be 'demo_only', got '{account_mode}'."
        )

    execution_mode = str(raw.get("execution_mode", "")).strip().lower()
    if execution_mode not in {"read_only", "demo_auto"}:
        raise ConfigValidationError(
            f"Invalid execution_mode '{execution_mode}'. Expected 'read_only' or 'demo_auto'."
        )

    # Safety section validation (Fail Closed)
    safety_raw = raw.get("safety")
    if not isinstance(safety_raw, dict):
        raise ConfigValidationError("Missing or invalid 'safety' configuration section.")

    safety = SafetyConfig(
        require_stop_loss=bool(safety_raw.get("require_stop_loss", False)),
        reject_stale_data=bool(safety_raw.get("reject_stale_data", False)),
        reject_excessive_spread=bool(safety_raw.get("reject_excessive_spread", False)),
        block_live_accounts=bool(safety_raw.get("block_live_accounts", False)),
        kill_switch=bool(safety_raw.get("kill_switch", False)),
    )

    if not safety.block_live_accounts:
        raise ConfigValidationError("Safety violation: safety.block_live_accounts must be true.")
    if not safety.require_stop_loss:
        raise ConfigValidationError("Safety violation: safety.require_stop_loss must be true.")
    if not safety.reject_stale_data:
        raise ConfigValidationError("Safety violation: safety.reject_stale_data must be true.")
    if not safety.reject_excessive_spread:
        raise ConfigValidationError("Safety violation: safety.reject_excessive_spread must be true.")
    if not safety.kill_switch:
        raise ConfigValidationError("Safety violation: safety.kill_switch must be true.")

    # Symbols validation
    symbols_raw = raw.get("symbols")
    if not isinstance(symbols_raw, dict):
        raise ConfigValidationError("Missing or invalid 'symbols' section.")

    allowed = [str(s).strip().upper() for s in symbols_raw.get("allowed", []) if str(s).strip()]
    if not allowed:
        raise ConfigValidationError("symbols.allowed cannot be empty.")

    enabled = [str(s).strip().upper() for s in symbols_raw.get("enabled", []) if str(s).strip()]
    unknown_enabled = set(enabled) - set(allowed)
    if unknown_enabled:
        raise ConfigValidationError(
            f"symbols.enabled contains symbols not in symbols.allowed: {sorted(unknown_enabled)}"
        )
    if enabled and execution_mode == "read_only":
        raise ConfigValidationError(
            "Milestone M0-M1 safety lock: symbols.enabled must be empty ([]). Trading is not enabled yet in read_only mode."
        )

    # Timeframes validation
    timeframes_raw = raw.get("timeframes", [])
    if not isinstance(timeframes_raw, list) or not timeframes_raw:
        raise ConfigValidationError("timeframes must be a non-empty list.")
    timeframes = [str(tf).strip().upper() for tf in timeframes_raw]
    invalid_tfs = set(timeframes) - SUPPORTED_TIMEFRAMES
    if invalid_tfs:
        raise ConfigValidationError(f"Unsupported timeframes: {sorted(invalid_tfs)}")

    # Risk validation
    risk_raw = raw.get("risk")
    if not isinstance(risk_raw, dict):
        raise ConfigValidationError("Missing or invalid 'risk' section.")

    risk = RiskConfig(
        risk_per_trade_pct=float(risk_raw.get("risk_per_trade_pct", 0)),
        max_total_open_risk_pct=float(risk_raw.get("max_total_open_risk_pct", 0)),
        max_daily_loss_pct=float(risk_raw.get("max_daily_loss_pct", 0)),
        max_drawdown_pct=float(risk_raw.get("max_drawdown_pct", 0)),
        max_positions_per_symbol=int(risk_raw.get("max_positions_per_symbol", 0)),
    )
    if not (0 < risk.risk_per_trade_pct <= 1.0):
        raise ConfigValidationError("risk.risk_per_trade_pct must be between 0 and 1.0%.")
    if not (risk.risk_per_trade_pct <= risk.max_total_open_risk_pct <= 2.0):
        raise ConfigValidationError(
            "risk.max_total_open_risk_pct must be >= risk_per_trade_pct and <= 2.0%."
        )
    if not (0 < risk.max_daily_loss_pct <= 5.0):
        raise ConfigValidationError("risk.max_daily_loss_pct must be between 0 and 5.0%.")
    if not (0 < risk.max_drawdown_pct <= 10.0):
        raise ConfigValidationError("risk.max_drawdown_pct must be between 0 and 10.0%.")
    if risk.max_positions_per_symbol < 1:
        raise ConfigValidationError("risk.max_positions_per_symbol must be >= 1.")

    # Data quality configuration
    dq_raw = raw.get("data_quality", {})
    max_candle_age = dq_raw.get("max_candle_age_seconds", {"M15": 1800, "H1": 7200})
    max_spread = dq_raw.get(
        "max_spread_points",
        {"XAUUSD": 500, "XAGUSD": 400, "EURUSD": 30, "default": 100},
    )
    data_quality = DataQualityConfig(
        max_candle_age_seconds={str(k).upper(): int(v) for k, v in max_candle_age.items()},
        max_tick_age_seconds=int(dq_raw.get("max_tick_age_seconds", 60)),
        min_candle_count=int(dq_raw.get("min_candle_count", 50)),
        max_spread_points={str(k): int(v) for k, v in max_spread.items()},
    )

    resolved_env = env_config if env_config is not None else load_env_config()

    return AppConfig(
        platform=platform,
        account_mode=account_mode,
        execution_mode=execution_mode,
        symbols=SymbolsConfig(allowed=allowed, enabled=enabled),
        timeframes=timeframes,
        data_quality=data_quality,
        risk=risk,
        safety=safety,
        mt5_env=resolved_env,
    )


def load_config(
    config_path: str | Path = "config/demo.yaml",
    env_override: dict[str, str] | None = None,
) -> AppConfig:
    """Load YAML configuration file and validate with environment rules."""
    path = Path(config_path)
    if not path.exists():
        raise ConfigValidationError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    env_cfg = load_env_config(env_override=env_override)
    return validate_raw_config(raw, env_config=env_cfg)
