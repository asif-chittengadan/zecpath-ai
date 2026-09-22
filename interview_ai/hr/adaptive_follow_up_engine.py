class AdaptiveFollowUpEngine:
    """
    Selects the appropriate follow-up strategy based on
    HR response classification.

    Supported triggers:
        - clarification
        - deepening
        - example_based
        - scenario_based
        - none
    """

    def decide(self, analysis, category):
        """
        Decide which follow-up strategy should be used.

        Args:
            analysis: Output from HRResponseAnalyzer.analyze()
            category: HR interview question category

        Returns:
            {
                "trigger": str,
                "follow_up_required": bool,
                "question": str | None,
                "reason": str
            }
        """

        classification = analysis.get(
            "classification",
            "incomplete"
        )

        category = self._normalize_category(category)

        if classification == "incomplete":
            return self._build_result(
                trigger="clarification",
                required=True,
                question=self._clarification_question(category),
                reason="Candidate response is incomplete."
            )

        if classification == "vague":
            return self._build_result(
                trigger="deepening",
                required=True,
                question=self._deepening_question(category),
                reason="Candidate response is vague."
            )

        if classification == "confident":
            return self._build_result(
                trigger="scenario_based",
                required=True,
                question=self._scenario_question(category),
                reason=(
                    "Candidate response is detailed and confident; "
                    "a more challenging follow-up can be asked."
                )
            )

        if classification == "complete":
            if category in {
                "career_journey",
                "strengths_weaknesses",
                "teamwork_culture_fit"
            }:
                return self._build_result(
                    trigger="example_based",
                    required=True,
                    question=self._example_question(category),
                    reason=(
                        "Candidate response is complete, but an example "
                        "can provide stronger behavioral evidence."
                    )
                )

            return self._build_result(
                trigger="none",
                required=False,
                question=None,
                reason="Response is sufficiently complete."
            )

        return self._build_result(
            trigger="clarification",
            required=True,
            question=self._clarification_question(category),
            reason="Unknown response classification."
        )

    def _clarification_question(self, category):
        questions = {
            "self_introduction":
                "Could you tell me a little more about your background?",

            "career_journey":
                "Could you explain that part of your career journey in more detail?",

            "strengths_weaknesses":
                "Could you explain that strength or area for improvement more clearly?",

            "teamwork_culture_fit":
                "Could you explain what happened in that team situation?",

            "career_goals":
                "Could you explain your career goal in a little more detail?",

            "availability_commitment":
                "Could you clarify your availability and commitment?"
        }

        return questions.get(
            category,
            "Could you please explain your answer in more detail?"
        )

    def _deepening_question(self, category):
        questions = {
            "self_introduction":
                "Which part of your background is most relevant to this role?",

            "career_journey":
                "What was your specific contribution during that experience?",

            "strengths_weaknesses":
                "How has that affected your work or learning?",

            "teamwork_culture_fit":
                "What was your specific responsibility in that situation?",

            "career_goals":
                "Why is that career direction important to you?",

            "availability_commitment":
                "Are there any factors that could affect your joining availability?"
        }

        return questions.get(
            category,
            "Could you provide more specific details?"
        )

    def _example_question(self, category):
        questions = {
            "career_journey":
                "Could you give me a specific example from that experience?",

            "strengths_weaknesses":
                "Could you give me an example that demonstrates this?",

            "teamwork_culture_fit":
                "Could you give me a specific example of how you handled that situation?"
        }

        return questions.get(
            category,
            "Could you give me a specific example?"
        )

    def _scenario_question(self, category):
        questions = {
            "self_introduction":
                (
                    "If you joined this role, which part of your "
                    "background would help you contribute first?"
                ),

            "career_journey":
                (
                    "If you faced a similar challenge in this role, "
                    "how would you approach it differently?"
                ),

            "strengths_weaknesses":
                (
                    "How would you apply that strength when facing "
                    "a difficult situation at work?"
                ),

            "teamwork_culture_fit":
                (
                    "Suppose two teammates strongly disagree with "
                    "your approach. How would you handle the situation?"
                ),

            "career_goals":
                (
                    "If your role changes significantly over the next "
                    "two years, how would you adapt your career plan?"
                ),

            "availability_commitment":
                (
                    "If the team needed you to join earlier than expected, "
                    "how would you handle that situation?"
                )
        }

        return questions.get(
            category,
            "How would you handle a similar situation in this role?"
        )

    @staticmethod
    def _build_result(
        trigger,
        required,
        question,
        reason
    ):
        return {
            "trigger": trigger,
            "follow_up_required": required,
            "question": question,
            "reason": reason
        }

    @staticmethod
    def _normalize_category(value):
        return (
            str(value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )