import urllib.request
import json

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:25];
(
  node["shop"="beauty"](30.15,-92.15,30.30,-91.90);
  node["amenity"="doctors"](30.15,-92.15,30.30,-91.90);
  node["healthcare"](30.15,-92.15,30.30,-91.90);
);
out body;
>;
out skel qt;
"""

req = urllib.request.Request(
    overpass_url,
    data=overpass_query.encode('utf-8'),
    headers={'User-Agent': 'MedspaScraper/1.0'}
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        elements = data.get('elements', [])
        print(f"Found {len(elements)} elements in Lafayette area.")
        count = 0
        for el in elements:
            tags = el.get('tags', {})
            if tags:
                name = tags.get('name', 'Unknown')
                addr = f"{tags.get('addr:housenumber', '')} {tags.get('addr:street', '')}, {tags.get('addr:city', 'Lafayette')}".strip()
                phone = tags.get('phone', tags.get('contact:phone', 'N/A'))
                website = tags.get('website', tags.get('contact:website', 'N/A'))
                print(f"Name: {name} | Phone: {phone} | Website: {website} | Address: {addr}")
                count += 1
                if count >= 15:
                    break
except Exception as e:
    print(f"Error: {e}")
