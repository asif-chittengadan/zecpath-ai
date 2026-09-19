import json
from pathlib import Path

from scoring.eligibility_decision_engine import EligibilityDecisionEngine


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "day30_eligibility_threshold_cases.json"
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
        candidate = case["candidate"]
        rules = all_rules[role]

        result = engine.evaluate(candidate, rules)
        actual = result["decision"]
        expected = case["expected_baseline"]

        results.append({
            "case_id": case["case_id"],
            "role": role,
            "focus": case["focus"],
            "ats_score": candidate.get("ats_score"),
            "expected_decision": expected,
            "actual_decision": actual,
            "match": actual == expected,
            "failed_rules": result["failed_rules"],
            "review_rules": result["review_rules"],
        })

    matches = sum(item["match"] for item in results)
    total = len(results)
    agreement = (matches / total * 100) if total else 0

    print("\nDay 30 Eligibility Threshold Baseline")
    print("=" * 55)

    for item in results:
        status = "PASS" if item["match"] else "FAIL"
        print(
            f'{status} | {item["case_id"]} | {item["role"]} | '
            f'ATS={item["ats_score"]} | '
            f'Expected={item["expected_decision"]} | '
            f'Actual={item["actual_decision"]}'
        )

        if item["failed_rules"]:
            print(f'      Failed: {item["failed_rules"]}')
        if item["review_rules"]:
            print(f'      Review: {item["review_rules"]}')

    print("\nSummary")
    print("-" * 55)
    print(f"Cases: {total}")
    print(f"Matches: {matches}")
    print(f"Agreement: {agreement:.2f}%")

    output_path = BASE_DIR / "day30_eligibility_baseline_results.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            {
                "total_cases": total,
                "matches": matches,
                "agreement_percent": round(agreement, 2),
                "results": results,
            },
            file,
            indent=2,
        )

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
