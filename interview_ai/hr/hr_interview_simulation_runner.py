from pathlib import Path

from interview_ai.hr.hr_interview_simulator import (
    HRInterviewSimulator
)
from interview_ai.hr.hr_interview_scoring_engine import (
    HRInterviewScoringEngine
)


class HRInterviewSimulationRunner:
    """
    Runs simulated HR interviews and evaluates candidates
    using the existing HR interview scoring engine.
    """

    DEFAULT_SCORES = {
        "answer_relevance": [75],
        "communication": [75],
        "confidence": [75],
        "consistency": [75]
    }

    DEFAULT_CONFIG_PATH = (
        Path("config") /
        "hr_interview_scoring_rules.json"
    )

    def __init__(self, config_path=None):
        self.simulator = HRInterviewSimulator()

        if config_path is None:
            config_path = self.DEFAULT_CONFIG_PATH

        self.scoring_engine = HRInterviewScoringEngine(
            config_path
        )

    @staticmethod
    def _normalize_question_scores(question_scores):
        """
        Convert per-question component scores into
        one normalized 0-100 score per component.

        Example:
            [80, 80] -> 80
        """
        normalized = {}

        for parameter, values in question_scores.items():
            if values is None:
                normalized[parameter] = 0.0
                continue

            if isinstance(values, (int, float)):
                normalized[parameter] = float(values)
                continue

            if isinstance(values, (list, tuple)):
                if not values:
                    normalized[parameter] = 0.0
                else:
                    numeric_values = [
                        float(value)
                        for value in values
                    ]

                    normalized[parameter] = round(
                        sum(numeric_values)
                        / len(numeric_values),
                        2
                    )
                continue

            normalized[parameter] = 0.0

        return normalized

    def run_candidate(
        self,
        candidate_type,
        candidate_name="Test Candidate",
        responses=None,
        scores=None,
        question_scores=None
    ):
        # 1. Simulate interview
        simulation = self.simulator.simulate(
            candidate_type=candidate_type,
            candidate_name=candidate_name,
            responses=responses
        )

        # 2. Select scoring input
        if question_scores is not None:
            raw_scores = question_scores
        elif scores is not None:
            raw_scores = scores
        else:
            raw_scores = self.DEFAULT_SCORES

        # 3. Normalize per-question scores
        normalized_scores = (
            self._normalize_question_scores(
                raw_scores
            )
        )

        # 4. Make sure all required parameters exist
        for parameter in self.DEFAULT_SCORES:
            if parameter not in normalized_scores:
                normalized_scores[parameter] = 0.0

        # 5. Calculate weighted HR score
        hr_score = self.scoring_engine.calculate_score(
            answer_relevance=normalized_scores[
                "answer_relevance"
            ],
            communication=normalized_scores[
                "communication"
            ],
            confidence=normalized_scores[
                "confidence"
            ],
            consistency=normalized_scores[
                "consistency"
            ]
        )

        return {
            "candidate_name":
                simulation["candidate_name"],

            "candidate_type":
                simulation["candidate_type"],

            "responses":
                simulation["responses"],

            "response_count":
                simulation["response_count"],

            "normalized_scores":
                normalized_scores,

            "hr_score":
                hr_score
        }

    def run_all(
        self,
        candidate_name_prefix="Test Candidate"
    ):
        results = []

        for candidate_type in sorted(
            HRInterviewSimulator.CANDIDATE_TYPES
        ):
            result = self.run_candidate(
                candidate_type=candidate_type,
                candidate_name=(
                    f"{candidate_name_prefix} - "
                    f"{candidate_type.title()}"
                )
            )

            results.append(result)

        return results