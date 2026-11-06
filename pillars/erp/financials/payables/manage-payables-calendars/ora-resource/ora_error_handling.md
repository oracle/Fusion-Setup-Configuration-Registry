# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Package, parent-child, or semantic gate fails | Stop before candidate preparation and state the exact missing package fact or documented contract |
| Preview or import reports an error | Preserve sanitized diagnostics and the immutable candidate identity; do not retry automatically |
| Outcome is uncertain | Do not resubmit; reconcile the original attempt through the central workflow |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input blocked | Exact package structure or parent-child linkage is invalid | Correct the package or linkage and revalidate |
| Design blocked | Field lifecycle semantics or governed execution evidence is missing | Obtain the documented evidence or approval boundary before preview |
| Execution blocked | Immutable preview or explicit approval is absent | Complete the central preview and approval workflow |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before any candidate import | Exact task, target scope, immutable preview identity, known blockers, and required approval boundary |
| On failure | Failure class, sanitized diagnostics reference, and safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing field semantics | Do not infer required values, defaults, field types, allowable values, updateability, resolver behavior, or direct-write endpoints |
| Failed or uncertain import | Do not automatically retry or resubmit |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CALENDAR.EXECUTION_GATE | decision | 30 | execution_gate | approved_preview->CALENDAR.READY_FOR_DATA_LOADER;not_ready->CALENDAR.EXECUTION_BLOCKED | CALENDAR.ENFORCE_DESIGN | stop | A governed execution request exists |
| CALENDAR.INPUT_BLOCKED | terminal | 40 | terminal | none | none | stop | Package or parent-child validation fails |
| CALENDAR.DESIGN_BLOCKED | terminal | 50 | terminal | none | none | stop | A package or semantic evidence blocker is reached |
| CALENDAR.READY_FOR_DATA_LOADER | terminal | 60 | terminal | none | CALENDAR.EXECUTION_GATE | stop | A governed immutable preview and explicit approval are available |
| CALENDAR.EXECUTION_BLOCKED | terminal | 70 | terminal | none | none | stop | Execution approval or preview is absent |

## Supporting Parent Failures

Stop before import on `MISSING_PARENT`, `MISSING_PARENT_BASELINE`, or
`PARENT_ROW_CHANGED`, or `AUDIT_FIELD_POPULATED`. For an existing calendar,
rebuild from its fresh baseline header and apply only any header changes the
user requested. For a new calendar, require an explicit calendar create with
its required values. Do not invent a parent. Leave audit fields blank.
Revalidate the new candidate and follow the normal preview and approval workflow. For Calendars, reject child-only uploaded ZIPs even
when the parent exists in the baseline; validation does not modify uploads.

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
