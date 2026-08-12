from scoring.weight_config import WeightConfig


config = WeightConfig()


roles = [
    "Data Analyst",
    "Data Scientist",
    "Software Developer",
    "Unknown Role"
]


for role in roles:

    weights = config.get_weights(role)

    print(
        f"\nRole: {role}"
    )

    print(
        "Weights:",
        weights
    )

    print(
        "Valid:",
        config.validate_weights(weights)
    )