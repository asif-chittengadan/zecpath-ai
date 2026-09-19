"""
Zecpath AI - Day 29
AI Conversation Flow Engine

Controls the screening conversation after a question is asked.
Handles:
- silence
- confusion
- repeated answers
- invalid/off-topic answers
- fallback questions
- follow-up triggers
- retry and polite failure logic

This module uses only the Python standard library.
Existing Zecpath answer-understanding logic can be injected through
the answer_analyzer callback instead of being duplicated here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from screening_ai.response_quality_checker import ResponseQualityChecker
from screening_ai.edge_case_handler import EdgeCaseHandler


class ConversationState(str, Enum):
    START = "START"
    ASK_QUESTION = "ASK_QUESTION"
    WAITING_FOR_RESPONSE = "WAITING_FOR_RESPONSE"
    PROCESS_RESPONSE = "PROCESS_RESPONSE"
    HANDLE_SILENCE = "HANDLE_SILENCE"
    HANDLE_CONFUSION = "HANDLE_CONFUSION"
    HANDLE_REPETITION = "HANDLE_REPETITION"
    IS_ANSWER_VALID = "IS_ANSWER_VALID"
    STORE_ANSWER = "STORE_ANSWER"
    ASK_FALLBACK = "ASK_FALLBACK"
    CHECK_FOLLOW_UP = "CHECK_FOLLOW_UP"
    ASK_FOLLOW_UP = "ASK_FOLLOW_UP"
    MORE_QUESTIONS = "MORE_QUESTIONS"
    NEXT_QUESTION = "NEXT_QUESTION"
    RETRY = "RETRY"
    END_CALL = "END_CALL"
    FAILED = "FAILED"


@dataclass
class ConversationContext:
    session_id: str
    candidate_id: str
    questions: List[Dict[str, Any]]
    current_index: int = 0
    state: ConversationState = ConversationState.START
    retry_count: int = 0
    silence_count: int = 0
    confusion_count: int = 0
    repetition_count: int = 0
    fallback_count: int = 0
    answers: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    last_response: str = ""
    last_action: str = ""
    completed: bool = False


class ConversationFlowEngine:
    """State-machine controller for an AI screening conversation."""

    def __init__(
        self,
        rules_path: str = "config/conversation_flow_rules.json",
        answer_analyzer: Optional[Callable[[str, str, List[Dict[str, Any]]], Dict[str, Any]]] = None,
        edge_case_rules_path: Optional[str] = None,
    ) -> None:
        self.rules = self._load_rules(rules_path)
        self.answer_analyzer = answer_analyzer
        self.edge_case_checker = None
        self.edge_case_handler = None

        if edge_case_rules_path:
            edge_rules = self._load_rules(edge_case_rules_path)
            self.edge_case_checker = ResponseQualityChecker(edge_rules)
            self.edge_case_handler = EdgeCaseHandler(edge_rules)

    @staticmethod
    def _load_rules(rules_path: str) -> Dict[str, Any]:
        from pathlib import Path

        path = Path(rules_path)
        if not path.exists():
            raise FileNotFoundError(f"Conversation flow rules not found: {path}")

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def start(self, session_id: str, candidate_id: str, questions: List[Dict[str, Any]]) -> ConversationContext:
        if not questions:
            raise ValueError("At least one screening question is required.")

        context = ConversationContext(
            session_id=session_id,
            candidate_id=candidate_id,
            questions=questions,
        )
        self._transition(context, ConversationState.ASK_QUESTION, "Screening initialized.")
        return context

    def current_question(self, context: ConversationContext) -> Optional[Dict[str, Any]]:
        if 0 <= context.current_index < len(context.questions):
            return context.questions[context.current_index]
        return None

    def next_prompt(self, context: ConversationContext) -> Optional[str]:
        question = self.current_question(context)
        if question is None:
            return None
        return str(question.get("question") or question.get("text") or "").strip() or None

    def receive_response(
        self,
        context: ConversationContext,
        response: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if context.completed:
            return self._result(context, "call_already_completed")

        text = (response or "").strip()
        context.last_response = text

        # Day 31: optional response/audio quality handling.
        # Without edge_case_rules_path, the original Day 29 behavior remains unchanged.
        if self.edge_case_checker is not None and self.edge_case_handler is not None:
            quality = self.edge_case_checker.check(text, metadata or {})

            if quality["issues"]:
                retry_counts = dict(getattr(context, "edge_retry_counts", {}))
                edge_result = self.edge_case_handler.handle(
                    quality,
                    retry_counts,
                )
                context.edge_retry_counts = dict(edge_result["retry_count"])

                issue = edge_result.get("issue", "response_quality")

                if edge_result["action"] == "retry":
                    self._transition(
                        context,
                        ConversationState.RETRY,
                        f"Day 31 retry: {issue}",
                    )
                elif edge_result["action"] == "clarify":
                    self._transition(
                        context,
                        ConversationState.HANDLE_CONFUSION,
                        f"Day 31 clarification: {issue}",
                    )
                else:
                    self._transition(
                        context,
                        ConversationState.ASK_FALLBACK,
                        f"Day 31 safe fallback: {issue}",
                    )

                context.last_action = edge_result["action"]
                return self._result(
                    context,
                    edge_result["action"],
                    prompt=edge_result["message"],
                )

        if not text:
            return self._handle_silence(context)

        self._transition(context, ConversationState.PROCESS_RESPONSE, "Candidate response received.")

        question = self.current_question(context) or {}
        category = str(question.get("category", "")).strip().lower()
        analysis = self._analyze_response(context, text, category)

        if analysis["confused"]:
            return self._handle_confusion(context)

        if analysis["repeated"]:
            return self._handle_repetition(context)

        self._transition(context, ConversationState.IS_ANSWER_VALID, "Checking response validity.")

        if not analysis["valid"]:
            return self._handle_invalid(context, analysis.get("reason", "Response was not usable."))

        self._transition(context, ConversationState.STORE_ANSWER, "Response accepted.")
        context.answers.append(
            {
                "question_index": context.current_index,
                "question": question.get("question") or question.get("text", ""),
                "category": question.get("category", ""),
                "answer": text,
                "analysis": analysis,
            }
        )

        context.retry_count = 0
        context.silence_count = 0
        context.confusion_count = 0
        context.repetition_count = 0

        self._transition(context, ConversationState.CHECK_FOLLOW_UP, "Checking follow-up triggers.")

        if self._follow_up_required(analysis):
            context.last_action = "ask_follow_up"
            self._transition(context, ConversationState.ASK_FOLLOW_UP, "Follow-up triggered.")
            return self._result(
                context,
                "ask_follow_up",
                prompt=self._follow_up_prompt(analysis, question),
                answer_stored=True,
            )

        return self._move_after_answer(context)

    def submit_follow_up(
        self,
        context: ConversationContext,
        response: Optional[str],
    ) -> Dict[str, Any]:
        text = (response or "").strip()

        if not text:
            return self._handle_silence(context, is_follow_up=True)

        question = self.current_question(context) or {}
        context.answers.append(
            {
                "question_index": context.current_index,
                "question": self._follow_up_prompt({}, question),
                "category": question.get("category", ""),
                "answer": text,
                "is_follow_up": True,
            }
        )

        context.retry_count = 0
        context.silence_count = 0
        self._transition(context, ConversationState.MORE_QUESTIONS, "Follow-up answer stored.")
        return self._advance_or_end(context)

    def _analyze_response(
        self,
        context: ConversationContext,
        text: str,
        category: str,
    ) -> Dict[str, Any]:
        if self.answer_analyzer is not None:
            result = self.answer_analyzer(
                text,
                category,
                context.answers,
            )
            if not isinstance(result, dict):
                raise TypeError("answer_analyzer must return a dictionary.")

            return {
                "valid": bool(result.get("valid", True)),
                "confused": bool(result.get("confused", False))
                or self._looks_confused(text),
                "repeated": bool(result.get("repeated", False))
                or self._looks_repeated(text, context.answers),
                "follow_up": bool(result.get("follow_up", False)),
                "reason": result.get("reason", ""),
                "raw_analysis": result,
            }

        return {
            "valid": True,
            "confused": self._looks_confused(text),
            "repeated": self._looks_repeated(text, context.answers),
            "follow_up": False,
            "reason": "",
        }

    def _handle_silence(
        self,
        context: ConversationContext,
        is_follow_up: bool = False,
    ) -> Dict[str, Any]:
        context.silence_count += 1
        context.retry_count += 1
        self._transition(context, ConversationState.HANDLE_SILENCE, "No candidate response detected.")

        max_silence_retries = int(self.rules["retry_limits"]["silence"])

        if context.silence_count <= max_silence_retries:
            self._transition(context, ConversationState.RETRY, "Silence retry available.")
            prompt = self._silence_prompt(context.silence_count, is_follow_up)
            context.last_action = "retry_silence"
            return self._result(context, "retry", prompt=prompt)

        self._transition(context, ConversationState.ASK_FALLBACK, "Silence retry limit reached.")
        context.fallback_count += 1
        fallback = self._fallback_prompt(context)
        context.last_action = "fallback_after_silence"

        if fallback:
            return self._result(context, "fallback", prompt=fallback)

        return self._skip_current_question(context, "No response after retry limit.")

    def _handle_confusion(self, context: ConversationContext) -> Dict[str, Any]:
        context.confusion_count += 1
        context.retry_count += 1
        self._transition(context, ConversationState.HANDLE_CONFUSION, "Confusion detected.")

        max_confusion_retries = int(self.rules["retry_limits"]["confusion"])

        if context.confusion_count <= max_confusion_retries:
            self._transition(context, ConversationState.RETRY, "Clarification retry available.")
            context.last_action = "clarify_question"
            return self._result(
                context,
                "clarify",
                prompt=self._clarification_prompt(context),
            )

        self._transition(context, ConversationState.ASK_FALLBACK, "Confusion retry limit reached.")
        context.fallback_count += 1
        fallback = self._fallback_prompt(context)

        if fallback:
            context.last_action = "fallback_after_confusion"
            return self._result(context, "fallback", prompt=fallback)

        return self._skip_current_question(context, "Question remained unclear after retry limit.")

    def _handle_repetition(self, context: ConversationContext) -> Dict[str, Any]:
        context.repetition_count += 1
        context.retry_count += 1
        self._transition(context, ConversationState.HANDLE_REPETITION, "Repeated answer detected.")

        max_repetition_retries = int(self.rules["retry_limits"]["repetition"])

        if context.repetition_count <= max_repetition_retries:
            self._transition(context, ConversationState.RETRY, "Repetition retry available.")
            context.last_action = "redirect_repeated_answer"
            return self._result(
                context,
                "redirect",
                prompt=self.rules["messages"]["repetition_redirect"],
            )

        self._transition(context, ConversationState.ASK_FALLBACK, "Repetition retry limit reached.")
        context.fallback_count += 1
        fallback = self._fallback_prompt(context)

        if fallback:
            context.last_action = "fallback_after_repetition"
            return self._result(context, "fallback", prompt=fallback)

        return self._skip_current_question(context, "Repeated response after retry limit.")

    def _handle_invalid(self, context: ConversationContext, reason: str) -> Dict[str, Any]:
        context.retry_count += 1
        self._transition(context, ConversationState.ASK_FALLBACK, f"Invalid response: {reason}")
        context.fallback_count += 1

        max_invalid_retries = int(self.rules["retry_limits"]["invalid"])

        if context.fallback_count <= max_invalid_retries:
            fallback = self._fallback_prompt(context)
            if fallback:
                context.last_action = "fallback_invalid"
                return self._result(context, "fallback", prompt=fallback)

        return self._skip_current_question(context, "Invalid response after retry limit.")

    def _move_after_answer(self, context: ConversationContext) -> Dict[str, Any]:
        self._transition(context, ConversationState.MORE_QUESTIONS, "Checking remaining questions.")
        return self._advance_or_end(context)

    def _advance_or_end(self, context: ConversationContext) -> Dict[str, Any]:
        if context.current_index + 1 < len(context.questions):
            context.current_index += 1
            self._transition(context, ConversationState.NEXT_QUESTION, "Moving to next question.")
            self._transition(context, ConversationState.ASK_QUESTION, "Next question ready.")
            context.last_action = "next_question"
            return self._result(
                context,
                "next_question",
                prompt=self.next_prompt(context),
            )

        self._transition(context, ConversationState.END_CALL, "All screening questions completed.")
        context.completed = True
        context.last_action = "end_call"
        return self._result(context, "end_call")

    def _skip_current_question(self, context: ConversationContext, reason: str) -> Dict[str, Any]:
        self._transition(context, ConversationState.MORE_QUESTIONS, reason)
        return self._advance_or_end(context)

    def _fallback_prompt(self, context: ConversationContext) -> Optional[str]:
        question = self.current_question(context) or {}
        fallback = question.get("fallback_question")

        if fallback:
            return str(fallback)

        category = str(question.get("category", "")).strip().lower()
        category_fallbacks = self.rules.get("fallback_questions", {})
        return category_fallbacks.get(category) or self.rules.get("fallback_questions", {}).get("default")

    def _clarification_prompt(self, context: ConversationContext) -> str:
        question = self.next_prompt(context) or "the question"
        template = self.rules["messages"]["clarification"]
        return template.format(question=question)

    def _silence_prompt(self, count: int, is_follow_up: bool) -> str:
        prompts = self.rules["messages"]["silence"]
        index = min(count - 1, len(prompts) - 1)
        return prompts[index]

    def _follow_up_required(self, analysis: Dict[str, Any]) -> bool:
        return bool(analysis.get("follow_up", False))

    @staticmethod
    def _follow_up_prompt(
        analysis: Dict[str, Any],
        question: Dict[str, Any],
    ) -> str:
        prompt = analysis.get("raw_analysis", {}).get("follow_up_question")
        if prompt:
            return str(prompt)

        return str(
            question.get(
                "follow_up_question",
                "Could you briefly provide more details about that?",
            )
        )

    def _looks_confused(self, text: str) -> bool:
        normalized = " ".join(text.lower().split())
        phrases = self.rules.get("confusion_phrases", [])
        return any(phrase.lower() in normalized for phrase in phrases)

    @staticmethod
    def _looks_repeated(
        text: str,
        previous_answers: List[Dict[str, Any]],
    ) -> bool:
        normalized = ConversationFlowEngine._normalize_for_comparison(text)
        if not normalized:
            return False

        for item in previous_answers:
            previous = ConversationFlowEngine._normalize_for_comparison(
                str(item.get("answer", ""))
            )
            if previous and normalized == previous:
                return True

        return False

    @staticmethod
    def _normalize_for_comparison(text: str) -> str:
        return " ".join(
            text.lower().replace(".", " ").replace(",", " ").split()
        )

    def _transition(
        self,
        context: ConversationContext,
        state: ConversationState,
        reason: str,
    ) -> None:
        context.state = state
        context.events.append(
            {
                "state": state.value,
                "reason": reason,
                "question_index": context.current_index,
                "retry_count": context.retry_count,
            }
        )

    @staticmethod
    def _result(
        context: ConversationContext,
        action: str,
        prompt: Optional[str] = None,
        answer_stored: bool = False,
    ) -> Dict[str, Any]:
        return {
            "state": context.state.value,
            "action": action,
            "prompt": prompt,
            "answer_stored": answer_stored,
            "question_index": context.current_index,
            "retry_count": context.retry_count,
            "completed": context.completed,
            "answers_count": len(context.answers),
        }
