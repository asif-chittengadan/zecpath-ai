import unittest

from interview_ai.hr.hr_interview_engine import (
    HRInterviewEngine
)


class TestDay35HRCommunicationIntegration(unittest.TestCase):

    def setUp(self):
        self.engine = HRInterviewEngine(
            session_id="DAY35-COMM-001",
            candidate_id="CAND-035",
            role="Software Developer",
            candidate_type="fresher",
            role_type="technical"
        )

    def test_communication_is_generated(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "I completed my degree in Information Technology. "
                "I worked on Python and Django projects."
            )
        )

        self.assertIn(
            "communication",
            result
        )

    def test_communication_features_are_present(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "I completed my degree in Information Technology. "
                "I worked on Python and Django projects."
            )
        )

        features = result[
            "communication"
        ]["features"]

        self.assertIn(
            "fluency",
            features
        )

        self.assertIn(
            "grammar_quality",
            features
        )

        self.assertIn(
            "vocabulary_range",
            features
        )

        self.assertIn(
            "clarity",
            features
        )

        self.assertIn(
            "answer_structure",
            features
        )

    def test_normalized_score_is_bounded(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "I completed my degree in Information Technology. "
                "I worked on Python and Django projects."
            )
        )

        score = result[
            "communication"
        ]["normalized_score"]

        self.assertGreaterEqual(
            score,
            0
        )

        self.assertLessEqual(
            score,
            100
        )

    def test_communication_history_is_stored(self):
        self.engine.start()

        self.engine.submit_response(
            "I completed my degree in Information Technology."
        )

        history = (
            self.engine.get_communication_history()
        )

        self.assertEqual(
            len(history),
            1
        )

    def test_filler_words_are_reflected(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "Um, I basically worked on a Python project "
                "and developed the backend."
            )
        )

        features = result[
            "communication"
        ]["features"]

        self.assertGreater(
            features["filler_word_count"],
            0
        )

    def test_day34_follow_up_still_works(self):
        self.engine.start()

        result = self.engine.submit_response(
            "I am a graduate."
        )

        self.assertIn(
            "action",
            result
        )

        self.assertIn(
            "communication",
            result
        )

    def test_day35_does_not_remove_classification(self):
        self.engine.start()

        result = self.engine.submit_response(
            (
                "I completed my degree in Information Technology "
                "and worked on several software projects."
            )
        )

        self.assertIn(
            "classification",
            result
        )

    def test_multiple_responses_are_tracked(self):
        self.engine.start()

        self.engine.submit_response(
            "I completed my degree in Information Technology."
        )

        self.engine.submit_response(
            (
                "I worked on Python and Django projects "
                "during my academic work."
            )
        )

        history = (
            self.engine.get_communication_history()
        )

        self.assertEqual(
            len(history),
            2
        )


if __name__ == "__main__":
    unittest.main()