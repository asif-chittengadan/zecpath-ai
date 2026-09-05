import sys
sys.path.insert(0, ".")

from faster_whisper import WhisperModel

if len(sys.argv) < 3:
    print("Usage: python tests/diagnose_stt_clip.py <audio_path> <language_code>")
    print("Example: python tests/diagnose_stt_clip.py tests/audio_samples/ta_clean_02.wav ta")
    sys.exit(1)

AUDIO_PATH = sys.argv[1]
LANGUAGE = sys.argv[2]

print(f"Testing: {AUDIO_PATH} (language={LANGUAGE})")
print("Loading medium model (reuses cache if already downloaded)...")
model = WhisperModel("medium", device="cpu", compute_type="int8")

print("\n--- Attempt 1: vad_filter=True (same as stt.py) ---")
segments, info = model.transcribe(AUDIO_PATH, language=LANGUAGE, vad_filter=True)
segments = list(segments)
print(f"Detected language: {info.language} (probability {info.language_probability:.3f})")
print(f"Segments found: {len(segments)}")
for seg in segments:
    print(f"  [{seg.start:.2f}s -> {seg.end:.2f}s] {seg.text}")

print("\n--- Attempt 2: vad_filter=False ---")
segments2, info2 = model.transcribe(AUDIO_PATH, language=LANGUAGE, vad_filter=False)
segments2 = list(segments2)
print(f"Detected language: {info2.language} (probability {info2.language_probability:.3f})")
print(f"Segments found: {len(segments2)}")
for seg in segments2:
    print(f"  [{seg.start:.2f}s -> {seg.end:.2f}s] {seg.text}")

print("\n--- Attempt 3: language=None (let Whisper auto-detect) ---")
segments3, info3 = model.transcribe(AUDIO_PATH, vad_filter=False)
segments3 = list(segments3)
print(f"Detected language: {info3.language} (probability {info3.language_probability:.3f})")
print(f"Segments found: {len(segments3)}")
for seg in segments3:
    print(f"  [{seg.start:.2f}s -> {seg.end:.2f}s] {seg.text}")

print("\n--- Attempt 4: quality-filter thresholds disabled ---")
segments4, info4 = model.transcribe(
    AUDIO_PATH,
    language=LANGUAGE,
    vad_filter=False,
    no_speech_threshold=0.1,
    log_prob_threshold=None,
    compression_ratio_threshold=None,
    condition_on_previous_text=False
)
segments4 = list(segments4)
print(f"Detected language: {info4.language} (probability {info4.language_probability:.3f})")
print(f"Segments found: {len(segments4)}")
for seg in segments4:
    print(f"  [{seg.start:.2f}s -> {seg.end:.2f}s] no_speech_prob={seg.no_speech_prob:.3f} avg_logprob={seg.avg_logprob:.3f}")
    print(f"    text: {seg.text}")