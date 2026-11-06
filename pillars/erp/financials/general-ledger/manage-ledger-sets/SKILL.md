---
skill_id: "erp.financials.general-ledger.manage-ledger-sets"
name: "Manage Ledger Sets Setup Task Guidance"
description: "Create, review and update General Ledger ledger sets exclusively through declared endpoints and the FSCR framework, using fresh inputs, packaged FSM rules and ledger-scoped structural exports; UI access and existing-set deletion are prohibited."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "General Ledger"
functional_area_code: "ORA_FIN_GENERAL_LEDGER"
task_code: "GL_MANAGE_LEDGER_SETS"
task_name: "Manage Ledger Sets"
parent_skill_id: "erp.financials.general-ledger"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.5.3"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "ledger_set_operation_and_field_delta"
  - "ledger_set_header_and_members"
  - "fusion_environment_context"
  - "authoritative_baseline_and_reference_evidence"
  - "fresh_ledger_scoped_structural_evidence"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "validated_fsm_package_and_task_handoff"
  - "ledger_set_verification_result"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/general-ledger/manage-ledger-sets/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/general-ledger/manage-ledger-sets/current/"
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
oracle_supplied_guidance_files:
  - purpose: "Input contract"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Read-only resolver contracts"
    location: "ora-resource/ora_reference_lookups.md"
  - purpose: "Dependency readiness"
    location: "ora-resource/ora_dependency_readiness.md"
  - purpose: "Create defaults and update preservation"
    location: "ora-resource/ora_defaulting_rules.md"
  - purpose: "Business and artifact policy"
    location: "ora-resource/ora_design_enforcement.md"
  - purpose: "Task validation handoff and errors"
    location: "ora-resource/ora_error_handling.md"
oracle_supplied_guidance_status: "Task-node guidance for creation, review and update; environment-specific references and import semantics must be verified at execution."
side_effects:
  - "Prepares task-specific FSM package changes locally; delegated export can create an export process and delegated core.data-loader execution can change ledger-set headers and assignments after its approval gate."
required_privileges:
  - "Endpoint privileges for FSCR task export/import GL_MANAGE_LEDGER_SETS and ledger-scoped GL_MANAGE_PRIMARY_LEDGERS export in the selected environment"
  - "COA metadata export access only when a named required structural gap triggers the conditional fallback"
  - "Read privileges for the declared reference endpoints and any explicitly configured FSCR metadata/report adapter required by the selected checks"
---

# Manage Ledger Sets Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Ledger Sets` under `General Ledger`.

Use a ledger set to process or report compatible ledgers together. Data access sets continue to govern security. This skill covers the corresponding business operations exclusively through declared endpoints and the existing FSM/Data Loader route.

## Framework-Only Execution

This skill and its delegated ledger-set workflow must never access the Fusion UI for discovery, checks, creation, review, updates or result verification. Do not open or navigate task pages, inspect browser DOM/network state, take screenshots, scrape screens, operate controls, or use a browser/manual UI fallback. UI screenshots and grid extracts are not authoritative runtime evidence. Perform checks through the declared reference endpoints using core.fusion-api.rest-api-client; acquire templates and setup data through shared.setup-export.task-level-export; submit writes and inspect status/logs through core.data-loader.

Each required fact must come from packaged rules, current declared endpoint results or an explicitly designated current artifact produced by the selected FSCR workflow. Conditional metadata/report checks require an already configured and declared FSCR endpoint/adapter; do not invent an endpoint, issue ad hoc SQL or substitute UI evidence. If a required field, membership, relationship or DFF fact cannot be obtained by that route, return catalog_or_metadata_mismatch with reason missing_framework_evidence and identify the exact missing fact/contract. Stop the affected operation until supported framework evidence is available. An explicit request to execute the task through UI returns input_validation with reason ui_execution_prohibited.

Authentication remains delegated to core.auth. If its supported flow needs interactive login, core.auth may open the login for the user to complete; the agent must not inspect or operate that login UI, read credentials, or navigate to Fusion task pages. This user authentication handoff is not a task execution or verification route.

## Existing Ledger Set Preservation

Deletion of an already-created ledger set is prohibited by FSCR policy. Reject requests to delete, purge, reset, clean up, roll back by deletion, or delete and recreate an existing set before any deletion-related export, package preparation, upload or live action. This applies to UI controls, REST or other adapters, FSM import instructions and test-data cleanup. Privileges, a supported Oracle delete capability, or general approval for tests/imports do not waive this rule. Return `input_validation` with reason `ledger_set_deletion_prohibited`, identify the requested set and preserve it; do not offer another deletion route.

Removing an individual assignment is a separate update operation subject to the existing supported-import, default-ledger and nonempty-membership gates. It must preserve the parent set. Do not remove all assignments, change its identity, or use replacement/import controls as a workaround to delete the set. Ordinary create, review and supported updates retain their current workflows.

## Setup Task Skill Contract

- task_code: `GL_MANAGE_LEDGER_SETS`
- task_name: `Manage Ledger Sets`
- parent_skill_id: `erp.financials.general-ledger`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `General Ledger`
- functional_area_code: `ORA_FIN_GENERAL_LEDGER`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Ledger Sets` under `General Ledger`.

## Setup Task Metadata

- Task name: `Manage Ledger Sets`
- Task code: `GL_MANAGE_LEDGER_SETS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Obtain or validate the current task template/spec with `shared.setup-export.task-level-export`; acquire the resolved primary ledger's scoped Manage Primary Ledgers export for shared structural values. Creation applies the packaged ledger-set rules; a separate COA export is conditional on a named required structural gap. No full ledger-set data export or previous run is required.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `General Ledger`
- Setup task name: `Manage Ledger Sets`
- Setup task code: `GL_MANAGE_LEDGER_SETS`




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

Use the parent functional-area skill `erp.financials.general-ledger` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Resource Read Order and Ownership

Read this manifest, the compiled [registry](ora-resource/ora_rule_registry.json), and each reachable source anchor. Resolve this task as one nested task, code `GL_MANAGE_LEDGER_SETS`.

Read [input validation](ora-resource/ora_input_validation.md), [reference lookups](ora-resource/ora_reference_lookups.md), [dependency readiness](ora-resource/ora_dependency_readiness.md), [defaults](ora-resource/ora_defaulting_rules.md), [design enforcement](ora-resource/ora_design_enforcement.md), and [error handling](ora-resource/ora_error_handling.md). These are the six runtime rule owners. This entrypoint owns field-to-package mapping, framework route selection and endpoint/export-based post-change verification.

## Task-Local Plan Validation

Build `setup_task_plan` directly from the shipped registry and its local source tables. This is an LLM validation step; it requires no authoring tool or planner script. Before any external request, require all of the following:

| Check | Required result |
|---|---|
| Task identity and readiness | Registry schema is `3.0`, representation is `nested`, and the selected task matches `GL_MANAGE_LEDGER_SETS` / `Manage Ledger Sets`. The task and every reachable node are `ready`, with empty `blocking_reasons`. |
| Graph integrity | Node IDs are unique; `start_node` is `MLS.VALIDATE_INPUT`; every prerequisite and transition target exists; the graph is acyclic; and every path ends at `MLS.DONE` or `MLS.FAILED`. |
| Source integrity | Every `source.file` resolves inside this skill's `ora-resource/` folder and its heading exists. Match each node by Rule ID to exactly one source `Task Nodes` row; node type, sequence, action type, transitions, prerequisites, failure behavior, and applicability must agree. Treat source line numbers as navigation hints, not proof. |
| Rule and resolver completeness | Read the owning validation, dependency, lookup, defaulting, design, and error rules for every reachable node. Each named resolver has exactly one local or live definition with its source, match rule, outputs, and failure behavior. Missing definitions, unresolved `TBD` values, or contradictions block the plan. |
| Supported actions and routes | This task uses `validate_input`, `reference_lookup`, `resolve_dependency`, `apply_default`, `design_enforcement`, `execution_gate`, `error_handler`, and `terminal`. Live resolvers use the declared REST client; local rules stay local. A node's action or route label alone does not authorize an external operation. |
| Request boundary | Normalize the request as create, update, review, or supported membership/default/DFF work on a ledger set. Reject existing-set deletion and deletion-equivalent cleanup or replacement before any lookup. |

Only after these checks pass, record a machine-readable `setup_task_plan` with `status: planned`, `validation.status: ready`, exact task identity, start node, the validated graph, and checked source references. A ready plan permits entry into the graph; each node still requires current evidence and its operation-specific gates.

For a missing, stale, inconsistent, or incomplete graph or source, stop with `FAILED` before external execution. Record the failed check, Rule ID/source when available, failure class, and corrective action in project diagnostics. Use `input validation` for malformed or incomplete contracts and `catalog mismatch` for task identity disagreement. Request correction of the MLS resources and registry; do not repair the graph during execution or substitute an undeclared route.

## Node Execution

1. Start at `MLS.VALIDATE_INPUT`. Follow declared transition outcomes; sequence numbers do not authorize skipping a node. Every listed prerequisite must have succeeded in the current run before a node can execute.
2. Apply only the reached node's owning source rules and named resolvers. Record the observed outcome and sanitized evidence, then follow its exact transition target. An unlisted outcome stops with `FAILED`; never invent a transition, lookup, default, retry, or cross-task action.
3. Complete the active workflow's environment, identity, privilege, catalog, payload, artifact, and approval checks before each external operation. Obtain approval for the exact target environment, operation, and immutable package immediately before the applicable create or upload request. Submit at most once in the run unless the owning rule explicitly permits another operation.
4. At `MLS.EXECUTION_GATE`, validate the exact prepared package before the loader renders approval. `MLS.DONE` means validation passed for the Data Loader handoff, not that an import completed. `MLS.FAILED` means stop and disclose the blocker.
5. Maintain a task-local run record with the normalized request fingerprint, current node, completed path and outcomes, sanitized evidence references, missing requirements, approval fingerprints, verified side effects, and safe resume stage. Exclude credentials, tokens, sensitive payloads, and protected response data.
6. On resume, compare the request fingerprint and refresh changed or time-sensitive evidence. A material input, environment, package, or delta change invalidates validation and approval. Reconcile any uncertain mutation through the declared safe verification route before considering a retry; never replay it automatically.

The registry validates inputs and the exact prepared package before the loader shows approval. `MLS.DONE` means task validation passed for a write, not that an import completed. Do not require prior import completion or a second task approval in the pre-upload Task Hook. Read-only review requires current complete evidence for the requested fields; it does not require an import candidate.

## FSCR Workflow

1. In implementation use, enter through `router.implementation-router`, select the project/environment, and resolve create, review, or update. Reject existing-set deletion and deletion-equivalent cleanup/replacement requests under Existing Ledger Set Preservation before preparing any action. Record the requested header fields, direct members, explicit member additions/removals, default, and DFF changes. Keep omitted fields distinct from explicit clears.
2. For create, use the declared core read-only client to run the fresh exact Name and independent ShortName prechecks, resolve members and the selected COA/calendar, confirm period compatibility and conditional currency, and resolve the balancing column. Delegate stale-token handling to core.auth and its user-completed login handoff; do not access any Fusion UI. Zero successful precheck matches means no conflict observed in the queried scope; disclose visibility limits. Failed/incomplete reads, observed conflicts and known restrictions invalidating the selected setup check block. Do not require a separate global inventory or any previous run for ordinary preparation.
3. Obtain or validate the current GL_MANAGE_LEDGER_SETS template and acquire a fresh ledger-scoped GL_MANAGE_PRIMARY_LEDGERS export through shared.setup-export.task-level-export. Scope by the resolved PRIMARY LedgerId using the acquisition contract in ora_reference_lookups.md. Read only the matching primary row's allowlisted structural fields; related rows may accompany the scoped family export. Show each exact export operation and obtain its required approval before POST. Do not routinely export COA configuration. Use the conditional COA acquisition/joins only for an identified required structural gap that the scoped export, declared lookups and packaged rules cannot resolve; disclose the exact missing field and additional export scope first. For update/review or nested/GAAP/DFF requirements, acquire only the additional current evidence needed by the selected operation. No full ledger-set export is an ordinary create dependency.
4. Apply packaged MLS_FSM_CREATE_V1 in ora_defaulting_rules.md; it supplies 27 explicit initialization values, new-name derivations and named omission rules without an external profile receipt. Prepare the candidate with fresh reference results, allowlisted scoped structural values and requested business fields, or a supported explicit update delta against current state. Validate all archive rows, actual fields/types and every field disposition, preserve current XML/header metadata, and retain only intended parents/assignments. A new project/environment/COA alone is not a profile incompatibility. Never transplant primary-ledger accounting options, another object's generated identity or audit values. Disclose base-profile descriptor and unresolved management-field omissions as authoring policies requiring server validation; blank management fields do not prove that the chart lacks a management role.
5. Hand the FSM ZIP to [core.data-loader](../../../../../core/data-loader/SKILL.md). The loader finishes file/API preflight, binds Task Hook validation to immutable upload bytes, then renders its own approval. Task Hook uses this task's compiled plan and six source files. Any package, target, scope or routing change requires fresh validation and approval. The loader recognizes `ASM_SETUP_CSV_METADATA.xml`, retains valid ZIP bytes/basename, and owns the FSM initiation payload. Do not call an FSM import API directly, rewrite its envelope, convert the ZIP to HDL, or use `businessObject` as a ledger-set REST endpoint.
6. After the user requests results/status, use the loader's declared status workflow and apply the [mandatory log-review gate](ora-resource/ora_error_handling.md#mandatory-log-review-before-outcome-reporting) before quoting success or failure. Missing or inconsistent logs leave the import outcome unconfirmed; status summaries alone are provisional. Reconcile its loaded/failed counts with the reviewed FSM ProcessLog and, on failure, the available detailed results reports; a failed parent can also cause its child object to fail, so object counts are not a count of distinct business errors. Submission is not completion. For a requested end-to-end verification, explicitly include status/results in the execution scope, run the applicable declared GETs and acquire a current re-export or output of an already declared FSCR report adapter when required. Compare the requested final header and direct/effective membership. Missing framework evidence remains a reported verification gap; never open the UI or replay a mutation to close it.

## Controlled Import Patterns

The success and round-trip observations below are historical reports; their target releases and qualification receipts are not recorded in this reusable package and have not been independently verified here. Treat them as preparation examples, not proof of qualification for another release, tenant, ledger family or field combination. Apply all current template, reference, relationship, classification and persisted-state checks; historical receipts are not a runtime prerequisite.

| Pattern | Package and validation guidance |
|---|---|
| Single-category create | A set may have only a primary, only an eligible secondary, or only a reporting-currency ledger. Resolve the related primary ledger for structural evidence even when it is not a direct member. |
| Multiple direct members on create | One parent row can have multiple child assignment rows, including compatible primary/secondary or primary/reporting combinations. Validate every member and the final graph; do not assume all members share currency when Classification is None. |
| Classified and nested create | Currency-specific and GAAP-view examples succeeded with eligible members. For a nested assignment, match the nested set's classification to the parent as well as validating effective-leaf currency and shared accounting structure. |
| Header update | Description and an eligible Default Ledger can be supplied in an update package while preserving the existing identity, classification, structure and assignments. A blank default on create is valid; adding it later is an update. |
| Assignment addition | Add a newly eligible direct ledger to an existing set by retaining the original parent business key and existing assignment rows, then including the new child row. Re-export or otherwise inspect the current baseline first and verify that no old member disappeared. |
| Field-length boundaries | A 30-character Name with an independently checked explicit 20-character ShortName has been accepted on create. A separate create accepted a 240-character Description. These are separate field limits; a long Name still needs a distinct ShortName. |
| Description serialization | A Description update containing a comma, double quotes and a newline has survived import and re-export. Use a CSV writer/parser and preserve the exact logical value; do not split records on physical lines or remove characters to avoid quoting. |

Each accepted import still requires Data Loader status, FSM ProcessLog and persisted-state verification. A successful object count by itself does not establish every requested field or relationship.

## Qualification Boundaries

Keep reusable preparation rules separate from project test evidence. Runtime uses fresh declared sources, not test names, archive contents, request IDs or previous runs. A passed combination qualifies that behavior under its checked contract; it does not prove every field is individually necessary or automatically defaulted by Oracle.

| Evidence or operation | Interpretation and remaining limit |
|---|---|
| Negative pre-import checks | Assisted evaluation of compiled task rules can establish an FSCR rejection. Report it separately from an automated check or Oracle server rejection; do not submit an invalid package to reproduce a local blocker. |
| Multiple invalid properties | Report every observed violation, but do not claim isolated coverage of one restriction when another incompatibility also blocks the request. GAAP family/level eligibility requires its own current evidence. |
| Minimal Name/member request | The declared COA resolver can resolve an omitted chart from the common member ChartOfAccountsId. The calendar resolver still requires an exact selected display name; request that missing selection without equating PeriodSetName to UserPeriodSetName. Fully automatic Name/member-only creation remains unqualified. |
| DFF | A missing-metadata rejection does not qualify valid segment writes or invalid value-set rejection. Both require a declared deployed mapping and value-set source. |
| Ambiguous identities | Retain the fail-closed lookup contract; absence of a naturally ambiguous fixture does not establish live ambiguity coverage. |
| Removal, clearing, rename, assignment dates/status | Create, review and Description-update success do not qualify these operations. Require the operation-specific contract described in Runtime Evidence Requirements. Existing-set deletion remains prohibited. |

## Creation without a Full Ledger-Set Data Export

Collect Name and at least one direct member in the selected project/environment. Accept an explicit Chart of Accounts or resolve the common member chart through the declared COA resolver. Obtain the exact selected Accounting Calendar display name when missing; the current calendar contract does not qualify automatic display-name derivation. Offer Description, Classification, Default Ledger and deployed DFF values; Currency is required for Currency-specific or GAAP view. ShortName is an advanced choice only when Name exceeds 20 characters or its independent precheck finds a conflict. Do not ask for internal codes, a qualification profile, ledger accounting flags, timestamps or a full export.

| Stage | Framework action | Required evidence |
|---|---|---|
| Template | Obtain or validate the designated current task template/spec, both CSV headers and ASM metadata. | Exact task/environment/release and current schema compatibility; template cells do not supply runtime defaults. |
| Identity | Run both declared Name queries and the independent ShortName query; derive AccessSetName from the new Name. | Fresh completed negative prechecks, no observed L/S conflict and queried-scope disclosure. |
| References | Resolve the selected members, COA, calendar, period type, conditional currency and balancing column. | Fresh outputs from the declared resolvers with exact identity and structural compatibility. |
| Structure | Acquire the resolved primary ledger's scoped Manage Primary Ledgers export and extract only allowlisted structural keys/segment values. | Exact primary identity and selected structure/calendar agreement; balancing pair cross-check and explicit management-field dispositions. A COA export is conditional on a named required gap. |
| Initialization | Explicitly apply the 27 packaged header values in ora_defaulting_rules.md. | Built-in MLS_FSM_CREATE_V1 and compatible current fields/types; no external qualification receipt or automatic-default claim. |
| Omissions and DFF | Apply the named blank-cell rules, including display descriptors; apply current DFF requiredness/requested values. | Each current column classified; known required-value or metadata differences block. Descriptor omission is disclosed, not claimed as individually proven Oracle defaulting. |
| Candidate | Write one new GL_LEDGER_SET_DEF row and one ORA_GL_LEDGER_SET_ASSIGN row per intended direct member into the current template carrier. | Correct parent keys, independently resolved L/S member types, preserved XML and no unrelated setup rows. |
| Handoff | Run shared validation and the compiled Task Hook, then use core.data-loader's immutable preview, approval and submission. | All applicable runtime gates passed and the final archive digest bound to approval. |
| Result | On requested status/results, inspect detailed diagnostics and verify persisted requested fields and direct/effective membership through the selected read-only route. | Core process outcome plus field-specific state evidence; a lookup returning only the new Name is not complete verification. |

This is a fresh-input creation route: user business choices, packaged ledger-set rules, current template shape, fresh lookup checks and a primary-ledger-scoped structural export. A separate COA export is not a standard creation prerequisite; invoke it only for a named required structural gap, never merely because a new chart or project has no prior profile. Do not inspect another project's runs, test archives or session logs. Missing history is not a blocker. A stricter tenant-wide duplicate policy is conditional on an explicit user/project requirement and a selected authorized evidence source; normal preparation records the scope of the declared GETs. Actual metadata/access errors, observed duplicates, incompatible members and unsupported requested operations remain blockers. Oracle acceptance and persisted verification are separate from preparation readiness.

## Business Operation Coverage through FSCR

| Operation | Framework checks | Framework action |
|---|---|---|
| Find/review | Resolve exact identity through the declared GETs; obtain a current task baseline for requested fields/membership not exposed by those GETs. | Return endpoint/export-based findings; no import. |
| Create | Validate Name, optional Description/Classification, shared chart/calendar, conditional currency and nonempty membership. | Prepare one GL_LEDGER_SET_DEF parent and explicit assignment rows, then use Data Loader. |
| Add members | Resolve exact member names and L/S types; validate compatibility, classification and nested graph. | Retain current rows on update and include the intended new assignments. |
| Default Ledger | Validate the requested eligible ledger against final assigned membership using declared endpoint/export facts. | Populate DefaultLedgerName only when supported; a requested later change is a separately validated update. |
| DFF | Require current deployed mappings, requiredness, types and value sets from a declared FSCR metadata source. | Populate only requested/required mapped segments; missing framework metadata blocks the affected change. |
| Submit | Shared validation and Task Hook bind the intended package to immutable bytes. | Data Loader owns approval, upload, initiation, status and process diagnostics. |
| Update | Acquire the current persisted baseline and establish supported import semantics for each requested change. Classification is preserved after assignments exist. | Apply only the supported explicit delta and verify through GETs/current re-export. |
| Delete existing set | Prohibited under Existing Ledger Set Preservation. | Return ledger_set_deletion_prohibited; no alternate executor. |
| Remove assignment | Require proven explicit import removal semantics, an eligible remaining default and nonempty final membership. | Preserve the parent set; omission alone is not deletion. |
| Cancel preparation | Determine whether submission occurred through the loader's recorded handoff/status. | Stop before submission; after submission reconcile the existing process instead of deleting or replaying it. |

## FSM Package Mapping

Resolve the task's FSM parent and assignment business objects using the following mappings. Validate member names, XML paths, ordered headers, types and metadata against the selected environment's current task template before preparing a package; do not fix column counts or infer import behavior from sample rows.

| Member | Business object / XML path | Key and handling |
|---|---|---|
| GL_LEDGER_SET_DEF.csv | GL_LEDGER_SET_DEF; /LedgerSetVO/LedgerSetVORow | Parent Name is the ledger-set business key. Preserve current exported sequence, ordered headers and types. |
| ORA_GL_LEDGER_SET_ASSIGN.csv | ORA_GL_LEDGER_SET_ASSIGN; /LedgerSetVO/LedgerSetVORow/LedgerSetNormAssignVO/LedgerSetNormAssignVORow | Child GL_LEDGER_SET_DEF.Name points to parent Name; LedgerName and ObjectTypeCode identify direct assignments. Preserve current exported sequence, ordered headers and types. |
| ASM_SETUP_CSV_METADATA.xml | TASK_CSV export metadata; ObjectShortName GL_MANAGE_LEDGER_SETS | Preserve XML business-object paths, attribute/type lists, sequence and supported metadata. Do not hand-create undocumented import control flags or scope keys. |

| User business value | FSM field(s) | Mapping boundary |
|---|---|---|
| Name / Description | Name / Description | Check duplicate names across L and S; preserve omitted update values. Rename additionally needs proven import identification semantics and coordinated child keys. |
| Chart of Accounts | KeyFlexfieldCode / StructureInstanceCode | Resolve actual same-release instance code. Use ChartOfAccountsId for compatibility evidence; never add it as a CSV column unless the current template declares it. |
| Accounting Calendar | PeriodSetName / UserPeriodSetName | Resolve internal versus display names explicitly; do not infer AccountedPeriodType from calendar text or invent an absent column. |
| Classification | LedgerSetClassificationCode | Blank, ORA_GL_CURRENCY_SPECIFIC, or ORA_GL_GAAP_VIEW; preserve on update. |
| Classified Currency | LedgerSetCurrencyCode | Store the selected monetary code here; legacy CurrencyCode uses the packaged initialization value. |
| Default Ledger | DefaultLedgerName | Exact eligible assigned member; preserve unless explicitly changed. |
| Header DFF | AttributeCategory, Attribute1 through Attribute15, AttributeNumber1 through AttributeNumber5, AttributeDate1 through AttributeDate5 | Only explicitly mapped deployed segments; type/length/value-set checks precede writing. |
| Direct membership | Child GL_LEDGER_SET_DEF.Name, LedgerName, ObjectTypeCode | L for ledger, S for nested ledger set; compare direct and flattened representations separately. |
| Assignment dates/status/DFF | Child StartDate, EndDate, StatusCode, AttributeCategory, Attribute1 through Attribute15 | Require supported current import semantics and declared deployed metadata; the presence of a CSV attribute alone does not prove write support. |
| FSM identities and internal fields | ShortName, AccessSetName, who-columns and other technical values | Apply the independent short-name precheck, packaged new-name derivations, initialization and omission rules; never transplant another object's identity or timestamps. |

For create, author one new parent and explicit direct-member rows using the current template, packaged initialization/omission rules and fresh allowlisted scoped structural values. For ordinary update, retain the exact original business key and change only supported requested fields; preserve all nonrequested member relationships. A CSV natural-key name change may create a second object instead of renaming the first, so block an automated rename until stable-ID matching or same-release import behavior is demonstrated. Similarly, require a proven explicit import contract for removal, field clearing and assignment dates/status. Do not infer these operations from a populated export alone.

## Verification through Declared Endpoints and FSCR Exports

After confirmed Data Loader completion, resolve the saved exact set through the applicable declared GETs and compare the returned identity/structure facts. Use a fresh task re-export for saved Name, Description, Classification, Currency, structure/calendar, Default Ledger, requested DFF values and direct assignment rows not all exposed by the lookup endpoints. Compare each direct member and its L/S type; recursively expand nested sets from current framework-acquired evidence and validate leaf compatibility. HTTP success, initiation and object counts alone are insufficient.

Parse verification CSVs as logical records and select the exact parent and its keyed assignment rows, regardless of row order or unrelated sets in the export. For update, compare all nonrequested non-audit header fields and the complete retained direct membership against the fresh pre-update baseline. Compare requested string values after CSV decoding, including embedded punctuation and newlines. Record generated audit/locking changes separately. A new post-update export is required to verify the final update; an earlier post-create export proves only the earlier state.

The following Oracle tables explain the data model; they do not authorize direct database access or supply an undeclared reporting endpoint. GL table evidence may be consumed only from an already configured, declared FSCR machine-readable report adapter. Without such a route use the declared endpoints/current task exports, or disclose the exact unresolved verification fact.

| Table | Evidence Meaning |
|---|---|
| GL_LEDGERS | Stable ledger/set identity, Name/ShortName, ObjectTypeCode, header structure, classification/currency and default identity. |
| GL_LEDGER_SET_NORM_ASSIGN | Direct set/member relationships, including nested sets. FSM assignment rows represent this direct graph. |
| GL_LEDGER_SET_ASSIGNMENTS | Effective flattened membership. Expansion from current task exports must be distinguished from an independently reported flattened-table result. |
| GL_LEDGER_RELATIONSHIPS | Primary family, source/target categories, relationship status and eligible conversion level where supported metadata provides it. |

Inspect all available dated/status rows before deriving active membership; do not guess a status code. Require the direct graph to match the approved assignments and its leaf expansion to match the intended effective members. Verify changed header/DFF values separately. Keep generated optimistic-lock versions as evidence, not imported business input. If independent flattened-table or deployed-DFF verification is requested and no declared framework source provides it, report that limit; never substitute UI inspection or ad hoc SQL.

## Runtime Evidence Requirements

Check current import field/type contracts, supported change semantics and conditional requiredness through current task metadata and declared framework evidence. Resolve feature availability and GAAP eligible conversion levels, recursively validate nested membership, and obtain deployed DFF mappings before preparing affected changes. Do not inspect UI visibility, editability or controls as a runtime check.

Require a supported same-release import contract for assignment removal, field clearing, rename and generated-field changes beyond the packaged creation rules. Establish those operation-specific contracts through authoritative task metadata or an explicitly approved controlled import/re-export verification. Do not apply this update-operation gate to ordinary creation under MLS_FSM_CREATE_V1. Export shape alone does not prove write behavior; preparation readiness does not replace Oracle acceptance or persisted verification. Store current execution evidence separately from reusable guidance.

## Sources

- [GL_LEDGERS, 26C](https://docs.oracle.com/en/cloud/saas/financials/26c/oedmf/glledgers-28674.html): header schema, lengths and classification codes.
- [Ledger Set Classifications, 26C](https://docs.oracle.com/en/cloud/saas/financials/26c/faigl/ledger-set-classifications.html): classification and assignment restriction.
- [Feature introduction](https://docs.oracle.com/en/cloud/saas/readiness/erp/24d/fins24d/24D-fin-wn-f34529.htm): conditional Currency and adjustment-only secondary examples. Prefer current-release documentation and declared metadata when this older wording is stricter; this source does not permit runtime UI inspection.
- [Ledger/ledger-set LOV, 26C](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-dataaccesssetledgerslov-get.html): read-only identity/structure fields and paging.
- [Ledgers LOV, 26B](https://docs.oracle.com/en/cloud/saas/financials/26b/farfa/op-ledgerslov-get.html): read-only member currency/structure contract; verify target-release metadata before use.
- [Currencies LOV, Common Features 26C](https://docs.oracle.com/en/cloud/saas/applications-common/26c/farca/op-http-servername-fscmrestapi-resources-11.13.18.05-currencieslov-get.html): exact currency code, enabled/monetary flags and active dates for the read-only classification-currency resolver.
- [Ledger-set assignments, 26A](https://docs.oracle.com/en/cloud/saas/financials/26a/oedmf/glledgersetassignments-6152.html), [normalized assignments, 25D](https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/glledgersetnormassign-14127.html), and [ledger relationships, 26A](https://docs.oracle.com/en/cloud/saas/financials/26a/oedmf/glledgerrelationships-6344.html): separately authorized reporting evidence; confirm the selected release's schema.
- [Examples of ledger sets, 26B](https://docs.oracle.com/en/cloud/saas/financials/26b/faigl/examples-of-ledger-sets.html): shared chart, calendar and period-type compatibility.
- [Financials REST endpoint index, 26C](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/rest-endpoints.html): consult the selected release's operation contracts. Declared lookup endpoints are read-only; task writes use core.data-loader.

## Recovery, Failure and Review Discipline

Pillar reviewers are the ERP financials owners and FSCR QA. Preflight exact task identity, environment, privileges, source/candidate shape, dependency evidence, intended operation, immutable digest and the selected executor's approval. Use the failure classes and bounded read retries in ora_error_handling.md; core owns export/load wait limits and process diagnostics. On timeout report last status and known process/request ID, then reconcile that process before any new submission. No automatic mutation retry, destructive reset or implicit rollback is allowed. Preserve safe partial results, redact credentials and sensitive payloads, and keep customer/runtime artifacts outside reusable tracked guidance under the active project policy or the core executor's authoritative persistence rules.


## Endpoint-Only Runtime Verification

This skill and every delegate must never access Fusion setup UI for discovery, duplicate checks, validation, review, configuration or result verification. Do not navigate task pages, inspect browser DOM/network state, operate controls, scrape grids, take screenshots or ask the user for UI evidence as a verification workaround. Screenshots and manually transcribed UI values are not authoritative runtime verification evidence.

Use only the declared FSCR core read clients and endpoint-backed status/diagnostic workflows for runtime checks. Complete exact-match lookup pagination and match the selected environment and identity. Inspect actual responses; failed, partial or unauthorized reads cannot prove absence, equality or success. Templates and approved framework artifacts retain their existing operation-specific source rules; packaged business rules explain accepted inputs but do not prove current saved state. Missing required endpoint facts are exact evidence gaps, not permission to invent an API, inspect UI or claim an unverified value. Qualified omission/first-submission profiles retain their stated limits and must not be represented as endpoint proof of global duplicate absence.

Authentication is the sole browser handoff: core.auth may open login for the user to complete. The agent must not inspect or operate the login, read credentials or navigate onward to task pages. Historical UI research retained as generic packaged knowledge never requires fresh runtime UI access.

Before quoting any result, apply the mandatory log-review and result-evidence rules in [error handling](ora-resource/ora_error_handling.md#mandatory-log-review-before-outcome-reporting). Submitted FSM imports require the actual matching process logs; lookups, native REST actions, validation and no-op results require their own actual response/diagnostic or evaluated-rule evidence. Do not invent an FSM log for an unsubmitted request or read-only action.
