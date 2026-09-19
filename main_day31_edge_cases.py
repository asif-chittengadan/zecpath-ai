import json
from pathlib import Path

from screening_ai.response_quality_checker import ResponseQualityChecker
from screening_ai.edge_case_handler import EdgeCaseHandler


BASE_DIR = Path(__file__).resolve().parent


def load_rules():
    with open(
        BASE_DIR / "config" / "edge_case_rules.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def main():
    rules = load_rules()
    checker = ResponseQualityChecker(rules)
    handler = EdgeCaseHandler(rules)

    scenarios = [
        {
            "name": "Valid response",
            "answer": "I have two years of Python experience.",
            "metadata": {"audio_confidence": 0.95, "noise_score": 0.10}
        },
        {
            "name": "Poor audio",
            "answer": "I have two years of experience.",
            "metadata": {"audio_confidence": 0.40}
        },
        {
            "name": "Background noise",
            "answer": "I have two years of experience.",
            "metadata": {"noise_score": 0.90}
        },
        {
            "name": "Missing answer",
            "answer": "",
            "metadata": {}
        },
        {
            "name": "Language mixing",
            "answer": "Haan, I have two years of experience.",
            "metadata": {}
        }
    ]

    print("\nDay 31 Edge Case Demo")
    print("=" * 55)

    for scenario in scenarios:
        quality = checker.check(
            scenario["answer"],
            scenario["metadata"]
        )
        decision = handler.handle(quality, {})

        print(f"\nScenario: {scenario['name']}")
        print(f"Issues: {quality['issues']}")
        print(f"Action: {decision['action']}")
        print(f"Message: {decision['message']}")


if __name__ == "__main__":
    main()
