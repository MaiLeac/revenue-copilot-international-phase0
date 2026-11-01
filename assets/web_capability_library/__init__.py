"""Money HQ Reusable Web Capability Library & Independent Visual Quality Gate.

Combines MaiLeac's curated GitHub Stars (`Nutlope/hallmark`, `alchaincyf/huashu-design`,
`eternity4719/HowToLiveBetter`, `Vincentwei1021/video-shotcraft`, `browser-use/browser-use`)
and owned repositories (`MaiLeac/flow-scout-core`, `MaiLeac/Sisan`, `MaiLeac/vuong-quoc-loser`,
`MaiLeac/awesome-ai-video-code`) into a queryable capability library and anti-AI-slop gate.
"""

from assets.web_capability_library.library import (
    VisualAuditFinding,
    VisualAuditReport,
    audit_html_file,
    audit_html_source,
    get_approved_dependencies,
    get_decision_guide,
    load_catalog,
    search_capabilities,
)

__all__ = [
    "VisualAuditFinding",
    "VisualAuditReport",
    "audit_html_file",
    "audit_html_source",
    "get_approved_dependencies",
    "get_decision_guide",
    "load_catalog",
    "search_capabilities",
]
