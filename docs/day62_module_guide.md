# Day 62 - Module Guide

This guide explains what each application package does, how its main pieces fit together, and which files currently contain no implementation. It follows the code in the repository; a module name or README description is not treated as proof that a feature is fully wired into a running service.

## Application entry points

| File | Purpose |
|---|---|
| main.py | Demonstrates extracting and normalizing one configured resume. |
| main_resume.py | Finds the first PDF in data/resumes and runs the resume text pipeline. |
| main_job_parser.py | Parses each PDF in data/job_descriptions and writes a JSON file under data/parsed_jd. |
| main_day56_full_system_simulation.py | Runs a synthetic local flow through ATS, screening, HR, technical, unified scoring, and a final decision; it omits file upload and machine-test scoring. |
| main_candidate_ranking.py and other main_day*.py files | Demonstrations, analysis runs, or day-specific experiments; they are not a production server entry point. |

## parsers - resumes and job descriptions

The parser package reads candidate and job documents, cleans text, splits sections, extracts fields, and writes structured results.

| File or group | Explanation |
|---|---|
| pdf_reader.py, docx_reader.py | Extract source text from PDF and DOCX files. |
| resume_engine.py | Simple resume text pipeline: validate path, extract text, clean and normalize it, save cleaned text, and return it. |
| resume_section_parser.py | Structured resume path: split a resume into sections and extract personal information, skills, education, experience, projects, certifications, and languages. |
| smart_resume_parser.py | Cleans and deduplicates section-parser output and removes common page/header noise. |
| resume_errors.py | Defines input, extraction, parsing, and output exceptions, and validates resume paths. |
| text_cleaner.py, normalizer.py | Clean raw text and normalize its formatting for later parsing. |
| section_splitter.py, section_normalizer.py, section_classifier.py, section_builder.py | Identify resume headings, normalize section labels, classify text, and construct section output. |
| personal_info_extractor.py, resume_skill_extractor.py, resume_experience_extractor.py, resume_education_extractor.py | Extract core candidate fields from resume sections. |
| project_extractor.py, resume_certification_extractor.py, language_extractor.py | Extract projects, certifications, and languages from structured resume sections. |
| heading_detector.py | Detects likely section headings in document text. |
| output_writer.py | Saves cleaned resume text under data/cleaned and returns the output path. |
| job_parser.py | Coordinates job-description reading, cleanup, section extraction, and role/skill/experience/education extraction. |
| jd_cleaner.py, jd_normalizer.py, section_extractor.py | Clean and normalize job text, then divide it into named sections. |
| role_extractor.py, skill_extractor.py, experience_extractor.py, education_extractor.py, requirement_extractor.py | Extract job role, skills, experience requirements, education requirements, and other qualification requirements. |
| jd_builder.py | Produces the parsed job-description dictionary and serializes it to JSON. |
| certification_extractor.py | Extracts certification mentions for parser workflows that use it. |
| synonym_mapper.py | Maps known equivalent terms for normalization and matching. |
| resume_parser.py | Empty file; it provides no active parser implementation. |

The repository has two resume paths with different outputs: ResumeEngine returns cleaned text, while ResumeSectionParser and SmartResumeParser produce structured sections. Candidate matching consumes structured resume data, so the text-only entry point does not by itself complete ATS scoring.

## scoring - candidate evaluation and decisions

The scoring package transforms parsed candidate and job data into component scores, round totals, rankings, and recommendations.

| File | Explanation |
|---|---|
| resume_schema_adapter.py | Converts supported legacy resume shapes into the normalized ATS schema. |
| fairness_masker.py | Creates a masked scoring copy so selected identifying details are not used as matching features. |
| candidate_matching_service.py | Coordinates resume normalization, masking, skill matching, experience and education alignment, semantic similarity, and ATS score generation. |
| semantic_matching_engine.py | Uses the configured sentence-transformer model to compare skill and full-text content semantically. |
| ats_scoring_engine.py, weight_config.py | Clamp four component values, apply role-specific weights from data/scoring_weights.json, and return a score and component explanations. |
| candidate_score_generator.py | Shapes the ATS engine result into the candidate score response format. |
| screening_scoring_engine.py | Scores screening answers for clarity, relevance, completeness, and consistency, then aggregates question results. |
| unified_scoring_engine.py | Normalizes and combines available ATS, screening, HR, technical, and machine-test scores using config/unified_scoring_rules.json. |
| unified_candidate_score.py, unified_candidate_score_generator.py | Define the validated unified score record, create explanations, save JSON output, and write a score audit event. |
| explainability/explanation_generator.py | Builds a readable contribution and decision explanation from score results. |
| eligibility_decision_engine.py | Applies explicit job rules such as minimum ATS score, required skills, experience, location, and availability. |
| recommendation.py | Converts the unified score, eligibility results, and risk signals into Selected, Hold / Review, or Rejected. |
| final_recommendation_generator.py | Coordinates recommendation inputs, logs the decision, and saves the result as JSON. |
| ranking_engine.py, shortlisting_module.py | Sorts candidates by score, assigns ranks, and classifies candidates by configured thresholds. |
| bias_evaluator.py | Evaluates candidate-score differences across groups using supplied comparison data. |
| reports.py | Builds a hiring intelligence report from candidate-profile and scoring data. |
| score_engine.py | Empty file; it provides no active score engine. |

The component APIs are usually called separately. The Day 56 simulation demonstrates one synthetic integration of ATS, screening, HR, technical, unified scoring, and final decision. It uses fixture resume/JD data, demo HR responses, illustrative technical rubric values, and no machine-test score; it does not establish a production file-upload or parser-to-ATS flow.

## screening_ai - candidate screening conversation

The screening package contains response-processing helpers and a state-machine controller for text or voice screening.

| File | Explanation |
|---|---|
| conversation_flow.py | Manages screening question/answer progression, retries, silence, confusion, repeated or invalid answers, fallbacks, follow-ups, and completion state. |
| stt.py | Converts supported audio input into a transcript using the configured speech-recognition dependency. |
| transcript_normalizer.py | Cleans transcript text before downstream answer analysis. |
| answer_understanding_engine.py | Extracts structured meaning or answer attributes from a response. |
| intent_classifier.py | Classifies response intent using configured rules. |
| response_quality_checker.py, edge_case_handler.py | Detect low-quality or unusual answers and determine a suitable recovery action. |
| day29_answer_adapter.py | Adapts answer-analysis output to the conversation-flow contract. |
| communication.py, behavioral_indicators.py, sentiment_analyzer.py | Derive communication, behavioral, and sentiment signals from responses. |
| availability_extractor.py, salary_expectation_extractor.py | Extract availability and salary expectation details from candidate answers. |
| screening_report_builder.py | Formats screening-session results into a report structure. |
| screening.py | Empty file; no top-level screening orchestrator is implemented here. |
| tts.py | Empty file; no text-to-speech implementation is present here. |

The conversation state machine can use these helpers, but an empty screening.py means there is no central module in that file that wires the entire screening flow together.

## interview_ai - HR, technical, behavioral, integrity, and practical evaluation

### HR interviews

The HR interview controller combines question flow and response capture with adaptive questions and multiple analysis signals.

| File or group | Explanation |
|---|---|
| hr_interview_engine.py | Main controller for the HR interview lifecycle and integration of its components. |
| interview_state.py, interview_flow.py, dynamic_conversation_state.py | Store session state, manage interview phases, and track dynamic conversation context. |
| question_generator.py, follow_up_engine.py, adaptive_follow_up_engine.py, difficulty_adapter.py, repetition_guard.py | Select questions, generate follow-ups, adapt difficulty, and avoid repeated questions. |
| response_analyzer.py, problem_solving_clarity_analyzer.py | Analyze answer quality, problem-solving clarity, and response signals. |
| communication_feature_analyzer.py, communication_scoring_engine.py, communication_score_normalizer.py | Extract and normalize communication features and produce communication scores. |
| confidence_analyzer.py, behavioral_confidence_engine.py, stress_indicator_analyzer.py, sentiment_scoring_engine.py | Analyze confidence, stress, and sentiment signals. |
| contradiction_analyzer.py, interview_risk_analyzer.py | Identify inconsistent statements and interview risk signals. |
| aptitude_evaluation_engine.py, aptitude_logic_scoring_engine.py | Evaluate aptitude and logical-reasoning answers. |
| hr_interview_scoring_engine.py, hr_scoring_config.py, hr_score_normalizer.py, unified_scoring_config.py | Configure, normalize, and combine HR interview score components. |
| interview_summary_generator.py, interview_summary_pipeline.py, hr_interview_report_generator.py | Build interview summaries and reports from session and evaluation data. |
| hr_performance_summary.py, hr_scoring_inconsistency_analyzer.py, hr_manual_evaluation_comparator.py | Summarize performance, inspect score consistency, and compare AI scores with human assessments. |
| hr_interview_simulator.py, hr_interview_simulation_runner.py, hr_interview_test_report_generator.py, day45_demo.py | Run demonstrations or simulations and create their result reports. These are support tools, not web endpoints. |

### Technical interviews

| File or group | Explanation |
|---|---|
| technical_engine.py | Main technical-interview controller coordinating state, flow, questions, role mapping, and difficulty. |
| technical_interview.py, technical_flow.py, technical_state.py | Define interview stages and experience bands, stage transitions, and per-candidate interview progress. |
| role_skill_mapper.py, question_hierarchy.py | Map a role to skill domains and select questions by stage and difficulty. |
| difficulty_adapter.py | Adjust question difficulty based on experience and answer quality. |
| answer_depth_analyzer.py | Evaluates the level of detail in a technical response. |
| technical_scoring_rubric.py, technical_scoring_engine.py, technical_score_normalizer.py | Define question-specific criteria, compute weighted answer scores, and normalize results. |
| skill_wise_scoring.py, technical_evaluation_report.py | Aggregate skill-level results and create an explainable technical evaluation report. |

### Other interview support

| File or group | Explanation |
|---|---|
| behavioral_analysis_framework.py, behavioral_evaluator.py, behavioral_scoring_model.py | Analyze behavioral observations and supplied signal scores, then summarize behavioral evaluation results. |
| integrity/integrity_detection_framework.py, malpractice_detection_logic.py, integrity_evaluator.py, risk_flagging_system.py | Evaluate interview-integrity observations and convert risk signals into review flags. |
| machine_test/machine_test_framework.py, task_evaluation_logic.py, time_based_scoring.py, machine_test_evaluator.py | Validate practical tasks, capture submissions, combine component evaluations, and apply configured time adjustments. |
| evaluation/interview_evaluator.py | Empty file; no shared evaluator implementation is present here. |
| question_bank/question_bank.py | Empty file; no question-bank class is implemented in this file. Question data is currently read by other components from JSON files. |
| adaptive_questions.py, behavior.py | Empty files; they do not provide active implementations. |

## ats_engine - legacy package placeholders

The files ats_engine/ats_score.py, ats_engine/matcher.py, and ats_engine/ranking.py are empty. Active ATS scoring and ranking behavior is implemented in the scoring package, particularly candidate_matching_service.py, ats_scoring_engine.py, ranking_engine.py, and shortlisting_module.py.

## compliance - consent, access, audit, and retention

| File | Explanation |
|---|---|
| models.py | Defines consent types and immutable consent records. |
| consent_manager.py | Creates and checks consent records for candidate-processing purposes. |
| access_control.py | Checks role-based permissions and candidate scope for a principal supplied by a trusted caller; it does not authenticate the caller. |
| audit_logger.py | Appends score and decision events to local JSONL files. |
| retention_manager.py | Calculates retention decisions and emits retention events; it does not delete files or database rows itself. |

These are compliance-support components. Their presence does not by itself mean access control, retention execution, or secure audit storage is wired around every application path.

## utils - shared support code

| File | Explanation |
|---|---|
| logger.py | Configures the project logger and its local application log. |
| json_output.py | Writes validated JSON atomically so a failed write does not leave a partially overwritten output. |
| config.py, helpers.py | Empty files; no shared configuration or helper functions are currently defined in them. |

## Configuration and data files

The JSON files in config/ supply scoring weights, eligibility rules, interview rules, conversational rules, risk settings, access policy, retention policy, and report behavior. JSON files under data/ supply question banks, role/skill lists, sample resumes and jobs, and saved output examples. They are data sources for the Python modules rather than independent services.

## Website

website/index.html is a static page. The repository does not contain a connected backend route layer serving it as an interactive hiring application.

## Module boundaries to keep in mind

1. Resume text extraction and structured resume parsing are separate pipelines.
2. ATS scoring consumes structured resume and job-description data; it is not triggered by parsing alone.
3. Screening and interview components return local objects or dictionaries; the repository does not expose them through a web API.
4. Unified scoring requires the caller to supply results from earlier stages.
5. Compliance modules provide helpers, but callers must invoke them and enforce their policies.

