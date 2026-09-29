import unittest

from interview_ai.hr.hr_score_normalizer import (
    HRScoreNormalizer
)


class TestHRScoreNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = HRScoreNormalizer()

    def test_single_question(self):
        result = self.normalizer.normalize([
            {
                "answer_relevance": 80,
                "communication": 90,
                "confidence": 70,
                "consistency": 85
            }
        ])

        self.assertEqual(
            result["answered_questions"],
            1
        )

        self.assertEqual(
            result["normalized_scores"]["answer_relevance"],
            80.0
        )

    def test_multiple_questions_are_averaged(self):
        result = self.normalizer.normalize([
            {
                "answer_relevance": 80,
                "communication": 90,
                "confidence": 70,
                "consistency": 85
            },
            {
                "answer_relevance": 60,
                "communication": 80,
                "confidence": 90,
                "consistency": 75
            }
        ])

        self.assertEqual(
            result["normalized_scores"]["answer_relevance"],
            70.0
        )

        self.assertEqual(
            result["normalized_scores"]["communication"],
            85.0
        )

        self.assertEqual(
            result["normalized_scores"]["confidence"],
            80.0
        )

        self.assertEqual(
            result["normalized_scores"]["consistency"],
            80.0
        )

    def test_interview_length_does_not_change_average(self):
        short_interview = self.normalizer.normalize([
            {
                "answer_relevance": 80,
                "communication": 80,
                "confidence": 80,
                "consistency": 80
            }
        ])

        long_interview = self.normalizer.normalize([
            {
                "answer_relevance": 80,
                "communication": 80,
                "confidence": 80,
                "consistency": 80
            },
            {
                "answer_relevance": 80,
                "communication": 80,
                "confidence": 80,
                "consistency": 80
            },
            {
                "answer_relevance": 80,
                "communication": 80,
                "confidence": 80,
                "consistency": 80
            }
        ])

        self.assertEqual(
            short_interview["normalized_scores"],
            long_interview["normalized_scores"]
        )

    def test_empty_interview_is_safe(self):
        result = self.normalizer.normalize([])

        self.assertEqual(
            result["answered_questions"],
            0
        )

        self.assertEqual(
            result["normalized_scores"]["answer_relevance"],
            0.0
        )

    def test_scores_are_bounded(self):
        result = self.normalizer.normalize([
            {
                "answer_relevance": 150,
                "communication": -20,
                "confidence": 120,
                "consistency": -10
            }
        ])

        self.assertEqual(
            result["normalized_scores"]["answer_relevance"],
            100.0
        )

        self.assertEqual(
            result["normalized_scores"]["communication"],
            0.0
        )

        self.assertEqual(
            result["normalized_scores"]["confidence"],
            100.0
        )

        self.assertEqual(
            result["normalized_scores"]["consistency"],
            0.0
        )

    def test_completion_ratio_for_answered_questions(self):
        result = self.normalizer.normalize([
            {
                "answer_relevance": 80,
                "communication": 80,
                "confidence": 80,
                "consistency": 80
            }
        ])

        self.assertEqual(
            result["completion_ratio"],
            1.0
        )


if __name__ == "__main__":
    unittest.main()