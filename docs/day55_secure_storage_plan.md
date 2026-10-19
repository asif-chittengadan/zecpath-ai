# Day 55: Secure Storage Plan

## Purpose

Protect candidate transcripts, interview summaries, scores, recommendations,
and hiring reports from unauthorized reading or modification while preserving
the retention rules defined for ZECPATH.

## Current repository state

The repository currently writes several candidate-related outputs as plaintext
JSON or Markdown:

| Data | Current writer | Current default location |
| --- | --- | --- |
| Hiring intelligence report | `scoring/reports.py` | `data/hiring_reports/` |
| Final recommendation | `scoring/final_recommendation_generator.py` | `data/recommendations/final_recommendations.json` |
| Unified candidate score | `scoring/unified_candidate_score_generator.py` | `data/unified_scores/unified_candidate_score.json` |
| HR interview summary | `interview_ai/hr/interview_summary_pipeline.py` | `data/interview_summaries/interview_summary.json` |
| Screening report | `screening_ai/screening_report_builder.py` | Caller-supplied Markdown path |
| Voice transcript | `data/transcript_schema.json` | Schema exists; no transcript persistence writer was found |

These locations are suitable for development examples only. The current writers
do not encrypt their output. `.env` and `logs/` are ignored by Git, but the
candidate output directories above are not covered by those ignore rules.

## Proposed storage design

1. Route transcript and report writes through one `SecureRecordStore` interface.
   Producers should not write candidate records directly with `open()` or
   `write_text()`.
2. Serialize one record, encrypt it before it reaches the filesystem, and store
   ciphertext under a private storage root. Use opaque random storage filenames;
   keep candidate names and IDs inside the encrypted payload.
3. Use AES-256-GCM authenticated encryption. Generate a fresh 96-bit nonce for
   every encryption under a key. Bind the opaque record ID, record type, and
   format version as authenticated additional data. A failed authentication
   check must stop the read. The `cryptography` package provides the `AESGCM`
   API and documents its key, nonce, and authentication behavior
   ([AES-GCM documentation](https://cryptography.io/en/stable/hazmat/primitives/aead/)).
4. Store only the minimum lookup metadata outside the ciphertext: format
   version, algorithm, key identifier, nonce, and opaque storage ID. Do not put
   candidate names, transcript text, report summaries, or decisions in paths,
   filenames, or unencrypted indexes.
5. Write ciphertext atomically: create a temporary file in the protected
   directory, flush it, then replace the destination. Restrict that directory
   to the application service account and authorized operators through OS or
   storage ACLs.

## Key management

- Never hard-code encryption keys, commit them, put them in reports, or write
  them beside encrypted records.
- For local development, load a generated key from an ignored environment file
  or the operating system's credential store. The application must fail closed
  if its key is unavailable or malformed.
- In production, use a managed key service and envelope encryption: a managed
  key encrypts per-environment or per-record data keys. Grant decrypt access
  only to the storage service identity.
- Attach a key version to each encrypted object. Rotate keys on a schedule and
  after suspected exposure; support decrypting with approved old versions while
  new writes use the current version. Back up key material separately from
  ciphertext and test recovery.

## Access and audit boundaries

Encryption protects files at rest; it does not decide who may read them.
`compliance/access_control.py` now provides a default-deny RBAC check with
candidate assignment scopes, and `config/access_control_policy.json` defines
the initial role permissions. A trusted authentication layer must create the
`Principal`; callers must not accept a role or candidate assignment directly
from an untrusted request. The future storage service must call
`require_permission()` before each read, write, list, or delete operation.
Keep raw transcript and report content out of application logs and the existing
audit event stream; audit only opaque record IDs, operation, actor, timestamp,
and outcome.

## Retention and deletion

Use `config/retention_policy.json` as the source of retention periods:

- Transcript: 180 days
- AI evaluation/report: 365 days
- Audit record: 730 days

The storage service must execute the `RetentionManager` decision, delete
expired ciphertext and temporary copies, and respect legal holds. Backup copies
must follow the same retention schedule. A retention event must not contain
the transcript or report body.

## Migration sequence

1. Add and review the encrypted storage service and its key configuration.
2. Wire `AccessController` checks at the storage boundary before migrating
   writers.
3. Migrate report and transcript writers one at a time; use `.enc` outputs and
   update readers to decrypt through the service.
4. Move existing plaintext files into the encrypted store, verify the protected
   copies, then securely remove plaintext copies and temporary exports.
5. Verify key rotation, restore, retention deletion, and denied-access behavior
   before using real candidate data.

The access-control module is implemented, but the repository has no
authentication or trusted user-session layer yet, and the existing report
writers do not invoke the new checks. Generated reports remain plaintext and
must not be treated as securely stored production records until the migration
steps are complete.
