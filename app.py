import os
import time

from flask import Flask, jsonify, render_template, request, session

from game import leaderboard as lb
from game import missions as M
from game import scoring as S

START_LIVES = 3
RETRY_PENALTY = 100


def new_run():
    return {"lives": START_LIVES, "score": 0, "xp": 0, "combo": 1, "done": [],
            "attempts": 0, "correct": 0, "time": 0.0, "started": {}, "submitted": False}


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get("BUGHUNT_SECRET") or os.urandom(24),
                      DATABASE=os.path.join(app.root_path, "database", "game.db"),
                      SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_HTTPONLY=True)
    if config:
        app.config.update(config)
    lb.init_db(app.config["DATABASE"])

    def run_state():
        if "run" not in session:
            session["run"] = new_run()
        return dict(session["run"])

    def save(run):
        session["run"] = run
        session.modified = True

    def summary(run):
        acc = round(100 * run["correct"] / run["attempts"]) if run["attempts"] else 0
        return {"lives": run["lives"], "score": run["score"], "xp": run["xp"], "combo": run["combo"],
                "rank": S.rank_for(run["xp"]), "completed": run["done"], "accuracy": acc,
                "time": round(run["time"]), "total_missions": len(M.MISSIONS),
                "finished": len(run["done"]) == len(M.MISSIONS)}

    def err(msg, code):
        return jsonify({"error": msg}), code

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "missions": len(M.MISSIONS)})

    @app.get("/api/game/missions")
    def list_missions():
        return jsonify({"missions": [{"id": m["id"], "title": m["title"]} for m in M.MISSIONS],
                        "categories": M.CATEGORIES, "severities": M.SEVERITIES})

    @app.get("/api/game/mission/<int:mission_id>")
    def get_mission(mission_id):
        m = M.get_mission(mission_id)
        return jsonify(M.public_view(m)) if m else err("mission not found", 404)

    @app.post("/api/game/mission/<int:mission_id>/start")
    def start_mission(mission_id):
        if not M.get_mission(mission_id):
            return err("mission not found", 404)
        run = run_state()
        run["started"][str(mission_id)] = time.time()
        save(run)
        return jsonify({"started": True, "time_limit": M.TIME_LIMIT})

    @app.post("/api/game/mission/<int:mission_id>/submit")
    def submit(mission_id):
        m = M.get_mission(mission_id)
        if not m:
            return err("mission not found", 404)
        run = run_state()
        if run["lives"] <= 0:
            return err("no lives left, retry first", 403)
        if mission_id in run["done"]:
            return err("mission already completed", 409)
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return err("JSON object body required", 400)
        category, severity, diagnosis = data.get("category"), data.get("severity"), data.get("diagnosis", "")
        if category not in M.CATEGORIES:
            return err("invalid category", 400)
        if severity not in M.SEVERITIES:
            return err("invalid severity", 400)
        if not isinstance(diagnosis, str) or len(diagnosis) > 300:
            return err("diagnosis must be a string of at most 300 characters", 400)

        started = run["started"].get(str(mission_id))
        elapsed = time.time() - started if started else M.TIME_LIMIT  # no start = no speed bonus
        res = S.evaluate(m, category, severity, diagnosis, elapsed, run["combo"])
        run["attempts"] += 1
        out = {"solved": res["solved"], "parts": res["parts"]}
        if res["solved"]:
            run["correct"] += 1
            run["xp"] += res["xp"]
            run["score"] += res["score"]
            run["combo"] = res["combo"]
            run["time"] += elapsed
            run["done"].append(mission_id)
            run["started"].pop(str(mission_id), None)
            out |= {"breakdown": res["breakdown"], "multiplier": res["multiplier"],
                    "gained_xp": res["xp"], "gained_score": res["score"],
                    "solution": {"category": m["answer"]["category"], "severity": m["answer"]["severity"],
                                 "explanation": m["answer"]["explanation"]}}
        else:
            run["lives"] -= 1
            run["combo"] = 1
        save(run)
        return jsonify(out | {"state": summary(run), "game_over": run["lives"] <= 0})

    @app.get("/api/game/state")
    def state():
        return jsonify(summary(run_state()))

    @app.post("/api/game/reset")
    def reset():
        save(new_run())
        return jsonify(summary(new_run()))

    @app.post("/api/game/retry")
    def retry():
        run = run_state()
        if run["lives"] <= 0:
            run["lives"], run["combo"] = START_LIVES, 1
            run["xp"] = max(0, run["xp"] - RETRY_PENALTY)
            run["score"] = max(0, run["score"] - RETRY_PENALTY)
            save(run)
        return jsonify(summary(run))

    @app.get("/api/leaderboard")
    def get_board():
        return jsonify({"entries": lb.top_entries(app.config["DATABASE"])})

    @app.post("/api/leaderboard")
    def post_board():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return err("JSON object body required", 400)
        name, problem = lb.validate_name(data.get("name"))
        if problem:
            return err(problem, 400)
        run = run_state()
        s = summary(run)
        if not s["finished"]:
            return err("finish all missions first", 403)
        if run["submitted"]:
            return err("score already submitted", 409)
        # score/xp come from the server-side session, never from the request body
        lb.add_entry(app.config["DATABASE"], name, s["score"], s["xp"], len(s["completed"]),
                     s["accuracy"], s["time"], s["rank"])
        run["submitted"] = True
        save(run)
        return jsonify({"saved": True, "entries": lb.top_entries(app.config["DATABASE"])}), 201

    @app.errorhandler(404)
    def not_found(_):
        if request.path.startswith("/api/"):
            return err("not found", 404)
        return "Not found", 404

    @app.errorhandler(405)
    def bad_method(_):
        return err("method not allowed", 405)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
