import unittest

from interview_ai.hr.communication_feature_analyzer import (
    CommunicationFeatureAnalyzer
)


class TestDay35CommunicationFeatureAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = CommunicationFeatureAnalyzer()

    def test_empty_answer(self):
        result = self.analyzer.analyze("")

        self.assertEqual(result["word_count"], 0)
        self.assertEqual(result["sentence_count"], 0)
        self.assertEqual(result["fluency"], 0)

    def test_word_and_sentence_count(self):
        result = self.analyzer.analyze(
            "I completed my degree in IT. I worked on software projects."
        )

        self.assertEqual(result["word_count"], 11)
        self.assertEqual(result["sentence_count"], 2)

    def test_filler_words_are_detected(self):
        result = self.analyzer.analyze(
            "Um, I basically worked on a Python project."
        )

        self.assertIn(
            "um",
            result["filler_words"]
        )

        self.assertIn(
            "basically",
            result["filler_words"]
        )

        self.assertEqual(
            result["filler_word_count"],
            2
        )

    def test_vocabulary_range_is_calculated(self):
        result = self.analyzer.analyze(
            "Python development requires problem solving and Python testing."
        )

        self.assertGreater(
            result["vocabulary_range"],
            0
        )

        self.assertLessEqual(
            result["vocabulary_range"],
            100
        )

    def test_clarity_is_calculated(self):
        result = self.analyzer.analyze(
            (
                "I worked on a software project using Python. "
                "I developed the backend and tested the application."
            )
        )

        self.assertGreater(
            result["clarity"],
            0
        )

    def test_structure_detects_multiple_sentences(self):
        result = self.analyzer.analyze(
            (
                "First, I understood the requirements. "
                "Then, I developed the solution. "
                "Finally, I tested the application."
            )
        )

        self.assertEqual(
            result["answer_structure"],
            100
        )

    def test_all_required_features_exist(self):
        result = self.analyzer.analyze(
            "I worked on a Python project and explained the solution clearly."
        )

        required_features = {
            "fluency",
            "grammar_quality",
            "vocabulary_range",
            "clarity",
            "filler_words",
            "filler_word_count",
            "answer_structure"
        }

        self.assertTrue(
            required_features.issubset(
                result.keys()
            )
        )

    def test_scores_are_bounded(self):
        result = self.analyzer.analyze(
            (
                "I completed my degree. "
                "I worked on multiple projects. "
                "I explained my solutions clearly."
            )
        )

        for key in [
            "fluency",
            "grammar_quality",
            "vocabulary_range",
            "clarity",
            "answer_structure"
        ]:
            self.assertGreaterEqual(
                result[key],
                0
            )

            self.assertLessEqual(
                result[key],
                100
            )


if __name__ == "__main__":
    unittest.main()