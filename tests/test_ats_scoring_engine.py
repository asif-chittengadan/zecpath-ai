from scoring.ats_scoring_engine import ATSScoringEngine


engine = ATSScoringEngine()


result = engine.calculate_score(
    role="Data Analyst",
    skill_match=0.90,
    experience_relevance=0.80,
    education_alignment=1.00,
    semantic_similarity=0.85
)


print("\n===== ATS SCORING RESULT =====\n")

print("Role:")
print(result["role"])

print("\nComponent Scores:")

print(
    "Skill Match:",
    result["skill_match"]
)

print(
    "Experience Relevance:",
    result["experience_relevance"]
)

print(
    "Education Alignment:",
    result["education_alignment"]
)

print(
    "Semantic Similarity:",
    result["semantic_similarity"]
)

print("\nWeights:")
print(result["weights"])

print("\nOverall Score:")
print(result["overall_score"])

print("\nOverall Percentage:")
print(
    f'{result["overall_percentage"]}%'
)
print("\n===== EXPLANATION =====\n")

for explanation in result["explanations"]:

    print(
        f'{explanation["component"]}: '
        f'Score={explanation["score"]}, '
        f'Weight={explanation["weight"]}, '
        f'Contribution={explanation["contribution"]}'
    )
print("\n===== MISSING DATA TESTS =====\n")


test_cases = [

    {
        "name": "Missing Education",
        "role": "Data Analyst",
        "skill_match": 0.90,
        "experience_relevance": 0.80,
        "education_alignment": None,
        "semantic_similarity": 0.85
    },

    {
        "name": "Missing Experience",
        "role": "Data Analyst",
        "skill_match": 0.90,
        "experience_relevance": None,
        "education_alignment": 1.00,
        "semantic_similarity": 0.85
    },

    {
        "name": "Missing Skills",
        "role": "Data Analyst",
        "skill_match": None,
        "experience_relevance": 0.80,
        "education_alignment": 1.00,
        "semantic_similarity": 0.85
    },

    {
        "name": "All Data Missing",
        "role": "Data Analyst",
        "skill_match": None,
        "experience_relevance": None,
        "education_alignment": None,
        "semantic_similarity": None
    }
]


for test in test_cases:

    result = engine.calculate_score(
        role=test["role"],
        skill_match=test["skill_match"],
        experience_relevance=test["experience_relevance"],
        education_alignment=test["education_alignment"],
        semantic_similarity=test["semantic_similarity"]
    )

    print(
        f'{test["name"]}: '
        f'Score={result["overall_score"]} | '
        f'Percentage={result["overall_percentage"]}%'
    )