from screening_ai.answer_understanding_engine import AnswerUnderstandingEngine
from screening_ai.day29_answer_adapter import Day29AnswerAdapter
from screening_ai.conversation_flow import ConversationFlowEngine


def main() -> None:
    questions = [
        {
            "category": "Experience",
            "question": "How many years of experience do you have?",
            "fallback_question": "Could you tell me your total work experience in years?",
        },
        {
            "category": "Skills",
            "question": "Which technologies are you comfortable using?",
            "fallback_question": "Could you name one or two technologies you have worked with?",
        },
    ]

    answer_engine = AnswerUnderstandingEngine()
    adapter = Day29AnswerAdapter(answer_engine)

    flow_engine = ConversationFlowEngine(
        rules_path="config/conversation_flow_rules.json",
        answer_analyzer=adapter.analyze,
    )

    context = flow_engine.start(
        session_id="SESSION-DAY29-DEMO",
        candidate_id="CANDIDATE-DAY29-DEMO",
        questions=questions,
    )

    print("AI:", flow_engine.next_prompt(context))

    responses = [
        "I have two years of experience.",
        "Python and SQL.",
    ]

    for response in responses:
        result = flow_engine.receive_response(
            context,
            response
        )

        if result["prompt"]:
            print("AI:", result["prompt"])

        print(
            f"State={result['state']} | "
            f"Action={result['action']} | "
            f"Answers={result['answers_count']}"
        )


if __name__ == "__main__":
    main()