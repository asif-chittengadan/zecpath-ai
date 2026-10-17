import json
from pathlib import Path

from scoring.eligibility_decision_engine import EligibilityDecisionEngine


BASE_DIR = Path(__file__).resolve().parent
RULES_PATH = BASE_DIR / "config" / "eligibility_rules.json"
CASE_FILES = [
    BASE_DIR / "data" / "day30_eligibility_threshold_cases.json",
    BASE_DIR / "data" / "day30_false_rejection_edge_cases.json",
]
OUTPUT_PATH = BASE_DIR / "reports" / "day54_error_analysis.json"

POSITIVE = "Eligible"
NEGATIVE = "Rejected"


def percentage(numerator, denominator):
    if denominator == 0:
        return None
    return round(numerator / denominator * 100, 2)


def main():
    with RULES_PATH.open("r", encoding="utf-8") as file:
        rules_by_role = json.load(file)

    engine = EligibilityDecisionEngine()
    results = []

    for case_path in CASE_FILES:
        with case_path.open("r", encoding="utf-8") as file:
            cases = json.load(file)

        for case in cases:
            role = case["role"]
            expected = case.get(
                "expected_baseline",
                case.get("expected_decision"),
            )

            if role not in rules_by_role:
                raise ValueError(f"No eligibility rules found for role: {role}")

            actual_result = engine.evaluate(
                case["candidate"],
                rules_by_role[role],
            )
            actual = actual_result["decision"]

            results.append(
                {
                    "case_id": case["case_id"],
                    "source_file": case_path.name,
                    "role": role,
                    "expected": expected,
                    "actual": actual,
                    "match": expected == actual,
                    "failed_rules": actual_result["failed_rules"],
                    "review_rules": actual_result["review_rules"],
                }
            )

    labels = sorted(
        {
            item[label_key]
            for item in results
            for label_key in ("expected", "actual")
        }
    )

    confusion_matrix = {
        expected: {actual: 0 for actual in labels}
        for expected in labels
    }

    for item in results:
        confusion_matrix[item["expected"]][item["actual"]] += 1

    # Binary metrics include only Eligible and Rejected outcomes.
    # Review remains a separate outcome.
    binary_results = [
        item
        for item in results
        if item["expected"] in {POSITIVE, NEGATIVE}
        and item["actual"] in {POSITIVE, NEGATIVE}
    ]

    true_positives = sum(
        item["expected"] == POSITIVE and item["actual"] == POSITIVE
        for item in binary_results
    )
    true_negatives = sum(
        item["expected"] == NEGATIVE and item["actual"] == NEGATIVE
        for item in binary_results
    )

    false_positive_cases = [
        item for item in results
        if item["expected"] == NEGATIVE and item["actual"] == POSITIVE
    ]
    false_negative_cases = [
        item for item in results
        if item["expected"] == POSITIVE and item["actual"] == NEGATIVE
    ]
    review_mismatch_cases = [
        item for item in results
        if item["expected"] != item["actual"]
        and "Review" in {item["expected"], item["actual"]}
    ]
    mismatches = [item for item in results if not item["match"]]

    report = {
        "positive_class": POSITIVE,
        "negative_class": NEGATIVE,
        "total_cases": len(results),
        "matches": sum(item["match"] for item in results),
        "overall_agreement_percent": percentage(
            sum(item["match"] for item in results),
            len(results),
        ),
        "binary_case_count": len(binary_results),
        "confusion_matrix_expected_rows_actual_columns": confusion_matrix,
        "binary_metrics_percent": {
            "accuracy": percentage(
                true_positives + true_negatives,
                len(binary_results),
            ),
            "precision": percentage(
                true_positives,
                true_positives + len(false_positive_cases),
            ),
            "recall": percentage(
                true_positives,
                true_positives + len(false_negative_cases),
            ),
        },
        "false_positive_cases": false_positive_cases,
        "false_negative_cases": false_negative_cases,
        "review_mismatch_cases": review_mismatch_cases,
        "all_mismatches": mismatches,
        "note": (
            "These are designed repository test cases, not real-world "
            "candidate outcomes."
        ),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"Cases analyzed: {report['total_cases']}")
    print(f"False positives: {len(false_positive_cases)}")
    print(f"False negatives: {len(false_negative_cases)}")
    print(f"Review mismatches: {len(review_mismatch_cases)}")
    print(f"All mismatches: {len(mismatches)}")
    print(f"Report saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()