from scoring.weight_config import WeightConfig


class ATSScoringEngine:

    def __init__(self):

        self.weight_config = WeightConfig()

    def normalize_component_score(self, score):

        if score is None:
            return 0.0

        try:
            score = float(score)
        except (TypeError, ValueError):
            return 0.0

        if score < 0:
            return 0.0

        if score > 1:
            return 1.0

        return round(score, 4)

    def calculate_score(
        self,
        role,
        skill_match=0.0,
        experience_relevance=0.0,
        education_alignment=0.0,
        semantic_similarity=0.0
    ):

        weights = self.weight_config.get_weights(role)

        if not self.weight_config.validate_weights(weights):
            raise ValueError(
                f"Invalid scoring weights for role: {role}"
            )

        skill_match = self.normalize_component_score(
            skill_match
        )

        experience_relevance = self.normalize_component_score(
            experience_relevance
        )

        education_alignment = self.normalize_component_score(
            education_alignment
        )

        semantic_similarity = self.normalize_component_score(
            semantic_similarity
        )

        weighted_score = (
            skill_match
            * weights["skill_match"]
        ) + (
            experience_relevance
            * weights["experience_relevance"]
        ) + (
            education_alignment
            * weights["education_alignment"]
        ) + (
            semantic_similarity
            * weights["semantic_similarity"]
        )

        explanations = self.generate_explanation(
            {
                "skill_match": skill_match,
                "experience_relevance": experience_relevance,
                "education_alignment": education_alignment,
                "semantic_similarity": semantic_similarity,
                "weights": weights
            }
        )

        return {
            "role": role or "Unknown",
            "skill_match": round(
                skill_match,
                4
            ),
            "experience_relevance": round(
                experience_relevance,
                4
            ),
            "education_alignment": round(
                education_alignment,
                4
            ),
            "semantic_similarity": round(
                semantic_similarity,
                4
            ),
            "weights": weights,
            "overall_score": round(
                weighted_score,
                4
            ),
            "overall_percentage": round(
                weighted_score * 100,
                2
            ),
            "explanations": explanations
        }

    def __normalize_score(self, score):

        if score is None:
            return 0.0

        try:
            score = float(score)
        except (
            TypeError,
            ValueError
        ):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                score
            )
        )

    def generate_explanation(self, result):

        explanations = []

        components = [
            (
                "Skill Match",
                result["skill_match"],
                result["weights"]["skill_match"]
            ),
            (
                "Experience Relevance",
                result["experience_relevance"],
                result["weights"]["experience_relevance"]
            ),
            (
                "Education Alignment",
                result["education_alignment"],
                result["weights"]["education_alignment"]
            ),
            (
                "Semantic Similarity",
                result["semantic_similarity"],
                result["weights"]["semantic_similarity"]
            )
        ]

        for name, score, weight in components:

            contribution = score * weight

            explanations.append({
                "component": name,
                "score": round(score, 4),
                "weight": weight,
                "contribution": round(
                    contribution,
                    4
                )
            })

        return explanations
    