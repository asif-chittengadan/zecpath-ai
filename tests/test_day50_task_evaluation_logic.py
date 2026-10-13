import pytest

from interview_ai.machine_test.task_evaluation_logic import (
    TaskEvaluationLogic,
)


def test_weighted_evaluation_score():
    result = TaskEvaluationLogic().evaluate(90, 80, 85, 70)

    assert result["evaluation_score"] == 83.0
    assert result["maximum_score"] == 100
    assert result["human_review_required"] is True


def test_perfect_scores_return_100():
    result = TaskEvaluationLogic().evaluate(100, 100, 100, 100)

    assert result["evaluation_score"] == 100


def test_invalid_score_is_rejected():
    with pytest.raises(ValueError):
        TaskEvaluationLogic().evaluate(101, 80, 85, 70)


def test_code_and_execution_result_are_captured():
    result = TaskEvaluationLogic.capture_submission(
        "print(2 + 3)",
        {"exit_code": 0, "stdout": "5", "stderr": ""},
    )

    assert result["code_snapshot"] == "print(2 + 3)"
    assert result["execution_result"]["stdout"] == "5"


def test_invalid_submission_types_are_rejected():
    with pytest.raises(TypeError):
        TaskEvaluationLogic.capture_submission(
            None, {"exit_code": 0}
        )