"""Topic extraction and text categorization for Khoa Học Tài Chính - Vương Tố Linh.
"""

import json
from pathlib import Path

src = Path(__file__).resolve().parents[1] / "data" / "scraped_telegram" / "khoahoctaichinh_Vuongtolinh.json"
posts = json.loads(src.read_text(encoding="utf-8"))

out_lines = [f"Total posts: {len(posts)}"]

categories = {
    "Vĩ mô, Lãi suất, Cung tiền & Tín dụng": ["lãi suất", "cung tiền", "ngân hàng", "tín dụng", "bơm tiền", "hút tiền", "lạm phát", "fed", "sbv", "tỷ giá", "dxy"],
    "Bất động sản & Pháp lý Vốn": ["bđs", "bất động sản", "nhà ở", "chung cư", "đất", "pháp lý", "góp vốn", "hình thành trong tương lai"],
    "Chứng khoán & Cấu trúc Doanh nghiệp": ["cổ phiếu", "chứng khoán", "lái", "doanh nghiệp", "niêm yết", "trái phiếu", "thế chấp", "chia cổ tức"],
    "Crypto & Tài chính Quốc tế": ["crypto", "bitcoin", "binance", "cz", "usdt", "rửa tiền", "mỹ", "trung quốc"],
    "Tâm lý học hành vi, Bẫy thị trường & Triết lý": ["bẫy", "lợn rừng", "tham lam", "ngu ngốc", "con ruột", "con ghẻ", "lợi ích", "thị trường"],
}

categorized = {k: [] for k in categories}
for p in posts:
    txt = p.get("text", "").lower()
    matched = False
    for cat, kws in categories.items():
        if any(kw in txt for kw in kws):
            categorized[cat].append(p)
            matched = True
    if not matched:
        categorized.setdefault("Khác", []).append(p)

for cat, plist in categorized.items():
    out_lines.append(f"\n=== {cat}: {len(plist)} bài ===")
    for sample in plist[:5]:
        snippet = sample.get("text", "").replace("\n", " ")[:200]
        out_lines.append(f"  - [{sample.get('datetime', '')[:10]}] {snippet}...")

out_file = Path("C:/Users/ACER/Documents/Codex/revenue-copilot-international-phase0/data/vuongtolinh_summary.txt")
out_file.write_text("\n".join(out_lines), encoding="utf-8")
print("Written analysis to data/vuongtolinh_summary.txt")
