class TaskEvaluationLogic:
    WEIGHTS = {
        "correctness": 0.40,
        "efficiency": 0.20,
        "code_quality": 0.20,
        "problem_solving": 0.20,
    }

    @staticmethod
    def _validate_score(value, name):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not 0 <= value <= 100
        ):
            raise ValueError(f"{name} must be between 0 and 100")

    def evaluate(self, correctness, efficiency, code_quality, problem_solving):
        scores = {
            "correctness": correctness,
            "efficiency": efficiency,
            "code_quality": code_quality,
            "problem_solving": problem_solving,
        }

        for name, value in scores.items():
            self._validate_score(value, name)

        breakdown = {
            name: {
                "score": value,
                "weight": self.WEIGHTS[name],
                "weighted_score": round(
                    value * self.WEIGHTS[name], 2
                ),
            }
            for name, value in scores.items()
        }

        return {
            "evaluation_score": round(
                sum(item["weighted_score"] for item in breakdown.values()),
                2,
            ),
            "maximum_score": 100,
            "breakdown": breakdown,
            "human_review_required": True,
        }

    @staticmethod
    def capture_submission(code, execution_result):
        if not isinstance(code, str):
            raise TypeError("code must be a string")

        if not isinstance(execution_result, dict):
            raise TypeError("execution_result must be a dictionary")

        return {
            "code_snapshot": code,
            "execution_result": execution_result.copy(),
        }