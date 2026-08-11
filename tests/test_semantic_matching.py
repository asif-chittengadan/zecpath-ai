from scoring.semantic_matching_engine import SemanticMatchingEngine


engine = SemanticMatchingEngine()


candidate_skills = [
    "Python",
    "SQL",
    "Power BI",
    "Pandas"
]

required_skills = [
    "Python",
    "SQL",
    "Power BI",
    "Tableau"
]


candidate_experience = """
Data Analyst with experience in Python, SQL and Power BI.
Analyzed business datasets and created analytical dashboards.
"""

required_experience = """
Experience analyzing business data using Python and SQL
and developing BI dashboards.
"""


candidate_projects = [
    "Built a sales analytics dashboard using Power BI, DAX and Power Query.",
    "Developed interactive reports for business performance analysis."
]

required_projects = [
    "Experience developing BI dashboards and analytical reporting solutions."
]


result = engine.calculate_resume_jd_score(
    candidate_skills,
    required_skills,
    candidate_experience,
    required_experience,
    candidate_projects,
    required_projects
)


print("Skills Score:", result["skills_score"])
print("Experience Score:", result["experience_score"])
print("Projects Score:", result["projects_score"])
print("Overall Score:", result["overall_score"])
print("Threshold:", result["threshold"])
print("Matched:", result["matched"])