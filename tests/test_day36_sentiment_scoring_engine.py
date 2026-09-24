import unittest

from interview_ai.hr.sentiment_scoring_engine import (
    SentimentScoringEngine
)


class TestDay36SentimentScoringEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SentimentScoringEngine()

    def test_positive_response(self):
        result = self.engine.analyze(
            "I am confident, motivated and excited about this role."
        )

        self.assertEqual(
            result["sentiment"],
            "positive"
        )

        self.assertGreater(
            result["score"],
            50
        )

    def test_negative_response(self):
        result = self.engine.analyze(
            "I am worried and nervous about the difficult situation."
        )

        self.assertEqual(
            result["sentiment"],
            "negative"
        )

        self.assertLess(
            result["score"],
            50
        )

    def test_neutral_response(self):
        result = self.engine.analyze(
            "I worked on a Python project during my degree."
        )

        self.assertEqual(
            result["sentiment"],
            "neutral"
        )

        self.assertEqual(
            result["score"],
            50
        )

    def test_positive_words_are_detected(self):
        result = self.engine.analyze(
            "I successfully learned Python and improved my skills."
        )

        self.assertIn(
            "learned",
            result["positive_words"]
        )

        self.assertIn(
            "improved",
            result["positive_words"]
        )

    def test_negative_words_are_detected(self):
        result = self.engine.analyze(
            "I was confused and frustrated by the problem."
        )

        self.assertIn(
            "confused",
            result["negative_words"]
        )

        self.assertIn(
            "frustrated",
            result["negative_words"]
        )

    def test_mixed_sentiment(self):
        result = self.engine.analyze(
            "I am confident but also nervous about the interview."
        )

        self.assertEqual(
            result["positive_count"],
            1
        )

        self.assertEqual(
            result["negative_count"],
            1
        )

        self.assertEqual(
            result["sentiment"],
            "neutral"
        )

        self.assertEqual(
            result["score"],
            50
        )

    def test_empty_response_is_safe(self):
        result = self.engine.analyze("")

        self.assertEqual(
            result["sentiment"],
            "neutral"
        )

        self.assertEqual(
            result["score"],
            50
        )

    def test_score_is_bounded(self):
        responses = [
            "confident motivated successful",
            "worried nervous failure",
            "I worked on Python"
        ]

        for response in responses:
            result = self.engine.analyze(
                response
            )

            self.assertGreaterEqual(
                result["score"],
                0
            )

            self.assertLessEqual(
                result["score"],
                100
            )

    def test_punctuation_is_handled(self):
        result = self.engine.analyze(
            "Great! I am confident, motivated, and excited."
        )

        self.assertIn(
            "great",
            result["positive_words"]
        )

        self.assertIn(
            "confident",
            result["positive_words"]
        )


if __name__ == "__main__":
    unittest.main()