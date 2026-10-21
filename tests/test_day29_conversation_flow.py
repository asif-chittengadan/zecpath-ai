import unittest

from screening_ai.conversation_flow import ConversationFlowEngine, ConversationState


QUESTIONS = [
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


class TestDay29ConversationFlow(unittest.TestCase):

    def setUp(self):
        self.engine = ConversationFlowEngine(
            rules_path="config/conversation_flow_rules.json"
        )
        self.context = self.engine.start(
            session_id="TEST-SESSION",
            candidate_id="TEST-CANDIDATE",
            questions=QUESTIONS,
        )

    def test_start_state(self):
        self.assertEqual(self.context.state, ConversationState.ASK_QUESTION)
        self.assertEqual(self.engine.next_prompt(self.context), QUESTIONS[0]["question"])

    def test_normal_response_moves_to_next_question(self):
        result = self.engine.receive_response(self.context, "I have two years of experience.")
        self.assertEqual(result["action"], "next_question")
        self.assertEqual(self.context.current_index, 1)

    def test_silence_retry(self):
        result = self.engine.receive_response(self.context, "")
        self.assertEqual(result["action"], "retry")
        self.assertEqual(self.context.state, ConversationState.RETRY)

    def test_silence_reaches_fallback(self):
        self.engine.receive_response(self.context, "")
        self.engine.receive_response(self.context, "")
        result = self.engine.receive_response(self.context, "")
        self.assertEqual(result["action"], "fallback")
        self.assertIn("total work experience", result["prompt"])

    def test_confusion(self):
        result = self.engine.receive_response(self.context, "I don't understand.")
        self.assertEqual(result["action"], "clarify")
        self.assertEqual(self.context.state, ConversationState.RETRY)

    def test_repeated_answer(self):
        self.engine.receive_response(self.context, "I have two years of experience.")
        result = self.engine.receive_response(self.context, "I have two years of experience.")
        self.assertEqual(result["action"], "redirect")
        self.assertEqual(self.context.state, ConversationState.RETRY)

    def test_fallback_question(self):
        analyzer = lambda text, category, previous: {
            "valid": False,
            "confused": False,
            "repeated": False,
            "reason": "off_topic"
        }
        engine = ConversationFlowEngine(
            rules_path="config/conversation_flow_rules.json",
            answer_analyzer=analyzer,
        )
        context = engine.start("S", "C", QUESTIONS)
        result = engine.receive_response(context, "I like football.")
        self.assertEqual(result["action"], "fallback")
        self.assertIn("total work experience", result["prompt"])

    def test_follow_up_trigger(self):
        analyzer = lambda text, category, previous: {
            "valid": True,
            "confused": False,
            "repeated": False,
            "follow_up": True,
            "follow_up_question": "Could you describe one of those projects?"
        }
        engine = ConversationFlowEngine(
            rules_path="config/conversation_flow_rules.json",
            answer_analyzer=analyzer,
        )
        context = engine.start("S", "C", QUESTIONS)
        result = engine.receive_response(context, "I have two years of Python experience.")
        self.assertEqual(result["action"], "ask_follow_up")
        self.assertEqual(
            result["prompt"],
            "Could you describe one of those projects?"
        )
        self.assertEqual(context.state, ConversationState.ASK_FOLLOW_UP)

    def test_follow_up_answer_uses_the_dynamic_question_that_was_shown(self):
        follow_up_question = "Could you describe one of those projects?"
        analyzer = lambda text, category, previous: {
            "valid": True,
            "confused": False,
            "repeated": False,
            "follow_up": True,
            "follow_up_question": follow_up_question,
        }
        engine = ConversationFlowEngine(
            rules_path="config/conversation_flow_rules.json",
            answer_analyzer=analyzer,
        )
        context = engine.start("S", "C", QUESTIONS)

        first = engine.receive_response(context, "I built two Python projects.")
        self.assertEqual(first["prompt"], follow_up_question)

        # Use the normal response method to ensure a shared API caller does
        # not store the follow-up reply as a second main-question answer.
        result = engine.receive_response(context, "One was a reporting API.")

        self.assertEqual(result["action"], "next_question")
        self.assertEqual(context.answers[1]["question"], follow_up_question)
        self.assertTrue(context.answers[1]["is_follow_up"])
        self.assertEqual(context.answers[1]["answer"], "One was a reporting API.")
        self.assertIsNone(context.pending_follow_up_question)

    def test_follow_up_reply_after_silence_retry_stays_attached(self):
        follow_up_question = "Could you describe one of those projects?"
        analyzer = lambda text, category, previous: {
            "valid": True,
            "follow_up": True,
            "follow_up_question": follow_up_question,
        }
        engine = ConversationFlowEngine(
            rules_path="config/conversation_flow_rules.json",
            answer_analyzer=analyzer,
        )
        context = engine.start("S", "C", QUESTIONS)

        engine.receive_response(context, "I built two Python projects.")
        retry = engine.receive_response(context, "")
        self.assertEqual(retry["action"], "retry")

        result = engine.receive_response(context, "One was a reporting API.")

        self.assertEqual(result["action"], "next_question")
        self.assertEqual(context.answers[1]["question"], follow_up_question)
        self.assertTrue(context.answers[1]["is_follow_up"])

    def test_follow_up_cannot_be_submitted_when_none_is_pending(self):
        result = self.engine.submit_follow_up(self.context, "Unprompted detail")

        self.assertEqual(result["action"], "no_follow_up_pending")
        self.assertEqual(self.context.answers, [])
        self.assertEqual(self.context.current_index, 0)

    def test_end_call(self):
        self.engine.receive_response(self.context, "I have two years of experience.")
        result = self.engine.receive_response(
            self.context,
            "Python and SQL."
        )
        self.assertEqual(result["action"], "end_call")
        self.assertTrue(self.context.completed)
        self.assertEqual(self.context.state, ConversationState.END_CALL)


if __name__ == "__main__":
    unittest.main()
