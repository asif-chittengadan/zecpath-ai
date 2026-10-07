import re
import json
from pathlib import Path

from interview_ai.hr.hr_interview_engine import HRInterviewEngine

def calculate_answer_relevance(
    question,
    response
):
    """
    Calculate a deterministic answer-relevance score.

    This is a transparent demonstration heuristic.
    It is not a semantic NLP similarity model.
    """

    if not question or not response:
        return 0.0

    question = str(question).strip().lower()
    response = str(response).strip().lower()

    words = re.findall(
        r"[a-zA-Z0-9]+",
        response
    )

    question_words = re.findall(
        r"[a-zA-Z0-9]+",
        question
    )

    word_count = len(words)

    if word_count < 3:
        return 25.0

    if word_count < 8:
        completeness_score = 45.0
    elif word_count < 15:
        completeness_score = 70.0
    else:
        completeness_score = 90.0

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "as",
        "is",
        "are",
        "was",
        "were",
        "you",
        "your",
        "this",
        "that",
        "how",
        "what",
        "why",
        "could",
        "would",
        "can",
        "do",
        "did",
        "about",
        "me",
        "tell",
        "describe"
    }

    meaningful_question_words = {
        word
        for word in question_words
        if word not in stop_words
        and len(word) > 2
    }

    response_words = set(words)

    if meaningful_question_words:
        overlap = (
            meaningful_question_words
            & response_words
        )

        overlap_ratio = (
            len(overlap)
            / len(meaningful_question_words)
        )
    else:
        overlap_ratio = 0.0

    overlap_score = min(
        overlap_ratio * 100,
        100.0
    )

    if word_count >= 8:
        length_score = 100.0
    else:
        length_score = (
            word_count / 8
        ) * 100

    relevance_score = (
        completeness_score * 0.50
        + overlap_score * 0.20
        + length_score * 0.30
    )

    return round(
        min(relevance_score, 100.0),
        2
    )

BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    BASE_DIR /
    "data" /
    "day45_demo_dataset.json"
)


# Additional responses are used when the adaptive
# follow-up engine asks extra questions.
DEMO_RESPONSES = [
    "I recently completed my B.Tech in Information Technology and worked on software and AI related projects.",

    "One example was a project where I developed a software module and solved issues by breaking the problem into smaller tasks.",

    "My main strengths are problem solving, willingness to learn and consistency.",

    "For example, when I faced a technical issue, I analyzed the requirement, tested possible solutions and selected the most reliable approach.",

    "I chose a technical career because I enjoy solving problems and building useful software applications.",

    "During a project, I worked with team members on different modules and coordinated during integration and testing.",

    "One challenge was combining different modules, so we discussed the interfaces and tested the complete workflow together.",

    "I would bring problem solving, willingness to learn and the ability to understand technical requirements to this role.",

    "For example, when I faced a technical issue, I analyzed the requirement, tested possible solutions and selected the most reliable approach.",

    "I am currently working to improve my backend development and understanding of production software systems.",

    "One example is working on software projects where I had to understand existing code and identify the cause of problems.",

    "When I work with a teammate, I first understand their technical reasoning and compare it with the project requirements.",

    "If there is a disagreement, I prefer discussing the options, testing the approaches when possible and selecting the solution that best fits the requirement.",

    "I believe good teamwork requires clear communication, respect for different opinions and responsibility for assigned work.",

    "My career goal is to become a strong software engineer with practical experience in backend systems and AI applications.",

    "I want to continue improving my technical skills while gaining experience working on real production systems.",

    "I am interested in this role because it matches my interest in software development and problem solving.",

    "A technical challenge I may face is understanding an unfamiliar codebase. I would first understand the architecture, reproduce the issue and then implement and test a solution.",

    "I am prepared to commit to the role and follow the organization's working requirements.",

    "I am comfortable learning new tools and processes required by the team.",

    "I am interested in the opportunity and would be happy to contribute while continuing to learn and develop as an engineer.",

    "I would like to add that I am motivated to learn, contribute to the team and grow as a software engineer."
]

def load_demo_dataset():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_demo():
    dataset = load_demo_dataset()

    candidate = dataset["demo_candidate"]

    engine = HRInterviewEngine(
        session_id=dataset["interview_session"]["session_id"],
        candidate_id=candidate["candidate_id"],
        role=candidate["role"],
        candidate_type=candidate["candidate_type"],
        role_type=candidate["role_type"]
    )

    print("=" * 60)
    print("ZECPATH AI — DAY 45 HR INTERVIEW DEMO")
    print("=" * 60)

    print(f"\nCandidate : {candidate['name']}")
    print(f"Role      : {candidate['role']}")

    print("\nStarting interview...\n")

    question = engine.start()

    response_index = 0

    while question is not None:

        print("-" * 60)

        state = engine.get_state()

        print(f"Phase: {state['current_phase']}")
        print(f"Q: {question}")

        if response_index >= len(DEMO_RESPONSES):
            print("\nNo more demo responses available.")
            break

        response = DEMO_RESPONSES[response_index]
        response_index += 1

        print(f"A: {response}")

        result = engine.submit_response(response)

        print(
            f"\nClassification : "
            f"{result.get('classification')}"
        )

        print(
            f"Difficulty     : "
            f"{result.get('difficulty_level')}"
        )

        communication = result.get("communication")

        if communication:
            print(
                "Communication  : "
                f"{communication.get('normalized_score')}"
            )

        if result.get("action") == "follow_up":
            print("\nAdaptive Follow-up:")
            print(f"Q: {result.get('question')}")

            question = result.get("question")

        elif result.get("action") == "next_question":
            print("\nNext Question:")
            print(f"Q: {result.get('question')}")

            question = result.get("question")

        elif result.get("action") == "completed":
            print("\nInterview completed successfully.")
            question = None

        else:
            question = result.get("question")

    print("\n" + "=" * 60)
    print("FINAL INTERVIEW STATE")
    print("=" * 60)

    state = engine.get_state()

    print(json.dumps(state, indent=2))

    print("\n" + "=" * 60)
    print("HR INTERVIEW SCORING")
    print("=" * 60)

    question_scores = []

    response_history = state.get(
        "response_history",
        []
    )

    communication_history = (
        engine.get_communication_history()
    )

    for index, item in enumerate(response_history):

        communication_score = 0.0

        if index < len(communication_history):
            communication_score = communication_history[index].get(
                "normalized_score",
                0.0
            )

        response_text = item.get(
            "response",
            ""
        )

        behavioral = engine.analyze_behavioral_signals(
            response=response_text,
            previous_data={
                "experience_years": 0,
                "availability_days": 0,
                "skills": [
                    "python",
                    "sql",
                    "django"
                ]
            }
        )

        behavioral_confidence = behavioral.get(
            "behavioral_confidence",
            {}
        )

        confidence_score = behavioral_confidence.get(
            "behavioral_confidence_score",
            communication_score
        )

        try:
            confidence_score = float(
                confidence_score
            )
        except (TypeError, ValueError):
            confidence_score = communication_score

        confidence_score = max(
            0.0,
            min(100.0, confidence_score)
        )

        contradiction_result = behavioral.get(
            "contradiction",
            {}
        )

        contradiction_count = contradiction_result.get(
            "count",
            0
        )

        consistency_score = max(
            0.0,
            100.0 - (
                contradiction_count * 10.0
            )
        )

        question = item.get(
            "question",
            ""
        )

        answer_relevance = calculate_answer_relevance(
            question,
            response_text
        )

        question_scores.append({
            "answer_relevance": answer_relevance,
            "communication": communication_score,
            "confidence": confidence_score,
            "consistency": consistency_score
        })

    score_result = engine.calculate_hr_interview_score(
        question_scores
    )

    print(
        f"\nFinal HR Interview Score : "
        f"{score_result['final_score']}"
    )

    print(
        f"Answered Questions       : "
        f"{score_result['answered_questions']}"
    )

    print(
        f"Completion Ratio         : "
        f"{score_result['completion_ratio']}"
    )

    print("\nNormalized Scores:")

    print(
        json.dumps(
            score_result["normalized_scores"],
            indent=2
        )
    )
    print("\n" + "=" * 60)
    print("FINAL HIRING RECOMMENDATION")
    print("=" * 60)

    hr_score = score_result["final_score"]
    interview_completed = state["interview_completed"]

    if not interview_completed:
        recommendation = "HOLD_REVIEW"
        reason = (
            "Interview was not completed. "
            "Human review is required."
        )

    elif hr_score >= 80:
        recommendation = "RECOMMEND"
        reason = (
            "Completed HR interview with a strong overall "
            "demonstration score."
        )

    elif hr_score >= 65:
        recommendation = "HOLD_REVIEW"
        reason = (
            "Interview completed with a moderate score. "
            "Additional human evaluation is recommended."
        )

    else:
        recommendation = "DO_NOT_RECOMMEND"
        reason = (
            "HR interview score is below the demonstration "
            "recommendation threshold."
        )

    final_recommendation = {
        "status": recommendation,
        "hr_interview_score": hr_score,
        "interview_completed": interview_completed,
        "reason": reason,
        "human_review_required": True
    }

    print(
        json.dumps(
            final_recommendation,
            indent=2
        )
    )

    print("\nScore Breakdown:")

    print(
        json.dumps(
            score_result["breakdown"],
            indent=2
        )
    )

    print("\n" + "=" * 60)
    print("DAY 45 DEMO FINISHED")
    print("=" * 60)

    demo_result = {
        "version": "1.0",
        "demo": "ZECPATH AI Day 45 HR Interview",
        "candidate": {
            "candidate_id": state["candidate_id"],
            "role": state["role"],
            "candidate_type": state["candidate_type"],
            "role_type": state["role_type"]
        },
        "interview": {
            "session_id": state["session_id"],
            "current_phase": state["current_phase"],
            "questions_answered": state["questions_answered"],
            "completion_ratio": score_result["completion_ratio"],
            "interview_completed": state["interview_completed"]
        },
        "scoring": {
            "final_score": score_result["final_score"],
            "normalized_scores": score_result[
                "normalized_scores"
            ],
            "breakdown": score_result["breakdown"]
        },
        "recommendation": final_recommendation,
        "scoring_notes": [
            "Communication score is produced by the existing deterministic communication scoring pipeline.",
            "Confidence score is produced by the existing behavioral confidence engine.",
            "Consistency score is derived from contradiction detection.",
            "Answer relevance uses a transparent deterministic demonstration heuristic based on response completeness, keyword overlap and response length.",
            "The recommendation is a decision-support output and requires human review."
        ]
    }

    output_file = "data/day45_demo_result.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            demo_result,
            file,
            indent=2
        )

    print(
        f"\nDemo result saved to: {output_file}"
    )

if __name__ == "__main__":
    run_demo()