import unittest

from interview_ai.hr.response_analyzer import HRResponseAnalyzer


class TestDay34ResponseAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = HRResponseAnalyzer()

    def test_empty_response_is_incomplete(self):
        result = self.analyzer.analyze("")

        self.assertEqual(
            result["classification"],
            "incomplete"
        )

    def test_short_response_is_incomplete(self):
        result = self.analyzer.analyze(
            "I worked there."
        )

        self.assertEqual(
            result["classification"],
            "incomplete"
        )

    def test_vague_response(self):
        result = self.analyzer.analyze(
            "Maybe I worked on something like that and things like that."
        )

        self.assertEqual(
            result["classification"],
            "vague"
        )

    def test_complete_response(self):
        result = self.analyzer.analyze(
            (
                "I worked on a college project using Python and Django. "
                "I handled the backend development and database integration."
            )
        )

        self.assertEqual(
            result["classification"],
            "complete"
        )

    def test_confident_response(self):
        result = self.analyzer.analyze(
            (
                "I successfully implemented the backend using Python and Django. "
                "I handled the database integration and worked with my team."
            )
        )

        self.assertEqual(
            result["classification"],
            "confident"
        )

    def test_word_count_is_returned(self):
        result = self.analyzer.analyze(
            "I worked on a Python project during my final year."
        )

        self.assertGreater(
            result["word_count"],
            0
        )

    def test_response_normalization(self):
        result = self.analyzer.analyze(
            (
                "   I worked on a Python project using Python and Django.   "
            )
        )

        self.assertIn(
            result["classification"],
            {
                "complete",
                "confident"
            }
        )


if __name__ == "__main__":
    unittest.main()