---
skill_id: "scm.manufacturing-and-supply-chain-materials-management.supply-chain-financial-flows.manage-supply-chain-financial-orchestration-lookups"
name: "Financial Orchestration Lookups Setup Task Guidance"
description: "Routes FOS lookup requests through Apps Common and catalog-supported setup artifacts through shared export and Data Loader; browser navigation and execution are prohibited."
layer: "pillar"
pillar: "SCM"
offering: "Manufacturing and Supply Chain Materials Management"
functional_area: "Supply Chain Financial Flows"
functional_area_code: "ORA_FOS_SUPPLY_CHAIN_FIN_FLOW"
task_code: "ORA_FOS_MANAGE_LOOKUPS"
task_name: "Manage Supply Chain Financial Orchestration Lookups"
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
  - "lookup_request"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/supply-chain-financial-flows/manage-supply-chain-financial-orchestration-lookups/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/manufacturing-and-supply-chain-materials-management/supply-chain-financial-flows/manage-supply-chain-financial-orchestration-lookups/current/"
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
side_effects: ["Delegates approved FOS lookup mutations and supported setup-data export/import to common workflows."]
required_privileges: ["Fusion privileges appropriate to the selected FOS Lookup Type or Lookup Code"]
---

# Financial Orchestration Lookups Setup Task Guidance

## Purpose and task contract

Provide FOS business scope and delegate execution for Manage Supply Chain
Financial Orchestration Lookups under Supply Chain Financial Flows.

- Task code: `ORA_FOS_MANAGE_LOOKUPS`
- Functional area code: `ORA_FOS_SUPPLY_CHAIN_FIN_FLOW`
- Offering: Manufacturing and Supply Chain Materials Management
- Catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`
- Availability, export/import, and CSV export/import flags: `Y`
- Data Loader import mode: `FSM`; no registered REST business object is declared.

Use the [parent skill](../SKILL.md) for task sequencing. Resolve project context,
target environment, exact requested operation, target identities, and supplied
values before delegation.

## Apps Common lookup routing

Route every lookup-type, lookup-code, and translation request through
[Apps Common](../../../../../core/fusion-api/apps-common/SKILL.md)
(`core.fusion-api.apps-common`). Pass `fusion_environment_context`,
`common_feature_request` with the lookup request and FOS task context, and
`execution_options`. Apps Common selects its Lookups workflow, which owns
resource discovery, supported fields, authentication, permissions, request
construction, preview, execution, and verification.

FOS lookups use the Standard Lookups workflow. Supply that view to Apps Common
and require the returned identity to match the requested type and code. Do not
switch to a different lookup view after a failed write or permission error.
An unresolved category must be handled by Apps Common's documented discovery,
not by this pillar selecting endpoints.

Do not invoke the nested lookup skill or REST client directly from this
wrapper. A missing common capability is a blocker; it does not authorize
another execution route.

## Strict no-browser boundary

Do not open, select, inspect, or navigate browser tabs, including an already-open
Safari tab. Do not use browser automation, desktop UI control, DOM/accessibility
inspection, screen scraping, or enabled-button checks. This prohibition covers
discovery, reads, permission checks, changes, export/import, and verification;
read-only navigation is not an exception.

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

## FOS scope and change validation

Accept only exact lookup-type names beginning with `FOS_` or `fos_`.
Preserve case; mixed-case `Fos_` is outside scope. Apply the scope to every
requested row, including imported changes. Filter inventory results to these
prefixes; do not assume that the underscore in a query pattern is a literal
prefix character. Verify each returned technical name.

For an all-types or all-codes request, require the common provider's complete
paged result, deduplicate by exact type or type/code identity, then apply the
scope filter. Label a bounded or incomplete result as partial. The documented
inventory below and a small export sample cannot establish completeness.
Resolve a supplied business meaning against current in-scope results; ask for
an exact selection when more than one match remains, without deriving codes
from labels or silently changing case.

Through Apps Common, support only the operations its selected Standard Lookups
contract supports: type/code reads, creates, updates, deletes, and translation
reads. An enable/disable request is an update only if the selected resource
contract supports the field. Do not invent translation writes or additional
fields from a UI label.

Before a mutation, obtain the current exact resource or the common workflow's
create-target absence check. Preserve all fields outside the requested delta.
Use returned configuration-level restrictions and actual API diagnostics.
Do not conclude that every error is a privilege issue or that System level
prevents every update. If Fusion identifies a System-level create/delete
restriction, report it; report privilege denial only when evidenced by the
delegated response. Never try another route to evade either restriction.

For creation, carry the user's business defaults into the preview only after
the common workflow verifies their supported field/value mapping:

- Lookup Type Module: `Supply Chain Financial Orchestration Foundation` when
  omitted. Resolve its technical identity; do not invent a module ID.
  Preserve a user-supplied module when it is valid for the selected contract.
- REST Access Secured: `Secure` when omitted. Validate the supported mapping
  for Secure, Anonymous, or Authenticated before sending any value.
- Lookup Code Enabled: `true` when omitted, subject to the supported schema.

State defaults and omitted optional values briefly in the preview. Validate
mandatory fields from the common contract; do not treat Meaning or another
required field as optional based on prior UI observations. If a requested
module, REST-access setting, lookup DFF, or other field is unsupported, stop
and identify the exact missing capability before any write.

Show the exact environment, operation, type, code when relevant, current state,
and immutable proposed delta. Use the selected common workflow's explicit
approval immediately before mutation and its fresh read to verify the result.

## CSV export, import, and validation

Catalog-supported setup-data artifacts use the same path as Costing Lookups:
[task-level export](../../../../../shared/setup-export/task-level-export/SKILL.md),
[setup-data validation](../../../../../shared/validation/setup-data-validator/SKILL.md),
[reference-data validation](../../../../../shared/validation/reference-data-validator/SKILL.md),
then [Data Loader](../../../../../core/data-loader/SKILL.md) for FSM CSV import.

Pass this exact task identity, offering, functional area, confirmed environment,
project context, and positive task sequence. Revalidate the catalog support
flags and package identity. Data Loader owns its Task Hook, immutable-archive
approval, upload, and import lifecycle; do not add a second import approval or
call `setupTaskCSVImports` directly.

Preserve the export skill's mode contract: a bare export request defaults to
template/spec; use populated setup-data mode only for an explicit current-data
request. Do not treat a template as the current lookup inventory. Data Loader
initiation is not completed import. Its status calls and polling require the
user's status/completion-monitoring request; do not add automatic polling here.

CSV/FSM artifacts do not replace Apps Common for individual lookup operations.
This route does not implement the former UI Export to Excel feature. If Excel
is requested, explain the available CSV setup export and resolve the requested
format through a supported workflow before execution. Do not silently substitute
a CSV ZIP for an Excel workbook or promise a browser Downloads destination.

## Diagnostics and persistence

Inherit retry, timeout, and approval rules from the selected common/shared
workflow. Never automatically retry a mutation. On timeout or uncertain outcome,
return the last status and available process/job identifiers for a later status
check; do not report success or initiate compensation.

Classify failures using `governance/error-handling-guidelines.md`: invalid scope
or fields, catalog/metadata mismatch, auth/authz, transport/environment, Fusion
API, failed/timed-out process, artifact persistence, or approval blocker.
Return `execution_result`, `diagnostics`, and `audit_summary` with the route,
task, environment, safe message, identifiers, and next action. Preserve partial
successes and an errors list. Persist wrapper-owned planning/validation evidence,
skill runs, and token usage through the project-management skills. Respect the
delegated workflow's persistence policy: do not create extra local reports,
logs, or run records following a successful Data Loader initiation. Redact
credentials, tokens, headers, and sensitive values.

## Reference data and review

Unlike Costing's fixed lookup-type inventory, the approved FOS scope is the
explicit prefix rule above. Runtime resource identity still requires an exact
read. No application ID is needed for the common Standard Lookups route.
Module technical identifiers and field enums must come from the selected
workflow's verified metadata; they are not static values in this wrapper.

| Data | Source and when needed |
| --- | --- |
| Lookup view and approved scope | Standard Lookups and the FOS prefix rule in this skill |
| Lookup Type and Lookup Code | Exact request plus the common workflow's current resource read; code identity is needed only for a code operation |
| Translation language | Explicit requested language for a single translation read; no default language is stored |
| Configuration level and field permissions | Current common-resource metadata/response; never a copied static permission table |
| Module identifier and REST-access values | Verified mapping under the selected common contract when needed for the requested create/update; the business default alone is not a technical ID |
| FSM artifact identity | Exact task export metadata and supported schema, including parent keys; positive task sequence comes from the active Task Hook context |

No `ApplicationId`, `ViewApplicationId`, `SetId`, or Data Loader REST business
object is supplied merely because another lookup category needs one. Apps
Common owns any additional identity required by the selected resource contract.

### Documented FOS lookup inventory

Historical FOS lookup seed-data reference.
These 33 exact FOS-prefixed names are historical seed-data references, not a
complete current inventory, an existence guarantee, or a restrictive allowlist.
The approved prefix rule still accepts other `FOS_` / `fos_` names, including
custom types, subject to common-workflow validation.

| Source seed-data group | Documented lookup types |
| --- | --- |
| FosEventManagement | `FOS_SHIPMENT_DOCUMENT_TYPES`, `FOS_EVENT_MSG_FUNCTION`, `FOS_DOCUMENT_TYPE`, `FOS_IMT_DOCUMENT_TYPES`, `FOS_MESSAGE_TYPE`, `FOS_PROCUREMENT_DOCUMENT_TYPES`, `FOS_SOURCE_EVENT_DOC_STATUS` |
| FosOrchestrationProcess | `FOS_FLOW_HEADER_STATUS`, `FOS_EVENT_DOC_STATUS`, `FOS_ORCHESTRATION_MSG_FUNCTION`, `FOS_SOURCE_TXN_EVENT_STATUS`, `FOS_TRADE_RELATIONSHIP_TYPES`, `FOS_TXN_EVENT_STATUS`, `FOS_TASK_STATUS` |
| FosSetup | `FOS_PRICING_STRATEGIES`, `FOS_QUALIFIER_OPERATORS`, `FOS_TASK_TYPE_CATEGORY`, `FOS_MULTIPLE_OPTIONS_CRITERIA`, `FOS_MARKUP_TYPE`, `FOS_FLOW_TYPE_FOR_TASK`, `FOS_CURRENCY_OPTIONS`, `FOS_CONJUNCTION`, `FOS_BUYER_VALUE_OPTION`, `FOS_AGREEMENT_TYPE`, `FOS_AGREEMENT_SUPPLIER_BASIS`, `FOS_AGREEMENT_REQ_ORG_BASIS`, `FOS_AGREEMENT_CUSTOMER_BASIS`, `FOS_AGREEMENT_BASIS_HEADS`, `FOS_SELLER_VALUE_OPTION`, `FOS_PCBU_PROFILES`, `FOS_FLOW_TYPE_FOR_EVENT`, `FOS_AGREEMENT_STATUS`, `FOS_AGR_BASIS_OPERATORS` |

The source groups identify `scm/fos/db/data/<group>/StandardLookupTypeSD.xml`;
they are not selectable module names or ModuleIds. The source also names
`ORA_FOS_EVENT_MSG_CATEGORY` and `ORA_FOS_AGREEMENT_TYPE_FOR_VAL`, but these
remain outside the approved prefix scope. Require an explicit scope change
before operating on them through this wrapper.

The historical document records `REST_ACCESS_SECURED=AUTH`. Do not use that
value as the current API enum, current access setting, permission evidence,
or a replacement for the user's approved Secure create default. Resolve
current settings and supported field mappings through Apps Common. No fixed
lookup-code values, configuration levels, translated meanings, or module
technical IDs are established by this inventory.

Offline review scenarios: an out-of-scope type stops before delegation;
an exact FOS code update enters Apps Common with only the requested delta;
a System restriction or 403 never triggers a browser fallback; an Excel request
does not invoke an unsupported UI export. Required reviewers are the FOS Pillar
Lead/SME and an FSCR A-Team/core reviewer.
