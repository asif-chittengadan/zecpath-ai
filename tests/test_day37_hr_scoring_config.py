import json
import tempfile
import unittest
from pathlib import Path

from interview_ai.hr.hr_scoring_config import (
    HRScoringConfig
)


class TestDay37HRScoringConfig(unittest.TestCase):

    def setUp(self):
        self.config_path = Path(
            "config/hr_interview_scoring_rules.json"
        )

        self.config = HRScoringConfig(
            self.config_path
        )

    def test_all_required_parameters_exist(self):
        weights = self.config.get_weights()

        self.assertEqual(
            set(weights.keys()),
            {
                "answer_relevance",
                "communication",
                "confidence",
                "consistency"
            }
        )

    def test_weights_sum_to_one(self):
        weights = self.config.get_weights()

        self.assertAlmostEqual(
            sum(weights.values()),
            1.0
        )

    def test_answer_relevance_weight(self):
        self.assertEqual(
            self.config.get_weight(
                "answer_relevance"
            ),
            0.30
        )

    def test_communication_weight(self):
        self.assertEqual(
            self.config.get_weight(
                "communication"
            ),
            0.25
        )

    def test_confidence_weight(self):
        self.assertEqual(
            self.config.get_weight(
                "confidence"
            ),
            0.20
        )

    def test_consistency_weight(self):
        self.assertEqual(
            self.config.get_weight(
                "consistency"
            ),
            0.25
        )

    def test_score_range(self):
        score_range = (
            self.config.get_score_range()
        )

        self.assertEqual(
            score_range["minimum"],
            0
        )

        self.assertEqual(
            score_range["maximum"],
            100
        )

    def test_normalization_is_enabled(self):
        self.assertTrue(
            self.config.is_normalization_enabled()
        )

    def test_invalid_weight_total_is_rejected(self):
        invalid_config = {
            "parameters": {
                "answer_relevance": {
                    "weight": 0.50
                },
                "communication": {
                    "weight": 0.20
                },
                "confidence": {
                    "weight": 0.10
                },
                "consistency": {
                    "weight": 0.10
                }
            }
        }

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8"
        ) as file:
            json.dump(
                invalid_config,
                file
            )
            temp_path = file.name

        try:
            with self.assertRaises(
                ValueError
            ):
                HRScoringConfig(temp_path)
        finally:
            Path(temp_path).unlink(
                missing_ok=True
            )

    def test_missing_parameter_is_rejected(self):
        invalid_config = {
            "parameters": {
                "answer_relevance": {
                    "weight": 0.30
                },
                "communication": {
                    "weight": 0.25
                },
                "confidence": {
                    "weight": 0.20
                }
            }
        }

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8"
        ) as file:
            json.dump(
                invalid_config,
                file
            )
            temp_path = file.name

        try:
            with self.assertRaises(
                ValueError
            ):
                HRScoringConfig(temp_path)
        finally:
            Path(temp_path).unlink(
                missing_ok=True
            )


if __name__ == "__main__":
    unittest.main()