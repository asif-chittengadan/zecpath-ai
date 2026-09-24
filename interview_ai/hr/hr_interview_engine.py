from interview_ai.hr.interview_state import InterviewState
from interview_ai.hr.interview_flow import HRInterviewFlow
from interview_ai.hr.question_generator import HRQuestionGenerator
from interview_ai.hr.follow_up_engine import HRFollowUpEngine

from interview_ai.hr.response_analyzer import HRResponseAnalyzer
from interview_ai.hr.adaptive_follow_up_engine import AdaptiveFollowUpEngine
from interview_ai.hr.difficulty_adapter import InterviewDifficultyAdapter
from interview_ai.hr.repetition_guard import InterviewRepetitionGuard
from interview_ai.hr.dynamic_conversation_state import (
    DynamicConversationState
)

from interview_ai.hr.communication_feature_analyzer import (
    CommunicationFeatureAnalyzer
)

from interview_ai.hr.communication_scoring_engine import (
    CommunicationScoringEngine
)

from interview_ai.hr.communication_score_normalizer import (
    CommunicationScoreNormalizer
)
from interview_ai.hr.confidence_analyzer import (
    ConfidenceAnalyzer
)

from interview_ai.hr.sentiment_scoring_engine import (
    SentimentScoringEngine
)

from interview_ai.hr.contradiction_analyzer import (
    ContradictionAnalyzer
)

from interview_ai.hr.stress_indicator_analyzer import (
    StressIndicatorAnalyzer
)

from interview_ai.hr.behavioral_confidence_engine import (
    BehavioralConfidenceEngine
)

class HRInterviewEngine:
    """
    ZECPATH AI V2 HR Interview Engine.

    Integrates:
    - Question Generator
    - Interview State
    - Interview Flow
    - Day 33 Follow-Up Engine
    - Day 34 Response Analyzer
    - Day 34 Adaptive Follow-Up Engine
    - Day 34 Difficulty Adapter
    - Day 34 Repetition Guard
    - Day 34 Dynamic Conversation State
    """

    PHASE_QUESTION_CATEGORIES = {
        "introduction": [
            "self_introduction"
        ],
        "core_hr": [
            "career_journey",
            "strengths_weaknesses",
            "teamwork_culture_fit",
            "career_goals",
            "availability_commitment"
        ]
    }

    def __init__(
        self,
        session_id,
        candidate_id,
        role,
        candidate_type,
        role_type,
        question_bank_path="data/hr_question_bank.json"
    ):
        self.state = InterviewState(
            session_id=session_id,
            candidate_id=candidate_id,
            role=role,
            candidate_type=candidate_type,
            role_type=role_type
        )

        self.flow = HRInterviewFlow(self.state)

        self.question_generator = HRQuestionGenerator(
            question_bank_path
        )

        # Day 33 compatibility
        self.follow_up_engine = HRFollowUpEngine()

        # Day 34 components
        self.response_analyzer = HRResponseAnalyzer()
        self.adaptive_follow_up_engine = AdaptiveFollowUpEngine()
        self.difficulty_adapter = InterviewDifficultyAdapter()
        self.repetition_guard = InterviewRepetitionGuard()
        self.dynamic_state = DynamicConversationState()

        # Day 35 communication evaluation
        self.communication_feature_analyzer = (
            CommunicationFeatureAnalyzer()
        )
        self.communication_scoring_engine = (
            CommunicationScoringEngine()
        )
        self.communication_score_normalizer = (
            CommunicationScoreNormalizer()
        )
        self.communication_history = []
        # Day 36 behavioral analysis
        self.confidence_analyzer = (
            ConfidenceAnalyzer()
        )

        self.sentiment_scoring_engine = (
            SentimentScoringEngine()
        )

        self.contradiction_analyzer = (
            ContradictionAnalyzer()
        )

        self.stress_indicator_analyzer = (
            StressIndicatorAnalyzer()
        )

        self.behavioral_confidence_engine = (
            BehavioralConfidenceEngine()
        )

        self.behavioral_history = []

        self.category_index = 0
        self.question_index = 0

        self.follow_up_active = False
        self.current_category = None

    def start(self):
        """
        Start the HR interview.
        """

        self.flow.start()

        return self._prepare_next_question()

    def submit_response(self, response):
        """
        Process a candidate response using the Day 34
        dynamic follow-up pipeline.
        """

        if self.state.current_question is None:
            raise RuntimeError(
                "No active question. Start the interview first."
            )

        # -------------------------------------------------
        # 1. Analyze candidate response
        # -------------------------------------------------

        analysis = self.response_analyzer.analyze(
            response
        )

        # -------------------------------------------------
        # Day 35 - Communication evaluation
        # -------------------------------------------------

        communication_features = (
            self.communication_feature_analyzer.analyze(
                response
            )
        )

        communication_score_result = (
            self.communication_scoring_engine.score(
                communication_features
            )
        )

        communication_score = (
            self.communication_score_normalizer.normalize(
                communication_score_result["score"],
                communication_features["word_count"]
            )
        )

        communication_result = {
            "features": communication_features,
            "raw_score": communication_score_result["score"],
            "normalized_score": communication_score
        }

        self.communication_history.append(
            communication_result
        )

        classification = analysis["classification"]

        # -------------------------------------------------
        # 2. Determine adaptive difficulty
        # -------------------------------------------------

        difficulty_level = (
            self.difficulty_adapter.determine_level(
                classification
            )
        )

        # -------------------------------------------------
        # 3. Store response in Day 33 state
        # -------------------------------------------------

        self.flow.capture_response(
            response,
            follow_up_eligible=(
                classification != "complete"
                or self.current_category in {
                    "career_journey",
                    "strengths_weaknesses",
                    "teamwork_culture_fit"
                }
            )
        )

        # -------------------------------------------------
        # 4. Store response in Day 34 state
        # -------------------------------------------------

        self.dynamic_state.record_response(
            response=response,
            classification=classification,
            difficulty_level=difficulty_level
        )

        # -------------------------------------------------
        # 5. Decide adaptive follow-up
        # -------------------------------------------------

        decision = self.adaptive_follow_up_engine.decide(
            analysis,
            self.current_category
        )

        # -------------------------------------------------
        # 6. Prevent endless follow-up loops
        # -------------------------------------------------

        if self.follow_up_active:
            decision = {
                "trigger": "none",
                "follow_up_required": False,
                "question": None,
                "reason": (
                    "Follow-up already used for the current "
                    "response chain."
                )
            }

        # -------------------------------------------------
        # 7. Handle follow-up
        # -------------------------------------------------

        if decision["follow_up_required"]:

            follow_up_question = decision["question"]

            # Check repetition
            if self.repetition_guard.is_repeated(
                follow_up_question
            ):
                alternatives = self._get_alternatives(
                    decision["trigger"],
                    self.current_category
                )

                alternative = (
                    self.repetition_guard.get_alternative(
                        follow_up_question,
                        alternatives
                    )
                )

                if alternative is not None:
                    follow_up_question = alternative
                else:
                    decision = {
                        "trigger": "none",
                        "follow_up_required": False,
                        "question": None,
                        "reason": (
                            "No unused follow-up question "
                            "was available."
                        )
                    }

            if decision["follow_up_required"]:

                self.follow_up_active = True

                question_id = (
                    f"{self.state.current_question_id}-"
                    f"FOLLOWUP"
                )

                self.state.set_question(
                    question_id,
                    follow_up_question
                )

                self.repetition_guard.register_question(
                    follow_up_question
                )

                self.dynamic_state.record_follow_up(
                    follow_up_type=decision["trigger"],
                    question=follow_up_question
                )

                return {
                    "action": "follow_up",
                    "question": follow_up_question,
                    "phase": self.state.current_phase,
                    "classification": classification,
                    "difficulty_level": difficulty_level,
                    "follow_up_type": decision["trigger"],
                    "follow_up_required": True,

                    # Day 33 backward compatibility
                    "follow_up_eligible": True,
                    "communication": communication_result
                }

        # -------------------------------------------------
        # 8. Continue to next main question
        # -------------------------------------------------

        self.follow_up_active = False

        next_question = self._prepare_next_question()

        if next_question is None:
            return {
                "action": "completed",
                "question": None,
                "phase": self.state.current_phase,
                "classification": classification,
                "difficulty_level": difficulty_level,
                "follow_up_type": None,
                "follow_up_required": False,
                "communication": communication_result
            }

        return {
            "action": "next_question",
            "question": next_question,
            "phase": self.state.current_phase,
            "classification": classification,
            "difficulty_level": difficulty_level,
            "follow_up_type": None,
            "follow_up_required": False,

            # Day 33 backward compatibility
            "follow_up_eligible": False,
            "communication": communication_result
        }

    def _prepare_next_question(self):
        """
        Select and store the next main interview question.
        """

        phase = self.state.current_phase

        if phase == "introduction":
            categories = self.PHASE_QUESTION_CATEGORIES[
                "introduction"
            ]

        elif phase == "core_hr":
            categories = self.PHASE_QUESTION_CATEGORIES[
                "core_hr"
            ]

        elif phase == "role_based_evaluation":
            return self._prepare_role_question()

        elif phase == "closing":
            self.state.complete_interview()
            return None

        else:
            raise ValueError(
                f"Unknown interview phase: {phase}"
            )

        if self.category_index >= len(categories):
            self.category_index = 0
            self.question_index = 0

            next_phase = self.flow.move_to_next_phase()

            if next_phase == "closing":
                return self._prepare_next_question()

            return self._prepare_next_question()

        category = categories[self.category_index]

        questions = self.question_generator.generate(
            category,
            self.state.candidate_type,
            self.state.role_type
        )

        if self.question_index >= len(questions):
            self.category_index += 1
            self.question_index = 0

            return self._prepare_next_question()

        question = questions[self.question_index]

        question_id = (
            f"{phase.upper()}-"
            f"{self.category_index + 1:02d}-"
            f"{self.question_index + 1:02d}"
        )

        self.current_category = category

        self.state.set_question(
            question_id,
            question
        )

        self.dynamic_state.set_question(
            question_id,
            question
        )

        self.repetition_guard.register_question(
            question
        )

        self.question_index += 1

        return question

    def _prepare_role_question(self):
        """
        Prepare a deterministic role-based question.
        """

        role = self.state.role

        if self.state.role_type == "technical":
            question = (
                f"Could you describe a technical challenge "
                f"you would expect to face in a {role} role "
                f"and how you would approach it?"
            )
        else:
            question = (
                f"Could you describe how your experience "
                f"would help you contribute effectively as a {role}?"
            )

        self.current_category = (
            "role_based_evaluation"
        )

        question_id = "ROLE-EVAL-001"

        self.state.set_question(
            question_id,
            question
        )

        self.dynamic_state.set_question(
            question_id,
            question
        )

        self.repetition_guard.register_question(
            question
        )

        return question

    def _get_alternatives(
        self,
        trigger,
        category
    ):
        """
        Return alternative follow-up questions when the
        preferred question has already been asked.
        """

        alternatives = {
            "clarification": [
                "Could you explain that from another perspective?",
                "Could you clarify the main point of your answer?"
            ],

            "deepening": [
                "What was the most important part of that experience?",
                "What did you personally learn from that situation?"
            ],

            "example_based": [
                "Could you describe a different example?",
                "Can you share another situation where this happened?"
            ],

            "scenario_based": [
                "How would you approach a similar challenge?",
                "What would you do if the situation became more complex?"
            ]
        }

        return alternatives.get(
            trigger,
            []
        )

    def get_state(self):
        """
        Return the Day 33 interview state.
        """
        return self.flow.get_state()

    def get_dynamic_state(self):
        """
        Return the Day 34 adaptive state.
        """
        return self.dynamic_state.get_state()

    def get_communication_history(self):
        """
        Return communication evaluations for all submitted responses.
        """

        return list(
            self.communication_history
        )

    def analyze_behavioral_signals(
        self,
        response,
        previous_data=None,
        metadata=None
    ):
        """
        Run the complete Day 36 behavioral analysis pipeline.
        """

        confidence_result = (
            self.confidence_analyzer.analyze(
                response,
                metadata
            )
        )

        sentiment_result = (
            self.sentiment_scoring_engine.analyze(
                response
            )
        )

        contradiction_result = (
            self.contradiction_analyzer.analyze(
                response,
                previous_data
            )
        )

        stress_result = (
            self.stress_indicator_analyzer.analyze(
                response,
                metadata
            )
        )

        behavioral_result = (
            self.behavioral_confidence_engine.calculate(
                confidence_result=confidence_result,
                sentiment_result=sentiment_result,
                contradiction_result=contradiction_result,
                stress_result=stress_result
            )
        )

        result = {
            "confidence": confidence_result,
            "sentiment": sentiment_result,
            "contradiction": contradiction_result,
            "stress": stress_result,
            "behavioral_confidence": behavioral_result
        }

        self.behavioral_history.append(
            result
        )

        return result

    def get_behavioral_history(self):
        """
        Return behavioral analysis results
        for submitted interview responses.
        """

        return list(
            self.behavioral_history
        )