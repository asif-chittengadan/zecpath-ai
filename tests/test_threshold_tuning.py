from scoring.semantic_matching_engine import SemanticMatchingEngine


engine = SemanticMatchingEngine()


test_cases = [

    {
        "name": "Strong Match",
        "candidate": """
        Data Analyst with experience in Python, SQL and Power BI.
        Built dashboards and analyzed business datasets.
        """,
        "required": """
        Data Analyst with experience using Python, SQL and Power BI
        to analyze data and build business dashboards.
        """,
        "expected": True
    },

    {
        "name": "Related Match",
        "candidate": """
        Data Analyst experienced in Python, SQL and business reporting.
        """,
        "required": """
        Business Intelligence Analyst with experience in Python,
        SQL and analytical reporting.
        """,
        "expected": True
    },

    {
        "name": "Weak Match",
        "candidate": """
        Data Analyst with experience in Excel and Power BI.
        """,
        "required": """
        Machine Learning Engineer experienced in deep learning,
        neural networks and model deployment.
        """,
        "expected": False
    },

    {
        "name": "Unrelated",
        "candidate": """
        Data Analyst working with Python, SQL and Power BI.
        """,
        "required": """
        Civil Engineer experienced in structural design,
        construction planning and AutoCAD.
        """,
        "expected": False
    }
]


print("\n===== THRESHOLD TESTING =====\n")


for test in test_cases:

    score = engine.calculate_similarity(
        test["candidate"],
        test["required"]
    )

    result = engine.classify_similarity(
        score,
        threshold=0.70
    )

    print(
        f'{test["name"]}: '
        f'Score={score} | '
        f'Matched={result["matched"]} | '
        f'Expected={test["expected"]}'
    )