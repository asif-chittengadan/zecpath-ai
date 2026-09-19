import json
from pathlib import Path

from scoring.eligibility_decision_engine import EligibilityDecisionEngine


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "day30_false_rejection_edge_cases.json"
RULES_PATH = Path("config/eligibility_rules.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    cases = load_json(DATA_PATH)
    all_rules = load_json(RULES_PATH)
    engine = EligibilityDecisionEngine()

    results = []

    for case in cases:
        role = case["role"]
        result = engine.evaluate(case["candidate"], all_rules[role])

        expected = case["expected_decision"]
        actual = result["decision"]
        matched = actual == expected

        results.append({
            "case_id": case["case_id"],
            "role": role,
            "purpose": case["purpose"],
            "expected_decision": expected,
            "actual_decision": actual,
            "match": matched,
            "failed_rules": result["failed_rules"],
            "review_rules": result["review_rules"],
        })

        status = "PASS" if matched else "FAIL"
        print(
            f"{status} | {case['case_id']} | {role} | "
            f"Expected={expected} | Actual={actual}"
        )

        if result["failed_rules"]:
            print(f"      Failed: {result['failed_rules']}")
        if result["review_rules"]:
            print(f"      Review: {result['review_rules']}")

    total = len(results)
    matches = sum(item["match"] for item in results)
    agreement = matches / total * 100 if total else 0

    false_rejection_candidates = [
        item for item in results
        if item["expected_decision"] in {"Eligible", "Review"}
        and item["actual_decision"] == "Rejected"
    ]

    print("\nDay 30 False-Rejection Edge Test")
    print("=" * 55)
    print(f"Cases: {total}")
    print(f"Matches: {matches}")
    print(f"Agreement: {agreement:.2f}%")
    print(f"False-rejection candidates: {len(false_rejection_candidates)}")

    if false_rejection_candidates:
        print("\nPotential false rejections:")
        for item in false_rejection_candidates:
            print(
                f"- {item['case_id']}: {item['role']} | "
                f"{item['failed_rules']}"
            )
    else:
        print("\nNo false-rejection candidates found in this edge-case set.")

    output_path = BASE_DIR / "day30_false_rejection_edge_results.json"
    output_path.write_text(
        json.dumps(
            {
                "total_cases": total,
                "matches": matches,
                "agreement_percent": round(agreement, 2),
                "false_rejection_candidates": len(false_rejection_candidates),
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
