import urllib.request
from bs4 import BeautifulSoup
from pathlib import Path

results = []
for mid in [2, 3, 4, 5, 10, 20, 50, 100, 200, 300, 400, 500]:
    url = f"https://t.me/nhatlongtc/{mid}?embed=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        txt = soup.find('div', class_='tgme_widget_message_text')
        time_tag = soup.find('time')
        if txt:
            results.append({
                "id": mid,
                "time": time_tag.get('datetime', '') if time_tag else '',
                "text": txt.get_text('\n', strip=True)
            })
    except Exception as e:
        pass

out_file = Path("C:/Users/ACER/Documents/Codex/revenue-copilot-international-phase0/data/sample_nhatlong.json")
out_file.parent.mkdir(parents=True, exist_ok=True)
import json
out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"Scraped {len(results)} sample posts from nhatlongtc")
