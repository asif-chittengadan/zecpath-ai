import json
from pathlib import Path


class ScreeningScoringEngine:

    def __init__(self, rules_path=None):
        if rules_path is None:
            rules_path = (
                Path(__file__).resolve().parent.parent
                / "config"
                / "screening_scoring_rules.json"
            )

        self.rules = self._load_rules(rules_path)

    def _load_rules(self, rules_path):
        with open(
            rules_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    def score_question(
        self,
        question,
        answer,
        category,
        expected_keywords=None,
        previous_answers=None
    ):
        if answer is None:
            answer = ""

        if not isinstance(answer, str):
            answer = str(answer)

        answer = answer.strip()

        if expected_keywords is None:
            expected_keywords = []

        if previous_answers is None:
            previous_answers = []

        clarity = self._score_clarity(answer)

        relevance = self._score_relevance(
            question,
            answer,
            category,
            expected_keywords
        )

        completeness = self._score_completeness(
            answer,
            expected_keywords
        )

        consistency = self._score_consistency(
            answer,
            previous_answers
        )

        scores = {
            "clarity": clarity,
            "relevance": relevance,
            "completeness": completeness,
            "consistency": consistency
        }

        normalized_scores = {
            parameter: round((score / 10) * 100, 2)
            for parameter, score in scores.items()
        }

        explanations = {
            "clarity": self._explain_clarity(clarity, answer),
            "relevance": self._explain_relevance(
                relevance,
                expected_keywords
            ),
            "completeness": self._explain_completeness(
                completeness,
                expected_keywords
            ),
            "consistency": self._explain_consistency(
                consistency,
                previous_answers
            )
        }

        return {
            "question": question,
            "answer": answer,
            "category": category,
            "scores": scores,
            "normalized_scores": normalized_scores,
            "explanations": explanations
        }

    def _score_clarity(self, answer):
        if not answer:
            return 0.0

        words = answer.split()
        word_count = len(words)

        if word_count == 1:
            return 3.0

        if word_count <= 3:
            return 5.0

        if word_count <= 10:
            return 8.0

        return 10.0

    def _score_relevance(
        self,
        question,
        answer,
        category,
        expected_keywords
    ):
        if not answer:
            return 0.0

        answer_lower = answer.lower()

        matches = 0

        for keyword in expected_keywords:
            if str(keyword).lower() in answer_lower:
                matches += 1

        if expected_keywords:
            match_ratio = (
                matches / len(expected_keywords)
            )

            return round(
                match_ratio * 10,
                2
            )

        if category:
            category_terms = category.lower().split()

            category_matches = sum(
                1
                for term in category_terms
                if term in answer_lower
            )

            if category_matches > 0:
                return 8.0

        return 5.0

    def _score_completeness(
        self,
        answer,
        expected_keywords
    ):
        if not answer:
            return 0.0

        if not expected_keywords:
            return 10.0

        answer_lower = answer.lower()

        matched_keywords = sum(
            1
            for keyword in expected_keywords
            if str(keyword).lower() in answer_lower
        )

        completeness_ratio = (
            matched_keywords / len(expected_keywords)
        )

        return round(
            completeness_ratio * 10,
            2
        )

    def _score_consistency(
        self,
        answer,
        previous_answers
    ):
        if not answer:
            return 0.0

        if not previous_answers:
            return 10.0

        answer_lower = answer.lower()

        for previous_answer in previous_answers:
            if not previous_answer:
                continue

            previous_lower = (
                str(previous_answer).lower()
            )

            if answer_lower == previous_lower:
                return 10.0

        return 8.0

    def aggregate_scores(self, question_scores):
        if not question_scores:
            return {
                "total_screening_score": 0.0,
                "questions_evaluated": 0
            }

        weights = {
            parameter: details["weight"]
            for parameter, details in self.rules["parameters"].items()
        }

        parameter_totals = {
            parameter: 0.0
            for parameter in weights
        }

        for question_score in question_scores:
            normalized_scores = question_score["normalized_scores"]

            for parameter, weight in weights.items():
                parameter_totals[parameter] += (
                    normalized_scores.get(parameter, 0.0) * weight
                )

        question_count = len(question_scores)

        parameter_averages = {
            parameter: round(
                total / question_count,
                2
            )
            for parameter, total in parameter_totals.items()
        }

        total_screening_score = round(
            sum(parameter_averages.values()),
            2
        )

        return {
            "total_screening_score": total_screening_score,
            "questions_evaluated": question_count,
            "parameter_scores": parameter_averages
        }

    def _explain_clarity(self, score, answer):
        if not answer:
            return "No answer was provided."

        if score <= 3:
            return "The answer is very short and provides limited detail."

        if score <= 5:
            return "The answer is understandable but provides limited detail."

        if score <= 8:
            return "The answer is clear and provides a reasonable amount of detail."

        return "The answer is clear and provides sufficient detail."

    def _explain_relevance(self, score, expected_keywords):
        if not expected_keywords:
            return "No specific keywords were provided for relevance evaluation."

        if score == 0:
            return "The answer does not contain the expected information."

        if score < 5:
            return "The answer contains limited relevant information."

        if score < 10:
            return "The answer contains some of the expected relevant information."

        return "The answer contains all expected relevant information."

    def _explain_completeness(self, score, expected_keywords):
        if not expected_keywords:
            return "No specific completeness requirements were provided."

        if score == 0:
            return "The answer does not contain the expected information."

        if score < 5:
            return "The answer contains only a small portion of the expected information."

        if score < 10:
            return "The answer contains some but not all expected information."

        return "The answer contains all expected information."

    def _explain_consistency(self, score, previous_answers):
        if not previous_answers:
            return "No previous answers were available for consistency comparison."

        if score == 10:
            return "The answer is consistent with the available previous responses."

        return "The answer is broadly consistent with the available previous responses."