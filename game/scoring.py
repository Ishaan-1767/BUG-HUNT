"""All score/XP/rank logic lives here (server-side only)."""
from .missions import SEVERITIES, TIME_LIMIT

MAX_COMBO = 5
RANKS = [(3000, "DEFECT MASTER"), (2000, "QA OPERATIVE"), (1000, "BUG HUNTER"), (500, "BUG SCOUT"), (0, "ROOKIE")]


def rank_for(xp):
    return next(name for floor, name in RANKS if xp >= floor)


def diagnosis_ratio(text, groups):
    """Fraction of idea-groups mentioned (any synonym in a group counts)."""
    text = (text or "").lower()
    if not groups:
        return 0.0
    return sum(any(w in text for w in g) for g in groups) / len(groups)


def evaluate(mission, category, severity, diagnosis, elapsed, combo):
    ans = mission["answer"]
    cat_ok = category == ans["category"]
    sev_ok = severity == ans["severity"]
    sev_gap = abs(SEVERITIES.index(severity) - SEVERITIES.index(ans["severity"]))
    ratio = diagnosis_ratio(diagnosis, ans["keywords"])
    diag_ok = ratio >= 0.5
    parts = int(cat_ok) + int(sev_ok) + int(diag_ok)
    result = {"solved": parts >= 2, "parts": {"category": cat_ok, "severity": sev_ok, "diagnosis": diag_ok}}
    if not result["solved"]:
        return result | {"combo": 1}
    b = {
        "base": 100,
        "category": 100 if cat_ok else 0,
        "severity": 100 if sev_ok else (50 if sev_gap == 1 else 0),
        "diagnosis": round(150 * ratio) if diag_ok else 0,
        "speed": round(50 * max(0.0, TIME_LIMIT - elapsed) / TIME_LIMIT),
        "perfect": 100 if parts == 3 else 0,
    }
    xp = sum(b.values())
    mult = max(1, min(combo, MAX_COMBO))
    return result | {"breakdown": b, "multiplier": mult, "xp": xp, "score": xp * mult,
                     "combo": min(combo + 1, MAX_COMBO) if parts == 3 else combo}
