import urllib.request
import json

# Overpass API query for Abbeville, LA
# Bounding box around Abbeville approximately: 29.93 to 30.02, -92.18 to -92.08
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:25];
(
  node["amenity"="doctors"](29.90,-92.25,30.05,-92.05);
  node["amenity"="clinic"](29.90,-92.25,30.05,-92.05);
  node["healthcare"](29.90,-92.25,30.05,-92.05);
  node["shop"="beauty"](29.90,-92.25,30.05,-92.05);
  node["shop"="massage"](29.90,-92.25,30.05,-92.05);
  way["amenity"="doctors"](29.90,-92.25,30.05,-92.05);
  way["amenity"="clinic"](29.90,-92.25,30.05,-92.05);
  way["healthcare"](29.90,-92.25,30.05,-92.05);
  way["shop"="beauty"](29.90,-92.25,30.05,-92.05);
  way["shop"="massage"](29.90,-92.25,30.05,-92.05);
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
        print(f"Found {len(elements)} elements.")
        for el in elements:
            tags = el.get('tags', {})
            if tags:
                name = tags.get('name', 'Unknown')
                addr = f"{tags.get('addr:housenumber', '')} {tags.get('addr:street', '')}, {tags.get('addr:city', 'Abbeville')}".strip()
                phone = tags.get('phone', tags.get('contact:phone', 'N/A'))
                website = tags.get('website', tags.get('contact:website', 'N/A'))
                amenity = tags.get('amenity', tags.get('shop', tags.get('healthcare', '')))
                print(f"Name: {name} | Type: {amenity} | Address: {addr} | Phone: {phone} | Website: {website}")
except Exception as e:
    print(f"Error: {e}")
