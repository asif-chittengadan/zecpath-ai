class InterviewSummaryGenerator:
    """
    Generates a structured recruiter-ready summary
    from HR interview analysis.
    """

    def generate_summary(
        self,
        strengths=None,
        weaknesses=None,
        cultural_fit_indicators=None,
        risk_flags=None,
        inconsistencies=None,
        overall_hr_score=None
    ):
        return {
            "candidate_strengths": strengths or [],
            "candidate_weaknesses": weaknesses or [],
            "cultural_fit_indicators": cultural_fit_indicators or [],
            "risk_flags": risk_flags or [],
            "inconsistencies": inconsistencies or [],
            "overall_hr_performance": self._build_performance_summary(
                overall_hr_score
            )
        }

    def _build_performance_summary(self, score):
        if score is None:
            return {
                "score": None,
                "level": "not_available"
            }

        try:
            score = float(score)
        except (TypeError, ValueError):
            return {
                "score": None,
                "level": "not_available"
            }

        score = max(0.0, min(100.0, score))

        if score >= 75:
            level = "high"
        elif score >= 50:
            level = "moderate"
        elif score >= 25:
            level = "low"
        else:
            level = "very_low"

        return {
            "score": round(score, 2),
            "level": level
        }