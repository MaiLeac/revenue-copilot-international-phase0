"""Unit and integration tests for the Web Capability Library and Visual Quality Gate.

Verifies:
1. Complete catalog loaded from `assets/web_capability_library/catalog.json`.
2. Query/search capability by category, project, and query term.
3. Decision guide and approved dependencies schema.
4. Visual quality gate catches Hallmark Floor Gate violations (missing tokens, transition:all, emoji buttons, glued arrows).
5. All live Money HQ HTML assets achieve 100/100 and pass the gate.
"""

from __future__ import annotations

from pathlib import Path

from assets.web_capability_library import (
    audit_html_file,
    audit_html_source,
    get_approved_dependencies,
    get_decision_guide,
    load_catalog,
    search_capabilities,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_catalog_structure_and_counts() -> None:
    catalog = load_catalog()
    assert catalog["owner"] == "MaiLeac"
    assert catalog["pagination_verified"]["github_starred_repositories_total"] == 7
    assert catalog["pagination_verified"]["github_owned_repositories_total"] == 9
    assert len(catalog["resources"]) >= 10

    # Ensure hallmark and huashu-design are present
    names = {r["name"] for r in catalog["resources"]}
    assert "Nutlope/hallmark" in names
    assert "alchaincyf/huashu-design" in names
    assert "MaiLeac/flow-scout-core" in names
    assert "MaiLeac/Sisan" in names


def test_search_capabilities_filtering() -> None:
    # Filter by category
    design_tools = search_capabilities(category="Premium UI components and design systems")
    assert any(r["name"] == "Nutlope/hallmark" for r in design_tools)

    # Filter by target project
    sisan_tools = search_capabilities(project="Sisan / Wink Home")
    assert len(sisan_tools) >= 2
    assert any(r["name"] == "MaiLeac/Sisan" for r in sisan_tools)

    # Filter by query
    qa_tools = search_capabilities(query="Flow-Scout")
    assert any(r["name"] == "MaiLeac/flow-scout-core" for r in qa_tools)


def test_decision_guide_and_approved_dependencies() -> None:
    guide = get_decision_guide()
    assert "1_direct_reuse" in guide
    assert "2_adapt_pattern" in guide
    assert "3_build_from_scratch" in guide

    deps = get_approved_dependencies()
    assert "react_typescript_stack" in deps
    assert "static_html_editorial_stack" in deps
    pkg_names = {p["package"] for p in deps["react_typescript_stack"]}
    assert "lucide-react" in pkg_names
    assert "motion" in pkg_names


def test_visual_audit_catches_ai_slop_violations() -> None:
    # 1. Missing tokens
    rep1 = audit_html_source("<html><body><h1>Hello</h1></body></html>")
    assert not rep1.passed
    assert any(f.gate_id == "GATE-TOKEN-01" for f in rep1.findings)

    # 2. transition: all
    bad_css = "<html><head><style>:root{} a { transition: all 0.3s; }</style></head><body><footer></footer></body></html>"
    rep2 = audit_html_source(bad_css)
    assert not rep2.passed
    assert any(f.gate_id == "GATE-TRANSITION-02" for f in rep2.findings)

    # 3. Emoji in button
    bad_btn = "<html><head><style>:root{} a:focus-visible{} @media (prefers-reduced-motion: reduce){}</style></head><body><button>🚀 Buy</button><footer></footer></body></html>"
    rep3 = audit_html_source(bad_btn)
    assert not rep3.passed
    assert any(f.gate_id == "GATE-SLOP-11" for f in rep3.findings)

    # 4. Glued arrow in CTA
    bad_arrow = "<html><head><style>:root{} a:focus-visible{} @media (prefers-reduced-motion: reduce){}</style></head><body><a href='/buy'>Buy Now →</a><footer></footer></body></html>"
    rep4 = audit_html_source(bad_arrow)
    assert not rep4.passed
    assert any(f.gate_id == "GATE-PUNCT-10" for f in rep4.findings)


def test_live_html_assets_pass_quality_gate() -> None:
    for rel_path in [
        "index.html",
        "experiments/exp03-duong-nhan-ai-mvp/index.html",
        "experiments/exp02-catalogue-qa-pilot/index.html",
    ]:
        p = REPO_ROOT / rel_path
        assert p.exists()
        rep = audit_html_file(p)
        assert rep.passed, f"{rel_path} failed quality gate: {rep.findings}"
        assert rep.score_100 == 100
