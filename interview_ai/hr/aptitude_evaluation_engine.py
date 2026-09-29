import json
from pathlib import Path

from interview_ai.hr.aptitude_logic_scoring_engine import (
    AptitudeLogicScoringEngine
)


class AptitudeEvaluationEngine:
    """
    Evaluates reasoning and situational aptitude responses.
    """

    def __init__(
        self,
        questions_path="data/aptitude_questions.json",
        scenarios_path="data/situational_scenarios.json",
        scoring_config_path="config/aptitude_scoring_rules.json"
    ):
        questions_data = self._load_json(
            questions_path
        )

        scenarios_data = self._load_json(
            scenarios_path
        )

        self.questions = self._extract_questions(
            questions_data
        )

        self.scenarios = self._extract_scenarios(
            scenarios_data
        )

        self.scoring_engine = AptitudeLogicScoringEngine(
            scoring_config_path
        )

    def _load_json(self, file_path):
        path = Path(file_path)

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def _extract_questions(self, data):
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            questions = data.get("questions", [])

            if isinstance(questions, list):
                return questions

        return []


    def _extract_scenarios(self, data):
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            scenarios = data.get("scenarios", [])

            if isinstance(scenarios, list):
                return scenarios

        return []

    def evaluate_reasoning_answer(
        self,
        question_id,
        selected_answer
    ):
        question = self._find_question(
            question_id
        )

        if question is None:
            return {
                "question_id": question_id,
                "correct": False,
                "score": 0
            }

        correct = (
            selected_answer
            == question["correct_answer"]
        )

        score = 100 if correct else 0

        return {
            "question_id": question_id,
            "correct": correct,
            "score": score,
            "category": question["category"],
            "difficulty": question["difficulty"]
        }

    def evaluate_situational_answer(
        self,
        scenario_id,
        selected_answer
    ):
        scenario = self._find_scenario(
            scenario_id
        )

        if scenario is None:
            return {
                "scenario_id": scenario_id,
                "ideal_match": False,
                "score": 0
            }

        ideal_match = (
            selected_answer
            == scenario["ideal_answer"]
        )

        score = 100 if ideal_match else 0

        return {
            "scenario_id": scenario_id,
            "ideal_match": ideal_match,
            "score": score,
            "category": scenario["category"],
            "difficulty": scenario["difficulty"]
        }

    def evaluate_problem_solving(
        self,
        response
    ):
        result = (
            self.scoring_engine
            .analyze_problem_solving_clarity(
                response
            )
        )

        return result

    def calculate_aptitude_score(
        self,
        reasoning_accuracy,
        reasoning_structure,
        problem_solving,
        clarity
    ):
        return self.scoring_engine.calculate_score(
            reasoning_accuracy=reasoning_accuracy,
            reasoning_structure=reasoning_structure,
            problem_solving=problem_solving,
            clarity=clarity
        )

    def _find_question(self, question_id):
        for question in self.questions:
            if question.get("question_id") == question_id:
                return question

        return None

    def _find_scenario(self, scenario_id):
        for scenario in self.scenarios:
            if scenario.get("scenario_id") == scenario_id:
                return scenario

        return None