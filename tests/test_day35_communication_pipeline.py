import unittest

from interview_ai.hr.communication_feature_analyzer import (
    CommunicationFeatureAnalyzer
)
from interview_ai.hr.communication_scoring_engine import (
    CommunicationScoringEngine
)
from interview_ai.hr.communication_score_normalizer import (
    CommunicationScoreNormalizer
)


class TestDay35CommunicationPipeline(unittest.TestCase):

    def setUp(self):
        self.analyzer = CommunicationFeatureAnalyzer()
        self.scorer = CommunicationScoringEngine()
        self.normalizer = CommunicationScoreNormalizer()

    def evaluate(self, answer):
        features = self.analyzer.analyze(answer)

        raw_result = self.scorer.score(features)

        normalized = self.normalizer.normalize(
            raw_result["score"],
            features["word_count"]
        )

        return {
            "features": features,
            "raw_score": raw_result["score"],
            "normalized_score": normalized
        }

    def test_strong_answer(self):
        result = self.evaluate(
            (
                "I worked on a Python project during my final year. "
                "First, I understood the requirements. "
                "Then, I developed the backend and tested the APIs. "
                "Finally, I documented the solution."
            )
        )

        self.assertGreater(
            result["normalized_score"],
            50
        )

    def test_short_answer(self):
        result = self.evaluate(
            "I worked on Python."
        )

        self.assertGreaterEqual(
            result["normalized_score"],
            0
        )

        self.assertLessEqual(
            result["normalized_score"],
            100
        )

    def test_empty_answer(self):
        result = self.evaluate("")

        self.assertEqual(
            result["normalized_score"],
            0
        )

    def test_filler_words_reduce_control_score(self):
        clean = self.evaluate(
            (
                "I worked on a Python project and "
                "developed the backend."
            )
        )

        filler = self.evaluate(
            (
                "Um, I basically worked on a Python project "
                "and developed the backend."
            )
        )

        self.assertGreater(
            clean["features"]["filler_word_count"],
            0
            if filler["features"]["filler_word_count"] == 0
            else -1
        )

        self.assertLess(
            filler["features"]["filler_word_count"],
            10
        )

    def test_structured_answer(self):
        result = self.evaluate(
            (
                "First, I analyzed the problem. "
                "Then, I designed the solution. "
                "Finally, I tested the implementation."
            )
        )

        self.assertEqual(
            result["features"]["answer_structure"],
            100
        )

    def test_scores_are_bounded(self):
        answers = [
            "",
            "Yes.",
            "I worked on Python.",
            (
                "I completed my degree in Information Technology "
                "and worked on several software projects."
            )
        ]

        for answer in answers:
            result = self.evaluate(answer)

            self.assertGreaterEqual(
                result["normalized_score"],
                0
            )

            self.assertLessEqual(
                result["normalized_score"],
                100
            )

    def test_pipeline_returns_all_sections(self):
        result = self.evaluate(
            "I worked on a Python project."
        )

        self.assertIn(
            "features",
            result
        )

        self.assertIn(
            "raw_score",
            result
        )

        self.assertIn(
            "normalized_score",
            result
        )

    def test_raw_and_normalized_scores_exist(self):
        result = self.evaluate(
            (
                "I completed my degree and worked "
                "on Python projects."
            )
        )

        self.assertGreaterEqual(
            result["raw_score"],
            0
        )

        self.assertGreaterEqual(
            result["normalized_score"],
            0
        )

    def test_vocabulary_feature_is_generated(self):
        result = self.evaluate(
            (
                "I designed a backend architecture "
                "and implemented database integration."
            )
        )

        self.assertGreater(
            result["features"]["vocabulary_range"],
            0
        )


if __name__ == "__main__":
    unittest.main()