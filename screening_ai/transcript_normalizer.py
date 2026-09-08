import json
import re

from utils.logger import logger


RULES_PATH = "data/normalization_rules.json"
SKILLS_PATH = "data/skills.json"


class TranscriptNormalizer:

    _rules = None

    _skill_display_casing = None

    def __init__(self):

        if TranscriptNormalizer._rules is None:

            TranscriptNormalizer._rules = self.__load_json(
                RULES_PATH
            )

        self.rules = TranscriptNormalizer._rules

        if TranscriptNormalizer._skill_display_casing is None:

            TranscriptNormalizer._skill_display_casing = (
                self.__build_skill_display_casing()
            )

        self.skill_display_casing = TranscriptNormalizer._skill_display_casing

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

    def __build_skill_display_casing(self):

        skills_data = self.__load_json(SKILLS_PATH)

        stoplist = set(
            self.rules["display_casing"]["skill_stoplist"]
        )

        display_casing = {}

        for category_skills in skills_data.values():

            for skill in category_skills:

                key = skill.lower()

                if key in stoplist:
                    continue

                if self.__skill_needs_casing_restore(skill):
                    display_casing[key] = skill

        return display_casing

    def __skill_needs_casing_restore(
        self,
        skill
    ):

        for word in skill.split():

            if re.search(r"[/+#.]", word):
                return True

            if word.isupper() and len(word) > 1:
                return True

            if any(c.isupper() for c in word[1:]):
                return True

        return False

    def normalize(
        self,
        raw_transcript
    ):

        if not raw_transcript:
            return ""

        text = raw_transcript

        text = self.__fold_case(text)
        text = self.__clean_whitespace(text)
        text = self.__remove_interruption_markers(text)
        text = self.__remove_fillers(text)
        text = self.__normalize_numbers(text)
        text = self.__expand_contractions(text)
        text = self.__normalize_punctuation(text)
        text = self.__map_boolean_phrases(text)
        text = self.__restore_display_casing(text)

        return self.__clean_whitespace(text)

    def __fold_case(
        self,
        text
    ):

        return text.lower()

    def __clean_whitespace(
        self,
        text
    ):

        return re.sub(r"\s+", " ", text).strip()

    def __remove_interruption_markers(
        self,
        text
    ):

        for marker in self.rules["interruption_markers"]:
            text = text.replace(marker, " ")

        return self.__clean_whitespace(text)

    def __remove_fillers(
        self,
        text
    ):

        for phrase in self.rules["filler_phrases"]:
            text = re.sub(
                rf"\s*,?\s*\b{re.escape(phrase)}\b\s*,?",
                " ",
                text
            )

        words = text.split()

        filler_words = set(self.rules["filler_words"])

        kept_words = [
            word for word in words
            if word.strip(",.") not in filler_words
        ]

        return " ".join(kept_words)

    def __expand_contractions(
        self,
        text
    ):

        for contraction, expansion in self.rules["contractions"].items():
            text = re.sub(
                rf"\b{re.escape(contraction)}\b",
                expansion,
                text
            )

        return text

    def __normalize_punctuation(
        self,
        text
    ):

        terminators = "".join(
            re.escape(t) for t in self.rules["sentence_terminators"]
        )

        text = re.sub(rf"\s+([{terminators}])", r"\1", text)
        text = re.sub(rf"[{terminators}]{{2,}}", ".", text)

        if text and text[-1] not in self.rules["sentence_terminators"]:
            text += "."

        return text

    def __map_boolean_phrases(
        self,
        text
    ):

        affirmative = self.rules["boolean_affirmative"]
        negative = self.rules["boolean_negative"]

        for phrase in negative["global"]:
            text = re.sub(
                rf"\b{re.escape(phrase)}\b",
                "no",
                text
            )

        for phrase in affirmative["global"]:
            text = re.sub(
                rf"\b{re.escape(phrase)}\b",
                "yes",
                text
            )

        for phrase in negative["utterance_initial"]:
            text = re.sub(
                rf"^\s*{re.escape(phrase)}\b",
                "no",
                text,
                count=1
            )

        for phrase in affirmative["utterance_initial"]:
            text = re.sub(
                rf"^\s*{re.escape(phrase)}\b",
                "yes",
                text,
                count=1
            )

        return text

    def __restore_display_casing(
        self,
        text
    ):

        combined = {
            **self.rules["display_acronyms"],
            **self.skill_display_casing
        }

        ordered_keys = sorted(
            combined.keys(),
            key=len,
            reverse=True
        )

        for key in ordered_keys:
            pattern = r"(?<![a-zA-Z0-9])" + re.escape(key) + r"(?![a-zA-Z0-9])"
            text = re.sub(pattern, combined[key], text)

        return text

    def __normalize_numbers(
        self,
        text
    ):

        rules = self.rules["number_words"]

        ones = rules["ones"]
        teens = rules["teens"]
        tens = rules["tens"]
        scales = rules["scales"]
        guards = self.rules.get("number_word_guards", {})
        guarded_words = set(guards.get("guarded_words", []))
        skip_when_followed_by = set(guards.get("skip_when_followed_by", []))

        start_words = set(ones) | set(teens) | set(tens) | set(scales)

        words = text.split()
        result = []
        i = 0

        while i < len(words):

            word = words[i].strip(",.")

            if word in start_words:

                value, consumed = self.__parse_number_run(
                    words, i, ones, teens, tens, scales
                )

                is_single_guarded_word = (
                    consumed == 1 and word in guarded_words
                )

                next_word = (
                    words[i + consumed].strip(",.")
                    if i + consumed < len(words)
                    else None
                )

                if is_single_guarded_word and next_word in skip_when_followed_by:
                    result.append(words[i])
                    i += 1
                else:
                    result.append(str(value))
                    i += consumed

            else:
                result.append(words[i])
                i += 1

        return " ".join(result)

    def __parse_number_run(
        self,
        words,
        start,
        ones,
        teens,
        tens,
        scales
    ):

        total = 0
        current = 0
        i = start
        consumed = 0

        while i < len(words):

            word = words[i].strip(",.")

            if word in ones:
                current += ones[word]

            elif word in teens:
                current += teens[word]

            elif word in tens:
                current += tens[word]

            elif word in scales:
                scale = scales[word]

                if current == 0:
                    current = 1

                if scale >= 1000:
                    total += current * scale
                    current = 0
                else:
                    current *= scale

            elif word == "and" and self.__next_word_continues_number(
                words, i, ones, teens, tens, scales
            ):
                pass

            else:
                break

            i += 1
            consumed += 1

        return total + current, consumed

    def __next_word_continues_number(
        self,
        words,
        index,
        ones,
        teens,
        tens,
        scales
    ):

        if index + 1 >= len(words):
            return False

        next_word = words[index + 1].strip(",.")

        return (
            next_word in ones
            or next_word in teens
            or next_word in tens
            or next_word in scales
        )