"""Merge CSV batches with an auditable, conservative exact-duplicate rule.

Standard library only. Inputs are never modified. Ambiguous rows and columns
remain intact for the customer to decide; the script does not guess business data.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def merge(inputs: list[Path], output: Path) -> dict:
    if not inputs:
        raise ValueError("At least one input CSV is required")
    output_display = str(output)
    output = output.resolve()
    if output in {path.resolve() for path in inputs}:
        raise ValueError("Output must differ from every input")

    columns: list[str] = []
    records: list[tuple[Path, int, dict[str, str]]] = []
    for path in inputs:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or None in reader.fieldnames:
                raise ValueError(f"Missing or malformed header: {path}")
            headers = [name.strip() for name in reader.fieldnames]
            if not all(headers) or len(headers) != len(set(headers)):
                raise ValueError(f"Empty or duplicate normalized header: {path}")
            for name in headers:
                if name not in columns:
                    columns.append(name)
            for number, raw in enumerate(reader, start=2):
                if None in raw:
                    raise ValueError(f"Extra fields in {path}:{number}; refusing data loss")
                row = {name: (raw[original] or "").strip() for original, name in zip(reader.fieldnames, headers)}
                if any(value.startswith(("=", "+", "-", "@")) for value in row.values()):
                    raise ValueError(f"Spreadsheet formula-like cell in {path}:{number}; review before export")
                records.append((path, number, row))

    kept: list[dict[str, str]] = []
    duplicates: list[dict] = []
    first_seen: dict[tuple[str, ...], tuple[Path, int]] = {}
    for path, number, row in records:
        full_row = {name: row.get(name, "") for name in columns}
        # Exact after edge-space trimming only. Case and internal spaces may matter.
        signature = tuple(full_row[name] for name in columns)
        if signature in first_seen:
            original_path, original_number = first_seen[signature]
            duplicates.append({"source": str(path), "source_row": number,
                               "duplicate_of": str(original_path), "duplicate_of_row": original_number})
        else:
            first_seen[signature] = (path, number)
            kept.append(full_row)

    if len(records) != len(kept) + len(duplicates):
        raise AssertionError("Row reconciliation failed")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(kept)
    report = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": [str(path) for path in inputs], "output": output_display,
        "input_rows": len(records), "output_rows": len(kept),
        "exact_duplicate_rows_removed": len(duplicates), "columns": columns,
        "duplicate_provenance": duplicates,
        "method": "Trim header and cell edge whitespace; merge columns by exact header; remove only exact full-row duplicates.",
        "requires_customer_decision": "Which columns are irrelevant, whether near-duplicates should merge, and how conflicting values should be resolved.",
    }
    output.with_suffix(".audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()
    print(json.dumps(merge(args.inputs, args.output), ensure_ascii=False))


if __name__ == "__main__":
    main()
