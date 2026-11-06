---
skill_id: "cx.configure-price-quote.quoting.quoting-to-oracle-order-management-integration"
name: "Quoting to Oracle Order Management Integration Setup Task Guidance"
description: "Provides task-specific setup guidance for Quoting to Oracle Order Management Integration, including the CPQ Fusion Account Generic Integration Data Loader workflow."
layer: "pillar"
pillar: "CX"
offering: "Configure Price Quote"
functional_area: "Quoting"
functional_area_code: "CUSTOM_QUOTING"
task_code: "CUSTOM_QUOTING_TO_ORACLE_ORDER_MANAGEMENT_INTEGRATION"
task_name: "Quoting to Oracle Order Management Integration"
parent_skill_id: "cx.configure-price-quote.quoting"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "REST"
businessObjects:
  - "CpqCommerceSettings"
  - "IntegrationVendors"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "orchestration"
execution_mode: "hybrid"
owner_team: "CX configure price quote pillar team"
version: "0.1.1"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "cpq_scope_assignment_confirmation"
  - "fusion_account_integration_confirmation"
  - "native_flow_prerequisites_confirmation"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "commerce_setting_result"
  - "commerce_setting_data_loader_source"
  - "fusion_account_integration_validation"
  - "fusion_account_integration_source"
  - "om_process_assignment_rule_guidance"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/quoting/quoting-to-oracle-order-management-integration/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/cx/configure-price-quote/quoting/quoting-to-oracle-order-management-integration/current/"
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
  - "Reads the CPQ Commerce enableBomPartAttributesOnModelLine setting after CPQ OAuth scope validation."
  - "Prepares a CpqCommerceSettings source when the setting is not Yes; core.data-loader owns source validation, immutable archive preparation, Task Hook approval, upload, and initiation."
  - "Prepares an IntegrationVendors source and validates its immutable upload artifact through Core against live Fusion metadata."
  - "Uploads and initiates Generic Integration only through core.data-loader after Task Hook validation and approval of its exact immutable artifact."
required_privileges:
  - "FACPQ privilege to read CPQ Commerce settings."
  - "Access to the CpqCommerceSettings and IntegrationVendors Data Loader business objects and to CPQ Integration Center."
  - "Privileges to upload and initiate an approved Data Loader archive."
---

# Quoting to Oracle Order Management Integration Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Quoting to Oracle Order Management Integration` under `Quoting`.

## Setup Task Skill Contract

- task_code: `CUSTOM_QUOTING_TO_ORACLE_ORDER_MANAGEMENT_INTEGRATION`
- task_name: `Quoting to Oracle Order Management Integration`
- parent_skill_id: `cx.configure-price-quote.quoting`
- pillar: `CX`
- offering: `Configure Price Quote`
- functional_area: `Quoting`
- functional_area_code: `CUSTOM_QUOTING`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `REST`
- businessObjects: `CpqCommerceSettings`, `IntegrationVendors`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Quoting to Oracle Order Management Integration` under `Quoting`.

## Setup Task Metadata

- Task name: `Quoting to Oracle Order Management Integration`
- Task code: `CUSTOM_QUOTING_TO_ORACLE_ORDER_MANAGEMENT_INTEGRATION`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `REST`
- Business Objects: `CpqCommerceSettings`, `IntegrationVendors`

## Source and Applicability

Use the current [Oracle native CPQ-in-Fusion integration guide](https://help-cxsales.oraclecloud.com/cpq/Content/Integrating_With_BigMachines/Integration_Guides/OrderMgmtIntegration_CPQFusion.htm)
for domain prerequisites and the current Core contracts for execution. This task
owns the Fusion Account connection and Commerce setting. The guide's separate
Fusion Order connection is a prerequisite; the two names are not interchangeable.
Before final readiness, require administrator evidence for the applicable native
prerequisites through `verify_native_flow_prerequisites_confirmation`. Missing
confirmation blocks readiness. This task does not configure those prerequisites
or select an alternative API route. Any missing prerequisite needs its own
catalog-resolved workflow; stop if that workflow is unavailable.

The OM procedure below uses this task's selected subscription orchestration
process. Oracle presents that process as an example; it is not a universal choice
for every order flow. Confirm the intended process with the OM administrator.
No release-specific API support is inferred from this manual procedure.

## Core Data Loader Contract for 26.10

This backport uses the persisted-preflight Data Loader and Task Hook contract
provided by this branch. Read `core/data-loader/SKILL.md` and
`core/data-loader/task-hook/SKILL.md`; do not use the in-memory session commands
from another branch.

Prepare the source and complete Core mapping, Business Object/API validation,
and final immutable archive preparation. Retain the internal preflight with
`--preflight-envelope-output`. Verify that preflight before calling Task Hook's
`data-load` with the active project's exact task context, task name and sequence.
Evaluate the returned graph against that final artifact, using only the declared
read-only lookups. Never invoke Task Validator commands directly.

After the task rules pass, use Task Hook's `build-data-load-preview` with the
final artifact binding and ordered rule results. Persist the internal preflight
and task preview as required by Core, and present the helper's complete
approval-required Markdown verbatim. Wait for the applicable Core approval.
On approval, use `approve-data-load-preview`, then
`verify-approved-data-load-archive`. Persist its returned
`taskValidationEnvelope` unchanged and provide it through
`--task-validation-envelope`. Submit with `--approved-preflight-envelope` and
`--confirm-upload`; omit the original source, mapping and routing arguments.
Do not construct an envelope manually. Missing or changed artifacts, a context
mismatch, or invalid approval require fresh validation and approval. Do not
rebuild the archive, reopen original sources or repeat live task lookups after
approval. Keep credentials and tokens out of all retained artifacts.

After initiation, return Core's accepted-initiation Markdown verbatim and pause.
Query status and errors through Core only when the user explicitly requests
load information. An initiation response proves submission, not completion.
After the requested status check reports success, perform this task's declared
read-backs before continuing. Failures, timeouts and uncertain results block
completion; follow Core recovery and diagnostic rules without automatic task-level
resubmission. Keep sanitized pillar stage and external-ID records in the project;
Core owns its required archive, preflight, Task Hook and diagnostic artifacts.

## Offering Readiness

Before configuration, use `core.fusion-api.rest-api-client` to read the Order
Management and Configure Price Quote offerings. Require exactly one offering
match for each and confirm the resolved identities `DOO_ORCHESTRATION` and
`ORA_CONFIGURE_PRICE_QUOTE` through the documented BOSS hydration. Stop if
either offering is absent or ambiguous, or its selected-choice lookup does not
confirm an enabled, checked Yes. Use the complete requests and match rules in
`ora-resource/ora_reference_lookups.md`; identity alone does not prove enablement.

## Commerce Setting: Populate Part Attributes for a Model with a BOM Part

This skill owns the Native OM integration setting
`enableBomPartAttributesOnModelLine`.

1. Validate a single CPQ OAuth scope token and confirm it is assigned to the
   target OAuth client. Never use credentials supplied in chat.
2. Read the current value with:

   ```text
   GET /cpq/rest/v19/settings/COMMERCE/enableBomPartAttributesOnModelLine
   Accept: application/json
   ```

3. If the value is `Yes`, record compliant status and continue. If it is not
   `Yes`, prepare a `CpqCommerceSettings` source and validate its immutable
   upload artifact through `core.data-loader` against live metadata. The source
   must contain only this fixed setting contract:

   ```json
   {
     "CpqCommerceSettings": [{
       "cpqCommerceSettingKey": "enableBomPartAttributesOnModelLine",
       "RestAction": "PATCH",
       "Accept": "application/json",
       "Content-Type": "application/json"
     }],
     "Items": [{
       "cpqCommerceSettingKey": "enableBomPartAttributesOnModelLine",
       "RestAction": "PATCH",
       "type": "COMMERCE",
       "key": "enableBomPartAttributesOnModelLine",
       "value": "Yes"
     }]
   }
   ```

4. Complete Core preflight and Task Hook validation for that final artifact.
   Build the Task Hook preview and use the Core approval workflow above for upload
   and initiation; do not issue direct CPQ PATCH, POST, PUT, or DELETE.
5. After a user-requested Core status check confirms load success, reread the
   same CPQ setting endpoint
   and require the value to be `Yes`. On a failed, timed-out, or indeterminate
   import, preserve redacted diagnostics and reconcile through read-only
   evidence; do not retry or roll back automatically.

`CpqCommerceSettings` is the approved Data Loader business object for this
Commerce setting route. The direct CPQ Settings PATCH endpoint is retained only
as the Data Loader record action and is never called by this skill.

## CPQ Fusion Account Generic Integration

This CPQ--OM task owns the **Fusion Account Integration** Generic Integration
connection. The user-confirmed CPQ--OM flow uses the registered
`IntegrationVendors` Data Loader business object and does **not** require a
Fusion CRM connection to be staged or enabled first.

### Preconditions and discovery

1. Use the active Run Book environment as the sole target. Confirm that
   `IntegrationVendors` is visible through `core.data-loader` live metadata.
2. Retrieve the existing vendor collection through the read-only CPQ endpoint
   `GET /cpq/rest/v19/integrationVendors` with `Accept: application/json`.
   Select exactly one item whose `integrationType` and `vendorName` are both
   `genericIntegration` and whose `properties.items[name=name].value` is
   `Fusion Account Integration`.
3. If one item exists, record its sanitized enabled state and `requestUrl`,
   then validate that the URL is the active Run Book environment. Do not
   create a duplicate. If zero items exist, continue to Data Loader creation;
   if more than one item exists, stop as an ambiguous configuration.
4. If it is absent, prepare one create-oriented Data Loader artifact with the
   following exact values. Use the live metadata column order and hierarchy as
   authoritative.

```text
IntegrationVendors (integrationVendorsKey)
└── properties (propertyId, integrationVendorsKey)
    └── items (propertyId, name, value)
```

| Parent or item | Value |
| --- | --- |
| `integrationType` | `genericIntegration` |
| `vendorName` | `genericIntegration` |
| `name` | `Fusion Account Integration` |
| `requestUrl` | Active Run Book Fusion environment base URL |
| `username` | `FDOS_CREDENTIAL_REQUIRED` |
| `password` | `FDOS_CREDENTIAL_REQUIRED` |
| `enabled` | `false` |

Every `items` row must use the same `propertyId` as its `properties` parent.
Never place customer credentials, OAuth tokens, or CPQ scopes in a workbook,
archive, project artifact, diagnostic, or chat response.

### Create and validate workflow

1. Prepare the create-oriented `IntegrationVendors` source with placeholder
   credentials and `enabled=false`. Validate the final archive records and
   parent/child linkage against live metadata through Core. A mismatch blocks
   the workflow.
2. Complete Task Hook validation and build its internal preview for the final
   immutable artifact. Show Core's approval-required Markdown verbatim. Obtain
   the applicable approval, then approve and verify through Task Hook and submit
   the exact retained preflight and unchanged task envelope through Core.
3. Report initiation, then pause until the user requests load information. Use
   Core's status/error helper for that request. Continue only after confirmed load
   success; failure, pending status or unavailable status leaves completion
   unverified. Do not poll automatically, retry the load, or invoke direct CPQ writes.
4. After a confirmed successful load, the user replaces the placeholders, enables the
   connection, and saves it in **CPQ Admin > Integrations > Integration
   Center**. Confirm the enabled state through that read-only UI verification.

When the named connection is absent, the Task Hook graph ends with validated
final archive records, after which Task Hook builds the bound approval preview.
After the approved load and user-managed credential save, resume with a fresh read-only collection
GET and Integration Center verification. Continue to OM rule readiness only
when exactly one named connection has the active Run Book URL and is enabled.

### Boundaries

- Direct Integration Vendor REST is allowed only for the documented read-only
  collection GET used to determine whether the named connection exists. Do not
  use direct POST, PUT, PATCH, or DELETE; creation remains Data Loader-based.
- Do not create a duplicate when user-managed Integration Center verification
  confirms the named connection exists.
- Do not upload, initiate, retry, enable, or save without the approval required
  by the applicable Data Loader or user-managed UI stage.

## Preflight and Failure Handling

Before any read or mutation, confirm the active Run Book environment, target
offering readiness, required OAuth scope, and current resource identity. For
the Generic Integration route, also confirm live Data Loader metadata, final
archive record linkage and Core's persisted preflight target binding. Task Hook owns
approval-envelope integrity and its match to the immutable upload artifact.

Classify failures as input validation, catalog mismatch, auth/authz,
transport/environment, Fusion API, process timeout, artifact persistence, or
approval blocker. Refresh a rejected cached token once only as delegated to
the core client. Never retry a PATCH, upload, initiation, or other uncertain
mutation without a fresh current-state read and immediate explicit approval.
Persist a sanitized task-stage run record and relevant external IDs under the
project workspace. Delegate required preflight, Task Hook and diagnostic
artifacts to their Core workflows. Never persist credentials, tokens, raw authorization headers, or raw
responses containing sensitive values.

## OM Process Assignment Rule

For this supported task flow, this is a manual Order Management task. Do not make a GET call or
attempt to create, activate, or deploy the rule through an API.

After Generic Integration read-back, always report the OM rule stage and
present the following instructions to the Order Management administrator
exactly; do not shorten, paraphrase, or replace them with API guidance. If the
same target project's exact rule confirmation remains applicable and the user
has not reported a rule change, state that the rule is already confirmed active
and deployed. Label the steps as the documented procedure and do not ask the
administrator to create a duplicate. Report setup readiness after the required
read-backs and rule confirmation. Offer a CPQ Book Order as a separate,
optional business validation when the user wants transaction-level proof.
The documented OM rule procedure is:

1. Go to **Home Page → User Profile Options → Setup and Maintenance**.
2. Search for **Manage Process Assignment Rules for Sales Orders** and open the task.
3. Select **Create New Rule**.
4. Enter the rule name: **Oracle CPQ Orchestration Process Assignment Rule**.
5. Add the IF condition: **Source Order System (Order Header)** equals
   `Oracle CPQ`.
6. Add the THEN DO action: **Process Name (Order Fulfill Line)** equals
   `DOO_ProductFulfillmentWithIntegratedSubscription`.
7. Select **Save and Close**.
8. Open the new rule, select **Activate Rule**, and enter an **Effective Start
   Date**.
9. Select **Save and Close** again.
10. Deploy the rule.
11. Confirm that the rule is active and deployed before submitting CPQ Book
    Orders.

Record the administrator's confirmation of the exact name, condition, action,
active state, and deployed state. Missing, inactive, or undeployed rules are
manual-task blockers; do not issue GET, POST, PATCH, or deploy requests from
this skill.

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

Use the parent functional-area skill `cx.configure-price-quote.quoting` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.
