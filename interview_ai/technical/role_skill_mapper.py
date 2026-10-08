"""
ZECPATH AI - Technical Role Skill Mapper

Day 46:
Maps technical job roles to their relevant skill domains.
"""


from interview_ai.technical.technical_interview import (
    TechnicalInterviewConfig,
)


class TechnicalRoleSkillMapper:
    """
    Maps technical roles to skill domains.
    """

    ROLE_ALIASES = {
        "mern developer": "mern",
        "mern stack developer": "mern",
        "full stack developer": "mern",
        "java developer": "java",
        "spring boot developer": "java",
        "python developer": "python",
        "python backend developer": "python",
        "devops engineer": "devops",
        "devops developer": "devops",
    }

    @classmethod
    def get_domain(cls, role):
        if not isinstance(role, str):
            raise TypeError("Role must be a string.")

        role_key = role.strip().lower()

        if role_key in TechnicalInterviewConfig.ROLE_SKILL_DOMAINS:
            return role_key

        return cls.ROLE_ALIASES.get(role_key)

    @classmethod
    def get_skills(cls, role):
        domain = cls.get_domain(role)

        if domain is None:
            return []

        return TechnicalInterviewConfig.get_skill_domains(
            domain
        )

    @classmethod
    def is_supported_role(cls, role):
        return cls.get_domain(role) is not None