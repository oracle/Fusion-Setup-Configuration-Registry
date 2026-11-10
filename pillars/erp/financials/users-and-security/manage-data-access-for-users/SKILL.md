---
skill_id: "erp.financials.users-and-security.manage-data-access-for-users"
name: "Manage Data Access for Users Setup Task Guidance"
description: "Selects the MDA method, validates assignment intent, and delegates FSM and registered REST-mode mutation artifacts to core.data-loader. Supports direct REST reads and later Data Loader status and assignment verification."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Users and Security"
functional_area_code: "ORA_ASK_USERS_AND_SECURITY"
task_code: "ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS"
task_name: "Manage Data Access for Users"
parent_skill_id: "erp.financials.users-and-security"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "ERP financials pillar team"
version: "0.18.3"
inputs:
  - "operation"
  - "action"
  - "assignment_records_or_filters"
  - "rest_read_options"
  - "requested_effective_dates"
  - "route"
  - "setup_data_artifacts"
  - "rest_loader_business_object"
  - "data_loader_request_id_or_ucm_content_id"
  - "execution_approval"
outputs:
  - "normalized_assignment_specification"
  - "mda_validation_result"
  - "role_object_mapping_decision"
  - "route_recommendation"
  - "route_handoff_requirements"
  - "template_only_archive_and_extracted_package"
  - "immutable_execution_preview"
  - "execution_result"
  - "rest_operation_plan"
  - "assignment_list"
  - "rest_read_result"
  - "assignment_verification_result"
  - "rest_loader_contract_evidence"
  - "data_loader_artifact_or_preview"
  - "data_load_submission_receipt"
  - "data_load_status"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.fusion-api.rest-api-client"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.rest-api-client"
  - "core.data-loader"
persists_project_state: true
state_updates:
  - "validation_results"
  - "reports"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/users-and-security/manage-data-access-for-users/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "report"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/users-and-security/manage-data-access-for-users/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
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
oracle_supplied_guidance_files:
  - purpose: "Input requirements and ordered task validation"
    location: "ora-resource/ora_input_validation.md"
  - purpose: "Task-local dependency readiness"
    location: "ora-resource/ora_dependency_readiness.md"
  - purpose: "Source-backed defaults"
    location: "ora-resource/ora_defaulting_rules.md"
  - purpose: "MDA design invariants"
    location: "ora-resource/ora_design_enforcement.md"
  - purpose: "MDA failure interpretation"
    location: "ora-resource/ora_error_handling.md"
  - purpose: "Common mutation identity/context lookups, FSM mapping/date resolvers, and REST read, reconciliation, and verification contracts"
    location: "ora-resource/ora_reference_lookups.md"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "May perform active-workflow-selected, read-only Fusion lookups through core.fusion-api.rest-api-client."
  - "May obtain a data-bearing exact-task export through shared.setup-export.task-level-export for FSM export/list requests or FSM Revoke original-date resolution."
  - "Downloads and extracts an exact-task Template Only FSM package through shared.setup-export.task-level-export for FSM mutation preparation."
  - "May hand off validated FSM packages to core.data-loader for import under its own preview and approval workflow."
  - "May read dataSecurities for selected REST List/search, assignment Get, Count, reconciliation, and verification."
  - "May generate registered REST Data Loader samples and prepare assignment artifacts through core.data-loader."
  - "May submit REST-mode assignment create/reactivate/deactivate artifacts through core.data-loader under its approval workflow; processing is asynchronous. Creation may also create a missing role/context mapping."
  - "May request Data Loader status and diagnostics, and verify assignment state after terminal success, only on a later explicit status/results/verification request."
required_privileges:
  - "Read access to userAccounts, rolesLOV, and userAccountRoles for mutation identity and membership lookups."
  - "Read access to dataSecurities for REST customer reads, reconciliation, and verification."
  - "For REST mutations, access to the selected registered Data Loader business object, metadata/templates, UCM upload, initiation, and underlying assignment create/update operations. For loader follow-ups, access to the requested status/diagnostics."
  - "Task export and import privileges required by shared.setup-export.task-level-export and core.data-loader for the selected FSM operation."
---

# Manage Data Access for Users Setup Task Guidance

## Purpose

Provide task rules for ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS through FSM and REST operations. Classify request intent and select the method through the central policy before method-specific input checks. Common mutation validation precedes the selected method's mutation prerequisites and execution contract.

FSM prepares an exact-task Template Only-derived package. REST reconciles assignments and prepares a registered REST-mode Data Loader artifact. Both delegate mutation validation, immutable preview, approval, upload, initiation, and job diagnostics to core.data-loader. The shared REST client performs only declared read-only lookups, customer reads, and assignment verification for MDA.

## Supported Scope

- Direct user assignments: Grant, Revoke, activate, reactivate, and deactivate.
- FSM package preparation and data-bearing task export/list.
- REST-mode asynchronous Grant/Revoke through Data Loader, plus List/search, Count, and Get through the documented dataSecurities GET contracts. Collection completeness is reported separately from rows observed by a finder-free GET.
- Later explicit Data Loader status, progress, results, errors, or verification requests using the accepted submission reference.
- Mixed Grant/Revoke rows for different assignments in one selected method and environment.

Provisioning-rule creation or maintenance remains outside this skill. Both provisioning-rule CSV members remain header-only in generated FSM mutation packages.

## Resolved Task Scope

When the user explicitly selects this skill, its manifest is the authoritative
scope for every MDA operation: ERP / Financials / Users and Security,
`ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS`. Do not ask the user to select,
reconfirm, or repeat the offering or functional area. The same task name may
occur elsewhere in the catalog, but that does not make this selected skill
ambiguous. Ask about offering scope only if the user explicitly requests a
different offering or the request contradicts this skill's declared scope.

## Common Section

Use the environment/properties context established by the invoking workflow and shared core services, including any explicit override, consistently for all MDA operations.

Before asking for input, reuse supplied and retained facts through the catalogs,
local resolvers, and environment configuration declared for the current workflow
stage. Preserve supplied business values. Ask only for a required fact that
remains missing, ambiguous, or conflicting. When classifying a mutation outcome,
apply the selected method's decision rules to the requested action and the
evidence those rules require. Report a no-op only when those rules select it,
naming the action and observed state that justified it.

### Method and Operation Selection

At MDA.CLASSIFY_REQUEST, distinguish a new assignment request from a later loader status/results/verification request under ora_input_validation.md. A loader follow-up reaches MDA.LOADER_STATUS_READY without mutation preparation. For assignment requests, at MDA.SELECT_METHOD load and apply the
[Method Selection Policy](ora-resource/ora_input_validation.md#method-selection-policy).
That section alone owns the routing algorithm, threshold, read default, and
selection-lifetime rules. Apply only the selected method and operation's input
checks before live lookups. Explicit and derived selections enter identical
field derivation, validation, and execution paths. A failed prerequisite does
not authorize switching methods.

REST requests an unscheduled assignment-state change, executed asynchronously by Data Loader; it does not promise immediate completion. Do not ask for or send start dates, end dates, or original assignment dates. If the user explicitly requests scheduled or date-limited access, explain that this REST workflow cannot fulfill that instruction and obtain their method selection before proceeding. Do not discard date intent or silently choose FSM.

The manifest's dataloader_import_mode remains the existing FSM default, not a selector for this dual-method workflow. businessObject remains blank until a loader discriminator is verified; the resource name dataSecurities alone is not registration evidence. Resolve the REST business object under the REST Loader Contract below and pass that exact discriminator explicitly to core.data-loader. Never use a combined FSM/REST manifest enum. The retained selected_method controls each handoff; read-only user/role/membership lookups do not change it.

| Selected method and operation      | Required input group at intake                                                  | Next workflow                                                           |
| ---------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Selected FSM Grant/Revoke          | Common mutation identity/context values plus applicable FSM date intent         | FSM mapping, Template Only package, Data Loader handoff                 |
| Selected REST Grant/Revoke         | Common mutation identity/context values plus unscheduled-state intent; no dates | Reconciliation, registered REST loader artifact, Data Loader handoff    |
| Selected FSM export/list           | Selected task export scope; no mutation fields                                  | Data-bearing exact-task export                                          |
| Selected REST List/Get/Count       | Applicable REST read scope and options; no mutation fields                      | Selected REST read resolver                                             |
| Loader status/results/verification | Request ID or UCM Content ID, environment, and applicable submission evidence   | Data Loader status; assignment verification only after terminal success |

### Common Grant/Revoke Validation

Require explicit per-row action, target username, role display name or code, supported context label/alias, and every ordered value.

At MDA.VALIDATE_INPUT, apply resolve_mutation_context_label from ora-resource/ora_reference_lookups.md before declaring a mutation context missing or unsupported or asking for clarification. A uniquely resolved approved alias satisfies the explicit-context requirement. Retain the resolution record in the normalized assignment specification.

For each mutation row, resolve one eligible active user, one eligible active non-data role, and membership in that exact role. Then consume the intake context resolution and bind its required ordered values. Follow the owning resource contracts; never guess identities or derive context from a value.

Customer reads/export follow their own scope checks and skip mutation-only eligibility, membership, date, and package requirements. Environment, authentication, and the caller's applicable read access remain required.

### Context-Value Handling and Future Validation

Preserve exact supplied values. In this version, existence/eligibility validation of context values is not enabled; ContextValueHandlingStatus=not_prevalidated describes current behavior, not a permanent restriction on future versions.

Only documented FSM Revoke date matching and REST reconciliation/verification compare assignments. They do not authorize value substitution or a separate context-value LOV lookup.

The assignment method is independent of a future validation source. Future context-specific validators may use explicitly approved FSM extracts or REST APIs after their resolver, applicability, readiness, and error contracts are authored. No additional validation source or fallback is enabled by this extension point. An extract of current assignments alone does not prove that an unassigned context value is invalid.

### Batch Handling

Retain per-row action, canonical identity, ordered values, and applicable date intent. Collapse identical requests and reject conflicting intents without discarding FSM date distinctions.

All requested rows must pass applicable checks before either mutation handoff. For REST, retain no-op rows as outcomes but exclude them from the loader artifact; an all-no-op request creates no sample or load. Do not infer FSM no-ops or change its package rules. Do not silently submit a subset; reduced scope requires explicit selection and a fresh preview. Neither loader method is assumed atomic or ordered by input row. Reject conflicting desired states for the same assignment; do not split a dependent sequence into concurrent records.

The task graph evaluates all applicable rows before advancing each shared stage. A row failure blocks aggregate readiness. Different user/role scopes receive independent reconciliation.

### Resource Routing and Graph Boundary

Load the task-node execution guide declared by the planner, the selected registry and plan, and each reached source section. Do not execute a stale, incomplete, or inconsistent graph.

| Resource                                 | Responsibility                                                         |
| ---------------------------------------- | ---------------------------------------------------------------------- |
| ora-resource/ora_input_validation.md     | Input shape, operation/method selection, and context-value positions   |
| ora-resource/ora_reference_lookups.md    | All lookup mechanics, one context table, FSM resolvers, and REST reads |
| ora-resource/ora_dependency_readiness.md | Selected-route dependencies and aggregate readiness                    |
| ora-resource/ora_defaulting_rules.md     | Common and method-specific defaults                                    |
| ora-resource/ora_design_enforcement.md   | Mandatory policy, method boundaries, and blocking conditions           |
| ora-resource/ora_error_handling.md       | Gates, task-specific failures, safe disclosure, and recovery           |

Registry terminals return readiness or completed read/no-op outcomes only. A terminal does not invoke another skill or write. This SKILL.md owns the FSM import/export handoffs, REST artifact preparation, and loader-status handoff below. MDA.REST_PREPARE_READY returns planning readiness to prepare the loader artifact; MDA.REST_READY returns final-artifact validation to the calling Data Loader Task Hook, never another submission.

## FSM Method

### Method Instructions

Use shared.setup-export.task-level-export for exact-task Template/data exports and core.data-loader for import. FSM retains its effective-date and portable CSV identity rules; it does not use dataSecurities reconciliation.

### Common for Grant and Revoke

After common mutation validation, resolve the local RoleCode/ObjectName mapping decision, applicable dates, and the exact-task Template package. The local catalog is an FSM packaging reference. Follow the portable locator, package members/headers, USER_DEFINED, and carrier rules in ora-resource/ora_design_enforcement.md, and mapping-row construction in ora-resource/ora_reference_lookups.md.

### Grant

- Set ActiveFlag=Y through the FSM defaults.
- Preserve valid explicit dates; apply documented defaults only when omitted.
- Include one deduplicated user-defined mapping row per unlisted RoleCode/ObjectName pair. Keep mapping rows absent for listed pairs.
- Never ask the Revoke original-date question or run its resolver.

### Revoke

- Require this row's valid original StartDateActive and source.
- A valid supplied original date requires no export.
- Follow the FSM Revoke intake rule for a missing date; explicitly unknown dates are resolved by resolve_active_revoke_assignment at MDA.CHECK_DEPENDENCIES after common checks.
- Preserve unknown_confirmed across failures; do not repeat the date question.
- Set ActiveFlag=N; preserve a valid explicit end date.
- Never default or borrow the original date; do not create a mapping solely to revoke.
- The selected MDA task and Financials / Users and Security metadata identify the lookup scope; do not ask the user to select an offering.
- Derived dates require a completed, validated data ZIP and receipt. A pending process or log does not establish a date.

### Template Only Acquisition and Extraction

For every FSM mutation, obtain the package before creating or filling any row:

1. Invoke `shared.setup-export.task-level-export` for task code `ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS` with explicit `--template-only`. Never use `--data` as the mutation-package baseline; it is permitted only for the separately declared Revoke start-date lookup.
2. Require the exporter to use `setupTaskCSVTemplateExports`, poll the returned Template process, and download its `FileContent` ZIP. This Template Only acquisition step must not call `setupTaskCSVExports`; the separate Revoke lookup uses the shared exporter's data mode.
3. Verify that the download is a ZIP, then extract it immediately into a new, empty, request-scoped folder under the selected project workspace. Refuse an existing nonempty extraction target instead of overwriting it.
4. Validate the extracted metadata, four expected CSV members, and exact ordered headers before row construction. Preserve the downloaded ZIP and extracted source unchanged as provenance.
5. Copy the validated extracted files to a separate working package. Populate `ORA_FUN_ALL_USER_DATA_ACCESS.csv` for every validated requested assignment. Populate `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` only for deduplicated unlisted Grant/reactivation pairs. Keep both provisioning-rule CSV files header-only.

Use the shared exporter rather than implementing task-local REST or polling logic. A previously downloaded archive is reusable only when it is proven to be a Template Only export for the same environment and exact task, its ZIP and member contract still validate, and its immutable provenance is retained; otherwise download a fresh Template Only package.

For Revoke rows with an explicitly unknown original start date, the shared
exporter may obtain data as lookup evidence only. Use explicit `--data`;
follow the receipt, exact-match, and resume contract in
`ora-resource/ora_reference_lookups.md`. Never use that data ZIP as a mutation
baseline. Pending or failed lookup attempts retain each affected row's
`unknown_confirmed` state and block the handoff under
`ora-resource/ora_error_handling.md`; they do not trigger another date question.

### Export/List

After MDA.FSM_EXPORT_READY, use shared.setup-export.task-level-export in data mode for the selected task, requested scope, and environment. Follow its own execution, polling, download, and evidence requirements. This handoff is explicitly selected by the MDA workflow.

Do not require mutation rows, original Revoke dates, or a Template Only package for a user-facing export/list. A data export does not become a mutation-package baseline.

### Data Loader Handoff

After MDA.HANDOFF_READY, hand the exact validated Template-derived package and validation evidence to core.data-loader. That skill owns immutable-artifact handling, preview, approval, submission, and requested status checks. Do not add a second task-local approval or demand a standalone approve keyword.

Include the retained method-selection evidence with the normalized request. Any
Task Hook re-entry uses that same FSM selection under Method Selection Policy;
it must not treat the prepared package as a new omitted-method request.

Readiness is not import success. Report execution only from returned executor evidence. Follow Data Loader recovery rules; do not independently retry imports or switch methods.

## REST Method

### Method Instructions

For selected REST mutations, use the registered business-object workflow in core.data-loader. MDA must not call assignment POST/PATCH directly, including through the shared REST client. Use core.fusion-api.rest-api-client only for the declared GETs against:

```text
/fscmRestApi/resources/11.13.18.05/dataSecurities
```

Read that client's references/fusion-rest-api.md before invoking its existing scripts/fusion_rest_client.py. Use the selected environment properties, standard Fusion authentication, and authorized token-cache context; do not default to another environment or construct a new transport.

MDA owns assignment rules, lifecycle classification, and semantic verification. Data Loader owns source conversion, final artifact validation, Task Hook, preview, approval, upload, initiation, and job recovery. The readiness graph never hides a Fusion write. No new task-rest adapter, direct REST executor, or ora_rest_execution.md is used.

### Common for Grant and Revoke

After common validation, reconcile all requested rows through resolve_rest_assignment. Require complete pagination, include inactive assignments, and block ambiguity or invalid state. Do not ask for or send dates.

Create and update rows both retain the common active-user, active non-data-role, and exact membership checks. Supporting GETs are read-only validation. Customer read options never limit reconciliation or verification evidence.

Use RoleNameCr for canonical display-role evidence and RoleCommonName for technical-role checks. Bind the exact REST SecurityContext literal and ordered values from the single context table. Map these to fields only when the current loader contract proves the mapping; do not copy FSM/HCM RoleName or assume every GET attribute is writable.

The local mapping catalog is not a REST eligibility gate. Fusion validates the assignment. Creation may create a missing role/context mapping; disclose this possible side effect without promising it or adding mapping/provisioning records to the REST artifact.

### Lifecycle Decision Table

This is the sole operation-selection table; resource gates reference it.

| Exact assignment result                       | Grant                                  | Revoke                                   |
| --------------------------------------------- | -------------------------------------- | ---------------------------------------- |
| No match after complete reconciliation        | Create row with proven POST operation  | No-op                                    |
| One inactive assignment                       | Update row targeting that ID; activate | No-op                                    |
| One active assignment                         | No-op                                  | Update row targeting that ID; deactivate |
| Multiple distinct exact assignments           | Block                                  | Block                                    |
| Incomplete or invalid identity/state evidence | Block                                  | Block                                    |

### REST Loader Contract

For every selected REST Grant or Revoke that needs a write, follow this sequence. The selected method remains REST, but every mutation is submitted through `core.data-loader`; direct `dataSecurities` calls are for the declared GETs only.

1. Reconcile the exact assignment and select create, activate, deactivate, or no-op from the Lifecycle Decision Table. A no-op ends without a loader artifact.
2. At MDA.REST_LOADER_CONTRACT, use resolve_rest_loader_contract in ora_reference_lookups.md and core.data-loader's read-only sample/metadata workflow. Resolve the exact registered object for this task in the selected environment. Use a supplied rest_loader_business_object as a candidate, or `dataSecurities` as a search candidate when omitted. Require one matching registration, its UCM template, current field/key metadata, and the fields needed for the selected lifecycle operation. A similar object name or a successful assignment GET does not establish the loader target.
3. Derive the smallest executable row for that operation from the normalized request, fresh reconciliation, current loader schema, and the documented `dataSecurities` create/update behavior. Do not use a generated example row as the business input. Check the current schema and operation rules on every request.
4. Have core.data-loader convert and validate the source, then validate the final immutable archive at MDA.REST_VALIDATE_ARTIFACT through Task Hook. Compare its actual DAT records to the request and lifecycle decision. Core owns its single exact-artifact preview, approval, upload, initiation, and later status workflow. An accepted initiation is not assignment success; verify terminal processing and fresh assignment state only on the permitted later results/verification request.

Through core.data-loader, resolve one registered object and generate its current editable XLSX, attribute-details workbook, and key-fields workbook together:

```text
python3 -B core/data-loader/scripts/generate_sample_dat.py <exact-business-object-candidate> --output-dir <permitted-project-artifact-directory> [--properties <explicit-environment-override>]
```

Use the existing core workflow and its authorized authentication context; do not run this command during skill authoring or invent a metadata client. Sample generation is read-only schema evidence, not submission or proof of business success. When the exact registered template exposes `RestAction` and the operation's required fields/keys, use the core Data Loader action contract and Oracle `dataSecurities` operation documentation to proceed to artifact validation. Do not demand a separate published loader action document or a past successful import. Missing or ambiguous registration, absent required fields/keys, conflicting target metadata, or an unsafe final artifact blocks this REST route. Do not switch methods or write directly.

For `dataSecurities.UserRoleDataAssignmentId`, distinguish schema requiredness from create input. Oracle's documented POST omits this server-generated ID and returns it. The attribute-details workbook may mark it required and the editable sample may contain a placeholder; neither makes it a create input. Do not block solely on that flag or copy the placeholder. Apply the same live-schema and final-artifact checks to every create.

### Grant and Revoke Artifact Rules

Build executable rows only from the validated request and complete reconciliation. The generated sample supplies structure, never an assignment baseline. Remove all sample/example rows and unrelated child/DFF rows; leave unused sections header-only. For mixed batches, prove support for each row's operation before preparing one artifact.

| Lifecycle outcome | Required artifact behavior                                                                                                                                                                                                                                                                                                                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Create            | Set `RestAction=POST`; map canonical user, role, exact context, and ordered values to current writable fields. Omit `UserRoleDataAssignmentId`, `ActiveFlag`, generated IDs, dates, audit fields, finder variables, FSM carriers, and Upsert-Mode from the executable record. Oracle documents a generated ID and active-by-default POST for this assignment. A blank field is not equivalent to omission. |
| Reactivate        | For Grant of one inactive exact assignment, set `RestAction=PATCH`, the unique UserRoleDataAssignmentId from fresh complete reconciliation, and the loader representation of active `ActiveFlag`. Omit other assignment attributes so they cannot be changed.                                                                                                                                              |
| Deactivate        | For Revoke of one active exact assignment, set `RestAction=PATCH`, the unique UserRoleDataAssignmentId from fresh complete reconciliation, and the loader representation of inactive `ActiveFlag`. Omit other assignment attributes; do not use DELETE, remove role membership, or create a mapping row.                                                                                                   |
| No-op             | Retain the row outcome outside the load; create no executable row.                                                                                                                                                                                                                                                                                                                                         |

Evaluate the same algorithm for every user, role, context, and assignment age. The live loader attribute type and task mapping determine the PATCH `ActiveFlag` representation; for the registered `dataSecurities` `String(1)` field, use `Y` for active and `N` for inactive unless current metadata declares a conflicting encoding. Required DAT section structure does not count as an extra assignment attribute. An absent or inactive exact assignment on Revoke, or an active exact assignment on Grant, remains a no-op under the lifecycle table.

Do not confuse UserRoleDataAssignmentId with membership UserRoleId or trust an unverified supplied ID. Keep identifier precision and context leading zeroes as text. Do not put JSON booleans into a `String(1)` DAT field or send Rolerf/Userrf as writable fields. If a required loader field cannot be populated without changing unrelated data, block before preview. Do not copy an entire existing assignment to satisfy a template.

Revoke never requests an original date or FSM export. Scheduled/date-limited intent remains unsupported for this REST branch. Core may internally convert XLSX to DAT/ZIP; explicitly requested DAT sources follow the same exact-row rules.

### Preparation and Task Hook Re-entry

Use internal workflow_stage=planning for a new REST mutation. MDA.REST_VALIDATE_ARTIFACT returns needs_preparation to MDA.REST_PREPARE_READY only after the loader contract passes. This SKILL.md then delegates reviewed source preparation, conversion, schema validation, and immutable ZIP preparation to core.data-loader. Supply the exact ERP / Financials / Users and Security task context and resolved business object. The user's Grant/Revoke request is the identified load intent; template generation alone never authorizes upload.

Core calls its existing data-load Task Hook for the final immutable artifact before approval. Use workflow_stage=task_validation and carry the original normalized request, selected_method, method_selection_source, routing_record_count, no-op decisions, environment, current loader schema evidence, and archiveSha256. These are handoff inputs, not facts inferred from the generated workbook. Evaluate MDA.REST_LOADER_CONTRACT and MDA.REST_VALIDATE_ARTIFACT against that request and the actual final archive, then return their ordered rule results through the Task Hook's normal preview contract. Keep identities and payloads out of sanitized task-node records. Missing or mismatched request, method, environment, schema, or artifact evidence blocks the preview; no separate historical-operation receipt is required.

Re-entry evaluates the selected graph against that exact artifact. Reuse the same current metadata/sample evidence; do not regenerate samples, reconstruct a different source, re-count artifact rows for routing, or invoke Data Loader recursively. Read back the prepared archive and compare each executable row with the normalized request: create rows require proven identity/context/value fields, while state-only PATCH rows require only the reconciled assignment ID, PATCH action, and intended ActiveFlag value. Verify the complete identity/context through reconciliation; do not copy those fields into a PATCH record. Confirm no examples, no-op rows, unsupported fields, DELETE directives, or unrelated records survived conversion. Refresh reconciliation only during preapproval validation when evidence is stale; a changed lifecycle decision invalidates the artifact and requires fresh preparation and validation. A missing stage/context or mismatch blocks approval.

MDA.REST_READY now means that Task Hook validation passed for the final archive. Return rule results to the existing core preview workflow. It is neither submission nor assignment success.

The REST artifact checks apply only after the REST branch reaches MDA.REST_LOADER_CONTRACT. They do not apply to FSM Grant or Revoke, FSM mapping and date resolution, FSM package validation, or the FSM Data Loader handoff. Both methods submit only through core.data-loader.

### Read Operations

REST reads support List/search, Get one assignment by UserRoleDataAssignmentId, complete matching collections or requested result windows, and exact or estimated assignment counts.

User, role, security context, and context values are optional search predicates. Do not require missing mutation fields or perform mutation-only active-user, active-role, membership, context-value arity, effective-date, or package checks for customer reads.

rest_read_options may supply output fields, sort fields/directions, starting offset, maximum returned assignments, or count kind, as applicable to the selected read mode. Customer output fields are optional; use the default assignment projection when omitted. Follow ora_input_validation.md and the query, framework, projection, and pagination contracts in ora_reference_lookups.md. Preserve supported LIKE, NOT LIKE, IN, NOT IN, NOT BETWEEN, comparisons, null checks, and grouped AND/OR expressions. Standalone unary NOT is unsupported; reject it before invoking REST.

A successful requested page is not a complete collection. An estimated count is not an exact count. Read results are not FSM configuration-package exports.

### List/Search

Use list_rest_assignments with Read Collection Selection in ora_reference_lookups.md and retain all supplied filters. One user's details use `finder=ManageDataAccessRF;Userrf=<supplied username>` across roles and contexts; do not ask for a role or context. Use `Rolerf` for one exact display role and both finder variables when both identities are fixed. For several exact users sharing one display role, use that role finder with `q=Userrf IN (...)`. For a finite user or role set without one shared finder, complete the applicable finder-bound GETs and merge distinct assignment IDs. Never narrow an OR expression to just one member. Keep remaining predicates in q and verify returned finder-bound identities.

Output fields remain optional. For valid context-only, context-value-only, technical-role-only, pattern, or other scopes without an exhaustive finder plan, execute the documented collection GET with the supplied q, if any, through this selected REST read workflow without inventing mutation inputs or a wildcard finder. Report matching rows as observed; HTTP 200, including an empty result, does not alone establish complete coverage, absence, or an exact count. Do not silently switch methods or claim completeness without independent exhaustive evidence.

Honor requested fields, sorting, offset, and result limits. Without a requested window, retrieve the complete matching collection. An offset without a maximum retrieves the remaining collection from that offset. Keep the finder on every page, advance offsets by raw rows, and collapse consistent duplicate assignment IDs before reporting distinct returned_count. Apply only the selected operation's read defaults.

### Get One Assignment

Use get_rest_assignment for one explicit assignment ID without additional search predicates. Do not ask for username, role, context, or values. Return the assignment or an explicit not-found result.

When an ID is combined with other predicates, use collection search with the ID and every supplied condition. Never silently discard filters.

### Count

Use count_rest_assignments. An ordinary "how many" request means an exact retrieved count. Use an estimated count only when requested or explicitly accepted and clearly label it estimated; never silently replace an exact count with an estimate.

Counts apply to distinct assignment IDs and use the same GET plan as List. Exact counts require complete retrieval of every required finder-bound branch and deduplication after merging. A finder-free response without independent exhaustive evidence cannot provide an exact zero or count; an estimate from overlapping branches must not be summed. Distinct-user or distinct-role counts require separately stated aggregation semantics.

### API Capability and Skill Scope

Customer read options do not change mutation reconciliation or verification requirements. The enabled business changes remain creation, activation, and deactivation through the registered loader; broader API or loader capabilities do not enable general assignment editing.

General assignment editing and Upsert-Mode are not enabled by broader reads. Do not invent DELETE, PUT, child-resource, or expansion operations.

### Preview, Approval, and Submission

Data Loader owns the single immutable-artifact preview and approval gate. Include the business effect, target environment, verified loader object, validated operation/assignment scope, excluded no-op count, and possible creation of missing mappings in its source review. Supply the exact final artifact and Task Hook results. Follow the core helper's authoritative Markdown output; do not add a second MDA approval or expose protected identifiers in that report.

Use core.data-loader's current contextual approval or explicit same-request auto-approval policy for this identified load. A prior direct-REST approval or test receipt covering endpoint/JSON is not approval of the new loader artifact; require authorization that covers its exact content and environment. Readiness, a sample request, customer reads, and verified no-ops do not authorize a mutation.

After approval, core verifies the retained artifact and envelopes and submits those unchanged bytes. MDA must not rerun lookups, change rows, regenerate templates, or silently convert an update to a create in this submission phase. A known changed request/environment or changed/missing approved artifact requires a fresh validation and approval cycle. Assignment state may change while a job waits; approval is not a concurrency lock. Do not promise input order, per-row stop-before-next behavior, atomicity, or exactly-once execution.

Return core.data-loader's complete Data Load In Progress report immediately after accepted initiation. Do not poll, request diagnostics, call verify_rest_assignment, or claim assignment success in the initiation request. Retain the permitted submission reference, artifact fingerprint, selected method, environment, and sanitized scope/receipt references for a later request. Let core manage its execution artifacts; do not copy credentials, protected payloads, assignment IDs, or ETags into task-node records or tracked files.

### Later Loader Status and Assignment Verification

After MDA.LOADER_STATUS_READY, hand the exact Request ID or UCM Content ID and environment to core.data-loader for the requested status/progress/results/errors/verification operation. Do not run mutation identity checks, reselect FSM/REST, regenerate samples, build an archive, or initiate a load. Resolve the request from an unambiguous retained submission reference when available; otherwise request only the missing reference/environment. Plain assignment List/Get/Count requests remain on their existing GET routes.

1. Return pending, unavailable, failed, or partial results with Data Loader's diagnostics; none is assignment success. Do not automatically resubmit, roll back, or run semantic verification of a failed/partial load.
2. A status-only request returns the core status report. For a results or verification request, proceed to assignment readback only after core proves terminal success for the exact bound MDA submission. Require the approved scope and artifact/submission linkage; a Request ID alone cannot reconstruct or prove the intended assignments. Missing linkage permits reporting status but leaves semantic verification unverified.
3. For a successful REST-mode load, call verify_rest_assignment for each submitted tuple and compare the desired state. Resolve created assignment IDs from complete exact-tuple GET evidence; a Data Loader Request ID is not an assignment ID. Preserve no-op outcomes as preflight observations, not newly verified load successes. A successful FSM submission follows its existing task-specific verification/export contract; it does not become a REST-mode mutation.
4. Report processing success separately from verified, mismatch, and unverified assignment results. Readback proves observed assignment state, not effective access through every product page or that this request caused the state.

### Recovery

Follow core.data-loader for upload/initiation authentication, retries, status, and diagnostics. MDA adds no outer write retry, automatic rollback, batch replay, or method fallback. Reconcile accepted/pending/uncertain submissions using their existing references; do not create another job merely because a response or diagnostic was unavailable. A separately requested corrective load must use a fresh current plan, artifact, and approval covering only its selected rows.

## Failure Handling

Classify failures as input validation, catalog mismatch, auth/authz, transport/environment, Fusion API, process timeout, process failed, artifact persistence, or approval blocker. Retain row-level errors, partial successes, and a non-success aggregate status for incomplete/failed work.

Follow the selected executor's timeout and recovery rules. Redact secrets, credentials, tokens, Authorization headers, token caches, sensitive payloads, and unrelated assignment rows. A diagnostic/persistence failure must not trigger another write.

## Source Basis

- Current Oracle Financials REST contract for `dataSecurities`.
- Current Oracle HCM REST contracts for `userAccounts`, `rolesLOV`, and `userAccountRoles`.
- The `ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS` Template, metadata, and CSV header contract.
- The Available Role/Object Mappings table in `ora-resource/ora_reference_lookups.md`, derived from `Security_Context_Mapping_Final.xlsx` RoleCode, ObjectName, and ApplicationId values.
- Reviewed Manage Data Access for Users UI and import mappings for role, context, `ObjectName`, and context carriers.
- Oracle Help behavior for assigning and revoking user data access.

- [Oracle Financials 26C dataSecurities GET](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-datasecurities-get.html).
- [Oracle Financials 26B dataSecurities item GET](https://docs.oracle.com/en/cloud/saas/financials/26b/farfa/op-datasecurities-userroledataassignmentid-get.html); the 26C item page was unavailable during this read-contract review.
- [Oracle ADF REST query/finder literal construction and collection parameters](https://docs.oracle.com/en/middleware/developer-tools/adf/12.2.1.4/develop/consuming-adf-restful-web-services.html).
- [Oracle REST collection query operators](https://docs.oracle.com/en/cloud/saas/project-management/26c/fapap/Collections.html).
- [Oracle Financials REST framework versions](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/Setting_the_REST_Framework_Version.html).
- [Oracle Financials 26C dataSecurities POST](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-datasecurities-post.html).
- [Oracle Financials 26C dataSecurities PATCH](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-datasecurities-userroledataassignmentid-patch.html).

## Output Contract

### Common

Return operation, method-selection evidence, environment, validated scope, readiness, blockers, row outcomes, and aggregate status. For mutations include action/desired state, canonical identities/membership evidence, context, exact values, current ContextValueHandlingStatus, duplicate/conflict decisions, and applicable date intent. Do not require mutation-only output fields for reads.

Retain these method-selection fields in the normalized assignment specification
and mda_validation_result, and carry them through handoff and resume:

- selected_method: FSM or REST.
- method_selection_source: explicit or derived.
- routing_record_count: the original assignment count used for automatic mutation selection; null for reads or when an explicit method required no count.
- method_selection_policy: ora-resource/ora_input_validation.md#method-selection-policy.

Include each mutation row's context_resolution status and mapping-source reference. Keep its supplied label and resolved mapping in runtime state; persist only permitted, sanitized alias-resolution evidence under the existing project redaction rules. Label resolution does not establish context-value existence, eligibility, or effective access.

#### User-Facing Reporting

Apply this contract to every MDA outcome: FSM Grant/Revoke, package
preparation, export/download/extraction, REST List/Get/Count, assignment
creation/reactivation/deactivation, loader follow-up, and verification.

Maintain two distinct outputs:

- Internal handoff/evidence: retain the technical facts required for
  validation, execution, audit, and safe resume.
- User response: explain the business outcome, affected scope, whether
  a change was submitted or verified, and any necessary next action.

Internal Rule IDs, graph paths, resolver names, readiness signals,
fingerprints, and internal field names are not user-facing messages.
Retain them in permitted internal evidence unless technical diagnostics
are requested.

Translate internal statuses into plain language without changing their
meaning. For example:

- Readiness means preparation or validation completed, not submission.
- Accepted submission means processing is in progress, not access granted.
- Processing success does not establish assignment verification.
- Partial retrieval does not establish complete results or absence.

For FSM export/download/extraction, report which requested deliverables
are ready and link them. Keep acquisition and lookup details internal.
Include a recovery reference when required by the active workflow.

Preserve core.data-loader's authoritative preview, approval, submission,
and status reports, including actionable diagnostics and deliverables.
Do not add internal MDA narration around those reports.

Use the outcome messages and failure-disclosure rules in
ora-resource/ora_error_handling.md. These reporting rules do not change routing,
validation, lifecycle decisions, approval, execution, or recovery.

### FSM

Include mapping decision/Application IDs as permitted reference evidence, conditional mapping-row requirement, dates and their sources, unresolved unknown-date states, sanitized Revoke receipts, Template/package provenance, package validation, handoff, and returned executor outcomes. Follow existing source-evidence persistence/redaction requirements.

### REST

For mutations include reconciliation completeness, planned create/reactivate/deactivate/no-op, verified loader contract, artifact and approval fingerprints, submission reference/status, and safe resume stage in permitted internal evidence. Include selected method and original routing-count evidence across preparation and Task Hook re-entry. On accepted initiation return only the core report; assignment_verification_result is pending/not_requested until a later successful verification workflow. For later results distinguish verified successes, preflight no-ops, failures, uncertain/unverified rows, and unattempted corrective work with an errors array. Never infer row success from job acceptance or a desired state observed after uncertain processing.

For customer reads return rest_read_result with:

- Read mode and supplied filter/ID or explicit all-assignment scope.
- Requested and applied output options, including defaults and any internal projection/tie-breaker additions.
- Permitted assignment results and returned_count.
- requested_scope_complete and collection_complete as separate facts.
- Safe continuation information, including next_offset when additional retrieval is possible.
- Count value and kind (exact or estimated), when applicable; interrupted exact retrieval may expose only a clearly labeled partial_count.
- Found/not-found status for a single-assignment read.

Successful completion of a requested window or an estimated count must not be reported as retrieval of every matching assignment. Keep the existing assignment_list output for List/search consumers.

Readiness is not success. An HTTP result without required readback is not verified completion. Do not report failed/uncertain mutation as no change.
