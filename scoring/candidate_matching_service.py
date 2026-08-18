from scoring.semantic_matching_engine import SemanticMatchingEngine
from scoring.candidate_score_generator import CandidateScoreGenerator


class CandidateMatchingService:

    _semantic_engine = None

    def __init__(self):

        if CandidateMatchingService._semantic_engine is None:

            CandidateMatchingService._semantic_engine = (
                SemanticMatchingEngine()
            )

        self.semantic_engine = (
            CandidateMatchingService._semantic_engine
        )

        self.score_generator = CandidateScoreGenerator()

    def generate_score(
        self,
        resume,
        job_description
    ):

        candidate_name = self.__extract_candidate_name(
            resume
        )

        role = job_description.get(
            "role",
            ""
        )

        # -----------------------------
        # Skills
        # -----------------------------

        candidate_skills = self.__extract_skills(
            resume
        )

        required_skills = job_description.get(
            "skills",
            []
        )

        skill_result = (
            self.semantic_engine.calculate_skill_similarity(
                candidate_skills,
                required_skills
            )
        )

        skill_match = skill_result.get(
            "score",
            0.0
        )

        # -----------------------------
        # Experience
        # -----------------------------

        experience_relevance = (
            self.__calculate_experience_relevance(
                resume,
                job_description
            )
        )

        # -----------------------------
        # Education
        # -----------------------------

        education_alignment = (
            self.__calculate_education_alignment(
                resume,
                job_description
            )
        )

        # -----------------------------
        # Semantic Similarity
        # -----------------------------

        candidate_text = (
            self.__build_candidate_text(
                resume
            )
        )

        job_text = (
            self.__build_job_text(
                job_description
            )
        )

        semantic_similarity = (
            self.semantic_engine.calculate_similarity(
                candidate_text,
                job_text
            )
        )

        # -----------------------------
        # Final ATS Score
        # -----------------------------

        return self.score_generator.generate(
            candidate_name=candidate_name,
            role=role,
            skill_match=skill_match,
            experience_relevance=experience_relevance,
            education_alignment=education_alignment,
            semantic_similarity=semantic_similarity
        )

    def __extract_candidate_name(
        self,
        resume
    ):

        others = resume.get(
            "Others",
            []
        )

        if others:

            return others[0].strip()

        return "Unknown"

    def __extract_skills(
        self,
        resume
    ):

        skills = resume.get(
            "Skills",
            {}
        )

        result = []

        for category in [
            "technical",
            "business",
            "creative"
        ]:

            category_skills = skills.get(
                category,
                []
            )

            for item in category_skills:

                if isinstance(item, dict):

                    skill = item.get(
                        "skill",
                        ""
                    )

                else:

                    skill = str(item)

                if skill:
                    result.append(skill)

        return list(
            dict.fromkeys(result)
        )

    def __calculate_experience_relevance(
        self,
        resume,
        job_description
    ):

        experience = resume.get(
            "Experience",
            {}
        )

        job_experience = job_description.get(
            "experience",
            {}
        )

        total_experience = experience.get(
            "total_experience",
            {}
        )

        candidate_years = total_experience.get(
            "years",
            0
        )

        minimum = job_experience.get(
            "minimum",
            0
        )

        maximum = job_experience.get(
            "maximum",
            0
        )

        job_text = job_experience.get(
            "text",
            ""
        ).lower()

        # Fresher requirement
        if "fresher" in job_text:

            if candidate_years == 0:
                return 1.0

            return 0.5

        # No experience requirement
        if (
            minimum == 0
            and maximum == 0
        ):

            return 1.0

        if candidate_years < minimum:

            return 0.0

        if (
            maximum > 0
            and candidate_years > maximum
        ):

            return 0.5

        return 1.0

    def __calculate_education_alignment(
        self,
        resume,
        job_description
    ):

        education = resume.get(
            "Education",
            {}
        )

        required_education = job_description.get(
            "education",
            []
        )

        if not education or not required_education:
            return 0.0

        candidate_degree = str(
            education.get("degree", "")
        ).strip().lower()

        candidate_field = str(
            education.get("field_of_study", "")
        ).strip().lower()

        if not candidate_degree and not candidate_field:
            return 0.0

        # -----------------------------
        # Normalize JD requirements
        # -----------------------------

        degree_aliases = {
            "b.tech": "bachelor of technology",
            "b.e": "bachelor of engineering",
            "b.sc": "bachelor of science",
            "bca": "bachelor of computer applications",
            "bba": "bachelor of business administration",
            "m.tech": "master of technology",
            "m.e": "master of engineering",
            "m.sc": "master of science",
            "mca": "master of computer applications",
            "mba": "master of business administration"
        }

        normalized_requirements = []

        for requirement in required_education:

            requirement = str(
                requirement
            ).strip().lower()

            normalized_requirement = degree_aliases.get(
                requirement,
                requirement
            )

            normalized_requirements.append(
                normalized_requirement
            )

        # -----------------------------
        # Degree match
        # -----------------------------

        degree_match = False

        for requirement in normalized_requirements:

            if (
                requirement == candidate_degree
                or requirement in candidate_degree
                or candidate_degree in requirement
            ):

                degree_match = True
                break

        # -----------------------------
        # Field match
        # -----------------------------

        field_match = False

        for requirement in normalized_requirements:

            if requirement == candidate_field:

                field_match = True
                break

            if (
                requirement in candidate_field
                or candidate_field in requirement
            ):

                field_match = True
                break

        # -----------------------------
        # Final alignment
        # -----------------------------

        if degree_match and field_match:
            return 1.0

        if degree_match:
            return 0.5

        if field_match:
            return 0.5

        return 0.0
    def __build_candidate_text(
        self,
        resume
    ):

        parts = []

        summary = resume.get(
            "Summary",
            []
        )

        if isinstance(summary, list):

            parts.extend(summary)

        else:

            parts.append(
                str(summary)
            )

        projects = resume.get(
            "Projects",
            []
        )

        if isinstance(projects, list):

            parts.extend(projects)

        else:

            parts.append(
                str(projects)
            )

        return " ".join(
            str(part)
            for part in parts
            if part
        )

    def __build_job_text(
        self,
        job_description
    ):

        parts = []

        role = job_description.get(
            "role",
            ""
        )

        if role:
            parts.append(role)

        skills = job_description.get(
            "skills",
            []
        )

        parts.extend(
            str(skill)
            for skill in skills
        )

        experience = job_description.get(
            "experience",
            {}
        )

        if experience.get("text"):
            parts.append(
                experience["text"]
            )

        education = job_description.get(
            "education",
            []
        )

        parts.extend(
            str(item)
            for item in education
        )

        return " ".join(parts)