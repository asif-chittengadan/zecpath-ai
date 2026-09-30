import unittest

from interview_ai.hr.hr_manual_evaluation_comparator import (
    HRManualEvaluationComparator
)


class TestDay40ManualEvaluationComparator(unittest.TestCase):

    def setUp(self):
        self.comparator = HRManualEvaluationComparator()

    def test_matching_scores(self):
        ai_scores = {
            "answer_relevance": 80,
            "communication": 75,
            "confidence": 70,
            "consistency": 85
        }

        manual_scores = {
            "answer_relevance": 80,
            "communication": 75,
            "confidence": 70,
            "consistency": 85
        }

        result = self.comparator.compare(
            ai_scores,
            manual_scores
        )

        self.assertEqual(
            result["average_difference"],
            0
        )

        self.assertTrue(
            result["all_within_tolerance"]
        )

    def test_small_difference_within_tolerance(self):
        ai_scores = {
            "answer_relevance": 80,
            "communication": 75,
            "confidence": 70,
            "consistency": 85
        }

        manual_scores = {
            "answer_relevance": 84,
            "communication": 77,
            "confidence": 72,
            "consistency": 81
        }

        result = self.comparator.compare(
            ai_scores,
            manual_scores,
            tolerance=5
        )

        self.assertTrue(
            result["all_within_tolerance"]
        )

        self.assertEqual(
            result["inconsistency_count"],
            0
        )

    def test_large_difference_detected(self):
        ai_scores = {
            "answer_relevance": 80,
            "communication": 75,
            "confidence": 70,
            "consistency": 85
        }

        manual_scores = {
            "answer_relevance": 60,
            "communication": 75,
            "confidence": 50,
            "consistency": 85
        }

        result = self.comparator.compare(
            ai_scores,
            manual_scores,
            tolerance=5
        )

        self.assertFalse(
            result["all_within_tolerance"]
        )

        self.assertEqual(
            result["inconsistency_count"],
            2
        )

        self.assertIn(
            "answer_relevance",
            result["inconsistent_parameters"]
        )

        self.assertIn(
            "confidence",
            result["inconsistent_parameters"]
        )

    def test_difference_is_calculated_correctly(self):
        ai_scores = {
            "answer_relevance": 80,
            "communication": 70,
            "confidence": 60,
            "consistency": 90
        }

        manual_scores = {
            "answer_relevance": 75,
            "communication": 80,
            "confidence": 60,
            "consistency": 85
        }

        result = self.comparator.compare(
            ai_scores,
            manual_scores
        )

        self.assertEqual(
            result["comparison"][
                "answer_relevance"
            ]["difference"],
            5
        )

        self.assertEqual(
            result["comparison"][
                "communication"
            ]["difference"],
            10
        )

        self.assertEqual(
            result["comparison"][
                "confidence"
            ]["difference"],
            0
        )

        self.assertEqual(
            result["comparison"][
                "consistency"
            ]["difference"],
            5
        )

    def test_custom_tolerance(self):
        ai_scores = {
            "answer_relevance": 80,
            "communication": 75,
            "confidence": 70,
            "consistency": 85
        }

        manual_scores = {
            "answer_relevance": 88,
            "communication": 75,
            "confidence": 70,
            "consistency": 85
        }

        result = self.comparator.compare(
            ai_scores,
            manual_scores,
            tolerance=10
        )

        self.assertTrue(
            result["all_within_tolerance"]
        )


if __name__ == "__main__":
    unittest.main()