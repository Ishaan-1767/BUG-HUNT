"""Mission definitions. `answer` is server-only and never sent to the client."""

CATEGORIES = ["Logic", "UI", "API", "Validation", "Data", "State Management", "Security", "Performance"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
TIME_LIMIT = 90  # seconds


def _m(id, title, briefing, widget, data, category, severity, keywords, explanation):
    return {
        "id": id, "title": title, "briefing": briefing, "widget": widget, "data": data,
        "answer": {"category": category, "severity": severity,
                   "keywords": keywords,  # list of synonym groups; each group = one idea
                   "explanation": explanation},
    }


MISSIONS = [
    _m(1, "BROKEN LOGIN",
       "The NEXUS staff portal is letting people in. Try different credentials (valid: admin / nexus123).",
       "login", {}, "Security", "Critical",
       [["empty", "blank", "no password", "without password", "missing password"],
        ["accept", "allow", "login", "log in", "bypass", "authenticat", "access"]],
       "Login succeeds for admin with an EMPTY password: authentication bypass."),
    _m(2, "API HUNTER",
       "GET /users/9999 answered. Read the response carefully. Does it make sense?",
       "api", {"request": "GET /api/users/9999",
               "status": 200,
               "body": {"error": "User not found", "user": None}},
       "API", "High",
       [["200", "status"], ["not found", "404", "error", "null", "none", "missing user"]],
       "A 'not found' error is returned with HTTP 200 instead of 404."),
    _m(3, "ZERO DIVISION",
       "The finance calculator is live. Push it to its limits.",
       "calc", {}, "Logic", "Medium",
       [["zero", "/ 0", "/0", "divide", "division"],
        ["0", "error", "exception", "infinity", "handle", "wrong", "silent"]],
       "Dividing by zero silently returns 0 instead of raising an error."),
    _m(4, "FORM FAILURE",
       "The registration service is accepting bad accounts. Try to register with invalid data.",
       "form", {}, "Validation", "High",
       [["password"], ["short", "length", "minimum", "min", "weak", "characters", "too small"]],
       "Passwords of any length (even 1 character) are accepted."),
    _m(5, "STATE MACHINE",
       "Session controller: LOCKED > LOGIN > AUTHENTICATED > LOCKED. Walk every transition.",
       "state", {}, "State Management", "High",
       [["locked"], ["logout", "log out"], ["authenticated", "bypass", "skip", "without login", "login"]],
       "From LOCKED, 'logout' jumps straight to AUTHENTICATED, skipping login."),
    _m(6, "DATA VALIDATOR",
       "Compare expected and actual payloads. Report what is malformed.",
       "json", {"expected": {"id": 101, "name": "Alex", "age": 21},
                "actual": {"id": "101", "name": "", "age": -4}},
       "Data", "Medium",
       [["id", "string", "type"], ["name", "empty", "blank"], ["age", "negative", "-4"]],
       "id has the wrong type, name is empty, and age is negative."),
    _m(7, "UI GHOST BUG",
       "The visit counter should add 1 per click. Click it. Then click it again.",
       "counter", {}, "UI", "Low",
       [["counter", "count", "number", "increment"], ["skip", "jump", "two", "2", "+2", "5", "6", "wrong"]],
       "The counter skips a number (4 jumps to 6)."),
    _m(8, "THE FINAL DEFECT",
       "Checkout service. Price is 20 per unit. Break it in every way you can, then report the worst issue.",
       "checkout", {"price": 20}, "Validation", "Critical",
       [["negative", "-", "quantity", "qty"], ["total", "price", "discount", "refund", "money"],
        ["validat", "accept", "check", "range", "limit"]],
       "Quantity and discount are unvalidated: negative quantity or >100% discount makes negative totals."),
]


def get_mission(mission_id):
    return next((m for m in MISSIONS if m["id"] == mission_id), None)


def public_view(m):
    return {k: m[k] for k in ("id", "title", "briefing", "widget", "data")} | {"time_limit": TIME_LIMIT}
