"""
ZECPATH AI - Skill-Wise Scoring
Day 47: Aggregates technical scores by individual skill.
"""


class SkillWiseScoring:

    def __init__(self):
        self.skill_results = {}

    def add_result(self, skill, score):
        if not isinstance(skill, str) or not skill.strip():
            raise ValueError("Skill must be a non-empty string.")

        if (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
        ):
            raise TypeError("Score must be numeric.")

        if not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100.")

        skill_name = skill.strip().lower()

        if skill_name not in self.skill_results:
            self.skill_results[skill_name] = []

        self.skill_results[skill_name].append(float(score))

    def get_breakdown(self):
        breakdown = {}

        for skill, scores in self.skill_results.items():
            average = sum(scores) / len(scores)

            breakdown[skill] = {
                "average_score": round(average, 2),
                "questions_evaluated": len(scores),
                "scores": [round(score, 2) for score in scores],
            }

        return breakdown

    def get_overall_skill_score(self):
        breakdown = self.get_breakdown()

        if not breakdown:
            return 0.0

        return round(
            sum(
                item["average_score"]
                for item in breakdown.values()
            ) / len(breakdown),
            2,
        )
