import urllib.request
import re

url = "https://www.getlayers.ai/layer/glass-wave"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')

print("Page length:", len(html))
# Find prompt or copyable code
texts = re.findall(r'<p[^>]*>(.*?)</p>', html)
for t in texts[:15]:
    if any(k in t.lower() for k in ["prompt", "glass", "wave", "scene", "template", "layer"]):
        print("P:", t)

# Find code blocks or pre tags
pres = re.findall(r'<pre[^>]*>(.*?)</pre>', html, re.DOTALL)
print("Pre tags:", len(pres))
