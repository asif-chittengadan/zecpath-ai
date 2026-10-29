# Day 62 - Zecpath AI System Reference

This reference records the architecture, callable Python interfaces, scoring rules, and data contracts present in the repository. It describes the current implementation, including features that remain separate components rather than one running service.

## 1. Architecture

Zecpath AI is a modular Python codebase. The top-level packages divide work by responsibility:

| Package | Responsibility |
|---|---|
| `parsers/` | Read and normalize resumes and job descriptions; extract structured fields. |
| `ats_engine/` | Earlier ATS matching and ranking components. |
| `scoring/` | Resume-to-job scoring, interview-round aggregation, eligibility, recommendations, explainability, and fairness helpers. |
| `screening_ai/` | Speech and transcript utilities, response analysis, and a conversation state machine. |
| `interview_ai/hr/` | HR interview state, questions, adaptive follow-ups, response signals, and scoring. |
| `interview_ai/technical/` | Technical interview flow, question selection, difficulty adaptation, and answer scoring. |
| `interview_ai/machine_test/` | Practical task submission evaluation and time adjustment. |
| `compliance/` | Consent, access policy checks, audit events, and retention decisions. |
| `config/`, `data/`, `logs/` | JSON rules and sample data, local outputs, and logs. |

Other interview modules provide behavioral evaluation, interview-integrity and risk checks, reusable evaluation helpers, and question-bank access.

The main runnable scripts are batch or demonstration entry points: `main.py` processes a configured resume, `main_resume.py` processes the first PDF in `data/resumes/`, and `main_job_parser.py` parses PDFs from `data/job_descriptions/`. `main_day56_full_system_simulation.py` wires ATS, screening, HR interview, technical interview, unified scoring, and a final decision into a synthetic demonstration. It uses fixture data and illustrative technical rubric inputs, skips machine-test scoring, and does not exercise a real upload-to-parser-to-ATS path. The repository does not provide a production application server.

The intended information flow is:

1. Resume and job-description parsers produce text or structured data.
2. `CandidateMatchingService` compares structured resume data with a parsed job description and returns an ATS score.
3. Screening, HR interview, technical interview, and machine-test components produce stage results independently.
4. `UnifiedScoringEngine` combines available stage scores. `FinalRecommendationGenerator` can apply eligibility and risk checks, write a decision record, and log it.

Each stage can be called separately. The Day 56 script is a synthetic integration harness for selected stages; there is no production orchestrator that carries real uploaded candidate files through every stage.

## 2. API Surface

There are no implemented FastAPI or Flask routes in the project source. The API currently means callable Python classes and functions; clients use imports and method calls. The package list or README mentioning FastAPI does not by itself provide HTTP endpoints.

| Interface | Main contract |
|---|---|
| `parsers.resume_engine.ResumeEngine.process(file_path)` | Reads PDF/DOCX resume text, cleans and normalizes it, writes `data/cleaned/<name>.txt`, and returns normalized text. |
| `parsers.job_parser.JobParser.parse(pdf_path)` | Parses a job-description PDF and returns `{role, skills, experience, education}`. `JDBuilder.save(jd, output_file)` writes the object as JSON. |
| `scoring.candidate_matching_service.CandidateMatchingService.generate_score(resume, job_description)` | Accepts structured resume data and a JD dictionary; returns candidate/role, ATS score and percentage, component scores, weights, and explanations. `generate_scores(...)` processes an iterable of resumes. |
| `scoring.screening_scoring_engine.ScreeningScoringEngine.score_question(...)` / `aggregate_scores(...)` | Scores one answer and aggregates per-question results into a screening score and parameter breakdown. |
| `screening_ai.conversation_flow.ConversationFlowEngine.start(session_id, candidate_id, questions)` | Starts a screening conversation state machine and returns an in-memory `ConversationContext`; it is not an HTTP session API. |
| `interview_ai.hr.hr_interview_engine.HRInterviewEngine` | Construct with session/candidate/role metadata; `start()` begins and `submit_response(response)` advances the HR interview. It also exposes state, signal-history, and scoring methods. |
| `interview_ai.technical.technical_engine.TechnicalInterviewEngine` | Construct with `candidate_id`, `role`, and `experience_years`; use `get_next_question()`, `submit_answer(...)`, and `get_progress()` to control the interview. |
| `scoring.unified_scoring_engine.UnifiedScoringEngine.calculate_score(...)` | Aggregates required ATS, screening, and HR scores plus optional technical and machine-test scores. |
| `scoring.unified_candidate_score_generator.UnifiedCandidateScoreGenerator.generate(...)` | Builds a validated unified-score record, writes local JSON output, and logs a score audit event. |
| `scoring.final_recommendation_generator.FinalRecommendationGenerator.generate(...)` | Combines unified score with optional eligibility and risk results, writes a recommendation JSON file, and logs a decision audit event. |
| `main_day56_full_system_simulation.run_simulation(...)` | Runs the synthetic Day 56 flow and writes a report; it is a local demonstration entry point, not an HTTP endpoint. |

These are in-process interfaces. The repository does not define HTTP authentication, request/response schemas, endpoint versioning, or a deployed API server.

## 3. Scoring Logic

### ATS resume-to-job score

`CandidateMatchingService` normalizes the resume schema, removes identifying details from the scoring copy, computes skill, experience, education, and semantic similarity components, then calls `ATSScoringEngine`.

```text
ATS score (0..1) = skill_match × skill_weight
                  + experience_relevance × experience_weight
                  + education_alignment × education_weight
                  + semantic_similarity × semantic_weight
Percentage = ATS score × 100
```

All four inputs are clamped to 0..1. Default weights are 0.35 / 0.30 / 0.15 / 0.20. Role-specific weights are in `data/scoring_weights.json`; they must total 1.0.

### Screening score

Each answer is scored on clarity, relevance, completeness, and consistency on a 0..10 scale. The values are converted to 0..100 and combined using `config/screening_scoring_rules.json`; the current four weights are equal at 0.25. The aggregate is the mean of each weighted parameter across evaluated answers, summed to a 0..100 total.

### HR and technical interview scores

- HR score: answer relevance 30%, communication 25%, confidence 20%, and consistency 25%, configured in `config/hr_interview_scoring_rules.json`.
- Technical score: accuracy 40%, depth 25%, logical reasoning 20%, and real-world applicability 15% by default. Question-type rubrics can replace these weights. The scoring function accepts component scores as inputs; it does not itself establish that those judgments were generated automatically from an answer.
- Machine-test score: correctness, efficiency, code quality, and problem-solving components are evaluated, with an optional time bonus or penalty. The evaluator marks the result as requiring human review.

### Unified candidate score and recommendation

The configured default round weights are ATS 25%, screening 15%, HR 20%, technical 25%, and machine test 15%. The score engine requires ATS, screening, and HR inputs; technical and machine-test scores are optional. If only the required three rounds are supplied, legacy weights apply (default 40% / 25% / 35%). If additional rounds are supplied, active round weights are renormalized to total 100%.

The score result includes raw and normalized round scores, effective weights, weighted contributions, unified score, and explainability. The Day 56 simulation supplies ATS, screening, HR, and technical scores but omits the optional machine-test score. It uses synthetic data, demo HR heuristics, and explicit technical rubric inputs; it is evidence that those selected components can be joined in one local run, not that production candidate intake is integrated. The recommendation engine has default thresholds of 75 for selection and 50 for review; failed eligibility rules can reject, while unresolved eligibility or high-risk signals can force human review. These thresholds are application logic, not evidence of validated hiring policy.

## 4. Data Models and Persistence

### Resume and job description

`ResumeSchemaAdapter` normalizes accepted resume input to these fields:

```text
Summary: list of text
Skills: {technical: list, business: list, creative: list}
Experience: {total_experience: {years, months, total_months}}
Education: {degree, field_of_study}
Projects: list of text
Others: list of text (including display-name metadata when present)
```

The parsed job-description JSON contract is:

```json
{
  "role": "string",
  "skills": ["string"],
  "experience": {"minimum": 0, "maximum": 0, "text": "string"},
  "education": ["string"]
}
```

The exact experience object is parser-produced and may contain additional fields; the scoring service accepts and normalizes common aliases.

### Session and score records

- Screening uses an in-memory `ConversationContext` with session/candidate IDs, questions, current state, counters, answers, and events.
- HR interview state stores session/candidate IDs, role, interview phase, current question, response history, and completion status.
- Technical interview state stores candidate/role/experience, stage, difficulty, question history, and completion status.
- `UnifiedCandidateScore` contains candidate identity, role, round scores, normalized scores, weights, weighted scores, a 0..100 unified score, and `human_review_required` (true by default).
- Consent and retention use immutable dataclasses. Audit events are JSONL records containing event IDs, timestamps, candidate IDs, scores or decision details, and schema version.

### Storage status

Structured outputs and configuration are primarily local JSON files. `db/screening_schema.sql` defines relational tables for candidates, jobs, screening sessions, transcripts, and review flags; no database connection or ORM integration was found in the application modules. The audit logger writes local JSONL files. Revisit this status if a persistent service or database backend is added.

## 5. Source Map

- Architecture and run entry points: `README.md`, `main.py`, `main_resume.py`, `main_job_parser.py`
- Parser contracts: `parsers/resume_engine.py`, `parsers/job_parser.py`, `parsers/jd_builder.py`, `scoring/resume_schema_adapter.py`
- ATS and unified scoring: `scoring/candidate_matching_service.py`, `scoring/ats_scoring_engine.py`, `scoring/unified_scoring_engine.py`, `config/unified_scoring_rules.json`, `data/scoring_weights.json`
- Screening/interview scoring: `scoring/screening_scoring_engine.py`, `config/screening_scoring_rules.json`, `interview_ai/hr/hr_interview_scoring_engine.py`, `interview_ai/technical/technical_scoring_engine.py`
- Core records and storage schema: `scoring/unified_candidate_score.py`, `screening_ai/conversation_flow.py`, `interview_ai/hr/interview_state.py`, `interview_ai/technical/technical_state.py`, `compliance/models.py`, `db/screening_schema.sql`
