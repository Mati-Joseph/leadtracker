"""Fetch businesses from OpenStreetMap via the free Overpass API (no key, no billing)."""
import re
import requests

URL = "https://overpass-api.de/api/interpreter"
UA = "LeadTrackerBot/0.1 (contact research)"
TAG_RE = re.compile(r"^[a-z_:]+=[a-z_:]+$")


def build_query(area, tag="amenity=driving_school"):
    """Build an Overpass QL query. `area` is 'Kenya' (whole country) or an admin-area name."""
    if not TAG_RE.match(tag):
        raise ValueError("invalid tag, expected key=value like amenity=driving_school")
    key, value = tag.split("=", 1)
    area = re.sub(r'["\\]', "", area or "").strip()
    if area.lower() in ("", "kenya", "ke"):
        pick = 'area["ISO3166-1"="KE"][admin_level=2]->.a;'
    else:
        pick = f'area["name"="{area}"]["boundary"="administrative"]->.a;'
    return f'[out:json][timeout:60];{pick}nwr["{key}"="{value}"](area.a);out center tags;'


def _address(t):
    parts = [t.get("addr:housenumber"), t.get("addr:street"),
             t.get("addr:suburb"), t.get("addr:city") or t.get("addr:town")]
    return ", ".join(p for p in parts if p)


def parse_elements(elements):
    places = []
    for e in elements:
        t = e.get("tags", {})
        if not t.get("name"):
            continue
        places.append({
            "place_id": f"osm:{e['type']}/{e['id']}",
            "name": t["name"],
            "address": _address(t),
            "phone": t.get("phone") or t.get("contact:phone", ""),
            "website": t.get("website") or t.get("contact:website", ""),
            "email": t.get("email") or t.get("contact:email", ""),
        })
    return places


def search_osm(area, tag="amenity=driving_school"):
    r = requests.post(URL, data={"data": build_query(area, tag)},
                      headers={"User-Agent": UA}, timeout=90)
    if r.status_code != 200:
        raise RuntimeError(f"Overpass HTTP {r.status_code}: {r.text[:200]}")
    try:
        data = r.json()
    except ValueError:
        raise RuntimeError(f"Overpass returned non-JSON: {r.text[:200]}")
    return parse_elements(data.get("elements", []))
