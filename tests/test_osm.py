import pytest

from app.collector_osm import build_query, parse_elements

ELEMENTS = [
    {
        "type": "node",
        "id": 1,
        "tags": {
            "name": "ABC Driving School",
            "addr:street": "Moi Ave",
            "addr:city": "Nairobi",
            "phone": "+254700",
            "website": "https://abc.ke",
            "email": "info@abc.ke",
        },
    },
    {
        "type": "way",
        "id": 2,
        "tags": {"amenity": "driving_school"},
    },  # no name -> skipped
]


def test_parse_elements():
    out = parse_elements(ELEMENTS)
    assert len(out) == 1
    assert out[0]["place_id"] == "osm:node/1"
    assert out[0]["address"] == "Moi Ave, Nairobi"
    assert out[0]["email"] == "info@abc.ke"


def test_build_query():
    assert 'ISO3166-1"="KE' in build_query("Kenya")
    q = build_query('Nai"robi')
    assert 'name"="Nairobi"' in q and 'Nai"' not in q
    with pytest.raises(ValueError):
        build_query("Kenya", 'amenity=x"];drop')


def test_collect_route_uses_osm_and_saves_email(app, client, monkeypatch):
    monkeypatch.setattr("app.routes.search_osm", lambda q: parse_elements(ELEMENTS))
    r = client.post("/api/collect", json={"query": "Nairobi"})
    assert r.json == {"fetched": 1, "new_branches": 1}
    assert client.get("/api/businesses").json[0]["email"] == "info@abc.ke"


def test_collect_route_reports_overpass_error(app, client, monkeypatch):
    def boom(q):
        raise RuntimeError("Overpass returned non-JSON: <html>busy")

    monkeypatch.setattr("app.routes.search_osm", boom)
    r = client.post("/api/collect", json={"query": "Kenya"})
    assert r.status_code == 502 and "non-JSON" in r.json["error"]


def test_search_osm_retries_when_busy(monkeypatch):
    from app.collector_osm import search_osm

    class R:
        def __init__(self, code, js=None):
            self.status_code, self._js, self.text = code, js, "busy"

        def json(self):
            return self._js

    seq = [R(502), R(200, {"elements": ELEMENTS})]
    monkeypatch.setattr("app.collector_osm.requests.post", lambda *a, **k: seq.pop(0))
    monkeypatch.setattr("app.collector_osm.time.sleep", lambda s: None)
    assert len(search_osm("Kenya")) == 1
    assert seq == []
