# Manage Transaction Sources Error Handling and Handoff Gates


## Error Situations

| Situation | What Should Happen |
|---|---|
| Required input is missing or invalid | Return the exact affected field and do not build an approvable candidate |
| A reference has zero or multiple matches | Return the portable keys and match count; never choose an identifier arbitrarily |
| Optional public preflight is unavailable | Record the transport or authorization class and continue only to offline build; FSM validation remains mandatory |
| FSM validation later reports an error | Preserve the request/process identity and sanitized diagnostic; stop before retry |
| A prior live attempt has uncertain outcome | Reconcile with read-only verification before considering another attempt |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| INPUT_VALIDATION | Missing, malformed, off-domain, or conditionally invalid input | Correct the specific row and regenerate preview |
| REFERENCE_ZERO_MATCH | No target matches the portable business key | Correct or create prerequisite setup through its own approved workflow |
| REFERENCE_AMBIGUOUS | More than one target matches | Supply the missing set or identifier context |
| PREFLIGHT_UNAVAILABLE | Read-only public preflight cannot run | Retain the limitation and rely on later exact-task FSM validation |
| PACKAGE_CONTRACT_BLOCKED | Requested behavior is not represented by the confirmed package contract | Obtain matching-release evidence before claiming support |
| EVIDENCE_UNRESOLVED_UPDATE | A non-key, non-audit implementor-target update field has no source-backed support conclusion | Disclose the gap; after deterministic checks pass, offer only an exact implementor-approved governed application-validation attempt |
| ENTITY_OPERATION_OWNERSHIP_BLOCKED | A direct operation or override targets a package dependency or reconciliation-only entity | Target the evidence-backed implementor entity; never use an override to bypass ownership |
| APPROVAL_BLOCKER | No immutable Data Loader preview or candidate-bound approval exists | Stop before every Fusion write |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Offline candidate | Exact task code/name, normalized business inputs, omitted system fields, source-backed defaults, unresolved blockers, and artifact fingerprint |
| Unresolved update choice | Exact update operation, uniquely export-owning `ORA_AR_TXN_BATCH_SOURCE` or `AR_BATCH_SOURCE` entity, requested fields and raw values, evidence gap, deterministic checks, environment, unchanged-value preservation, one-submission/no-retry boundary, and the fact that approval to test is not proof of product support |
| Immutable Data Loader preview | Target nonproduction environment, exact ZIP/member fingerprints, intended operation, row-level validation results, and approval boundary |
| Failure | Failure class, affected row/business key, sanitized diagnostic, process/request identity when present, and one safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| No immutable preview and explicit candidate-bound approval | Do not submit an FSM import |
| Candidate changed after preview | Do not reuse prior approval; generate a new preview |
| Unresolved or ambiguous reference | Do not invent an ID or silently select a match |
| Wrong package entity for the requested operation | Keep AR_BATCH_SOURCE non-targetable for create; for update, select only the entity containing the exact Name plus SetCode key in the fresh export and never move the row across projections |
| Key, audit/identity, source-proven unsupported, package-integrity, authorization, or deterministically invalid field | Do not offer the unresolved-field override path |
| Failed or uncertain live attempt | Do not automatically retry |



## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTS.HANDOFF_GATE | decision | 6 | execution_gate | static_ready->MTS.STATIC_READY;blocked->MTS.RETURN_ISSUES | MTS.ENFORCE_DESIGN | stop | Before handing a normalized request to task-owned offline package tooling |
| MTS.STATIC_READY | terminal | 7 | terminal | none | MTS.HANDOFF_GATE | stop | Static validation, dependencies, defaults, and design gates passed |
| MTS.RETURN_ISSUES | terminal | 90 | terminal | none | none | stop | Any blocking validation, reference, design, approval, or package-contract outcome |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-UI-MTS; SRC-CS-AMIMPL | Surfaced validation and FSM import failure boundaries |
| SRC-FSM-CURRENT; SRC-FSM-TEMPLATE | Exact task package identity and safe offline validation basis |
| SRC-DOC-COMPLETION-26C; SRC-DOC-NUMBERING-26C | User-facing completion and numbering constraints |
| Generation prompt safety contract | Run Book, Data Loader, preview, approval, retry, repository, and contribution gates |
