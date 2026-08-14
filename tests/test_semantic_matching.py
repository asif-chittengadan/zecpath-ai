from scoring.semantic_matching_engine import SemanticMatchingEngine


engine = SemanticMatchingEngine()

candidate_skills = [
    "Python",
    "JavaScript",
    "Power BI"
]

required_skills = [
    "Python",
    "JavaScript",
    "Business Intelligence"
]

result = engine.calculate_skill_similarity(
    candidate_skills,
    required_skills
)

print(result)