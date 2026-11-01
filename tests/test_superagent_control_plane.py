"""Unit and integration tests for the Money HQ Superagent Control Plane.

Verifies the 7-step vertical slice adapted from DeepSeek Superagent architecture:
1. Proactive event/scheduled trigger discovery without manual owner request.
2. Persistent storage of Trigger, EvalDecision, Mandate, and Ticket with priority & acceptance criteria.
3. Isolated worker execution in per-ticket session directories.
4. Durable step-level progress & output checkpointing.
5. Watchdog crash/interruption recovery without losing state or duplicating completed steps.
6. Evaluator acceptance verification & retry/escalation decision logic.
7. Quiet-by-default owner notification gating (alerts only on genuine `person/*` escalations).
"""

from __future__ import annotations

import json
from pathlib import Path

from assets.superagent_control_plane import (
    AcceptanceCriterion,
    ControlPlaneEngine,
    PolicyConfig,
    RevenueScore,
    SuperagentStore,
    TriggerEvent,
    render_attention_panel,
)


def _setup_synthetic_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "finance").mkdir(parents=True, exist_ok=True)
    (repo / "operations").mkdir(parents=True, exist_ok=True)
    (repo / "finance" / "MONEY_HQ_DASHBOARD.csv").write_text(
        "metric_id,name,value_vnd\nMET-L4,Realized Cash L4,0\n",
        encoding="utf-8",
    )
    (repo / "finance" / "MONEY_HQ_DASHBOARD.md").write_text(
        "# Money HQ Dashboard\n- **Realized Revenue (`L4` Collected Cash):** 0 VND\n",
        encoding="utf-8",
    )
    return repo


def test_proactive_discovery_and_idempotent_intake(tmp_path: Path) -> None:
    repo = _setup_synthetic_repo(tmp_path)
    sched_file = tmp_path / "tasks.json"
    sched_file.write_text(
        json.dumps(
            [
                {
                    "uuid": "mhqfin02",
                    "name": "Money HQ - Daily Financial and Blocker Report",
                    "state": "error",
                    "last_run": "2026-11-01T20:31:15+07:00",
                    "last_result": "ERROR: litellm.AuthenticationError: 401 Clerk",
                }
            ]
        ),
        encoding="utf-8",
    )

    store = SuperagentStore(repo / "operations" / "superagent_store.db")
    engine = ControlPlaneEngine(repo_root=repo, store=store)

    # Step 1: Proactive triggers generated without manual owner request
    triggers = engine.discover_proactive_triggers(scheduler_tasks_path=sched_file)
    assert len(triggers) == 2
    kinds = {t.task_kind for t in triggers}
    assert "recover_agent_zero_financial_sync" in kinds
    assert "build_storefront_and_organic_acquisition_pack" in kinds

    # Step 2: Persistent storage + idempotent deduplication
    dec1, tkt1 = engine.intake_and_evaluate(triggers[0])
    assert dec1.outcome == "accept"
    assert tkt1 is not None
    mandate = store.get_mandate(tkt1.mandate_id)
    assert mandate is not None
    assert mandate.budget_cap_vnd == 0

    # Submitting the exact same Trigger twice must be deduplicated idempotently
    dec_dup, tkt_dup = engine.intake_and_evaluate(triggers[0])
    assert dec_dup.outcome == "ignore"
    assert dec_dup.matched_rule == "RULE-IDEMPOTENT-DEDUP"
    assert tkt_dup is not None
    assert tkt_dup.ticket_id == tkt1.ticket_id
    assert len(store.list_tickets()) == 1


def test_isolated_execution_checkpoint_and_crash_recovery(tmp_path: Path) -> None:
    repo = _setup_synthetic_repo(tmp_path)
    store = SuperagentStore(repo / "operations" / "superagent_store.db")
    notifications: list[str] = []
    engine = ControlPlaneEngine(
        repo_root=repo,
        store=store,
        notifier=lambda msg: (notifications.append(msg) or {"ok": True}),
    )

    triggers = [
        t
        for t in engine.discover_proactive_triggers(scheduler_tasks_path=tmp_path / "none.json")
        if t.task_kind == "build_storefront_and_organic_acquisition_pack"
    ]
    assert len(triggers) == 1
    _, ticket = engine.intake_and_evaluate(triggers[0])
    assert ticket is not None

    # Step 3 & 4: Execute in isolated worker directory, but simulate crash/interruption on step 2
    asn1 = engine.execute_ticket(
        ticket.ticket_id,
        simulate_interrupt_on_step="step_2_seo_sitemap_robots",
    )
    assert asn1.status == "interrupted"
    steps_after_crash = json.loads(asn1.completed_steps_json)
    assert steps_after_crash == ["step_1_storefront_hub"]
    assert (repo / "index.html").exists()
    assert not (repo / "sitemap.xml").exists()

    # Step 5: Watchdog detects interrupted assignment and queues recovery without losing step 1
    recovered = engine.run_watchdog_recovery()
    assert recovered == [ticket.ticket_id]
    requeued_ticket = store.get_ticket(ticket.ticket_id)
    assert requeued_ticket is not None
    assert requeued_ticket.stage == "working/queued"
    assert requeued_ticket.retry_count == 1

    # Resume execution: step 1 is already in checkpoint_state.json, so worker finishes steps 2 & 3
    asn2 = engine.execute_ticket(ticket.ticket_id)
    assert asn2.status == "completed"
    steps_after_recovery = json.loads(asn2.completed_steps_json)
    assert steps_after_recovery == [
        "step_1_storefront_hub",
        "step_2_seo_sitemap_robots",
        "step_3_distribution_kits_dryrun",
    ]

    # Step 6: Evaluator verified all acceptance criteria and closed ticket
    final_ticket = store.get_ticket(ticket.ticket_id)
    assert final_ticket is not None
    assert final_ticket.status == "ended"
    assert final_ticket.stage == "ended"
    assert final_ticket.outcome == "completed_verified_observe_staged"

    # Step 7: Quiet by default — routine autonomous recovery & completion sends ZERO owner alerts
    assert notifications == []


def test_budget_and_retry_exhaustion_escalation_notifies_owner(tmp_path: Path) -> None:
    repo = _setup_synthetic_repo(tmp_path)
    store = SuperagentStore(repo / "operations" / "superagent_store.db")
    notifications: list[str] = []
    engine = ControlPlaneEngine(
        repo_root=repo,
        store=store,
        policy=PolicyConfig(approved_budget_cap_vnd=0, default_max_retries=1),
        notifier=lambda msg: (notifications.append(msg) or {"ok": True}),
    )

    # Case A: Paid tool request above 0 VND budget cap -> immediate escalation to person/answer
    paid_trigger = TriggerEvent(
        trigger_id="TRG-PAID-ADS-01",
        source_id="opportunity_scanner",
        thread_id="thread:paid_ads",
        actor="system:proactive",
        strength="inferred",
        title="Run Paid Meta Ads Campaign",
        objective="Spend 500,000 VND on paid ads",
        task_kind="paid_ads",
        revenue_score=RevenueScore(
            expected_net_profit_vnd_30d=2_000_000,
            time_to_first_revenue_days=2,
            owner_intervention_hours=0.5,
            incremental_cost_vnd=500_000,
            probability_of_success=0.5,
            operational_risk=0.4,
        ),
        requires_owner_identity_or_spend=True,
    )
    dec, tkt = engine.intake_and_evaluate(paid_trigger)
    assert dec.outcome == "escalate"
    assert tkt is not None
    assert tkt.stage == "person/answer"
    assert len(notifications) == 1
    assert "TRG-PAID-ADS-01" in notifications[0] or tkt.ticket_id in notifications[0]

    # Case B: Unsatisfied acceptance criterion exhausts retry limit -> escalates to person/blocked_failed
    bad_trigger = TriggerEvent(
        trigger_id="TRG-MISSING-OUTPUT-01",
        source_id="opportunity_scanner",
        thread_id="thread:missing_output",
        actor="system:proactive",
        strength="inferred",
        title="Task with impossible acceptance criterion",
        objective="Test evaluator failure and retry exhaustion",
        task_kind="generic_task",
        revenue_score=RevenueScore(
            expected_net_profit_vnd_30d=300_000,
            time_to_first_revenue_days=1,
            owner_intervention_hours=0.0,
            incremental_cost_vnd=0,
            probability_of_success=0.8,
            operational_risk=0.1,
        ),
        acceptance_criteria=(
            AcceptanceCriterion(
                criterion_id="AC-IMPOSSIBLE",
                description="File that worker does not create",
                required_path="nonexistent/output.txt",
            ),
        ),
    )
    _, bad_tkt = engine.intake_and_evaluate(bad_trigger)
    assert bad_tkt is not None
    # First attempt fails acceptance criterion -> Watchdog increments retry_count to 1
    engine.execute_ticket(bad_tkt.ticket_id)
    mid_tkt = store.get_ticket(bad_tkt.ticket_id)
    assert mid_tkt is not None
    assert mid_tkt.retry_count == 1
    assert mid_tkt.stage == "working/queued"

    # Second attempt fails acceptance criterion -> retries exhausted (1/1) -> escalates to person/blocked_failed
    engine.execute_ticket(bad_tkt.ticket_id)
    escalated_tkt = store.get_ticket(bad_tkt.ticket_id)
    assert escalated_tkt is not None
    assert escalated_tkt.stage == "person/blocked_failed"
    assert len(notifications) == 2

    panel_md = render_attention_panel(store, engine.policy)
    assert "[ACTION REQUIRED]" in panel_md
    assert escalated_tkt.ticket_id in panel_md


def test_no_hardcoded_credentials_in_telegram_tools() -> None:
    import re

    repo_root = Path(__file__).resolve().parent.parent
    token_pattern = re.compile(r"\b\d{8,11}:[A-Za-z0-9_-]{30,}\b")
    for rel_path in ("tools/telegram_notify.py", "tools/telegram_listener.py"):
        content = (repo_root / rel_path).read_text(encoding="utf-8")
        assert not token_pattern.search(content), f"Hardcoded Telegram token found in {rel_path}"
        assert "load_telegram_credentials" in content
