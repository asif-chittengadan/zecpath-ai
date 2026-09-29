import unittest

from interview_ai.hr.aptitude_evaluation_engine import (
    AptitudeEvaluationEngine
)


class TestDay38AptitudeEvaluationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = AptitudeEvaluationEngine()

    def test_reasoning_correct_answer(self):
        question = self.engine.questions[0]

        result = self.engine.evaluate_reasoning_answer(
            question["question_id"],
            question["correct_answer"]
        )

        self.assertTrue(result["correct"])
        self.assertEqual(result["score"], 100)

    def test_reasoning_wrong_answer(self):
        question = self.engine.questions[0]

        wrong_answer = next(
            option
            for option in question["options"]
            if option != question["correct_answer"]
        )

        result = self.engine.evaluate_reasoning_answer(
            question["question_id"],
            wrong_answer
        )

        self.assertFalse(result["correct"])
        self.assertEqual(result["score"], 0)

    def test_unknown_question(self):
        result = self.engine.evaluate_reasoning_answer(
            "UNKNOWN",
            "A"
        )

        self.assertFalse(result["correct"])
        self.assertEqual(result["score"], 0)

    def test_situational_answer(self):
        scenario = self.engine.scenarios[0]

        result = self.engine.evaluate_situational_answer(
            scenario["scenario_id"],
            scenario["ideal_answer"]
        )

        self.assertTrue(result["ideal_match"])
        self.assertEqual(result["score"], 100)

    def test_unknown_scenario(self):
        result = self.engine.evaluate_situational_answer(
            "UNKNOWN",
            "A"
        )

        self.assertFalse(result["ideal_match"])
        self.assertEqual(result["score"], 0)

    def test_problem_solving_evaluation(self):
        response = (
            "First, I would identify the root cause. "
            "Then I would analyze the issue and consider "
            "different approaches. Finally, I would implement "
            "the solution and test the result."
        )

        result = self.engine.evaluate_problem_solving(
            response
        )

        self.assertEqual(
            result["clarity_score"],
            100
        )

    def test_aptitude_score(self):
        result = self.engine.calculate_aptitude_score(
            reasoning_accuracy=80,
            reasoning_structure=90,
            problem_solving=70,
            clarity=100
        )

        self.assertIn(
            "final_score",
            result
        )

        self.assertGreaterEqual(
            result["final_score"],
            0
        )

        self.assertLessEqual(
            result["final_score"],
            100
        )

    def test_score_breakdown_available(self):
        result = self.engine.scoring_engine.get_score_breakdown(
            reasoning_accuracy=80,
            reasoning_structure=90,
            problem_solving=70,
            clarity=100
        )

        self.assertEqual(
            len(result["breakdown"]),
            4
        )


if __name__ == "__main__":
    unittest.main()