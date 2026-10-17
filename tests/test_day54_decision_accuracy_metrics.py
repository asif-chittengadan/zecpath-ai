
from scoring.recommendation import RecommendationAIEngine


def test_decision_accuracy_metrics():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    # Known expected outcomes for this controlled test dataset.
    dataset = [
        (90, "Selected"),
        (80, "Selected"),
        (75, "Selected"),
        (60, "Hold / Review"),
        (50, "Hold / Review"),
        (40, "Rejected"),
        (20, "Rejected"),
    ]

    predictions = [
        engine.evaluate(score)["decision"]
        for score, _ in dataset
    ]

    actual = [expected for _, expected in dataset]

    correct = sum(
        predicted == expected
        for predicted, expected in zip(predictions, actual)
    )

    accuracy = correct / len(dataset)

    assert len(predictions) == len(dataset)
    assert 0 <= accuracy <= 1
    assert accuracy == 1.0


def test_decision_class_distribution():
    engine = RecommendationAIEngine(
        selection_threshold=75,
        review_threshold=50,
    )

    scores = [90, 80, 60, 50, 40, 20]

    decisions = [
        engine.evaluate(score)["decision"]
        for score in scores
    ]

    assert decisions.count("Selected") == 2
    assert decisions.count("Hold / Review") == 2
    assert decisions.count("Rejected") == 2
