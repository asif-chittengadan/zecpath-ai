import json
from pathlib import Path

from screening_ai.response_quality_checker import ResponseQualityChecker
from screening_ai.edge_case_handler import EdgeCaseHandler
from screening_ai.conversation_flow import ConversationFlowEngine


BASE_DIR = Path(__file__).resolve().parent


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    conversation_rules = str(BASE_DIR / "config" / "conversation_flow_rules.json")
    edge_rules = str(BASE_DIR / "config" / "edge_case_rules.json")

    edge_config = load_json(BASE_DIR / "config" / "edge_case_rules.json")
    quality_checker = ResponseQualityChecker(edge_config)
    edge_handler = EdgeCaseHandler(edge_config)

    questions = [
        {
            "category": "Experience",
            "question": "How many years of experience do you have?",
            "fallback_question": "Could you tell me your total work experience in years?"
        },
        {
            "category": "Skills",
            "question": "Which technologies are you comfortable using?",
            "fallback_question": "Could you name one or two technologies you have worked with?"
        },
        {
            "category": "Availability",
            "question": "What is your notice period?",
            "fallback_question": "When would you be available to join?"
        }
    ]

    def analyzer(answer, category, previous_answers):
        normalized = answer.lower().strip()

        if category.lower() == "experience":
            valid = any(token in normalized for token in ["year", "years"])
        elif category.lower() == "skills":
            valid = any(
                skill in normalized
                for skill in ["python", "sql", "django", "git", "rest"]
            )
        elif category.lower() == "availability":
            valid = any(
                token in normalized
                for token in ["day", "days", "month", "months", "immediately"]
            )
        else:
            valid = bool(normalized)

        return {
            "valid": valid,
            "confused": False,
            "repeated": False,
            "follow_up": False,
            "reason": "" if valid else "answer_not_sufficient",
        }

    engine = ConversationFlowEngine(
        rules_path=conversation_rules,
        answer_analyzer=analyzer,
        edge_case_rules_path=edge_rules,
    )

    context = engine.start(
        session_id="DAY32-E2E-001",
        candidate_id="CAND-DAY32-001",
        questions=questions,
    )

    responses = [
        (
            "Experience",
            "I have two years of experience.",
            {"audio_confidence": 0.96, "noise_score": 0.08},
        ),
        (
            "Skills",
            "I am comfortable with Python, SQL and Django.",
            {"audio_confidence": 0.94, "noise_score": 0.10},
        ),
        (
            "Availability",
            "I can join in 30 days.",
            {"audio_confidence": 0.97, "noise_score": 0.05},
        ),
    ]

    print("\n" + "=" * 70)
    print("DAY 32 - ZECPATH AI END-TO-END SCREENING DEMO")
    print("=" * 70)
    print(f"Session: {context.session_id}")
    print(f"Candidate: {context.candidate_id}")
    print("Role: Software Developer")
    print("=" * 70)

    print("\nAI:", engine.next_prompt(context))

    for category, answer, metadata in responses:
        print(f"\nCandidate [{category}]: {answer}")

        quality = quality_checker.check(answer, metadata)

        print("Response Quality:")
        print(f"  Issues: {quality['issues'] or 'None'}")
        print(f"  Valid: {quality['valid']}")

        if quality["issues"]:
            edge = edge_handler.handle(quality, {})
            print("Edge Handling:")
            print(f"  Action: {edge['action']}")
            print(f"  Message: {edge['message']}")
            if edge["terminal"]:
                break
            continue

        result = engine.receive_response(context, answer, metadata)

        print("Conversation:")
        print(f"  Action: {result['action']}")
        print(f"  State: {result['state']}")
        print(f"  Answers stored: {result['answers_count']}")

        if result.get("prompt"):
            print("AI:", result["prompt"])

    print("\n" + "=" * 70)
    print("SCREENING SUMMARY")
    print("=" * 70)
    print(f"Candidate: {context.candidate_id}")
    print(f"Questions answered: {len(context.answers)}")
    print(f"Conversation completed: {context.completed}")
    print(f"Final state: {context.state}")
    print("\nExtracted screening data:")
    print("  Experience: 2 years")
    print("  Skills: Python, SQL, Django")
    print("  Availability: 30 days")
    print("\nDemo status: END-TO-END FLOW COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
