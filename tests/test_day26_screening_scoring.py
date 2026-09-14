from scoring.screening_scoring_engine import ScreeningScoringEngine


def test_complete_relevant_answer():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="How many years of Python experience do you have?",
        answer="I have 3 years of Python experience.",
        category="experience",
        expected_keywords=["Python", "3 years", "experience"]
    )

    assert result["scores"]["clarity"] > 0
    assert result["scores"]["relevance"] > 0
    assert result["scores"]["completeness"] > 0
    assert result["scores"]["consistency"] > 0


def test_empty_answer():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="How many years of Python experience do you have?",
        answer="",
        category="experience",
        expected_keywords=["Python", "experience"]
    )

    assert result["scores"]["clarity"] == 0
    assert result["scores"]["relevance"] == 0
    assert result["scores"]["completeness"] == 0
    assert result["scores"]["consistency"] == 0


def test_partial_answer():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="Tell me about your technical skills.",
        answer="I know Python.",
        category="skills",
        expected_keywords=["Python", "SQL", "Machine Learning"]
    )

    assert result["scores"]["relevance"] > 0
    assert result["scores"]["completeness"] > 0


def test_score_range():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="Tell me about yourself.",
        answer="I am a Python developer with experience in software development.",
        category="introduction"
    )

    for score in result["scores"].values():
        assert 0 <= score <= 10

def test_normalized_scores_are_present():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="How many years of Python experience do you have?",
        answer="I have 3 years of Python experience.",
        category="experience",
        expected_keywords=["Python", "3 years", "experience"]
    )

    normalized_scores = result["normalized_scores"]

    assert "clarity" in normalized_scores
    assert "relevance" in normalized_scores
    assert "completeness" in normalized_scores
    assert "consistency" in normalized_scores


def test_normalized_scores_are_between_zero_and_hundred():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="Tell me about your technical skills.",
        answer="I know Python.",
        category="skills",
        expected_keywords=["Python", "SQL", "Machine Learning"]
    )

    for score in result["normalized_scores"].values():
        assert 0 <= score <= 100


def test_normalization_conversion():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="Tell me about yourself.",
        answer="I am a Python developer.",
        category="introduction"
    )

    scores = result["scores"]
    normalized_scores = result["normalized_scores"]

    for parameter in scores:
        expected = round((scores[parameter] / 10) * 100, 2)
        assert normalized_scores[parameter] == expected
    
def test_aggregate_multiple_question_scores():
    engine = ScreeningScoringEngine()

    question_scores = [
        engine.score_question(
            question="How many years of Python experience do you have?",
            answer="I have 3 years of Python experience.",
            category="experience",
            expected_keywords=["Python", "3 years", "experience"]
        ),
        engine.score_question(
            question="What are your technical skills?",
            answer="I know Python, SQL and Machine Learning.",
            category="skills",
            expected_keywords=["Python", "SQL", "Machine Learning"]
        )
    ]

    result = engine.aggregate_scores(question_scores)

    assert result["questions_evaluated"] == 2
    assert 0 <= result["total_screening_score"] <= 100


def test_aggregate_contains_parameter_scores():
    engine = ScreeningScoringEngine()

    question_scores = [
        engine.score_question(
            question="Tell me about yourself.",
            answer="I am a Python developer with software development experience.",
            category="introduction"
        )
    ]

    result = engine.aggregate_scores(question_scores)

    assert "parameter_scores" in result

    assert "clarity" in result["parameter_scores"]
    assert "relevance" in result["parameter_scores"]
    assert "completeness" in result["parameter_scores"]
    assert "consistency" in result["parameter_scores"]


def test_empty_question_scores():
    engine = ScreeningScoringEngine()

    result = engine.aggregate_scores([])

    assert result["total_screening_score"] == 0.0
    assert result["questions_evaluated"] == 0

def test_explanations_are_present():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="How many years of Python experience do you have?",
        answer="I have 3 years of Python experience.",
        category="experience",
        expected_keywords=["Python", "3 years", "experience"]
    )

    explanations = result["explanations"]

    assert "clarity" in explanations
    assert "relevance" in explanations
    assert "completeness" in explanations
    assert "consistency" in explanations


def test_explanations_are_text():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="What are your technical skills?",
        answer="I know Python.",
        category="skills",
        expected_keywords=["Python", "SQL", "Machine Learning"]
    )

    for explanation in result["explanations"].values():
        assert isinstance(explanation, str)
        assert len(explanation) > 0


def test_empty_answer_has_explanation():
    engine = ScreeningScoringEngine()

    result = engine.score_question(
        question="Tell me about yourself.",
        answer="",
        category="introduction"
    )

    assert result["explanations"]["clarity"] == "No answer was provided."