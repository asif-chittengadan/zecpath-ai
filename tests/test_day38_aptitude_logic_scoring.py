import unittest

from interview_ai.hr.aptitude_logic_scoring_engine import (
    AptitudeLogicScoringEngine
)


class TestDay38AptitudeLogicScoring(unittest.TestCase):

    def setUp(self):
        self.engine = AptitudeLogicScoringEngine(
            "config/aptitude_scoring_rules.json"
        )

    def test_weighted_score(self):
        result = self.engine.calculate_score(
            reasoning_accuracy=80,
            reasoning_structure=90,
            problem_solving=70,
            clarity=85
        )

        expected = (
            80 * 0.30
            + 90 * 0.25
            + 70 * 0.25
            + 85 * 0.20
        )

        self.assertEqual(
            result["final_score"],
            round(expected, 2)
        )

    def test_all_scores_are_100(self):
        result = self.engine.calculate_score(
            reasoning_accuracy=100,
            reasoning_structure=100,
            problem_solving=100,
            clarity=100
        )

        self.assertEqual(
            result["final_score"],
            100.0
        )

    def test_all_scores_are_zero(self):
        result = self.engine.calculate_score(
            reasoning_accuracy=0,
            reasoning_structure=0,
            problem_solving=0,
            clarity=0
        )

        self.assertEqual(
            result["final_score"],
            0.0
        )

    def test_scores_are_bounded(self):
        result = self.engine.calculate_score(
            reasoning_accuracy=150,
            reasoning_structure=-20,
            problem_solving=120,
            clarity=-10
        )

        self.assertEqual(
            result["component_scores"][
                "reasoning_accuracy"
            ],
            100.0
        )

        self.assertEqual(
            result["component_scores"][
                "reasoning_structure"
            ],
            0.0
        )

        self.assertEqual(
            result["component_scores"][
                "problem_solving"
            ],
            100.0
        )

        self.assertEqual(
            result["component_scores"][
                "clarity"
            ],
            0.0
        )

    def test_invalid_values_are_safe(self):
        result = self.engine.calculate_score(
            reasoning_accuracy="invalid",
            reasoning_structure=None,
            problem_solving="invalid",
            clarity=None
        )

        self.assertEqual(
            result["final_score"],
            0.0
        )

    def test_breakdown_contains_all_parameters(self):
        result = self.engine.get_score_breakdown(
            reasoning_accuracy=80,
            reasoning_structure=90,
            problem_solving=70,
            clarity=85
        )

        parameters = [
            item["parameter"]
            for item in result["breakdown"]
        ]

        self.assertEqual(
            set(parameters),
            {
                "reasoning_accuracy",
                "reasoning_structure",
                "problem_solving",
                "clarity"
            }
        )

    def test_breakdown_contributions_equal_final_score(self):
        result = self.engine.get_score_breakdown(
            reasoning_accuracy=80,
            reasoning_structure=90,
            problem_solving=70,
            clarity=85
        )

        total = round(
            sum(
                item["contribution"]
                for item in result["breakdown"]
            ),
            2
        )

        self.assertEqual(
            total,
            result["final_score"]
        )

    def test_weight_percentages(self):
        result = self.engine.get_score_breakdown(
            reasoning_accuracy=80,
            reasoning_structure=90,
            problem_solving=70,
            clarity=85
        )

        weights = {
            item["parameter"]:
                item["weight_percentage"]
            for item in result["breakdown"]
        }

        self.assertEqual(
            weights["reasoning_accuracy"],
            30.0
        )

        self.assertEqual(
            weights["reasoning_structure"],
            25.0
        )

        self.assertEqual(
            weights["problem_solving"],
            25.0
        )

        self.assertEqual(
            weights["clarity"],
            20.0
        )


if __name__ == "__main__":
    unittest.main()