import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

html = urllib.request.urlopen('https://www.getlayers.ai/').read().decode('utf-8', 'ignore')
css_links = re.findall(r'href="([^"]+\.css[^"]*)"', html)
print("CSS links found:", css_links)

# Also check static chunks for CSS modules or tailwind
for link in css_links:
    full_url = "https://www.getlayers.ai" + link if link.startswith("/") else link
    css_text = urllib.request.urlopen(full_url).read().decode('utf-8', 'ignore')
    print(f"Downloaded {link}: length {len(css_text)}")
    # Print root tokens
    root_vars = re.findall(r'--[a-zA-Z0-9_-]+:[^;]+;', css_text)
    print(f"Found {len(root_vars)} CSS vars:", root_vars[:15])
    with open("getlayers_styles.css", "w", encoding="utf-8") as f:
        f.write(css_text)
    print("Saved to getlayers_styles.css")
