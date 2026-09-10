from screening_ai.intent_classifier import IntentClassifier


def test_empty_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "",
        "experience"
    )

    assert result["intent_label"] == "missing"


def test_whitespace_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "   ",
        "skills"
    )

    assert result["intent_label"] == "missing"


def test_none_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        None,
        "education"
    )

    assert result["intent_label"] == "missing"


def test_not_sure_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "I am not sure.",
        "experience"
    )

    assert result["intent_label"] == "vague"


def test_maybe_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "Maybe.",
        "skills"
    )

    assert result["intent_label"] == "vague"


def test_some_experience_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "I have some experience.",
        "experience"
    )

    assert result["intent_label"] == "vague"


def test_not_much_experience_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "I don't have much experience.",
        "experience"
    )

    assert result["intent_label"] == "vague"


if __name__ == "__main__":
    test_empty_answer()
    test_whitespace_answer()
    test_none_answer()
    test_not_sure_answer()
    test_maybe_answer()
    test_some_experience_answer()
    test_not_much_experience_answer()

    print("Day 25 missing/vague detection tests passed.")