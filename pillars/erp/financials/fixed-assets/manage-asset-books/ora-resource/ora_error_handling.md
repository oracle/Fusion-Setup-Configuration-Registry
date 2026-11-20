# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Fresh FSM export or structural metadata is unavailable or contradictory | Stop package generation and obtain a fresh structural contract. |
| Fusion returns `FA_BOOKCTL_INCORRECT_BOOK_NAME` | Correct the Book Name or Asset Book Code, refresh target state, then present the corrected package for approval. |
| Fusion returns `FA_BOOKCTL_INV_FISCALYR` | Preserve the ProcessLog and treat this as an unresolved Asset Books fiscal-year reference/contract failure. Reverify that the exact selected Fiscal Year belongs to the selected Depreciation Calendar and contains the approved current period. Do not retry by blanking Fiscal Year, substituting another same-date fiscal year, or resubmitting the same ZIP. Prepare a new package only after the reference or contract evidence changes and the normal preview and approval gates are repeated. |
| Final ZIP validation finds a missing, blank, duplicated, or invalid defaulted field, or an unresolved Associated Corporate Book | Block the package. Reapply the authoritative rule in ora_defaulting_rules.md, rebuild the affected `asset book data file` row, and rerun final ZIP validation before approval. |
| Import execution fails or is uncertain | Do not retry automatically. Rediscover target state, retain safe diagnostics, and require a new reviewed plan and approval before retrying. |
| Submission is accepted but terminal status, ProcessLog, or fresh Asset Books read-back is unavailable | Report `accepted — pending parent verification`; do not claim completion or start dependent work. |
| Credentials, tokens, headers, or secrets appear in evidence | Do not persist or disclose them. Stop and use the approved authentication route. |

## DFF Failures

Identify whether a failure belongs to FA_BOOK_CONTROLS or JGxFABookControls.
Report regional definition/applicability gaps as unverified evidence;
never resolve them by blanking regional values, copying ordinary values,
selecting another context, or assuming the regional flexfield is optional.

For missing required DFF input, report the affected book, segment Prompt,
SegmentCode, ColumnName, context, and ValueSetCode when present. Recover
existing supplied input first, then request only unresolved business values.
Stop before Design Preview or package generation.

For absent, failed, incomplete, or wrong-environment/batch definition evidence,
retain safe export diagnostics and report the dependency as unverified.
Never interpret an export failure as an empty required-segment definition.

For invalid context, ambiguous mapping, invalid value, or final-artifact
mismatch, identify the affected book and field and stop. Do not remove
required values, substitute another context, or bypass the normal approval gates.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FA_BOOK.DESIGN_APPROVAL_GATE | decision | 7 | execution_gate | approved->FA_BOOK.PACKAGE_PREPARED;approval_missing->FA_BOOK.RETURN_ISSUES | FA_BOOK.DESIGN_ENFORCED | stop | The complete business Design Preview requires approval before ZIP creation. |
| FA_BOOK.IMPORT_GATE | decision | 10 | execution_gate | ready->FA_BOOK.VALIDATED;incomplete->FA_BOOK.RETURN_ISSUES | FA_BOOK.FINAL_ZIP_VALIDATED | stop | Require applicable read-only task validation and immutable-artifact checks for the exact target and requested scope. Return ready without requiring upload approval or a submission receipt: core.data-loader obtains submission approval after task validation. This node does not submit, poll, or report acceptance. Missing, stale, or mismatched validation/artifact evidence returns incomplete. |
| FA_BOOK.VALIDATED | terminal | 110 | terminal | none | FA_BOOK.IMPORT_GATE | stop | Return validated_for_import for the current validation scope; no upload approval, submission, acceptance, or Fusion completion is implied. The parent/Core workflow may report accepted only after its accepted-initiation response supplies a request ID correlated to the exact target and reviewed immutable archive/hash. Parent verification remains required. |
| FA_BOOK.EXISTS_IDENTICAL | terminal | 120 | terminal | none | FA_BOOK.EXISTENCE_CHECKED | continue | An existing book exactly matches the requested definition. |
| FA_BOOK.EXISTS_DIFFERENT | terminal | 130 | terminal | none | FA_BOOK.EXISTENCE_CHECKED | continue | An existing book differs from the requested definition. |
| FA_BOOK.RETURN_ISSUES | terminal | 140 | terminal | none | none | continue | Input, dependency, contract, design, artifact, approval, or verification readiness is blocked. |
