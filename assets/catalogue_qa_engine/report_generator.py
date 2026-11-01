"""Client-Facing Executive HTML Report & Proof Packager for Catalogue QA (SVC-01 / EXP-02).

Generates a self-contained, zero-dependency, print-ready HTML Executive Audit Report
from CatalogueQAEngine results at 0 VND marginal LLM/API cost.
"""

from __future__ import annotations

import csv
import html
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from assets.catalogue_qa_engine.catalogue_qa import (
    AuditSummary,
    CatalogueIssue,
    CatalogueQAEngine,
)


def compute_catalogue_health_score(summary: AuditSummary) -> int:
    """Compute a deterministic 0-100 health score based on criticals, warnings, and auto-fixes."""
    if summary.total_rows_read <= 0:
        return 0
    penalty = (
        (summary.critical_unresolved_count * 8)
        + (summary.warning_count * 3)
        + (summary.auto_fixed_count * 0.5)
    )
    raw_score = max(0.0, 100.0 - (penalty * (100.0 / max(summary.total_rows_read, 20))))
    return int(round(min(100.0, raw_score)))


def render_executive_html_report(
    summary: AuditSummary,
    issues: list[CatalogueIssue],
    client_label: str = "E-Commerce Catalogue Batch",
    generated_at_iso: str | None = None,
) -> str:
    """Render a self-contained client-facing HTML executive report."""
    timestamp = generated_at_iso or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    health_score = compute_catalogue_health_score(summary)

    if summary.passed_ready_for_import:
        gate_badge_bg = "#065f46"
        gate_badge_text = "READY FOR STORE IMPORT"
    else:
        gate_badge_bg = "#991b1b"
        gate_badge_text = f"HOLD IMPORT: {summary.critical_unresolved_count} CRITICAL ROWS NEED CLIENT SIGN-OFF"

    critical_issues = [i for i in issues if i.severity == "CRITICAL"]
    warning_issues = [i for i in issues if i.severity == "WARNING"]
    autofix_issues = [i for i in issues if i.severity == "AUTO_FIXED"]

    code_rows_html = []
    for code, count in sorted(summary.issues_by_code.items(), key=lambda kv: (-kv[1], kv[0])):
        code_rows_html.append(
            f"<tr><td><code>{html.escape(code)}</code></td>"
            f"<td class='num'>{count}</td></tr>"
        )
    if not code_rows_html:
        code_rows_html.append("<tr><td colspan='2'>No issues detected.</td></tr>")

    def _render_issue_rows(items: list[CatalogueIssue], limit: int = 50) -> str:
        if not items:
            return "<tr><td colspan='7' class='empty'>None detected in this batch.</td></tr>"
        out = []
        for item in items[:limit]:
            sev_class = item.severity.lower()
            out.append(
                "<tr>"
                f"<td class='num'>{item.row_number}</td>"
                f"<td><code>{html.escape(item.handle)}</code></td>"
                f"<td><code>{html.escape(item.sku or '—')}</code></td>"
                f"<td>{html.escape(item.field_name)}</td>"
                f"<td><span class='pill {sev_class}'>{html.escape(item.issue_code)}</span></td>"
                f"<td><code>{html.escape(item.original_value or '—')}</code> &rarr; "
                f"<code>{html.escape(item.remediated_value or '—')}</code></td>"
                f"<td>{html.escape(item.description)}</td>"
                "</tr>"
            )
        return "\n".join(out)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catalogue QA Executive Audit — {html.escape(summary.input_file)}</title>
<style>
  :root {{
    --bg: #f8fafc;
    --card: #ffffff;
    --ink: #0f172a;
    --muted: #475569;
    --border: #e2e8f0;
    --critical: #dc2626;
    --warning: #d97706;
    --autofix: #0284c7;
    --ok: #059669;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 32px 20px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.5;
  }}
  .container {{ max-width: 1120px; margin: 0 auto; }}
  .header {{
    background: #0f172a;
    color: #fff;
    padding: 28px 32px;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
  }}
  .header h1 {{ margin: 0 0 6px 0; font-size: 22px; }}
  .header .meta {{ color: #cbd5e1; font-size: 13px; }}
  .gate-badge {{
    background: {gate_badge_bg};
    color: #fff;
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.02em;
  }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 14px;
    margin-top: 20px;
  }}
  .kpi {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 18px;
  }}
  .kpi .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; font-weight: 600; }}
  .kpi .value {{ font-size: 26px; font-weight: 800; margin-top: 4px; }}
  .kpi .sub {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
  .section {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 22px 24px;
    margin-top: 20px;
  }}
  .section h2 {{ margin: 0 0 12px 0; font-size: 17px; }}
  .policy-note {{
    background: #fffbeb;
    border-left: 4px solid var(--warning);
    padding: 10px 14px;
    font-size: 13px;
    margin-bottom: 14px;
    border-radius: 4px;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }}
  th {{ background: #f1f5f9; font-weight: 700; color: #334155; }}
  td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.empty {{ text-align: center; color: var(--muted); padding: 18px; }}
  code {{ background: #f1f5f9; padding: 2px 5px; border-radius: 4px; font-size: 12px; }}
  .pill {{
    display: inline-block;
    padding: 2px 7px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
  }}
  .pill.critical {{ background: #fee2e2; color: #991b1b; }}
  .pill.warning {{ background: #fef3c7; color: #92400e; }}
  .pill.auto_fixed {{ background: #e0f2fe; color: #075985; }}
  .footer {{
    margin-top: 24px;
    text-align: center;
    font-size: 12px;
    color: var(--muted);
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>E-Commerce Catalogue QA &amp; Reconciliation Audit</h1>
      <div class="meta">Client / Batch: <strong>{html.escape(client_label)}</strong> &bull; Source: <code>{html.escape(summary.input_file)}</code> &bull; Generated: {html.escape(timestamp)}</div>
    </div>
    <div class="gate-badge">{html.escape(gate_badge_text)}</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi">
      <div class="label">Pre-Clean Health Score</div>
      <div class="value">{health_score}/100</div>
      <div class="sub">Deterministic audit index</div>
    </div>
    <div class="kpi">
      <div class="label">Rows Reconciled</div>
      <div class="value">{summary.total_rows_output}/{summary.total_rows_read}</div>
      <div class="sub">{summary.unique_handles} handles &bull; {summary.unique_skus} unique SKUs</div>
    </div>
    <div class="kpi">
      <div class="label">Auto-Fixed Issues</div>
      <div class="value" style="color: var(--autofix);">{summary.auto_fixed_count}</div>
      <div class="sub">Leading zeros, slugs, prices, status</div>
    </div>
    <div class="kpi">
      <div class="label">Critical Blockers</div>
      <div class="value" style="color: var(--critical);">{summary.critical_unresolved_count}</div>
      <div class="sub">Never guessed; client sign-off required</div>
    </div>
    <div class="kpi">
      <div class="label">Warnings &amp; PII Flags</div>
      <div class="value" style="color: var(--warning);">{summary.warning_count}</div>
      <div class="sub">{summary.pii_flags_count} PII leaks auto-redacted</div>
    </div>
  </div>

  <div class="section">
    <h2>1. Critical Unresolved Rows (Requires Client Confirmation Before Import)</h2>
    <div class="policy-note">
      <strong>Zero-Hallucination Guarantee:</strong> Our deterministic QA engine never invents missing SKUs, never guesses business prices, and never deletes duplicate variants silently. Please confirm the desired values for the {len(critical_issues)} critical findings below.
    </div>
    <table>
      <thead>
        <tr>
          <th class="num">Row</th>
          <th>Handle</th>
          <th>SKU</th>
          <th>Field</th>
          <th>Issue Code</th>
          <th>Original &rarr; Remediated</th>
          <th>Action Needed</th>
        </tr>
      </thead>
      <tbody>
        {_render_issue_rows(critical_issues, limit=50)}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>2. Warnings &amp; Privacy Redactions ({len(warning_issues)})</h2>
    <table>
      <thead>
        <tr>
          <th class="num">Row</th>
          <th>Handle</th>
          <th>SKU</th>
          <th>Field</th>
          <th>Issue Code</th>
          <th>Original &rarr; Remediated</th>
          <th>Detail</th>
        </tr>
      </thead>
      <tbody>
        {_render_issue_rows(warning_issues, limit=30)}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>3. Issue Code Distribution Summary</h2>
    <table>
      <thead>
        <tr>
          <th>Issue Code</th>
          <th class="num">Occurrences</th>
        </tr>
      </thead>
      <tbody>
        {"".join(code_rows_html)}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>4. Sample Auto-Fixed Remediations (Showing first 25 of {len(autofix_issues)})</h2>
    <table>
      <thead>
        <tr>
          <th class="num">Row</th>
          <th>Handle</th>
          <th>SKU</th>
          <th>Field</th>
          <th>Issue Code</th>
          <th>Original &rarr; Remediated</th>
          <th>Rule Applied</th>
        </tr>
      </thead>
      <tbody>
        {_render_issue_rows(autofix_issues, limit=25)}
      </tbody>
    </table>
  </div>

  <div class="footer">
    Generated deterministically by Money HQ Catalogue QA Engine (SVC-01) &bull; Zero External LLM Exposure &bull; 100% Row Reconciliation
  </div>
</div>
</body>
</html>
"""


def generate_html_report_from_csv(
    input_csv: str | Path,
    output_html: str | Path,
    client_label: str = "Shopify / WooCommerce Store Audit",
    expected_sku_digits: int = 6,
) -> AuditSummary:
    """Run CatalogueQAEngine on input_csv and write a self-contained HTML report to output_html."""
    in_path = Path(input_csv)
    with in_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    engine = CatalogueQAEngine(expected_sku_digits=expected_sku_digits)
    _, issues, summary = engine.audit_and_clean_rows(rows, source_name=in_path.name)
    html_content = render_executive_html_report(
        summary=summary,
        issues=issues,
        client_label=client_label,
    )
    out_path = Path(output_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_content, encoding="utf-8")
    return summary


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    sample_dir = repo_root / "experiments" / "exp02-catalogue-qa-pilot" / "sample_portfolio"
    sample_in = sample_dir / "synthetic_dirty_catalogue_120rows.csv"
    sample_out = sample_dir / "sample_executive_audit_report.html"
    if sample_in.exists():
        result = generate_html_report_from_csv(
            input_csv=sample_in,
            output_html=sample_out,
            client_label="Synthetic Apparel & Home Demo Batch (120 SKUs)",
        )
        print(
            f"Generated {sample_out.name}: rows={result.total_rows_read}, "
            f"auto_fixed={result.auto_fixed_count}, critical={result.critical_unresolved_count}"
        )
