# STT Accuracy Test Report — Voice Screening Calls

**Project:** Zecpath AI Hiring Platform
**Module:** screening_ai
**Generated from:** tests/test_day24_stt_accuracy.py

---

## 1. Per-Clip Results

| Clip | Language | Accent | Noise | WER | Confidence | Flagged |
|---|---|---|---|---|---|---|
| C01 | en | Indian English | clean | 0.167 | 0.652 | no |
| C04 | hi | Hindi (native) | clean | 0.667 | 0.564 | yes |
| C06 | ml | Malayalam (native) | clean | 1.0 | 0.001 | yes |
| C08 | ta | Tamil (native) | clean | 1.0 | 0.0 | yes |

## 2. Accuracy by Language

| Language | Clips | Avg WER | Avg Confidence |
|---|---|---|---|
| en | 1 | 0.167 | 0.652 |
| hi | 1 | 0.667 | 0.564 |
| ml | 1 | 1.0 | 0.001 |
| ta | 1 | 1.0 | 0.0 |

## 3. Accuracy by Noise Condition

| Noise Condition | Clips | Avg WER | Avg Confidence |
|---|---|---|---|
| clean | 4 | 0.709 | 0.304 |

## 4. Overall Summary

- Total clips tested: 4
- Overall average WER: 0.709
- Clips flagged for review (confidence < 0.6): 3