import unittest

from interview_ai.hr.unified_scoring_config import (
    UnifiedScoringConfig
)


class TestDay41UnifiedScoringConfig(
    unittest.TestCase
):

    CONFIG_PATH = (
        "config/unified_scoring_rules.json"
    )

    def setUp(self):
        self.config = UnifiedScoringConfig(
            self.CONFIG_PATH
        )

    def test_required_rounds_exist(self):
        weights = self.config.get_weights()

        self.assertEqual(
            set(weights.keys()),
            {
                "ats",
                "screening",
                "hr_interview"
            }
        )

    def test_weights_total_one(self):
        weights = self.config.get_weights()

        self.assertEqual(
            round(sum(weights.values()), 6),
            1.0
        )

    def test_ats_weight(self):
        self.assertEqual(
            self.config.get_weight("ats"),
            0.40
        )

    def test_screening_weight(self):
        self.assertEqual(
            self.config.get_weight("screening"),
            0.25
        )

    def test_hr_interview_weight(self):
        self.assertEqual(
            self.config.get_weight("hr_interview"),
            0.35
        )

    def test_screening_input_range(self):
        score_range = (
            self.config.get_input_range(
                "screening"
            )
        )

        self.assertEqual(
            score_range["minimum"],
            0
        )

        self.assertEqual(
            score_range["maximum"],
            10
        )

    def test_hr_input_range(self):
        score_range = (
            self.config.get_input_range(
                "hr_interview"
            )
        )

        self.assertEqual(
            score_range["minimum"],
            0
        )

        self.assertEqual(
            score_range["maximum"],
            100
        )


if __name__ == "__main__":
    unittest.main()