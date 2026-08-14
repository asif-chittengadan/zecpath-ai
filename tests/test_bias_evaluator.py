from scoring.bias_evaluator import BiasEvaluator


candidates = [
    {
        "candidate": "Candidate A",
        "score": 0.90
    },
    {
        "candidate": "Candidate B",
        "score": 0.72
    },
    {
        "candidate": "Candidate C",
        "score": 0.51
    }
]


evaluator = BiasEvaluator()

result = evaluator.evaluate(
    candidates
)

print("\n===== BIAS EVALUATION =====")

print(
    "Candidate Count:",
    result["candidate_count"]
)

print(
    "Score Range:",
    result["score_range"]
)

print(
    "Bias Indicators:",
    result["bias_indicators"]
)