from screening_ai.screening_report_builder import (
    ScreeningReportBuilder
)


def create_builder():
    return ScreeningReportBuilder()


def create_answer_results():
    return [
        {
            "category": "experience",
            "question": "How many years of experience do you have?",
            "answer": "I have two years of experience."
        },
        {
            "category": "skills",
            "question": "What technical skills do you have?",
            "answer": "Python and SQL",
            "extracted_skills": [
                "Python",
                "SQL"
            ]
        },
        {
            "category": "availability",
            "question": "Are you available immediately?",
            "answer": "Yes, I am available immediately."
        },
        {
            "category": "salary",
            "question": "What are your salary expectations?",
            "answer": "6 LPA"
        }
    ]


def create_behavioral_analysis():
    return {
        "communication": {
            "communication_strength": {
                "score": 85
            },
            "hesitation": {
                "detected": False
            },
            "uncertainty": {
                "detected": False
            },
            "contradiction": {
                "detected": False
            },
            "response_length": {
                "category": "adequate"
            },
            "response_pace": {
                "category": "normal"
            }
        },
        "sentiment": {
            "sentiment": "positive",
            "score": 20
        },
        "behavioral_strength": 86
    }


def create_screening_score():
    return {
        "total_screening_score": 82.5,
        "questions_evaluated": 4,
        "parameter_scores": {
            "clarity": 85,
            "relevance": 84,
            "completeness": 80,
            "consistency": 81
        }
    }


def test_report_builder_returns_structured_report():
    builder = create_builder()

    report = builder.build_report(
        candidate={
            "name": "Test Candidate",
            "email": "test@example.com",
            "role": "Data Analyst"
        },
        answer_results=create_answer_results(),
        screening_score=create_screening_score(),
        behavioral_analysis=create_behavioral_analysis()
    )

    assert isinstance(report, dict)
    assert "candidate_information" in report
    assert "key_answers" in report
    assert "screening_score" in report
    assert "communication_signals" in report
    assert "strengths" in report
    assert "risks" in report
    assert "missing_data" in report


def test_key_answers_are_extracted():
    builder = create_builder()

    report = builder.build_report(
        answer_results=create_answer_results()
    )

    assert len(report["key_answers"]) == 4


def test_salary_is_highlighted():
    builder = create_builder()

    report = builder.build_report(
        answer_results=create_answer_results()
    )

    assert report["salary_expectation"] == "6 LPA"


def test_availability_is_highlighted():
    builder = create_builder()

    report = builder.build_report(
        answer_results=create_answer_results()
    )

    assert (
        report["availability"]
        == "Yes, I am available immediately."
    )


def test_skills_are_highlighted():
    builder = create_builder()

    report = builder.build_report(
        answer_results=create_answer_results()
    )

    assert "Python" in report[
        "skill_confirmations"
    ]

    assert "SQL" in report[
        "skill_confirmations"
    ]


def test_screening_score_is_included():
    builder = create_builder()

    report = builder.build_report(
        screening_score=create_screening_score()
    )

    assert (
        report["screening_score"]["total_score"]
        == 82.5
    )


def test_behavioral_signals_are_included():
    builder = create_builder()

    report = builder.build_report(
        behavioral_analysis=create_behavioral_analysis()
    )

    signals = report[
        "communication_signals"
    ]

    assert (
        signals["communication_strength"]["score"]
        == 85
    )

    assert (
        signals["sentiment"]["sentiment"]
        == "positive"
    )


def test_missing_data_is_detected():
    builder = create_builder()

    report = builder.build_report(
        answer_results=[
            {
                "category": "experience",
                "answer": "Two years"
            }
        ]
    )

    assert "salary" in report["missing_data"]
    assert "availability" in report["missing_data"]
    assert "skills" in report["missing_data"]


def test_risk_is_detected_for_low_score():
    builder = create_builder()

    report = builder.build_report(
        screening_score={
            "total_screening_score": 40,
            "questions_evaluated": 3
        }
    )

    assert len(report["risks"]) > 0


def test_markdown_report_is_generated():
    builder = create_builder()

    report = builder.build_report(
        candidate={
            "name": "Test Candidate",
            "email": "test@example.com",
            "role": "Data Analyst"
        },
        answer_results=create_answer_results(),
        screening_score=create_screening_score(),
        behavioral_analysis=create_behavioral_analysis()
    )

    markdown = builder.to_markdown(
        report
    )

    assert "# AI Screening Report" in markdown
    assert "## Key Answers" in markdown
    assert "## Strengths" in markdown
    assert "## Risks" in markdown
    assert "## Recruiter Summary" in markdown