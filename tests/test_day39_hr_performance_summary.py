import unittest

from interview_ai.hr.hr_performance_summary import (
    HRPerformanceSummary
)


class TestDay39HRPerformanceSummary(unittest.TestCase):

    def setUp(self):
        self.summary = HRPerformanceSummary()

    def test_generates_summary(self):
        result = self.summary.generate(
            overall_score=82,
            component_scores={
                "answer_relevance": 85,
                "communication": 80,
                "confidence": 78,
                "consistency": 86
            }
        )

        self.assertEqual(
            result["overall_score"],
            82
        )

        self.assertEqual(
            result["performance_level"],
            "high"
        )

        self.assertEqual(
            result["component_count"],
            4
        )

    def test_high_performance(self):
        result = self.summary.generate(
            overall_score=90
        )

        self.assertEqual(
            result["performance_level"],
            "high"
        )

    def test_moderate_performance(self):
        result = self.summary.generate(
            overall_score=60
        )

        self.assertEqual(
            result["performance_level"],
            "moderate"
        )

    def test_low_performance(self):
        result = self.summary.generate(
            overall_score=30
        )

        self.assertEqual(
            result["performance_level"],
            "low"
        )

    def test_very_low_performance(self):
        result = self.summary.generate(
            overall_score=10
        )

        self.assertEqual(
            result["performance_level"],
            "very_low"
        )

    def test_score_is_bounded(self):
        high = self.summary.generate(
            overall_score=150
        )

        low = self.summary.generate(
            overall_score=-20
        )

        self.assertEqual(
            high["overall_score"],
            100
        )

        self.assertEqual(
            low["overall_score"],
            0
        )

    def test_invalid_score(self):
        result = self.summary.generate(
            overall_score="invalid"
        )

        self.assertIsNone(
            result["overall_score"]
        )

        self.assertEqual(
            result["performance_level"],
            "not_available"
        )

    def test_invalid_component_scores(self):
        result = self.summary.generate(
            overall_score=70,
            component_scores="invalid"
        )

        self.assertEqual(
            result["component_scores"],
            {}
        )

        self.assertEqual(
            result["component_count"],
            0
        )


if __name__ == "__main__":
    unittest.main()