"""
ZECPATH AI - Technical Interview Question Hierarchy

Day 46:
Defines the hierarchy of technical interview questions based on
interview stage and candidate experience level.
"""


class TechnicalQuestionHierarchy:
    """
    Defines technical interview question categories and difficulty.
    """

    # ---------------------------------------------------------
    # Question Hierarchy
    # ---------------------------------------------------------

    HIERARCHY = {
        "introduction": {
            "basic": [
                "Tell me about your technical background.",
                "Which programming languages are you comfortable with?",
            ],
            "intermediate": [
                "Describe your technical experience and major projects.",
                "Which technologies have you used in production or practical projects?",
            ],
            "advanced": [
                "Describe your overall engineering experience and the systems you have worked on.",
                "Which technical decisions have you made that had a significant impact on a project?",
            ],
        },

        "experience_based": {
            "basic": [
                "Describe a project you have worked on.",
                "What was your role in the project?",
            ],
            "intermediate": [
                "Describe a technical problem you solved in a project.",
                "How did you debug and resolve a difficult issue?",
            ],
            "advanced": [
                "Describe a complex technical problem you solved and the trade-offs you considered.",
                "Describe an architectural decision you made and why you selected that approach.",
            ],
        },

        "conceptual": {
            "basic": [
                "What is object-oriented programming?",
                "What is the difference between a list and a tuple?",
            ],
            "intermediate": [
                "Explain how an API works between a client and a server.",
                "What is database indexing and why is it useful?",
            ],
            "advanced": [
                "Explain the trade-offs between different database scaling strategies.",
                "How would you design a system for high availability and scalability?",
            ],
        },

        "scenario_based": {
            "basic": [
                "A program is producing an unexpected error. How would you debug it?",
                "An application is running slowly. What would you check first?",
            ],
            "intermediate": [
                "A web application suddenly receives a large increase in traffic. How would you handle it?",
                "A production API is returning intermittent failures. How would you investigate the problem?",
            ],
            "advanced": [
                "Design a scalable system capable of handling millions of users.",
                "A distributed system is experiencing latency and reliability problems. How would you diagnose and improve it?",
            ],
        },
    }

    # ---------------------------------------------------------
    # Difficulty Progression
    # ---------------------------------------------------------

    DIFFICULTY_ORDER = [
        "basic",
        "intermediate",
        "advanced",
    ]

    # ---------------------------------------------------------
    # Public Methods
    # ---------------------------------------------------------

    @classmethod
    def get_questions(cls, category, difficulty):
        """
        Return questions for a category and difficulty level.
        """

        if category not in cls.HIERARCHY:
            raise ValueError(
                f"Unknown question category: {category}"
            )

        if difficulty not in cls.DIFFICULTY_ORDER:
            raise ValueError(
                f"Unknown difficulty level: {difficulty}"
            )

        return list(
            cls.HIERARCHY[category][difficulty]
        )

    @classmethod
    def get_categories(cls):
        """
        Return all technical interview categories.
        """

        return list(cls.HIERARCHY.keys())

    @classmethod
    def get_difficulty_levels(cls):
        """
        Return supported difficulty levels.
        """

        return list(cls.DIFFICULTY_ORDER)

    @classmethod
    def get_next_difficulty(cls, current_difficulty):
        """
        Move to the next difficulty level.
        """

        if current_difficulty not in cls.DIFFICULTY_ORDER:
            raise ValueError(
                f"Unknown difficulty level: {current_difficulty}"
            )

        current_index = cls.DIFFICULTY_ORDER.index(
            current_difficulty
        )

        if current_index >= len(cls.DIFFICULTY_ORDER) - 1:
            return "advanced"

        return cls.DIFFICULTY_ORDER[current_index + 1]