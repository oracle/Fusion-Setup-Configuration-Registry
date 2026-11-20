# Task-owned export evidence adapter

## Core authentication reuse

The adapter follows the Expenses SIC Codes and Corporate Card Expense Types
pattern: core owns authentication, cache storage, service context and transport.
The selected properties are frozen and checked around authentication and reads.
A changed profile stops the operation. This adapter always requests fresh core
OAuth login, even when `--force-login` is omitted. The flag is compatibility-only;
there is no cached-token or explicit-token override. `--open-browser` lets core
open sign-in. Every delegated live session also requires fresh authentication
and per-sign-in manual account confirmation under [the live workflow](live-setup-workflow.md).

Only read-only status/download failures with HTTP 401/403 may refresh once and
repeat the read. Creation is always one attempt: even 401/403 leaves its receipt
for reconciliation and does not replay the POST. A failed refresh stops.
Core still does not verify token subject against the configured username;
manual account confirmation is separate evidence, not an automated identity
guarantee. No custom token cache, token decoding or pillar login is introduced.

## Shared-service boundary

At the selected live export step, the task adapter delegates creation to the
public `create_setup_task_csv_export.create_export` interface. Shared services own
the request URL, body, HTTP headers and transport; the task does not patch modules
or rebuild the POST. Task-owned work is credential sanitization, exact-task
evidence validation and a one-attempt receipt. The shared interface's actual
default media/framework behavior must be qualified during current live QA;
this patch does not claim the prior custom-header live run tested that interface.

An exclusive receipt is written before the shared create call. Direct-list and
nested-items response envelopes are parsed, accepting exactly one positive ID
bound to the task. A lost response leaves SUBMISSION_UNCONFIRMED. Do not replay
the POST, infer a process ID, or edit the receipt to bypass reconciliation.

The receipt is created with private permissions through no-follow directory
descriptors and remains open across the shared call. Its update uses that same
descriptor, verifies the receipt and parent identities, and refuses substituted
files or ancestors. A post-call persistence failure retains the known ProcessId
in the sanitized recovery diagnostic; it never authorizes another export POST.
Platforms without these filesystem controls stop before creating an export.

Supported tasks are programs, existing issuers and expense-type mapping rules.
Receipts and exports stay inside the initialized active project's exports folder.
Download rechecks target/task/template binding, then delegates bounded polling,
singleton result lookup and in-memory download to shared services. Only sanitized
CSV evidence is saved, with exact headers and credentialPreservation=NOT_VERIFIED.
These sanitized snapshots are not import candidates; prepared issuer, party and
download CSVs remain header-only for this CREATE contract.

## Failure evidence and recovery

Each failure or timeout saves a new `*-diagnostic-<unique-id>.json` next to the
receipt. It records stage, failure class, task, operation, selected environment,
known ProcessId, HTTP status when available, elapsed seconds, artifact references
and a concrete recovery action. Existing diagnostics are never overwritten.
Unsafe preflight paths cannot receive diagnostics; return the sanitized report.

For terminal failures and pending jobs, persist the allowlisted status snapshot
(TaskCode, ProcessId, StatusCode and ProcessCompletedFlag). The raw ProcessLog and
HTTP body may contain setup credentials: do not persist them. This status-payload
alternative is deliberate. Request the owning shared diagnostic workflow for
further investigation with its redaction/retention controls. Raw log text must
never be passed through as if safe merely because it is called a log.

Pending polls exit 3; terminal failed/warning outcomes exit 4; other blocked
operations exit 2. Authentication/privilege, HTTP, transport, input and local
persistence errors retain distinct categories. A failed receipt update retains
the known ProcessId in the returned diagnostic; failed diagnostic persistence
adds an errors entry without hiding the original failure. No automatic POST retry is attempted. Read-only 401/403 recovery may request
one fresh core login before repeating the same read.
