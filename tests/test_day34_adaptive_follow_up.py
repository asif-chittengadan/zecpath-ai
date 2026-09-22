import unittest

from interview_ai.hr.adaptive_follow_up_engine import (
    AdaptiveFollowUpEngine
)


class TestDay34AdaptiveFollowUp(unittest.TestCase):

    def setUp(self):
        self.engine = AdaptiveFollowUpEngine()

    def test_incomplete_triggers_clarification(self):
        analysis = {
            "classification": "incomplete"
        }

        result = self.engine.decide(
            analysis,
            "career_journey"
        )

        self.assertEqual(
            result["trigger"],
            "clarification"
        )

        self.assertTrue(
            result["follow_up_required"]
        )

    def test_vague_triggers_deepening(self):
        analysis = {
            "classification": "vague"
        }

        result = self.engine.decide(
            analysis,
            "teamwork_culture_fit"
        )

        self.assertEqual(
            result["trigger"],
            "deepening"
        )

        self.assertTrue(
            result["follow_up_required"]
        )

    def test_complete_behavioral_answer_gets_example(self):
        analysis = {
            "classification": "complete"
        }

        result = self.engine.decide(
            analysis,
            "strengths_weaknesses"
        )

        self.assertEqual(
            result["trigger"],
            "example_based"
        )

        self.assertTrue(
            result["follow_up_required"]
        )

    def test_complete_non_behavioral_answer_moves_forward(self):
        analysis = {
            "classification": "complete"
        }

        result = self.engine.decide(
            analysis,
            "availability_commitment"
        )

        self.assertEqual(
            result["trigger"],
            "none"
        )

        self.assertFalse(
            result["follow_up_required"]
        )

        self.assertIsNone(
            result["question"]
        )

    def test_confident_response_gets_scenario_question(self):
        analysis = {
            "classification": "confident"
        }

        result = self.engine.decide(
            analysis,
            "teamwork_culture_fit"
        )

        self.assertEqual(
            result["trigger"],
            "scenario_based"
        )

        self.assertTrue(
            result["follow_up_required"]
        )

        self.assertIsNotNone(
            result["question"]
        )

    def test_category_normalization(self):
        analysis = {
            "classification": "vague"
        }

        result = self.engine.decide(
            analysis,
            "Teamwork Culture Fit"
        )

        self.assertEqual(
            result["question"],
            "What was your specific responsibility in that situation?"
        )

    def test_unknown_classification_safe_fallback(self):
        analysis = {
            "classification": "unknown"
        }

        result = self.engine.decide(
            analysis,
            "career_goals"
        )

        self.assertEqual(
            result["trigger"],
            "clarification"
        )

        self.assertTrue(
            result["follow_up_required"]
        )


if __name__ == "__main__":
    unittest.main()