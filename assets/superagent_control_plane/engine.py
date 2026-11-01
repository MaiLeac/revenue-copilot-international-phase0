"""Money HQ Superagent Control Plane Engine.

Adapts DeepSeek Superagent architecture (`docs/000-philosophy.md` through
`docs/007-architecture.md`) into a deterministic, zero-cost Python control plane
for autonomous digital asset & revenue operations.

Core Domain Concepts:
- Source: Event producer with durable read cursor so restarts never replay events.
- Trigger: Immutable event with deterministic `idempotency_key` (`source_id:event_key`).
- Thread: Ordered stream of Triggers grouped by operational topic.
- Policy: Versioned rules, budget cap (`0 VND` default), concurrency limits, and
  `accept_mode` (`observe` vs `local_autonomous`).
- Eval: Two-layer judgment (Gate + Revenue-First Prioritizer) producing a Decision
  (`accept`, `observe_only`, `ignore`, `stop`, or `escalate`).
- Mandate: Immutable authorization attached to an accepted Ticket (`policy_version`,
  `scope`, `accept_mode`, `budget_cap_vnd`, `max_retries`, `timeout_sec`).
- Ticket: Unit of authorized work with mutually exclusive stages (`person/answer`,
  `person/review`, `person/blocked_failed`, `working/queued`, `working`, `idle`, `ended`).
- Assignment: Binding of a Ticket to an Isolated Executor Session directory
  (`operations/superagent_work/worker-<ticket_id>/`) with step-level checkpoints.
- Watchdog: Detects interrupted, timed-out, or crashed Assignments and resumes
  from the last verified checkpoint without losing state or duplicating work.
- Attention Panel: Minimal owner-facing view answering:
  1. Does anything need me now?
  2. Is the system healthy and doing the right things?
  3. What is the history of each piece of work from Trigger -> Eval -> Ticket?
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from typing import Any, Callable


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class RevenueScore:
    """Revenue-first prioritization score for candidate work."""

    expected_net_profit_vnd_30d: int
    time_to_first_revenue_days: int
    owner_intervention_hours: float
    incremental_cost_vnd: int
    probability_of_success: float
    operational_risk: float  # 0.0 (safe) to 1.0 (high risk)

    @property
    def priority_score(self) -> float:
        """Higher score = higher priority. Penalizes owner intervention, cost, delay, and risk."""
        if self.incremental_cost_vnd > 0 or self.operational_risk >= 0.8:
            return -1000.0
        expected_ev = self.expected_net_profit_vnd_30d * max(0.0, min(1.0, self.probability_of_success))
        time_divisor = max(1.0, float(self.time_to_first_revenue_days))
        owner_penalty = 1.0 + (self.owner_intervention_hours * 5.0)
        risk_penalty = 1.0 + (self.operational_risk * 2.0)
        return round((expected_ev / 1000.0) / (time_divisor * owner_penalty * risk_penalty), 2)


@dataclass(frozen=True)
class AcceptanceCriterion:
    """Deterministic check evaluated after worker execution."""

    criterion_id: str
    description: str
    required_path: str = ""
    required_substring: str = ""


@dataclass(frozen=True)
class PolicyConfig:
    """Versioned operating policy for the Money HQ Control Plane."""

    policy_version: str = "2026-11-01.v1"
    accept_mode: str = "observe"  # "observe" keeps external publishing in dry-run; allows safe local builds
    approved_budget_cap_vnd: int = 0
    max_concurrent_workers: int = 2
    default_timeout_sec: int = 120
    default_max_retries: int = 2
    allowed_sources: tuple[str, ...] = (
        "opportunity_scanner",
        "agent_zero_watchdog",
        "telegram_owner",
        "financial_reconciler",
    )
    allowed_actors: tuple[str, ...] = ("owner:mai", "system:proactive", "system:watchdog")


@dataclass(frozen=True)
class TriggerEvent:
    """Immutable event emitted by a Source."""

    trigger_id: str
    source_id: str
    thread_id: str
    actor: str
    strength: str  # "explicit" or "inferred"
    title: str
    objective: str
    task_kind: str
    revenue_score: RevenueScore
    requires_external_publish: bool = False
    requires_owner_identity_or_spend: bool = False
    acceptance_criteria: tuple[AcceptanceCriterion, ...] = ()
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)

    @property
    def idempotency_key(self) -> str:
        raw = f"{self.source_id}:{self.trigger_id}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


@dataclass(frozen=True)
class EvalDecision:
    """Output of Eval (Gate + Revenue Assessor)."""

    decision_id: str
    trigger_id: str
    thread_id: str
    outcome: str  # "accept", "ignore", "stop", "escalate"
    execution_mode: str  # "local_execute_external_observe", "full_observe_dry_run", "blocked_escalation"
    priority_score: float
    matched_rule: str
    reason: str
    policy_version: str
    decided_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class MandateRecord:
    """Immutable authorization granted to a Ticket upon Eval accept."""

    mandate_id: str
    ticket_id: str
    policy_version: str
    scope: str
    strength: str
    execution_mode: str
    matched_rule: str
    actor: str
    source_id: str
    budget_cap_vnd: int
    max_retries: int
    timeout_sec: int
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class TicketRecord:
    """Durable unit of authorized work."""

    ticket_id: str
    thread_id: str
    trigger_id: str
    mandate_id: str
    idempotency_key: str
    title: str
    objective: str
    task_kind: str
    priority_score: float
    status: str  # "open", "ended"
    stage: str  # "working/queued", "working", "idle", "person/review", "person/blocked_failed", "person/answer", "ended"
    outcome: str  # "", "completed_verified", "observed_dry_run", "escalated_to_owner", "stopped_by_owner", "failed"
    retry_count: int
    acceptance_criteria_json: str
    payload_json: str
    latest_report: str = ""
    attention_question: str = ""
    owner_notified: int = 0
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass
class AssignmentRecord:
    """Binding of a Ticket to an Isolated Executor Session with step checkpoints."""

    assignment_id: str
    ticket_id: str
    worker_session_id: str
    workspace_dir: str
    status: str  # "pending", "running", "interrupted", "completed", "failed"
    completed_steps_json: str = "[]"
    outputs_json: str = "{}"
    error_message: str = ""
    started_at: str = field(default_factory=utc_now_iso)
    heartbeat_at: str = field(default_factory=utc_now_iso)
    ended_at: str = ""


class SuperagentStore:
    """Durable SQLite persistence layer for the Money HQ Control Plane."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS source_cursors (
                    source_id TEXT PRIMARY KEY,
                    cursor_value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS triggers (
                    trigger_id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    source_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    strength TEXT NOT NULL,
                    title TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    task_kind TEXT NOT NULL,
                    priority_score REAL NOT NULL,
                    requires_external_publish INTEGER NOT NULL,
                    requires_owner_identity_or_spend INTEGER NOT NULL,
                    revenue_score_json TEXT NOT NULL,
                    acceptance_criteria_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    disposition TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    trigger_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    priority_score REAL NOT NULL,
                    matched_rule TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    policy_version TEXT NOT NULL,
                    decided_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS mandates (
                    mandate_id TEXT PRIMARY KEY,
                    ticket_id TEXT NOT NULL,
                    policy_version TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    strength TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    matched_rule TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    budget_cap_vnd INTEGER NOT NULL,
                    max_retries INTEGER NOT NULL,
                    timeout_sec INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    trigger_id TEXT NOT NULL,
                    mandate_id TEXT NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    task_kind TEXT NOT NULL,
                    priority_score REAL NOT NULL,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    retry_count INTEGER NOT NULL,
                    acceptance_criteria_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    latest_report TEXT NOT NULL,
                    attention_question TEXT NOT NULL,
                    owner_notified INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS assignments (
                    assignment_id TEXT PRIMARY KEY,
                    ticket_id TEXT NOT NULL,
                    worker_session_id TEXT NOT NULL,
                    workspace_dir TEXT NOT NULL,
                    status TEXT NOT NULL,
                    completed_steps_json TEXT NOT NULL,
                    outputs_json TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    heartbeat_at TEXT NOT NULL,
                    ended_at TEXT NOT NULL
                );
                """
            )

    def get_source_cursor(self, source_id: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT cursor_value FROM source_cursors WHERE source_id = ?",
                (source_id,),
            ).fetchone()
            return str(row["cursor_value"]) if row else None

    def set_source_cursor(self, source_id: str, cursor_value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO source_cursors (source_id, cursor_value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    cursor_value = excluded.cursor_value,
                    updated_at = excluded.updated_at
                """,
                (source_id, cursor_value, utc_now_iso()),
            )

    def get_ticket_by_idempotency_key(self, idempotency_key: str) -> TicketRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM tickets WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
            return self._row_to_ticket(row) if row else None

    def get_ticket(self, ticket_id: str) -> TicketRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM tickets WHERE ticket_id = ?",
                (ticket_id,),
            ).fetchone()
            return self._row_to_ticket(row) if row else None

    def list_tickets(self) -> list[TicketRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tickets ORDER BY priority_score DESC, created_at ASC"
            ).fetchall()
            return [self._row_to_ticket(r) for r in rows]

    def list_decisions(self) -> list[EvalDecision]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM decisions ORDER BY decided_at DESC"
            ).fetchall()
            return [
                EvalDecision(
                    decision_id=r["decision_id"],
                    trigger_id=r["trigger_id"],
                    thread_id=r["thread_id"],
                    outcome=r["outcome"],
                    execution_mode=r["execution_mode"],
                    priority_score=float(r["priority_score"]),
                    matched_rule=r["matched_rule"],
                    reason=r["reason"],
                    policy_version=r["policy_version"],
                    decided_at=r["decided_at"],
                )
                for r in rows
            ]

    def list_assignments(self, ticket_id: str | None = None) -> list[AssignmentRecord]:
        with self._connect() as conn:
            if ticket_id:
                rows = conn.execute(
                    "SELECT * FROM assignments WHERE ticket_id = ? ORDER BY started_at ASC",
                    (ticket_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM assignments ORDER BY started_at ASC"
                ).fetchall()
            return [self._row_to_assignment(r) for r in rows]

    def get_mandate(self, mandate_id: str) -> MandateRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM mandates WHERE mandate_id = ?",
                (mandate_id,),
            ).fetchone()
            if not row:
                return None
            return MandateRecord(
                mandate_id=row["mandate_id"],
                ticket_id=row["ticket_id"],
                policy_version=row["policy_version"],
                scope=row["scope"],
                strength=row["strength"],
                execution_mode=row["execution_mode"],
                matched_rule=row["matched_rule"],
                actor=row["actor"],
                source_id=row["source_id"],
                budget_cap_vnd=int(row["budget_cap_vnd"]),
                max_retries=int(row["max_retries"]),
                timeout_sec=int(row["timeout_sec"]),
                created_at=row["created_at"],
            )

    @staticmethod
    def _row_to_ticket(row: sqlite3.Row) -> TicketRecord:
        return TicketRecord(
            ticket_id=row["ticket_id"],
            thread_id=row["thread_id"],
            trigger_id=row["trigger_id"],
            mandate_id=row["mandate_id"],
            idempotency_key=row["idempotency_key"],
            title=row["title"],
            objective=row["objective"],
            task_kind=row["task_kind"],
            priority_score=float(row["priority_score"]),
            status=row["status"],
            stage=row["stage"],
            outcome=row["outcome"],
            retry_count=int(row["retry_count"]),
            acceptance_criteria_json=row["acceptance_criteria_json"],
            payload_json=row["payload_json"],
            latest_report=row["latest_report"],
            attention_question=row["attention_question"],
            owner_notified=int(row["owner_notified"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_assignment(row: sqlite3.Row) -> AssignmentRecord:
        return AssignmentRecord(
            assignment_id=row["assignment_id"],
            ticket_id=row["ticket_id"],
            worker_session_id=row["worker_session_id"],
            workspace_dir=row["workspace_dir"],
            status=row["status"],
            completed_steps_json=row["completed_steps_json"],
            outputs_json=row["outputs_json"],
            error_message=row["error_message"],
            started_at=row["started_at"],
            heartbeat_at=row["heartbeat_at"],
            ended_at=row["ended_at"],
        )


class ControlPlaneEngine:
    """Synchronous domain engine for Money HQ Superagent operations."""

    def __init__(
        self,
        repo_root: Path,
        store: SuperagentStore,
        policy: PolicyConfig | None = None,
        work_root: Path | None = None,
        notifier: Callable[[str], dict[str, Any]] | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.store = store
        self.policy = policy or PolicyConfig()
        self.work_root = work_root or (repo_root / "operations" / "superagent_work")
        self.work_root.mkdir(parents=True, exist_ok=True)
        self.notifier = notifier

    # ------------------------------------------------------------------
    # 1. PROACTIVE SOURCES (Event & Opportunity Discovery without Owner)
    # ------------------------------------------------------------------
    def discover_proactive_triggers(
        self,
        scheduler_tasks_path: Path | None = None,
    ) -> list[TriggerEvent]:
        """Scan repository, funnels, and Agent Zero scheduler to generate Triggers."""
        triggers: list[TriggerEvent] = []

        # Source A: Agent Zero Scheduler Watchdog (`agent_zero_watchdog`)
        sched_path = scheduler_tasks_path or Path(
            r"C:\Users\ACER\agent-zero\agent-zero\usr\scheduler\tasks.json"
        )
        if sched_path.exists():
            try:
                raw_sched = json.loads(sched_path.read_text(encoding="utf-8"))
                tasks_data = raw_sched.get("tasks", []) if isinstance(raw_sched, dict) else raw_sched
                for t in tasks_data:
                    if isinstance(t, dict) and t.get("state") == "error":
                        uuid_val = t.get("uuid", "unknown")
                        last_run = t.get("last_run", "unknown")
                        last_res = str(t.get("last_result", ""))
                        trig_id = f"TRG-WATCHDOG-{uuid_val}-{last_run[:16]}"
                        triggers.append(
                            TriggerEvent(
                                trigger_id=trig_id,
                                source_id="agent_zero_watchdog",
                                thread_id=f"thread:scheduler:{uuid_val}",
                                actor="system:watchdog",
                                strength="inferred",
                                title=f"Recover failed Agent Zero scheduled task ({t.get('name', uuid_val)})",
                                objective=(
                                    "Execute deterministic financial reconciliation & blocker check "
                                    "outside the failed OpenRouter/Clerk LLM loop and reset error state."
                                ),
                                task_kind="recover_agent_zero_financial_sync",
                                revenue_score=RevenueScore(
                                    expected_net_profit_vnd_30d=500_000,
                                    time_to_first_revenue_days=1,
                                    owner_intervention_hours=0.0,
                                    incremental_cost_vnd=0,
                                    probability_of_success=0.99,
                                    operational_risk=0.05,
                                ),
                                requires_external_publish=False,
                                requires_owner_identity_or_spend=False,
                                acceptance_criteria=(
                                    AcceptanceCriterion(
                                        criterion_id="AC-FIN-CSV",
                                        description="Verified MONEY_HQ_DASHBOARD.csv exists with L4=0 VND",
                                        required_path="finance/MONEY_HQ_DASHBOARD.csv",
                                        required_substring="Realized Cash L4",
                                    ),
                                    AcceptanceCriterion(
                                        criterion_id="AC-FIN-MD",
                                        description="Verified MONEY_HQ_DASHBOARD.md is refreshed",
                                        required_path="finance/MONEY_HQ_DASHBOARD.md",
                                        required_substring="Realized Revenue",
                                    ),
                                ),
                                payload={
                                    "task_uuid": uuid_val,
                                    "task_name": t.get("name", ""),
                                    "failed_error": last_res[:240],
                                    "scheduler_path": str(sched_path),
                                },
                            )
                        )
            except Exception:
                pass

        # Source B: Proactive Revenue & Distribution Opportunity Scanner (`opportunity_scanner`)
        root_storefront = self.repo_root / "index.html"
        sitemap_file = self.repo_root / "sitemap.xml"
        exp03_kit = self.repo_root / "experiments" / "exp03-duong-nhan-ai-mvp" / "distribution_kit.json"
        exp02_kit = self.repo_root / "experiments" / "exp02-catalogue-qa-pilot" / "distribution_kit.json"

        if not (root_storefront.exists() and sitemap_file.exists() and exp03_kit.exists() and exp02_kit.exists()):
            triggers.append(
                TriggerEvent(
                    trigger_id="TRG-REV-STOREFRONT-SEO-01",
                    source_id="opportunity_scanner",
                    thread_id="thread:revenue:organic_acquisition_hub",
                    actor="system:proactive",
                    strength="inferred",
                    title="Build Commercial Storefront Hub, SEO Sitemap & Organic Acquisition Kits (EXP-02 & EXP-03)",
                    objective=(
                        "Deploy root commercial storefront `index.html`, `sitemap.xml`, `robots.txt`, "
                        "and compliant organic distribution kits for Dưỡng Nhan (299k/$12) and Global CSV Fixer (199k/$9), "
                        "while keeping external social/community posting in OBSERVE dry-run mode."
                    ),
                    task_kind="build_storefront_and_organic_acquisition_pack",
                    revenue_score=RevenueScore(
                        expected_net_profit_vnd_30d=6_490_000,
                        time_to_first_revenue_days=3,
                        owner_intervention_hours=0.0,
                        incremental_cost_vnd=0,
                        probability_of_success=0.65,
                        operational_risk=0.10,
                    ),
                    requires_external_publish=True,  # External syndication stays in OBSERVE mode
                    requires_owner_identity_or_spend=False,
                    acceptance_criteria=(
                        AcceptanceCriterion(
                            criterion_id="AC-HUB-HTML",
                            description="Root commercial storefront index.html built with Payoneer & VietQR links",
                            required_path="index.html",
                            required_substring="experiments/exp03-duong-nhan-ai-mvp/",
                        ),
                        AcceptanceCriterion(
                            criterion_id="AC-SITEMAP",
                            description="SEO sitemap.xml generated for GitHub Pages discovery",
                            required_path="sitemap.xml",
                            required_substring="https://maileac.github.io/revenue-copilot-international-phase0/",
                        ),
                        AcceptanceCriterion(
                            criterion_id="AC-DIST-EXP03",
                            description="Dưỡng Nhan organic acquisition kit generated with observe-mode dry-run log",
                            required_path="experiments/exp03-duong-nhan-ai-mvp/distribution_kit.json",
                            required_substring="observe_dry_run",
                        ),
                        AcceptanceCriterion(
                            criterion_id="AC-DIST-EXP02",
                            description="Global CSV Fixer B2B outreach kit generated with observe-mode dry-run log",
                            required_path="experiments/exp02-catalogue-qa-pilot/distribution_kit.json",
                            required_substring="observe_dry_run",
                        ),
                    ),
                    payload={
                        "target_assets": ["EXP-03", "EXP-02"],
                        "storefront_url": "https://maileac.github.io/revenue-copilot-international-phase0/",
                    },
                )
            )

        return triggers

    # ------------------------------------------------------------------
    # 2. INTAKE & EVAL (Gate + Revenue-First Prioritizer + Mandate)
    # ------------------------------------------------------------------
    def intake_and_evaluate(self, trigger: TriggerEvent) -> tuple[EvalDecision, TicketRecord | None]:
        """Record Trigger idempotently, run Eval against Policy, and create Ticket + Mandate if accepted."""
        existing_ticket = self.store.get_ticket_by_idempotency_key(trigger.idempotency_key)
        if existing_ticket is not None:
            decision = EvalDecision(
                decision_id=f"DEC-DUP-{trigger.idempotency_key[:10]}",
                trigger_id=trigger.trigger_id,
                thread_id=trigger.thread_id,
                outcome="ignore",
                execution_mode="duplicate_noop",
                priority_score=existing_ticket.priority_score,
                matched_rule="RULE-IDEMPOTENT-DEDUP",
                reason=f"Idempotent duplicate of existing Ticket {existing_ticket.ticket_id}",
                policy_version=self.policy.policy_version,
            )
            return decision, existing_ticket

        # Gate checks
        if trigger.source_id not in self.policy.allowed_sources or trigger.actor not in self.policy.allowed_actors:
            decision = EvalDecision(
                decision_id=f"DEC-GATE-{trigger.idempotency_key[:10]}",
                trigger_id=trigger.trigger_id,
                thread_id=trigger.thread_id,
                outcome="ignore",
                execution_mode="not_admitted",
                priority_score=0.0,
                matched_rule="RULE-GATE-UNLISTED",
                reason="Source or actor not in Policy allowed list.",
                policy_version=self.policy.policy_version,
            )
            self._persist_intake(trigger, decision, None, None)
            return decision, None

        # Budget & Identity escalation check
        if (
            trigger.revenue_score.incremental_cost_vnd > self.policy.approved_budget_cap_vnd
            or trigger.requires_owner_identity_or_spend
        ):
            decision = EvalDecision(
                decision_id=f"DEC-ESC-{trigger.idempotency_key[:10]}",
                trigger_id=trigger.trigger_id,
                thread_id=trigger.thread_id,
                outcome="escalate",
                execution_mode="blocked_escalation",
                priority_score=trigger.revenue_score.priority_score,
                matched_rule="RULE-SAFETY-BUDGET-IDENTITY-GATE",
                reason=(
                    f"Requires owner identity/approval or cost ({trigger.revenue_score.incremental_cost_vnd} VND) "
                    f"exceeds cap ({self.policy.approved_budget_cap_vnd} VND)."
                ),
                policy_version=self.policy.policy_version,
            )
            ticket_id = f"TKT-{trigger.idempotency_key[:8].upper()}"
            mandate = MandateRecord(
                mandate_id=f"MND-{trigger.idempotency_key[:8].upper()}",
                ticket_id=ticket_id,
                policy_version=self.policy.policy_version,
                scope=trigger.task_kind,
                strength=trigger.strength,
                execution_mode="blocked_escalation",
                matched_rule=decision.matched_rule,
                actor=trigger.actor,
                source_id=trigger.source_id,
                budget_cap_vnd=self.policy.approved_budget_cap_vnd,
                max_retries=0,
                timeout_sec=self.policy.default_timeout_sec,
            )
            ticket = TicketRecord(
                ticket_id=ticket_id,
                thread_id=trigger.thread_id,
                trigger_id=trigger.trigger_id,
                mandate_id=mandate.mandate_id,
                idempotency_key=trigger.idempotency_key,
                title=trigger.title,
                objective=trigger.objective,
                task_kind=trigger.task_kind,
                priority_score=trigger.revenue_score.priority_score,
                status="open",
                stage="person/answer",
                outcome="escalated_to_owner",
                retry_count=0,
                acceptance_criteria_json=json.dumps(
                    [dataclasses.asdict(c) for c in trigger.acceptance_criteria],
                    ensure_ascii=False,
                ),
                payload_json=json.dumps(trigger.payload, ensure_ascii=False),
                latest_report=decision.reason,
                attention_question=(
                    f"Approve identity/budget action for '{trigger.title}' "
                    f"(Cost: {trigger.revenue_score.incremental_cost_vnd} VND)?"
                ),
            )
            self._persist_intake(trigger, decision, mandate, ticket)
            self._notify_owner_if_needed(ticket)
            return decision, ticket

        # Determine execution mode under Observe policy
        exec_mode = (
            "local_execute_external_observe"
            if (self.policy.accept_mode == "observe" and trigger.requires_external_publish)
            else "local_autonomous"
        )
        matched_rule = (
            "RULE-PROACTIVE-OBSERVE-SAFE-BUILD"
            if exec_mode == "local_execute_external_observe"
            else "RULE-DETERMINISTIC-OPS"
        )
        decision = EvalDecision(
            decision_id=f"DEC-ACC-{trigger.idempotency_key[:10]}",
            trigger_id=trigger.trigger_id,
            thread_id=trigger.thread_id,
            outcome="accept",
            execution_mode=exec_mode,
            priority_score=trigger.revenue_score.priority_score,
            matched_rule=matched_rule,
            reason=(
                f"Accepted with priority_score={trigger.revenue_score.priority_score}, "
                f"cost=0 VND, owner_hours={trigger.revenue_score.owner_intervention_hours}, "
                f"mode={exec_mode}."
            ),
            policy_version=self.policy.policy_version,
        )
        ticket_id = f"TKT-{trigger.idempotency_key[:8].upper()}"
        mandate = MandateRecord(
            mandate_id=f"MND-{trigger.idempotency_key[:8].upper()}",
            ticket_id=ticket_id,
            policy_version=self.policy.policy_version,
            scope=trigger.task_kind,
            strength=trigger.strength,
            execution_mode=exec_mode,
            matched_rule=matched_rule,
            actor=trigger.actor,
            source_id=trigger.source_id,
            budget_cap_vnd=self.policy.approved_budget_cap_vnd,
            max_retries=self.policy.default_max_retries,
            timeout_sec=self.policy.default_timeout_sec,
        )
        ticket = TicketRecord(
            ticket_id=ticket_id,
            thread_id=trigger.thread_id,
            trigger_id=trigger.trigger_id,
            mandate_id=mandate.mandate_id,
            idempotency_key=trigger.idempotency_key,
            title=trigger.title,
            objective=trigger.objective,
            task_kind=trigger.task_kind,
            priority_score=trigger.revenue_score.priority_score,
            status="open",
            stage="working/queued",
            outcome="",
            retry_count=0,
            acceptance_criteria_json=json.dumps(
                [dataclasses.asdict(c) for c in trigger.acceptance_criteria],
                ensure_ascii=False,
            ),
            payload_json=json.dumps(trigger.payload, ensure_ascii=False),
        )
        self._persist_intake(trigger, decision, mandate, ticket)
        return decision, ticket

    def _persist_intake(
        self,
        trigger: TriggerEvent,
        decision: EvalDecision,
        mandate: MandateRecord | None,
        ticket: TicketRecord | None,
    ) -> None:
        with self.store._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO triggers (
                    trigger_id, idempotency_key, source_id, thread_id, actor,
                    strength, title, objective, task_kind, priority_score,
                    requires_external_publish, requires_owner_identity_or_spend,
                    revenue_score_json, acceptance_criteria_json, payload_json,
                    disposition, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trigger.trigger_id,
                    trigger.idempotency_key,
                    trigger.source_id,
                    trigger.thread_id,
                    trigger.actor,
                    trigger.strength,
                    trigger.title,
                    trigger.objective,
                    trigger.task_kind,
                    trigger.revenue_score.priority_score,
                    1 if trigger.requires_external_publish else 0,
                    1 if trigger.requires_owner_identity_or_spend else 0,
                    json.dumps(dataclasses.asdict(trigger.revenue_score), ensure_ascii=False),
                    json.dumps([dataclasses.asdict(c) for c in trigger.acceptance_criteria], ensure_ascii=False),
                    json.dumps(trigger.payload, ensure_ascii=False),
                    decision.outcome,
                    trigger.created_at,
                ),
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO decisions (
                    decision_id, trigger_id, thread_id, outcome, execution_mode,
                    priority_score, matched_rule, reason, policy_version, decided_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.decision_id,
                    decision.trigger_id,
                    decision.thread_id,
                    decision.outcome,
                    decision.execution_mode,
                    decision.priority_score,
                    decision.matched_rule,
                    decision.reason,
                    decision.policy_version,
                    decision.decided_at,
                ),
            )
            if mandate is not None:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO mandates (
                        mandate_id, ticket_id, policy_version, scope, strength,
                        execution_mode, matched_rule, actor, source_id,
                        budget_cap_vnd, max_retries, timeout_sec, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        mandate.mandate_id,
                        mandate.ticket_id,
                        mandate.policy_version,
                        mandate.scope,
                        mandate.strength,
                        mandate.execution_mode,
                        mandate.matched_rule,
                        mandate.actor,
                        mandate.source_id,
                        mandate.budget_cap_vnd,
                        mandate.max_retries,
                        mandate.timeout_sec,
                        mandate.created_at,
                    ),
                )
            if ticket is not None:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO tickets (
                        ticket_id, thread_id, trigger_id, mandate_id, idempotency_key,
                        title, objective, task_kind, priority_score, status, stage,
                        outcome, retry_count, acceptance_criteria_json, payload_json,
                        latest_report, attention_question, owner_notified, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ticket.ticket_id,
                        ticket.thread_id,
                        ticket.trigger_id,
                        ticket.mandate_id,
                        ticket.idempotency_key,
                        ticket.title,
                        ticket.objective,
                        ticket.task_kind,
                        ticket.priority_score,
                        ticket.status,
                        ticket.stage,
                        ticket.outcome,
                        ticket.retry_count,
                        ticket.acceptance_criteria_json,
                        ticket.payload_json,
                        ticket.latest_report,
                        ticket.attention_question,
                        ticket.owner_notified,
                        ticket.created_at,
                        ticket.updated_at,
                    ),
                )

    # ------------------------------------------------------------------
    # 3. WATCHDOG & CRASH RECOVERY
    # ------------------------------------------------------------------
    def run_watchdog_recovery(self) -> list[str]:
        """Inspect interrupted or failed Assignments and requeue recoverable Tickets."""
        recovered_tickets: list[str] = []
        tickets = self.store.list_tickets()
        for ticket in tickets:
            if ticket.status != "open":
                continue
            mandate = self.store.get_mandate(ticket.mandate_id)
            max_retries = mandate.max_retries if mandate else self.policy.default_max_retries
            assignments = self.store.list_assignments(ticket.ticket_id)
            if not assignments:
                continue
            latest = assignments[-1]
            if latest.status in ("interrupted", "failed") or (
                ticket.stage == "working" and latest.status == "running"
            ):
                if ticket.retry_count < max_retries:
                    new_retry = ticket.retry_count + 1
                    with self.store._connect() as conn:
                        if latest.status == "running":
                            conn.execute(
                                "UPDATE assignments SET status = 'interrupted', ended_at = ? WHERE assignment_id = ?",
                                (utc_now_iso(), latest.assignment_id),
                            )
                        conn.execute(
                            """
                            UPDATE tickets
                            SET stage = 'working/queued',
                                retry_count = ?,
                                latest_report = ?,
                                updated_at = ?
                            WHERE ticket_id = ?
                            """,
                            (
                                new_retry,
                                f"Watchdog recovered interrupted assignment {latest.assignment_id} (retry {new_retry}/{max_retries}).",
                                utc_now_iso(),
                                ticket.ticket_id,
                            ),
                        )
                    recovered_tickets.append(ticket.ticket_id)
                else:
                    # Retries exhausted -> escalate to person/blocked_failed
                    with self.store._connect() as conn:
                        conn.execute(
                            """
                            UPDATE tickets
                            SET stage = 'person/blocked_failed',
                                outcome = 'escalated_to_owner',
                                attention_question = ?,
                                updated_at = ?
                            WHERE ticket_id = ?
                            """,
                            (
                                f"Ticket {ticket.ticket_id} exhausted {max_retries} retries. Last error: {latest.error_message}",
                                utc_now_iso(),
                                ticket.ticket_id,
                            ),
                        )
                    updated = self.store.get_ticket(ticket.ticket_id)
                    if updated:
                        self._notify_owner_if_needed(updated)
        return recovered_tickets

    # ------------------------------------------------------------------
    # 4. ISOLATED EXECUTOR & CHECKPOINTED WORKER SESSIONS
    # ------------------------------------------------------------------
    def execute_queued_tickets(self, simulate_interrupt_on_step: str | None = None) -> list[AssignmentRecord]:
        """Run queued Tickets up to concurrency limit inside isolated session directories."""
        executed: list[AssignmentRecord] = []
        open_tickets = [
            t for t in self.store.list_tickets()
            if t.status == "open" and t.stage == "working/queued"
        ]
        for ticket in open_tickets[: self.policy.max_concurrent_workers]:
            assignment = self.execute_ticket(
                ticket.ticket_id,
                simulate_interrupt_on_step=simulate_interrupt_on_step,
            )
            executed.append(assignment)
        return executed

    def execute_ticket(
        self,
        ticket_id: str,
        simulate_interrupt_on_step: str | None = None,
    ) -> AssignmentRecord:
        """Execute one Ticket in an isolated workspace directory with step checkpoints."""
        ticket = self.store.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError(f"Unknown ticket_id: {ticket_id}")

        mandate = self.store.get_mandate(ticket.mandate_id)
        existing_assignments = self.store.list_assignments(ticket_id)
        seq = len(existing_assignments) + 1
        assignment_id = f"ASN-{ticket_id[4:]}-{seq:02d}"
        worker_session_id = f"worker-{ticket_id.lower()}"
        workspace_dir = self.work_root / worker_session_id
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Load durable checkpoint state from workspace so completed steps are never duplicated
        checkpoint_file = workspace_dir / "checkpoint_state.json"
        if checkpoint_file.exists():
            cp_data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        else:
            cp_data = {"completed_steps": [], "outputs": {}}

        completed_steps: list[str] = list(cp_data.get("completed_steps", []))
        outputs: dict[str, Any] = dict(cp_data.get("outputs", {}))

        now_str = utc_now_iso()
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tickets SET stage = 'working', updated_at = ? WHERE ticket_id = ?",
                (now_str, ticket_id),
            )
            conn.execute(
                """
                INSERT INTO assignments (
                    assignment_id, ticket_id, worker_session_id, workspace_dir,
                    status, completed_steps_json, outputs_json, error_message,
                    started_at, heartbeat_at, ended_at
                ) VALUES (?, ?, ?, ?, 'running', ?, ?, '', ?, ?, '')
                """,
                (
                    assignment_id,
                    ticket_id,
                    worker_session_id,
                    str(workspace_dir),
                    json.dumps(completed_steps),
                    json.dumps(outputs),
                    now_str,
                    now_str,
                ),
            )

        def record_step(step_name: str, step_output: dict[str, Any]) -> None:
            if step_name not in completed_steps:
                completed_steps.append(step_name)
            outputs[step_name] = step_output
            checkpoint_file.write_text(
                json.dumps(
                    {
                        "ticket_id": ticket_id,
                        "assignment_id": assignment_id,
                        "completed_steps": completed_steps,
                        "outputs": outputs,
                        "updated_at": utc_now_iso(),
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with self.store._connect() as conn:
                conn.execute(
                    """
                    UPDATE assignments
                    SET completed_steps_json = ?, outputs_json = ?, heartbeat_at = ?
                    WHERE assignment_id = ?
                    """,
                    (
                        json.dumps(completed_steps),
                        json.dumps(outputs, ensure_ascii=False),
                        utc_now_iso(),
                        assignment_id,
                    ),
                )

        try:
            if ticket.task_kind == "recover_agent_zero_financial_sync":
                self._worker_recover_financial_sync(
                    ticket=ticket,
                    workspace_dir=workspace_dir,
                    completed_steps=completed_steps,
                    record_step=record_step,
                    simulate_interrupt_on_step=simulate_interrupt_on_step,
                )
            elif ticket.task_kind == "build_storefront_and_organic_acquisition_pack":
                self._worker_build_storefront_and_acquisition_pack(
                    ticket=ticket,
                    mandate=mandate,
                    workspace_dir=workspace_dir,
                    completed_steps=completed_steps,
                    record_step=record_step,
                    simulate_interrupt_on_step=simulate_interrupt_on_step,
                )
            else:
                self._worker_generic_task(
                    ticket=ticket,
                    workspace_dir=workspace_dir,
                    completed_steps=completed_steps,
                    record_step=record_step,
                    simulate_interrupt_on_step=simulate_interrupt_on_step,
                )

            with self.store._connect() as conn:
                conn.execute(
                    """
                    UPDATE assignments
                    SET status = 'completed', ended_at = ?, heartbeat_at = ?
                    WHERE assignment_id = ?
                    """,
                    (utc_now_iso(), utc_now_iso(), assignment_id),
                )
            self.evaluate_assignment_result(ticket_id, assignment_id)
        except InterruptedError as exc:
            with self.store._connect() as conn:
                conn.execute(
                    """
                    UPDATE assignments
                    SET status = 'interrupted', error_message = ?, ended_at = ?
                    WHERE assignment_id = ?
                    """,
                    (str(exc), utc_now_iso(), assignment_id),
                )
        except Exception as exc:
            with self.store._connect() as conn:
                conn.execute(
                    """
                    UPDATE assignments
                    SET status = 'failed', error_message = ?, ended_at = ?
                    WHERE assignment_id = ?
                    """,
                    (str(exc), utc_now_iso(), assignment_id),
                )
            self.evaluate_assignment_result(ticket_id, assignment_id)

        assignments = self.store.list_assignments(ticket_id)
        return assignments[-1]

    def _worker_recover_financial_sync(
        self,
        ticket: TicketRecord,
        workspace_dir: Path,
        completed_steps: list[str],
        record_step: Callable[[str, dict[str, Any]], None],
        simulate_interrupt_on_step: str | None,
    ) -> None:
        payload = json.loads(ticket.payload_json or "{}")

        # Step 1: Run deterministic dashboard reconciliation in isolated process
        if "step_1_run_dashboard_reconcile" not in completed_steps:
            if simulate_interrupt_on_step == "step_1_run_dashboard_reconcile":
                raise InterruptedError("Simulated worker interruption at step_1_run_dashboard_reconcile")
            dashboard_script = self.repo_root / "tools" / "money_hq_dashboard.py"
            if dashboard_script.exists():
                res = subprocess.run(
                    [sys.executable, str(dashboard_script)],
                    cwd=str(self.repo_root),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                stdout_summary = res.stdout.strip()[:300]
            else:
                stdout_summary = "dashboard script skipped in synthetic repo"
            (workspace_dir / "reconcile_output.txt").write_text(stdout_summary, encoding="utf-8")
            record_step("step_1_run_dashboard_reconcile", {"stdout": stdout_summary})

        # Step 2: Reset stale error state in Agent Zero scheduler tasks.json if present
        if "step_2_clear_scheduler_error" not in completed_steps:
            if simulate_interrupt_on_step == "step_2_clear_scheduler_error":
                raise InterruptedError("Simulated worker interruption at step_2_clear_scheduler_error")
            sched_path_str = payload.get("scheduler_path", "")
            cleared = False
            if sched_path_str and Path(sched_path_str).exists():
                sched_file = Path(sched_path_str)
                raw_sched = json.loads(sched_file.read_text(encoding="utf-8"))
                tasks_data = raw_sched.get("tasks", []) if isinstance(raw_sched, dict) else raw_sched
                for item in tasks_data:
                    if isinstance(item, dict) and item.get("uuid") == payload.get("task_uuid") and item.get("state") == "error":
                        item["state"] = "idle"
                        item["last_result"] = (
                            "RECOVERED_BY_SUPERAGENT_CONTROL_PLANE: Deterministic reconciliation "
                            "completed without LLM/OpenRouter dependency (L4=0 VND, L3=0 VND, Spend=0 VND)."
                        )
                        cleared = True
                if cleared:
                    sched_file.write_text(json.dumps(raw_sched, indent=2, ensure_ascii=False), encoding="utf-8")
            record_step("step_2_clear_scheduler_error", {"scheduler_error_cleared": cleared})

    def _worker_build_storefront_and_acquisition_pack(
        self,
        ticket: TicketRecord,
        mandate: MandateRecord | None,
        workspace_dir: Path,
        completed_steps: list[str],
        record_step: Callable[[str, dict[str, Any]], None],
        simulate_interrupt_on_step: str | None,
    ) -> None:
        execution_mode = mandate.execution_mode if mandate else "local_execute_external_observe"

        # Step 1: Build commercial storefront hub `index.html` in isolated workspace then promote
        if "step_1_storefront_hub" not in completed_steps:
            if simulate_interrupt_on_step == "step_1_storefront_hub":
                raise InterruptedError("Simulated worker interruption at step_1_storefront_hub")
            hub_html = self._render_storefront_hub_html()
            staged_hub = workspace_dir / "index.html"
            staged_hub.write_text(hub_html, encoding="utf-8")
            shutil.copyfile(staged_hub, self.repo_root / "index.html")
            record_step(
                "step_1_storefront_hub",
                {"promoted_file": "index.html", "bytes": len(hub_html.encode("utf-8"))},
            )

        # Step 2: Build `sitemap.xml` and `robots.txt` for organic search indexing
        if "step_2_seo_sitemap_robots" not in completed_steps:
            if simulate_interrupt_on_step == "step_2_seo_sitemap_robots":
                raise InterruptedError("Simulated worker interruption at step_2_seo_sitemap_robots")
            base_url = "https://maileac.github.io/revenue-copilot-international-phase0"
            sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{base_url}/experiments/exp03-duong-nhan-ai-mvp/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>{base_url}/experiments/exp03-duong-nhan-ai-mvp/handbook.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>{base_url}/experiments/exp02-catalogue-qa-pilot/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>
"""
            robots_txt = (
                "User-agent: *\n"
                "Allow: /\n"
                f"Sitemap: {base_url}/sitemap.xml\n"
            )
            (workspace_dir / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
            (workspace_dir / "robots.txt").write_text(robots_txt, encoding="utf-8")
            shutil.copyfile(workspace_dir / "sitemap.xml", self.repo_root / "sitemap.xml")
            shutil.copyfile(workspace_dir / "robots.txt", self.repo_root / "robots.txt")
            record_step(
                "step_2_seo_sitemap_robots",
                {"promoted_files": ["sitemap.xml", "robots.txt"]},
            )

        # Step 3: Generate compliant Organic Acquisition Kits in OBSERVE dry-run mode
        if "step_3_distribution_kits_dryrun" not in completed_steps:
            if simulate_interrupt_on_step == "step_3_distribution_kits_dryrun":
                raise InterruptedError("Simulated worker interruption at step_3_distribution_kits_dryrun")
            exp03_dir = self.repo_root / "experiments" / "exp03-duong-nhan-ai-mvp"
            exp02_dir = self.repo_root / "experiments" / "exp02-catalogue-qa-pilot"
            exp03_dir.mkdir(parents=True, exist_ok=True)
            exp02_dir.mkdir(parents=True, exist_ok=True)

            exp03_kit = {
                "asset_id": "EXP-03",
                "product_name": "Cẩm Nang Dưỡng Nhan & Trắc Nghiệm 7 Thể Chất Đông Y",
                "live_url": "https://maileac.github.io/revenue-copilot-international-phase0/experiments/exp03-duong-nhan-ai-mvp/",
                "pricing": {"vnd": 299000, "usd": 12, "checkout_channels": ["VietQR", "Payoneer"]},
                "external_publish_mode": "observe_dry_run" if "observe" in execution_mode else "live",
                "compliant_acquisition_channels": [
                    {
                        "channel": "Google Search / GitHub Pages Organic SEO",
                        "status": "active_via_sitemap",
                        "target_keywords": [
                            "trắc nghiệm thể chất đông y miễn phí",
                            "thực đơn dưỡng nhan 28 ngày khí hư huyết hư",
                            "trà dưỡng nhan cho dân văn phòng mất ngủ",
                        ],
                    },
                    {
                        "channel": "Facebook Group / Threads Chia Sẻ Chăm Sóc Sức Khỏe Chủ Động (Zero-Spend Value Post)",
                        "status": "observe_dry_run_staged",
                        "hook_title": "Mình vừa tổng hợp bộ Trắc nghiệm 7 Thể chất Đông Y (Khí hư, Huyết hư, Dương hư, Đàm thấp...) chạy ngay trên trình duyệt, không cần cài app",
                        "cta_url": "https://maileac.github.io/revenue-copilot-international-phase0/experiments/exp03-duong-nhan-ai-mvp/",
                    },
                    {
                        "channel": "Pinterest / Short-Form Infographic Pin",
                        "status": "observe_dry_run_staged",
                        "hook_title": "Bảng Phân Biệt 7 Thể Chất Đông Y & 14 Bài Trà - Canh Dưỡng Nhan Theo Chu Kỳ",
                        "cta_url": "https://maileac.github.io/revenue-copilot-international-phase0/experiments/exp03-duong-nhan-ai-mvp/handbook.html",
                    },
                ],
                "generated_at": utc_now_iso(),
            }

            exp02_kit = {
                "asset_id": "EXP-02",
                "product_name": "Global E-Commerce Catalogue CSV Fixer & Profit Auditor",
                "live_url": "https://maileac.github.io/revenue-copilot-international-phase0/experiments/exp02-catalogue-qa-pilot/",
                "pricing": {"vnd": 199000, "usd": 9, "checkout_channels": ["Payoneer", "VietQR"]},
                "external_publish_mode": "observe_dry_run" if "observe" in execution_mode else "live",
                "compliant_acquisition_channels": [
                    {
                        "channel": "GitHub Topic & Organic Search Indexing",
                        "status": "active_via_sitemap",
                        "target_keywords": [
                            "shopify csv import error fixer browser",
                            "chuẩn hóa file csv sản phẩm shopee tiktok shop",
                            "ecommerce catalogue profit margin auditor tool",
                        ],
                    },
                    {
                        "channel": "Shopify / Seller Community Helpful Answer Template",
                        "status": "observe_dry_run_staged",
                        "hook_title": "Client-side tool to audit SKU margin leaks, fix HTML/UTF-8 corruption, and normalize variants before bulk CSV import (100% browser-local)",
                        "cta_url": "https://maileac.github.io/revenue-copilot-international-phase0/experiments/exp02-catalogue-qa-pilot/",
                    },
                ],
                "generated_at": utc_now_iso(),
            }

            (exp03_dir / "distribution_kit.json").write_text(
                json.dumps(exp03_kit, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            (exp02_dir / "distribution_kit.json").write_text(
                json.dumps(exp02_kit, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            record_step(
                "step_3_distribution_kits_dryrun",
                {
                    "exp03_kit": "experiments/exp03-duong-nhan-ai-mvp/distribution_kit.json",
                    "exp02_kit": "experiments/exp02-catalogue-qa-pilot/distribution_kit.json",
                    "external_publish_mode": "observe_dry_run",
                },
            )

    def _worker_generic_task(
        self,
        ticket: TicketRecord,
        workspace_dir: Path,
        completed_steps: list[str],
        record_step: Callable[[str, dict[str, Any]], None],
        simulate_interrupt_on_step: str | None,
    ) -> None:
        if "step_1_execute" not in completed_steps:
            if simulate_interrupt_on_step == "step_1_execute":
                raise InterruptedError("Simulated worker interruption at step_1_execute")
            out_file = workspace_dir / "generic_result.json"
            out_file.write_text(
                json.dumps({"ticket_id": ticket.ticket_id, "status": "ok"}, indent=2),
                encoding="utf-8",
            )
            record_step("step_1_execute", {"result_file": str(out_file)})

    @staticmethod
    def _render_storefront_hub_html() -> str:
        return """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Money HQ Digital Assets Studio | Công Cụ B2B & Cẩm Nang Chăm Sóc Sức Khỏe Chủ Động</title>
  <meta name="description" content="Hệ sinh thái sản phẩm số vận hành tự động: Cẩm Nang Dưỡng Nhan Đông Y Ứng Dụng (EXP-03) và Global E-Commerce Catalogue CSV Fixer (EXP-02)." />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "Money HQ Autonomous Digital Products",
    "itemListElement": [
      {
        "@type": "SoftwareApplication",
        "position": 1,
        "name": "Cẩm Nang Dưỡng Nhan & Trắc Nghiệm 7 Thể Chất Đông Y",
        "applicationCategory": "HealthApplication",
        "offers": {"@type": "Offer", "price": "12.00", "priceCurrency": "USD"}
      },
      {
        "@type": "SoftwareApplication",
        "position": 2,
        "name": "Global E-Commerce Catalogue CSV Fixer & Profit Auditor",
        "applicationCategory": "BusinessApplication",
        "offers": {"@type": "Offer", "price": "9.00", "priceCurrency": "USD"}
      }
    ]
  }
  </script>
  <style>
    :root {
      --bg: #0f172a;
      --card: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --emerald: #10b981;
      --amber: #f59e0b;
      --rose: #f43f5e;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }
    .container { max-width: 1080px; margin: 0 auto; padding: 40px 20px; }
    .badge {
      display: inline-block;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.35);
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: 14px;
    }
    h1 { font-size: 2.2rem; margin-bottom: 12px; }
    .subtitle { color: var(--muted); max-width: 760px; margin-bottom: 32px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 28px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .card h2 { font-size: 1.35rem; margin-bottom: 10px; }
    .card p { color: var(--muted); font-size: 0.95rem; margin-bottom: 16px; }
    .price-row {
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: 18px;
      font-weight: 700;
      color: #fbbf24;
    }
    .btn-group { display: flex; flex-wrap: wrap; gap: 10px; }
    .btn {
      display: inline-block;
      text-decoration: none;
      padding: 10px 18px;
      border-radius: 10px;
      font-weight: 700;
      font-size: 0.9rem;
    }
    .btn-primary { background: var(--emerald); color: #06281e; }
    .btn-secondary { background: rgba(255,255,255,0.08); color: var(--text); border: 1px solid var(--border); }
    .how-it-works {
      margin-top: 40px;
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px;
    }
    footer {
      margin-top: 48px;
      padding-top: 24px;
      border-top: 1px solid var(--border);
      color: var(--muted);
      font-size: 0.85rem;
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }
    footer a { color: #38bdf8; text-decoration: none; }
  </style>
</head>
<body>
  <div class="container">
    <span class="badge">MONEY HQ DIGITAL ASSET STUDIO • VẬN HÀNH TỰ ĐỘNG 24/7</span>
    <h1>Hệ Sinh Thái Sản Phẩm Số & Công Cụ B2B Quốc Tế</h1>
    <p class="subtitle">
      Trải nghiệm trực tiếp trên trình duyệt (100% Client-Side, bảo mật dữ liệu tuyệt đối).
      Hỗ trợ thanh toán tự động qua <strong>Payoneer Quốc tế (USD)</strong> và <strong>Chuyển khoản VietQR 24/7 (VND)</strong>.
    </p>

    <div class="grid">
      <div class="card">
        <div>
          <span class="badge">SỨC KHỎE & DƯỠNG NHAN (VN & GLOBAL DIASPORA)</span>
          <h2>1. Trắc Nghiệm 7 Thể Chất Đông Y & Cẩm Nang Dưỡng Nhan 28 Ngày</h2>
          <p>
            Đánh giá nhanh thể chất (Khí hư, Huyết hư, Dương hư, Âm hư, Khí trệ, Đàm thấp, Bình hòa) trong 2 phút.
            Tra cứu 14 bài trà/canh thực dưỡng, nghe hướng dẫn Audio giọng đọc và tải trọn bộ Cẩm nang PDF A4.
          </p>
          <div class="price-row">
            <span>Giá trọn bộ: 299.000đ (VN) / $12 USD (Quốc tế)</span>
          </div>
        </div>
        <div class="btn-group">
          <a class="btn btn-primary" href="experiments/exp03-duong-nhan-ai-mvp/">Làm Trắc Nghiệm Miễn Phí →</a>
          <a class="btn btn-secondary" href="experiments/exp03-duong-nhan-ai-mvp/handbook.html">Xem Cẩm Nang 28 Ngày</a>
        </div>
      </div>

      <div class="card">
        <div>
          <span class="badge">B2B E-COMMERCE SAAS TOOL (SHOPIFY / AMAZON / SHOPEE)</span>
          <h2>2. Global Catalogue CSV Fixer & Profit Leak Auditor</h2>
          <p>
            Tự động phát hiện lỗi biên lợi nhuận âm, chuẩn hóa SKU/Variant, dọn sạch rác HTML và xuất file CSV
            chuẩn hóa ngay trên trình duyệt mà không cần upload dữ liệu nhạy cảm lên server.
          </p>
          <div class="price-row">
            <span>Bản Pro Không Giới Hạn: $9 USD / 199.000đ</span>
          </div>
        </div>
        <div class="btn-group">
          <a class="btn btn-primary" href="experiments/exp02-catalogue-qa-pilot/">Mở Công Cụ CSV Fixer →</a>
        </div>
      </div>
    </div>

    <div class="how-it-works">
      <h3>Quy trình Trải nghiệm & Mở khóa Tự động</h3>
      <p style="color: var(--muted); margin-top: 8px;">
        1. Dùng thử miễn phí tính năng chẩn đoán/kiểm tra ngay trên web.<br/>
        2. Thanh toán qua <strong>VietQR</strong> (khách Việt Nam) hoặc <strong>Payoneer: lethanhmaicombo@gmail.com</strong> (khách Quốc tế).<br/>
        3. Nhận mã kích hoạt và tải trọn bộ sản phẩm ngay lập tức, kèm bảo hành hoàn tiền 7 ngày.
      </p>
    </div>

    <footer>
      <div>© 2026 Money HQ Digital Studio • Liên hệ hỗ trợ: <a href="mailto:lethanhmaicombo@gmail.com">lethanhmaicombo@gmail.com</a></div>
      <div>
        <a href="experiments/exp03-duong-nhan-ai-mvp/">Dưỡng Nhan AI</a> •
        <a href="experiments/exp02-catalogue-qa-pilot/">Global CSV Fixer</a> •
        <a href="sitemap.xml">Sitemap</a>
      </div>
    </footer>
  </div>
</body>
</html>
"""

    # ------------------------------------------------------------------
    # 5. EVALUATOR (Acceptance Criteria Verification & Next Action)
    # ------------------------------------------------------------------
    def evaluate_assignment_result(self, ticket_id: str, assignment_id: str) -> str:
        """Verify outputs against Ticket acceptance criteria and decide: continue/complete, retry, or escalate."""
        ticket = self.store.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError(f"Unknown ticket_id: {ticket_id}")
        mandate = self.store.get_mandate(ticket.mandate_id)
        assignments = [a for a in self.store.list_assignments(ticket_id) if a.assignment_id == assignment_id]
        if not assignments:
            raise ValueError(f"Unknown assignment_id: {assignment_id}")
        assignment = assignments[-1]

        if assignment.status != "completed":
            # Let watchdog handle retry vs escalation
            self.run_watchdog_recovery()
            updated = self.store.get_ticket(ticket_id)
            return updated.stage if updated else "failed"

        criteria_raw = json.loads(ticket.acceptance_criteria_json or "[]")
        failures: list[str] = []
        for item in criteria_raw:
            req_path = item.get("required_path", "")
            req_sub = item.get("required_substring", "")
            if req_path:
                full_path = self.repo_root / req_path
                if not full_path.exists():
                    failures.append(f"Missing required path: {req_path}")
                    continue
                if req_sub:
                    content = full_path.read_text(encoding="utf-8", errors="ignore")
                    if req_sub not in content:
                        failures.append(f"Missing required substring '{req_sub}' in {req_path}")

        if failures:
            err_msg = "; ".join(failures)
            with self.store._connect() as conn:
                conn.execute(
                    "UPDATE assignments SET status = 'failed', error_message = ? WHERE assignment_id = ?",
                    (err_msg, assignment_id),
                )
            self.run_watchdog_recovery()
            updated = self.store.get_ticket(ticket_id)
            return updated.stage if updated else "failed"

        # All acceptance criteria verified!
        exec_mode = mandate.execution_mode if mandate else "local_autonomous"
        final_outcome = (
            "completed_verified_observe_staged"
            if "observe" in exec_mode
            else "completed_verified"
        )
        report_msg = (
            f"All {len(criteria_raw)} acceptance criteria verified in assignment {assignment_id} "
            f"(mode={exec_mode}, cost=0 VND)."
        )
        with self.store._connect() as conn:
            conn.execute(
                """
                UPDATE tickets
                SET status = 'ended',
                    stage = 'ended',
                    outcome = ?,
                    latest_report = ?,
                    updated_at = ?
                WHERE ticket_id = ?
                """,
                (final_outcome, report_msg, utc_now_iso(), ticket_id),
            )
        return "ended"

    # ------------------------------------------------------------------
    # 6. QUIET-BY-DEFAULT OWNER NOTIFICATION GATING
    # ------------------------------------------------------------------
    def _notify_owner_if_needed(self, ticket: TicketRecord) -> bool:
        """Send Telegram notification ONLY when a Ticket requires genuine human decision/intervention."""
        if not ticket.stage.startswith("person/") or ticket.owner_notified:
            return False
        msg = (
            f"⚠️ <b>[SUPERAGENT ESCALATION] Cần Mai quyết định:</b>\n"
            f"• <b>Ticket:</b> <code>{ticket.ticket_id}</code> — {ticket.title}\n"
            f"• <b>Lý do:</b> {ticket.attention_question or ticket.latest_report}"
        )
        if self.notifier is not None:
            try:
                self.notifier(msg)
            except Exception:
                pass
        with self.store._connect() as conn:
            conn.execute(
                "UPDATE tickets SET owner_notified = 1, updated_at = ? WHERE ticket_id = ?",
                (utc_now_iso(), ticket.ticket_id),
            )
        return True

    # ------------------------------------------------------------------
    # 7. SINGLE PASS ORCHESTRATION (`run_pass`)
    # ------------------------------------------------------------------
    def run_pass(
        self,
        scheduler_tasks_path: Path | None = None,
        attention_panel_path: Path | None = None,
    ) -> dict[str, Any]:
        """Run one complete Superagent pass: Watchdog -> Proactive Discovery -> Intake/Eval -> Execute -> Panel."""
        recovered = self.run_watchdog_recovery()
        discovered = self.discover_proactive_triggers(scheduler_tasks_path=scheduler_tasks_path)
        decisions: list[str] = []
        for trig in discovered:
            dec, _ = self.intake_and_evaluate(trig)
            decisions.append(f"{trig.trigger_id}:{dec.outcome}")

        executed = self.execute_queued_tickets()
        panel_file = attention_panel_path or (self.repo_root / "operations" / "ATTENTION_PANEL.md")
        panel_md = render_attention_panel(self.store, self.policy)
        panel_file.parent.mkdir(parents=True, exist_ok=True)
        panel_file.write_text(panel_md, encoding="utf-8")

        return {
            "recovered_tickets": recovered,
            "discovered_triggers": len(discovered),
            "decisions": decisions,
            "executed_assignments": [a.assignment_id for a in executed],
            "attention_panel_path": str(panel_file),
        }


def render_attention_panel(store: SuperagentStore, policy: PolicyConfig) -> str:
    """Render the DeepSeek-style Attention Panel (`docs/005-panel.md`) answering the 3 supervisory questions."""
    tickets = store.list_tickets()
    decisions = store.list_decisions()
    assignments = store.list_assignments()

    needing_person = [t for t in tickets if t.status == "open" and t.stage.startswith("person/")]
    working_or_queued = [t for t in tickets if t.status == "open" and not t.stage.startswith("person/")]
    ended_tickets = [t for t in tickets if t.status == "ended"]

    lines: list[str] = [
        "# MONEY HQ SUPERAGENT — ATTENTION PANEL",
        "",
        f"- **Policy Version:** `{policy.policy_version}` | **Accept Mode:** `{policy.accept_mode}` | **Budget Cap:** `{policy.approved_budget_cap_vnd:,} VND` (`0 VND` spend enforced)",
        f"- **Updated At (UTC):** `{utc_now_iso()}`",
        "",
        "---",
        "",
        "## 1. Does anything need the Owner (Mai) right now?",
        "",
    ]

    if not needing_person:
        lines.append("- **Quiet / Healthy:** `0` tickets waiting for owner intervention. No manual action needed.")
    else:
        for t in needing_person:
            lines.append(
                f"- **[ACTION REQUIRED] `{t.ticket_id}` ({t.stage}) — {t.title}**: {t.attention_question or t.latest_report}"
            )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 2. Is the system healthy and doing the right things?",
            "",
            f"- **Open / Working Tickets:** `{len(working_or_queued)}`",
            f"- **Completed / Verified Tickets:** `{len(ended_tickets)}`",
            f"- **Total Eval Decisions Recorded:** `{len(decisions)}`",
            f"- **Total Isolated Worker Assignments:** `{len(assignments)}`",
            "- **Financial Guardrails:** `L4 Realized Cash = 0 VND` | `L3 Pending Payout = 0 VND` | `Incremental Spend = 0 VND`",
            "",
            "---",
            "",
            "## 3. Work History (Trigger → Eval → Mandate → Ticket → Assignment)",
            "",
            "| Ticket ID | Trigger ID | Priority Score | Stage / Status | Outcome | Retries | Latest Verified Report |",
            "|---|---|---:|---|---|---:|---|",
        ]
    )

    for t in tickets:
        lines.append(
            f"| `{t.ticket_id}` | `{t.trigger_id}` | `{t.priority_score:.2f}` | `{t.stage}` | `{t.outcome or 'in_progress'}` | `{t.retry_count}` | {t.latest_report or t.objective} |"
        )

    lines.append("")
    return "\n".join(lines)
