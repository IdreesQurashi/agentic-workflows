import urllib.request
import urllib.parse
import json
import re

# Fetch Yelp search for Medical Spas in Abbeville, LA
url = "https://www.yelp.com/search?find_desc=Medical+Spas&find_loc=Abbeville%2C+LA"
req = urllib.request.Request(
    url,
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
)

try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        # Yelp JSON state or business names in JSON-LD or meta tags
        # Let's search for json-ld or business names
        matches = re.findall(r'"name":"([^"]+)"', html)
        print("Found names in Yelp HTML:", set(matches[:30]))

        # Let's find JSON-LD blocks
        json_lds = re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
        for jld in json_lds:
            try:
                data = json.loads(jld)
                print("JSON-LD found:", type(data))
            except:
                pass
except Exception as e:
    print(f"Error fetching Yelp: {e}")
