import json
import os
import wave

from screening_ai.stt import SpeechToTextEngine


TEST_CASES_PATH = "tests/day24_stt_test_clips.json"
REPORT_OUTPUT_PATH = "docs/stt_accuracy_report.md"

CHUNK_SIZE_BYTES = 3200
EXPECTED_SAMPLE_RATE = 16000
EXPECTED_CHANNELS = 1

LOW_CONFIDENCE_THRESHOLD = 0.60


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def read_wav_chunks(audio_path):

    with wave.open(audio_path, "rb") as wav_file:

        if wav_file.getframerate() != EXPECTED_SAMPLE_RATE:
            raise ValueError(
                f"{audio_path}: sample rate is "
                f"{wav_file.getframerate()}Hz, expected "
                f"{EXPECTED_SAMPLE_RATE}Hz. Convert with ffmpeg first, "
                f"e.g. ffmpeg -i input.wav -ar 16000 -ac 1 output.wav"
            )

        if wav_file.getnchannels() != EXPECTED_CHANNELS:
            raise ValueError(
                f"{audio_path}: has {wav_file.getnchannels()} channels, "
                f"expected mono (1)."
            )

        chunks = []

        data = wav_file.readframes(
            wav_file.getnframes()
        )

        for i in range(0, len(data), CHUNK_SIZE_BYTES):
            chunks.append(
                data[i:i + CHUNK_SIZE_BYTES]
            )

        duration_seconds = round(
            wav_file.getnframes() / wav_file.getframerate(),
            2
        )

        return chunks, duration_seconds


def run_clip_through_stt(audio_path, language):

    chunks, duration_seconds = read_wav_chunks(audio_path)

    engine = SpeechToTextEngine(language=language)
    engine.start()

    for chunk in chunks:
        engine.push_audio_chunk(chunk)

    engine.push_audio_chunk(None)

    final_transcript = ""
    confidence_level = None
    saw_final = False

    for event in engine.listen():

        if event["event_type"] == "final":
            final_transcript = event["raw_transcript"]
            confidence_level = event["confidence_level"]
            saw_final = True

        elif event["event_type"] == "silence":
            break

    return {
        "transcript": final_transcript,
        "confidence_level": confidence_level,
        "duration_seconds": duration_seconds,
        "saw_final": saw_final
    }


def tokenize(text):

    return text.lower().strip().split()


def word_error_rate(expected, actual):

    reference = tokenize(expected)
    hypothesis = tokenize(actual)

    if len(reference) == 0:
        return 0.0 if len(hypothesis) == 0 else 1.0

    distance_matrix = [
        [0] * (len(hypothesis) + 1)
        for _ in range(len(reference) + 1)
    ]

    for i in range(len(reference) + 1):
        distance_matrix[i][0] = i

    for j in range(len(hypothesis) + 1):
        distance_matrix[0][j] = j

    for i in range(1, len(reference) + 1):

        for j in range(1, len(hypothesis) + 1):

            if reference[i - 1] == hypothesis[j - 1]:
                cost = 0
            else:
                cost = 1

            distance_matrix[i][j] = min(
                distance_matrix[i - 1][j] + 1,
                distance_matrix[i][j - 1] + 1,
                distance_matrix[i - 1][j - 1] + cost
            )

    edit_distance = distance_matrix[len(reference)][len(hypothesis)]

    return round(edit_distance / len(reference), 3)


def run_all_tests():

    test_cases = load_json(TEST_CASES_PATH)

    results = []

    print(
        "\n===== DAY 24 STT ACCURACY TEST =====\n"
    )

    for case in test_cases:

        print(
            f"Running {case['clip_id']} "
            f"({case['accent']}, {case['noise_condition']})..."
        )

        if case["expected_transcript"] == "REPLACE_WITH_GROUND_TRUTH_TRANSCRIPT":
            print(
                f"  SKIPPED: {case['clip_id']} has no ground truth "
                f"transcript filled in yet.\n"
            )
            continue

        if not os.path.exists(case["audio_path"]):
            print(
                f"  SKIPPED: audio file not found at "
                f"{case['audio_path']}\n"
            )
            continue

        try:

            stt_result = run_clip_through_stt(
                case["audio_path"],
                case["language"]
            )

            wer = word_error_rate(
                case["expected_transcript"],
                stt_result["transcript"]
            )

            result = {
                **case,
                "actual_transcript": stt_result["transcript"],
                "confidence_level": stt_result["confidence_level"],
                "duration_seconds": stt_result["duration_seconds"],
                "word_error_rate": wer,
                "flagged_for_review": (
                    stt_result["confidence_level"] is not None
                    and stt_result["confidence_level"] < LOW_CONFIDENCE_THRESHOLD
                )
            }

            results.append(result)

            print(
                f"  WER: {wer}, confidence: "
                f"{stt_result['confidence_level']}\n"
            )

        except Exception as error:

            print(
                f"  ERROR running {case['clip_id']}: {error}\n"
            )

    return results


def summarize_by_key(results, key):

    groups = {}

    for result in results:

        group_key = result[key]
        groups.setdefault(group_key, []).append(result)

    summary = {}

    for group_key, group_results in groups.items():

        avg_wer = round(
            sum(r["word_error_rate"] for r in group_results)
            / len(group_results),
            3
        )

        confidences = [
            r["confidence_level"] for r in group_results
            if r["confidence_level"] is not None
        ]

        avg_confidence = (
            round(sum(confidences) / len(confidences), 3)
            if confidences else None
        )

        summary[group_key] = {
            "clip_count": len(group_results),
            "avg_word_error_rate": avg_wer,
            "avg_confidence": avg_confidence
        }

    return summary


def build_report(results):

    lines = []

    lines.append("# STT Accuracy Test Report — Voice Screening Calls")
    lines.append("")
    lines.append("**Project:** Zecpath AI Hiring Platform")
    lines.append("**Module:** screening_ai")
    lines.append("**Generated from:** tests/test_day24_stt_accuracy.py")
    lines.append("")
    lines.append("---")
    lines.append("")

    if not results:
        lines.append(
            "No results — every test case was skipped. Fill in "
            "expected_transcript and audio_path in "
            "tests/day24_stt_test_clips.json and re-run."
        )
        return "\n".join(lines)

    lines.append("## 1. Per-Clip Results")
    lines.append("")
    lines.append(
        "| Clip | Language | Accent | Noise | WER | Confidence | Flagged |"
    )
    lines.append(
        "|---|---|---|---|---|---|---|"
    )

    for r in results:
        lines.append(
            f"| {r['clip_id']} | {r['language']} | {r['accent']} | "
            f"{r['noise_condition']} | {r['word_error_rate']} | "
            f"{r['confidence_level']} | "
            f"{'yes' if r['flagged_for_review'] else 'no'} |"
        )

    lines.append("")
    lines.append("## 2. Accuracy by Language")
    lines.append("")
    lines.append("| Language | Clips | Avg WER | Avg Confidence |")
    lines.append("|---|---|---|---|")

    for language, stats in summarize_by_key(results, "language").items():
        lines.append(
            f"| {language} | {stats['clip_count']} | "
            f"{stats['avg_word_error_rate']} | "
            f"{stats['avg_confidence']} |"
        )

    lines.append("")
    lines.append("## 3. Accuracy by Noise Condition")
    lines.append("")
    lines.append("| Noise Condition | Clips | Avg WER | Avg Confidence |")
    lines.append("|---|---|---|---|")

    for condition, stats in summarize_by_key(
        results, "noise_condition"
    ).items():
        lines.append(
            f"| {condition} | {stats['clip_count']} | "
            f"{stats['avg_word_error_rate']} | "
            f"{stats['avg_confidence']} |"
        )

    overall_wer = round(
        sum(r["word_error_rate"] for r in results) / len(results),
        3
    )

    flagged_count = sum(
        1 for r in results if r["flagged_for_review"]
    )

    lines.append("")
    lines.append("## 4. Overall Summary")
    lines.append("")
    lines.append(f"- Total clips tested: {len(results)}")
    lines.append(f"- Overall average WER: {overall_wer}")
    lines.append(
        f"- Clips flagged for review (confidence < "
        f"{LOW_CONFIDENCE_THRESHOLD}): {flagged_count}"
    )

    return "\n".join(lines)


def main():

    results = run_all_tests()

    report = build_report(results)

    os.makedirs(
        os.path.dirname(REPORT_OUTPUT_PATH),
        exist_ok=True
    )

    with open(
        REPORT_OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)

    print(
        f"Report written to {REPORT_OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()