"""Unit tests for the Crowdtesting & QA Workflow Toolkit (CASH-01 / JOB-01 / EXP-01)."""

from __future__ import annotations

from pathlib import Path

from assets.qa_workflow_toolkit.bug_report_preflight import (
    BugReportDraft,
    BugReportPreflightValidator,
)
from assets.qa_workflow_toolkit.qa_earnings_tracker import (
    QASessionRecord,
    append_verified_l4_to_cash_ledger,
    evaluate_session_economics,
)


def test_preflight_validator_passes_high_quality_report() -> None:
    validator = BugReportPreflightValidator()
    draft = BugReportDraft(
        title="[Hotel Checkout / Promo Code] - Advertised promo code OCTHTL is rejected as invalid at checkout",
        environment="Windows 11 64-bit, Chrome 130.0",
        url_or_build="https://www.onetravel.com/hotels",
        steps_to_reproduce=[
            "Navigate to OneTravel Hotels and search for Mexico City.",
            "Select 'Suites Reforma by Homirent' displaying promo code 'OCTHTL' on the listing card.",
            "Proceed to the payment/checkout page and enter 'OCTHTL' in the promo code input.",
            "Click Apply and observe the validation message.",
        ],
        actual_result="The checkout form rejects the advertised code with 'Promo code is not valid' and applies $0 discount.",
        expected_result="The promo code 'OCTHTL' advertised on the hotel card should be accepted and apply the stated discount.",
        attachments=["octhtl_promo_error.mp4", "octhtl_card_screenshot.png", "network_har.log"],
        checked_known_issues_list=True,
        verified_clean_session_or_incognito=True,
    )
    res = validator.validate(draft)
    assert res.ready_to_submit is True
    assert res.blockers == []
    assert res.score_pct == 100
    assert "### Steps to Reproduce" in res.formatted_markdown


def test_preflight_validator_blocks_pii_and_incomplete_steps() -> None:
    validator = BugReportPreflightValidator()
    draft = BugReportDraft(
        title="Bug on page",
        environment="",
        url_or_build="https://example.com",
        steps_to_reproduce=[" logged in with mypersonalemail@gmail.com "],
        actual_result="Broken",
        expected_result="Works",
        attachments=[],
        checked_known_issues_list=False,
        verified_clean_session_or_incognito=False,
    )
    res = validator.validate(draft)
    assert res.ready_to_submit is False
    assert any("PRIVACY GATE" in b for b in res.blockers)
    assert any("Steps to Reproduce" in b for b in res.blockers)
    assert any("Known Issues" in b for b in res.blockers)


def test_qa_earnings_tracker_separates_l3_pending_from_l4_cash(tmp_path: Path) -> None:
    ledger = tmp_path / "CASH_LEDGER.csv"
    ledger.write_text(
        "date,stream,gross_received,currency,platform_payment_fees,fx_costs,refunds,net_usable_cash,proof_reference_redacted,owner_hours,status,notes\n",
        encoding="utf-8",
    )

    l3_record = QASessionRecord(
        date="2026-10-31",
        platform="uTest",
        cycle_or_project="Cycle-562706-OneTravel",
        unpaid_prep_hours=1.0,
        active_work_hours=3.0,
        bugs_submitted=3,
        bugs_approved=3,
        gross_usd=28.0,
        platform_or_payment_fee_usd=0.0,
        payout_status="L3_APPROVED_PENDING",
        redacted_proof_ref="UTEST-562706-RANK1",
    )
    econ = evaluate_session_economics(l3_record)
    assert econ.passes_hourly_floor is True
    assert econ.is_usable_cash_l4 is False

    # L3 pending must NOT be appended to CASH_LEDGER.csv as collected cash
    appended_l3 = append_verified_l4_to_cash_ledger(ledger, l3_record)
    assert appended_l3 is False
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 1

    # Once L4 cash is actually received, it appends cleanly
    l4_record = QASessionRecord(
        date="2026-11-15",
        platform="uTest",
        cycle_or_project="Cycle-562706-OneTravel",
        unpaid_prep_hours=1.0,
        active_work_hours=3.0,
        bugs_submitted=3,
        bugs_approved=3,
        gross_usd=28.0,
        platform_or_payment_fee_usd=0.0,
        payout_status="L4_COLLECTED_CASH",
        redacted_proof_ref="PAYPAL-TX-REDACTED",
    )
    appended_l4 = append_verified_l4_to_cash_ledger(ledger, l4_record)
    assert appended_l4 is True
    lines = ledger.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert "L4_COLLECTED_CASH" in lines[1]
