# Day 61 - Monitoring Dashboard Design

## Purpose

Provide a clear view of candidate-processing health and interview outcomes while keeping candidate identity, review notes, and decision audit details out of general operational dashboards. This is a dashboard blueprint; the repository does not currently contain a monitoring UI or a deployed API.

## Audience and access

| View | Audience | Content |
| --- | --- | --- |
| Operations overview | System operator / developer | Pipeline volume, latency, failures, retries, model readiness, and alert status. No candidate names or raw application content. |
| Interview outcomes | Hiring operations / authorized HR users | Interview scheduling and completion counts, stage progression, and human-review outcomes by role and stage. Use aggregated counts. |
| AI quality | Model owner / authorized reviewer | Matched AI-human score and decision metrics, model version, review coverage, sample count, and evaluation period. Label results preliminary when samples are small. |
| Decision audit | Authorized auditor, in a separate restricted view | Access to individual decision records through a protected audit service after authorization is enforced at the storage boundary. The current `AuditLogger` writes local files directly and does not enforce access control. Do not embed raw audit records in the general dashboard. |

## Global filters and conventions

- Time range and reporting window.
- Environment (`development`, `staging`, `production`) when those environments exist.
- Role category, pipeline stage, outcome, and model version.
- Display counts and denominators with every rate; use an explicit “insufficient data” state rather than showing zero when data is missing.
- Use bounded aggregate dimensions only. Do not offer candidate ID, name, email, request ID, transcript, or resume-text filters in general dashboard views.
- Keep protected-group fairness analysis in a separately governed audit view with its own access rules.

## Page 1 - Candidate pipeline health

### Top summary cards

1. Accepted pipeline runs.
2. Completed runs and completion rate (`completed / accepted`).
3. Terminal failure rate (`terminal failures / accepted`) with failed count.
4. End-to-end p50 and p95 latency with request count and time window.
5. Model readiness and active critical/warning alerts.

### Processing funnel

Show counts and conversion rates for applicable stages:

`Resume received -> Parse succeeded -> ATS scored -> Screening completed -> HR interview completed -> Technical interview completed -> Decision generated`

For each step, show the number entering and completing the step, the conversion percentage, and the number of records missing that stage outcome. Separate operational failures from expected workflow outcomes such as withdrawal, no-show, or a human decision not to advance. Do not infer that an omitted stage means a candidate failed.

### Latency and failure panels

- Horizontal stage-latency chart with p50 and p95 for parsing, ATS scoring, screening, HR interview, technical interview, and decision generation.
- Time-series chart for accepted, completed, retried, and terminally failed runs.
- Failure table grouped by stage and error code, with count, rate, first/last seen, and related alert/runbook link.
- Model startup/warm-up time shown separately from warm request latency.

## Page 2 - Interview outcomes

Show separate results for HR and technical interview stages, with role category and reporting period filters.

- **Interview completion rate:** completed interviews divided by scheduled interviews. Show no-shows, cancellations, and withdrawals separately when those statuses are available.
- **Interview advancement rate:** candidates marked to advance by the recorded human decision divided by completed interviews with a final review decision. Do not count pending or missing decisions in the denominator.
- **AI-human agreement:** show only when matched, adjudicated labels are available; display the matched sample count, review coverage, role, stage, model version, and period beside the metric.
- Trend charts should display counts alongside rates so a small denominator is visible.
- Provide a stage comparison for HR versus technical interviews without combining their distinct rubrics into one success score.

“Success” means progression under the defined human review outcome for that stage. It does not mean that a candidate was hired, nor does it mean the AI's score was correct. If the organization chooses a different business definition, record it and update the dashboard labels before use.

## Page 3 - AI quality and model tracking

- Mean absolute score difference and mean signed score difference against adjudicated human reviews.
- Decision agreement, advance precision/recall, and false-rejection rate for the declared positive class.
- Matched human-review count and coverage; clearly mark quality as “not measurable” if review labels are absent.
- Comparison by model version and evaluation period. Do not mix versions in one trend without labeling deployments.
- Show evaluation sample counts and a link to the applicable review methodology. Do not expose reviewer notes or individual candidate records in the aggregate view.

## Page 4 - Alert and audit links

- Current alert count by severity, affected stage/model version, time opened, and owner/runbook action.
- Recent service incidents and their resolution state.
- Once a protected audit service is implemented, provide an authorized link from an operational event or `audit_event_id` to the audit system. The general dashboard should not display candidate identifiers or full decision reasons.

## Data sources and availability states

| Panel | Intended source | Current availability |
| --- | --- | --- |
| Pipeline volume, stage latency, failures, retries | Structured operational events from `day61_logging_structure.md` | Not yet emitted consistently by the application. |
| Score/decision audit history | Local JSONL files from `compliance/audit_logger.py` | Score and decision events exist, but the logger does not enforce access control or encryption. Connect a protected storage boundary before production use. |
| Completed interview schedule/outcome | Interview workflow status events | Must be captured consistently before completion and advancement rates can be computed. |
| AI-versus-human quality | Matched AI output plus completed, adjudicated human review feedback | Not currently available as a structured review dataset; show “not measurable” until added. |
| API latency and availability | API request logs and readiness checks | No API route is currently present. |

## Refresh and presentation rules

- Refresh operational counts, latency, failures, and alert state on a short interval such as one minute when a monitoring backend is available.
- Refresh human-review quality on a daily or weekly cadence, based on completed labels; always show the evaluation window.
- Avoid presenting p95 or accuracy values without their sample counts. Use the provisional minimum sample rules from `day61_alerting_rules.md` for pilot quality checks, and confirm them before production.
- Use consistent definitions from `day61_metrics_definition.md`. Display UTC or one clearly labeled business timezone across every time series.
- Keep colors and labels consistent for status: completed, in progress, failed, and awaiting human review. Never use color alone to communicate status.

