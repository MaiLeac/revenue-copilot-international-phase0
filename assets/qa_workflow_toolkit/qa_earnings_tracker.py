"""QA & Contract Earnings / Time Economics Reconciler (CASH-01 / JOB-01).

Calculates net usable VND, hourly contribution after the owner's 50,000 VND/hr shadow wage,
and separates L3 (platform-approved pending payout) from L4 (usable cash received in bank).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

DEFAULT_SHADOW_WAGE_VND = 50_000.0
DEFAULT_USD_TO_VND = 25_640.0  # Gate 0 F03 reference buy transfer rate


@dataclass(frozen=True)
class QASessionRecord:
    date: str
    platform: str          # e.g. "uTest", "Testlio", "Lionbridge"
    cycle_or_project: str  # e.g. "Cycle-562706-OneTravel"
    unpaid_prep_hours: float
    active_work_hours: float
    bugs_submitted: int
    bugs_approved: int
    gross_usd: float
    platform_or_payment_fee_usd: float
    fx_haircut_pct: float = 0.03
    withdrawal_fixed_fee_vnd: float = 60_000.0
    payout_status: str = "L3_APPROVED_PENDING"  # L3_APPROVED_PENDING or L4_COLLECTED_CASH
    redacted_proof_ref: str = ""

    @property
    def total_owner_hours(self) -> float:
        return round(self.unpaid_prep_hours + self.active_work_hours, 2)


@dataclass(frozen=True)
class SessionEconomics:
    gross_vnd: float
    total_fees_and_fx_vnd: float
    net_cash_before_labor_vnd: float
    shadow_labor_cost_vnd: float
    contribution_after_labor_vnd: float
    realized_net_vnd_per_hour: float
    passes_hourly_floor: bool
    is_usable_cash_l4: bool


def evaluate_session_economics(
    record: QASessionRecord,
    usd_to_vnd: float = DEFAULT_USD_TO_VND,
    shadow_wage_vnd: float = DEFAULT_SHADOW_WAGE_VND,
) -> SessionEconomics:
    """Compute VND economics and check against the 50,000 VND/hr shadow wage floor."""
    if record.total_owner_hours <= 0:
        raise ValueError("total_owner_hours must be > 0.")

    gross_vnd = round(record.gross_usd * usd_to_vnd)
    after_usd_fee = max(0.0, record.gross_usd - record.platform_or_payment_fee_usd)
    converted_after_fx = after_usd_fee * usd_to_vnd * (1.0 - record.fx_haircut_pct)

    withdrawal_fee = record.withdrawal_fixed_fee_vnd if record.gross_usd > 0 else 0.0
    net_before_labor = round(max(0.0, converted_after_fx - withdrawal_fee))
    total_fees_vnd = max(0.0, gross_vnd - net_before_labor)

    labor_cost_vnd = round(record.total_owner_hours * shadow_wage_vnd)
    contribution_after_labor = round(net_before_labor - labor_cost_vnd)
    net_per_hour = round(net_before_labor / record.total_owner_hours)

    return SessionEconomics(
        gross_vnd=gross_vnd,
        total_fees_and_fx_vnd=total_fees_vnd,
        net_cash_before_labor_vnd=net_before_labor,
        shadow_labor_cost_vnd=labor_cost_vnd,
        contribution_after_labor_vnd=contribution_after_labor,
        realized_net_vnd_per_hour=net_per_hour,
        passes_hourly_floor=(net_per_hour >= shadow_wage_vnd),
        is_usable_cash_l4=(record.payout_status.strip().upper() == "L4_COLLECTED_CASH"),
    )


def append_verified_l4_to_cash_ledger(
    ledger_csv: str | Path,
    record: QASessionRecord,
    usd_to_vnd: float = DEFAULT_USD_TO_VND,
) -> bool:
    """Append a row to finance/CASH_LEDGER.csv ONLY if payout_status is L4_COLLECTED_CASH.

    Per OPERATING_SYSTEM.md Section 4 & Revenue Discipline:
    Never record platform balances or L3 pending payouts as collected cash revenue.
    """
    econ = evaluate_session_economics(record, usd_to_vnd=usd_to_vnd)
    if not econ.is_usable_cash_l4:
        return False

    path = Path(ledger_csv)
    fee_vnd = round(record.platform_or_payment_fee_usd * usd_to_vnd + (record.withdrawal_fixed_fee_vnd if record.gross_usd > 0 else 0))
    fx_vnd = round(econ.total_fees_and_fx_vnd - fee_vnd)

    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                record.date,
                f"{record.platform}:{record.cycle_or_project}",
                int(econ.gross_vnd),
                "VND",
                int(max(0, fee_vnd)),
                int(max(0, fx_vnd)),
                0,
                int(econ.net_cash_before_labor_vnd),
                record.redacted_proof_ref or "OWNER_VERIFIED_RECEIPT",
                record.total_owner_hours,
                "L4_COLLECTED_CASH",
                f"Approved bugs={record.bugs_approved}/{record.bugs_submitted}; net/hr={int(econ.realized_net_vnd_per_hour)} VND",
            ]
        )
    return True
