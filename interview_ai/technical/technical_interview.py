"""
ZECPATH AI - Technical Interview System

Day 46:
Defines the technical interview structure, experience-level logic,
role-to-skill-domain mapping, and interview flow states.
"""


class TechnicalInterviewConfig:
    """
    Configuration and structural rules for the technical interview.
    """

    # ---------------------------------------------------------
    # Technical Interview Structure
    # ---------------------------------------------------------

    INTERVIEW_STAGES = [
        "introduction",
        "experience_based",
        "conceptual",
        "scenario_based",
        "completed",
    ]

    # ---------------------------------------------------------
    # Experience-Based Difficulty
    # ---------------------------------------------------------

    EXPERIENCE_LEVELS = {
        "0-2": {
            "label": "basic",
            "description": "Basic technical concepts and fundamentals",
        },
        "3-5": {
            "label": "intermediate",
            "description": "Intermediate technical concepts and practical application",
        },
        "5+": {
            "label": "advanced",
            "description": "Advanced technical concepts and system design",
        },
    }

    # ---------------------------------------------------------
    # Role → Skill Domain Mapping
    # ---------------------------------------------------------

    ROLE_SKILL_DOMAINS = {
        "mern": [
            "javascript",
            "react",
            "node.js",
            "express.js",
            "mongodb",
        ],
        "java": [
            "java",
            "spring",
            "spring boot",
            "sql",
            "object oriented programming",
        ],
        "python": [
            "python",
            "django",
            "flask",
            "fastapi",
            "sql",
        ],
        "devops": [
            "linux",
            "docker",
            "kubernetes",
            "ci/cd",
            "cloud",
        ],
    }

    # ---------------------------------------------------------
    # Difficulty Progression
    # ---------------------------------------------------------

    DIFFICULTY_LEVELS = [
        "basic",
        "intermediate",
        "advanced",
    ]

    # ---------------------------------------------------------
    # Flow States
    # ---------------------------------------------------------

    FLOW_TRANSITIONS = {
        "introduction": "experience_based",
        "experience_based": "conceptual",
        "conceptual": "scenario_based",
        "scenario_based": "completed",
    }

    @classmethod
    def get_experience_level(cls, years):
        """
        Determine the interview difficulty level from experience.

        0-2 years  -> basic
        3-5 years  -> intermediate
        5+ years   -> advanced
        """

        if years < 0:
            raise ValueError("Experience years cannot be negative.")

        if years <= 2:
            return cls.EXPERIENCE_LEVELS["0-2"]

        if years <= 5:
            return cls.EXPERIENCE_LEVELS["3-5"]

        return cls.EXPERIENCE_LEVELS["5+"]

    @classmethod
    def get_skill_domains(cls, role):
        """
        Return skill domains associated with a job role.
        """

        if not isinstance(role, str):
            raise TypeError("Role must be a string.")

        role_key = role.strip().lower()

        return cls.ROLE_SKILL_DOMAINS.get(role_key, [])

    @classmethod
    def get_next_stage(cls, current_stage):
        """
        Return the next interview stage.
        """

        if current_stage not in cls.FLOW_TRANSITIONS:
            if current_stage == "completed":
                return "completed"

            raise ValueError(
                f"Unknown interview stage: {current_stage}"
            )

        return cls.FLOW_TRANSITIONS[current_stage]

    @classmethod
    def get_initial_stage(cls):
        """
        Return the first stage of the technical interview.
        """

        return cls.INTERVIEW_STAGES[0]

    @classmethod
    def get_difficulty_levels(cls):
        """
        Return supported question difficulty levels.
        """

        return list(cls.DIFFICULTY_LEVELS)
        
    @classmethod
    def get_next_difficulty(cls, current_difficulty):
        if current_difficulty not in cls.DIFFICULTY_LEVELS:
            raise ValueError(
                f"Unknown difficulty level: {current_difficulty}"
            )

        current_index = cls.DIFFICULTY_LEVELS.index(
            current_difficulty
        )

        if current_index >= len(cls.DIFFICULTY_LEVELS) - 1:
            return "advanced"

        return cls.DIFFICULTY_LEVELS[current_index + 1]