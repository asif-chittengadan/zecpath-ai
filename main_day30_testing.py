import json
from pathlib import Path

from screening_ai.answer_understanding_engine import AnswerUnderstandingEngine


TEST_CASES_PATH = Path("data/day30_test_cases.json")


def load_test_cases():
    with TEST_CASES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)["cases"]


def run_simulations():
    engine = AnswerUnderstandingEngine()
    cases = load_test_cases()

    results = []

    for case in cases:
        semantic = engine.understand(
            answer=case["candidate_answer"],
            category=case["category"],
        )

        intent = semantic.get("intent", {})
        ai_intent = intent.get("intent_label", "")

        expected_intent = case["human_expected_intent"]
        matched = ai_intent == expected_intent

        results.append(
            {
                "case_id": case["case_id"],
                "category": case["category"],
                "candidate_answer": case["candidate_answer"],
                "human_expected_intent": expected_intent,
                "ai_intent": ai_intent,
                "human_expected_action": case["human_expected_action"],
                "intent_match": matched,
                "extracted": {
                    "skills": semantic.get("skills", []),
                    "experience": semantic.get("experience", {}),
                    "availability": semantic.get("availability"),
                    "salary": semantic.get("salary"),
                },
                "reason": case["reason"],
            }
        )

    return results


def print_results(results):
    matches = sum(item["intent_match"] for item in results)
    total = len(results)

    print("=" * 70)
    print("DAY 30 - SIMULATED SCREENING TEST")
    print("=" * 70)

    for item in results:
        status = "PASS" if item["intent_match"] else "MISMATCH"

        print(
            f"{item['case_id']} | "
            f"{item['category']} | "
            f"Expected: {item['human_expected_intent']} | "
            f"AI: {item['ai_intent']} | "
            f"{status}"
        )

    print("=" * 70)
    print(f"Intent matches: {matches}/{total}")

    if total:
        accuracy = (matches / total) * 100
        print(f"Intent agreement: {accuracy:.2f}%")

    print("=" * 70)


def main():
    results = run_simulations()
    print_results(results)


if __name__ == "__main__":
    main()
