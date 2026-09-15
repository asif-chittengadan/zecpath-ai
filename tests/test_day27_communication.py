from screening_ai.communication import CommunicationAnalyzer


def test_clear_response():
    analyzer = CommunicationAnalyzer()

    result = analyzer.analyze(
        "I have three years of experience in Python and SQL."
    )

    assert result["word_count"] > 0
    assert result["hesitation"]["detected"] is False
    assert result["uncertainty"]["detected"] is False
    assert result["communication_strength"]["score"] > 0


def test_hesitation_detection():
    analyzer = CommunicationAnalyzer()

    result = analyzer.analyze(
        "Um, I have, um, three years of experience."
    )

    assert result["hesitation"]["detected"] is True
    assert result["hesitation"]["count"] == 2
    assert "um" in result["hesitation"]["filler_words"]


def test_uncertainty_detection():
    analyzer = CommunicationAnalyzer()

    result = analyzer.analyze(
        "I am not sure, but I think I have around two years of experience."
    )

    assert result["uncertainty"]["detected"] is True
    assert result["uncertainty"]["count"] >= 1


def test_contradiction_detection():
    analyzer = CommunicationAnalyzer()

    result = analyzer.analyze(
        "I have three years of experience. Actually, I want to correct that."
    )

    assert result["contradictions"]["detected"] is True
    assert result["contradictions"]["count"] >= 1


def test_response_length():
    analyzer = CommunicationAnalyzer()

    result = analyzer.analyze(
        "Yes."
    )

    assert result["word_count"] == 1
    assert result["response_length"]["category"] == "very_short"


def test_response_pace():
    analyzer = CommunicationAnalyzer()

    response = (
        "I have three years of experience working with Python "
        "and SQL on multiple software development projects."
    )

    result = analyzer.analyze(
        response,
        duration_seconds=10
    )

    assert result["response_pace_wpm"] is not None
    assert result["response_pace_wpm"] > 0


def test_missing_duration():
    analyzer = CommunicationAnalyzer()

    result = analyzer.analyze(
        "I have experience in Python."
    )

    assert result["response_pace_wpm"] is None


def test_empty_response():
    analyzer = CommunicationAnalyzer()

    result = analyzer.analyze("")

    assert result["word_count"] == 0
    assert result["response_length"]["category"] == "empty"
    assert result["communication_strength"]["score"] == 0.0