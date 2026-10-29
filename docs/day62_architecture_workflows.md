# Day 62 - Architecture Diagrams and Workflows

These diagrams describe the code present in the repository. Solid arrows show a flow implemented within a component or demonstrated by the Day 56 simulation. Dashed arrows show a caller-supplied handoff or an optional component; they do not mean that a production service automatically connects the steps.

## 1. Candidate evaluation modules

```mermaid
flowchart LR
  subgraph Documents
    Resume[Resume file or structured resume]
    JD[Job description PDF or structured JD]
  end

  Resume --> ResumeParse[Resume parsing components]
  JD --> JDParse[JobParser and JDBuilder]
  ResumeParse -. caller handoff .-> Adapter[ResumeSchemaAdapter]
  Adapter --> Match[CandidateMatchingService]
  JDParse -. caller supplies parsed JD .-> Match
  Match --> ATS[ATS score and explanation]

  subgraph SeparateStages[Separately callable evaluation stages]
    Conversation[Screening conversation]
    ScreenScore[ScreeningScoringEngine]
    HR[HR interview]
    Tech[Technical interview]
    Machine[Machine-test evaluator]
  end
  Conversation --> ScreenScore

  ATS -. caller supplies score .-> Unified[UnifiedScoringEngine]
  ScreenScore -. caller supplies score .-> Unified
  HR -. caller supplies score .-> Unified
  Tech -. caller supplies score .-> Unified
  Machine -. optional caller supplies score .-> Unified
  Unified --> Decision[FinalRecommendationGenerator]
  Eligibility[Eligibility rules and risk signals] -. optional inputs .-> Decision
  Decision --> Report[Recommendation JSON]
  Unified --> ScoreAudit[Score audit JSONL]
  Decision --> DecisionAudit[Decision audit JSONL]
```

The dashed boundaries matter: most modules return Python objects or dictionaries. The calling code is responsible for passing outputs between stages. The Day 56 simulation is the repository's explicit synthetic integration example; its limits are shown below.

## 2. Document parsing and ATS handoff

```mermaid
flowchart TD
  ResumeFile[Resume PDF or DOCX] --> TextPath[ResumeEngine]
  TextPath --> CleanText[Cleaned text file]

  ResumeFile --> StructuredPath[ResumeSectionParser]
  StructuredPath --> SmartParser[SmartResumeParser cleanup]
  SmartParser -. caller handoff .-> ResumeAdapter[ResumeSchemaAdapter]
  ResumeAdapter -. caller handoff .-> Matching[CandidateMatchingService]

  JDFile[Job description PDF] --> JobParser[JobParser]
  JobParser --> JDObject[Role, skills, experience, education]
  JDObject --> JDWriter[JDBuilder.save]
  JDWriter --> JDFileOut[Parsed JD JSON]
  JDObject -. caller supplies object .-> Matching

  Matching --> ATSResult[ATS score, component scores, explanations]
  Fixture[Day 56 structured JSON fixture] --> Matching
```

ResumeEngine produces cleaned text; it does not produce the structured resume object expected by ATS matching. The structured parser and ATS adapter are callable separately, but the repository's standard resume scripts do not connect them automatically. The Day 56 simulation loads structured resume and job data directly from its fixture, bypassing file upload and document parsing.

## 3. Day 56 synthetic end-to-end simulation

```mermaid
flowchart TD
  Fixture[data/day56_simulation_input.json] --> Consent[Synthetic consent grants and checks]
  Consent --> ATS[CandidateMatchingService]
  Consent --> Screening[ConversationFlowEngine]
  Screening --> ScreeningScore[ScreeningScoringEngine]
  Consent --> HR[HRInterviewEngine with demo responses]
  Consent --> Technical[TechnicalInterviewEngine question flow]
  Rubric[Illustrative rubric values in fixture] --> TechScore[TechnicalScoringEngine]
  Technical --> TechScore

  ATS --> Unified[UnifiedCandidateScoreGenerator]
  ScreeningScore --> Unified
  HR --> Unified
  TechScore --> Unified
  Unified --> Recommend[FinalRecommendationGenerator]
  ReviewRule[Synthetic rule requiring human review] --> Recommend
  Recommend --> FinalReport[reports/day56_e2e_run.json]

  HumanCases[data/day30_test_cases.json] --> Intent[IntentClassifier]
  Intent --> Agreement[Separate 10-case screening agreement summary]
  Agreement --> FinalReport

  MachineTest[Machine-test score is omitted]
```

What this simulation proves:

- The local script can join ATS, screening, HR, technical, unified scoring, and a final recommendation in one synthetic run.
- Score and decision audit records are written to a temporary directory during the run; the durable output is the JSON report.
- A separate human-reference dataset is used for screening-intent agreement. It does not contain a human rating for the simulated candidate.

What it does not prove:

- Candidate file upload or a PDF/DOCX parser-to-ATS handoff. The resume and job data are loaded from a structured JSON fixture.
- A machine-test scoring round. No machine-test score is supplied to unified scoring.
- Automatic technical scoring of free-text answers. The interview question flow is exercised, but the technical rubric values are supplied by the fixture.
- Production hiring accuracy, fairness, or throughput. HR answers are synthetic and use demonstration heuristics; the final recommendation receives an explicit review rule.

## 4. Screening conversation workflow

```mermaid
flowchart TD
  Start[Start session with questions] --> Ask[Ask current question]
  Ask --> Response[Receive candidate response]
  Response --> Empty{Response empty?}
  Empty -- yes --> Silence[Count silence and retry]
  Silence --> SilenceLimit{Retry limit reached?}
  SilenceLimit -- no --> Ask
  SilenceLimit -- yes --> Fallback[Ask fallback or skip question]

  Empty -- no --> Analyze[Optional quality checks and answer analysis]
  Analyze --> Confused{Confused?}
  Confused -- yes --> Confusion[Clarify, retry, then fallback if needed]
  Confused -- no --> Repeated{Repeated?}
  Repeated -- yes --> Repetition[Redirect, retry, then fallback if needed]
  Repeated -- no --> Valid{Answer valid?}
  Valid -- no --> Invalid[Fallback or skip question]
  Valid -- yes --> Store[Store answer]
  Store --> FollowUp{Follow-up requested?}
  FollowUp -- yes --> AskFollowUp[Ask follow-up and store response]
  FollowUp -- no --> Advance[Advance to next question]
  AskFollowUp --> Advance
  Fallback --> Advance
  Confusion --> Advance
  Repetition --> Advance
  Invalid --> Advance
  Advance --> More{Questions remain?}
  More -- yes --> Ask
  More -- no --> Complete[Mark conversation complete]
```

An answer analyzer is optional. When supplied, the Day 56 simulation uses Day29AnswerAdapter to connect semantic answer understanding to the state machine. Speech-to-text is available as a separate utility; no text-to-speech implementation is present in screening_ai/tts.py.

## 5. Interview score handoffs

| Stage | Session/result flow | Score passed onward |
|---|---|---|
| Screening | Conversation state machine stores accepted responses; screening scorer evaluates the questions and aggregates them. | Screening score on a 0-100 scale. |
| HR interview | HRInterviewEngine runs question flow and captures responses; analyzers and the HR scoring engine build component scores. | HR interview score on a 0-100 scale. |
| Technical interview | TechnicalInterviewEngine manages stage, difficulty, questions, and progress; the technical scoring engine consumes rubric component values. | Technical score on a 0-100 scale. |
| Machine test | MachineTestEvaluator validates task and submission data, evaluates components, and applies time adjustment. | Optional score on a 0-100 scale; not used in the Day 56 simulation. |

Unified scoring accepts stage scores; it does not start these interviews itself. Human review remains an explicit part of score, risk, and decision handling.

