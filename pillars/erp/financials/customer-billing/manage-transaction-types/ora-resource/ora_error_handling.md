# Manage Transaction Types Error Handling


## Error Situations

| Situation | What Should Happen |
|---|---|
| Package identity, member set, header order, metadata, row width, or release pair is invalid | Stop before Data Loader and show the exact structural mismatch |
| A fixed domain, Boolean, date, key, or relationship check fails | Show the entity, field, rejected value category, supporting rule, and safe correction |
| A source-proven FSM resolver returns no match or ambiguity | Surface the resolver failure; do not substitute another set, reference, business unit, ledger, or transaction type |
| A Partial environment choice is requested | Stop and request exact environment verification; do not infer a code from a label |
| Account-combination validation is requested | Stop unless the explicit nonproduction validation gate is open; disclose that the FSM path may create a valid combination |
| Data Loader or Fusion returns an error or uncertain status | Preserve the exact attempt identity, make no automatic retry, and require a fresh preview and approval after correction |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| INVALID_INPUT | Local source-backed validation failed | Correct input and rebuild the candidate |
| EVIDENCE_UNRESOLVED | A Partial resolver or unsupported operation was requested | Collect the named evidence or omit the optional behavior |
| PACKAGE_INVALID | ZIP, CSV, metadata, or row-width contract failed | Rebuild from the exact fresh template/current pair |
| FSM_REJECTED | The governed FSM import resolver or validator rejected a row | Preserve diagnostics; correct once; generate a new preview |
| ATTEMPT_UNCERTAIN | Status retrieval timed out or authentication expired after submission | Reauthenticate once when allowed and resume the same attempt; never resubmit automatically |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Static candidate review | Exact task, operation, entity keys, preserved rows/values, explicit defaults, blockers, and candidate SHA-256 |
| Data Loader approval | Immutable artifact identity, environment, business effect, Task Hook result, and the exact candidate-specific approval boundary |
| Post-submission | UCM/content identity, Fusion request/process identity, terminal result, diagnostics, persisted-state result, and Run Book synchronization separately |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| A direct FSM or REST write is requested from this task skill | Do not bypass core.data-loader |
| Inputs changed after preview or approval | Do not reuse approval; rebuild and revalidate |
| A failed or uncertain submission exists | Do not retry automatically |
| Production, commit, push, merge, publication, or branch replacement is requested without its own authority | Do not perform it |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTT.GATE_DATALOADER | decision | 50 | execution_gate | ready->RETURN_SUCCESS;blocked->RETURN_ISSUES | MTT.ENFORCE_DESIGN | stop | The final immutable FSM ZIP has passed task-local validation and awaits the separate core.data-loader flow |
| RETURN_SUCCESS | terminal | 60 | terminal | none | MTT.GATE_DATALOADER | stop | The package is ready for governed Data Loader validation; no mutation is authorized by this result |
| RETURN_ISSUES | terminal | 999 | terminal | none | none | stop | Any validation, dependency, default, design, or approval gate fails |

<!-- E2E-DISCOVERY:DISC-MTT-FIELD-LENGTH-20260909 -->
## Field length correction

When a requested Name exceeds 20 characters or Description exceeds 80 characters, stop before candidate generation and explain which business record and field is too long, its actual character count, and the supported maximum. Ask the implementor to provide or approve shortened business text, then rebuild a new immutable preview. Do not retry a previously failed package and do not reuse its approval. If Fusion reports an otherwise unknown validation, preserve the complete diagnostic and return it for a new correction cycle. Evidence: `SRC-EDM-RA-CUST-26B`, `SRC-E2E-MTT-FIELD-LENGTH-20260909`.
