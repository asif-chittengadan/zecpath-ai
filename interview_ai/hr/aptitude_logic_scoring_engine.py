from interview_ai.hr.hr_scoring_config import (
    HRScoringConfig
)
from interview_ai.hr.problem_solving_clarity_analyzer import (
    ProblemSolvingClarityAnalyzer
)


class AptitudeLogicScoringEngine:
    """
    Scores logical thinking and problem-solving ability
    using configurable weighted parameters.
    """

    PARAMETERS = [
        "reasoning_accuracy",
        "reasoning_structure",
        "problem_solving",
        "clarity"
    ]

    def __init__(self, config_path):
        self.config = HRScoringConfig(
            config_path,
            required_parameters=self.PARAMETERS
        )
        self.clarity_analyzer = ProblemSolvingClarityAnalyzer()

        self._validate_parameters()

    def _validate_parameters(self):
        configured = set(
            self.config.get_weights().keys()
        )

        required = set(
            self.PARAMETERS
        )

        missing = required - configured

        if missing:
            raise ValueError(
                "Missing aptitude scoring parameters: "
                + ", ".join(sorted(missing))
            )

    def analyze_problem_solving_clarity(self, response):
        """
        Analyze a candidate's problem-solving response
        and return the clarity evaluation.
        """

        return self.clarity_analyzer.analyze(response)

    def get_clarity_score(self, response):
        """
        Return the normalized clarity score from a
        problem-solving response.
        """

        result = self.analyze_problem_solving_clarity(
            response
        )

        return result["clarity_score"]

    def calculate_score(
        self,
        reasoning_accuracy,
        reasoning_structure,
        problem_solving,
        clarity
    ):
        scores = {
            "reasoning_accuracy": self._normalize_score(
                reasoning_accuracy
            ),
            "reasoning_structure": self._normalize_score(
                reasoning_structure
            ),
            "problem_solving": self._normalize_score(
                problem_solving
            ),
            "clarity": self._normalize_score(
                clarity
            )
        }

        weighted_scores = {}

        for parameter, score in scores.items():
            weight = self.config.get_weight(
                parameter
            )

            weighted_scores[parameter] = round(
                score * weight,
                2
            )

        final_score = round(
            sum(weighted_scores.values()),
            2
        )

        return {
            "final_score": final_score,
            "component_scores": scores,
            "weighted_scores": weighted_scores
        }

    def get_score_breakdown(
        self,
        reasoning_accuracy,
        reasoning_structure,
        problem_solving,
        clarity
    ):
        result = self.calculate_score(
            reasoning_accuracy=reasoning_accuracy,
            reasoning_structure=reasoning_structure,
            problem_solving=problem_solving,
            clarity=clarity
        )

        breakdown = []

        for parameter in self.PARAMETERS:
            weight = self.config.get_weight(
                parameter
            )

            breakdown.append({
                "parameter": parameter,
                "score": result[
                    "component_scores"
                ][parameter],
                "weight": weight,
                "weight_percentage": round(
                    weight * 100,
                    2
                ),
                "contribution": result[
                    "weighted_scores"
                ][parameter]
            })

        return {
            "final_score": result["final_score"],
            "breakdown": breakdown
        }

    def _normalize_score(self, score):
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0

        return round(
            max(
                0.0,
                min(
                    100.0,
                    score
                )
            ),
            2
        )