"""Deterministic SKU & E-Commerce Catalogue QA Engine (SVC-01 / EXP-02).

Audits, reconciles, and cleans CSV product catalogues (<=200 rows standard pilot batch)
without external API calls or LLM hallucination risk.
"""

from __future__ import annotations

import csv
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}(?!\d)")


@dataclass(frozen=True)
class CatalogueIssue:
    row_number: int
    handle: str
    sku: str
    field_name: str
    severity: str  # CRITICAL, WARNING, AUTO_FIXED
    issue_code: str
    description: str
    original_value: str
    remediated_value: str


@dataclass
class AuditSummary:
    input_file: str
    total_rows_read: int = 0
    total_rows_output: int = 0
    unique_handles: int = 0
    unique_skus: int = 0
    auto_fixed_count: int = 0
    warning_count: int = 0
    critical_unresolved_count: int = 0
    issues_by_code: dict[str, int] = field(default_factory=dict)
    pii_flags_count: int = 0
    passed_ready_for_import: bool = False


class CatalogueQAEngine:
    """Rule-based catalogue QA and normalization engine for Shopify/e-commerce CSV batches."""

    def __init__(self, expected_sku_digits: int = 6, max_rows: int = 500) -> None:
        self.expected_sku_digits = expected_sku_digits
        self.max_rows = max_rows

    def audit_and_clean_rows(
        self,
        rows: list[dict[str, Any]],
        source_name: str = "memory_batch.csv",
    ) -> tuple[list[dict[str, str]], list[CatalogueIssue], AuditSummary]:
        if len(rows) > self.max_rows:
            raise ValueError(
                f"Batch size ({len(rows)} rows) exceeds maximum scoped limit ({self.max_rows} rows)."
            )

        cleaned_rows: list[dict[str, str]] = []
        issues: list[CatalogueIssue] = []
        seen_skus: dict[str, int] = {}
        handle_titles: dict[str, str] = {}
        handle_options: dict[str, set[tuple[str, str]]] = {}

        for idx, raw_row in enumerate(rows, start=2):  # Row 1 is CSV header
            row = {str(k).strip(): ("" if v is None else str(v)) for k, v in raw_row.items()}

            handle = self._clean_whitespace(row.get("Handle", ""))
            title = self._clean_whitespace(row.get("Title", ""))
            sku_raw = row.get("Variant SKU", "").strip()
            price_raw = row.get("Variant Price", "").strip()
            compare_raw = row.get("Variant Compare At Price", "").strip()
            opt1_name = self._clean_whitespace(row.get("Option1 Name", ""))
            opt1_val = self._clean_whitespace(row.get("Option1 Value", ""))
            vendor = self._clean_whitespace(row.get("Vendor", ""))
            status_raw = self._clean_whitespace(row.get("Status", ""))
            body_html = row.get("Body (HTML)", "").strip()

            # 1. Handle normalization
            normalized_handle = self._normalize_handle(handle or title)
            if not normalized_handle:
                self._record_issue(
                    issues,
                    idx,
                    handle,
                    sku_raw,
                    "Handle",
                    "CRITICAL",
                    "MISSING_HANDLE_AND_TITLE",
                    "Both Handle and Title are empty; row cannot be linked to a product.",
                    handle,
                    "",
                )
            elif normalized_handle != handle:
                self._record_issue(
                    issues,
                    idx,
                    normalized_handle,
                    sku_raw,
                    "Handle",
                    "AUTO_FIXED",
                    "HANDLE_NORMALIZED",
                    "Normalized handle slug to lowercase hyphenated ASCII.",
                    handle,
                    normalized_handle,
                )
            row["Handle"] = normalized_handle

            # 2. Title whitespace & parent-child consistency
            if title != row.get("Title", ""):
                self._record_issue(
                    issues,
                    idx,
                    normalized_handle,
                    sku_raw,
                    "Title",
                    "AUTO_FIXED",
                    "WHITESPACE_CLEANED",
                    "Trimmed redundant whitespace in Title.",
                    row.get("Title", ""),
                    title,
                )
            row["Title"] = title
            if normalized_handle:
                if normalized_handle not in handle_titles:
                    if title:
                        handle_titles[normalized_handle] = title
                    else:
                        self._record_issue(
                            issues,
                            idx,
                            normalized_handle,
                            sku_raw,
                            "Title",
                            "CRITICAL",
                            "ORPHAN_VARIANT_NO_PARENT_TITLE",
                            "First occurrence of product Handle is missing a parent Title.",
                            "",
                            "",
                        )

            # 3. SKU checks: missing, leading-zero restoration, duplicate SKU
            cleaned_sku = sku_raw.upper().replace(" ", "")
            if not cleaned_sku:
                self._record_issue(
                    issues,
                    idx,
                    normalized_handle,
                    "",
                    "Variant SKU",
                    "CRITICAL",
                    "MISSING_SKU",
                    "Variant SKU is empty; never invent missing SKUs without client mapping.",
                    sku_raw,
                    "",
                )
            else:
                # Check Excel leading-zero stripping on purely numeric SKUs
                if cleaned_sku.isdigit() and len(cleaned_sku) < self.expected_sku_digits:
                    restored_sku = cleaned_sku.zfill(self.expected_sku_digits)
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        restored_sku,
                        "Variant SKU",
                        "AUTO_FIXED",
                        "SKU_LEADING_ZERO_RESTORED",
                        f"Restored leading zeros on numeric SKU to {self.expected_sku_digits} digits.",
                        sku_raw,
                        restored_sku,
                    )
                    cleaned_sku = restored_sku
                elif cleaned_sku != sku_raw:
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        cleaned_sku,
                        "Variant SKU",
                        "AUTO_FIXED",
                        "SKU_FORMAT_NORMALIZED",
                        "Normalized SKU casing and removed spaces.",
                        sku_raw,
                        cleaned_sku,
                    )

                if cleaned_sku in seen_skus:
                    first_row = seen_skus[cleaned_sku]
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        cleaned_sku,
                        "Variant SKU",
                        "CRITICAL",
                        "DUPLICATE_SKU",
                        f"Duplicate Variant SKU '{cleaned_sku}' (first seen on row {first_row}).",
                        cleaned_sku,
                        cleaned_sku,
                    )
                else:
                    seen_skus[cleaned_sku] = idx

            row["Variant SKU"] = cleaned_sku

            # 4. Option1 Name / Value consistency & duplicate variant option check
            if opt1_name:
                std_opt_name = opt1_name.title()
                if std_opt_name != row.get("Option1 Name", ""):
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        cleaned_sku,
                        "Option1 Name",
                        "AUTO_FIXED",
                        "OPTION_NAME_NORMALIZED",
                        "Standardized Option1 Name casing/whitespace.",
                        row.get("Option1 Name", ""),
                        std_opt_name,
                    )
                row["Option1 Name"] = std_opt_name

            if not opt1_val:
                self._record_issue(
                    issues,
                    idx,
                    normalized_handle,
                    cleaned_sku,
                    "Option1 Value",
                    "CRITICAL",
                    "MISSING_OPTION_VALUE",
                    "Option1 Value is empty; Shopify/WooCommerce imports fail when variant option is blank.",
                    row.get("Option1 Value", ""),
                    "",
                )
            else:
                row["Option1 Value"] = opt1_val
                if normalized_handle:
                    opt_Set = handle_options.setdefault(normalized_handle, set())
                    opt_pair = (row.get("Option1 Name", "").lower(), opt1_val.lower())
                    if opt_pair in opt_Set:
                        self._record_issue(
                            issues,
                            idx,
                            normalized_handle,
                            cleaned_sku,
                            "Option1 Value",
                            "CRITICAL",
                            "DUPLICATE_VARIANT_OPTION",
                            f"Duplicate option combination '{opt1_val}' under handle '{normalized_handle}'.",
                            opt1_val,
                            opt1_val,
                        )
                    else:
                        opt_Set.add(opt_pair)

            # 5. Price & Compare-At-Price validation
            parsed_price = self._parse_price(price_raw)
            if parsed_price is None or parsed_price <= 0:
                self._record_issue(
                    issues,
                    idx,
                    normalized_handle,
                    cleaned_sku,
                    "Variant Price",
                    "CRITICAL",
                    "INVALID_OR_NON_POSITIVE_PRICE",
                    "Variant Price is missing, non-numeric, or <= 0. Business prices are never guessed.",
                    price_raw,
                    price_raw,
                )
            else:
                formatted_price = f"{parsed_price:.2f}"
                if formatted_price != price_raw:
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        cleaned_sku,
                        "Variant Price",
                        "AUTO_FIXED",
                        "PRICE_NUMBER_FORMATTED",
                        "Removed currency symbols/commas and formatted to 2 decimal places.",
                        price_raw,
                        formatted_price,
                    )
                row["Variant Price"] = formatted_price

            if compare_raw:
                parsed_compare = self._parse_price(compare_raw)
                if parsed_compare is None or parsed_compare <= 0:
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        cleaned_sku,
                        "Variant Compare At Price",
                        "WARNING",
                        "INVALID_COMPARE_AT_PRICE",
                        "Compare At Price is non-numeric or <= 0.",
                        compare_raw,
                        compare_raw,
                    )
                elif parsed_price is not None and parsed_compare < parsed_price:
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        cleaned_sku,
                        "Variant Compare At Price",
                        "WARNING",
                        "COMPARE_AT_LOWER_THAN_PRICE",
                        f"Compare At Price ({parsed_compare:.2f}) is lower than Variant Price ({parsed_price:.2f}).",
                        compare_raw,
                        f"{parsed_compare:.2f}",
                    )
                else:
                    row["Variant Compare At Price"] = f"{parsed_compare:.2f}"

            # 6. Status normalization
            if status_raw:
                norm_status = status_raw.lower()
                if norm_status not in {"active", "draft", "archived"}:
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        cleaned_sku,
                        "Status",
                        "WARNING",
                        "UNRECOGNIZED_STATUS",
                        "Status is not one of active, draft, archived.",
                        status_raw,
                        norm_status,
                    )
                elif norm_status != row.get("Status", ""):
                    self._record_issue(
                        issues,
                        idx,
                        normalized_handle,
                        cleaned_sku,
                        "Status",
                        "AUTO_FIXED",
                        "STATUS_CASED_LOWER",
                        "Normalized Status value to lowercase.",
                        row.get("Status", ""),
                        norm_status,
                    )
                row["Status"] = norm_status

            # 7. Vendor normalization
            if vendor != row.get("Vendor", ""):
                row["Vendor"] = vendor

            # 8. PII leak scan in description / Body (HTML)
            if body_html and (EMAIL_RE.search(body_html) or PHONE_RE.search(body_html)):
                redacted_body = EMAIL_RE.sub("[REDACTED_EMAIL]", body_html)
                redacted_body = PHONE_RE.sub("[REDACTED_PHONE]", redacted_body)
                self._record_issue(
                    issues,
                    idx,
                    normalized_handle,
                    cleaned_sku,
                    "Body (HTML)",
                    "WARNING",
                    "PII_DETECTED_IN_DESCRIPTION",
                    "Potential email or phone number detected in product description; flagged/redacted per privacy rule.",
                    "[REDACTED_PII_IN_ORIGINAL]",
                    redacted_body,
                )
                row["Body (HTML)"] = redacted_body

            cleaned_rows.append(row)

        summary = self._build_summary(source_name, rows, cleaned_rows, issues)
        return cleaned_rows, issues, summary

    def process_files(
        self,
        input_csv: str | Path,
        output_cleaned_csv: str | Path,
        output_issue_log_csv: str | Path,
        output_report_md: str | Path,
    ) -> AuditSummary:
        in_path = Path(input_csv)
        with in_path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)

        cleaned_rows, issues, summary = self.audit_and_clean_rows(rows, source_name=in_path.name)

        out_clean = Path(output_cleaned_csv)
        out_clean.parent.mkdir(parents=True, exist_ok=True)
        with out_clean.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)

        out_issues = Path(output_issue_log_csv)
        out_issues.parent.mkdir(parents=True, exist_ok=True)
        issue_fields = [
            "row_number",
            "handle",
            "sku",
            "field_name",
            "severity",
            "issue_code",
            "description",
            "original_value",
            "remediated_value",
        ]
        with out_issues.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=issue_fields)
            writer.writeheader()
            for issue in issues:
                writer.writerow(asdict(issue))

        out_md = Path(output_report_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(self.render_markdown_report(summary, issues), encoding="utf-8")
        return summary

    @staticmethod
    def render_markdown_report(summary: AuditSummary, issues: list[CatalogueIssue]) -> str:
        status_label = (
            "READY FOR IMPORT"
            if summary.passed_ready_for_import
            else "REQUIRES CLIENT DECISION ON CRITICAL ROWS BEFORE IMPORT"
        )
        lines = [
            f"# Catalogue QA & Reconciliation Report — `{summary.input_file}`",
            "",
            f"**Import Gate Status:** `{status_label}`",
            "",
            "## 1. Before / After Reconciliation Metrics",
            "",
            "| Metric | Count | Notes |",
            "|---|---:|---|",
            f"| Total Input Variant Rows | {summary.total_rows_read} | Scoped batch cap: <=200 rows |",
            f"| Total Output Variant Rows | {summary.total_rows_output} | 100% row reconciliation preserved |",
            f"| Unique Product Handles | {summary.unique_handles} | Normalized slug format |",
            f"| Unique Validated SKUs | {summary.unique_skus} | Post leading-zero restoration |",
            f"| Auto-Fixed Formatting Issues | {summary.auto_fixed_count} | Deterministic rule fixes applied |",
            f"| Warnings (Review Recommended) | {summary.warning_count} | Compare-at-price or PII flags |",
            f"| Critical Unresolved Issues | {summary.critical_unresolved_count} | Missing/duplicate SKUs or invalid prices (never guessed) |",
            f"| PII Leakage Flags | {summary.pii_flags_count} | Emails/phones redacted in Body HTML |",
            "",
            "## 2. Breakdown by Issue Code",
            "",
            "| Issue Code | Occurrences |",
            "|---|---:|",
        ]
        for code, count in sorted(summary.issues_by_code.items()):
            lines.append(f"| `{code}` | {count} |")

        criticals = [i for i in issues if i.severity == "CRITICAL"]
        lines.extend(
            [
                "",
                "## 3. Critical Unresolved Rows (Requires Client Confirmation)",
                "",
                "> Per operating policy, the QA engine **never guesses business prices, missing SKUs, or missing variant options**.",
                "",
                "| Row | Handle | SKU | Field | Issue Code | Detail |",
                "|---:|---|---|---|---|---|",
            ]
        )
        for item in criticals[:25]:
            lines.append(
                f"| {item.row_number} | `{item.handle}` | `{item.sku}` | `{item.field_name}` | `{item.issue_code}` | {item.description} |"
            )
        if not criticals:
            lines.append("| - | - | - | - | `NONE` | All rows passed critical validation checks. |")

        return "\n".join(lines) + "\n"

    def _build_summary(
        self,
        source_name: str,
        raw_rows: list[dict[str, Any]],
        cleaned_rows: list[dict[str, str]],
        issues: list[CatalogueIssue],
    ) -> AuditSummary:
        code_counts: dict[str, int] = {}
        auto_fixed = 0
        warnings = 0
        criticals = 0
        pii_flags = 0

        for iss in issues:
            code_counts[iss.issue_code] = code_counts.get(iss.issue_code, 0) + 1
            if iss.severity == "AUTO_FIXED":
                auto_fixed += 1
            elif iss.severity == "WARNING":
                warnings += 1
            elif iss.severity == "CRITICAL":
                criticals += 1
            if iss.issue_code == "PII_DETECTED_IN_DESCRIPTION":
                pii_flags += 1

        handles = {r.get("Handle", "") for r in cleaned_rows if r.get("Handle", "")}
        skus = {r.get("Variant SKU", "") for r in cleaned_rows if r.get("Variant SKU", "")}

        return AuditSummary(
            input_file=source_name,
            total_rows_read=len(raw_rows),
            total_rows_output=len(cleaned_rows),
            unique_handles=len(handles),
            unique_skus=len(skus),
            auto_fixed_count=auto_fixed,
            warning_count=warnings,
            critical_unresolved_count=criticals,
            issues_by_code=code_counts,
            pii_flags_count=pii_flags,
            passed_ready_for_import=(criticals == 0 and len(raw_rows) == len(cleaned_rows)),
        )

    @staticmethod
    def _record_issue(
        issues: list[CatalogueIssue],
        row_number: int,
        handle: str,
        sku: str,
        field_name: str,
        severity: str,
        issue_code: str,
        description: str,
        original_value: str,
        remediated_value: str,
    ) -> None:
        issues.append(
            CatalogueIssue(
                row_number=row_number,
                handle=handle,
                sku=sku,
                field_name=field_name,
                severity=severity,
                issue_code=issue_code,
                description=description,
                original_value=original_value,
                remediated_value=remediated_value,
            )
        )

    @staticmethod
    def _clean_whitespace(val: str) -> str:
        return re.sub(r"\s+", " ", val.strip())

    @staticmethod
    def _normalize_handle(val: str) -> str:
        slug = val.strip().lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        return slug.strip("-")

    @staticmethod
    def _parse_price(val: str) -> float | None:
        if not val:
            return None
        cleaned = re.sub(r"[$€£,\s]", "", val)
        try:
            return float(cleaned)
        except ValueError:
            return None
