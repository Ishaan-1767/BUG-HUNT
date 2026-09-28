import pytest

from app import create_app
from game.missions import MISSIONS


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db"), "SECRET_KEY": "test"})
    return app.test_client()


def good_answer(mission):
    a = mission["answer"]
    return {"category": a["category"], "severity": a["severity"],
            "diagnosis": " ".join(g[0] for g in a["keywords"])}


def solve(client, mid):
    m = next(x for x in MISSIONS if x["id"] == mid)
    client.post(f"/api/game/mission/{mid}/start")
    return client.post(f"/api/game/mission/{mid}/submit", json=good_answer(m))


def fail(client, mid=1):
    return client.post(f"/api/game/mission/{mid}/submit",
                       json={"category": "Performance", "severity": "Low", "diagnosis": "nothing"})


def finish_game(client):
    for m in MISSIONS:
        solve(client, m["id"])
