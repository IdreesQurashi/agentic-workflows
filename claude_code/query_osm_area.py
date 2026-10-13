import urllib.request
import json

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:15];
area[name="Abbeville"]->.searchArea;
(
  node["shop"="beauty"](area.searchArea);
  node["amenity"="doctors"](area.searchArea);
  node["healthcare"](area.searchArea);
);
out body;
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
        print(f"Found {len(elements)} elements in Abbeville area.")
        for el in elements:
            tags = el.get('tags', {})
            if tags:
                name = tags.get('name', 'Unknown')
                addr = f"{tags.get('addr:housenumber', '')} {tags.get('addr:street', '')}, {tags.get('addr:city', 'Abbeville')}".strip()
                phone = tags.get('phone', tags.get('contact:phone', 'N/A'))
                website = tags.get('website', tags.get('contact:website', 'N/A'))
                print(f"Title: {name} | Phone: {phone} | Website: {website} | Address: {addr}")
except Exception as e:
    print(f"Error: {e}")
