# Funds capture profile outcomes and safe handoff


A static or offline pass is not a successful import. Preserve actual application diagnostics and exact request identity.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Known invalid field | Stop before package generation; name exact field, offending value and field rule. |
| Evidence unresolved | An unresolved business field is evidence_unresolved, not proven invalid. Apply every known deterministic rule first. For an eligible unresolved field, disclose the exact gap and expected FSM diagnostic surface and obtain explicit acceptance for that exact candidate before normal preview and import approval. This never bypasses package integrity, target identity, parent ownership, key/audit protection, a proven-invalid rule, an explicitly unsupported operation/field, environment authorization or candidate-specific submission approval. Stop after rejection; no automatic retry. |
| LOV mismatch | Retain 25071 multiple-match or 25072 no-match only when actually surfaced; configured null exceptions and source applicability remain material. |
| XML row duplicate | Retain TooManyObjectsException/RowReadXMLException and exact affected key. |
| Import rejection or uncertain result | Stop. Capture sanitized process result/logs and reconcile read-only before requesting a new decision; never automatically retry. |
| Partial family processing | Do not promise all-or-nothing rollback. Reconcile each affected family and preserve unrelated data. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Business design review | Exact task/environment, operation, key, proposed changes, reference evidence, known validation results and remaining accepted uncertainty, before loader approval. |
| Loader approval preview | Display the active Data Loader returned approval Markdown verbatim; do not add business-design details, alternate wording or task-specific approval tokens. |
| Import approval | Active Data Loader approval contract bound to unchanged candidate; design confirmation is separate. |
| Verification | Fresh export identity, field-by-field persisted comparisons and preservation. Strict date metadata permits equivalent calendar forms only for identical dates. |
| Handoff | Readiness means only that declared local checks passed; Data Loader retains submission and approval authority. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing approval | No submission or direct browser/REST/SQL mutation. |
| Unavailable supported route | No task-local import bypass, private loader calls, saved-envelope fallback into an interactive session, or persistence of memory-only session inputs for offline validation. |
| Failed load | No automatic retry or expanded scope. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FCPP.HANDOFF | step | 50 | execution_gate | success->FCPP.READY | FCPP.DESIGN | stop | Selected task request |

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FCPP.READY | terminal | 60 | terminal | none | FCPP.HANDOFF | stop | Local checks complete; return readiness to the active Run Book and Data Loader, not import success |
