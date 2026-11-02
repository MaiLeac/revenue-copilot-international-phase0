import urllib.request
import re
from pathlib import Path

out_lines = []
for url in ['https://t.me/nhatlongtc', 'https://t.me/s/nhatlongtc']:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            title = re.findall(r'<title>(.*?)</title>', html)
            desc = re.findall(r'<meta property="og:description" content="(.*?)"', html)
            out_lines.append(f"URL: {url}")
            out_lines.append(f"Title: {title}")
            out_lines.append(f"Desc: {desc}")
            out_lines.append(f"HTML snippet: {html[:2500]}")
            out_lines.append("="*50)
    except Exception as e:
        out_lines.append(f"Error {url}: {e}")

Path("data/nhatlong_check.txt").write_text("\n".join(out_lines), encoding="utf-8")
print("Written to data/nhatlong_check.txt")
