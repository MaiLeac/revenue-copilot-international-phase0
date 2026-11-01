"""Execution adapter for Exness MT5 Demo Trading Engine (Milestone M2 Autonomous Execution)."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any

from app.config import AppConfig
from app.mt5.connection import ACCOUNT_TRADE_MODE_DEMO, MT5ConnectionManager
from app.mt5.market_data import SymbolSpec
from app.risk.kill_switch import KillSwitch
from app.strategies.base import StrategySignal

logger = logging.getLogger("trading_agent.mt5.execution")


class ReadOnlyExecutionError(PermissionError):
    """Raised on any attempt to place, modify, or close orders during read_only mode."""


class ExecutionSafetyError(RuntimeError):
    """Raised when an execution safety rule is violated."""


@dataclass(frozen=True)
class OrderResult:
    ticket: int
    symbol: str
    direction: str
    volume: float
    price: float
    stop_loss: float
    take_profit: float
    comment: str
    retcode: int
    success: bool
    message: str


class DemoExecutionAdapter:
    """Safely executes orders on a verified MT5 DEMO terminal with strict risk sizing."""

    def __init__(
        self,
        config: AppConfig | None = None,
        connection: MT5ConnectionManager | None = None,
        kill_switch: KillSwitch | None = None,
    ) -> None:
        self._config = config
        self._connection = connection
        self._kill_switch = kill_switch

    def _ensure_can_execute(self) -> Any:
        if self._config is None or self._config.execution_mode == "read_only":
            raise ReadOnlyExecutionError(
                "SAFETY LOCK: Order placement is disabled in Milestone M0-M1 (Read-Only Connector)."
            )
        if self._connection is None or not self._connection.is_connected:
            raise ExecutionSafetyError("Cannot execute: MT5 connection is not initialized.")
        if self._kill_switch is not None:
            self._kill_switch.assert_healthy()

        account_meta = self._connection.read_account_metadata()
        if account_meta.trade_mode != ACCOUNT_TRADE_MODE_DEMO or not account_meta.is_verified_demo:
            raise ExecutionSafetyError(
                f"SAFETY LOCK: Live/real accounts are strictly blocked. Got trade_mode={account_meta.trade_mode_label}"
            )
        if not account_meta.trade_allowed:
            raise ExecutionSafetyError(
                f"SAFETY LOCK: Trade is not allowed for account #{account_meta.login} on MT5 terminal."
            )
        if not account_meta.trade_expert:
            raise ExecutionSafetyError(
                "SAFETY LOCK: Automated trading (Expert Advisors / Algo) is disabled in MT5 terminal."
            )
        return self._connection.backend

    def calculate_lot_size(
        self,
        signal: StrategySignal,
        spec: SymbolSpec,
        account_balance: float,
    ) -> float:
        """Calculate lot size based on fixed fractional risk and ATR stop distance with accurate tick value.
        
        Strictly rounds DOWN (floor) to ensure cash risk never exceeds the configured risk budget.
        Fails closed if configuration, entry price, or stop loss is missing.
        """
        import math

        if not self._config:
            raise ExecutionSafetyError("Safety violation: ExecutionAdapter has no AppConfig configured.")

        if signal.entry_price is None or signal.stop_loss is None:
            raise ExecutionSafetyError("Safety violation: Signal must have explicit entry_price and stop_loss.")

        stop_dist = abs(signal.entry_price - signal.stop_loss)
        if stop_dist <= 0:
            raise ExecutionSafetyError(f"Safety violation: Stop distance must be positive, got {stop_dist}")

        risk_pct = self._config.risk.risk_per_trade_pct
        risk_cash = account_balance * (risk_pct / 100.0)

        mt5 = self._connection.backend if self._connection else None
        min_vol = 0.01
        max_vol = 10.0
        step_vol = 0.01
        tick_size = 0.01
        tick_value = spec.contract_size * tick_size if spec.contract_size > 0 else 1.0

        if mt5:
            info = mt5.symbol_info(spec.broker_symbol)
            if info:
                min_vol = getattr(info, "volume_min", 0.01) or 0.01
                max_vol = getattr(info, "volume_max", 10.0) or 10.0
                step_vol = getattr(info, "volume_step", 0.01) or 0.01
                info_tick_size = getattr(info, "trade_tick_size", None)
                if info_tick_size and info_tick_size > 0:
                    tick_size = info_tick_size
                elif getattr(info, "digits", None):
                    tick_size = 10 ** (-info.digits)
                
                info_tick_val = getattr(info, "trade_tick_value", None)
                if info_tick_val and info_tick_val > 0:
                    tick_value = info_tick_val
                elif spec.contract_size > 0:
                    tick_value = spec.contract_size * tick_size

        if tick_size <= 0:
            tick_size = 0.01
        if tick_value <= 0:
            tick_value = 1.0

        cash_risk_per_lot = (stop_dist / tick_size) * tick_value
        if cash_risk_per_lot <= 0:
            raise ExecutionSafetyError(f"Safety violation: Cash risk per lot is non-positive ({cash_risk_per_lot})")

        raw_lots = risk_cash / cash_risk_per_lot

        # Strictly floor (round DOWN) to volume step so risk budget is never breached
        # Using round(..., 8) avoids binary floating-point representation errors (e.g. 1.0 / 0.01 == 99.99999999999999)
        decimals = max(0, -int(math.floor(math.log10(step_vol)))) if step_vol > 0 else 2
        steps = math.floor(round(raw_lots / step_vol, 8))
        lots = round(steps * step_vol, decimals)

        # Enforce minimum broker volume constraint: if min_vol risks more than risk_cash, reject order!
        if lots < min_vol:
            min_lot_cash_risk = min_vol * cash_risk_per_lot
            if min_lot_cash_risk > risk_cash:
                raise ExecutionSafetyError(
                    f"Risk limit rejected: Minimum broker volume ({min_vol}) risks ${min_lot_cash_risk:.2f}, "
                    f"which exceeds the maximum allowed risk budget of ${risk_cash:.2f}."
                )
            lots = min_vol

        # Cross-validate with MT5 internal order_calc_profit if terminal backend is available
        if mt5 and signal.entry_price and signal.stop_loss:
            if not hasattr(mt5, "order_calc_profit"):
                if self._config and self._config.execution_mode == "demo_auto":
                    raise ExecutionSafetyError("Safety violation: MT5 backend missing required order_calc_profit method in demo_auto mode.")
            else:
                mt5_type = 0 if signal.direction == "BUY" else 1
                try:
                    calc_pnl = mt5.order_calc_profit(mt5_type, spec.broker_symbol, lots, signal.entry_price, signal.stop_loss)
                except Exception as e:
                    raise ExecutionSafetyError(f"order_calc_profit check failed with exception: {e}")

                if calc_pnl is None:
                    raise ExecutionSafetyError(
                        f"order_calc_profit returned None for {spec.broker_symbol} (action={mt5_type}, lots={lots}, "
                        f"entry={signal.entry_price}, sl={signal.stop_loss}). Terminal cannot calculate monetary risk."
                    )

                if calc_pnl >= 0:
                    raise ExecutionSafetyError(
                        f"order_calc_profit returned non-negative PnL ({calc_pnl}) at Stop Loss for {spec.broker_symbol}. "
                        "Anomalous quote or inverted SL rejected."
                    )

                sim_cash_risk = abs(calc_pnl)
                while sim_cash_risk > risk_cash * 1.0001 and steps > 1:
                    steps -= 1
                    lots = round(steps * step_vol, decimals)
                    calc_pnl = mt5.order_calc_profit(mt5_type, spec.broker_symbol, lots, signal.entry_price, signal.stop_loss)
                    if calc_pnl is None:
                        raise ExecutionSafetyError("order_calc_profit returned None during lot size ratcheting.")
                    sim_cash_risk = abs(calc_pnl)

                # Final post-ratchet risk budget verification (AUDIT P0: ensure min step does not exceed budget)
                if sim_cash_risk > risk_cash * 1.0001:
                    raise ExecutionSafetyError(
                        f"Broker-calculated risk (${sim_cash_risk:.2f}) still exceeds risk budget (${risk_cash:.2f}) "
                        f"after lot reduction to minimum steps ({lots} lots). Order rejected."
                    )

        lots = min(lots, max_vol)
        return lots

    def get_open_positions(self, broker_symbol: str | None = None) -> list[Any]:
        """Fetch current open positions on MT5 terminal."""
        mt5 = self._ensure_can_execute()
        if broker_symbol:
            positions = mt5.positions_get(symbol=broker_symbol)
        else:
            positions = mt5.positions_get()
        return list(positions) if positions else []

    def place_order(
        self,
        signal: StrategySignal | None = None,
        spec: SymbolSpec | None = None,
        **kwargs: Any,
    ) -> OrderResult:
        """Execute a market order on MT5 Demo with hard stop-loss and take-profit."""
        mt5 = self._ensure_can_execute()

        if signal is None or spec is None:
            raise ReadOnlyExecutionError(
                "SAFETY LOCK: Order placement is disabled in Milestone M0-M1 (Read-Only Connector)."
            )

        if signal.direction not in ("BUY", "SELL"):
            return OrderResult(
                ticket=0,
                symbol=spec.broker_symbol,
                direction="FLAT",
                volume=0.0,
                price=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                comment="Skipped FLAT signal",
                retcode=0,
                success=False,
                message="Direction is FLAT",
            )

        # Check existing open positions
        open_pos = self.get_open_positions(spec.broker_symbol)
        max_pos = self._config.risk.max_positions_per_symbol if self._config else 1
        if len(open_pos) >= max_pos:
            logger.info(
                f"Position limit reached for {spec.broker_symbol}: open={len(open_pos)}, max={max_pos}"
            )
            return OrderResult(
                ticket=0,
                symbol=spec.broker_symbol,
                direction=signal.direction,
                volume=0.0,
                price=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                comment="Max positions limit reached",
                retcode=0,
                success=False,
                message="Position limit reached",
            )

        # Require stop loss
        if self._config and self._config.safety.require_stop_loss and not signal.stop_loss:
            raise ExecutionSafetyError("Safety violation: stop_loss is required for all orders.")

        account_meta = self._connection.read_account_metadata()
        lots = self.calculate_lot_size(signal, spec, account_meta.balance)

        tick = mt5.symbol_info_tick(spec.broker_symbol)
        if not tick:
            raise ExecutionSafetyError(f"No live tick available for {spec.broker_symbol}")

        is_buy = signal.direction == "BUY"
        order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL
        price = tick.ask if is_buy else tick.bid

        # Dynamic filling mode fallback (AUDIT-04)
        filling_mode = getattr(mt5, "ORDER_FILLING_IOC", 1)
        sym_info = mt5.symbol_info(spec.broker_symbol)
        if sym_info:
            flags = getattr(sym_info, "filling_mode", 0)
            if flags & 2:  # SYMBOL_FILLING_IOC
                filling_mode = getattr(mt5, "ORDER_FILLING_IOC", 1)
            elif flags & 1:  # SYMBOL_FILLING_FOK
                filling_mode = getattr(mt5, "ORDER_FILLING_FOK", 0)
            elif hasattr(mt5, "ORDER_FILLING_RETURN"):
                filling_mode = getattr(mt5, "ORDER_FILLING_RETURN", 2)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": spec.broker_symbol,
            "volume": lots,
            "type": order_type,
            "price": price,
            "sl": float(signal.stop_loss or 0.0),
            "tp": float(signal.take_profit or 0.0),
            "deviation": 25,
            "magic": 889100,
            "comment": "MoneyHQ_AutoTrade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        result = mt5.order_send(request)
        if result is None:
            err = mt5.last_error()
            raise ExecutionSafetyError(f"order_send returned None. last_error={err}")

        # Check retcode (10009 = TRADE_RETCODE_DONE, 10008 = TRADE_RETCODE_PLACED)
        success = result.retcode in (10008, 10009)
        order_res = OrderResult(
            ticket=result.order,
            symbol=spec.broker_symbol,
            direction=signal.direction,
            volume=result.volume or lots,
            price=result.price or price,
            stop_loss=signal.stop_loss or 0.0,
            take_profit=signal.take_profit or 0.0,
            comment=result.comment,
            retcode=result.retcode,
            success=success,
            message=result.comment or ("Order executed successfully" if success else "Order failed"),
        )

        logger.info(
            f"Executed order {spec.broker_symbol} {signal.direction} {lots} lots: retcode={result.retcode} ({result.comment})",
            extra={"structured_data": asdict(order_res) if hasattr(order_res, "__dataclass_fields__") else {}},
        )
        return order_res

    def modify_order(
        self,
        ticket: int,
        sl: float | None = None,
        tp: float | None = None,
    ) -> bool:
        """Modify existing position SL/TP on MT5 Demo terminal."""
        mt5 = self._ensure_can_execute()
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            logger.warning(f"Cannot modify position #{ticket}: ticket not found.")
            return False

        pos = positions[0]
        new_sl = float(sl) if sl is not None else float(getattr(pos, "sl", 0.0))
        new_tp = float(tp) if tp is not None else float(getattr(pos, "tp", 0.0))

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": pos.symbol,
            "sl": new_sl,
            "tp": new_tp,
        }
        res = mt5.order_send(request)
        success = res is not None and res.retcode in (10008, 10009)
        if success:
            logger.info(f"Modified position #{ticket}: sl={new_sl}, tp={new_tp}")
        else:
            err = res.comment if res else mt5.last_error()
            logger.warning(f"Failed to modify position #{ticket}: {err}")
        return success

    def close_position(self, ticket: int) -> bool:
        mt5 = self._ensure_can_execute()
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False
        pos = positions[0]
        is_buy = pos.type == mt5.POSITION_TYPE_BUY
        close_type = mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY
        tick = mt5.symbol_info_tick(pos.symbol)
        if not tick:
            return False
        price = tick.bid if is_buy else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 25,
            "magic": 889100,
            "comment": "MoneyHQ_AutoClose",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        res = mt5.order_send(request)
        return res is not None and res.retcode in (10008, 10009)
