# Manage System Controls: Error Handling

## Failure Classes

| Failure class | Safe next action |
|---|---|
| Input validation | Return to [ora_input_validation.md](ora_input_validation.md), identify every missing or invalid business value together, and revalidate. |
| Lookup evidence | Return to [ora_reference_lookups.md](ora_reference_lookups.md), retain sanitized diagnostics, and stop until complete target evidence is available. |
| Dependency | Return to [ora_dependency_readiness.md](ora_dependency_readiness.md) and resolve the blocking prerequisite. |
| Design enforcement | Return to [ora_design_enforcement.md](ora_design_enforcement.md) and correct the rejected design or obtain the required decision. |
| Approval | Keep the immutable archive in review state until explicit approval is received. |
| Import process | Report the task, target, process or request ID, last status, elapsed time, and safe next-check path. |
| Post-execution verification | The Fixed Assets parent applies the System Controls verification criteria in [ora_reference_lookups.md](ora_reference_lookups.md), retains terminal process evidence, and blocks completion and downstream handoff until fresh target evidence is available. |

## Disclosure Rules

| Situation | What must be shown |
|---|---|
| Pre-import block | Failure class, concise business explanation, owner resource, and next safe action. |
| Import result | Archive identity, target, process or request ID, terminal status, and created, skipped, warned, or failed counts when available. |

## Refusal Rules

| Situation | What must not happen |
|---|---|
| Unresolved validation, lookup, dependency, or design rule | Do not prepare or submit an import. |
| Missing approval | Do not submit a live import. |
| Existing System Controls row | Do not create, update, or prepare a ZIP. Show the existing definition as read-only. It is immutable; never propose or perform a structure-reference update for a KFF replacement or migration. |
| Failed, pending, or timed-out import | Do not alter defaults by trial and error or automatically resubmit. |
| Successful loader or FSM status without fresh System Controls read-back | Do not claim completion. |
## Approved Import Handoff

After an approved immutable FSM package is accepted, report it as `accepted — pending parent verification`. The Fixed Assets parent retains the request context and invokes `core.data-loader` for routed status and FSM ProcessLog retrieval. The parent then applies the System Controls target-state verification criteria in [ora_reference_lookups.md](ora_reference_lookups.md). This task does not poll or claim completion. The workflow must pause for a terminal failure, unresolved status conflict, missing required input, absent fresh target evidence, or a separate approval for a new state-changing operation. A dependent task may reuse only parent-verified System Controls context.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SYS.DONE_READ_ONLY | terminal | 36 | terminal | none | SYS.LOOKUP_EXISTING | continue | One exact Enterprise Name row already exists |
| SYS.IMPORT_GATE | decision | 60 | execution_gate | approved->SYS.DONE_READY;blocked->SYS.HANDLE_APPROVAL | SYS.ENFORCE_DESIGN | stop | A reviewed package is proposed for import |
| SYS.HANDLE_INPUT | step | 70 | error_handler | handled->SYS.ISSUES | SYS.VALIDATE_INPUT | stop | Identity or creation input is invalid |
| SYS.HANDLE_DEPENDENCY | step | 80 | error_handler | handled->SYS.ISSUES | SYS.RESOLVE_DEPENDENCIES | stop | A prerequisite is unresolved |
| SYS.HANDLE_LOOKUP | step | 90 | error_handler | handled->SYS.ISSUES | SYS.LOOKUP_EXISTING | stop | Lookup evidence is missing or ambiguous |
| SYS.HANDLE_DESIGN | step | 100 | error_handler | handled->SYS.ISSUES | SYS.ENFORCE_DESIGN | stop | A design rule blocks the request |
| SYS.HANDLE_APPROVAL | step | 110 | error_handler | handled->SYS.ISSUES | SYS.IMPORT_GATE | stop | Import approval is missing |
| SYS.DONE_READY | terminal | 120 | terminal | none | SYS.IMPORT_GATE | continue | Package is ready for approved import |
| SYS.ISSUES | terminal | 130 | terminal | none | none | continue | Any validation, lookup, dependency, design, or approval issue |
