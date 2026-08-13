import json

from scoring.candidate_matching_service import CandidateMatchingService


CV_PATH = "data/labeled_resumes/cv ASIF.json"

JD_PATH = "data/parsed_jd/JD_Solution Consultant Apprentice(1).json"


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    resume = load_json(CV_PATH)

    job_description = load_json(
        JD_PATH
    )

    service = CandidateMatchingService()

    result = service.generate_score(
        resume,
        job_description
    )

    print("\n===== ACTUAL CV ↔ JD ATS SCORE =====\n")

    print(
        "Candidate:",
        result["candidate"]
    )

    print(
        "Role:",
        result["role"]
    )

    print(
        "\nSkill Match:",
        result["components"]["skill_match"]
    )

    print(
        "Experience Relevance:",
        result["components"][
            "experience_relevance"
        ]
    )

    print(
        "Education Alignment:",
        result["components"][
            "education_alignment"
        ]
    )

    print(
        "Semantic Similarity:",
        result["components"][
            "semantic_similarity"
        ]
    )

    print(
        "\nOverall Score:",
        result["score"]
    )

    print(
        "Overall Percentage:",
        f'{result["percentage"]}%'
    )

    print("\nWeights:")

    print(result["weights"])

    print("\nExplanations:")

    for explanation in result["explanations"]:

        print(
            f'{explanation["component"]}: '
            f'Score={explanation["score"]}, '
            f'Weight={explanation["weight"]}, '
            f'Contribution={explanation["contribution"]}'
        )


if __name__ == "__main__":
    main()