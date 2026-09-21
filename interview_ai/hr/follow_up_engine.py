class HRFollowUpEngine:
    """
    Determines whether an HR interview answer should receive
    a follow-up question.
    """

    def __init__(self, minimum_words=8):
        self.minimum_words = minimum_words

    def evaluate(self, question, response, category):
        """
        Evaluate whether the candidate response needs a follow-up.

        Returns:
            {
                "eligible": bool,
                "reason": str
            }
        """

        question = self._normalize_text(question)
        response = self._normalize_text(response)
        category = self._normalize_category(category)

        if not response:
            return {
                "eligible": False,
                "reason": "No response provided."
            }

        word_count = len(response.split())

        if word_count < self.minimum_words:
            return {
                "eligible": True,
                "reason": "Response is too brief."
            }

        if category in {
            "teamwork_culture_fit",
            "career_journey",
            "strengths_weaknesses"
        }:
            if word_count < self.minimum_words + 5:
                return {
                    "eligible": True,
                    "reason": "Behavioral response needs more detail."
                }

        return {
            "eligible": False,
            "reason": "Response contains sufficient detail."
        }

    def generate_follow_up(self, question, category):
        """
        Generate a category-specific follow-up question.
        """

        category = self._normalize_category(category)

        follow_ups = {
            "self_introduction":
                "Could you tell me a little more about that experience?",

            "career_journey":
                "What was your specific contribution in that experience?",

            "strengths_weaknesses":
                "Could you give me an example that demonstrates this?",

            "teamwork_culture_fit":
                "What was your specific responsibility in that situation?",

            "career_goals":
                "What steps are you taking toward that goal?",

            "availability_commitment":
                "Could you provide a little more detail about your availability?"
        }

        return follow_ups.get(
            category,
            "Could you please provide a little more detail?"
        )

    @staticmethod
    def _normalize_text(value):
        """
        Normalize natural-language text without removing spaces.
        """
        return " ".join(str(value).strip().lower().split())

    @staticmethod
    def _normalize_category(value):
        """
        Normalize category names for dictionary lookup.
        """
        return (
            str(value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )