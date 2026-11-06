---
skill_id: "scm.supply-chain-planning.supply-chain-planning-configuration.manage-planning-measures"
name: "Manage Planning Measures Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Planning Measures under the Supply Chain Planning Configuration functional area."
layer: "pillar"
pillar: "SCM"
offering: "Supply Chain Planning"
functional_area: "Supply Chain Planning Configuration"
functional_area_code: "ORA_MSC_VC_PLANNING_CONFIGURAT"
task_code: "CUSTOM_MSC_MANAGE_PLANNING_MEASURES"
task_name: "Manage Planning Measures"
parent_skill_id: "scm.supply-chain-planning.supply-chain-planning-configuration"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObjects:
  - "planningMeasures"
  - "planningMeasureSourceLists"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM supply chain planning pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
  - "core.data-loader.task-hook"
  - "core.fusion-api.rest-api-client"
uses_core:
  - "core.data-loader.task-hook"
  - "core.fusion-api.rest-api-client"
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "setup_task_sequence"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/scm/supply-chain-planning/supply-chain-planning-configuration/manage-planning-measures/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/supply-chain-planning/supply-chain-planning-configuration/manage-planning-measures/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Writes approved Planning Measure and related child changes to the selected Fusion environment."
  - "Deletes an approved Planning Measure only after the declared deletion checks."
  - "Persists project run, validation, diagnostic, and token-usage artifacts."
required_privileges:
  - "Fusion privileges appropriate to the operation; agent-side privilege preflight is optional under the task-scoped user-authorized exception below."
---

# Manage Planning Measures Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Planning Measures` under `Supply Chain Planning Configuration`.

## Setup Task Skill Contract

- task_code: `CUSTOM_MSC_MANAGE_PLANNING_MEASURES`
- task_name: `Manage Planning Measures`
- parent_skill_id: `scm.supply-chain-planning.supply-chain-planning-configuration`
- pillar: `SCM`
- offering: `Supply Chain Planning`
- functional_area: `Supply Chain Planning Configuration`
- functional_area_code: `ORA_MSC_VC_PLANNING_CONFIGURAT`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `REST`
- businessObjects: `planningMeasures`, `planningMeasureSourceLists`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Planning Measures` under `Supply Chain Planning Configuration`.

For a new Planning Measure, use supplied ordered measure levels when present. Otherwise use a supplied positive integer `GranularityId`; if neither measure levels nor `GranularityId` is supplied, default `GranularityId` to `135`. Resolve the selected ID through the declared `granularityLevels` lookup and take its ordered levels and `MeasureContextId` from the exact returned item. A missing, invalid, or failed lookup still blocks creation. Do not replace invalid explicitly supplied levels or an invalid explicitly supplied ID with the default. Clear `GranularityId` from an ordinary create source after resolution. For a create handoff originating from duplication, preserve the authoritative source `GranularityId` when the selected live create schema and adapter support that field and exact value; apply the duplicate granularity contract below instead of the ordinary clearing rule.

For supplied levels, validate an explicit Measure Context first. If omitted, check Default, then resolve the remaining levels to one uniquely supported context and validate the complete set there; ask only when context cannot be resolved uniquely. Use the context lookup with onlyData=false to retain its DimensionLevels links. For Project or Planning Attribute, retain the ordered Default subset for LevelsList after selected-context validation.

For a create whose level source is an explicitly supplied GranularityId, a successful complete granularityLevels lookup with exactly one matching item is authoritative for its ordered levels, dimensions, and context. Continue using those returned values without revalidating them through planningMeasureLevels or DimensionLevels; a missing dimension or LOV link in those separate lists does not block this branch. If the exact ID is absent, skip creation and report it as not found. A failed, malformed, ambiguous, or incomplete lookup still blocks creation; all other create validation and approval gates remain applicable.

Treat Configure-to-Order (CTO) as a Default dimension (MeasureContextId 1). Once its exact dimension and level identity are resolved, classify its levels as Default-eligible even when the separate Default-context dimension list omits CTO or its DimensionLevels link. Retain those levels in ordered LevelsList, including the Default subset for Project or Planning Attribute duplication. CTO alone does not require a non-Default context selection; unresolved or ambiguous level identity still blocks validation.

### Fusion-enforced authorization

Apply the [Fusion-enforced authorization policy](ora-resource/ora_design_enforcement.md#fusion-enforced-authorization). Agent-side privilege preflight is optional under its task-scoped user-authorized exception. Missing evidence or unknown mappings do not block execution or require a privilege-confirmation question. Fusion still enforces authorization; known denied access and actual authorization failures remain blockers. Keep the active workflow's environment, account/session, OAuth configuration, catalog, adapter, payload and execution-approval checks.

Fusion enforces authorization for every declared request. Apply `ora-resource/ora_error_handling.md` to a returned 403; do not infer a particular missing privilege or automatically retry a mutation. Keep all workflow, seeded-field, dependency, exact-payload approval and readback requirements in force. Each child loader session still requires its own displayed preview and fresh contextual approval.

### Seeded-measure update restriction

For an existing measure, resolve authoritative `IsSeeded` from the exact parent baseline before preparing an update, delete, or any Source List action. Apply the [seeded-state interpretation](ora-resource/ora_input_validation.md#seeded-state-interpretation): `1` means Yes (seeded/predefined); `0` and `2` both mean No (custom/non-seeded). Preserve the raw returned value as evidence. If the attribute is missing, null, unreadable, or outside these codes, stop. For a seeded measure, reject requested changes to `Name`, `Description`, measure value type (`Editable`, `StoreResult`, or collected/refreshed flags), `EditRange`, measure-group or measure-catalog assignments, `RelevantPlanType`, `BaseUOMCode`, `BaseCurrencyCode`, `AggrOrder`, `AggrMethodTime`, `AggrMethodOther`, `WeightedBy`, `DisaggrMethodOther`, `DisaggrBasisOther`, `SecBasis`, `DecimalPlaces`, `SourceType` or its source level/attribute configuration, `IsShared`, `DataTypeId`, and `GranularityId`. Also reject every `planningMeasureSourceLists` add, edit, or delete against a seeded parent. Compare requested changes with the baseline; carrying an unchanged value solely as a required match/context field is not a change. Do not silently omit a blocked change or replace it with a default. Fields outside this list remain subject to their existing editability, validation, adapter, and approval rules; this restriction does not itself authorize them.

## Edit and Delete Existing Measure Source Lists

Route explicit existing-row edits or deletes to `edit_measure_source_lists` or `delete_measure_source_lists`, respectively, in `ora-resource/ora_reference_lookups.md`. These branches support only existing rows; they never create rows or switch the parent source mode. Require authoritative non-seeded parent status and parent `SourceType = LIST` (the existing environment code mapping is `3`). Retrieve all target rows with `ListId`, `MeasureId`, `Name`, and `IsDefault` before any mutation. Use only the immutable server-generated `ListId` for row identity, never the Source List Name.

Apply `CPA.VALIDATE_EXISTING_SOURCE_LIST_ACTIONS` and `CPA.GATE_EXISTING_SOURCE_LIST_BATCH`. Updates contain only changed `Name` and/or `IsDefault`; validate Name against the environment metadata contract and IsDefault as `1` or `2`. No changes means no update. Evaluate the complete final row set, allowing zero defaults and at most one default. Making a row default includes demoting the previous default in the same batch. Delete only a verified row explicitly requested for deletion; omitted caller rows remain unchanged. Deleting the default requires no replacement unless requested.

The selected Run Book submits a POST to the version root `/fscmRestApi/resources/11.13.18.05/` on the selected environment through `core.fusion-api.rest-api-client`, with `Content-Type: application/vnd.oracle.adf.batch+json` and `REST-Framework-Version: 9`. Do not POST this batch body to the `/planningMeasures` collection or use `application/json`. The body is an object with a top-level `parts` array: first the parent measure `update` part at `/planningMeasures/{MeasureId}`, then the requested Source List `update` or `delete` parts at `/planningMeasureSourceLists/{verified ListId}`. These are relative batch part paths, not standalone request endpoints; bind the documented root endpoint and selected adapter to the active workflow rather than inferring an endpoint from a part path.

Retrieve the current parent baseline and `ObjectVersionNumber` before constructing its update payload. Include `ObjectVersionNumber`, `Owner`, `Name`, `Description`, and `DataTypeId` with their current retrieved values, preserving nulls and value types; do not introduce unrelated parent changes or change SourceType. Each part has a unique `id`. A Source List edit payload contains only changed `Name` and/or `IsDefault`. A Source List delete part contains `"payload": {}`. Include any previous-default demotion as another Source List update in the same `parts` array. If no child change remains, submit no batch, including no parent-only update.

Use this update shape with identities and parent values resolved from the current baseline (values below are synthetic):

```json
{
  "parts": [
    {
      "id": "part1",
      "operation": "update",
      "path": "/planningMeasures/101",
      "payload": {"ObjectVersionNumber": 2, "Owner": null, "Name": "Example Measure", "Description": null, "DataTypeId": "1"}
    },
    {
      "id": "part2",
      "operation": "update",
      "path": "/planningMeasureSourceLists/202",
      "payload": {"Name": "Example List", "IsDefault": 2}
    }
  ]
}
```

For deletion, retain the parent part and replace the child part with `{"id":"part2","operation":"delete","path":"/planningMeasureSourceLists/202","payload":{}}`. For an edit, omit each unchanged child field; `IsDefault: 2` represents false under the validated existing mapping.

Present the exact environment and complete POST body, including the parent update and any default demotion, for approval immediately before execution. Never send ListId, MeasureId, or version/audit fields in a Source List edit payload, and never include a Source List create operation. Verify every part, the parent values, and the full final Source List set, including unchanged rows, before reporting success; preserve partial failures and do not replay an uncertain batch. Screenshot values are examples only; resolve identities, version and values from the target environment.

## Planning Measure Field Capabilities

Use `ora-resource/ora_reference_lookups.md` for exact measure, UOM, and currency resolution and the configured Expression Builder validation contract. Apply `ora-resource/ora_input_validation.md` and `ora-resource/ora_design_enforcement.md` before preparing a source. A lookup or a documented REST operation is not an execution route.

- **Expression:** Accept optional `expression`. When `Expression` is requested , validate its exact text through `planningMeasureValidateExpressions`. Inspect the returned validation details for `Expression is valid`. Retain the response; surface any other returned detail message verbatim and stop before submission. For a non-editable, non-stored measure require a valid Expression or select Collected and Refreshed / stored result. Include the exact validated `Expression` on create or when added or changed on update. `SeededExpression` is read-only.
- **Edit Lock Expression:** Accept optional `editLockExpression` only when Editable and Advanced Settings are enabled. Validate its exact text with the same server-side validator, passing it in the request body's `Expression` field. Require a returned validation detail containing `Expression is valid`; include the exact validated text as `EditLockExpr` on create or when added or changed on update. `SeededEditLockExpr` is read-only.
- **UOM, currency, and price lists:** Apply the field contract below to the measure Name, base codes, and display associations. For an existing measure, add an association only if the active workflow selects and verifies its parent measure batch child-create contract. Do not substitute a standalone child REST request or an unsupported batch operation.

### Name, UOM, currency, and price-list payload fields

Read and construct this portion of the measure payload with only the following attributes; other measure fields follow their own validation rules:

The create branches use `CPA.VALIDATE_CREATE_MEASURE` and
`CPA.VALIDATE_CREATE_MEASURE_FROM_GRANULARITY` in
`ora-resource/ora_input_validation.md` to validate and construct these fields.
The update branch uses `CPA.VALIDATE_MEASURE_UPDATE_FIELDS` in the same file.

`Name` is required, nonblank, and unique among existing measures. Complete the current measure lookup before deciding uniqueness; any exact match blocks a new create. For an update, the measure's own unchanged Name is allowed, but a changed Name must not collide with another MeasureId.

Measure Catalog is required for creation and duplication, along with Measure Group and Plan Type. If the required Measure Catalog is omitted, blank, empty, or absent after seeded duplicate associations are excluded, stop the current create or duplicate handoff immediately with input_validation and report: Creation blocked: a valid Measure Catalog is required. Apply this local presence check before any create expression-validation POST; after a complete duplicate source read, apply it before context resolution. Do not ask a question, prompt for a catalog selection, or continue source preparation, preview, approval, or submission in that run. Require at least one resolved catalog before source preparation. An omitted selection is allowed for duplication only when a valid copied non-seeded association supplies it; an explicit blank, empty, missing, ambiguous, or unresolved selection blocks creation. Do not infer or default a catalog. For duplication, copy and validate non-seeded source catalog associations when present; if none remain after seeded links are excluded, stop this handoff. A later new request must supply a valid catalog selection.

Set `BaseUOMCode` only for a Number `DataTypeId` on a non-seeded, non-read-only measure when the selected granularity does not contain both `PRD` and `ORG`, and the exact code resolves through the UOM LOV. Set `BaseCurrencyCode` only for a Currency `DataTypeId` under the same seeded, read-only, and `PRD` plus `ORG` restrictions, with an exact Currency LOV match. Omit or set an inapplicable, unsupplied base code to null; reject an explicitly supplied code that violates these conditions. Resolve `DataTypeId` through the live data-type lookup rather than guessing numeric IDs.

For `MeasureUOM.items`, resolve every `UomCode` from the UOM LOV, deduplicate codes, and never substitute a display name. For `MeasureCurrency.items`, do the same with `CurrencyCode` and the Currency LOV. Do not include either association for Percent, Date, or Text measure data types. Reject unresolved codes or duplicates that remain after normalization.

For `MeasurePriceList.items`, resolve each supplied Price List name to exactly one live Price List ID, write that numeric ID as `PricelistId`, and deduplicate IDs. A missing or ambiguous name blocks the payload. Never send `PriceListName`, and never use a Source List `ListId` as `PricelistId`.

### Mandatory expression gate

Before preparing or submitting a measure create or edit payload, invoke the configured server-side validator for `planningMeasureValidateExpressions` separately for each requested `Expression` and `EditLockExpr`.

`CPA.VALIDATE_CREATE_EXPRESSIONS` and `CPA.VALIDATE_UPDATE_EXPRESSIONS` in
`ora-resource/ora_reference_lookups.md` own the validator request and response
contract as executable task nodes.

For a create request containing `Expression`, enter `CPA.VALIDATE_CREATE_EXPRESSIONS` and call the validator POST in the selected Fusion environment. Continue to measure creation only after that request validates the exact supplied text.

Use the workflow-selected `core.fusion-api.rest-api-client` to `POST /fscmRestApi/resources/11.13.18.05/planningMeasureValidateExpressions` against the selected Fusion environment's configured `restBaseUrl`. Use this task-specific relative endpoint with each selected environment without an `rv:` revision. Do not infer validator availability from Data Loader registration. If the configured REST client cannot invoke this POST, stop with `Expression validation is unavailable through the configured Planning Measure validator. The expression was not submitted.`

After the binding passes, invoke one validator POST per requested `Expression` or `EditLockExpr`. The JSON body contains `MeasureId` (null or empty for create or duplicate; the resolved existing ID for edit), target `Name`, and the exact text in `Expression`; put Edit Lock text in that field for its own call. Data Loader source validation and an archived measure payload do not establish expression validity. Do not omit a requested expression or replace Fusion validation with local syntax checks.

Inspect Fusion's validation message in the response body even when the validator POST returns an HTTP error status. Read each `o:errorDetails[].detail` string, or the plain server message if no JSON detail is returned; unwrap an HTTP error prefix before comparing the server message. Only the exact message `Expression is valid` with no conflicting message passes this gate, regardless of HTTP status. Display every other returned server message verbatim and stop before measure create or update; a transport failure without a readable server message or an empty or unreadable response blocks submission. Preserve each validated text and result with the target name and MeasureId in the pre-submit evidence. Carry the exact validated `Expression` or `EditLockExpr` into the final payload; stop until the selected create or update adapter accepts that field. Before create, present the target environment, measure name, validated expressions, each validation result, and final immutable create payload for the selected workflow's approval immediately before execution. Changed expression text, name, MeasureId, environment, or payload requires fresh validation and approval.

Before any live action, resolve project and Run Book state, exact environment, identity, full source data, supported operation and client, payload/schema, artifact, and approval requirements. Present the final immutable payload or import artifact. The routed `core.data-loader` or `core.runbook` approval is authoritative for its own execution; another routed mutation needs explicit approval immediately before execution. Verify changes by reading the exact measure and associations after successful completion. Persist a classified diagnostic and stop if a workflow, validator, LOV, adapter, or approval contract is missing.

## Planning Measure Duplicate and Delete Requests

Current functional guidance: [Oracle SCM 26D: Duplicate, Edit, and Delete Measures](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fasop/duplicate-edit-and-delete-measures.html). Verify the selected environment's supported schema and adapter as required below.

For duplication or deletion, use `ora-resource/ora_reference_lookups.md` to resolve a supplied measure name or MeasureId to exactly one current measure. Complete pagination before deciding whether a name is unique. A name that identifies one measure is sufficient; do not demand its internal ID from the user. A missing target, ambiguous name, incomplete lookup, or unverified environment identity stops the action with a specific explanation.

- **Delete:** Require a clear deletion request and a measure name or MeasureId. Resolve the name to one exact positive MeasureId and check the current seeded status and complete associations through the workflow-selected read-only lookup. Predefined measures and measures with blocking manual associations cannot be deleted. Disclose the environment, exact MeasureId, name, and impacts before the Data Loader preview. Use one core.data-loader session and its Task Hook preview and contextual approval; do not ask a second deletion-approval question. Never retry deletion automatically. Verify the Data Loader job result and errors before reporting deletion. Classify a failure as predefined-measure, manual-association, authorization, loader-process, or other API error.
- **Duplicate:** Require a source measure name or MeasureId. Apply the Fusion-enforced authorization policy above, including in the fresh create handoff and separately approved child load. Fusion still enforces account authorization; report any returned authorization failure without automatic retry. Create a new measure; never update the source or call an assumed dedicated duplicate operation. Copy valid applicable plan types, groups, catalogs, dimensionality, aggregation, value type, Expression, EditLockExpr, UOMs, currencies, price lists, conditional formats, and source-list values. Use the Duplicate name generation contract below. Set `MeasureId` to null; never submit the source MeasureId. Clear seeded catalog associations, SeededExpression, and SeededEditLockExpr; set the duplicate to non-seeded. Force validated copied Expression and EditLockExpr into the new create request even when their text is unchanged. Never reuse source ListId values; create fresh source-list child rows only after the parent returns its new MeasureId through the selected child adapter. Validate the complete copied definition and readback; ask for missing or invalid required copied settings only. Measure Catalog is required: valid copied non-seeded catalog associations satisfy the requirement when no selection is supplied; otherwise a missing, blank, empty or unresolved selection blocks this run without a catalog-selection question. Preserve the authoritative source GranularityId through the fresh create handoff, dependency synchronization, defaulting, and final immutable source when the selected live create schema and adapter accept it. Resolve it to validate the copied levels and context, not to erase it. Retain the adapter-support evidence and duplicate origin internally. If the adapter cannot preserve it, use a level-based alternative only after verifying equivalent dimensionality; otherwise stop before approval. Never replace a duplicate's granularity with the ordinary create default. Verify the saved duplicate's granularity and dimensionality against the approved source definition.

Route preparation and execution through the active project workflow and its declared client or adapter. The reference lookup is not authority to call a live endpoint. If a required workflow step or adapter is missing, record the gap in the project workspace and stop before mutation. For an external mutation routed outside `core.data-loader` or `core.runbook`, present the exact environment, operation, and payload or immutable artifact and obtain explicit approval immediately before execution. Report delete success only after the Data Loader job succeeds with no delete errors; report duplicate success only after readback confirms the approved name and validated definition. Otherwise report the failure class and specific cause, including authorization failure, predefined measure, manual association, or name collision.

### Duplicate payload fields

Copy `MeasureCalculationType` from the authoritative source, including an
explicitly returned null. Preserve its metadata-required type through source
preparation, the immutable payload, and readback; do not stringify numeric
values to work around a generic server error.
Do not copy `GoalValues`: send null in a REST create
payload, or omit it when Data Loader cannot represent null. Do not block or
report duplication solely because `GoalValues` is omitted or not retained.
Apply the contract in `ora-resource/ora_input_validation.md` during duplicate
validation and both fresh-create branches.
Omit `RestAction` from Fusion REST JSON payloads. For ADF_REST Data Loader
duplication, retain `RestAction=POST` solely as a loader control in each create
source row, including copied associations. Before approval, use the existing
live Data Loader schema checks to confirm the registered ADF_REST route accepts
RestAction and every create row has POST. Those checks satisfy this task's
loader-control validation; do not request proof of the server's internal JSON
transformation. Missing/wrong controls or unsupported metadata still block.

### Duplicate name generation

Inputs are `originalName` (the source `Name`) and `existingMeasureNames` (the complete, currently existing name list in the target environment). Treat names as exact, case-sensitive strings; do not trim, normalize, or interpret the source name as a pattern.

1. Start with `Copy of <originalName>`. If it does not exist, use it.
2. Otherwise, find exact matches for `Copy<n> of <originalName>`, where `<n>` is a positive integer with no spaces. Select the lowest positive integer not already used and generate `Copy<n> of <originalName>`: no Copy1 means Copy1; Copy1 and Copy2 mean Copy3; Copy1 and Copy3 mean Copy2.
3. Require a nonblank name that does not already exist and is at most 250 characters. If the candidate exceeds 250 characters, stop and request a shorter user-provided name; never silently truncate. Validate any user-provided replacement against the same length and uniqueness rules, and never reuse the source Name.
4. Carry the exact generated or validated replacement `Name` and `MeasureId: null` through the fresh create handoff and final duplicate create payload. Never submit the source MeasureId.
5. Re-query or revalidate uniqueness in the target environment immediately before the create POST through the selected workflow. Incomplete evidence or a new collision blocks submission. A changed name requires renewed validation and the owning workflow's approval of the revised immutable artifact; do not change an approved payload silently.

The duplicate identity fields are:

```json
{
  "Name": "<generated unique duplicate name>",
  "MeasureId": null
}
```

### Duplicate source-list handoff

During `CPA.LOOKUP_DUPLICATE_MEASURE`, use `list_existing_planning_measure_source_lists` with the exact resolved base MeasureId through the workflow-selected read-only client. Read every page and capture each row's MeasureId, ListId, Name, and IsDefault plus the authoritative parent SourceType. A failed, malformed, mismatched, or incomplete lookup blocks duplication; only a successful complete lookup establishes an empty list. Do not ask the user to re-enter available source-list details.

Carry all returned rows into the fresh create handoff as child candidates containing the exact `Name` and `IsDefault`, with source identity retained only as lookup evidence. For a List source preserve `SourceType: 3` explicitly on the new parent; never let ordinary create defaulting switch it to None. Apply the existing source-list name, default-row, and live-adapter validation rules before parent approval. Source rows conflicting with a non-List parent mode block duplication rather than being discarded. Never send the source MeasureId, ListId, ObjectVersionNumber, or audit fields in child create records.

Only when the complete original source-list lookup captured one or more rows, continue after the approved parent create succeeds or passes Duplicate parent readback reconciliation in `ora-resource/ora_error_handling.md`, using its verified new MeasureId through the existing parent-first Source List creation workflow and a separately approved child session under Planning Measure duplication approval below. A successful complete empty original lookup skips Source List preparation, approval, and submission; verify the duplicated parent and report its outcome without a child continuation. Each child record contains only the new MeasureId and the captured Name and IsDefault. Read back all source-list rows for the new MeasureId and compare their count and exact Name/IsDefault values with the approved copied set. Report complete duplication only when parent and children are verified. If child creation or readback fails, report partial success with the new parent MeasureId and child results; do not recreate the parent or automatically replay child writes.

A duplication request includes copying every captured source-list row. After the approved parent completes and its readback verifies the new MeasureId, automatically prepare and validate the captured child rows in a fresh Data Loader session; do not wait for a separate copy instruction. Display that session's preview and obtain fresh contextual approval before submitting its own pending previewId. Parent approval never authorizes the child load. A complete empty original lookup skips child preparation, approval and submission. A failed parent may continue only through Duplicate parent readback reconciliation in `ora-resource/ora_error_handling.md`; uncertain or timed-out outcomes remain blocked. Preserve the parent's actual job status and verify the exact final child count and Name/IsDefault before reporting complete duplication. Never recreate the parent or replay child writes automatically.

### Planning Measure duplication approval

Use the [Planning Measure duplication approval policy](ora-resource/ora_error_handling.md#planning-measure-duplication-approval). The parent and child loads require separate live-session previews and contextual approvals. Before parent approval, retain the validated parent definition, proposed name, captured source-list candidates and both completion checks as workflow evidence; disclose the planned child continuation without claiming that parent approval authorizes it.

After verified parent creation or eligible readback reconciliation, bind only the verified new MeasureId. Validate the copied child rows and their complete final state in a fresh session, display its ordinary approval Markdown, and wait for a new affirmative for that child preview. Send approve with only that child's pending previewId to that same session. Do not reuse the parent's approval or previewId. Changed records, environment or task, a lost or expired child session, or missing parent verification requires fresh validation and approval; never replay a write. A complete empty original child lookup skips the child step. Standalone Source List loads keep their ordinary approval. Preserve failed parent status and verify final rows before reporting the outcome.

### Planning Measure delete adapter

For `delete_planning_measure`, use `core.data-loader` for the `planningMeasures` parent delete. In the selected environment, confirm the exact registered top discriminator, ADF_REST type, parent DELETE support, required key fields, and import route from live Data Loader metadata; missing or ambiguous support blocks the action. Prepare one parent-only loader source with `RestAction=DELETE`, the exact positive MeasureId from the complete read-only target lookup, and only other metadata-required identity fields. Include no child, MERGE, POST, or unrelated field rows. Validate the source in the persistent Data Loader session under the active Run Book task context; Task Hook evaluates the captured records and the session owns its single preview and contextual approval. Submit once through that session. Accepted initiation is not deletion: confirm successful job completion and no delete errors through the declared Data Loader status workflow. Preserve partial or uncertain results and never replay a delete automatically. Do not issue a direct REST DELETE or infer loader delete support from the REST resource or sample-generation capability.

For delete preflight, use the workflow-selected read-only `core.fusion-api.rest-api-client` to resolve the measure and read `GET /fscmRestApi/resources/11.13.18.05/planningMeasures/{MeasureId}/child/measureAssociations`; collect every page and record each association's `Type`, `Name`, `ReferenceEntityId`, and `DeletionType`. Any `Manual` association blocks deletion; disclose `Automatic` associations as impacts. If the complete lookup or association result is missing, stop before the loader session. Present the exact target, environment, and impacts before the Data Loader preview, and retain the evidence with the validated loader source. Use the existing workflow identity/session and delete-capability checks. Do not request a separate deletion approval beyond the loader session. Changed target, evidence, environment, or loader source requires a fresh validation session and approval. Apply `ora-resource/ora_error_handling.md` to any 403; do not retry the mutation.

For this delete branch's approval, keep the Data Loader session's Markdown preview, pending previewId, and approval workflow unchanged. If the question dialog flattens the preview table, render those same validated facts in the dialog as plain text: `Business Object Validation: Passed. Task: <actual task>. File: <actual file>. Errors: None. Do you want to proceed with the data load?` Use only the live preview's task, file, and result; show validation blockers instead of an approval question when preview fails.

### Payload and operation contract

After live schema and selected-adapter validation, the complete create source may also include separately validated expression fields. Omit optional keys that were not supplied; omit unchanged expressions from an update. Supplied codes must resolve through the target environment's LOVs.

`CPA.VALIDATE_CREATE_MEASURE`,
`CPA.VALIDATE_CREATE_MEASURE_FROM_GRANULARITY`, and
`CPA.VALIDATE_DUPLICATE_MEASURE` in `ora-resource/ora_input_validation.md`
own the create and duplicate payload fields. The expression lookup nodes own
the server validation contract before either create branch prepares a source.

### Existing-measure update batch

For `update_planning_measure`, the selected Run Book uses `core.fusion-api.rest-api-client` to POST one ADF batch to the selected environment's `/fscmRestApi/resources/11.13.18.05/` version root with `Content-Type: application/vnd.oracle.adf.batch+json` and `REST-Framework-Version: 9`. This is the declared batch route for this task; do not ask the user to supply an endpoint or headers already specified here. Confirm the configured client origin matches the active Run Book environment and that the adapter accepts the requested part operations before execution.

`CPA.VALIDATE_MEASURE_UPDATE_FIELDS` resolves the exact measure, current parent and association baselines, seeded restrictions, requested changes, and live LOV values. `CPA.SUMMARIZE_MEASURE_UPDATE` constructs the complete `parts` array from those results and the selected live schema; the caller supplies requested business values, not a prebuilt batch. Put the parent `update` part at `/planningMeasures/{MeasureId}` first, with its required baseline/concurrency fields and only validated parent changes. For newly requested display associations, add a `create` part at `/planningMeasures/{MeasureId}/child/MeasureUOM` for each validated `UomCode`, `/planningMeasures/{MeasureId}/child/MeasureCurrency` for each validated `CurrencyCode`, and `/planningMeasures/{MeasureId}/child/MeasurePriceList` for each numeric, uniquely resolved `PricelistId`. Include the exact parent linkage and any other required child fields only as confirmed by the selected adapter's live contract. Compare the complete existing and requested final sets; omit unchanged associations and reject duplicate creates. Do not infer a removal or existing-child edit operation from these add examples.

For an existing measure's requested addition or removal of dimension levels in a specified measure context, complete the exact `planningMeasureContextLevels` lookup and validate the selected context and level IDs. Preserve unchanged levels and their order while computing the complete final comma-separated `MeasureContextLevelsList`; an omitted level is not a removal request. Route this change as a separate `POST /fscmRestApi/resources/11.13.18.05/planningMeasureContextLevels` through the selected Run Book REST client with `application/json` and only `MeasureContextId`, `MeasureId`, and `MeasureContextLevelsList` in the payload. A zero-row baseline permits an addition only when creation of that context row is confirmed; it cannot support a removal. For one existing row, confirm the selected adapter's POST update/upsert behavior before submission because Oracle documents POST as create by default; an ambiguous contract or multiple rows blocks the write. Preview the complete before/after list and exact POST, then read back the selected context row and compare its ordered levels with the approved final list. For a level-only request, report updated only when the levels match; otherwise report failure or unverifiable readback. Do not use the parent `GranularityId` or `MeasureContext` as completion checks or label a level-only result partially completed. A level-only request has no parent batch; for a combined request preview both operations, run the parent batch first, submit the context POST only after its success, and report each write result accurately without replay if the second write fails.

For an edit to an existing Measure Conditional Format rule, read the complete current `MeasureConditionalFormat` child collection for the exact MeasureId, identify one requested rule unambiguously, and retain its returned `@context.key`, child item link, and current values. Validate the proposed final rule using the existing conditional-format Basis/Threshold measure and Condition lookups: require Basis, Condition, Color, and exactly one of Threshold or CompValue. When switching comparison modes, explicitly clear the old alternative with null if the confirmed child update contract requires it. After the parent `update` part, add an `update` part at `/planningMeasures/{MeasureId}/child/MeasureConditionalFormat/{key}` using that row's exact returned `@context.key` as `{key}`. Verify the resulting unencoded child path resolves to the same row with a read-only GET and that the selected batch adapter supports this update shape; the URL-encoded item `self` link alone does not establish a batch part path. Never build the key from example IDs or guessed components. Construct the child payload from the requested changes and required retained fields confirmed by live metadata. A missing, ambiguous, or unverifiable child identity or update contract blocks this edit; do not turn it into a child create. Include the exact final conditional-format rule in the approval preview and verify it by readback.

For an explicitly requested deletion of an existing conditional-format rule, use the same complete child baseline, unique row identity, returned `@context.key`, and verified unencoded child path. After the parent `update` part, add a `delete` part at `/planningMeasures/{MeasureId}/child/MeasureConditionalFormat/{key}` with `"payload": {}` only when the selected batch adapter confirms that operation. Preview the exact row to remove, then verify that it is absent and all other rules remain unchanged after the batch. Never infer a deletion from omitted rule fields or example identifiers.

Build only parts for fields actually requested. Catalog, group, and Source List parts visible in a broader UI save are not implied by a Description, UOM, currency, or Price List request; route any explicitly requested changes through their own validation and seeded-measure gates. Bind the exact environment, method, headers, operations, paths, and complete payload values to the immutable Run Book preview for immediate approval, execute once, inspect every part result, and verify the parent and final association sets. A collapsed UI screenshot is evidence of operation/path shape, not a required input or a substitute for current baseline, lookup, or adapter validation.

The requested duplicate contract is a new `planningMeasures` create through the selected adapter. The new parent uses its unique `Name` and copied validated fields, including `Expression`, `EditLockExpr`, `MeasureUOM`, `MeasureCurrency`, and `MeasurePriceList`; it sets `MeasureId` to null and excludes source `IsSeeded`, SeededExpression, SeededEditLockExpr and seeded catalog associations. Do not set `IsSeeded` to 2 by assumption. Omit it unless the live create schema requires an explicit value and the non-seeded code is verified for that environment. Re-resolve copied Price List names to numeric `PricelistId` values before the new create. For deletion, use the Data Loader adapter above.

## Setup Task Metadata

- Task name: `Manage Planning Measures`
- Task code: `CUSTOM_MSC_MANAGE_PLANNING_MEASURES`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `REST`
- Business Objects: `planningMeasures`, `planningMeasureSourceLists`

`planningMeasureValidateExpressions` is a task-specific REST validation endpoint, excluded from the Data Loader business-object list and sample-generation route. Continue invoking its verified server-side operation before preparing a measure source with an expression; expression validation does not require Data Loader BO registration.

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

Do not route CSV export work to `shared.setup-export.task-level-export` or CSV import work to `core.data-loader` unless live Fusion metadata or Oracle guidance confirms support. Use `shared.validation.setup-data-validator` only when a setup data artifact is available for review. Use `shared.validation.reference-data-validator` when the task depends on cross-pillar reference data.


## Download Fusion Data Loader Sample

Use this workflow when `dataloader_import_mode: "REST"` and a Fusion Data Loader sample is needed for the task's business objects.

1. In the workflow-selected Fusion environment, resolve each of `planningMeasures` and `planningMeasureSourceLists` against live Data Loader metadata. Confirm each exact top discriminator, registered sections, supported sample operation, and import capability. Save a sanitized metadata result with the environment and observation time in the project workspace. If any object cannot be resolved or lacks the required contract, classify a catalog mismatch, stop the two-object sample route, and report the missing contract. Do not infer Data Loader support from the REST validation service or substitute a different object.
2. Generate the default editable XLSX samples through `core.data-loader`:

   ```bash
   python3 core/data-loader/scripts/generate_sample_dat.py \
     "planningMeasures" \
     "planningMeasureSourceLists" \
     --output-dir "<project-artifact-directory>"
   ```

3. Keep each business object's generated workbook set together:
   - editable sample workbook
   - attribute-details workbook
   - key-fields workbook
4. Confirm that the result contains both requested discriminators and review their generated headers and key fields before preparing source data. The batch publishes no workbook if any requested object fails to resolve. The operation uses read-only Fusion metadata and does not upload or import data.
5. Use the generated editable workbooks as the starting point for the later Data Loader preparation and approval workflow.

## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `scm.supply-chain-planning.supply-chain-planning-configuration` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
