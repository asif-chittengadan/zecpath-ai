from scoring.semantic_matching_engine import SemanticMatchingEngine


engine = SemanticMatchingEngine()

test_cases = [

    {
        "name": "Data Analyst - Strong Match",
        "candidate": """
        Data Analyst with experience in Python, SQL and Power BI.
        Analyzed business datasets and created dashboards.
        """,
        "job": """
        Data Analyst with experience in Python, SQL and Power BI.
        Analyze business data and create dashboards.
        """,
        "expected": True
    },

    {
        "name": "Data Scientist - Weak Match",
        "candidate": """
        Data Analyst with experience in Python, SQL and Power BI.
        """,
        "job": """
        Data Scientist with experience in machine learning,
        deep learning, statistics and predictive modeling.
        """,
        "expected": False
    },

    {
        "name": "Software Engineer - Weak Match",
        "candidate": """
        Data Analyst with experience in Python, SQL and Power BI.
        """,
        "job": """
        Software Engineer developing backend APIs and
        distributed software systems.
        """,
        "expected": False
    },

    {
        "name": "Cloud Engineer - Unrelated",
        "candidate": """
        Data Analyst with experience in Python, SQL and Power BI.
        """,
        "job": """
        Cloud Engineer with AWS, Kubernetes, Docker and
        cloud infrastructure experience.
        """,
        "expected": False
    },

    {
        "name": "Civil Engineer - Unrelated",
        "candidate": """
        Data Analyst with experience in Python, SQL and Power BI.
        """,
        "job": """
        Civil Engineer with structural design,
        construction planning and AutoCAD experience.
        """,
        "expected": False
    }
]


threshold = 0.70

correct = 0

print("\n===== MATCHING ACCURACY REPORT =====\n")

for test in test_cases:

    score = engine.calculate_similarity(
        test["candidate"],
        test["job"]
    )

    matched = score >= threshold

    if matched == test["expected"]:
        correct += 1

    print(
        f'{test["name"]}: '
        f'Score={score:.4f} | '
        f'Expected={test["expected"]} | '
        f'Predicted={matched}'
    )


total = len(test_cases)

accuracy = correct / total

print("\nTotal Test Cases:", total)
print("Correct Predictions:", correct)
print("Incorrect Predictions:", total - correct)
print("Threshold:", threshold)
print("Accuracy:", f"{accuracy:.2%}")