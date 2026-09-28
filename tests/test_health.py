def test_health_ok(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_unknown_api_route_returns_json_404(client):
    r = client.get("/api/nope")
    assert r.status_code == 404 and "error" in r.get_json()


def test_wrong_method_returns_405_json(client):
    assert client.post("/api/health").status_code == 405


def test_index_page_served(client):
    assert b"BUG//HUNT" in client.get("/").data
