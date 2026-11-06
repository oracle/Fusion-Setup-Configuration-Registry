# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| A resolver contract issue is recorded | Preserve the customer candidate and record the structured finding in preview and candidate evidence. Review and fix or reverify it during implementation review. |
| Payables Calendar Types REST returns HTTP 400 | Preserve the requested Calendar and record `validation_skipped` plus a structured `resolver_contract_issue` containing endpoint, supplied value, HTTP status, query fingerprint, sanitized diagnostic, timestamp, owner, and required action. It is not proof that the Calendar is invalid. Allow only separately approved FSM import; review and fix or reverify the issue during implementation review. |
| Supporting read-only GET is unavailable | Record `validation_skipped` with HTTP 401/403, TLS, network, timeout, rate-limit, or 5xx errors; endpoint; supplied value; and timestamp. For an explicit Set Code or Calendar, keep the supplied value and continue to package generation and, if approved, the governed FSM import. For a Set Name or unspecified set that still needs a Set Code, record the lookup failure, stop preparation, and ask for the actual Set Code; do not treat that required lookup as skipped. Malformed payloads and unexpected HTTP responses instead block as `resolver_failure`. |
| Package hierarchy or validation evidence changes | Re-run validation and evidence preparation; do not retry a load automatically |
| A new header has no matching installment, or Fusion returns `AP_AT_LEAST_ONE_CHILD` | Stop before preview/ZIP generation and ask for at least one installment for that new term. Enabled and disabled creates both require it; assignments and translations do not count. Never invent an installment or automatically retry the failed import. This rule does not require adding a line for an existing-parent change. |
| A child create or update lacks its parent, or validation reports `MISSING_PARENT`, `MISSING_PARENT_BASELINE`, or `PARENT_ROW_CHANGED` | Stop before import. Include the matching unchanged fresh-baseline `AP_TERM_HEADER` with audit fields blank, unless an explicit header operation supplies it. Do not invent a missing baseline parent. Revalidate and prepare a new preview. |
| A child-only Payment Terms archive succeeds but the requested line, subscription, or translation is absent from a fresh export | Treat the requested change as skipped, not successful. Preserve the import and export evidence; rebuild a new archive containing the matching `AP_TERM_HEADER` row and obtain a new preview and approval. |
| CSV parser reports a header or row-width error | Stop the load; rebuild from the exact template headers with full-width rows, then create a new preview and approval |
| A due basis, due-date method, percentage total, amount-zero, numeric-range, discount-completeness, or discount-order rule fails | Stop before ZIP generation; identify the operation and exact fields, request corrected values, and require a new preview. Do not silently add an installment, change a due basis, clamp a negative value, or reorder discounts. |
| A date or Rank rule fails | Stop before ZIP generation; identify the exact header and field. Do not repair a malformed date, reorder active dates, renumber Rank, or scope duplicate-Rank comparison by Set Code. |
| Payment-term Type is not `STD` | Stop before ZIP generation; identify the header and require `Type=STD`. Do not preserve or substitute another explicit type value. |
| A readable lookup returns zero rows | Stop as `not_found` before ZIP/import and retain the supplied Calendar or SetCode in the failure evidence. Do not substitute a returned row or proceed to import. |
| A lookup response is malformed or otherwise unexpected | Stop as `resolver_failure`; retain a sanitized diagnostic and do not generate or import a candidate. |
| Preview or import reports an error, or its outcome is uncertain | Preserve sanitized diagnostics and the immutable candidate identity. Do not retry or resubmit automatically; reconcile the original attempt through the central workflow. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input blocked | Package structure, CSV shape, dates, Rank, due terms, or discount rules are invalid | Correct the reported values or package structure and create a new preview. |
| Resolver blocked | A required Calendar or Set Code lookup returns no result or an invalid response | Correct the submitted value or resolver issue before package generation. |
| Execution blocked | Immutable preview or explicit approval is absent | Complete the central preview and approval workflow. |
| Failed | A controlled import returns an error or has an uncertain outcome | Preserve the original attempt and reconcile it without automatic resubmission. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before any candidate import | Exact task, target scope, immutable preview identity, known blockers, and required approval boundary |
| On failure | Failure class, sanitized diagnostics reference, and safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Incomplete resolver | Do not invent values, a writable operation, or an import rule |
| Failed or uncertain import | Do not automatically retry or resubmit. |

## Set Lookup Problems

- No match: stop and ask for a valid code or name. Keep the user's original value.
- More than one code: show the codes and names, then ask the user to choose.
- Access failure with an explicit code: keep that code and show that its check was skipped.
- Access failure with a name or unspecified set: stop and ask for the Set Code.
- Code and name disagree: stop and ask which set the user meant.

Do not silently change a code or choose a different set. See
[Reference Lookups](ora_reference_lookups.md) for the input and lookup contract.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PAYTERM.EXECUTION_GATE | step | 65 | execution_gate | approved_preview->SUCCESS.DONE;not_ready->PAYTERM.EXECUTION_BLOCKED | DESIGN.ENFORCE | stop | A governed execution request exists |
| ERROR.BLOCK | terminal | 70 | terminal | none | none | stop | A documented blocker is reached |
| PAYTERM.EXECUTION_BLOCKED | terminal | 75 | terminal | none | none | stop | Execution approval or preview is absent |
| SUCCESS.DONE | terminal | 80 | terminal | none | PAYTERM.EXECUTION_GATE | stop | A governed immutable preview and approval are available |

## Installment Requirement

A new payment term must include at least one valid installment, even when the
payment term is disabled. Set assignments and translations do not count as
installments. If no installment is supplied, stop before generating the import
ZIP and ask the user to provide one. Fusion reports `AP_AT_LEAST_ONE_CHILD`
when a new payment term has no installments.

For an existing payment term, adding a set assignment does not require adding
an installment. Include its matching header as described in the supporting
parent rules.

## Reconciliation Evidence

A ZIP with matching values does not prove that Fusion saved those values.
Before reporting reconciliation `PASS`, record the actual successful Data Loader
result and a completed Task Level Export started after that import. Use the
selected workflow's target environment, HTTPS origin and import request as the
independent context. Do not infer these facts from CSV contents or hand-write
successful observations. Keep the original service results beside this evidence
in the project workspace.

Pass `--verification-evidence` with `schemaVersion=fsm-post-import-readback-v1`
and these two observation objects:

| Object | Required fields |
|---|---|
| `importObservation` | `source=core.data-loader`, `status=SUCCEEDED`, exact `environment`, `baseUrl`, `taskCode`, `requestId`, returned `ucmContentId`, positive integer `loadedObjects`, `failedObjects=0`, exact `candidateSha256`, `baselineSha256`, `blueprintSha256`, `requirementsSha256`, and timezone-qualified `completedAt`, `observedAt` |
| `exportObservation` | `source=shared.setup-export.task-level-export`, `status=COMPLETED`, `processCompletedFlag=true`, exact `environment`, `baseUrl`, `taskCode`, returned `processId`, ESS `requestId`, downloaded ZIP `artifactSha256`, and timezone-qualified `startedAt`, `completedAt`, `observedAt` |

Use real workflow/service observations with explicit timezones; do not guess the
server timezone. The import request must match `--import-request-id`. The export
ESS request must match ZIP metadata; the export API process ID is a separate
identity and must also be retained. Package environments and every file digest
must match the selected target and exact files. Import completion and its
observation must precede export start; export completion and observation must
follow. Future, stale, missing or malformed observations, incomplete jobs,
foreign environments, changed files, and the candidate or baseline reused as
proof leave verification `PENDING`. A properly observed export that differs
from the requested result is `FAIL`.

Use `--compare-only` for a local comparison without these observations. It returns
`MATCH` or `DIFFERENT` and `persistenceVerification=NOT_PERFORMED`; neither result
claims that Fusion saved data. The offline command trusts evidence collected by
the governed workflow; it does not authenticate arbitrary caller-written JSON,
contact Fusion, authorize an import, or retry one.
