from tests.conftest import fail, finish_game, solve


def test_correct_answer_scores_and_raises_combo(client):
    r = solve(client, 1).get_json()
    assert r["solved"] and r["breakdown"]["category"] == 100 and r["breakdown"]["severity"] == 100
    assert r["breakdown"]["perfect"] == 100 and r["state"]["combo"] == 2
    assert r["gained_score"] == r["gained_xp"] * r["multiplier"]


def test_combo_multiplier_applies_on_second_mission(client):
    solve(client, 1)
    r = solve(client, 2).get_json()
    assert r["multiplier"] == 2 and r["gained_score"] == r["gained_xp"] * 2


def test_speed_bonus_bounded(client):
    assert 0 <= solve(client, 1).get_json()["breakdown"]["speed"] <= 50


def test_no_start_means_no_speed_bonus(client):
    from tests.conftest import good_answer
    from game.missions import MISSIONS
    r = client.post("/api/game/mission/1/submit", json=good_answer(MISSIONS[0])).get_json()
    assert r["breakdown"]["speed"] == 0


def test_wrong_answer_loses_life_and_resets_combo(client):
    solve(client, 1)
    r = fail(client, 2).get_json()
    assert not r["solved"] and r["state"]["lives"] == 2 and r["state"]["combo"] == 1
    assert "solution" not in r


def test_three_wrong_answers_end_game_then_retry(client):
    for _ in range(3):
        r = fail(client).get_json()
    assert r["game_over"] and fail(client).status_code == 403
    assert client.post("/api/game/retry").get_json()["lives"] == 3


def test_partial_credit_two_of_three_solves(client):
    r = client.post("/api/game/mission/1/submit",
                    json={"category": "Security", "severity": "Low", "diagnosis": "empty password accepted"}).get_json()
    assert r["solved"] and r["breakdown"]["severity"] == 0 and r["breakdown"]["perfect"] == 0


def test_cannot_resubmit_completed_mission(client):
    solve(client, 1)
    assert solve(client, 1).status_code == 409


def test_client_cannot_inject_score(client):
    r = client.post("/api/game/mission/1/submit",
                    json={"category": "Logic", "severity": "Low", "diagnosis": "x", "score": 999999, "xp": 999999})
    assert r.get_json()["state"]["score"] == 0


def test_invalid_payloads(client):
    url = "/api/game/mission/1/submit"
    assert client.post(url, data="not json").status_code == 400
    assert client.post(url, json=[1, 2]).status_code == 400
    assert client.post(url, json={"category": "Nope", "severity": "Low"}).status_code == 400
    assert client.post(url, json={"category": "Logic", "severity": "Huge"}).status_code == 400
    assert client.post(url, json={"category": "Logic", "severity": "Low", "diagnosis": "x" * 301}).status_code == 400
    assert client.post(url, json={"category": "Logic", "severity": "Low", "diagnosis": 5}).status_code == 400
    assert client.get("/api/game/state").get_json()["lives"] == 3  # invalid input costs no life


def test_submit_unknown_mission_404(client):
    assert client.post("/api/game/mission/99/submit", json={}).status_code == 404


def test_full_run_finishes_with_rank(client):
    finish_game(client)
    s = client.get("/api/game/state").get_json()
    assert s["finished"] and s["accuracy"] == 100 and s["rank"] in ("DEFECT MASTER", "QA OPERATIVE")


def test_retry_costs_xp_but_never_below_zero(client):
    solve(client, 1)
    xp_before = client.get("/api/game/state").get_json()["xp"]
    for _ in range(3):
        fail(client, 2)
    state = client.post("/api/game/retry").get_json()
    assert state["xp"] == max(0, xp_before - 100) and state["lives"] == 3
    for _ in range(3):
        fail(client, 2)
    for _ in range(10):
        client.post("/api/game/retry")
        for _ in range(3):
            fail(client, 2)
    assert client.get("/api/game/state").get_json()["xp"] >= 0