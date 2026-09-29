import unittest

from interview_ai.hr.hr_interview_engine import (
    HRInterviewEngine
)


class TestDay37HRScoringIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = HRInterviewEngine(
            session_id="test_session",
            candidate_id="test_candidate",
            role="Software Engineer",
            candidate_type="fresher",
            role_type="technical"
        )

    def test_hr_score_is_calculated(self):
        question_scores = [
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
        ]

        result = self.engine.calculate_hr_interview_score(
            question_scores
        )

        self.assertIn(
            "final_score",
            result
        )

        self.assertIn(
            "normalized_scores",
            result
        )

        self.assertIn(
            "breakdown",
            result
        )

    def test_score_is_between_zero_and_hundred(self):
        question_scores = [
            {
                "answer_relevance": 90,
                "communication": 85,
                "confidence": 80,
                "consistency": 95
            }
        ]

        result = self.engine.calculate_hr_interview_score(
            question_scores
        )

        self.assertGreaterEqual(
            result["final_score"],
            0
        )

        self.assertLessEqual(
            result["final_score"],
            100
        )

    def test_all_parameters_are_present(self):
        question_scores = [
            {
                "answer_relevance": 80,
                "communication": 90,
                "confidence": 70,
                "consistency": 85
            }
        ]

        result = self.engine.calculate_hr_interview_score(
            question_scores
        )

        self.assertEqual(
            set(result["normalized_scores"].keys()),
            {
                "answer_relevance",
                "communication",
                "confidence",
                "consistency"
            }
        )

    def test_interview_length_normalization(self):
        short_interview = [
            {
                "answer_relevance": 80,
                "communication": 80,
                "confidence": 80,
                "consistency": 80
            }
        ]

        long_interview = [
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
        ]

        short_result = (
            self.engine.calculate_hr_interview_score(
                short_interview
            )
        )

        long_result = (
            self.engine.calculate_hr_interview_score(
                long_interview
            )
        )

        self.assertEqual(
            short_result["final_score"],
            long_result["final_score"]
        )

    def test_breakdown_is_explainable(self):
        question_scores = [
            {
                "answer_relevance": 80,
                "communication": 90,
                "confidence": 70,
                "consistency": 85
            }
        ]

        result = self.engine.calculate_hr_interview_score(
            question_scores
        )

        self.assertEqual(
            len(result["breakdown"]),
            4
        )

        for item in result["breakdown"]:
            self.assertIn(
                "parameter",
                item
            )

            self.assertIn(
                "score",
                item
            )

            self.assertIn(
                "weight",
                item
            )

            self.assertIn(
                "contribution",
                item
            )


if __name__ == "__main__":
    unittest.main()