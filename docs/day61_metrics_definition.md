# Day 61 - Monitoring Metrics

## Scope

This document defines the key runtime and quality metrics requested for Day 61. It does not set alert thresholds; those belong in the alerting-rules task. Every dashboard value should show its observation window and sample count.

## Runtime metrics

| Metric | Definition | Dimensions / notes |
| --- | --- | --- |
| `pipeline_request_duration_seconds` | Time from accepting a request to returning its final response, including queue wait. Report p50 and p95. | By environment, route template, and outcome. The repository has no HTTP route yet, so initially use end-to-end command or pipeline-run duration and label it accordingly. |
| `pipeline_stage_duration_seconds` | Time spent in one stage, measured with a monotonic clock. Report p50 and p95 for parsing, scoring, screening, HR interview, technical interview, and decision generation where those stages run. | By environment, stage, model name/version, and outcome. Keep model loading and warm-up in a separate `model_startup_duration_seconds` metric. |
| `pipeline_runs_total` | Number of accepted pipeline runs, counted once when processing begins. | By environment and final outcome (`completed`, `failed`, `cancelled`). Do not count retries as new runs. |
| `pipeline_failures_total` | Number of runs ending in a terminal failure after retries are exhausted. | By stage and stable error code. Report failure rate as `terminal failures / accepted runs` for the same time window. Also show stage-level failures divided by runs that entered that stage. |
| `pipeline_retries_total` | Number of retry attempts after a recoverable error. | By stage and error code. Keep this separate from terminal failures so retries do not hide instability. |
| `pipeline_completions_per_minute` | Completed runs divided by elapsed minutes in the reporting window. | By environment; use only windows with a non-zero duration. |

## AI quality and human-review metrics

AI scores are model outputs, not ground truth. Compare them with a documented human-reviewed reference for the same candidate, role, decision stage, and model version. Do not compare an ATS score with a final hiring outcome as though they represented the same label.

### Continuous score comparison

When the AI and human reviewers use the same calibrated 0-100 scale, calculate:

- **Mean absolute score difference (percentage points):** `mean(abs(ai_score - adjudicated_human_score))`.
- **Mean signed difference (percentage points):** `mean(ai_score - adjudicated_human_score)`, which indicates average over-scoring or under-scoring.
- **Matched review coverage:** number of eligible AI assessments with a completed, matched human review divided by the number of eligible AI assessments.

Only compare records from the same role and assessment stage. Exclude incomplete reviews and document exclusions. Show the matched sample count and review period beside every value.

### Decision comparison

For a defined decision such as `advance` versus `do_not_advance`, use an adjudicated human label and report the confusion matrix, overall agreement, precision and recall for `advance`, and the false-rejection rate for candidates the human reference says should advance. Define the positive class before calculating these metrics. Report results by role and model version; keep fairness-group analysis in the separately governed audit process.

Human disagreement is possible. If multiple reviewers provide labels, record the review procedure and use an agreed adjudication rule before treating a label as the reference. Do not silently treat one reviewer's opinion as objective truth.

## Data sources and current gaps

- Runtime durations and outcomes should come from the structured operational events defined in `day61_logging_structure.md`.
- Score and decision values currently exist in local JSONL files written by `compliance/audit_logger.py`. The logger does not enforce access control or encryption; protect the files before using real candidate data or treating them as restricted production records.
- The current audit record includes a `human_review_required` flag, but it does not record a completed human review score or final review label. A governed, access-controlled review-feedback record is needed before AI-versus-human accuracy metrics can be calculated reliably.
- API request latency cannot be measured until an API boundary exists. Current local benchmark timings are service-level measurements, not HTTP response times.

## Reporting and data-quality rules

- Show p50 and p95 latency with request count and time window. Keep cold model load/warm-up separate from warm request latency.
- Show accuracy metrics with matched sample count, role, assessment stage, model version, and evaluation period. If the sample is small, label the result preliminary rather than presenting it as stable.
- Use only bounded dimensions such as environment, stage, outcome, model version, and role category. Never label metrics with candidate ID, name, request ID, email, or other high-cardinality personal data.
- Do not put raw resume text, interview transcripts, or reviewer notes in metrics. Store review labels and justifications under the approved audit and access controls.
- Define and validate a common score scale and decision mapping before comparing AI and human results. If scales differ, calibrate them before reporting an error metric.

## Summary metric set for the dashboard

1. End-to-end and per-stage p50/p95 latency, with run counts.
2. Accepted, completed, failed, and retried run counts; terminal failure rate and top error codes.
3. AI-to-human matched review coverage, score difference, and decision agreement once structured human outcomes are available.
4. Model name/version and evaluation window for every quality result.
