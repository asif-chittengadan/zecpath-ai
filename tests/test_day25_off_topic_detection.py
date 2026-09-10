from screening_ai.intent_classifier import IntentClassifier


def test_on_topic_experience_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "I have three years of experience in Python development.",
        "experience"
    )

    assert result["intent_label"] == "on_topic"


def test_on_topic_skills_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "I have strong skills in Python, SQL and Machine Learning.",
        "skills"
    )

    assert result["intent_label"] == "on_topic"


def test_off_topic_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "I really enjoy watching cricket and playing games.",
        "experience"
    )

    assert result["intent_label"] == "off_topic"


def test_off_topic_general_conversation():
    classifier = IntentClassifier()

    result = classifier.classify(
        "What is your favorite movie?",
        "education"
    )

    assert result["intent_label"] == "off_topic"


def test_missing_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "",
        "skills"
    )

    assert result["intent_label"] == "missing"


def test_vague_answer():
    classifier = IntentClassifier()

    result = classifier.classify(
        "I have some experience.",
        "experience"
    )

    assert result["intent_label"] == "vague"


if __name__ == "__main__":
    test_on_topic_experience_answer()
    test_on_topic_skills_answer()
    test_off_topic_answer()
    test_off_topic_general_conversation()
    test_missing_answer()
    test_vague_answer()

    print("Day 25 off-topic detection tests passed.")