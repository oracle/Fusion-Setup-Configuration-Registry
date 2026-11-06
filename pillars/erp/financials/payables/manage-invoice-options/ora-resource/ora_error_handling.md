# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Exact task package, template header, or node path does not match | Stop; rebuild the candidate from the exact task template and create a new immutable preview. |
| The FSM import hook cannot resolve a business-unit or payment-term source value | Preserve the exact dependency diagnostic, correct the named source field, and create a new immutable preview. Do not directly populate the resolved ID. |
| Fusion rejects an approved package | Preserve the process identity and diagnostics, refresh the same-task export, and stop before retry. |
| Candidate input or package changes after preview | Treat the approval as stale; revalidate and obtain a new candidate-bound approval through core.data-loader. |
| The supplied BuName has zero or multiple preflight matches, or a create row has no unambiguous EnterpriseId | Stop before package approval and preserve the diagnostic. Ask the requester which EnterpriseId to use for the blank create rows; do not create a business unit, guess an EnterpriseId, or substitute an OrgId. |
| A create target is already present in the fresh current export | Stop before package approval; require an explicit update request instead of resubmitting a duplicate row. |
| A submitted immutable system lookup code is outside the task-owned allowlist | Stop before package preview and return the named field with its allowed codes. |
| A readable payment-term or currency lookup returns zero records | Stop before candidate generation or preview and ask for a valid payment-term name or currency code. Do not downgrade a readable zero-result to an advisory. |
| An observed payment-term page contains a valid matching term, including repeated rows | Stop after that page; do not fetch later pages to prove uniqueness. Keep observed-page identity diagnostics, record uniquenessVerified=false, preserve the submitted name, and never serialize a returned ID. FSM performs final resolution. |
| A payment-term lookup returns different IDs, incomplete or inconsistent identity, or its endpoint is unavailable | Preserve the submitted name with a disclosed advisory receipt. A separately approved FSM import performs the final context-aware validation. |
| A currency lookup returns multiple records or its endpoint is unavailable | Preserve the submitted currency code with a disclosed advisory receipt; Fusion validates it during the separately approved import. Payment-term duplicate-ID handling does not change currency lookup policy. |
| A batch contains multiple independently invalid records | Validate every record, return one aggregated row-by-row diagnostic, and create no candidate ZIP. Resolve every blocking error before a new validation run. |
| A user uploads a structurally valid FSM ZIP with valid and invalid rows | Read the ZIP against a fresh baseline, classify existing keys as updates and absent keys as creates, validate every row, and return valid/invalid row results. Never import automatically; reject the whole upload when any blocking row error exists. |
| A customer-configured lookup code is invalid | Preserve the submitted CSV value and return Fusion's import diagnostic after the governed import. Do not invent a replacement code or retry automatically. |
| A read-only API preflight returns HTTP 400 | Preserve the submitted value. Record `validation_skipped` and a structured `resolver_contract_issue` with endpoint, supplied value, query fingerprint, sanitized diagnostic, timestamp, owner, and required maintenance action. The governed FSM import remains authoritative. A create-time BU/ledger derivation may still need a readable result because it supplies required create context. |

Account validation failures (invalid combination, missing existing CCID, SOAP
fault, timeout or unavailable endpoint) block candidate generation. Never keep a
previous successful receipt after a failed new lookup, retry an import, create a
combination or treat this check as an advisory lookup. Bind each receipt to its
operation, BU, ledger, ordered segments and baseline digest.

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Blocked | Missing exact package evidence or unresolved resolver contract | Collect the missing package or validation input, or retain static-only readiness. |
| Execution blocked | Immutable preview or explicit approval is absent | Complete the central preview and approval workflow. |
| Failed | A controlled import returns an error | Preserve the attempt and diagnose without automatic resubmission. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before any candidate import | Exact task, target scope, immutable preview identity, known blockers, and required approval boundary |
| On failure | Failure class, sanitized diagnostics reference, and safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Unresolved term resolver or package contract | Do not invent a public endpoint, choose a default term, or directly write to Fusion. |
| Failed or uncertain import | Do not retry, overwrite, or submit another package automatically. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INVOICE.EXECUTION_GATE | step | 60 | execution_gate | approved_preview->SUCCESS.DONE;not_ready->INVOICE.EXECUTION_BLOCKED | DESIGN.ENFORCE | stop | A governed execution request exists |
| ERROR.BLOCK | terminal | 70 | terminal | none | none | stop | A blocking rule is reached |
| INVOICE.EXECUTION_BLOCKED | terminal | 75 | terminal | none | none | stop | Execution approval or preview is absent |
| SUCCESS.DONE | terminal | 80 | terminal | none | INVOICE.EXECUTION_GATE | stop | A governed immutable preview and approval are available |

## Interest Account Completion

For requested enabled-interest accounts, run the narrow `verify-interest` follow-up defined in SKILL.md. Report account verification PASS, FAIL or PENDING separately from FSM import completion. A blank/different account must not produce configuration success; unrelated differences are outside this check.

## Saved Build Results Do Not Match an Upload

On `UPLOAD_CONTEXT_MISMATCH`, stop before import. Use the saved JSON report for
this exact task, ZIP, and fresh baseline, or repeat preparation to obtain new
results. Do not change hashes or relabel receipts to make old results pass.
For an account validation failure, keep all BU, ledger, segment, baseline,
existing-CCID, and DynamicInsertion=No checks in place.

## Post-Import Readback Evidence

A matching account in a ZIP is not proof that it was saved in Fusion. Before
`verify-interest` may return `PASS`, the routed workflow must record the actual
successful Data Loader result and a later completed Task Level Export. This
observation is local workflow evidence, not an authorization to call either
service or a substitute for their returned results. Never hand-write success
values or infer them from the candidate. If the required facts are unavailable,
keep verification `PENDING`.

The offline verifier accepts `--verification-evidence` with schema version
`invoice-options-interest-readback-v1`. Supply the selected environment, HTTPS
origin and completed import request independently through `--environment`,
`--base-url` and `--import-request-id`; take these from the active workflow.
Record these fields from the governed calls:

| Observation | Required fields |
|---|---|
| `importObservation` | `source=core.data-loader`; exact `environment`, `baseUrl`, `taskCode`, `requestId`, returned `ucmContentId`; normalized successful `status=SUCCEEDED`; positive integer `loadedObjects` and `failedObjects=0`; `candidateSha256`, `baselineSha256`, `blueprintSha256`; `completedAt`, `observedAt` |
| `exportObservation` | `source=shared.setup-export.task-level-export`; exact `environment`, `baseUrl`, `taskCode`; returned `processId` and ESS `requestId`; normalized completed `status=COMPLETED` and `processCompletedFlag=true`; downloaded ZIP `artifactSha256`; `startedAt`, `completedAt`, `observedAt` |

Hashes must describe the exact files used for this import and verification.
The export ESS request ID must match the ZIP metadata. The export API process
ID and ESS request ID are different identities; retain both. All package
`ProcessEnv` values must match the selected environment. Use timestamps with
explicit timezones from the observed workflow/server facts; do not guess a
server timezone or replace an old export's time with the current time.

Import completion must precede export start. Import observation must occur
between that completion and export start. Export completion and observation
must follow its start; a timestamp more than one minute in the future is
invalid. These checks bind freshness to this particular import, rather than
an arbitrary file-age cutoff. The baseline and submitted candidate, including
renamed copies, cannot serve as readback proof. Wrong environment/task/request,
changed files, incomplete results, stale or malformed observations all leave
verification `PENDING`. A validly observed export with a missing or different
requested account remains `FAIL`.

The observation file is evidence produced by the governed workflow, not a
cryptographic attestation. Preserve its original service results in that
workflow's evidence store; an arbitrary caller-created JSON file is not
independently authenticated by this offline command. This command never
contacts Fusion or repeats an import.

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
