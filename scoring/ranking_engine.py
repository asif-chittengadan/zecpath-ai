class RankingEngine:

    def rank_candidates(self, candidates):

        if not candidates:
            return []

        ranked = sorted(
            candidates,
            key=lambda candidate: candidate.get(
                "score",
                0
            ),
            reverse=True
        )

        for index, candidate in enumerate(
            ranked,
            start=1
        ):
            candidate["rank"] = index

        return ranked

    def get_top_candidates(
        self,
        candidates,
        limit=5
    ):

        ranked = self.rank_candidates(
            candidates
        )

        return ranked[:limit]

    def build_recruiter_output(
        self,
        ranked_candidates,
        shortlisting_module
    ):

        output = []

        for candidate in ranked_candidates:

            score = candidate.get(
                "score",
                0
            )

            status = candidate.get(
                "status",
                shortlisting_module.classify(score)
            )

            output.append({
                "rank": candidate.get(
                    "rank",
                    0
                ),
                "candidate": candidate.get(
                    "candidate",
                    "Unknown"
                ),
                "score": score,
                "status": status
            })

        return output