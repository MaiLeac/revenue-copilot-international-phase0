"""Local-only WINK asset model. Private holdings live outside the public repo."""
from __future__ import annotations

import csv
import json
import math
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = Path(os.environ.get("WINK_PRIVATE_DIR", str(REPO_ROOT.parent / "wink-private")))
HOLDINGS_FILE = PRIVATE_DIR / "holdings.json"
PRICES_FILE = PRIVATE_DIR / "prices.json"
DB_FILE = PRIVATE_DIR / "wink.db"
_WRITE_LOCK = threading.Lock()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid private data format: {path.name}")
    return data


def _connect() -> sqlite3.Connection:
    """Open the private SQLite database and import the initial local JSON once."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS assets (id TEXT PRIMARY KEY, data TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS quotes (code TEXT PRIMARY KEY, data TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS asset_edits (id INTEGER PRIMARY KEY, at TEXT NOT NULL, asset_id TEXT NOT NULL, old_data TEXT NOT NULL, new_data TEXT NOT NULL)")
    if not conn.execute("SELECT 1 FROM meta WHERE key='initialized'").fetchone():
        holdings, prices = _read_json(HOLDINGS_FILE), _read_json(PRICES_FILE)
        for asset in holdings.get("assets") or []:
            conn.execute("INSERT OR REPLACE INTO assets(id,data) VALUES (?,?)", (asset["id"], json.dumps(asset, ensure_ascii=False)))
        for code, quote in (prices.get("quotes") or {}).items():
            conn.execute("INSERT OR REPLACE INTO quotes(code,data) VALUES (?,?)", (code, json.dumps(quote, ensure_ascii=False)))
        for key in ("captured_at", "source", "themes", "theme_origin"):
            _meta_set(conn, key, holdings.get(key))
        _meta_set(conn, "prices_checked_at", prices.get("checked_at"))
        _meta_set(conn, "price_errors", prices.get("errors") or {})
        _meta_set(conn, "initialized", True)
    conn.commit()
    return conn


def _meta_set(conn: sqlite3.Connection, key: str, value: Any) -> None:
    conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)", (key, json.dumps(value, ensure_ascii=False)))


def _meta_get(conn: sqlite3.Connection, key: str) -> Any:
    row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return json.loads(row[0]) if row else None


def load_holdings() -> dict[str, Any]:
    with _connect() as conn:
        return {"assets": [json.loads(r[0]) for r in conn.execute("SELECT data FROM assets ORDER BY rowid")],
                **{key: _meta_get(conn, key) for key in ("captured_at", "source", "themes", "theme_origin")}}


def load_prices() -> dict[str, Any]:
    with _connect() as conn:
        return {"quotes": {r[0]: json.loads(r[1]) for r in conn.execute("SELECT code,data FROM quotes")},
                "checked_at": _meta_get(conn, "prices_checked_at"),
                "errors": _meta_get(conn, "price_errors") or {}}


def save_prices(quotes: dict[str, tuple], errors: dict[str, str]) -> None:
    """Persist only observed public quotes; a failed source retains its last good quote."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _WRITE_LOCK, _connect() as conn:
        for code, quote in quotes.items():
            if code == "KNP":
                buy, sell, source = quote
                data = {"value": buy, "sell": sell, "source": source, "checked_at": now,
                        "source_at": None, "quality": "source date unverified"}
            elif code in {"PSOL", "FX"}:
                value, source_at, source = quote
                data = {"value": value, "source": source, "checked_at": now,
                        "source_at": source_at, "quality": "source timestamp reported"}
            elif code == "SOL":
                value, source = quote
                data = {"value": value, "source": source, "checked_at": now,
                        "source_at": None, "quality": "spot response time only"}
            else:
                continue
            conn.execute("INSERT OR REPLACE INTO quotes(code,data) VALUES (?,?)", (code, json.dumps(data, ensure_ascii=False)))
        _meta_set(conn, "prices_checked_at", now)
        _meta_set(conn, "price_errors", errors)


def _money(value: Any) -> float | None:
    try:
        number = float(value)
        return number if math.isfinite(number) and number >= 0 else None
    except (ValueError, TypeError):
        return None


def cash_collected() -> dict[str, Any]:
    """Count only ledger entries with a proof reference and a collected status."""
    path = REPO_ROOT / "finance" / "CASH_LEDGER.csv"
    totals: dict[str, float] = {}
    count = 0
    if path.exists():
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                if row.get("status", "").strip().lower() not in {"collected", "received", "paid", "verified"}:
                    continue
                if not row.get("proof_reference_redacted", "").strip():
                    continue
                amount = _money(row.get("net_usable_cash"))
                if amount is None:
                    continue
                currency = row.get("currency", "").strip().upper()
                if not currency:
                    continue
                totals[currency] = totals.get(currency, 0) + amount
                count += 1
    return {"by_currency": totals, "verified_entries": count}


def build_state() -> dict[str, Any]:
    holdings = load_holdings()
    prices = load_prices()
    quote_map = prices.get("quotes") or {}
    fx = _money((quote_map.get("FX") or {}).get("value"))
    assets = []
    owner_totals: dict[str, float] = {}
    for asset in holdings.get("assets") or []:
        qty = _money(asset.get("quantity"))
        code = asset.get("price_code")
        quote = quote_map.get(code) or {}
        price = _money(quote.get("value"))
        value = None
        if qty is not None and price is not None:
            if code == "KNP":
                value = qty * price
            elif code in {"PSOL", "FX"} and fx is not None:
                value = qty * (price if code == "FX" else price * fx)
        cost = _money(asset.get("cost_vnd"))
        if cost is None and asset.get("cost_usd") is not None and fx is not None:
            usd_cost = _money(asset.get("cost_usd"))
            cost = usd_cost * fx if usd_cost is not None else None
        row = dict(asset)
        row.update({"value_vnd": round(value, 2) if value is not None else None,
                    "cost_comparison_vnd": round(cost, 2) if cost is not None else None,
                    "estimated_change_vnd": round(value - cost, 2) if value is not None and cost is not None else None,
                    "price_quality": quote.get("quality", "no verified quote"),
                    "price_checked_at": quote.get("checked_at"),
                    "source_at": quote.get("source_at")})
        if code == "FX" and qty is not None and asset.get("cost_usd") is not None:
            row["change_usd"] = round(qty - float(asset["cost_usd"]), 2)
        assets.append(row)
        if value is not None:
            owner = str(asset.get("owner"))
            owner_totals[owner] = owner_totals.get(owner, 0) + value
    return {
        "captured_at": holdings.get("captured_at"),
        "source": holdings.get("source"),
        "prices_checked_at": prices.get("checked_at"),
        "price_errors": prices.get("errors") or {},
        "assets": assets,
        "owner_totals_vnd": {k: round(v, 2) for k, v in owner_totals.items()},
        "family_total_vnd": round(sum(owner_totals.values()), 2),
        "cash": cash_collected(),
        "themes": holdings.get("themes") or [],
        "theme_origin": holdings.get("theme_origin"),
        "projects": [
            {"name": "Bản Thảo", "kind": "Sách số", "status": "Bản thảo; chưa có tiền thu được ghi nhận"},
            {"name": "CatalogueQA", "kind": "Công cụ B2B", "status": "Nguyên mẫu; chưa có tiền thu được ghi nhận"},
            {"name": "Wink Living", "kind": "Nền tảng", "status": "Cần xác minh kênh thu tiền"},
            {"name": "Loser Kingdom", "kind": "Ứng dụng", "status": "Chưa có khách trả tiền được ghi nhận"},
            {"name": "Little Loop Factory", "kind": "Công cụ video", "status": "Công cụ nội bộ; không tự tính là doanh thu"},
            {"name": "MT5", "kind": "Demo giao dịch", "status": "Không tính là tiền thu; backtest gần nhất âm 4,30%"},
        ],
    }


def update_asset(asset_id: str, quantity: Any, cost: Any, asof: str | None) -> dict[str, Any]:
    """Update one existing local holding, preserving an audit trail."""
    new_qty, new_cost = _money(quantity), _money(cost)
    if new_qty is None or new_cost is None or new_qty > 1_000_000 or new_cost > 100_000_000_000:
        raise ValueError("Số lượng hoặc vốn không hợp lệ")
    if asof:
        datetime.strptime(asof, "%Y-%m-%d")
    with _WRITE_LOCK:
        with _connect() as conn:
            row = conn.execute("SELECT data FROM assets WHERE id=?", (asset_id,)).fetchone()
            if row is None:
                raise ValueError("Tài sản không tồn tại")
            asset = json.loads(row[0])
            old = dict(asset)
            cost_key = "cost_usd" if asset.get("unit") == "USD equity" else "cost_vnd"
            asset["quantity"] = new_qty
            asset[cost_key] = new_cost
            asset["quantity_asof"] = asof
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            conn.execute("UPDATE assets SET data=? WHERE id=?", (json.dumps(asset, ensure_ascii=False), asset_id))
            conn.execute("INSERT INTO asset_edits(at,asset_id,old_data,new_data) VALUES (?,?,?,?)",
                         (now, asset_id, json.dumps(old, ensure_ascii=False), json.dumps(asset, ensure_ascii=False)))
            _meta_set(conn, "captured_at", now)
            return asset
