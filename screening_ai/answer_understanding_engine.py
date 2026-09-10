from screening_ai.intent_classifier import IntentClassifier
from parsers.skill_extractor import SkillExtractor
from parsers.experience_extractor import ExperienceExtractor
from screening_ai.availability_extractor import AvailabilityExtractor
from screening_ai.salary_expectation_extractor import (
    SalaryExpectationExtractor,
)


class AnswerUnderstandingEngine:
    """Convert a candidate answer into a structured semantic object."""

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.skill_extractor = SkillExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.availability_extractor = AvailabilityExtractor()
        self.salary_extractor = SalaryExpectationExtractor()

    def understand(self, answer, category):
        """
        Analyze a candidate answer and return structured information.

        Args:
            answer: Candidate's response.
            category: Question category such as experience, skills,
                      salary, availability, etc.

        Returns:
            dict: Structured semantic answer object.
        """

        if answer is None:
            answer = ""

        if not isinstance(answer, str):
            answer = str(answer)

        answer = answer.strip()

        intent = self.intent_classifier.classify(
            answer,
            category
        )

        skills = self.skill_extractor.extract(answer)
        experience = self.experience_extractor.extract(answer)
        availability = self.availability_extractor.extract(answer)
        salary = self.salary_extractor.extract(answer)

        return {
            "answer": answer,
            "category": category,
            "intent": intent,
            "skills": skills,
            "experience": {
                "minimum": experience["minimum"],
                "maximum": experience["maximum"],
                "text": experience["text"],
            },
            "availability": availability,
            "salary": salary,
        }


if __name__ == "__main__":
    engine = AnswerUnderstandingEngine()

    answer = (
        "I have 3 years of experience in Python and SQL. "
        "I can join immediately and I am expecting 8 LPA."
    )

    result = engine.understand(
        answer,
        "experience"
    )

    print(result)