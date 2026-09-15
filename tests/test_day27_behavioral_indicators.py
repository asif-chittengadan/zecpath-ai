from screening_ai.behavioral_indicators import (
    BehavioralIndicatorAnalyzer
)


def test_clear_response_behavioral_indicators():
    analyzer = BehavioralIndicatorAnalyzer()

    result = analyzer.analyze(
        "I have three years of experience in Python and SQL."
    )

    indicators = result["behavioral_indicators"]

    assert indicators["hesitation_detected"] is False
    assert indicators["uncertainty_detected"] is False
    assert indicators["contradiction_detected"] is False
    assert indicators["response_length"] != "empty"
    assert 0 <= result["communication_strength"]["score"] <= 100


def test_hesitation_behavioral_indicator():
    analyzer = BehavioralIndicatorAnalyzer()

    result = analyzer.analyze(
        "Um, I have, um, three years of experience."
    )

    assert (
        result["behavioral_indicators"]
        ["hesitation_detected"]
        is True
    )


def test_uncertainty_behavioral_indicator():
    analyzer = BehavioralIndicatorAnalyzer()

    result = analyzer.analyze(
        "I am not sure, but I think I have around two years of experience."
    )

    assert (
        result["behavioral_indicators"]
        ["uncertainty_detected"]
        is True
    )


def test_contradiction_behavioral_indicator():
    analyzer = BehavioralIndicatorAnalyzer()

    result = analyzer.analyze(
        "I have three years of experience. "
        "Actually, I want to correct that."
    )

    assert (
        result["behavioral_indicators"]
        ["contradiction_detected"]
        is True
    )


def test_sentiment_is_included():
    analyzer = BehavioralIndicatorAnalyzer()

    result = analyzer.analyze(
        "I successfully completed the project."
    )

    assert "sentiment" in result
    assert result["sentiment"]["sentiment"] == "positive"

    assert (
        result["behavioral_indicators"]["sentiment"]
        == "positive"
    )


def test_response_pace_is_included():
    analyzer = BehavioralIndicatorAnalyzer()

    result = analyzer.analyze(
        "I have three years of experience in Python and SQL.",
        duration_seconds=10
    )

    assert (
        result["behavioral_indicators"]
        ["response_pace_wpm"]
        is not None
    )

    assert (
        result["behavioral_indicators"]
        ["response_pace_wpm"]
        > 0
    )


def test_communication_strength_is_bounded():
    analyzer = BehavioralIndicatorAnalyzer()

    result = analyzer.analyze(
        "Um, maybe I think I could possibly do it. "
        "Actually, let me correct that."
    )

    score = result["communication_strength"]["score"]

    assert 0 <= score <= 100


def test_empty_response_behavioral_indicators():
    analyzer = BehavioralIndicatorAnalyzer()

    result = analyzer.analyze("")

    assert result["behavioral_indicators"]["hesitation_detected"] is False
    assert result["behavioral_indicators"]["uncertainty_detected"] is False
    assert result["behavioral_indicators"]["contradiction_detected"] is False
    assert result["behavioral_indicators"]["response_length"] == "empty"
    assert result["communication_strength"]["score"] == 0.0