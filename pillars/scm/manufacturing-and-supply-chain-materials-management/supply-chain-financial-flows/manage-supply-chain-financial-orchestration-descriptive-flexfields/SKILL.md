---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.supply-chain-financial-flows.manage-supply-chain-financial-orchestration-descriptive-flexfields"
name: "Financial Orchestration Descriptive Flexfields Setup Task Guidance"
description: "Routes FTR and PTR DFF setup export, approved FSM CSV import, deployment, and status through Apps Common; browser navigation and execution are prohibited."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Supply Chain Financial Flows"
functional_area_code: "ORA_FOS_SUPPLY_CHAIN_FIN_FLOW"
task_code: "ORA_FOS_MANAGE_DFF"
task_name: "Manage Supply Chain Financial Orchestration Descriptive Flexfields"
parent_skill_id: "scm.manufacturing-and-supply-chain-materials-management.supply-chain-financial-flows"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "SCM manufacturing and supply chain materials management pillar team"
version: "0.2.1"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "fusion_environment_context"
  - "dff_request"
  - "dff_task_context"
  - "flexfield_deployment_context"
  - "execution_options"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "execution_result"
  - "diagnostics"
  - "audit_summary"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "core.fusion-api.apps-common"
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.fusion-api.apps-common"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/supply-chain-financial-flows/manage-supply-chain-financial-orchestration-descriptive-flexfields/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/supply-chain-financial-flows/manage-supply-chain-financial-orchestration-descriptive-flexfields/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries: ["All"]
  countries: ["All"]
  fusion_releases: ["Current Oracle Fusion Cloud Applications release"]
side_effects: ["Delegates supported DFF exports, approved FSM imports, and approved deployments to Apps Common."]
required_privileges: ["Fusion privileges appropriate to the selected FOS DFF and action"]
---

# Financial Orchestration Descriptive Flexfields Setup Task Guidance

## Purpose and task contract

Provide FOS scope and delegate DFF setup-data export, approved FSM CSV import,
deployment, and deployment-status work in the same manner as Costing DFF.

- Task code: `ORA_FOS_MANAGE_DFF`
- Task name: Manage Supply Chain Financial Orchestration Descriptive Flexfields
- Functional area: Supply Chain Financial Flows (`ORA_FOS_SUPPLY_CHAIN_FIN_FLOW`)
- Offering: Manufacturing and Supply Chain Materials Management
- Catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`
- Availability, export/import, and CSV export/import flags: `Y`
- Data Loader import mode: `FSM`; no registered REST business object is declared.

Use the [parent skill](../SKILL.md) for sequencing. Require the exact environment,
project context, task scope, requested operation, and applicable setup artifact
or deployment context before execution.

## Strict Apps Common routing

Route every request through
[Apps Common](../../../../../core/fusion-api/apps-common/SKILL.md)
(`core.fusion-api.apps-common`). Apps Common selects its Descriptive Flexfields
workflow. Pass `fusion_environment_context`, `common_feature_request` containing
the exact `dff_task_context` and, for deployment/status,
`flexfield_deployment_context`, plus `execution_options`.

The selected common workflow owns task eligibility, export/import transport,
deployment requests, OAuth, privileges, approvals, and status handling. Do not
call its nested skill or REST client directly from this wrapper.

Missing capabilities or unresolved identities must stop the relevant operation;
no ad hoc REST, alternate import, or direct database fallback is permitted.

## Strict no-browser boundary

Do not open, select, inspect, or navigate browser tabs, including an already-open
Safari tab. Do not use browser automation, desktop UI control, DOM/accessibility
inspection, screen scraping, or enabled-button checks. This prohibition covers
discovery, reads, permission checks, changes, export/import, deployment, and
verification; read-only navigation is not an exception.

Carry this restriction into every delegated workflow. Never use a browser as a
fallback for missing identifiers, unsupported operations, authentication errors,
or API/import failures. Stop the affected operation and report the blocker and
supported next step instead; do not ask for browser access as a workaround.

Authentication remains owned by the declared common/shared route. Do not launch
or drive an OAuth login browser from this skill. If non-browser authentication
cannot proceed, ask the user to complete the required login separately, then
resume the declared route. Do not retrieve browser cookies or session tokens.

Separately requested manual UI QA is outside this skill, never an execution
route, fallback, or prerequisite for its automated verification.

## FOS flexfield scope

Allow only these exact existing DFF codes:

| Flexfield code | Business name | Application ID |
| --- | --- | --- |
| `FOS_TRADE_AGREEMENT_FTR` | Financial Orchestration Financial Route | `10115` |
| `FOS_TRADE_AGREEMENT_PTR` | Financial Orchestration Primary Route | `10115` |

Mapping evidence: verified FOS flexfield deployment metadata.
Its deployment XML and `[flexfieldType, applicationId, flexfieldCode]`
descriptor list independently identify each code with application ID `10115`.
This is reusable product registration evidence, not evidence of deployment
success or current status in the caller's target environment.

Reject other codes. For an individual configuration request, identify the exact
flexfield and context/segment when relevant, preserve the requested field delta,
and pass the request to Apps Common. The current common DFF contract supports
setup-task export/import and deployment/status; it does not provide direct
segment/context/header CRUD or a segment editor.

Do not claim direct CRUD is implemented. A requested edit requires a supported
artifact-preparation contract before import. If that contract is absent, report
the gap and required task-specific CSV schema/mapping; do not synthesize CSV
members, columns, defaults, or operations from screenshots. Value-set requests
are a separate Apps Common feature and must be explicitly routed there rather
than treated as a DFF editor action.

## Setup-data workflow

1. Enter Apps Common with the exact task code, name, offering, functional area,
   environment, project, and positive task sequence.
2. Its DFF workflow rechecks export/import and CSV support flags and routes
   exports to `shared.setup-export.task-level-export`. Pass the export intent
   explicitly: a request for current configuration needs populated setup data;
   a template/spec request needs template mode. A bare export request retains
   the shared export skill's template/spec default. A headers-only template
   cannot establish current values, available columns, or an application ID.
3. Validate the task artifact through `shared.validation.setup-data-validator`
   and `shared.validation.reference-data-validator`. Keep FTR/PTR identity and
   changes in scope. A task export can contain both allowed flexfields: disclose
   its actual scope instead of claiming it is filtered to just one DFF.
4. The common DFF workflow delegates a validated, nonempty, immutable FSM ZIP
   containing exact-case `ASM_SETUP_CSV_METADATA.xml` and the task CSVs to
   `core.data-loader`. Data Loader owns Task Hook validation, approval, upload,
   submission, and status handling. Preserve its initiation result; initiation
   is not completed import. Request status only when the user asks for status,
   results, or completion monitoring, following Data Loader's own contract.
   Do not call `setupTaskCSVImports` or
   `shared.setup-import.task-level-import`, or duplicate Data Loader's approval.
5. After successful import, follow the common DFF deployment workflow with its
   separate approval gate. Failed or incomplete import must not trigger deployment.

The source/exported schema must establish the exact parent/child identifiers,
required fields, references, and intended change before an import can be
proposed. An accepted archive is not proof of deployment or functional success.

## Application ID and deployment prerequisites

Deployment/status require a confirmed `application_id` together with the exact
allowed `flexfield_code`. These are distinct from the FSM task code and an
OAuth client ID.

Resolve `application_id` from the exact-code mapping in FOS flexfield scope
and pass it with `flexfield_code` to Apps Common. An omitted application ID
does not require another user question or a setup export. Preserve both
identifiers in the common preview. Do not use this ID for other DFF codes.

If an explicitly supplied ID or authoritative target-environment registration
record conflicts with the stored mapping, stop the affected operation as
`catalog_or_metadata_mismatch` and report the conflicting identities for
resolution. Do not silently replace either value or submit a deployment to
test it. Runtime values are not automatically promoted to reusable defaults;
changing the stored mapping requires source evidence for the exact code.

Do not copy an ID from Costing, Payroll, a generic example, or a prior trial.
An HTTP 200, echoed identifiers, initial DEPLOYING response, or "not submitted"
status is not proof of a registered code/ID mapping. Do not submit deployment
as an application-ID discovery test. Missing deployment inputs are
`input_validation`; conflicting or unresolved registration metadata is
`catalog_or_metadata_mismatch`. Stop the affected operation and name the missing
input or evidence; do not block unrelated supported operations.

With verified identifiers, delegate deployment to Apps Common. The common DFF
workflow applies the documented force default, presents the exact target,
endpoint and immutable payload, and obtains explicit approval immediately
before submission. Configuration/import approval is not deployment approval.

Return the delegated job ID, job status, deployment status, validation status,
validation report, and deployment error message. Poll only as requested using
the common workflow's bounds (currently 10 seconds, maximum 300 seconds).
Only its successful terminal deployment state proves completion; HTTP acceptance
alone does not. Preserve a terminal error and stop without automatic resubmission.

## Required reference and runtime data

| Operation | Stored task data | Runtime data passed to the common workflow |
| --- | --- | --- |
| Export | Task identity, offering, functional area, catalog support flags | Environment, project context, positive task sequence, explicit export intent; only verified task-supported criteria when filtering is requested |
| Import | Same task identity and FTR/PTR scope | Exact validated FSM ZIP, environment, project/Task Hook context and positive sequence, immutable archive approval owned by Data Loader |
| Deployment/status | Exact FTR/PTR application-ID mappings and source above | Selected exact code, mapped application ID, environment, optional force value and monitoring intent, deployment approval for a write |
| Segment/context configuration preparation | No FOS CSV edit contract is stored | Populated exact-task baseline, exact members/headers and parent-child keys, target identity and requested delta, value-set identity/compatibility and column ownership when affected |

Task sequence is supplied by the active task context, not copied from another
product's skill. A parent task-list code, root business-object code, export
filter attributes, or CSV member names may be retained only when supported by
the actual FOS task metadata/package; this wrapper does not invent them.
Do not copy Recruiting's `821`, its CSV contract, storage-column ranges, or
value-set defaults. Those are product-specific reference data.

### FOS storage references and their limits

Oracle's published table snapshots for
[FOS_AGREEMENT_FTR_F (26B)](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/fosagreementftrf-11031.html)
and [FOS_AGREEMENT_PTR_F (26A)](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/oedsc/fosagreementptrf-9547.html)
document the following DFF storage columns on each table. Reviewed 2026-09-24;
these are release-qualified references, not proof of the target pod's current
registration or available columns.

| Column family | Documented storage on each table |
| --- | --- |
| `ATTRIBUTE_CATEGORY` | `VARCHAR2(150)` context/structure discriminator |
| `ATTRIBUTE_CHAR1` through `ATTRIBUTE_CHAR15` | `VARCHAR2(150)` |
| `ATTRIBUTE_NUMBER1` through `ATTRIBUTE_NUMBER5` | `NUMBER`; no fixed precision/scale stated in these entries |
| `ATTRIBUTE_DATE1` through `ATTRIBUTE_DATE3` | `DATE` |
| `ATTRIBUTE_TIMESTAMP1` through `ATTRIBUTE_TIMESTAMP3` | `TIMESTAMP` |

DFF synchronization guidance explicitly distinguishes the PTR DFF code
`FOS_TRADE_AGREEMENT_PTR` from the physical table `FOS_AGREEMENT_PTR_F`.
For any allocation, verify the selected code's current table usage and column
availability through the routed evidence before applying these references;
do not infer the FTR binding solely from a matching suffix. Physical table
keys are not DFF setup CSV row keys. These sources authorize neither database
access, seed loading, BOSS synchronization, nor another execution route.

### Evidence needed for a FOS configuration-edit contract

The application-ID mapping enables deployment/status identity resolution. It
does not establish how to create, edit, disable, or delete configuration rows.
Before adding that preparation capability, obtain the following from a
completed populated export for `ORA_FOS_MANAGE_DFF` and verified task metadata:

| Evidence | What must be established, not copied from another product |
| --- | --- |
| Package identity and provenance | Exact task, source environment, completion evidence, immutable ZIP digest, encoding, metadata structure, member names and headers |
| DFF roots | Separate exact FTR/PTR code and application-ID identities, root business-object mapping, and export scope |
| Definition rows and joins | Actual representations and unique keys for globals, context selector, contexts and context-sensitive segments; preserve the selector separately from its children |
| Field mapping | User-facing names to actual CSV columns, required transport fields, flag/enumeration encodings, lengths and immutable identities |
| Storage ownership | Current table usage, datatype compatibility, occupied columns and global/context interactions; a disabled segment does not prove a column is free |
| Value sets | Exact exported identity and approved metadata for datatype, length, precision/scale and display compatibility; a label is not an internal ID |
| Ordering, defaults and translations | Scope of sequence uniqueness, verified presentation/default behavior, language keys and preservation of unrequested translations |
| Operation semantics | Proven create/update/disable/delete representation and verification; omitting a row is not evidence of supported deletion |

No completed FOS package establishing these mappings was available in this
repository review. Do not treat another team's filenames or a table schema
as the missing contract. This gap blocks configuration preparation, not an
otherwise valid export, import of an already validated immutable package, or
deployment/status operation. Source task sequence stays runtime-owned; do not
copy Recruiting's fixed sequences, contexts, task lists or column limits.

## Diagnostics, persistence, and review

Use `governance/error-handling-guidelines.md` and the selected workflow's
preflight, redaction, retry, and timeout policies. Missing task/field input is
`input_validation`; unsupported catalog/CSV/schema or registration identity is
`catalog_or_metadata_mismatch`. Preserve delegated auth/authz, transport,
Fusion API, process failure/timeout, artifact, and approval classifications.
Do not reclassify an unsupported operation as a privilege issue.

Persist wrapper-owned planning/validation evidence and skill/token-usage
records under the declared project paths using the project-management skills.
Respect the delegated workflow's persistence policy: Data Loader's successful
initiation must not trigger extra local reports, logs, or run records from this
wrapper. Return its completion/status evidence only when obtained through its
permitted status workflow. Preserve partial results and available ProcessId,
job ID, last status, and next-check guidance. Never persist secrets or tokens.
No automatic write retry, rollback, or compensation is implemented here.

Offline review scenarios: a segment edit without a supported artifact contract
reports the gap; either allowed code with an omitted application ID resolves
to `10115` in the common preview; a conflicting supplied ID stops before
submission; an import failure prevents deployment; a "not submitted" status is
reported as failure, never success. Required reviewers are the FOS Pillar
Lead/SME and an FSCR A-Team/core reviewer.
