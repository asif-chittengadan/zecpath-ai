import pytest

from interview_ai.machine_test.machine_test_evaluator import (
    MachineTestEvaluator,
)


@pytest.fixture
def task():
    return {
        "task_id": "MT-001",
        "title": "Sum Two Numbers",
        "task_type": "coding",
        "description": "Return the sum of two numbers.",
        "time_limit_minutes": 30,
    }


def test_integrated_evaluation(task):
    result = MachineTestEvaluator().evaluate_submission(
        task=task,
        candidate_id="CAND-001",
        code="def add(a, b): return a + b",
        execution_result={"exit_code": 0, "stdout": "5", "stderr": ""},
        correctness=90,
        efficiency=80,
        code_quality=85,
        problem_solving=70,
        time_taken_minutes=25,
    )

    assert result["final_score"] == 83.0
    assert result["task_id"] == "MT-001"
    assert result["submission"]["execution_result"]["exit_code"] == 0
    assert result["human_review_required"] is True


def test_invalid_candidate_id_is_rejected(task):
    with pytest.raises(ValueError):
        MachineTestEvaluator().evaluate_submission(
            task, "", "print(1)", {"exit_code": 0},
            90, 80, 85, 70, 20,
        )


def test_invalid_execution_result_is_rejected(task):
    with pytest.raises(TypeError):
        MachineTestEvaluator().evaluate_submission(
            task, "CAND-001", "print(1)", [],
            90, 80, 85, 70, 20,
        )


def test_invalid_task_is_rejected():
    with pytest.raises(ValueError):
        MachineTestEvaluator().evaluate_submission(
            {}, "CAND-001", "print(1)", {"exit_code": 0},
            90, 80, 85, 70, 20,
        )