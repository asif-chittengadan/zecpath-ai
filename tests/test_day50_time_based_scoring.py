import pytest

from interview_ai.machine_test.time_based_scoring import TimeBasedScoring


def test_score_without_bonus_or_penalty():
    result = TimeBasedScoring().calculate(80, 30, 30)
    assert result["final_score"] == 80


def test_early_completion_bonus():
    result = TimeBasedScoring(bonus_rate=0.1).calculate(80, 30, 15)
    assert result["final_score"] == 84


def test_overtime_penalty():
    result = TimeBasedScoring(penalty_rate=0.1).calculate(80, 30, 60)
    assert result["final_score"] == 72


def test_score_is_capped_at_100():
    result = TimeBasedScoring(bonus_rate=0.5).calculate(90, 30, 1)
    assert result["final_score"] <= 100


def test_invalid_time_limit_is_rejected():
    with pytest.raises(ValueError):
        TimeBasedScoring().calculate(80, 0, 10)