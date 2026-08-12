import json


class WeightConfig:

    def __init__(
        self,
        config_path="data/scoring_weights.json"
    ):

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.weights = json.load(file)

    def get_weights(self, role):

        if not role:
            return self.weights["default"]

        role = role.strip().lower()

        for configured_role, weights in self.weights.items():

            if configured_role.lower() == role:
                return weights

        return self.weights["default"]

    def validate_weights(self, weights):

        required_keys = [
            "skill_match",
            "experience_relevance",
            "education_alignment",
            "semantic_similarity"
        ]

        for key in required_keys:

            if key not in weights:
                return False

            if not isinstance(
                weights[key],
                (int, float)
            ):
                return False

            if not 0 <= weights[key] <= 1:
                return False

        total = sum(
            weights[key]
            for key in required_keys
        )

        return abs(total - 1.0) < 0.0001