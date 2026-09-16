import json
import os

from screening_ai.answer_understanding_engine import AnswerUnderstandingEngine
from scoring.screening_scoring_engine import ScreeningScoringEngine
from screening_ai.behavioral_indicators import BehavioralIndicatorAnalyzer
from screening_ai.screening_report_builder import ScreeningReportBuilder


SESSION_PATH = "data/screening_session_day28_test.json"
QUESTIONS_PATH = "data/hr_screening_questions.json"

OUTPUT_DIR = "data/screening_reports"
JSON_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "screening_report.json"
)
MARKDOWN_OUTPUT = os.path.join(
    OUTPUT_DIR,
    "screening_report.md"
)


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def build_question_map(question_data):
    question_map = {}

    if isinstance(question_data, list):
        questions = question_data
    elif isinstance(question_data, dict):
        questions = question_data.get(
            "questions",
            []
        )

    else:
        questions = []

    for question in questions:
        if not isinstance(question, dict):
            continue

        question_id = question.get(
            "question_id"
        )

        if question_id:
            question_map[question_id] = question

    return question_map


def build_answer_result(
    turn,
    question,
    answer_engine
):
    question_text = question.get(
        "question",
        turn.get("question_id", "")
    )

    answer = turn.get(
        "normalized_transcript",
        turn.get("raw_transcript", "")
    )

    category = question.get(
        "category",
        turn.get("extract_field", "")
    )

    result = answer_engine.understand(
        answer=answer,
        category=category
    )

    if not isinstance(result, dict):
        result = {}

    result["question_id"] = turn.get(
        "question_id"
    )

    result["question"] = question_text
    result["answer"] = answer
    result["category"] = category

    if turn.get("extract_field") == "skills":
        extracted_value = turn.get(
            "extracted_value",
            []
        )

        if isinstance(extracted_value, list):
            result["extracted_skills"] = (
                extracted_value
            )

    return result


def main():
    print("=" * 60)
    print("DAY 28 - AI SCREENING REPORT GENERATOR")
    print("=" * 60)

    session = load_json(
        SESSION_PATH
    )

    question_data = load_json(
        QUESTIONS_PATH
    )

    question_map = build_question_map(
        question_data
    )

    print(
        f"Session: {session.get('session_id')}"
    )
    print(
        f"Candidate: {session.get('candidate_id')}"
    )
    print(
        f"Job: {session.get('job_id')}"
    )
    print(
        f"Role: {session.get('role')}"
    )

    answer_engine = (
        AnswerUnderstandingEngine()
    )

    scoring_engine = (
        ScreeningScoringEngine()
    )

    behavioral_analyzer = (
        BehavioralIndicatorAnalyzer()
    )

    report_builder = (
        ScreeningReportBuilder()
    )

    answer_results = []
    question_scores = []
    behavioral_results = []

    previous_answers = []

    for turn in session.get(
        "turns",
        []
    ):
        question_id = turn.get(
            "question_id"
        )

        question = question_map.get(
            question_id,
            {}
        )

        answer_result = build_answer_result(
            turn,
            question,
            answer_engine
        )

        answer_results.append(
            answer_result
        )

        answer = answer_result.get(
            "answer",
            ""
        )

        category = answer_result.get(
            "category",
            ""
        )

        question_score = (
            scoring_engine.score_question(
                question=question.get(
                    "question",
                    question_id
                ),
                answer=answer,
                category=category,
                expected_keywords=None,
                previous_answers=previous_answers
            )
        )

        question_score["question_id"] = (
            question_id
        )

        question_scores.append(
            question_score
        )

        previous_answers.append(
            answer
        )

        behavioral_result = (
            behavioral_analyzer.analyze(
                response=turn.get(
                    "raw_transcript",
                    answer
                ),
                duration_seconds=turn.get(
                    "audio_duration_seconds"
                )
            )
        )

        behavioral_result["question_id"] = (
            question_id
        )

        behavioral_results.append(
            behavioral_result
        )

    screening_score = (
        scoring_engine.aggregate_scores(
            question_scores
        )
    )

    behavioral_analysis = (
        aggregate_behavioral_results(
            behavioral_results
        )
    )

    candidate = {
        "candidate_id": session.get(
            "candidate_id",
            ""
        ),
        "job_id": session.get(
            "job_id",
            ""
        ),
        "session_id": session.get(
            "session_id",
            ""
        ),
        "role": session.get(
            "role",
            ""
        )
    }

    report = report_builder.build_report(
        candidate=candidate,
        answer_results=answer_results,
        screening_score=screening_score,
        behavioral_analysis=behavioral_analysis
    )

    report["session_metadata"] = {
        "session_id": session.get(
            "session_id"
        ),
        "source_session_id": session.get(
            "source_session_id"
        ),
        "status": session.get(
            "status"
        ),
        "language": session.get(
            "language"
        ),
        "started_at": session.get(
            "started_at"
        ),
        "completed_at": session.get(
            "completed_at"
        )
    }

    report["review_flags"] = session.get(
        "review_flags",
        []
    )

    report["job_requirement_status"] = {
        "available": False,
        "job_id": session.get(
            "job_id"
        ),
        "message": (
            "Parsed JD for this job ID "
            "was not found in data/parsed_jd."
        )
    }

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with open(
        JSON_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    report_builder.save_markdown(
        report,
        MARKDOWN_OUTPUT
    )

    print()
    print("=" * 60)
    print("DAY 28 REPORT GENERATED")
    print("=" * 60)

    print(
        f"JSON: {JSON_OUTPUT}"
    )
    print(
        f"Markdown: {MARKDOWN_OUTPUT}"
    )

    print()
    print(
        f"Questions evaluated: "
        f"{screening_score.get('questions_evaluated', 0)}"
    )

    print(
        f"Screening score: "
        f"{screening_score.get('total_screening_score')}"
    )

    print(
        f"Review flags: "
        f"{len(session.get('review_flags', []))}"
    )


def aggregate_behavioral_results(
    results
):
    if not results:
        return {}

    communication_scores = []
    behavioral_scores = []
    sentiments = []

    hesitation_detected = False
    uncertainty_detected = False
    contradiction_detected = False

    total_words = 0
    total_duration = 0.0

    for result in results:
        communication = result.get(
            "communication",
            {}
        )

        communication_strength = (
            communication
            .get("communication_strength", {})
            .get("score")
        )

        if communication_strength is not None:
            communication_scores.append(
                communication_strength
            )

        behavioral_strength = (
            result.get(
                "communication_strength",
                {}
            )
            .get("score")
        )

        if behavioral_strength is not None:
            behavioral_scores.append(
                behavioral_strength
            )

        sentiment = result.get(
            "sentiment",
            {}
        )

        sentiment_value = sentiment.get(
            "sentiment"
        )

        if sentiment_value:
            sentiments.append(
                sentiment_value
            )

        hesitation_detected = (
            hesitation_detected
            or communication
            .get("hesitation", {})
            .get("detected", False)
        )

        uncertainty_detected = (
            uncertainty_detected
            or communication
            .get("uncertainty", {})
            .get("detected", False)
        )

        contradiction_detected = (
            contradiction_detected
            or communication
            .get("contradictions", {})
            .get("detected", False)
        )

        total_words += communication.get(
            "word_count",
            0
        )

        pace = communication.get(
            "response_pace_wpm"
        )

        duration = result.get(
            "communication",
            {}
        ).get(
            "duration_seconds"
        )

        if duration:
            total_duration += duration

    average_communication = (
        sum(communication_scores)
        / len(communication_scores)
        if communication_scores
        else 0.0
    )

    average_behavioral = (
        sum(behavioral_scores)
        / len(behavioral_scores)
        if behavioral_scores
        else 0.0
    )

    sentiment = "neutral"

    if sentiments:
        positive = sentiments.count(
            "positive"
        )
        negative = sentiments.count(
            "negative"
        )

        if positive > negative:
            sentiment = "positive"
        elif negative > positive:
            sentiment = "negative"

    return {
        "communication": {
            "communication_strength": {
                "score": round(
                    average_communication,
                    2
                ),
                "scale": "0-100"
            },
            "hesitation": {
                "detected": hesitation_detected
            },
            "uncertainty": {
                "detected": uncertainty_detected
            },
            "contradictions": {
                "detected": contradiction_detected
            }
        },
        "sentiment": {
            "sentiment": sentiment
        },
        "communication_strength": {
            "score": round(
                average_behavioral,
                2
            ),
            "scale": "0-100"
        }
    }


if __name__ == "__main__":
    main()