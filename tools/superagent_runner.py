"""Money HQ Superagent Control Plane CLI Runner.

Executes proactive discovery, intake/evaluation, crash recovery, isolated worker
assignments, acceptance verification, and updates `operations/ATTENTION_PANEL.md`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from assets.superagent_control_plane import (
    ControlPlaneEngine,
    PolicyConfig,
    SuperagentStore,
    render_attention_panel,
)
from tools.telegram_notify import send_telegram_alert


def build_engine(db_path: Path | None = None, dry_run_notify: bool = True) -> ControlPlaneEngine:
    actual_db = db_path or (REPO_ROOT / "operations" / "superagent_store.db")
    store = SuperagentStore(actual_db)
    policy = PolicyConfig(
        policy_version="2026-11-01.v1",
        accept_mode="observe",
        approved_budget_cap_vnd=0,
        max_concurrent_workers=2,
        default_timeout_sec=120,
        default_max_retries=2,
    )
    return ControlPlaneEngine(
        repo_root=REPO_ROOT,
        store=store,
        policy=policy,
        notifier=lambda msg: send_telegram_alert(msg, dry_run=dry_run_notify),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Money HQ Superagent Control Plane Runner")
    parser.add_argument("--run-pass", action="store_true", help="Run one complete proactive control plane pass")
    parser.add_argument(
        "--demonstrate-recovery",
        action="store_true",
        help="Demonstrate step interruption + Watchdog crash recovery on the first pass",
    )
    parser.add_argument("--live-notify", action="store_true", help="Enable live Telegram escalation notifications")
    args = parser.parse_args()

    engine = build_engine(dry_run_notify=not args.live_notify)

    if args.demonstrate_recovery:
        # 1. Discover proactive triggers and intake/evaluate them
        triggers = engine.discover_proactive_triggers()
        for trig in triggers:
            engine.intake_and_evaluate(trig)

        # 2. Simulate an interruption mid-execution on step 2 of the storefront build
        engine.execute_queued_tickets(simulate_interrupt_on_step="step_2_seo_sitemap_robots")

        # 3. Run full pass: Watchdog detects the interrupted assignment, recovers from step 1 checkpoint without repeating step 1, finishes steps 2 & 3, and verifies acceptance criteria!
        summary = engine.run_pass()
        print(json.dumps({"mode": "recovery_demonstrated", **summary}, indent=2, ensure_ascii=False))
        return 0

    summary = engine.run_pass()
    print(json.dumps({"mode": "standard_pass", **summary}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
