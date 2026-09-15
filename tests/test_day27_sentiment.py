from screening_ai.sentiment_analyzer import SentimentAnalyzer


def test_positive_sentiment():
    analyzer = SentimentAnalyzer()

    result = analyzer.analyze(
        "I successfully completed the project and improved the system."
    )

    assert result["sentiment"] == "positive"
    assert result["score"] > 0
    assert result["positive_count"] > 0
    assert result["negative_count"] == 0


def test_negative_sentiment():
    analyzer = SentimentAnalyzer()

    result = analyzer.analyze(
        "I struggled with the project and had several problems."
    )

    assert result["sentiment"] == "negative"
    assert result["score"] < 0
    assert result["negative_count"] > 0
    assert result["positive_count"] == 0


def test_neutral_sentiment():
    analyzer = SentimentAnalyzer()

    result = analyzer.analyze(
        "I worked on a Python project."
    )

    assert result["sentiment"] == "neutral"
    assert result["score"] == 0.0


def test_empty_response():
    analyzer = SentimentAnalyzer()

    result = analyzer.analyze("")

    assert result["sentiment"] == "neutral"
    assert result["score"] == 0.0
    assert result["positive_count"] == 0
    assert result["negative_count"] == 0


def test_case_insensitive_sentiment():
    analyzer = SentimentAnalyzer()

    result = analyzer.analyze(
        "I am VERY CONFIDENT and SUCCESSFUL."
    )

    assert result["sentiment"] == "positive"
    assert result["positive_count"] >= 2


def test_negation_handling():
    analyzer = SentimentAnalyzer()

    result = analyzer.analyze(
        "I am not confident about this task."
    )

    assert result["sentiment"] == "negative"
    assert result["negative_count"] > 0


def test_positive_matches_are_returned():
    analyzer = SentimentAnalyzer()

    result = analyzer.analyze(
        "I am confident, motivated and experienced."
    )

    assert "confident" in result["positive_matches"]
    assert "motivated" in result["positive_matches"]
    assert "experienced" in result["positive_matches"]


def test_negative_matches_are_returned():
    analyzer = SentimentAnalyzer()

    result = analyzer.analyze(
        "I was nervous and struggled with the problem."
    )

    assert "nervous" in result["negative_matches"]
    assert "struggled" in result["negative_matches"]