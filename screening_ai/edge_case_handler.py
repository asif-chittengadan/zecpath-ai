class EdgeCaseHandler:
    """Convert response-quality issues into retry, clarification, or safe fallback actions."""

    def __init__(self, rules):
        self.rules = rules
        self.retry_limits = rules.get("retry_limits", {})
        self.messages = rules.get("messages", {})

    def handle(self, quality_result, retry_counts=None):
        retry_counts = dict(retry_counts or {})
        issues = quality_result.get("issues", [])

        if not issues:
            return {
                "action": "continue",
                "message": None,
                "retry_count": retry_counts,
                "terminal": False
            }

        # One response may have several quality issues. Use a deterministic priority.
        priority = [
            "poor_audio",
            "background_noise",
            "missing_answer",
            "language_mixing"
        ]
        issue = next(
            (item for item in priority if item in issues),
            issues[0]
        )

        current_count = retry_counts.get(issue, 0)
        limit = int(self.retry_limits.get(issue, 1))

        if current_count < limit:
            retry_counts[issue] = current_count + 1
            return {
                "action": self._action_for(issue),
                "message": self.messages.get(
                    issue,
                    self.messages.get("safe_fallback")
                ),
                "retry_count": retry_counts,
                "terminal": False,
                "issue": issue
            }

        return {
            "action": "safe_fallback",
            "message": self.messages.get(
                "retry_limit",
                self.messages.get("safe_fallback")
            ),
            "retry_count": retry_counts,
            "terminal": True,
            "issue": issue
        }

    def _action_for(self, issue):
        if issue == "language_mixing":
            return "clarify"
        if issue == "missing_answer":
            return "retry"
        if issue in {"poor_audio", "background_noise"}:
            return "retry"
        return "safe_fallback"
