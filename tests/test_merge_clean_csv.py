import csv
import json
from pathlib import Path

import pytest

from tools.merge_clean_csv import merge


def test_reconcile_and_preserve_conflicts(tmp_path: Path):
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    first.write_text("Name,SKU,Price\nLamp,001,10\nLamp,001,10\n", encoding="utf-8")
    second.write_text(" Name ,SKU,Price,Color\n Lamp ,001,10,\nLamp,001,11,Blue\n", encoding="utf-8")
    output = tmp_path / "master.csv"
    report = merge([first, second], output)
    assert (report["input_rows"], report["output_rows"], report["exact_duplicate_rows_removed"]) == (4, 2, 2)
    with output.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert rows == [
        {"Name": "Lamp", "SKU": "001", "Price": "10", "Color": ""},
        {"Name": "Lamp", "SKU": "001", "Price": "11", "Color": "Blue"},
    ]
    assert len(json.loads(output.with_suffix(".audit.json").read_text(encoding="utf-8"))["duplicate_provenance"]) == 2


def test_rejects_malformed_and_in_place_output(tmp_path: Path):
    source = tmp_path / "source.csv"
    source.write_text("A\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Output must differ"):
        merge([source], source)
    with pytest.raises(ValueError, match="Extra fields"):
        merge([source], tmp_path / "out.csv")


def test_rejects_formula_like_cells(tmp_path: Path):
    source = tmp_path / "source.csv"
    source.write_text("Name,Notes\nTest,=HYPERLINK(\"\"x\"\")\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Spreadsheet formula-like"):
        merge([source], tmp_path / "out.csv")
