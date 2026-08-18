from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticMatchingEngine:

    def __init__(self):
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def encode(self, text):

        if not text:
            return None

        text = str(text).strip()

        if not text:
            return None

        return self._encode_cached(text)


    @lru_cache(maxsize=256)
    def _encode_cached(self, text):

        return self.model.encode(
            text,
            convert_to_numpy=True
        )

    def calculate_similarity(
        self,
        text_a,
        text_b
    ):

        embedding_a = self.encode(text_a)
        embedding_b = self.encode(text_b)

        if embedding_a is None or embedding_b is None:
            return 0.0

        score = cosine_similarity(
            [embedding_a],
            [embedding_b]
        )[0][0]

        return round(
            float(score),
            4
        )

    def calculate_section_similarity(
        self,
        candidate_section,
        required_section
    ):

        if not candidate_section or not required_section:
            return 0.0

        if isinstance(candidate_section, list):
            candidate_section = " ".join(
                str(item) for item in candidate_section
            )

        if isinstance(required_section, list):
            required_section = " ".join(
                str(item) for item in required_section
            )

        return self.calculate_similarity(
            candidate_section,
            required_section
        )

    def calculate_skill_similarity(
        self,
        candidate_skills,
        required_skills
    ):

        if not candidate_skills or not required_skills:
            return {
                "score": 0.0,
                "matched_skills": [],
                "missing_skills": []
            }

        candidate_skills = [
            str(skill).strip()
            for skill in candidate_skills
            if str(skill).strip()
        ]

        required_skills = [
            str(skill).strip()
            for skill in required_skills
            if str(skill).strip()
        ]

        if not candidate_skills or not required_skills:
            return {
                "score": 0.0,
                "matched_skills": [],
                "missing_skills": []
            }

        matched_skills = []
        missing_skills = []
        scores = []

        for required_skill in required_skills:

            best_score = 0.0
            best_candidate = None

            for candidate_skill in candidate_skills:

                candidate_normalized = candidate_skill.strip().lower()
                required_normalized = required_skill.strip().lower()

                if candidate_normalized == required_normalized:

                    score = 1.0

                else:

                    score = self.calculate_similarity(
                        candidate_skill,
                        required_skill
                    )

                if score > best_score:
                    best_score = score
                    best_candidate = candidate_skill

            scores.append(best_score)

            if best_score >= 0.70:
                matched_skills.append({
                    "required": required_skill,
                    "matched": best_candidate,
                    "score": best_score
                })
            else:
                missing_skills.append({
                    "required": required_skill,
                    "score": best_score
                })

        overall_score = sum(scores) / len(scores)

        return {
            "score": round(overall_score, 4),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills
        }

    def calculate_experience_similarity(
        self,
        candidate_experience,
        required_experience
    ):

        if not candidate_experience or not required_experience:
            return {
                "score": 0.0,
                "matched": False
            }

        if isinstance(candidate_experience, list):
            candidate_experience = " ".join(
                str(item) for item in candidate_experience
            )

        if isinstance(required_experience, list):
            required_experience = " ".join(
                str(item) for item in required_experience
            )

        candidate_experience = str(
            candidate_experience
        ).strip()

        required_experience = str(
            required_experience
        ).strip()

        if not candidate_experience or not required_experience:
            return {
                "score": 0.0,
                "matched": False
            }

        score = self.calculate_similarity(
            candidate_experience,
            required_experience
        )

        return {
            "score": score,
            "matched": score >= 0.70
        }

    def calculate_project_similarity(
        self,
        candidate_projects,
        required_projects
    ):

        if not candidate_projects or not required_projects:
            return {
                "score": 0.0,
                "matched": False
            }

        if isinstance(candidate_projects, list):
            candidate_projects = " ".join(
                str(project)
                for project in candidate_projects
            )

        if isinstance(required_projects, list):
            required_projects = " ".join(
                str(project)
                for project in required_projects
            )

        candidate_projects = str(
            candidate_projects
        ).strip()

        required_projects = str(
            required_projects
        ).strip()

        if not candidate_projects or not required_projects:
            return {
                "score": 0.0,
                "matched": False
            }

        score = self.calculate_similarity(
            candidate_projects,
            required_projects
        )

        return {
            "score": score,
            "matched": score >= 0.70
        }

    def calculate_resume_jd_score(
        self,
        candidate_skills,
        required_skills,
        candidate_experience,
        required_experience,
        candidate_projects,
        required_projects
    ):

        skills_result = self.calculate_skill_similarity(
            candidate_skills,
            required_skills
        )

        experience_result = self.calculate_experience_similarity(
            candidate_experience,
            required_experience
        )

        projects_result = self.calculate_project_similarity(
            candidate_projects,
            required_projects
        )

        overall_score = (
            skills_result["score"] * 0.40
            + experience_result["score"] * 0.35
            + projects_result["score"] * 0.25
        )

        overall_result = self.classify_similarity(
            overall_score,
            threshold=0.70
        )

        return {
            "skills_score": skills_result["score"],
            "experience_score": experience_result["score"],
            "projects_score": projects_result["score"],
            "overall_score": overall_result["score"],
            "threshold": overall_result["threshold"],
            "matched": overall_result["matched"]
        }

    def classify_similarity(
        self,
        score,
        threshold=0.70
    ):

        return {
            "score": round(score, 4),
            "threshold": threshold,
            "matched": score >= threshold
        }