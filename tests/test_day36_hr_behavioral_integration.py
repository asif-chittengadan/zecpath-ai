import unittest

from interview_ai.hr.hr_interview_engine import (
    HRInterviewEngine
)


class TestDay36HRBehavioralIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = HRInterviewEngine(
            session_id="DAY36-BEH-001",
            candidate_id="CAND-036",
            role="Software Developer",
            candidate_type="fresher",
            role_type="technical"
        )

    def test_behavioral_analysis_is_available(self):
        result = self.engine.analyze_behavioral_signals(
            "I am confident and motivated about this role."
        )

        self.assertIn(
            "confidence",
            result
        )

        self.assertIn(
            "sentiment",
            result
        )

        self.assertIn(
            "contradiction",
            result
        )

        self.assertIn(
            "stress",
            result
        )

        self.assertIn(
            "behavioral_confidence",
            result
        )

    def test_confidence_analysis_is_integrated(self):
        result = self.engine.analyze_behavioral_signals(
            "Um, I think I can probably do this."
        )

        self.assertGreater(
            result["confidence"]["hesitation_count"],
            0
        )

    def test_sentiment_analysis_is_integrated(self):
        result = self.engine.analyze_behavioral_signals(
            "I am confident and motivated about this opportunity."
        )

        self.assertEqual(
            result["sentiment"]["sentiment"],
            "positive"
        )

    def test_contradiction_analysis_is_integrated(self):
        result = self.engine.analyze_behavioral_signals(
            "I have three years of experience.",
            {
                "experience_years": 2
            }
        )

        self.assertTrue(
            result["contradiction"][
                "contradiction_detected"
            ]
        )

    def test_stress_analysis_is_integrated(self):
        result = self.engine.analyze_behavioral_signals(
            "I was nervous about the interview.",
            metadata={
                "pause_duration_seconds": 3
            }
        )

        self.assertIn(
            "stress_language",
            result["stress"]["stress_indicators"]
        )

        self.assertTrue(
            result["stress"]["long_pause_detected"]
        )

    def test_behavioral_score_is_generated(self):
        result = self.engine.analyze_behavioral_signals(
            "I am confident and motivated about this role."
        )

        score = result[
            "behavioral_confidence"
        ]["behavioral_confidence_score"]

        self.assertGreaterEqual(
            score,
            0
        )

        self.assertLessEqual(
            score,
            100
        )

    def test_behavioral_history_is_stored(self):
        self.engine.analyze_behavioral_signals(
            "I worked on Python projects."
        )

        history = (
            self.engine.get_behavioral_history()
        )

        self.assertEqual(
            len(history),
            1
        )

    def test_multiple_behavioral_analyses_are_tracked(self):
        self.engine.analyze_behavioral_signals(
            "I worked on Python projects."
        )

        self.engine.analyze_behavioral_signals(
            "I am motivated to learn new technologies."
        )

        history = (
            self.engine.get_behavioral_history()
        )

        self.assertEqual(
            len(history),
            2
        )

    def test_empty_response_is_safe(self):
        result = self.engine.analyze_behavioral_signals(
            ""
        )

        self.assertIn(
            "behavioral_confidence",
            result
        )

        score = result[
            "behavioral_confidence"
        ]["behavioral_confidence_score"]

        self.assertGreaterEqual(
            score,
            0
        )

        self.assertLessEqual(
            score,
            100
        )


if __name__ == "__main__":
    unittest.main()