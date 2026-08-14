class BiasEvaluator:

    def evaluate(self, candidates):

        if not candidates:
            return {
                "candidate_count": 0,
                "score_range": 0.0,
                "bias_indicators": []
            }

        scores = []

        for candidate in candidates:

            score = candidate.get(
                "score",
                0
            )

            try:
                score = float(score)
            except (TypeError, ValueError):
                score = 0.0

            if score > 1:
                score = score / 100

            score = max(
                0.0,
                min(score, 1.0)
            )

            scores.append(score)

        highest = max(scores)
        lowest = min(scores)

        score_range = round(
            highest - lowest,
            4
        )

        indicators = []

        if score_range > 0.50:
            indicators.append(
                "Large score variation detected"
            )

        if all(score == 0 for score in scores):
            indicators.append(
                "All candidates received zero scores"
            )

        return {
            "candidate_count": len(candidates),
            "score_range": score_range,
            "bias_indicators": indicators
        }