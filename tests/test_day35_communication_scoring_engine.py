import unittest

from interview_ai.hr.communication_scoring_engine import (
    CommunicationScoringEngine
)


class TestDay35CommunicationScoringEngine(unittest.TestCase):

    def setUp(self):
        self.engine = CommunicationScoringEngine()

    def test_perfect_features_produce_100(self):
        features = {
            "fluency": 100,
            "grammar_quality": 100,
            "vocabulary_range": 100,
            "clarity": 100,
            "answer_structure": 100,
            "filler_word_count": 0
        }

        result = self.engine.score(features)

        self.assertEqual(
            result["score"],
            100
        )

    def test_zero_features_produce_zero(self):
        features = {
            "fluency": 0,
            "grammar_quality": 0,
            "vocabulary_range": 0,
            "clarity": 0,
            "answer_structure": 0,
            "filler_word_count": 10
        }

        result = self.engine.score(features)

        self.assertEqual(
            result["score"],
            0
        )

    def test_weighted_score(self):
        features = {
            "fluency": 80,
            "grammar_quality": 80,
            "vocabulary_range": 60,
            "clarity": 90,
            "answer_structure": 70,
            "filler_word_count": 0
        }

        result = self.engine.score(features)

        expected = (
            (80 * 0.20)
            + (80 * 0.20)
            + (60 * 0.15)
            + (90 * 0.20)
            + (70 * 0.15)
            + (100 * 0.10)
        )

        self.assertEqual(
            result["score"],
            round(expected, 2)
        )

    def test_filler_control_without_fillers(self):
        features = {
            "filler_word_count": 0
        }

        result = self.engine.score(features)

        self.assertEqual(
            result["components"]["filler_control"],
            100
        )

    def test_filler_control_with_fillers(self):
        features = {
            "filler_word_count": 3
        }

        result = self.engine.score(features)

        self.assertEqual(
            result["components"]["filler_control"],
            70
        )

    def test_filler_penalty_is_bounded(self):
        features = {
            "filler_word_count": 20
        }

        result = self.engine.score(features)

        self.assertEqual(
            result["components"]["filler_control"],
            0
        )

    def test_missing_features_are_safe(self):
        result = self.engine.score({})

        self.assertEqual(
            result["score"],
            10
        )

    def test_scores_are_bounded(self):
        features = {
            "fluency": 500,
            "grammar_quality": -50,
            "vocabulary_range": 200,
            "clarity": 150,
            "answer_structure": -20,
            "filler_word_count": 0
        }

        result = self.engine.score(features)

        self.assertGreaterEqual(
            result["score"],
            0
        )

        self.assertLessEqual(
            result["score"],
            100
        )

    def test_formula_is_returned(self):
        features = {
            "fluency": 50
        }

        result = self.engine.score(features)

        self.assertIn(
            "Fluency",
            result["formula"]
        )

        self.assertIn(
            "Filler Control",
            result["formula"]
        )


if __name__ == "__main__":
    unittest.main()