# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Input, dependency, or design gate fails | Stop before candidate generation or import, retain the missing requirement, and request the exact correction or evidence |
| Preview or import reports an error | Preserve sanitized diagnostics and the immutable candidate identity; do not retry automatically |
| Outcome is uncertain | Do not resubmit; reconcile the original attempt through the central workflow |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input blocked | Required package, scope, or field evidence is absent or invalid | Correct the request or evidence and revalidate |
| Dependency blocked | A prerequisite is unresolved | Resolve the documented prerequisite before preview |
| Design blocked | A safety or governance rule fails | Correct the design contract before preview |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before any candidate import | Exact task, target scope, immutable preview identity, blockers, and required approval boundary |
| On failure | Failure class, sanitized diagnostics reference, and safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing field semantics | Do not infer a value, default, reference lookup, lifecycle operation, or direct-write endpoint |
| Failed or uncertain import | Do not automatically retry or resubmit |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PAYOPT.EXECUTION_GATE | step | 40 | execution_gate | approved_preview->PAYOPT.READY_FOR_DATA_LOADER;not_ready->PAYOPT.EXECUTION_BLOCKED | PAYOPT.ENFORCE_DESIGN | stop | A governed execution request exists |
| PAYOPT.INPUT_BLOCKED | terminal | 50 | terminal | none | none | stop | Input validation fails |
| PAYOPT.DEPENDENCY_BLOCKED | terminal | 60 | terminal | none | none | stop | Dependency readiness fails |
| PAYOPT.DESIGN_BLOCKED | terminal | 70 | terminal | none | none | stop | Design enforcement fails |
| PAYOPT.EXECUTION_BLOCKED | terminal | 80 | terminal | none | none | stop | Execution approval or preview is absent |
| PAYOPT.READY_FOR_DATA_LOADER | terminal | 90 | terminal | none | none | stop | A governed immutable preview and approval are available |

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
