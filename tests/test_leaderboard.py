import pytest

from tests.conftest import finish_game


def test_empty_leaderboard(client):
    assert client.get("/api/leaderboard").get_json() == {"entries": []}


def test_cannot_submit_before_finishing(client):
    assert client.post("/api/leaderboard", json={"name": "Ishaan"}).status_code == 403


@pytest.mark.parametrize("name", ["", " ", "a", "x" * 17, "<script>", "aaaa", "admin", None, 42, "Robert'); DROP"])
def test_invalid_names_rejected(client, name):
    finish_game(client)
    assert client.post("/api/leaderboard", json={"name": name}).status_code == 400


def test_invalid_body_rejected(client):
    assert client.post("/api/leaderboard", data="oops").status_code == 400
    assert client.post("/api/leaderboard", json=["x"]).status_code == 400


def test_valid_submission_uses_server_score_not_payload(client):
    finish_game(client)
    server_xp = client.get("/api/game/state").get_json()["xp"]
    r = client.post("/api/leaderboard", json={"name": "Ishaan", "score": 999999, "xp": 999999})
    assert r.status_code == 201
    entry = client.get("/api/leaderboard").get_json()["entries"][0]
    assert entry["name"] == "Ishaan" and entry["xp"] == server_xp != 999999 and entry["position"] == 1


def test_duplicate_submission_blocked(client):
    finish_game(client)
    client.post("/api/leaderboard", json={"name": "Ishaan"})
    assert client.post("/api/leaderboard", json={"name": "Ishaan"}).status_code == 409
