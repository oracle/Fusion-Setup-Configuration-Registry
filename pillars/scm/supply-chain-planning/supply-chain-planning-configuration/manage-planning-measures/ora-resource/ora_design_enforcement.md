# Manage Planning Measures Design Enforcement

## Fusion-enforced authorization

Use only the active workflow's selected environment, authenticated account,
OAuth configuration and declared client or adapter. Retain its existing
identity/session, catalog support, schema, payload and operation checks.

Fusion enforces authorization for every declared request. Handle an actual
401/403 through the selected core workflow and the response-first error policy;
a generic 403 does not identify a particular missing privilege. Never test
permissions with an extra write, substitute a browser or undeclared endpoint,
or automatically retry a failed mutation. Each loader session still requires
its own displayed preview and fresh contextual approval. All seeded-state,
dependency, payload, readback and no-replay requirements remain mandatory.

### Privilege evidence preflight

Task-scoped user-authorized exception, 19 October 2026: the user instructed,
"make Privilege preflight optional and yet make audit pass?" This supersedes the
earlier request to keep this task's preflight mandatory. For this task only,
agent-side privilege evidence assessment is optional, as an explicit exception
to the privilege-preflight clauses in AGENTS.md and
governance/error-handling-guidelines.md. It is not a declaration that grants
were verified and does not change policy for any other skill.

By default, continue normal validation, source preparation, preview and the
selected execution route without requesting privilege records, mappings, a
manual security review or privilege confirmation. Missing, stale or incomplete
evidence, an unknown privilege mapping, or an unavailable privilege-query
adapter is not by itself a blocker. Do not add a live call to test permissions.

If the user requests an optional assessment, evaluate available authoritative
records or an attributable manual security review against the exact environment,
account, planned parent/child and loader actions, OAuth scopes and target data
conditions. Never infer a verified grant from a role label, metadata GET, bare
confirmation or ordinary execution consent. Record passed only when the actual
required grants and conditions are established. Record absent or inconclusive
assessment as not_assessed or unresolved, never passed; it remains nonblocking.
Persist optional outcomes through existing validation_checkpoints and project
services, using standard validation-result info/warning findings to distinguish
an unassessed privilege from a verified grant. Do not introduce extra schema
fields or store raw security reports/credentials in reusable files.

Known denied access or an actual authorization failure still blocks the affected
action with authorization_or_privilege and existing response-first diagnostics;
never retry a mutation automatically. Identity/session, catalog/schema support,
seeded-state, payload, dependency, exact-preview approval and readback checks
remain mandatory. Parent approval does not authorize a fresh child session.

## Design Rules

### Planning Measure capability gates

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Seeded measure update or Source List action | Error | find_planning_measure_by_id_or_name | Authoritative IsSeeded is missing or ambiguous, or a seeded target requests any field or Source List change named in the Seeded-measure update restriction in ../SKILL.md | Report each blocked change and stop before source preparation, preview, or batch approval. Unchanged required identity/context fields are not updates; apply ordinary validation to all other fields. | No |
| EditRange would be changed | Error | find_planning_measure_by_id_or_name | Target is seeded or read-only, eligibility evidence is incomplete, or a non-editable payload includes EditRange | Stop any seeded/read-only EditRange change, including a default, clear, or copied value into the source. Preserve the stored value outside the change payload. Include a resolved EditRange only for an eligible Editable target. | No |
| Expression is supplied, changed, or copied | Error | validate_measure_expression | The configured Planning Measure REST validator is unavailable, the returned Fusion validation message does not state Expression is valid, the validated text differs from the payload, or a non-editable non-stored measure has no valid Expression | Display an invalid server message verbatim; for unavailable or inconclusive service return the prescribed unavailable message. Stop before submission, retain the exact validated text, and never edit SeededExpression. | No |
| Edit Lock expression is supplied, changed, or copied | Error | validate_edit_lock_expression | Editable or Advanced Settings is disabled, the configured Planning Measure REST validator is unavailable, the returned Fusion validation message does not state Expression is valid, or the validated text differs from the payload | Enable both prerequisites; display an invalid server message verbatim or return the prescribed unavailable message. Stop before submission and never edit SeededEditLockExpr. | No |
| Base or display UOM/currency is selected | Error | resolve_measure_uom_codes or resolve_measure_currency_codes | Any code lacks one exact live LOV match or the relevant association adapter is unconfirmed | Resolve all codes, remove duplicates, and use only the selected create or parent batch child route. | No |
| A measure is created or renamed | Error | check_planning_measure_name_unique | Name is blank, another measure has the same exact Name, or the paginated lookup is incomplete | Stop before source preparation; retain completed uniqueness evidence for the exact target Name. | No |
| Base UOM or Base Currency is supplied | Error | list_measure_data_types; resolve_measure_uom_codes or resolve_measure_currency_codes | BaseUOMCode is not Number, BaseCurrencyCode is not Currency, the measure is seeded/read-only, both PRD and ORG are present, or the supplied code has no exact LOV match | Reject an explicitly invalid base. Omit or null an unsupplied or inapplicable base; never infer eligibility from missing granularity evidence. | No |
| Display UOM or currency items are supplied | Error | resolve_measure_uom_codes or resolve_measure_currency_codes | Measure data type is Percent, Date, or Text; a code is unresolved; a display name is used as a code; or duplicates remain after normalization | Keep only resolved, distinct UomCode or CurrencyCode values in their respective item arrays. | No |
| A Price List association is supplied | Error | resolve_measure_price_list_ids | A name has zero or multiple exact LOV matches, its ID is not numeric, IDs remain duplicated, or PriceListName or Source List ListId would be submitted | Send only deduplicated numeric MeasurePriceList.items[].PricelistId values. | No |
| A measure is duplicated | Error | find_planning_measure_by_id_or_name | Source is not unique; target name collides; required copied settings, expression validation, or create/child route is missing | Create a new non-seeded measure using the exact case-sensitive name-generation contract in CPA.VALIDATE_DUPLICATE_MEASURE; enforce the 250-character limit and uniqueness immediately before create POST. Set MeasureId to null; strip source IsSeeded, seeded catalog links, seeded expression fields, and source ListIds. Do not force an unverified IsSeeded code. | No |
| A measure is deleted | Error | find_planning_measure_by_id_or_name; read_measure_delete_dependencies | Target is not unique, predefined/seeded, has blocking manual associations, or has incomplete dependency evidence | Stop and report the exact blocker before the Data Loader preview. | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPA.ENFORCE_DUPLICATE_MEASURE | decision | 259 | design_enforcement | pass->CPA.DUPLICATE_CREATE_HANDOFF;blocked->CPA.LOOKUP_FAILURE | CPA.VALIDATE_DUPLICATE_MEASURE | stop | Require a complete valid new-create projection. Apply the Fusion-enforced authorization policy in this file to the selected action, fresh create handoff and child load. Fusion authorization remains enforced; report any returned authorization failure without automatic retry. Normal validation and Data Loader approval still apply. Return the projection for a fresh Planning Measure create validation run and Data Loader handoff; never update the source or reuse its ListIds. If copied associations cannot be mapped by the selected create adapter, stop. A copied or archived Expression or EditLockExpr is not proof of validity; the fresh create run must pass the configured server validator before any create approval or submission. Require the projected DisaggrMethodOther to equal the captured source Allocation Type, including any supported blank/null state, and retain duplicate origin for the fresh create run. A missing source value, an unsupported allocation contract, or replacement with EQUAL blocks the handoff; Measure Value Type selection does not authorize changing the source allocation. Require a supported granularity strategy. For verified preservation support, the projection and final create source must retain the exact authoritative source GranularityId through defaulting and dependency synchronization. The fresh create run must check that the selected adapter does not drop or transform it. Otherwise require a verified equivalent level-based mapping; absent evidence blocks the handoff. Success readback must confirm the approved granularity and copied dimensionality.  For requested Project or Planning Attribute context, require the completed context-level projection lookup chain and selected-adapter support for its context lists. This explicitly selected context projection takes precedence over preserving the parent-context GranularityId. Verify the saved context-specific list and Default subset against the approved definition; unresolved finder or eligibility evidence blocks preview. |
| CPA.ENFORCE_DELETE_MEASURE | decision | 262 | design_enforcement | pass->CPA.DELETE_MEASURE_HANDOFF;blocked->CPA.LOOKUP_FAILURE | CPA.VALIDATE_DELETE_MEASURE | stop | Require a non-seeded target under the Seeded-state interpretation in ora_input_validation.md (`IsSeeded=0` or `2`; `1` is seeded and unsupported or missing values block), complete read-only association evidence with no Manual row, and a live-metadata-confirmed `core.data-loader` route for ADF_REST `planningMeasures` parent DELETE. Require one parent-only source row with `RestAction=DELETE`, exact MeasureId, and only metadata-required identity fields; no child or unrelated rows. Retain the selected environment/account, session and live parent DELETE capability checks. Disclose Automatic rows as impacts. Pass the validated target, source, and impact evidence to the Data Loader session for its single Task Hook preview and approval; this node performs no write or separate approval. Missing delete capability, keys, route, or adapter support blocks; do not substitute direct REST DELETE. |
| CPA.ENFORCE_CREATE_EDIT_RANGE | decision | 202 | design_enforcement | pass->CPA.VALIDATE_CREATE_SOURCE_TYPE;blocked->CPA.INPUT_VALIDATION_FAILURE | CPA.VALIDATE_CREATE_MEASURE | stop | Apply the EditRange design gate before source preparation and again against the final immutable source before submission. For an existing target require authoritative seeded and read-only status; unknown eligibility blocks the change. Never change EditRange for seeded or read-only measures, including defaulting or clearing. Omit EditRange when Measure Value Type does not select Editable. For an eligible editable target carry the input-validation result directly as EditRange with its resolved type; reject a missing, replaced, or transformed value. This node performs no write. |
| CPA.ENFORCE_GRANULARITY_EDIT_RANGE | decision | 207 | design_enforcement | pass->CPA.VALIDATE_CREATE_SOURCE_TYPE_FROM_GRANULARITY;blocked->CPA.INPUT_VALIDATION_FAILURE_FROM_GRANULARITY | CPA.VALIDATE_CREATE_MEASURE_FROM_GRANULARITY | stop | Apply the EditRange design gate before source preparation and again against the final immutable source before submission. For an existing target require authoritative seeded and read-only status; unknown eligibility blocks the change. Never change EditRange for seeded or read-only measures, including defaulting or clearing. Omit EditRange when Measure Value Type does not select Editable. For an eligible editable target carry the input-validation result directly as EditRange with its resolved type; reject a missing, replaced, or transformed value. This node performs no write. |
| CPA.ENFORCE_UPDATE_EDIT_RANGE | decision | 68 | design_enforcement | pass->CPA.SUMMARIZE_MEASURE_UPDATE;blocked->CPA.MEASURE_UPDATE_VALIDATION_FAILURE | CPA.VALIDATE_MEASURE_UPDATE_FIELDS | stop | Apply the EditRange design gate before source preparation and again against the final immutable source before submission. For an existing target require authoritative seeded and read-only status; unknown eligibility blocks the change. Never change EditRange for seeded or read-only measures, including defaulting or clearing. Omit EditRange when Measure Value Type does not select Editable. For an eligible editable target carry the input-validation result directly as EditRange with its resolved type; reject a missing, replaced, or transformed value. This node performs no write. |
