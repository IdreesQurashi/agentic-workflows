import urllib.request
import json

# Overpass API query for Abbeville and surrounding Vermilion Parish
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:30];
(
  node["shop"="beauty"](29.7,-92.4,30.2,-91.8);
  node["amenity"="doctors"](29.7,-92.4,30.2,-91.8);
  node["healthcare"](29.7,-92.4,30.2,-91.8);
  node["leisure"="fitness_centre"](29.7,-92.4,30.2,-91.8);
  way["shop"="beauty"](29.7,-92.4,30.2,-91.8);
  way["amenity"="doctors"](29.7,-92.4,30.2,-91.8);
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
        print(f"Found {len(elements)} elements in wider Abbeville/Vermilion region.")
        for el in elements:
            tags = el.get('tags', {})
            if tags:
                name = tags.get('name', 'Unknown')
                addr = f"{tags.get('addr:housenumber', '')} {tags.get('addr:street', '')}, {tags.get('addr:city', 'Abbeville')}".strip()
                phone = tags.get('phone', tags.get('contact:phone', 'N/A'))
                website = tags.get('website', tags.get('contact:website', 'N/A'))
                category = tags.get('shop', tags.get('amenity', tags.get('healthcare', 'beauty')))
                print(f"Title: {name}")
                print(f"Category: {category}")
                print(f"Address: {addr}")
                print(f"Phone: {phone}")
                print(f"Website: {website}")
                print("-" * 40)
except Exception as e:
    print(f"Error: {e}")
