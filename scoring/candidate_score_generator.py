from scoring.ats_scoring_engine import ATSScoringEngine


class CandidateScoreGenerator:

    def __init__(self):

        self.scoring_engine = ATSScoringEngine()

    def generate(
        self,
        candidate_name,
        role,
        skill_match=None,
        experience_relevance=None,
        education_alignment=None,
        semantic_similarity=None
    ):

        result = self.scoring_engine.calculate_score(
            role=role,
            skill_match=skill_match,
            experience_relevance=experience_relevance,
            education_alignment=education_alignment,
            semantic_similarity=semantic_similarity
        )

        return {
            "candidate": candidate_name or "Unknown",
            "role": result["role"],
            "score": result["overall_score"],
            "percentage": result["overall_percentage"],
            "components": {
                "skill_match": result["skill_match"],
                "experience_relevance": result[
                    "experience_relevance"
                ],
                "education_alignment": result[
                    "education_alignment"
                ],
                "semantic_similarity": result[
                    "semantic_similarity"
                ]
            },
            "weights": result["weights"],
            "explanations": result["explanations"]
        }