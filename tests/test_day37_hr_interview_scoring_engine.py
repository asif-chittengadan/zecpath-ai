import unittest

from interview_ai.hr.hr_interview_scoring_engine import (
    HRInterviewScoringEngine
)


class TestDay37HRInterviewScoringEngine(unittest.TestCase):

    def setUp(self):
        self.engine = HRInterviewScoringEngine(
            "config/hr_interview_scoring_rules.json"
        )

    def test_weighted_score(self):
        result = self.engine.calculate_score(
            answer_relevance=80,
            communication=90,
            confidence=70,
            consistency=85
        )

        self.assertEqual(
            result["final_score"],
            81.75
        )

    def test_all_scores_100(self):
        result = self.engine.calculate_score(
            answer_relevance=100,
            communication=100,
            confidence=100,
            consistency=100
        )

        self.assertEqual(
            result["final_score"],
            100
        )

    def test_all_scores_zero(self):
        result = self.engine.calculate_score(
            answer_relevance=0,
            communication=0,
            confidence=0,
            consistency=0
        )

        self.assertEqual(
            result["final_score"],
            0
        )

    def test_component_scores_are_returned(self):
        result = self.engine.calculate_score(
            answer_relevance=80,
            communication=90,
            confidence=70,
            consistency=85
        )

        self.assertIn(
            "component_scores",
            result
        )

        self.assertEqual(
            result["component_scores"][
                "communication"
            ],
            90
        )

    def test_weighted_scores_are_returned(self):
        result = self.engine.calculate_score(
            answer_relevance=80,
            communication=90,
            confidence=70,
            consistency=85
        )

        self.assertIn(
            "weighted_scores",
            result
        )

        self.assertEqual(
            result["weighted_scores"][
                "answer_relevance"
            ],
            24
        )

    def test_scores_above_100_are_bounded(self):
        result = self.engine.calculate_score(
            answer_relevance=150,
            communication=120,
            confidence=110,
            consistency=101
        )

        self.assertEqual(
            result["final_score"],
            100
        )

    def test_negative_scores_are_bounded(self):
        result = self.engine.calculate_score(
            answer_relevance=-20,
            communication=-10,
            confidence=-5,
            consistency=-100
        )

        self.assertEqual(
            result["final_score"],
            0
        )

    def test_invalid_score_is_safe(self):
        result = self.engine.calculate_score(
            answer_relevance="invalid",
            communication=80,
            confidence=70,
            consistency=90
        )

        self.assertEqual(
            result["component_scores"][
                "answer_relevance"
            ],
            0
        )

    def test_missing_score_is_safe(self):
        result = self.engine.calculate_score(
            answer_relevance=None,
            communication=80,
            confidence=70,
            consistency=90
        )

        self.assertEqual(
            result["component_scores"][
                "answer_relevance"
            ],
            0
        )

    def test_final_score_is_bounded(self):
        result = self.engine.calculate_score(
            answer_relevance=75,
            communication=80,
            confidence=85,
            consistency=90
        )

        self.assertGreaterEqual(
            result["final_score"],
            0
        )

        self.assertLessEqual(
            result["final_score"],
            100
        )
    def test_explainable_breakdown_is_returned(self):
        result = self.engine.get_score_breakdown(
            answer_relevance=80,
            communication=90,
            confidence=70,
            consistency=85
        )

        self.assertEqual(
            result["final_score"],
            81.75
        )

        self.assertIn(
            "breakdown",
            result
        )

        self.assertEqual(
            len(result["breakdown"]),
            4
        )

    def test_breakdown_contains_all_parameters(self):
        result = self.engine.get_score_breakdown(
            answer_relevance=80,
            communication=90,
            confidence=70,
            consistency=85
        )

        parameters = [
            item["parameter"]
            for item in result["breakdown"]
        ]

        self.assertEqual(
            set(parameters),
            {
                "answer_relevance",
                "communication",
                "confidence",
                "consistency"
            }
        )

    def test_breakdown_contains_weight_percentage(self):
        result = self.engine.get_score_breakdown(
            answer_relevance=80,
            communication=90,
            confidence=70,
            consistency=85
        )

        relevance = next(
            item
            for item in result["breakdown"]
            if item["parameter"] == "answer_relevance"
        )

        self.assertEqual(
            relevance["weight_percentage"],
            30.0
        )

    def test_breakdown_contributions_sum_to_final_score(self):
        result = self.engine.get_score_breakdown(
            answer_relevance=80,
            communication=90,
            confidence=70,
            consistency=85
        )

        total_contribution = round(
            sum(
                item["contribution"]
                for item in result["breakdown"]
            ),
            2
        )

        self.assertEqual(
            total_contribution,
            result["final_score"]
        )

if __name__ == "__main__":
    unittest.main()