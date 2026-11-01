"""Unit tests for the Deterministic Catalogue QA Engine (SVC-01 / EXP-02)."""

from __future__ import annotations

from pathlib import Path

import pytest

from assets.catalogue_qa_engine.catalogue_qa import CatalogueQAEngine
from assets.catalogue_qa_engine.generate_synthetic_sample import (
    build_synthetic_dirty_rows,
    generate_portfolio_sample,
)
from assets.catalogue_qa_engine.report_generator import (
    compute_catalogue_health_score,
    generate_html_report_from_csv,
)


def test_catalogue_engine_restores_leading_zeros_and_normalizes_fields() -> None:
    engine = CatalogueQAEngine(expected_sku_digits=6, max_rows=200)
    rows = [
        {
            "Handle": "  Linen Resort Shirt  ",
            "Title": "  Linen Resort Shirt  ",
            "Body (HTML)": "<p>Contact supplier@vendor.com or +1-415-555-0199</p>",
            "Vendor": "Avenue",
            "Option1 Name": " size ",
            "Option1 Value": "M",
            "Variant SKU": "4101",
            "Variant Price": " $29.00 ",
            "Variant Compare At Price": "39.00",
            "Status": "ACTIVE",
        }
    ]
    cleaned, issues, summary = engine.audit_and_clean_rows(rows)
    assert len(cleaned) == 1
    row = cleaned[0]
    assert row["Handle"] == "linen-resort-shirt"
    assert row["Title"] == "Linen Resort Shirt"
    assert row["Variant SKU"] == "004101"
    assert row["Variant Price"] == "29.00"
    assert row["Option1 Name"] == "Size"
    assert row["Status"] == "active"
    assert "[REDACTED_EMAIL]" in row["Body (HTML)"]
    assert "[REDACTED_PHONE]" in row["Body (HTML)"]
    assert summary.critical_unresolved_count == 0
    assert summary.passed_ready_for_import is True
    assert summary.pii_flags_count == 1


def test_catalogue_engine_flags_duplicate_and_missing_skus_and_invalid_prices() -> None:
    engine = CatalogueQAEngine(expected_sku_digits=6, max_rows=200)
    rows = [
        {
            "Handle": "item-a",
            "Title": "Item A",
            "Option1 Name": "Size",
            "Option1 Value": "S",
            "Variant SKU": "001001",
            "Variant Price": "20.00",
            "Variant Compare At Price": "25.00",
            "Status": "active",
        },
        {
            "Handle": "item-a",
            "Title": "Item A",
            "Option1 Name": "Size",
            "Option1 Value": "M",
            "Variant SKU": "001001",  # Duplicate SKU
            "Variant Price": "0.00",    # Invalid price
            "Variant Compare At Price": "",
            "Status": "active",
        },
        {
            "Handle": "item-a",
            "Title": "Item A",
            "Option1 Name": "Size",
            "Option1 Value": "",        # Missing option value
            "Variant SKU": "",          # Missing SKU
            "Variant Price": "20.00",
            "Variant Compare At Price": "",
            "Status": "active",
        },
    ]
    _, issues, summary = engine.audit_and_clean_rows(rows)
    codes = {i.issue_code for i in issues}
    assert "DUPLICATE_SKU" in codes
    assert "INVALID_OR_NON_POSITIVE_PRICE" in codes
    assert "MISSING_SKU" in codes
    assert "MISSING_OPTION_VALUE" in codes
    assert summary.critical_unresolved_count == 4
    assert summary.passed_ready_for_import is False


def test_catalogue_engine_enforces_max_rows_cap() -> None:
    engine = CatalogueQAEngine(expected_sku_digits=6, max_rows=5)
    rows = [{"Handle": f"h-{i}", "Title": "T", "Option1 Name": "Size", "Option1 Value": "S", "Variant SKU": f"00000{i}", "Variant Price": "10.00"} for i in range(6)]
    with pytest.raises(ValueError, match="exceeds maximum scoped limit"):
        engine.audit_and_clean_rows(rows)


def test_generate_synthetic_portfolio_sample_creates_all_artifacts(tmp_path: Path) -> None:
    dirty_rows = build_synthetic_dirty_rows()
    assert len(dirty_rows) == 120
    generate_portfolio_sample(tmp_path)
    assert (tmp_path / "synthetic_dirty_catalogue_120rows.csv").exists()
    assert (tmp_path / "synthetic_cleaned_catalogue_120rows.csv").exists()
    assert (tmp_path / "synthetic_issue_log.csv").exists()
    assert (tmp_path / "SYNTHETIC_CASE_STUDY_REPORT.md").exists()


def test_executive_html_report_generator_creates_self_contained_report(tmp_path: Path) -> None:
    generate_portfolio_sample(tmp_path)
    dirty_csv = tmp_path / "synthetic_dirty_catalogue_120rows.csv"
    out_html = tmp_path / "sample_executive_audit_report.html"
    summary = generate_html_report_from_csv(
        input_csv=dirty_csv,
        output_html=out_html,
        client_label="Unit Test Batch",
    )
    assert out_html.exists()
    content = out_html.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Unit Test Batch" in content
    assert "DUPLICATE_SKU" in content
    assert "SKU_LEADING_ZERO_RESTORED" in content
    assert "supplier@example-vendor.com" not in content  # Raw PII must never leak into HTML report
    score = compute_catalogue_health_score(summary)
    assert 0 <= score <= 100

