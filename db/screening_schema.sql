-- Zecpath AI Hiring Platform
-- Database schema for AI voice screening interactions
-- Module: screening_ai

CREATE TABLE candidates (
    candidate_id        VARCHAR(16)   PRIMARY KEY,   -- CAND-######
    full_name           VARCHAR(255)  NOT NULL,
    email                VARCHAR(255),
    phone                VARCHAR(32),
    resume_path          VARCHAR(512),
    created_at           TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jobs (
    job_id                VARCHAR(16)   PRIMARY KEY,   -- JOB-######
    role                  VARCHAR(255)  NOT NULL,
    company               VARCHAR(255),
    jd_path               VARCHAR(512),
    created_at            TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE screening_sessions (
    session_id            VARCHAR(24)   PRIMARY KEY,   -- SESSION-YYYYMMDD-####
    candidate_id          VARCHAR(16)   NOT NULL REFERENCES candidates(candidate_id),
    job_id                VARCHAR(16)   NOT NULL REFERENCES jobs(job_id),
    language              VARCHAR(8)    NOT NULL DEFAULT 'en',
    started_at            TIMESTAMP     NOT NULL,
    completed_at           TIMESTAMP,
    status                VARCHAR(16)   NOT NULL DEFAULT 'in_progress'
                           CHECK (status IN ('in_progress', 'completed', 'abandoned', 'failed'))
);

CREATE TABLE screening_transcripts (
    transcript_id          VARCHAR(24)   PRIMARY KEY,   -- TR-YYYYMMDD-####
    session_id             VARCHAR(24)   NOT NULL REFERENCES screening_sessions(session_id),
    candidate_id           VARCHAR(16)   NOT NULL REFERENCES candidates(candidate_id),
    job_id                 VARCHAR(16)   NOT NULL REFERENCES jobs(job_id),
    question_id            VARCHAR(32)   NOT NULL,      -- matches id in hr_screening_questions.json
    turn_index             INTEGER       NOT NULL,
    timestamp               TIMESTAMP     NOT NULL,
    speaker                 VARCHAR(16)   NOT NULL CHECK (speaker IN ('candidate', 'ai')),
    raw_transcript          TEXT,
    normalized_transcript   TEXT,
    confidence_level        DECIMAL(4,3)  CHECK (confidence_level BETWEEN 0.0 AND 1.0),
    answer_type              VARCHAR(16)   CHECK (answer_type IN ('open_text', 'number', 'choice', 'list', 'boolean', 'date')),
    extract_field             VARCHAR(64),
    extracted_value            TEXT,          -- stored as text, cast by extract_field's expected type on read
    audio_duration_seconds     DECIMAL(6,2),
    retry_count                 INTEGER       NOT NULL DEFAULT 0,
    flagged_for_review           BOOLEAN       NOT NULL DEFAULT FALSE,

    UNIQUE (session_id, turn_index)
);

CREATE INDEX idx_transcripts_session ON screening_transcripts(session_id);
CREATE INDEX idx_transcripts_candidate ON screening_transcripts(candidate_id);
CREATE INDEX idx_transcripts_question ON screening_transcripts(question_id);
CREATE INDEX idx_transcripts_flagged ON screening_transcripts(flagged_for_review) WHERE flagged_for_review = TRUE;

CREATE TABLE review_flags (
    flag_id                SERIAL        PRIMARY KEY,
    transcript_id           VARCHAR(24)   NOT NULL REFERENCES screening_transcripts(transcript_id),
    reason                   VARCHAR(64)   NOT NULL,     -- e.g. confidence_below_threshold, ambiguous_answer
    resolved                 BOOLEAN       NOT NULL DEFAULT FALSE,
    resolved_by               VARCHAR(255),
    resolved_at                TIMESTAMP
);
