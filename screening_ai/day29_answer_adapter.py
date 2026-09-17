from typing import Any, Dict, List, Optional

from screening_ai.answer_understanding_engine import AnswerUnderstandingEngine


class Day29AnswerAdapter:
    """Convert Day 25 semantic answer results into Day 29 flow signals."""

    def __init__(self, answer_engine: Optional[AnswerUnderstandingEngine] = None):
        self.answer_engine = answer_engine or AnswerUnderstandingEngine()

    def analyze(
        self,
        answer: str,
        category: str,
        previous_answers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if self.is_confused_text(answer):
            return {
                "valid": False,
                "confused": True,
                "repeated": False,
                "follow_up": False,
                "reason": "confusion",
                "follow_up_question": None,
                "semantic_result": None,
            }

        result = self.answer_engine.understand(
            answer=answer,
            category=category,
        )

        intent = result.get("intent", {})
        intent_label = str(intent.get("intent_label", "")).strip().lower()

        valid = intent_label not in {
            "missing",
            "vague",
            "off_topic",
        }

        follow_up = self._needs_follow_up(result, intent_label)

        return {
            "valid": valid,
            "confused": False,
            "repeated": False,
            "follow_up": follow_up,
            "reason": "" if valid else intent_label,
            "follow_up_question": self._follow_up_question(
                result,
                category,
            ) if follow_up else None,
            "semantic_result": result,
        }

    @staticmethod
    def _needs_follow_up(
        result: Dict[str, Any],
        intent_label: str,
    ) -> bool:
        if intent_label != "on_topic":
            return False

        category = str(result.get("category", "")).strip().lower()

        if category == "skills":
            return len(result.get("skills", [])) == 1

        if category == "experience":
            experience = result.get("experience", {})
            return bool(
                experience.get("minimum") is not None
                and not experience.get("text", "").strip()
            )

        return False

    @staticmethod
    def _follow_up_question(
        result: Dict[str, Any],
        category: str,
    ) -> str:
        if category == "skills":
            return "Could you briefly mention another technology you have worked with?"

        if category == "experience":
            return "Could you briefly describe the type of work you handled during that experience?"

        return "Could you briefly provide more details about that?"

    @staticmethod
    def is_confused_text(answer: str) -> bool:
        normalized = " ".join(str(answer).lower().split())

        phrases = (
            "i don't understand",
            "i do not understand",
            "what do you mean",
            "can you explain",
            "could you explain",
            "sorry what",
            "i am confused",
            "i'm confused",
            "please repeat",
            "can you repeat",
        )

        return any(phrase in normalized for phrase in phrases)
