"""SQLite leaderboard. Every query is parameterized."""
import os
import re
import sqlite3

NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.-]{1,15}$")
BLOCKED = {"admin", "null", "undefined", "root"}


def validate_name(name):
    """Return (clean_name, error). Error is None when valid."""
    if not isinstance(name, str):
        return None, "name must be a string"
    name = name.strip()
    if not NAME_RE.match(name):
        return None, "name must be 2-16 chars: letters, digits, space, . _ -"
    if name.lower() in BLOCKED or len(set(name.lower())) < 2:
        return None, "name is not allowed"
    return name, None


def _connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with _connect(path) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, score INTEGER NOT NULL,
            xp INTEGER NOT NULL, completed INTEGER NOT NULL, accuracy INTEGER NOT NULL,
            time_seconds INTEGER NOT NULL, rank TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")


def add_entry(path, name, score, xp, completed, accuracy, seconds, rank):
    with _connect(path) as c:
        cur = c.execute("INSERT INTO scores (name,score,xp,completed,accuracy,time_seconds,rank) VALUES (?,?,?,?,?,?,?)",
                        (name, score, xp, completed, accuracy, seconds, rank))
        return cur.lastrowid


def top_entries(path, limit=10):
    with _connect(path) as c:
        rows = c.execute("SELECT name,score,xp,completed,accuracy,time_seconds,rank FROM scores "
                         "ORDER BY xp DESC, time_seconds ASC LIMIT ?", (limit,)).fetchall()
    return [dict(r) | {"position": i + 1} for i, r in enumerate(rows)]
