import unittest

from interview_ai.hr.behavioral_confidence_engine import (
    BehavioralConfidenceEngine
)


class TestDay36BehavioralConfidenceEngine(unittest.TestCase):

    def setUp(self):
        self.engine = BehavioralConfidenceEngine()

    def test_clean_response_has_high_signal(self):
        result = self.engine.calculate(
            confidence_result={
                "hesitation_count": 0
            },
            sentiment_result={
                "sentiment": "positive"
            },
            contradiction_result={
                "count": 0
            },
            stress_result={
                "stress_level": "low"
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            100
        )

        self.assertEqual(
            result["interpretation"],
            "high_signal"
        )

    def test_hesitation_reduces_score(self):
        result = self.engine.calculate(
            confidence_result={
                "hesitation_count": 2
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            90
        )

    def test_contradiction_reduces_score(self):
        result = self.engine.calculate(
            contradiction_result={
                "count": 2
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            80
        )

    def test_moderate_stress_reduces_score(self):
        result = self.engine.calculate(
            stress_result={
                "stress_level": "moderate"
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            93
        )

    def test_high_stress_reduces_score(self):
        result = self.engine.calculate(
            stress_result={
                "stress_level": "high"
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            85
        )

    def test_negative_sentiment_reduces_score(self):
        result = self.engine.calculate(
            sentiment_result={
                "sentiment": "negative"
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            95
        )

    def test_positive_sentiment_bonus(self):
        result = self.engine.calculate(
            sentiment_result={
                "sentiment": "positive"
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            100
        )

    def test_combined_signals(self):
        result = self.engine.calculate(
            confidence_result={
                "hesitation_count": 2
            },
            sentiment_result={
                "sentiment": "negative"
            },
            contradiction_result={
                "count": 1
            },
            stress_result={
                "stress_level": "moderate"
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            68
        )

    def test_score_is_bounded(self):
        result = self.engine.calculate(
            confidence_result={
                "hesitation_count": 100
            },
            contradiction_result={
                "count": 100
            },
            sentiment_result={
                "sentiment": "negative"
            },
            stress_result={
                "stress_level": "high"
            }
        )

        self.assertEqual(
            result["behavioral_confidence_score"],
            0
        )

    def test_missing_inputs_are_safe(self):
        result = self.engine.calculate()

        self.assertEqual(
            result["behavioral_confidence_score"],
            100
        )

        self.assertIn(
            "interpretation",
            result
        )


if __name__ == "__main__":
    unittest.main()