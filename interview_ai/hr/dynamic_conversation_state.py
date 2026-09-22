from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DynamicConversationState:
    """
    Tracks adaptive questioning state during a V2 HR interview.
    """

    current_question_id: Optional[str] = None
    current_question: Optional[str] = None

    last_response: Optional[str] = None
    last_classification: Optional[str] = None

    difficulty_level: int = 1
    last_follow_up_type: Optional[str] = None

    follow_up_count: int = 0
    questions_asked: int = 0

    asked_questions: List[str] = field(default_factory=list)

    conversation_history: List[Dict] = field(
        default_factory=list
    )

    def set_question(self, question_id, question):
        """
        Set the currently active question.
        """

        self.current_question_id = question_id
        self.current_question = question

        self.questions_asked += 1

        if question not in self.asked_questions:
            self.asked_questions.append(question)

    def record_response(
        self,
        response,
        classification,
        difficulty_level
    ):
        """
        Record the candidate response and its classification.
        """

        self.last_response = response
        self.last_classification = classification
        self.difficulty_level = difficulty_level

        self.conversation_history.append({
            "question_id": self.current_question_id,
            "question": self.current_question,
            "response": response,
            "classification": classification,
            "difficulty_level": difficulty_level
        })

    def record_follow_up(
        self,
        follow_up_type,
        question
    ):
        """
        Record an adaptive follow-up question.
        """

        self.last_follow_up_type = follow_up_type
        self.follow_up_count += 1

        if question not in self.asked_questions:
            self.asked_questions.append(question)

        self.conversation_history.append({
            "event": "follow_up",
            "follow_up_type": follow_up_type,
            "question": question,
            "difficulty_level": self.difficulty_level
        })

    def was_question_asked(self, question):
        """
        Check whether a question has already been asked.
        """

        return question in self.asked_questions

    def get_state(self):
        """
        Return the current dynamic conversation state.
        """

        return {
            "current_question_id": self.current_question_id,
            "current_question": self.current_question,
            "last_response": self.last_response,
            "last_classification": self.last_classification,
            "difficulty_level": self.difficulty_level,
            "last_follow_up_type": self.last_follow_up_type,
            "follow_up_count": self.follow_up_count,
            "questions_asked": self.questions_asked,
            "asked_questions": list(self.asked_questions),
            "conversation_history": list(
                self.conversation_history
            )
        }

    def reset(self):
        """
        Reset the dynamic state for a new interview.
        """

        self.current_question_id = None
        self.current_question = None
        self.last_response = None
        self.last_classification = None
        self.difficulty_level = 1
        self.last_follow_up_type = None
        self.follow_up_count = 0
        self.questions_asked = 0
        self.asked_questions.clear()
        self.conversation_history.clear()