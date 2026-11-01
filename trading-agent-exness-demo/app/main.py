"""Entry point for Milestone M0-M1: Exness MT5 Read-Only Connector diagnostic runner."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import asdict
from typing import Any

from app.config import AppConfig, ConfigValidationError, load_config
from app.data.quality_gate import DataQualityError, DataQualityGate
from app.logging_setup import setup_logging
from app.mt5.connection import (
    LiveAccountBlockedError,
    MT5ConnectionError,
    MT5ConnectionManager,
)
from app.mt5.market_data import (
    MarketDataError,
    MT5MarketDataReader,
    SymbolValidationError,
)
from app.risk.kill_switch import KillSwitch


def run_diagnostic(
    config_path: str = "config/demo.yaml",
    mt5_backend: Any | None = None,
) -> dict[str, Any]:
    """Validate config, connect to MT5 Demo, inspect allowlist symbols, and run Data Quality Gate."""
    logger = setup_logging(os.environ.get("LOG_LEVEL", "INFO"))
    config: AppConfig = load_config(config_path)
    kill_switch = KillSwitch(enabled=config.safety.kill_switch)

    logger.info(
        "Loaded and validated configuration (Milestone M0-M1 Read-Only)",
        extra={
            "structured_data": {
                "platform": config.platform,
                "account_mode": config.account_mode,
                "execution_mode": config.execution_mode,
                "allowed_symbols": config.symbols.allowed,
                "enabled_symbols": config.symbols.enabled,
                "timeframes": config.timeframes,
            }
        },
    )

    conn = MT5ConnectionManager(config=config, mt5_backend=mt5_backend)
    summary: dict[str, Any] = {
        "account": None,
        "symbols": {},
        "quality_reports": [],
        "kill_switch_tripped": False,
    }

    try:
        account_meta = conn.connect()
        summary["account"] = asdict(account_meta)

        reader = MT5MarketDataReader(connection=conn, config=config)
        gate = DataQualityGate(config=config)

        for base_symbol in config.symbols.allowed:
            kill_switch.assert_healthy()
            spec = reader.read_symbol_spec(base_symbol)
            tick = reader.read_tick(base_symbol)
            summary["symbols"][base_symbol] = {
                "spec": asdict(spec),
                "latest_tick": asdict(tick),
            }
            logger.info(
                f"Discovered and validated symbol {base_symbol} -> {spec.broker_symbol}",
                extra={
                    "structured_data": {
                        "base_symbol": base_symbol,
                        "broker_symbol": spec.broker_symbol,
                        "contract_size": spec.contract_size,
                        "point": spec.point,
                        "spread_points": tick.spread_points,
                    }
                },
            )

            for tf in config.timeframes:
                candles = reader.read_candles(
                    base_symbol=base_symbol,
                    timeframe=tf,
                    count=max(config.data_quality.min_candle_count, 60),
                )
                report = gate.evaluate(
                    base_symbol=base_symbol,
                    timeframe=tf,
                    tick=tick,
                    candles=candles,
                )
                summary["quality_reports"].append(asdict(report))
                logger.info(
                    f"Data Quality Gate PASSED for {spec.broker_symbol} ({tf})",
                    extra={"structured_data": asdict(report)},
                )

    except (
        LiveAccountBlockedError,
        MT5ConnectionError,
        SymbolValidationError,
        MarketDataError,
        DataQualityError,
    ) as exc:
        kill_switch.trip(reason=str(exc), source=exc.__class__.__name__)
        summary["kill_switch_tripped"] = True
        logger.error(
            f"Safety/Quality check failed — KillSwitch tripped: {exc}",
            extra={"structured_data": {"error_type": exc.__class__.__name__, "detail": str(exc)}},
        )
        raise
    finally:
        conn.shutdown()

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exness MT5 Demo Read-Only Connector (M0-M1)"
    )
    parser.add_argument(
        "--config",
        default="config/demo.yaml",
        help="Path to YAML configuration file (default: config/demo.yaml)",
    )
    parser.add_argument(
        "--validate-config-only",
        action="store_true",
        help="Validate configuration and exit without connecting to MT5 terminal",
    )
    args = parser.parse_args()

    logger = setup_logging(os.environ.get("LOG_LEVEL", "INFO"))
    try:
        if args.validate_config_only:
            cfg = load_config(args.config)
            logger.info(
                "Configuration validation succeeded",
                extra={"structured_data": {"allowed_symbols": cfg.symbols.allowed}},
            )
            return 0
        run_diagnostic(config_path=args.config)
        return 0
    except ConfigValidationError as exc:
        logger.error(f"Configuration validation failed: {exc}")
        return 2
    except Exception as exc:
        logger.error(f"Execution halted: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
