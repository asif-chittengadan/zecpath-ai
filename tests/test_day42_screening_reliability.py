from scoring.screening_scoring_engine import (
    ScreeningScoringEngine
)


def test_keyword_does_not_match_inside_larger_word():

    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="How much experience do you have?",
        answer="I am inexperienced in this field.",
        category="experience",
        expected_keywords=["experience"]
    )

    assert result["scores"]["relevance"] == 0
    assert result["scores"]["completeness"] == 0


def test_exact_keyword_still_matches():

    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="How much experience do you have?",
        answer="I have 3 years of experience.",
        category="experience",
        expected_keywords=["experience"]
    )

    assert result["scores"]["relevance"] > 0
    assert result["scores"]["completeness"] > 0


def test_multi_word_keyword_matches():

    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="What are your technical skills?",
        answer="I have experience in machine learning.",
        category="skills",
        expected_keywords=["Machine Learning"]
    )

    assert result["scores"]["relevance"] == 10
    assert result["scores"]["completeness"] == 10


def test_unrelated_word_does_not_match_short_keyword():

    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="Do you know C?",
        answer="I work mainly with Java and Python.",
        category="skills",
        expected_keywords=["C"]
    )

    assert result["scores"]["relevance"] == 0
    assert result["scores"]["completeness"] == 0


def test_existing_python_experience_behavior_is_preserved():

    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="How many years of Python experience do you have?",
        answer="I have 3 years of Python experience.",
        category="experience",
        expected_keywords=[
            "Python",
            "3 years",
            "experience"
        ]
    )

    assert result["scores"]["relevance"] == 10
    assert result["scores"]["completeness"] == 10