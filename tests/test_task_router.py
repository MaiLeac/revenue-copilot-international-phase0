from pathlib import Path
import pytest
from tools.task_router import TaskRouter, TaskComplexity, ModelProvider, TaskSpec

def test_task_router_classifies_deterministic_commands():
    router = TaskRouter()
    spec = router.classify_task("báo cáo")
    assert spec.complexity == TaskComplexity.DETERMINISTIC
    decision = router.route_task(spec)
    assert decision.selected_provider == ModelProvider.DETERMINISTIC_SCRIPT
    assert decision.estimated_cost_usd == 0.0

def test_task_router_identifies_critical_risk():
    router = TaskRouter()
    spec = router.classify_task("Mở lệnh mua trên real account")
    assert spec.complexity == TaskComplexity.CRITICAL
    assert spec.requires_financial_authorization is True

def test_task_router_handles_coding_fallback_when_codex_unavailable():
    router = TaskRouter()
    spec = router.classify_task("Refactor css and fix button bug in index.html")
    assert spec.requires_code_generation is True
    decision = router.route_task(spec)
    assert decision.selected_provider == ModelProvider.ANTIGRAVITY_GEMINI
    assert "Codex" in decision.reason

def test_task_router_logs_audit_record(tmp_path: Path):
    router = TaskRouter(repo_root=tmp_path)
    spec = router.classify_task("test")
    decision = router.route_task(spec)
    router.log_decision(decision, spec)
    assert router.log_path.exists()
    content = router.log_path.read_text(encoding="utf-8")
    assert "deterministic_script" in content
