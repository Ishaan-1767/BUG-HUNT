# BUG//HUNT

### Overview
A cyberpunk QA mini-game. You are a junior tester at **NEXUS SYSTEMS**: interact with 8 deliberately broken mini-apps, then file a defect report (category, severity, diagnosis). A Flask API scores the report server-side.

### Features
8 varied missions (login, API response, calculator, form, state machine, data validation, UI counter, final boss) · lives, XP, combo multiplier (max x5), speed bonus, ranks · SQLite leaderboard · dev console with live API logs · keyboard accessible, responsive.

### Tech Stack
Python 3, Flask, SQLite (stdlib `sqlite3`), pytest, vanilla HTML/CSS/JS (no framework).

### Architecture
Browser (vanilla JS `fetch`) ⇄ REST API (`app.py`) ⇄ game logic (`game/`) + SQLite. Mission data and answers live only on the server. Run state (lives, score, combo, mission start time) is kept in a signed Flask session, so the client cannot set it.

### Project Structure
```
app.py            Flask app factory + routes
game/missions.py  mission data (answers stay server-side)
game/scoring.py   scoring, combo, ranks, diagnosis matching
game/leaderboard.py  SQLite + name validation
tests/            pytest suite (conftest.py has helpers)
templates/ static/  frontend
```

### How to Run
```bash
cd BUG-HUNT
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. The database is created automatically. Optional: set `BUGHUNT_SECRET` for a stable session key.

### Running Tests
```bash
pytest
```

### API Endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | liveness check |
| GET | `/api/game/missions` | mission list, categories, severities |
| GET | `/api/game/mission/<id>` | public mission data (404 if unknown) |
| POST | `/api/game/mission/<id>/start` | starts the server-side timer |
| POST | `/api/game/mission/<id>/submit` | body `{category, severity, diagnosis}`; returns breakdown/state |
| GET | `/api/game/state` | current run summary |
| POST | `/api/game/reset` · `/api/game/retry` | new run · restore lives after failure |
| GET | `/api/leaderboard` | top 10 by XP |
| POST | `/api/leaderboard` | body `{name}`; only after all missions solved |

### Scoring
Base 100 + category 100 + severity 100 (50 if one level off) + diagnosis up to 150 + speed up to 50 + perfect 100. XP is that sum; score is XP × combo. A submission is accepted if 2 of 3 parts are right; otherwise −1 life. Perfect answers raise the combo.

### Testing Strategy
**What I tested:** every endpoint, all 8 missions, scoring maths, rank boundaries, name validation, invalid payloads.
**Why:** the backend is the source of truth, so its rules (scoring, lives, anti-cheat) must be regression-proof.
**How pytest was used:** Flask `test_client` with a fixture that builds a fresh app and temp SQLite file per test (isolation); `parametrize` for boundaries; shared helpers in `conftest.py`.
**API edge cases:** unknown/negative/non-numeric IDs, non-JSON bodies, list instead of object, bad enums, over-long or non-string diagnosis, wrong HTTP method, duplicate submissions, submitting after game over, invalid names (empty, too long, HTML, SQL-like, blocked words).
**Anti-cheat:** score/XP are computed on the server from a signed session; extra fields such as `"score": 999999` are ignored (tested); the leaderboard reads totals from the session, not the request; answers are never sent to the client (tested); SQL is parameterized; timing is measured server-side.

### Future Improvements
More missions and difficulty levels · real authentication · hosted leaderboard · Playwright/Selenium UI tests · GitHub Actions CI · GenAI-generated test cases.
