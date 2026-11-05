"""Refresh public reference prices in WINK's local private database and report to Telegram."""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.telegram_notify import send_telegram_alert
from tools.wink_private_model import build_state, save_prices

ICT = timezone(timedelta(hours=7))
log = logging.getLogger("family_assets_prices")


def get_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "MoneyHQ-AssetPrices/1.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.load(response)


def fetch_knp() -> tuple[float, float, str]:
    """Accept only a row explicitly identifying KNP's 2024 silver bar."""
    from bs4 import BeautifulSoup

    req = urllib.request.Request("https://kimnganphuc.vn/gia-vang", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        soup = BeautifulSoup(response.read(), "html.parser")
    for row in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"], recursive=False)]
        if not cells or "2024" not in cells[0] or "bạc" not in cells[0].lower():
            continue
        if not any(part in cells[0].lower() for part in ("1kilo", "1 kilo", "1kg")):
            continue
        prices: list[float] = []
        for cell in cells[1:]:
            match = re.fullmatch(r"\s*(\d{2,3}(?:[.,]\d{3})+)\s*", cell)
            if match:
                prices.append(float(match.group(1).replace(".", "").replace(",", "")) * 1000)
        if len(prices) >= 2 and all(20_000_000 <= p <= 200_000_000 for p in prices[:2]):
            return prices[0], prices[1], "KNP bạc thỏi 2024"
    raise ValueError("Không xác minh được đúng dòng bạc KNP 2024 và đơn vị giá")


def fetch_sol() -> tuple[float, str]:
    data = get_json("https://api.coinbase.com/v2/prices/SOL-USD/spot")["data"]
    if data.get("base") != "SOL" or data.get("currency") != "USD":
        raise ValueError("SOL/USD sai mã")
    price = float(data["amount"])
    if not 1 <= price <= 2000:
        raise ValueError("SOL/USD ngoài khoảng kiểm tra")
    return price, "Coinbase SOL/USD"


def fetch_psol() -> tuple[float, str, str]:
    data = get_json("https://api.coingecko.com/api/v3/simple/price?ids=phantom-staked-sol&vs_currencies=usd&include_last_updated_at=true")
    item = data["phantom-staked-sol"]
    price = float(item["usd"])
    source_at = datetime.fromtimestamp(int(item["last_updated_at"]), timezone.utc)
    if not 1 <= price <= 2000 or datetime.now(timezone.utc) - source_at > timedelta(days=2):
        raise ValueError("PSOL thiếu giá mới đáng tin")
    return price, source_at.astimezone(ICT).strftime("%d/%m/%Y %H:%M"), "CoinGecko phantom-staked-sol"


def fetch_usd_vnd() -> tuple[float, str, str]:
    data = get_json("https://open.er-api.com/v6/latest/USD")
    if data.get("result") != "success" or data.get("base_code") != "USD":
        raise ValueError("USD/VND sai nguồn hoặc mã")
    rate = float(data["rates"]["VND"])
    if not 20_000 <= rate <= 35_000:
        raise ValueError("USD/VND ngoài khoảng kiểm tra")
    source_at = datetime.strptime(data["time_last_update_utc"], "%a, %d %b %Y %H:%M:%S %z")
    return rate, source_at.astimezone(ICT).strftime("%d/%m/%Y %H:%M"), "open.er-api.com"


def collect_quotes() -> tuple[dict[str, tuple], dict[str, str]]:
    quotes, errors = {}, {}
    for code, fetch in (("KNP", fetch_knp), ("SOL", fetch_sol), ("FX", fetch_usd_vnd), ("PSOL", fetch_psol)):
        try:
            quotes[code] = fetch()
        except Exception as exc:
            errors[code] = str(exc)
            log.warning("%s source failed: %s", code, exc)
    return quotes, errors


def _mil(value: float | None) -> str:
    return "?" if value is None else f"{value / 1_000_000:+,.1f}".replace(",", " ")


def _value_mil(value: float | None) -> str:
    return _mil(value).lstrip("+")


def _usd(value: float | None) -> str:
    return "?" if value is None else f"{value:,.2f}".replace(",", " ")


def format_telegram_report(state: dict[str, Any], stamp: str, fresh_count: int) -> str:
    """Compact owner/asset accounting; all VND differences are estimates."""
    lines = [f"📊 WINK · {stamp} · {fresh_count}/4 nguồn giá mới"]
    assets = state.get("assets") or []
    for owner, label in (("Mai", "MAI"), ("Mẹ", "MẸ"), ("Việt", "BẦU (VIỆT)")):
        group = [a for a in assets if a.get("owner") == owner]
        if not group:
            continue
        lines.append(label)
        for a in group:
            qty = a.get("quantity")
            if a.get("price_code") == "FX":
                cost = a.get("cost_usd")
                diff = a.get("change_usd")
                lines.append(f"• Exness: equity {_usd(qty)} USD / nạp {_usd(cost)} USD; chênh {_usd(diff)} USD (~{_mil(a.get('estimated_change_vnd'))}tr). Nhập tay {a.get('quantity_asof') or '?'}.")
            else:
                short = "Bạc KNP" if a.get("price_code") == "KNP" else a.get("name", "Tài sản")
                unit = "kg" if a.get("price_code") == "KNP" else "PSOL"
                qty_text = f"{qty:g}" if isinstance(qty, (int, float)) else str(qty)
                lines.append(f"• {short} {qty_text} {unit}: vốn {_value_mil(a.get('cost_comparison_vnd'))}tr → {_value_mil(a.get('value_vnd'))}tr ({_mil(a.get('estimated_change_vnd'))}tr).")
        total = state.get("owner_totals_vnd", {}).get(owner)
        lines.append(f"Tổng {label}: {_value_mil(total)}tr tạm tính.")
    lines.append("Bạc KNP: ngày giá nguồn chưa xác minh. Exness là equity cũ, không phải lãi đã chốt; VND quy đổi theo FX mới.")
    if state.get("price_errors"):
        lines.append("Lỗi nguồn: " + ", ".join(state["price_errors"]))
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Fetch public prices only; no local write or Telegram")
    parser.add_argument("--telegram-prices-only", action="store_true", help="Compatibility alias for local WINK update")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.dry_run:
        quotes, errors = collect_quotes()
        print(json.dumps({"quotes": quotes, "errors": errors}, ensure_ascii=False))
        return 0 if quotes else 1
    stamp = datetime.now(ICT).strftime("%d/%m %H:%M")
    quotes, errors = collect_quotes()
    try:
        save_prices(quotes, errors)
        message = format_telegram_report(build_state(), stamp, len(quotes))
    except Exception as exc:
        log.error("Private dashboard update failed: %s", exc.__class__.__name__)
        message = f"⚠️ WINK {stamp}: chưa lưu được giá ({exc.__class__.__name__})."
        result = send_telegram_alert(message)
        return 1 if result.get("ok") and not result.get("dry_run") else 2
    result = send_telegram_alert(message)
    if not result.get("ok") or result.get("dry_run"):
        log.error("Telegram delivery not verified")
        return 1
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
