"""
ZECPATH AI - Technical Evaluation Report
Day 47: Explainable technical evaluation with skill-wise scores.
"""


class TechnicalEvaluationReport:

    @staticmethod
    def generate(
        candidate_id,
        role,
        question_type,
        difficulty,
        scoring_result,
        depth_result,
        skill_breakdown=None,
        overall_skill_score=None,
    ):
        if not isinstance(scoring_result, dict):
            raise TypeError(
                "scoring_result must be a dictionary."
            )

        if not isinstance(depth_result, dict):
            raise TypeError(
                "depth_result must be a dictionary."
            )

        if skill_breakdown is None:
            skill_breakdown = {}

        if not isinstance(skill_breakdown, dict):
            raise TypeError(
                "skill_breakdown must be a dictionary."
            )

        explanations = {
            "accuracy": (
                "Measures correctness of the technical answer."
            ),
            "depth": (
                "Measures detail and depth of the explanation."
            ),
            "logical_reasoning": (
                "Measures the reasoning used in the answer."
            ),
            "real_world_applicability": (
                "Measures application to practical situations."
            ),
        }

        return {
            "candidate_id": candidate_id,
            "role": role,
            "question_type": question_type,
            "difficulty": difficulty,
            "technical_score": scoring_result.get(
                "final_score"
            ),
            "maximum_score": scoring_result.get(
                "maximum_score", 100
            ),
            "score_breakdown": scoring_result.get(
                "breakdown", {}
            ),
            "score_explanations": explanations,
            "answer_depth": depth_result,
            "skill_wise_breakdown": skill_breakdown,
            "overall_skill_score": overall_skill_score,
            "human_review_required": True,
        }
