import copy
import json
from collections import defaultdict
from pathlib import Path

from scoring.eligibility_decision_engine import EligibilityDecisionEngine


BASE_DIR = Path(__file__).resolve().parent
RULES_PATH = BASE_DIR / "config" / "eligibility_rules.json"
CASE_FILES = [
    BASE_DIR / "data" / "day30_eligibility_threshold_cases.json",
    BASE_DIR / "data" / "day30_false_rejection_edge_cases.json",
]
OUTPUT_PATH = BASE_DIR / "reports" / "day54_threshold_calibration.json"

POSITIVE = "Eligible"
NEGATIVE = "Rejected"


def load_cases():
    cases_by_role = defaultdict(list)

    for path in CASE_FILES:
        with path.open("r", encoding="utf-8") as file:
            cases = json.load(file)

        for case in cases:
            expected = case.get(
                "expected_baseline",
                case.get("expected_decision"),
            )
            cases_by_role[case["role"]].append(
                {
                    **case,
                    "expected_decision": expected,
                    "source_file": path.name,
                }
            )

    return cases_by_role


def evaluate_threshold(engine, cases, role_rules, threshold):
    trial_rules = copy.deepcopy(role_rules)
    trial_rules["minimum_ats_score"] = threshold
    results = []

    for case in cases:
        prediction = engine.evaluate(
            case["candidate"],
            trial_rules,
        )["decision"]

        results.append(
            {
                "case_id": case["case_id"],
                "source_file": case["source_file"],
                "expected": case["expected_decision"],
                "actual": prediction,
                "match": prediction == case["expected_decision"],
            }
        )

    false_positives = [
        item for item in results
        if item["expected"] == NEGATIVE and item["actual"] == POSITIVE
    ]
    false_negatives = [
        item for item in results
        if item["expected"] == POSITIVE and item["actual"] == NEGATIVE
    ]
    mismatches = [item for item in results if not item["match"]]

    return {
        "matches": len(results) - len(mismatches),
        "total_cases": len(results),
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
        "mismatches": mismatches,
    }


def main():
    with RULES_PATH.open("r", encoding="utf-8") as file:
        rules_by_role = json.load(file)

    cases_by_role = load_cases()
    engine = EligibilityDecisionEngine()
    role_reports = {}

    for role, cases in cases_by_role.items():
        if role not in rules_by_role:
            print(f"Skipping {role}: no eligibility rules found.")
            continue

        current_threshold = rules_by_role[role]["minimum_ats_score"]
        sweep = []

        for threshold in range(101):
            metrics = evaluate_threshold(
                engine,
                cases,
                rules_by_role[role],
                threshold,
            )
            sweep.append({"threshold": threshold, **metrics})

        best_match_count = max(item["matches"] for item in sweep)
        best_options = [
            item for item in sweep
            if item["matches"] == best_match_count
        ]

        # Keep the existing cutoff when it ties for best agreement.
        recommended = min(
            best_options,
            key=lambda item: (
                item["threshold"] != current_threshold,
                abs(item["threshold"] - current_threshold),
                item["threshold"],
            ),
        )

        current = next(
            item for item in sweep
            if item["threshold"] == current_threshold
        )

        role_reports[role] = {
            "current_threshold": current_threshold,
            "current_results": current,
            "recommended_threshold": recommended["threshold"],
            "recommended_results": recommended,
            "threshold_change_suggested": (
                recommended["threshold"] != current_threshold
            ),
        }

    report = {
        "purpose": "Threshold sweep using designed repository test cases.",
        "roles": role_reports,
        "note": (
            "This report does not modify eligibility_rules.json. "
            "These cases are not real-world candidate outcomes."
        ),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    for role, item in role_reports.items():
        current = item["current_results"]
        recommended = item["recommended_results"]
        print(
            f"{role}: current {item['current_threshold']} "
            f"({current['matches']}/{current['total_cases']} matches); "
            f"recommended {item['recommended_threshold']} "
            f"({recommended['matches']}/{recommended['total_cases']} matches)"
        )

    print(f"Report saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()