import unittest
from pathlib import Path

from screening_ai.conversation_flow import ConversationFlowEngine, ConversationState


BASE_DIR = Path(__file__).resolve().parents[1]


class TestDay31ConversationIntegration(unittest.TestCase):

    def setUp(self):
        self.questions = [
            {
                "category": "Experience",
                "question": "How many years of experience do you have?",
                "fallback_question": "Could you tell me your total work experience in years?"
            },
            {
                "category": "Skills",
                "question": "Which technologies are you comfortable using?",
                "fallback_question": "Could you name one or two technologies you have worked with?"
            }
        ]

        def analyzer(answer, category, previous_answers):
            return {
                "valid": True,
                "confused": False,
                "repeated": False,
                "follow_up": False,
                "reason": "",
            }

        self.engine = ConversationFlowEngine(
            rules_path=str(BASE_DIR / "config" / "conversation_flow_rules.json"),
            answer_analyzer=analyzer,
            edge_case_rules_path=str(BASE_DIR / "config" / "edge_case_rules.json"),
        )
        self.context = self.engine.start(
            "D31-SESSION",
            "D31-CANDIDATE",
            self.questions,
        )

    def test_valid_response_continues_normal_flow(self):
        result = self.engine.receive_response(
            self.context,
            "I have two years of experience.",
            {"audio_confidence": 0.95, "noise_score": 0.10},
        )
        self.assertEqual(result["action"], "next_question")
        self.assertEqual(result["answers_count"], 1)

    def test_poor_audio_retry(self):
        result = self.engine.receive_response(
            self.context,
            "I have two years of experience.",
            {"audio_confidence": 0.30},
        )
        self.assertEqual(result["action"], "retry")

    def test_background_noise_retry(self):
        result = self.engine.receive_response(
            self.context,
            "I have two years of experience.",
            {"noise_score": 0.95},
        )
        self.assertEqual(result["action"], "retry")

    def test_missing_answer_retry(self):
        result = self.engine.receive_response(self.context, "", {})
        self.assertEqual(result["action"], "retry")

    def test_language_mixing_clarification(self):
        result = self.engine.receive_response(
            self.context,
            "Haan, I have two years of experience.",
            {"language_mixed": True},
        )
        self.assertEqual(result["action"], "clarify")

    def test_retry_limit_safe_fallback(self):
        for _ in range(2):
            self.engine.receive_response(
                self.context,
                "I have two years of experience.",
                {"audio_confidence": 0.20},
            )

        result = self.engine.receive_response(
            self.context,
            "I have two years of experience.",
            {"audio_confidence": 0.20},
        )
        self.assertEqual(result["action"], "safe_fallback")

    def test_day29_compatibility_without_edge_handler(self):
        def analyzer(answer, category, previous_answers):
            return {
                "valid": True,
                "confused": False,
                "repeated": False,
                "follow_up": False,
                "reason": "",
            }

        legacy = ConversationFlowEngine(
            rules_path=str(BASE_DIR / "config" / "conversation_flow_rules.json"),
            answer_analyzer=analyzer,
        )
        context = legacy.start("LEGACY", "CANDIDATE", self.questions)
        result = legacy.receive_response(context, "")
        self.assertEqual(result["action"], "retry")
        self.assertEqual(context.state, ConversationState.RETRY)


if __name__ == "__main__":
    unittest.main()
