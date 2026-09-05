import re

from utils.logger import logger


class TranscriptNormalizer:

    FILLER_WORDS = {
        "um", "uh", "uhh", "umm", "like", "basically", "actually"
    }

    FILLER_PHRASES = [
        "you know"
    ]

    CONTRACTIONS = {
        "i'm": "i am",
        "i've": "i have",
        "i'll": "i will",
        "i'd": "i would",
        "don't": "do not",
        "doesn't": "does not",
        "didn't": "did not",
        "can't": "cannot",
        "won't": "will not",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "haven't": "have not",
        "hasn't": "has not",
        "hadn't": "had not",
        "shouldn't": "should not",
        "wouldn't": "would not",
        "couldn't": "could not",
        "it's": "it is",
        "that's": "that is",
        "there's": "there is",
        "you're": "you are",
        "we're": "we are",
        "they're": "they are"
    }

    BOOLEAN_AFFIRMATIVE = [
        "yeah", "yep", "yup", "sure", "of course", "definitely", "correct"
    ]

    BOOLEAN_NEGATIVE = [
        "not really", "no way", "nope", "nah"
    ]

    ONES = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9
    }

    TEENS = {
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16,
        "seventeen": 17, "eighteen": 18, "nineteen": 19
    }

    TENS = {
        "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
        "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
    }

    SCALES = {
        "hundred": 100,
        "thousand": 1000,
        "lakh": 100000,
        "lakhs": 100000,
        "crore": 10000000,
        "crores": 10000000
    }

    NUMBER_START_WORDS = (
        set(ONES) | set(TEENS) | set(TENS) | set(SCALES)
    )

    def normalize(
        self,
        raw_transcript
    ):

        if not raw_transcript:
            return ""

        text = raw_transcript

        text = self.__fold_case(text)
        text = self.__clean_whitespace(text)
        text = self.__remove_fillers(text)
        text = self.__normalize_numbers(text)
        text = self.__expand_contractions(text)
        text = self.__normalize_punctuation(text)
        text = self.__map_boolean_phrases(text)

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

    def __remove_fillers(
        self,
        text
    ):

        for phrase in self.FILLER_PHRASES:
            text = re.sub(
                rf"\s*,?\s*\b{re.escape(phrase)}\b\s*,?",
                " ",
                text
            )

        words = text.split()

        kept_words = [
            word for word in words
            if word.strip(",.") not in self.FILLER_WORDS
        ]

        return " ".join(kept_words)

    def __expand_contractions(
        self,
        text
    ):

        for contraction, expansion in self.CONTRACTIONS.items():
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

        text = re.sub(r"\s+([.,?!])", r"\1", text)
        text = re.sub(r"[.,?!]{2,}", ".", text)

        if text and text[-1] not in ".?!":
            text += "."

        return text

    def __map_boolean_phrases(
        self,
        text
    ):

        for phrase in self.BOOLEAN_NEGATIVE:
            text = re.sub(
                rf"\b{re.escape(phrase)}\b",
                "no",
                text
            )

        for phrase in self.BOOLEAN_AFFIRMATIVE:
            text = re.sub(
                rf"(?<!not )\b{re.escape(phrase)}\b",
                "yes",
                text
            )

        return text

    def __normalize_numbers(
        self,
        text
    ):

        words = text.split()
        result = []
        i = 0

        while i < len(words):

            word = words[i].strip(",.")

            if word in self.NUMBER_START_WORDS:
                value, consumed = self.__parse_number_run(words, i)
                result.append(str(value))
                i += consumed
            else:
                result.append(words[i])
                i += 1

        return " ".join(result)

    def __parse_number_run(
        self,
        words,
        start
    ):

        total = 0
        current = 0
        i = start
        consumed = 0

        while i < len(words):

            word = words[i].strip(",.")

            if word in self.ONES:
                current += self.ONES[word]

            elif word in self.TEENS:
                current += self.TEENS[word]

            elif word in self.TENS:
                current += self.TENS[word]

            elif word in self.SCALES:
                scale = self.SCALES[word]

                if current == 0:
                    current = 1

                if scale >= 1000:
                    total += current * scale
                    current = 0
                else:
                    current *= scale

            elif word == "and" and self.__next_word_continues_number(words, i):
                pass

            else:
                break

            i += 1
            consumed += 1

        return total + current, consumed

    def __next_word_continues_number(
        self,
        words,
        index
    ):

        if index + 1 >= len(words):
            return False

        next_word = words[index + 1].strip(",.")

        return (
            next_word in self.ONES
            or next_word in self.TEENS
            or next_word in self.TENS
            or next_word in self.SCALES
        )