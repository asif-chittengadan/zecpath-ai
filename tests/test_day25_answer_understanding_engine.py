from screening_ai.answer_understanding_engine import (
    AnswerUnderstandingEngine,
)


def test_complete_answer_understanding():
    engine = AnswerUnderstandingEngine()

    answer = (
        "I have 3 years of experience in Python and SQL. "
        "I can join immediately and I am expecting 8 LPA."
    )

    result = engine.understand(
        answer,
        "experience"
    )

    assert result["answer"] == answer
    assert result["category"] == "experience"

    assert result["intent"]["intent_label"] == "on_topic"

    assert "Python" in result["skills"]
    assert "SQL" in result["skills"]

    assert result["experience"]["minimum"] == 3

    assert result["availability"]["available"] is True
    assert result["availability"]["availability_type"] == "immediate"

    assert result["salary"]["salary_mentioned"] is True
    assert result["salary"]["minimum_lpa"] == 8
    assert result["salary"]["maximum_lpa"] == 8


def test_skill_answer():
    engine = AnswerUnderstandingEngine()

    answer = (
        "I am skilled in Python, SQL and Machine Learning."
    )

    result = engine.understand(
        answer,
        "skills"
    )

    assert result["intent"]["intent_label"] == "on_topic"
    assert "Python" in result["skills"]
    assert "SQL" in result["skills"]
    assert "Machine Learning" in result["skills"]


def test_missing_answer():
    engine = AnswerUnderstandingEngine()

    result = engine.understand(
        "",
        "experience"
    )

    assert result["intent"]["intent_label"] == "missing"
    assert result["skills"] == []
    assert result["experience"]["minimum"] is None
    assert result["salary"]["salary_mentioned"] is False


def test_structured_availability_answer():
    engine = AnswerUnderstandingEngine()

    answer = "I am currently serving a 30-day notice period."

    result = engine.understand(
        answer,
        "availability"
    )

    assert result["intent"]["intent_label"] == "on_topic"
    assert result["availability"]["available"] is True
    assert result["availability"]["availability_type"] == "notice_period"
    assert result["availability"]["notice_period_days"] == 30


if __name__ == "__main__":
    test_complete_answer_understanding()
    test_skill_answer()
    test_missing_answer()
    test_structured_availability_answer()

    print("Day 25 answer understanding engine tests passed.")