# Diagnostic handling contract

This is the task's handling policy for Meals policy/rate batches. It does not
assert a complete Oracle error catalog, reinterpret severity, or enable an
unresolved operation. Use the owning core workflow's result and presentation
contracts; do not replace Data Loader responses with a task-specific envelope.

## Before submission

Input shape/type problems are input validation failures. Report the worksheet,
row and field with the corrective action; generate no executable candidate.
For batches retain the affected policy association, full rate-key field names,
and workbook sheet/cell or row identity in safe diagnostics. Redact sensitive
values. An invalid row blocks the entire local candidate; it must not produce
a partial import package or imply Fusion transaction-wide atomicity.
Task, schema, reference-evidence or baseline identity mismatches are catalog
mismatches. Missing operation/resolver contracts are authoring blockers, not
evidence that Oracle rejects that operation. Preserve the exact failed node,
entity and unresolved field and direct the developer to its owning contract.

Missing contextual approval is an approval blocker. Changed candidate bytes or
inputs require the owning workflow's new preview/approval sequence. A reference
transport/authentication failure is unavailable evidence, not an invalid business
value. Keep the originating failure class and use only its declared recovery.

## Product diagnostics

Preserve the actual message, returned severity and available row/field identity.
State that its task-specific cause/remedy is unresolved until supported by the
diagnostic or reviewed source. Do not infer success from process counters,
invent a translation or propose an automatic fix. Role/geography inputs are
unsupported and must be rejected before candidate generation; an unexpected
target reference error does not authorize adding a new lookup route.

## After submission

Use core.data-loader's supported status/error route with the existing request
identity. Retrieve its required FSM ProcessLog when available; preserve the
central workflow's diagnostics and failure result. Distinguish request acceptance,
terminal processing status and reconciled business outcome. Retain partial
successes and an errors collection in the owning durable evidence when that
workflow prescribes it. Do not fabricate unavailable logs or zero error counts.

For a timeout, retain environment, task, process/request identity, last known
status and elapsed wait; stop at the owning workflow's retry/check gate. Do not
create a replacement process or submit the package again to obtain a status.
For failure, do not assume transaction-wide rollback: reconcile the requested
rows, their context/audits and non-target baseline rows before presenting a
completion or retry decision. Reconciliation failure or missing evidence remains
an unresolved outcome regardless of a successful import status.
Reconcile each requested policy and full rate key, including retained sibling
rates and unrelated rows. Preserve per-row successes and errors; do not label
a partially successful batch as complete or resubmit successful rows automatically.

A correction, replay, cleanup or rollback is a separate action and must follow
its owning workflow and contextual approval. No automatic deletion, replacement,
new null marker, alternative lookup or package modification is authorized by
this handling policy. Preserve original candidate and raw evidence; never rewrite
a mismatch as a pass through normalization.

## Authority

Repository AGENTS.md error handling and project workflow rules govern failure
classification, diagnostics and mutation gates. core/data-loader/SKILL.md owns
native status/error retrieval and user-facing reports. Unknown
product messages remain explicitly unresolved rather than blocking the definition
of how to handle them safely.
