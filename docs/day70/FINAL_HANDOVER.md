# Day 70 - Final Demo and Handover

## Purpose and completion status

The Day 70 work prepares the final system walkthrough and submission package. A local, synthetic end-to-end pipeline run is recorded in `reports/day70_final_demo.json`; the full automated test suite passed. This is an offline demonstration of the repository's pipeline. It is not a live presentation to the company, a production deployment, or a connection to the company's official website.

| Day 70 item | Status |
| --- | --- |
| Final system demo | Local synthetic pipeline run completed; in-person/live presentation remains external. |
| Knowledge transfer | Written handover and code map prepared; an actual walkthrough session remains external. |
| Internship evaluation | Pending. No mentor or reviewer feedback or score has been supplied. |
| Final submission package | Repository source, documentation, reports, and Day 70 PDF are indexed here. |

## Re-run the demo

From the project root in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
python -c "from pathlib import Path; from main_day63_end_to_end_simulation import run_simulation; result = run_simulation(output_path=Path('reports/day70_demo_rerun.json')); print('Profiles:', result['candidate_count'])"
```

The rerun writes to `reports/day70_demo_rerun.json` so it does not replace the recorded final run. The Sentence Transformers model may need to be downloaded on first use; once cached, the local model can be reused. To run automated tests:

```powershell
python -m pytest -q
```

Verified on 2026-11-09: **679 passed, 8 subtests passed**.

## Pipeline walkthrough

The runner is `main_day63_end_to_end_simulation.py`. It loads `data/day63_demo/dataset_manifest.json`, validates that the manifest is synthetic-only, resolves candidate and job-description fixture files under the dataset directory, and processes each profile through the stages below. Each candidate's stage inputs, intermediate scores, recommendation, and limitations are saved in the report.

1. **Resume intake and ATS:** The runner supplies already structured synthetic resume JSON; the production upload and resume parser are not exercised. `CandidateMatchingService` normalizes the resume, masks protected fields on a scoring copy, extracts skills, and computes the ATS result.
2. **Screening:** `ConversationFlowEngine` advances through supplied sample questions and answers; `ScreeningScoringEngine` applies its configured rubric.
3. **HR interview:** `HRInterviewEngine` uses fixture responses and the repository's deterministic demonstration heuristics.
4. **Technical interview:** the stage stores sample questions and responses, while the final numeric score comes from an explicit rubric fixture.
5. **Machine test:** the report stores sample code and a fixture execution summary. The runner does not execute or sandbox candidate code.
6. **Unified score and recommendation:** the configured weights combine the five scores. Eligibility rules and recommendation thresholds produce the final demo outcome.
7. **Report:** the runner writes a JSON record and pipeline-level observations. Consent records created by this runner are synthetic demo grants, not candidate authorization.

## Models and scoring logic

`scoring/semantic_matching_engine.py` loads the shared `all-MiniLM-L6-v2` Sentence Transformer model. It encodes text and compares vectors with cosine similarity. A process-wide model lock avoids duplicate initialization, while an LRU cache stores up to 256 encoded text values. `CandidateMatchingService` uses this for semantic text and skill similarity; exact skill matches are also handled explicitly.

The default ATS score for the demo role is:

`ATS = 100 x (0.35 x skill match + 0.30 x experience relevance + 0.15 x education alignment + 0.20 x semantic similarity)`

Each ATS component is normalized to 0-1. The unified score uses 0-100 inputs and the default weights in `config/unified_scoring_rules.json`:

`Unified = 0.25 x ATS + 0.15 x screening + 0.20 x HR + 0.25 x technical + 0.15 x machine test`

The configured interview rubrics are HR: relevance 0.30, communication 0.25, confidence 0.20, consistency 0.25; technical: accuracy 0.40, depth 0.25, reasoning 0.20, applicability 0.15; and machine test: correctness 0.40, efficiency 0.20, code quality 0.20, problem solving 0.20. Recommendation defaults are Selected at 75 or above, Hold / Review at 50-74.99, and Rejected below 50, with eligibility or risk rules able to require review or rejection.

## Recorded demo result

Four fictional Python-role profiles completed the configured pipeline. The recorded pipeline-measured total was **0.7726 seconds**; model initialization and first-use downloads are excluded from that report measurement, so it is not a production benchmark.

| Synthetic profile | ATS | Unified | Demo recommendation |
| --- | ---: | ---: | --- |
| Alex Morgan | 95.59 | 90.45 | Selected |
| Riley Chen | 94.71 | 81.44 | Selected |
| Taylor Brooks | 67.91 | 77.73 | Selected |
| Jamie Rivera | 70.60 | 61.71 | Hold / Review |

One recorded finding is that HR scores ranged only from 87.93 to 90.12 across varied profiles. This narrow 2.19-point spread suggests the deterministic HR heuristics do not distinguish these fixture profiles well; the score should be treated as a conversation aid, not a reliable ranking signal.

## Code map and handover discussion

- `main_day63_end_to_end_simulation.py` - orchestration and report writing.
- `data/day63_demo/` - manifest, fictional resumes, job descriptions, answers, and assessment fixtures.
- `scoring/semantic_matching_engine.py`, `scoring/candidate_matching_service.py`, and `scoring/ats_scoring_engine.py` - semantic matching, resume normalization, and ATS scoring.
- `screening_ai/conversation_flow.py` and `scoring/screening_scoring_engine.py` - screening state and rubric.
- `interview_ai/hr/`, `interview_ai/technical/`, and `interview_ai/machine_test/` - interview stages and scoring logic.
- `scoring/unified_scoring_engine.py`, `scoring/eligibility_decision_engine.py`, and `scoring/final_recommendation_generator.py` - combined score and outcome logic.
- `config/` - scoring weights, rubrics, and flow rules.
- `reports/day70_final_demo.json` - recorded run with scores, inputs, stage completion, and caveats.

For a knowledge-transfer session, walk through the runner first, follow one synthetic candidate through each stage, explain the default weights and decision thresholds, then discuss the HR score spread, fixture-only technical/machine-test evaluation, and how a future production interface would require secure upload, real consent, human review, access controls, and monitored deployment.

## Boundaries and external follow-up

This package documents a local prototype. It does not claim that the official company website was modified, that an application UI or production API is connected, or that all live integrations are complete. The demo uses fictional inputs and predetermined interview/rubric values. It does not execute supplied code. Recommendations must not be used for actual employment decisions without meaningful human review and appropriate validation.

The evaluator discussion and internship evaluation have not occurred in this workspace. No reviewer ratings or feedback are invented here. The remaining Day 70 actions are to present the walkthrough, transfer knowledge to the relevant team, and record the real evaluator's outcome when received.
