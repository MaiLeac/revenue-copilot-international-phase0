"""Configure Agent Zero v2.13 Scheduled Tasks for Money HQ.

Run inside the agent-zero container:
  /opt/venv-a0/bin/python /a0/usr/projects/money-hq/tools/agent-zero-setup/configure_scheduler.py
"""

from __future__ import annotations

import asyncio
import sys

sys.path.insert(0, "/a0")

from helpers.task_scheduler import ScheduledTask, TaskSchedule, TaskScheduler  # type: ignore


async def configure_money_hq_tasks() -> None:
    scheduler = TaskScheduler.get()
    await scheduler.reload()

    managed_names = {
        "Money HQ - Daily Operational and Opportunity Review",
        "Money HQ - Revenue Execution",
        "Money HQ - Daily Financial and Blocker Report",
    }
    for existing in list(scheduler.get_tasks()):
        if existing.name in managed_names:
            await scheduler.remove_task_by_uuid(existing.uuid)

    task_ops = ScheduledTask.create(
        name="Money HQ - Revenue Execution",
        system_prompt=(
            "You are money-coo. Follow OPERATING_SYSTEM.md, agents/AI_ROUTING_POLICY.md, "
            "and agents/COST_OPTIMIZATION_POLICY.md. Use deterministic scripts first "
            "(0 VND marginal cost). Do not spawn recursive tasks."
        ),
        prompt=(
            "Work in /a0/usr/projects/money-hq. Read git status and the previous task result. "
            "Complete one bounded, reversible improvement to an existing revenue path within 25 minutes. "
            "EXP-03 is digital-book-only: no physical tea, shipping, fabricated expert support or "
            "unverified payment confirmation. Prioritize removing a concrete purchase/delivery blocker, "
            "then verify the actual changed behavior. Do not stop after pytest or a research report. "
            "Do not start new projects, agents, trading processes, paid usage, outreach, publishing, "
            "account setup or credential changes. Preserve unrelated edits. Record changed files, "
            "verification and the next executable step in operations/EXECUTION_HANDOFF.md. "
            "If blocked, finish an independent useful task. Never delegate routine investigation back "
            "to the owner or treat missing sales as healthy because tests pass. Report facts only."
        ),
        schedule=TaskSchedule(
            minute="30",
            hour="*/4",
            day="*",
            month="*",
            weekday="*",
            timezone="Asia/Saigon",
        ),
        timezone="Asia/Saigon",
        project_name="money-hq",
        project_color="#10b981",
    )

    task_fin = ScheduledTask.create(
        name="Money HQ - Daily Financial and Blocker Report",
        system_prompt=(
            "You are money-coo. Follow OPERATING_SYSTEM.md and agents/COST_OPTIMIZATION_POLICY.md. "
            "Never fabricate revenue or mix L3 pending payouts with L4 realized cash."
        ),
        prompt=(
            "In /a0/usr/projects/money-hq, run `python tools/money_hq_dashboard.py` to verify "
            "L4 realized cash, L3 pending payouts, and the 500,000 VND budget cap. If any "
            "blocker, rejection spike, or budget alert exists, update operations/DAILY_BRIEF.md "
            "and operations/OWNER_ACTIONS.md."
        ),
        schedule=TaskSchedule(
            minute="30",
            hour="20",
            day="*",
            month="*",
            weekday="*",
            timezone="Asia/Saigon",
        ),
        timezone="Asia/Saigon",
        project_name="money-hq",
        project_color="#10b981",
    )

    await scheduler.add_task(task_ops)
    await scheduler.add_task(task_fin)
    await scheduler.save()
    print(f"Configured {len(scheduler.get_tasks())} scheduled tasks in /a0/usr/scheduler/tasks.json")


if __name__ == "__main__":
    asyncio.run(configure_money_hq_tasks())
