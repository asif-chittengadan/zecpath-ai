import json

from interview_ai.hr.communication_feature_analyzer import (
    CommunicationFeatureAnalyzer
)
from interview_ai.hr.communication_scoring_engine import (
    CommunicationScoringEngine
)
from interview_ai.hr.communication_score_normalizer import (
    CommunicationScoreNormalizer
)


def main():
    analyzer = CommunicationFeatureAnalyzer()
    scorer = CommunicationScoringEngine()
    normalizer = CommunicationScoreNormalizer()

    samples = [
        {
            "id": "COMM-001",
            "type": "strong_structured",
            "answer": (
                "First, I understood the project requirements. "
                "Then, I designed the backend using Python and Django. "
                "Finally, I tested the APIs and documented the solution."
            )
        },
        {
            "id": "COMM-002",
            "type": "normal",
            "answer": (
                "I completed my degree in Information Technology "
                "and worked on Python and Django projects."
            )
        },
        {
            "id": "COMM-003",
            "type": "short",
            "answer": "I worked on Python."
        },
        {
            "id": "COMM-004",
            "type": "filler_words",
            "answer": (
                "Um, I basically worked on a Python project "
                "and developed the backend."
            )
        },
        {
            "id": "COMM-005",
            "type": "empty",
            "answer": ""
        }
    ]

    results = []

    for sample in samples:
        features = analyzer.analyze(
            sample["answer"]
        )

        raw_result = scorer.score(
            features
        )

        normalized_score = normalizer.normalize(
            raw_result["score"],
            features["word_count"]
        )

        results.append({
            "id": sample["id"],
            "type": sample["type"],
            "answer": sample["answer"],
            "features": features,
            "raw_score": raw_result["score"],
            "normalized_score": normalized_score
        })

    print("=" * 70)
    print("DAY 35 - COMMUNICATION SCORE SAMPLES")
    print("=" * 70)

    for result in results:
        print()
        print(
            f"{result['id']} - {result['type']}"
        )
        print(
            f"Answer: {result['answer'] or '[EMPTY]'}"
        )
        print(
            f"Raw Score: {result['raw_score']}"
        )
        print(
            f"Normalized Score: "
            f"{result['normalized_score']}"
        )

    print()
    print("=" * 70)

    with open(
        "data/day35_communication_samples.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        "Saved: data/day35_communication_samples.json"
    )


if __name__ == "__main__":
    main()