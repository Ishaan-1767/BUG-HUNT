import pytest


def test_list_has_eight_missions(client):
    d = client.get("/api/game/missions").get_json()
    assert len(d["missions"]) == 8 and "Security" in d["categories"]


@pytest.mark.parametrize("mid", range(1, 9))
def test_every_mission_loads_without_leaking_answer(client, mid):
    r = client.get(f"/api/game/mission/{mid}")
    assert r.status_code == 200
    body = r.get_json()
    assert body["id"] == mid and "answer" not in body
    assert "keywords" not in r.get_data(as_text=True)


@pytest.mark.parametrize("mid", [0, 9, 999, -1])
def test_invalid_mission_id_404(client, mid):
    assert client.get(f"/api/game/mission/{mid}").status_code == 404


def test_non_numeric_mission_id_404(client):
    assert client.get("/api/game/mission/abc").status_code == 404
