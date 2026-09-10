import json

from scoring.semantic_matching_engine import SemanticMatchingEngine


RULES_PATH = "data/intent_classification_rules.json"


class IntentClassifier:

    _semantic_engine = None

    _rules = None

    def __init__(self):

        if IntentClassifier._semantic_engine is None:

            IntentClassifier._semantic_engine = (
                SemanticMatchingEngine()
            )

        self.semantic_engine = IntentClassifier._semantic_engine

        if IntentClassifier._rules is None:

            IntentClassifier._rules = self.__load_json(
                RULES_PATH
            )

        self.rules = IntentClassifier._rules

    def __load_json(
        self,
        path
    ):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def classify(
        self,
        source_text,
        category
    ):

        if not source_text or not source_text.strip():
            return self.__build_result(
                "missing",
                0.0
            )

        if self.__looks_vague(source_text):

            similarity = self.__max_similarity_to_category(
                source_text,
                category
            )

            return self.__build_result(
                "vague",
                similarity
            )

        similarity = self.__max_similarity_to_category(
            source_text,
            category
        )

        if similarity < self.rules["on_topic_similarity_threshold"]:
            return self.__build_result(
                "off_topic",
                similarity
            )

        return self.__build_result(
            "on_topic",
            similarity
        )

    def __max_similarity_to_category(
        self,
        source_text,
        category
    ):

        reference_examples = self.rules["reference_examples"].get(
            category,
            []
        )

        if not reference_examples:
            return 0.0

        scores = [
            self.semantic_engine.calculate_similarity(
                source_text,
                example
            )
            for example in reference_examples
        ]

        return max(scores)

    def __looks_vague(
        self,
        source_text
    ):
        stripped = source_text.strip().rstrip(".").lower()

        for phrase in self.rules["vague_phrases"]:
            if phrase in stripped:
                return True

        word_count = len(stripped.split())

        if word_count > self.rules["vague_word_count_threshold"]:
            return False

        return False
        
    def __build_result(
        self,
        intent_label,
        intent_confidence
    ):

        return {
            "intent_label": intent_label,
            "intent_confidence": round(intent_confidence, 4)
        }