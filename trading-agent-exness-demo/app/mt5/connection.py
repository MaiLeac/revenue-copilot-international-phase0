"""MT5 Terminal Connection Manager and Account Metadata Reader (Read-Only)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.config import AppConfig

logger = logging.getLogger("trading_agent.mt5.connection")

# MT5 Constants
ACCOUNT_TRADE_MODE_DEMO = 0
ACCOUNT_TRADE_MODE_CONTEST = 1
ACCOUNT_TRADE_MODE_REAL = 2


class MT5ConnectionError(RuntimeError):
    """Raised when the MT5 terminal is unavailable or fails initialization."""


class LiveAccountBlockedError(PermissionError):
    """Raised when a non-demo (Real/Contest/Unverified) account is detected."""


@dataclass(frozen=True)
class AccountMetadata:
    login: int
    server: str
    trade_mode: int
    trade_mode_label: str
    currency: str
    balance: float
    equity: float
    margin: float
    margin_free: float
    margin_mode: int
    leverage: int
    trade_allowed: bool
    trade_expert: bool
    is_verified_demo: bool


class MT5ConnectionManager:
    """Manages a strictly read-only connection to a verified MT5 DEMO terminal."""

    def __init__(self, config: AppConfig, mt5_backend: Any | None = None) -> None:
        self._config = config
        if mt5_backend is None:
            try:
                import MetaTrader5 as mt5_mod
                self._mt5 = mt5_mod
            except ImportError as exc:
                raise MT5ConnectionError(
                    "MetaTrader5 Python package is not installed or unavailable on this OS."
                ) from exc
        else:
            self._mt5 = mt5_backend
        self._connected = False

    @property
    def backend(self) -> Any:
        return self._mt5

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> AccountMetadata:
        """Initialize MT5 terminal connection and enforce DEMO-only account gate."""
        env = self._config.mt5_env
        init_kwargs: dict[str, Any] = {"timeout": env.timeout_ms}
        if env.terminal_path:
            init_kwargs["path"] = env.terminal_path
        if env.login is not None:
            init_kwargs["login"] = env.login
        if env.password is not None:
            init_kwargs["password"] = env.password
        if env.server is not None:
            init_kwargs["server"] = env.server

        try:
            initialized = self._mt5.initialize(**init_kwargs)
        except Exception as exc:
            self._connected = False
            raise MT5ConnectionError(f"Failed to initialize MT5 terminal: {exc}") from exc

        if not initialized:
            err = self._safe_last_error()
            self._connected = False
            raise MT5ConnectionError(
                f"MT5 terminal unavailable or initialization failed. last_error={err}"
            )

        self._connected = True
        try:
            account_meta = self.read_account_metadata()
        except Exception:
            self.shutdown()
            raise

        logger.info(
            "Connected to verified MT5 DEMO terminal",
            extra={
                "structured_data": {
                    "login": account_meta.login,
                    "server": account_meta.server,
                    "currency": account_meta.currency,
                    "balance": account_meta.balance,
                    "equity": account_meta.equity,
                    "leverage": account_meta.leverage,
                }
            },
        )
        return account_meta

    def read_account_metadata(self) -> AccountMetadata:
        """Read account info and fail closed if the account cannot be verified as DEMO."""
        if not self._connected:
            raise MT5ConnectionError("Cannot read account info: MT5 terminal is not connected.")

        term_info = self._mt5.terminal_info()
        if term_info is None or not getattr(term_info, "connected", False):
            raise MT5ConnectionError(
                "MT5 terminal is not connected to a broker trade server."
            )

        acc = self._mt5.account_info()
        if acc is None:
            err = self._safe_last_error()
            raise MT5ConnectionError(
                f"Failed to retrieve MT5 account_info(). last_error={err}"
            )

        trade_mode = getattr(acc, "trade_mode", None)
        server = str(getattr(acc, "server", "")).strip()
        login = int(getattr(acc, "login", 0))

        if trade_mode != ACCOUNT_TRADE_MODE_DEMO:
            self.shutdown()
            raise LiveAccountBlockedError(
                f"SAFETY LOCK TRIPPED: Account {login} on server '{server}' has "
                f"trade_mode={trade_mode} (expected {ACCOUNT_TRADE_MODE_DEMO}=DEMO). "
                "Live or non-demo accounts are strictly forbidden."
            )

        server_lower = server.lower()
        if "real" in server_lower or "live" in server_lower:
            self.shutdown()
            raise LiveAccountBlockedError(
                f"SAFETY LOCK TRIPPED: Server name '{server}' contains live/real indicator "
                "despite trade_mode flag. Failing closed."
            )

        if not server or login <= 0:
            self.shutdown()
            raise LiveAccountBlockedError(
                "SAFETY LOCK TRIPPED: Account login or server name is missing/uncertain."
            )

        return AccountMetadata(
            login=login,
            server=server,
            trade_mode=trade_mode,
            trade_mode_label="DEMO",
            currency=str(getattr(acc, "currency", "USD")),
            balance=float(getattr(acc, "balance", 0.0)),
            equity=float(getattr(acc, "equity", 0.0)),
            margin=float(getattr(acc, "margin", 0.0)),
            margin_free=float(getattr(acc, "margin_free", 0.0)),
            margin_mode=int(getattr(acc, "margin_mode", 0)),
            leverage=int(getattr(acc, "leverage", 0)),
            trade_allowed=bool(getattr(acc, "trade_allowed", False)),
            trade_expert=bool(getattr(acc, "trade_expert", False)),
            is_verified_demo=True,
        )

    def shutdown(self) -> None:
        """Cleanly close the MT5 terminal connection."""
        if self._connected:
            try:
                self._mt5.shutdown()
            except Exception as exc:
                logger.warning(f"Error during MT5 shutdown: {exc}")
            finally:
                self._connected = False

    def _safe_last_error(self) -> Any:
        try:
            return self._mt5.last_error()
        except Exception:
            return "unknown"
