import unittest

from interview_ai.hr.stress_indicator_analyzer import (
    StressIndicatorAnalyzer
)


class TestDay36StressIndicatorAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = StressIndicatorAnalyzer()

    def test_normal_response_has_low_stress(self):
        result = self.analyzer.analyze(
            "I worked on Python and Django projects."
        )

        self.assertEqual(
            result["stress_level"],
            "low"
        )

        self.assertEqual(
            result["stress_count"],
            0
        )

    def test_stress_word_is_detected(self):
        result = self.analyzer.analyze(
            "I was nervous about the interview."
        )

        self.assertIn(
            "nervous",
            result["stress_words"]
        )

        self.assertIn(
            "stress_language",
            result["stress_indicators"]
        )

    def test_hesitation_is_detected(self):
        result = self.analyzer.analyze(
            "Um, I am not sure about that."
        )

        self.assertIn(
            "um",
            result["hesitation_words"]
        )

        self.assertIn(
            "hesitation",
            result["stress_indicators"]
        )

    def test_repeated_words_are_detected(self):
        result = self.analyzer.analyze(
            "I worked worked on Python."
        )

        self.assertIn(
            "worked",
            result["repeated_words"]
        )

        self.assertIn(
            "repeated_words",
            result["stress_indicators"]
        )

    def test_long_pause_is_detected(self):
        result = self.analyzer.analyze(
            "I worked on Python.",
            {
                "pause_duration_seconds": 3
            }
        )

        self.assertTrue(
            result["long_pause_detected"]
        )

        self.assertIn(
            "long_pause",
            result["stress_indicators"]
        )

    def test_moderate_stress(self):
        result = self.analyzer.analyze(
            "I was nervous and um not sure."
        )

        self.assertEqual(
            result["stress_level"],
            "moderate"
        )

    def test_high_stress(self):
        result = self.analyzer.analyze(
            "I was nervous um worried and stressed."
        )

        self.assertEqual(
            result["stress_level"],
            "high"
        )

    def test_empty_response_is_safe(self):
        result = self.analyzer.analyze("")

        self.assertEqual(
            result["stress_level"],
            "low"
        )

        self.assertEqual(
            result["stress_count"],
            0
        )

    def test_invalid_metadata_is_safe(self):
        result = self.analyzer.analyze(
            "I worked on Python.",
            {
                "pause_duration_seconds": "invalid"
            }
        )

        self.assertFalse(
            result["long_pause_detected"]
        )

    def test_stress_count_is_returned(self):
        result = self.analyzer.analyze(
            "I am nervous about this."
        )

        self.assertGreaterEqual(
            result["stress_count"],
            1
        )


if __name__ == "__main__":
    unittest.main()