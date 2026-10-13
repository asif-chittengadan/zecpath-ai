from datetime import datetime, timezone

from interview_ai.machine_test.machine_test_framework import (
    MachineTestFramework,
)
from interview_ai.machine_test.task_evaluation_logic import (
    TaskEvaluationLogic,
)
from interview_ai.machine_test.time_based_scoring import (
    TimeBasedScoring,
)


class MachineTestEvaluator:
    def __init__(self, bonus_rate=0.0, penalty_rate=0.0):
        self.framework = MachineTestFramework()
        self.evaluation = TaskEvaluationLogic()
        self.time_scoring = TimeBasedScoring(
            bonus_rate=bonus_rate,
            penalty_rate=penalty_rate,
        )

    def evaluate_submission(
        self,
        task,
        candidate_id,
        code,
        execution_result,
        correctness,
        efficiency,
        code_quality,
        problem_solving,
        time_taken_minutes,
    ):
        self.framework.validate_task(task)

        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("candidate_id must be a non-empty string")

        if not isinstance(execution_result, dict):
            raise TypeError("execution_result must be a dictionary")

        if not isinstance(time_taken_minutes, (int, float)) or isinstance(
            time_taken_minutes, bool
        ):
            raise ValueError("time_taken_minutes must be numeric")

        submission = self.evaluation.capture_submission(
            code,
            execution_result,
        )

        component_scores = self.evaluation.evaluate(
            correctness,
            efficiency,
            code_quality,
            problem_solving,
        )

        timed_score = self.time_scoring.calculate(
            component_scores["evaluation_score"],
            task["time_limit_minutes"],
            time_taken_minutes,
        )

        return {
            "candidate_id": candidate_id.strip(),
            "task_id": task["task_id"],
            "task_type": task["task_type"],
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "submission": submission,
            "component_scores": component_scores,
            "time_scoring": timed_score,
            "final_score": timed_score["final_score"],
            "human_review_required": True,
        }