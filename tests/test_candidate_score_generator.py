from scoring.candidate_score_generator import CandidateScoreGenerator


generator = CandidateScoreGenerator()


result = generator.generate(
    candidate_name="Asif C",
    role="Data Analyst",
    skill_match=0.90,
    experience_relevance=0.80,
    education_alignment=1.00,
    semantic_similarity=0.85
)


print("\n===== CANDIDATE SCORE =====\n")

print("Candidate:")
print(result["candidate"])

print("\nRole:")
print(result["role"])

print("\nScore:")
print(result["score"])

print("\nPercentage:")
print(
    f'{result["percentage"]}%'
)

print("\nComponents:")
print(result["components"])

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