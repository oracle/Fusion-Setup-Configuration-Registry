# Manage Receivables System Options Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required field or conditional set is incomplete | Stop before preview and report the missing business inputs in implementation language; include technical package fields only as supporting diagnostics |
| Source-backed string maximum is exceeded | Stop before candidate ZIP generation. Report the exact entity and field, actual length, allowed maximum, and character unit; ask for a shorter business value and require a new immutable preview. Never silently truncate or rewrite the supplied value |
| Public preflight resolver returns zero or multiple rows | Classify as an invalid dependency for the affected field, record the input and cardinality, and do not choose a candidate or continue that row |
| Confirmed FSM import alternate-key resolver returns null | Record the field-specific dependency token, emit recoverable `AR:::AR_ATTR_NOT_EXISTS_TARGET_INS` with `ATTRIBUTE_NAME_LIST` and alternate-key values, remove the invalid `AR_SYSTEM_OPTIONS` XML element, and stop that row |
| Confirmed accounting-flexfield prompt validation returns no row | Surface `AiAcctFlexKeyLeftPrompt <value> does not exist`, apply the common recoverable invalid-dependency error and XML-element removal behavior, and stop that row |
| Optional public preflight path is unavailable for a Confirmed FSM import-only resolver | Continue static planning without public preflight; do not call internal components directly, and require complete inputs/context before immutable Data Loader preview and approval, then confirm field-scoped resolution or validation from FSM import and reconciliation |
| Account combination cannot be resolved or validated | Stop the row and report the concatenated segments and ledger/chart-of-accounts context without exposing sensitive physical IDs |
| Existing-row or irreversible rule conflicts | Show the requested-versus-existing difference and require a revised design decision; do not force the change |
| Package/process validation fails | Preserve redacted logs, archive fingerprint, task/process identifiers, and partial results; do not rebuild from current-data values blindly |
| Preview changes after approval | Invalidate approval and produce a new immutable preview |
| Submission result is uncertain | Do not resubmit; reconcile read-only task/process state first |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Required group, supported header, flag, or conditional set fails | Correct exact input |
| Dependency not ready | BU, ledger, set, rule, method, source, type, activity, organization, account, or prompt is missing/ambiguous | Correct reference data or input |
| Technical lookup gap | The applicable resolver contract is Partial, To collect, unsupported, or `TBD` | Handle the authoring gap internally. Ask the implementation user only for a bounded business decision or supported value; when eligible, offer the explicit nonproduction runtime-validation override. Never request authoring workbooks, source evidence, or CSV encodings |
| Public preflight limitation | A complete Confirmed FSM import resolution/validation contract exists but no supported public GET exists | Record the limitation and defer only the affected field's final check to FSM import after immutable Data Loader preview and approval; confirm the result during reconciliation |
| Business decision | Existing setup differs, irreversible behavior applies, or broad side effect requires owner choice | Present a field-level and affected-scope preview |
| Unsupported semantics | Behavioral meaning is not backed by a confirmed source | Ask one bounded business-language clarification or remove the field. A structurally valid value may proceed only with an eligible explicit nonproduction runtime-validation override, immutable preview, and separate approval |
| Package contract gap | Metadata, object identity, headers, release, successful status, or fingerprint is stale/missing | Refresh same-task evidence |
| Auth or authorization | Approved read/export/import privilege unavailable | Refresh approved authentication once for an idempotent read, then stop |
| Transport or environment | Network/service failure occurs before side effect | Retry only bounded idempotent reads |
| Fusion process failed | Export/import child process fails | Preserve redacted status/logs; do not replay automatically |
| Process timeout | Process remains nonterminal beyond bounded wait | Do not resubmit; provide exact next-check path |
| Verification mismatch | Successful process does not reconcile to approved natural-key/field expectations | Show the exact semantic diff and stop |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Static readiness | Task code/name, target/release, package identity, resolver classifications, retained public-preflight limitations, open semantic evidence, and no-live-execution status |
| Preview | Business unit, ledger/currency, every changed package field, reference receipts, defaults, irreversible/cross-row effects, unrelated-row preservation, and package fingerprint |
| Approval | Exact immutable preview fingerprint and the literal approval required by the active Data Loader contract |
| Failure | Failure class, target, task/process stage, affected row/field, redacted evidence, partial successes, and recommended action |
| Verification | Terminal process state, exact business-unit natural key, requested-versus-observed field diff, side-effect reconciliation, and zero unrelated mutations |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| No supported public preflight path | Do not invoke internal ADF paths, invent REST URLs, or substitute an unrelated service; use only a complete Confirmed FSM import contract through the separately governed Data Loader path |
| Current-data export is classified | Do not expose or embed environment values in examples, fixtures, documentation, or source control |
| Missing semantic evidence | Do not infer behavior from field names, current values, UI order, or database comments alone. Do not expose or request developer authoring artifacts; ask a bounded business question or use only the documented eligible nonproduction runtime-validation override |
| Developer-only authoring artifacts | Do not ask an implementation user for the Attributes Workbook, Source Register, CodeSearch evidence, source code, or internal CSV encodings |
| Uncertain or changed preview | Do not approve, submit, or retry until a new immutable preview is reviewed |
| Direct resource execution | Do not write Fusion setup from this resource layer; route the package through `core.data-loader` in FSM mode |
| Repository delivery | Do not commit, push, merge, or overwrite another task without separate authorization |

## BU Lookup Diagnostics

For an empty finBusinessUnitsLOV result, report the exact target, query, account context when known, and returned count. Do not diagnose missing BU data access solely from zero rows. Distinguish identity not resolved, inactive identity, function mismatch, ledger mismatch, duplicate create, missing update, authentication failure and incomplete export. Preserve the evidence and stop before candidate submission; do not use an assisted override as the normal resolver fix.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RSO.EXECUTION_GATE | decision | 60 | execution_gate | ready->RSO.DONE;blocked->RSO.HANDLE_ERROR | RSO.ENFORCE_DESIGN | stop | Immutable Data Loader preview exists and all static/runtime blockers are resolved |
| RSO.HANDLE_ERROR | step | 70 | error_handler | handled->RSO.RETURN_ISSUES | none | stop | Any validation, lookup, dependency, default, design, preview, or process failure |
| RSO.RETURN_ISSUES | terminal | 80 | terminal | none | none | stop | A blocking issue was classified and disclosed |
| RSO.DONE | terminal | 90 | terminal | none | RSO.EXECUTION_GATE | stop | All resource checks passed and the package is ready for separately approved Data Loader execution |
