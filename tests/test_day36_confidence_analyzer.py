import unittest

from interview_ai.hr.confidence_analyzer import (
    ConfidenceAnalyzer
)


class TestDay36ConfidenceAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = ConfidenceAnalyzer()

    def test_normal_response_has_no_hesitation(self):
        result = self.analyzer.analyze(
            "I worked on Python projects during my degree."
        )

        self.assertFalse(
            result["long_pause_detected"]
        )

        self.assertEqual(
            result["repeated_words"],
            []
        )

        self.assertEqual(
            result["uncertainty_phrases"],
            []
        )

    def test_long_pause_is_detected(self):
        result = self.analyzer.analyze(
            "I worked on Python projects.",
            {
                "pause_duration_seconds": 3.0
            }
        )

        self.assertTrue(
            result["long_pause_detected"]
        )

    def test_short_pause_is_not_long_pause(self):
        result = self.analyzer.analyze(
            "I worked on Python projects.",
            {
                "pause_duration_seconds": 1.0
            }
        )

        self.assertFalse(
            result["long_pause_detected"]
        )

    def test_repeated_words_are_detected(self):
        result = self.analyzer.analyze(
            "I worked worked on Python projects."
        )

        self.assertIn(
            "worked",
            result["repeated_words"]
        )

    def test_uncertainty_phrase_is_detected(self):
        result = self.analyzer.analyze(
            "I think I can probably handle this role."
        )

        self.assertIn(
            "i think",
            result["uncertainty_phrases"]
        )

        self.assertIn(
            "probably",
            result["uncertainty_phrases"]
        )

    def test_hesitation_words_are_detected(self):
        result = self.analyzer.analyze(
            "Um, I worked on a Python project."
        )

        self.assertIn(
            "um",
            result["hesitation_words"]
        )

    def test_hesitation_count_is_calculated(self):
        result = self.analyzer.analyze(
            "Um, I think I worked worked on Python.",
            {
                "pause_duration_seconds": 3
            }
        )

        self.assertGreaterEqual(
            result["hesitation_count"],
            3
        )

    def test_confidence_indicators_are_generated(self):
        result = self.analyzer.analyze(
            "I think I can probably do this."
        )

        self.assertIn(
            "uncertainty_language",
            result["confidence_indicators"]
        )

    def test_empty_response_is_safe(self):
        result = self.analyzer.analyze("")

        self.assertFalse(
            result["long_pause_detected"]
        )

        self.assertEqual(
            result["repeated_words"],
            []
        )

        self.assertEqual(
            result["uncertainty_phrases"],
            []
        )

        self.assertEqual(
            result["hesitation_count"],
            0
        )

    def test_invalid_pause_metadata_is_safe(self):
        result = self.analyzer.analyze(
            "I worked on Python.",
            {
                "pause_duration_seconds": "invalid"
            }
        )

        self.assertFalse(
            result["long_pause_detected"]
        )


if __name__ == "__main__":
    unittest.main()