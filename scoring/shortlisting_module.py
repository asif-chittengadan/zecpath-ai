import json


class ShortlistingModule:

    def __init__(
        self,
        config_path="data/ranking_config.json"
    ):

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.config = json.load(file)

    def classify(self, score):

        if score is None:
            score = 0.0

        score = float(score)

        shortlist_threshold = self.config[
            "shortlist_threshold"
        ]

        review_threshold = self.config[
            "review_threshold"
        ]

        if score >= shortlist_threshold:

            return "SHORTLIST"

        if score >= review_threshold:

            return "REVIEW"

        return "REJECT"