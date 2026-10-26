from app.grouping import save_places


def seed(app):
    with app.app_context():
        save_places([
            {"place_id": "1", "name": "ABC West", "address": "a", "phone": "07", "website": "https://abc.ke"},
            {"place_id": "2", "name": "ABC Thika", "address": "b", "phone": "", "website": "https://abc.ke"},
            {"place_id": "3", "name": "Solo", "address": "c", "phone": "", "website": ""},
        ])


def test_min_branches_filter(app, client):
    seed(app)
    assert len(client.get("/api/businesses").json) == 2
    rows = client.get("/api/businesses?min_branches=2").json
    assert [r["branch_count"] for r in rows] == [2]


def test_status_update_and_validation(app, client):
    seed(app)
    bid = client.get("/api/businesses?min_branches=2").json[0]["id"]
    r = client.patch(f"/api/businesses/{bid}", json={"status": "contacted", "notes": "called"})
    assert r.json["status"] == "contacted"
    assert client.patch(f"/api/businesses/{bid}", json={"status": "nope"}).status_code == 400
    assert len(client.get("/api/businesses?status=contacted").json) == 1


def test_exports(app, client):
    seed(app)
    assert b"ABC West" in client.get("/api/export/csv").data or b"ABC" in client.get("/api/export/csv").data
    assert client.get("/api/export/xlsx").data[:2] == b"PK"
    assert client.get("/api/export/pdf").data[:4] == b"%PDF"
    assert client.get("/api/export/zip").status_code == 400


def test_collect_without_key(client):
    assert client.post("/api/collect", json={"query": "driving schools Nairobi"}).status_code == 400
