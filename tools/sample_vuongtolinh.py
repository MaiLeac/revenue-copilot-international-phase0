import json
from pathlib import Path

src = Path.home() / "AppData" / "Local" / "Programs" / "antigravity" / "data" / "scraped_telegram" / "khoahoctaichinh_Vuongtolinh.json"
data = json.loads(src.read_text(encoding="utf-8"))

lines = [f"TOTAL MESSAGES: {len(data)}\n" + "="*50]
for i in [0, 1, 2, 5, 10, 20, 50, 100, 150, 200, 250, 300]:
    if i < len(data):
        m = data[i]
        lines.append(f"\n--- [INDEX {i} | ID: {m.get('post_id')} | DATE: {m.get('datetime')} | VIEWS: {m.get('views')}] ---")
        lines.append(m.get("text", "")[:600])

out = Path("C:/Users/ACER/Documents/Codex/revenue-copilot-international-phase0/data/sample_vuongtolinh.txt")
out.write_text("\n".join(lines), encoding="utf-8")
print("Written sample to data/sample_vuongtolinh.txt")
