import urllib.request
import urllib.parse
import json
import time

queries = [
    "medspa Abbeville LA",
    "medical spa Abbeville Louisiana",
    "skin care Abbeville LA",
    "spa Abbeville LA"
]

for q in queries:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&addressdetails=1&limit=5"
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.openstreetmap.org/'
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"\nQuery: {q} -> Found {len(data)} results")
            for item in data:
                print(f"  - Name: {item.get('display_name')}")
                print(f"    Type: {item.get('type')} | Class: {item.get('class')} | Lat/Lon: {item.get('lat')}, {item.get('lon')}")
    except Exception as e:
        print(f"Query {q} failed: {e}")
    time.sleep(1)
