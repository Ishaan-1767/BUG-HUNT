import pytest

from game.missions import MISSIONS
from game.scoring import diagnosis_ratio, evaluate, rank_for


@pytest.mark.parametrize("xp,rank", [(0, "ROOKIE"), (499, "ROOKIE"), (500, "BUG SCOUT"), (999, "BUG SCOUT"),
                                     (1000, "BUG HUNTER"), (1999, "BUG HUNTER"), (2000, "QA OPERATIVE"),
                                     (2999, "QA OPERATIVE"), (3000, "DEFECT MASTER")])
def test_rank_boundaries(xp, rank):
    assert rank_for(xp) == rank


def test_diagnosis_ratio_is_case_insensitive_and_synonym_aware():
    groups = [["empty", "blank"], ["accept"]]
    assert diagnosis_ratio("BLANK password ACCEPTED", groups) == 1.0
    assert diagnosis_ratio("blank", groups) == 0.5
    assert diagnosis_ratio("", groups) == 0.0


def test_combo_is_capped():
    m = MISSIONS[0]
    r = evaluate(m, "Security", "Critical", "empty password accepted", 0, 99)
    assert r["multiplier"] == 5 and r["combo"] == 5


def test_slow_answer_gets_no_speed_bonus():
    r = evaluate(MISSIONS[0], "Security", "Critical", "empty accept", 500, 1)
    assert r["breakdown"]["speed"] == 0
