import json


class HRQuestionGenerator:
    """Selects HR interview questions from the V2 question bank."""

    def __init__(self, question_bank_path="data/hr_question_bank.json"):
        with open(question_bank_path, "r", encoding="utf-8") as file:
            self.question_bank = json.load(file)

    def generate(self, category, candidate_type, role_type):
        category = self._normalize(category)
        candidate_type = self._normalize(candidate_type)
        role_type = self._normalize(role_type)

        if category not in self.question_bank["categories"]:
            raise ValueError(
                f"Unknown HR interview category: {category}"
            )

        if candidate_type not in {"fresher", "experienced"}:
            raise ValueError(
                "candidate_type must be 'fresher' or 'experienced'"
            )

        if role_type not in {"technical", "non_technical"}:
            raise ValueError(
                "role_type must be 'technical' or 'non_technical'"
            )

        questions = (
            self.question_bank["categories"][category]["questions"]
            [candidate_type][role_type]
        )

        return list(questions)

    @staticmethod
    def _normalize(value):
        return (
            str(value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )