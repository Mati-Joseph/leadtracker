"""Fetch places from Google Places API (New) Text Search."""
import requests

URL = "https://places.googleapis.com/v1/places:searchText"
FIELDS = ",".join([
    "places.id", "places.displayName", "places.formattedAddress",
    "places.nationalPhoneNumber", "places.websiteUri", "nextPageToken",
])


def search_places(query, api_key, max_pages=3):
    """Return a list of normalized place dicts for a text query."""
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set")
    headers = {"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": FIELDS}
    results, token = [], None
    for _ in range(max_pages):
        body = {"textQuery": query, "pageSize": 20}
        if token:
            body["pageToken"] = token
        r = requests.post(URL, json=body, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        for p in data.get("places", []):
            results.append({
                "place_id": p["id"],
                "name": (p.get("displayName") or {}).get("text", ""),
                "address": p.get("formattedAddress", ""),
                "phone": p.get("nationalPhoneNumber", ""),
                "website": p.get("websiteUri", ""),
            })
        token = data.get("nextPageToken")
        if not token:
            break
    return results
