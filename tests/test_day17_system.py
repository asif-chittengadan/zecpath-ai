import json
import os

from scoring.candidate_matching_service import CandidateMatchingService
from scoring.shortlisting_module import ShortlistingModule


TEST_CASES_PATH = "tests/day17_test_cases.json"
CV_FOLDER = "data/labeled_resumes"
JD_FOLDER = "data/parsed_jd"


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    test_cases = load_json(
        TEST_CASES_PATH
    )

    matching_service = CandidateMatchingService()
    shortlisting_module = ShortlistingModule()

    results = []

    print(
        "\n===== DAY 17 ATS SYSTEM TEST =====\n"
    )

    for case in test_cases:

        cv_path = os.path.join(
            CV_FOLDER,
            case["cv_file"]
        )

        jd_path = os.path.join(
            JD_FOLDER,
            case["jd_file"]
        )

        try:

            resume = load_json(
                cv_path
            )

            job_description = load_json(
                jd_path
            )

            result = matching_service.generate_score(
                resume,
                job_description
            )

            score = result["percentage"]

            ai_status = shortlisting_module.classify(
                score
            )

            manual_decision = case[
                "manual_decision"
            ]

            # Map ATS status to manual labels
            decision_mapping = {
                "MATCH": "SHORTLIST",
                "REVIEW": "REVIEW",
                "REJECT": "REJECT"
            }

            expected_ai_decision = decision_mapping.get(
                manual_decision,
                manual_decision
            )

            ai_decision = ai_status

            is_match = (
                expected_ai_decision == ai_decision
            )

            results.append({
                "test_id": case["test_id"],
                "category": case["category"],
                "candidate": result["candidate"],
                "role": result["role"],
                "score": score,
                "manual_decision": manual_decision,
                "ai_decision": ai_decision,
                "matched": is_match
            })

            print(
                f'{case["test_id"]} | '
                f'Candidate: {result["candidate"]} | '
                f'Role: {result["role"]} | '
                f'Score: {score}% | '
                f'Manual: {manual_decision} | '
                f'Expected AI: {expected_ai_decision} | '
                f'Actual AI: {ai_decision} | '
                f'Match: {"YES" if is_match else "NO"}'
            )

        except Exception as error:

            print(
                f'{case["test_id"]} | ERROR | {error}'
            )

    correct = sum(
        1
        for result in results
        if result["matched"]
    )

    total = len(results)

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    true_positive = 0
    false_positive = 0
    false_negative = 0
    true_negative = 0

    mismatches = []

    for result in results:

        manual = result["manual_decision"]
        ai = result["ai_decision"]

        manual_positive = (
            manual == "MATCH"
        )

        ai_positive = (
            ai == "SHORTLIST"
        )

        if manual_positive and ai_positive:
            true_positive += 1

        elif not manual_positive and ai_positive:
            false_positive += 1

        elif manual_positive and not ai_positive:
            false_negative += 1

        else:
            true_negative += 1

        if not result["matched"]:
            mismatches.append(result)

    precision = (
        true_positive /
        (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0
    )

    recall = (
        true_positive /
        (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0
    )

    print(
        "\n===== DAY 17 METRICS =====\n"
    )

    print(
        f"True Positives: {true_positive}"
    )

    print(
        f"False Positives: {false_positive}"
    )

    print(
        f"False Negatives: {false_negative}"
    )

    print(
        f"True Negatives: {true_negative}"
    )

    print(
        f"Precision: {precision * 100:.2f}%"
    )

    print(
        f"Recall: {recall * 100:.2f}%"
    )

    print(
        f"Mismatch Cases: {len(mismatches)}"
    )

    if mismatches:

        print(
            "\n===== MISMATCH CASES =====\n"
        )

        for mismatch in mismatches:

            print(
                f'{mismatch["test_id"]} | '
                f'Manual: {mismatch["manual_decision"]} | '
                f'AI: {mismatch["ai_decision"]} | '
                f'Score: {mismatch["score"]}%'
            )

    else:

        print(
            "No mismatch cases detected."
        )
        
    print(
        "\n===== DAY 17 SUMMARY =====\n"
    )

    print(
        "Total Test Cases:",
        total
    )

    print(
        "Correct Predictions:",
        correct
    )

    print(
        "Incorrect Predictions:",
        total - correct
    )

    print(
        "Accuracy:",
        f"{accuracy * 100:.2f}%"
    )


if __name__ == "__main__":
    main()