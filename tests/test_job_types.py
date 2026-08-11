from scoring.semantic_matching_engine import SemanticMatchingEngine


engine = SemanticMatchingEngine()


candidate = """
Data Analyst with experience in Python, SQL, Power BI and Pandas.
Analyzed business datasets, created dashboards and automated reports.
"""


job_types = {

    "Data Analyst": """
    Looking for a Data Analyst with Python, SQL and Power BI experience.
    Candidate should analyze business data and create dashboards.
    """,

    "Data Scientist": """
    Looking for a Data Scientist with experience in Python,
    machine learning, statistics, predictive modeling and data analysis.
    """,

    "Software Engineer": """
    Looking for a Software Engineer with experience in Python,
    software development, APIs, backend systems and programming.
    """,

    "Cloud Engineer": """
    Looking for a Cloud Engineer with experience in AWS,
    cloud infrastructure, Docker, Kubernetes and networking.
    """,

    "Civil Engineer": """
    Looking for a Civil Engineer with experience in structural design,
    construction planning, AutoCAD and site engineering.
    """
}


print("\n===== JOB TYPE VALIDATION =====\n")


results = []

for role, job_description in job_types.items():

    score = engine.calculate_similarity(
        candidate,
        job_description
    )

    result = engine.classify_similarity(
        score,
        threshold=0.70
    )

    results.append({
        "role": role,
        "score": score,
        "matched": result["matched"]
    })

    print(
        f"{role}: "
        f"Score={score} | "
        f"Matched={result['matched']}"
    )