class InterviewRepetitionGuard:
    """
    Prevents repeated or substantially similar interview questions.
    """

    def __init__(self):
        self.asked_questions = []

    def is_repeated(self, question):
        """
        Check whether a question has already been asked.
        """
        normalized = self._normalize(question)

        return normalized in self.asked_questions

    def register_question(self, question):
        """
        Store a question in the interview history.
        """
        normalized = self._normalize(question)

        if normalized not in self.asked_questions:
            self.asked_questions.append(normalized)

    def get_alternative(self, question, alternatives):
        """
        Return the first alternative that has not already been asked.

        Returns None if all alternatives have been used.
        """

        for alternative in alternatives:
            if not self.is_repeated(alternative):
                return alternative

        return None

    def clear(self):
        """
        Clear the question history.
        """
        self.asked_questions.clear()

    @staticmethod
    def _normalize(question):
        """
        Normalize a question for duplicate comparison.
        """
        return " ".join(
            str(question)
            .strip()
            .lower()
            .split()
        )