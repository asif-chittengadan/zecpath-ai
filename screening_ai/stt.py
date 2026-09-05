import queue

import numpy as np
from faster_whisper import WhisperModel

from utils.logger import logger


class SpeechToTextEngine:

    SUPPORTED_LANGUAGES = {
        "en": "en",
        "hi": "hi",
        "ml": "ml",
        "ta": "ta"
    }

    DEFAULT_LANGUAGE = "en"

    SAMPLE_RATE_HERTZ = 16000

    LOW_CONFIDENCE_THRESHOLD = 0.60

    MODEL_SIZE_BY_LANGUAGE = {
        "en": "small",
        "hi": "medium",
        "ml": "medium",
        "ta": "medium"
    }

    _models = {}

    def __init__(
        self,
        language=DEFAULT_LANGUAGE
    ):

        self.language_code = self.__resolve_language_code(
            language
        )

        model_size = self.MODEL_SIZE_BY_LANGUAGE.get(
            self.language_code,
            self.MODEL_SIZE_BY_LANGUAGE[self.DEFAULT_LANGUAGE]
        )

        self.model = self.__get_or_load_model(
            model_size
        )


        self.audio_queue = queue.Queue()

        self.is_streaming = False

    def __resolve_language_code(
        self,
        language
    ):

        return self.SUPPORTED_LANGUAGES.get(
            language,
            self.SUPPORTED_LANGUAGES[self.DEFAULT_LANGUAGE]
        )

    def __get_or_load_model(
        self,
        model_size
    ):

        if model_size not in SpeechToTextEngine._models:

            print(
                f"Loading Whisper '{model_size}' model "
                f"(first use downloads it, may take a few minutes)..."
            )

            SpeechToTextEngine._models[model_size] = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8"
            )

            print(
                f"Whisper '{model_size}' model ready."
            )

        return SpeechToTextEngine._models[model_size]

    def start(self):

        self.is_streaming = True

        logger.info(
            f"STT session started for language {self.language_code}"
        )

    def push_audio_chunk(
        self,
        chunk
    ):

        if not self.is_streaming:
            raise RuntimeError(
                "Stream not started. Call start() before pushing audio."
            )

        self.audio_queue.put(chunk)

    def stop(self):

        self.is_streaming = False

        logger.info("STT session stopped")

    def listen(self):

        chunks = self.__drain_queue()

        if not chunks:
            yield self.__build_silence_event()
            self.stop()
            return

        audio_array = self.__chunks_to_float32(
            chunks
        )

        segments, _ = self.model.transcribe(
            audio_array,
            language=self.language_code,
            vad_filter=True
        )

        transcript, confidence_level = self.__collect_segments(
            segments
        )

        yield self.__build_turn_event(
            transcript,
            confidence_level
        )

        self.stop()

    def __drain_queue(self):

        chunks = []

        while not self.audio_queue.empty():

            chunk = self.audio_queue.get()

            if chunk is None:
                break

            chunks.append(chunk)

        return chunks

    def __chunks_to_float32(
        self,
        chunks
    ):

        raw_bytes = b"".join(chunks)

        int16_array = np.frombuffer(
            raw_bytes,
            dtype=np.int16
        )

        return int16_array.astype(np.float32) / 32768.0

    def __collect_segments(
        self,
        segments
    ):

        transcript_parts = []
        confidences = []

        for segment in segments:

            transcript_parts.append(
                segment.text.strip()
            )

            confidences.append(
                self.__logprob_to_confidence(
                    segment.avg_logprob
                )
            )

        transcript = " ".join(transcript_parts).strip()

        confidence_level = (
            round(sum(confidences) / len(confidences), 3)
            if confidences
            else 0.0
        )

        return transcript, confidence_level

    def __logprob_to_confidence(
        self,
        avg_logprob
    ):

        confidence = 1.0 + avg_logprob

        return max(0.0, min(1.0, round(confidence, 3)))

    def __build_turn_event(
        self,
        transcript,
        confidence_level
    ):

        return {
            "event_type": "final",
            "raw_transcript": transcript,
            "confidence_level": confidence_level,
            "language": self.language_code,
            "flagged_for_review": (
                confidence_level < self.LOW_CONFIDENCE_THRESHOLD
            )
        }

    def __build_silence_event(self):

        logger.info(
            "No audio received, treating as silence"
        )

        return {
            "event_type": "silence",
            "raw_transcript": "",
            "confidence_level": None,
            "language": self.language_code,
            "flagged_for_review": False
        }