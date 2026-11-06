# Error Handling

| Situation | Required action |
|---|---|
| Source is unreadable, ambiguous, or missing required values | Stop before CSV generation and request the smallest clarification. |
| Current public template cannot be fetched | Stop as transport_or_environment; use a finite download timeout of at most 60 seconds per request and no automatic retry. Report the sanitized failure and verify the public source and connectivity before retrying; do not use a stale layout. |
| Retrieved template differs from the local contract | Stop as catalog_or_metadata_mismatch (template drift); resolve the changed contract before creating a package. |
| CSV or ZIP validation fails | Preserve supplied ZIPs. Use disposable workbook copies and new ZIP paths when generating corrected packages. Any package change requires fresh validation and approval. |
| ZIP changes after validation | Restart template-driven validation and produce new handoff evidence. |
| Preparation metadata is incomplete | Fail local validation and report the missing or inconsistent evidence for the supplied archive. |

Classify these failures as input_validation, catalog_or_metadata_mismatch,
transport_or_environment, or artifact_persistence. This skill does not perform
authorization, upload, import,
monitoring, ESS, or Fusion API operations; `core.data-loader` handles any
later execution failure in its own workflow.

Record failed local validation using `schemas/validation-result.schema.json`
and `schemas/skill-run.schema.json` in the active project workspace. Include
status, stage, failure class, sanitized message, recommended action, public-source
or local environment identity, and safe artifact references in schema-supported
fields. Omit credentials, tokens, authorization headers, and customer data.

## Validation Scope

Evaluate completeness and SHA-256 binding of the existing immutable archive's
recorded preparation evidence. Local readiness reports this evidence check;
it does not authorize an external operation or require repeated preparation
or handoff.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CHANGE_ORDER_FBDI.HANDOFF_GATE | decision | 3 | execution_gate | ready->CHANGE_ORDER_FBDI.READY_FOR_CORE_DATA_LOADER;blocked->CHANGE_ORDER_FBDI.FAILED | CHANGE_ORDER_FBDI.CONFIRM_LOADER_ROUTE | stop | Whenever completeness and SHA-256 binding of the supplied immutable archive's recorded preparation evidence are evaluated. |
| CHANGE_ORDER_FBDI.READY_FOR_CORE_DATA_LOADER | terminal | 4 | terminal | none | CHANGE_ORDER_FBDI.HANDOFF_GATE | continue | Local validation and immutable preparation evidence are complete; this result reports package readiness only. |
| CHANGE_ORDER_FBDI.FAILED | terminal | 5 | terminal | none | none | continue | Any local validation, template, public-source transport, or artifact-persistence failure occurs. |
