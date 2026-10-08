"""
ZECPATH AI - Technical Interview Engine

Day 46:
Coordinates the technical interview configuration,
question hierarchy, state, flow, role mapping,
and difficulty adaptation.
"""


from interview_ai.technical.technical_interview import (
    TechnicalInterviewConfig,
)

from interview_ai.technical.question_hierarchy import (
    TechnicalQuestionHierarchy,
)

from interview_ai.technical.technical_state import (
    TechnicalInterviewState,
)

from interview_ai.technical.technical_flow import (
    TechnicalInterviewFlow,
)

from interview_ai.technical.role_skill_mapper import (
    TechnicalRoleSkillMapper,
)

from interview_ai.technical.difficulty_adapter import (
    TechnicalDifficultyAdapter,
)


class TechnicalInterviewEngine:
    """
    Main controller for a technical interview session.
    """

    def __init__(
        self,
        candidate_id,
        role,
        experience_years,
    ):
        self.state = TechnicalInterviewState(
            candidate_id=candidate_id,
            role=role,
            experience_years=experience_years,
        )

        self.flow = TechnicalInterviewFlow()

        self.difficulty = (
            TechnicalDifficultyAdapter
            .get_initial_difficulty(
                experience_years
            )
        )

        self.skill_domain = (
            TechnicalRoleSkillMapper
            .get_domain(role)
        )

        self.skills = (
            TechnicalRoleSkillMapper
            .get_skills(role)
        )

        self.question_index = 0

    def get_interview_profile(self):
        return {
            "candidate_id": self.state.candidate_id,
            "role": self.state.role,
            "experience_years": (
                self.state.experience_years
            ),
            "experience_level": (
                TechnicalInterviewConfig
                .get_experience_level(
                    self.state.experience_years
                )["label"]
            ),
            "skill_domain": self.skill_domain,
            "skills": self.skills,
            "difficulty": self.difficulty,
        }

    def get_current_stage(self):
        return self.flow.get_current_stage()

    def get_next_question(self):
        stage = self.flow.get_current_stage()

        if stage == "completed":
            return None

        questions = (
            TechnicalQuestionHierarchy
            .get_questions(
                stage,
                self.difficulty,
            )
        )

        if self.question_index >= len(questions):
            self.question_index = 0

            next_stage = (
                self.flow.move_to_next_stage()
            )

            self.state.move_to_stage(
                next_stage
            )

            if next_stage == "completed":
                self.state.complete_interview()
                return None

            return self.get_next_question()

        question = questions[
            self.question_index
        ]

        self.state.set_question(
            question=question,
            difficulty=self.difficulty,
        )

        return question

    def submit_answer(
        self,
        answer_quality="acceptable",
    ):
        if self.state.current_question is None:
            raise ValueError(
                "No active question to answer."
            )

        self.state.record_answer()

        self.question_index += 1

        self.difficulty = (
            TechnicalDifficultyAdapter
            .adapt_to_answer(
                self.difficulty,
                answer_quality,
            )
        )

        return self.get_next_question()

    def get_progress(self):
        return self.state.get_progress()