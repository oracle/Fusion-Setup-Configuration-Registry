---
skill_id: "erp.financials.customers.manage-customer-uploads"
name: "Manage Customer Uploads Setup Task Guidance"
description: "Prepares and validates Customers-worksheet FBDI packages for Manage Customer Uploads in Customers; retains explicit readiness gates for governed live execution."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Customers"
functional_area_code: "ORA_EGP_CUSTOMER"
task_code: "ORA_AR_MANAGE_CUSTOMER_UPLOADS"
task_name: "Manage Customer Uploads"
parent_skill_id: "erp.financials.customers"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "FBDI"
businessObject: "customers"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.7"
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
uses_core:
  - "core.data-loader"
  - "core.data-loader.task-hook"
  - "core.fusion-api.rest-api-client"
  - "core.runbook"
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
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customers/manage-customer-uploads/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/customers/manage-customer-uploads/current/"
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
  - "Writes local offline preview ZIP and validation report to a new caller-selected directory."
  - "May request selected read-only customer evidence through central API clients after workflow selection and scope checks."
  - "Writes candidate-bound API captures and partial comparison reports to a new private directory outside the repository."
required_privileges: []
---

# Manage Customer Uploads Setup Task Guidance

## Current runtime availability

For an explicitly selected partial identity observation, the existing collector
supports `--read-scope rest-identity`. Read the
[REST identity contract](references/rest-identity.md) first. This candidate-bound
mode consumes only the existing core REST GET client and does not clear full
matching, reconciliation, approval or submission gates.

Read [governed read routes](references/governed-read-routes.md) before any runtime
read or handoff. This task-only revision uses the existing central REST GET and
Data Loader workflows and contributes no framework extension. Offline preparation
and synthetic evidence review are available. The combined read-only collector preserves the original REST/SOAP split using
task-owned SOAP parsing over unchanged core transport. Offline replay is available.
Exact attempt evidence uses `customer_attempt_collect.py` through unchanged core
REST GETs, with task-owned interpretation and the same strict association checks.
Use core's documented approval/recovery workflow; retain uncertain attempts and
never add task-level retries. A successful read or submitted request is not a
verified import or completed journey. Historical evidence does not qualify a new
candidate. The task is catalog-aligned under Financials / Customers.

## Purpose

Prepares and validates the Customers worksheet for `Manage Customer Uploads` under `Customers`, with explicit contracts for the governed FBDI journey.

## Setup Task Skill Contract

- task_code: `ORA_AR_MANAGE_CUSTOMER_UPLOADS`
- task_name: `Manage Customer Uploads`
- parent_skill_id: `erp.financials.customers`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Customers`
- functional_area_code: `ORA_EGP_CUSTOMER`
- available_flag: `Y`
- export_import_supported_flag: `N`
- csv_export_import_supported_flag: `N`
- dataloader_import_mode: `FBDI`
- businessObject: `customers`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when preparing or validating a Customers-worksheet package, or reviewing readiness for the governed FBDI import journey.

## Setup Task Metadata

- Task name: `Manage Customer Uploads`
- Task code: `ORA_AR_MANAGE_CUSTOMER_UPLOADS`
- Available: `Y`
- Export/import supported: `N`
- CSV export/import supported: `N`
- CSV export/import routing: `not supported`
- Data Loader import mode: `FBDI`
- Business Object: `customers`

## Import Route

`CSVExportImportSupportedFlag` is `N`, so this task is not marked as CSV export/import supported in the effective setup-task catalog.

The selected route is explicitly FBDI with business object `customers`. The catalog flags do not establish FBDI runtime readiness. Use the FBDI readiness and execution contracts below; no task-level FSM export is required.




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

Use the parent functional-area skill `erp.financials.customers` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Customers FBDI Authoring Status


SQL, JDBC, SQL Developer and Publisher are developer-test validation tools only.
Do not ask implementors for database access or query execution as part of this
functional journey. A successful SQL-backed test does not qualify the supported
runtime reconciliation path; retain that coverage dependency separately.

The selected flow is simplified Upload Customers, with the entire Customers worksheet in scope. Contacts, Reference Accounts and Customer Bank Accounts are deferred. Account receipt-method fields and all 30 account DFF values in Customers remain included. Offline checks and assisted governed execution use the candidate-specific evidence gates below; a prior campaign result does not approve a new environment or candidate.

The catalog's N flags describe FSM task export/import capability; they do not prohibit this explicitly selected FBDI route. The developer verified a deployed customers registration separately. Re-resolve live metadata for each target environment before using core.data-loader. Do not route this package through FSM exports or the CSV-only FSM tester.

Read [the source contract](references/source-contract.md), [the 87-field contract](assets/customer-contract.json), and all six [ora-resource files](ora-resource/ora_input_validation.md). The compiled registry supports planning; candidate evidence must pass [the central handoff evaluation](references/central-handoff.md). Local package checks and a complete registry do not grant runtime readiness or approval.

Before any implementor execution, prepare the assisted `setup_task_plan` from
[the shipped task registry](ora-resource/ora_rule_registry.json) and its owning
source rules. Require the exact task code and name declared above, schema `3.0`,
nested representation, and task and reachable-node
readiness `ready` with no blocking reasons. Confirm the start node `ARCU.INPUT`,
unique node IDs, existing prerequisites and declared transition targets, acyclic
paths ending at declared terminals, supported actions, and every reachable source
file within this task's ora-resource folder, heading and named resolver; require
agreement with the owning source Task Nodes rows. Stop on a missing, stale,
inconsistent or incomplete contract; do not repair the graph during execution.

Only after these checks pass, record `status: planned`, `validation.status: ready`,
exact task identity, checked sources and graph in `setup_task_plan` before starting at
`ARCU.INPUT`. Execute only reached nodes after their prerequisites pass, retain
sanitized evidence and declared outcomes, and follow only their exact transitions.
An unlisted outcome stops execution. A ready assisted plan permits entry into the
task graph; it does not approve an import or select another execution route.

After the final immutable archive and normal Data Loader preflight are available,
follow [the shipped Task Hook contract](../../../../../core/data-loader/task-hook/SKILL.md)
and its returned [rule-execution guide](../../../../../core/data-loader/references/task-rule-registry-execution.md)
through [the task phase contract](references/task-hook-handoff.md). Require ready
task validation and evaluated ordered rule results before preview; missing or
skipped task guidance does not satisfy this task's mandatory gates. Keep the
existing candidate approval, archive verification and submission controls. Do not
call internal validator scripts directly or defer the earlier assisted review
until this loader phase.

For supplied read-only source-key evidence, use [the identity evidence contract](references/identity-evidence.md) and its offline helper. It distinguishes missing evidence, no records, ambiguous records, and inactive references. It does not query Fusion or resolve complete operation effects. The assisted MATCH evaluator consumes reviewed supplied before-state evidence; see [the assisted evidence contract](references/assisted-evidence.md).

Then use [the ownership evidence contract](references/ownership-evidence.md) to check account/party, party-site/location, account-site and site-use relationships. A source-key match attached to the wrong parent is a mismatch. Supplied relationship evidence alone does not complete persisted-value reconciliation or authorize a live import.

Use [before-state target intent](references/target-evidence.md) to compare the
proposed create/update/reuse operations with actual reference, number and parent
observations. New-reference evidence never proves physical creation or grants
execution readiness.

For after-phase evidence, use [selected persisted-value comparison](references/value-evidence.md).
It covers 75 nonblank fields, including party DUNS, taxpayer ID and GSA,
the full location value projection,
the account DFF context and all 30
segments, and reports remaining fields
explicitly. A selected-value match is not full reconciliation or Journey completion.

Use [profile-class and requested-set reconciliation](references/profile-set-evidence.md)
for the two additional comparisons. It retains profile history, checks temporal
ambiguity, and verifies the requested set against both actual site records.
These checks do not prove all profile defaults or create/update/reuse effects.

Use [receipt-assignment comparison](references/receipt-evidence.md) for method,
BILL_TO scope, primary flag and start-date evidence. A matching assignment does
not prove insertion by this attempt or harmless replay; preserve assignment
history and verify before/after effects separately.

Use [before/after effect observations](references/effect-evidence.md) to compare
the declared entity intent with reference, ownership and complete selected-value
snapshots. Receipt inventory differences remain separate observations. New
references never stand in for proof of physical entity creation or attempt causality.

Use [bill-to link comparison](references/bill-to-evidence.md) for nonblank
BILL_TO_CUST_SITE_REF. Resolve its source reference separately from the persisted
site-use ID; retain target purpose, parent and set evidence. A selected link match
does not certify business eligibility, blank-update effects or loader branch.

Use [supporting profile and sibling-site inventories](references/supporting-effects.md)
to retain organization-profile history and detect changes on other party sites.
Primary-flag cleanup may affect siblings not listed in the candidate. Selected
inventory differences still need an explicit effect review and attempt evidence.

Use [taxpayer-registration comparison](references/tax-evidence.md) for
TAXPAYER_REGISTRATION_NUM against the party's THIRD_PARTY tax profile. The tax
callback is asynchronous; a matching value does not prove this attempt ran it.
Preserve exact text, profile ambiguity and separate before/after effect evidence.

Use [attempt-to-core association](references/attempt-association.md) to bind
retained candidate/context, Run Book/task, content and initiation IDs to exact
process definitions. It can prepare the staging-review input after a complete
match; it does not prove staging lineage or authorize a new attempt.

Use [registration and argument binding](references/registration-evidence.md) to
compare fresh supplied adapter evidence with the reviewed recipe and central
preflight, then carry its hashes into the actual Task Hook preview. Future
interface IDs and resolved job arguments remain unavailable before submission.

Use [request-scope observations](references/request-evidence.md) to compare
separately supplied interface/upload IDs with Customers staging evidence.
Keep initiation, interface, upload and batch IDs in their own namespaces.
Staging agreement cannot establish the unresolved live initiation-to-product link.

## Offline Business Input and Preview

Translate the user's business request into a reviewed JSON document with schema_version ar-customers-input-v1, operation create/update/mixed, provenance explicit-business-input, and a Customers array. Use exact field names from the contract, string values and null. Keep original references and leading zeros. The operation records user intent; it does not promise every field supports that operation. The actual existing-target effects must be resolved before a live approval.

When the user requests design or test-data generation, use provenance
proposed-business-input for the generated proposal. Preserve that origin; do not
claim the user supplied or accepted its values. Run the same checks, disclose all
proposed values/effects, and carry the input hash and provenance into the central
preview's finalData. The normal exact-candidate approval must explicitly cover
the proposed data and load; no separate pre-preview acceptance is required.
Neither provenance value grants execution authority or permits template examples
to become operational defaults.

The [synthetic two-site example](assets/synthetic-two-sites.json) demonstrates input shape only. It is not environment setup or a ready live candidate. Do not read template examples as user input. Direct XLSM intake and arbitrary spreadsheet conversion are not implemented; preserve the reviewed JSON as the explicit intermediate input.

```text
python <task-folder>/scripts/customers_package.py preview --input reviewed-business-input.json --output-dir <new-preview-directory>
python <task-folder>/scripts/customers_package.py inspect --zip <new-preview-directory>/candidate.zip --operation create
```

The helper validates known required fields, business character limits and [control-file UTF-8 byte limits](references/control-byte-limits.md), supplied flags/date, parent-input consistency and exact ZIP/CSV structure. It emits only ArUpdCustomers.csv with 87 ordered business fields plus END. It preserves supplied values and blanks without local business defaults. A zero exit from preview/inspect means those offline checks passed; inspect the report's live blockers. It never uploads, submits ESS, queries Fusion, rolls back or retries. Its inspection-size budget is a local processing limit, not a product row limit.

Synthetic examples illustrate input shape only; they are never implementor defaults or live input.

Use [the campaign evidence reviewer](references/campaign-review.md) to generate
the requested-field readback plan and recompute the individual checks from one
raw evidence bundle. It preserves partial outcomes and missing obligations; it
does not complete the live execution adapter or override registry readiness.
Follow [the verification plan](references/verification-plan.md) for before/after
collection, every omitted-field effect, partial outcomes and recovery decisions.

For the supported REST projections, follow
[governed read routes](references/governed-read-routes.md) and the exact evidence
scope in [REST reconciliation](references/rest-reconciliation.md). The complete
`customer_api_collect.py` live bundle uses the task SOAP adapter and existing
core REST client. Its injected-client coordinator is also used by offline tests.
The retained coordinator models independent bounded account and organization
party/site number searches and deployed account DFF metadata mapping. Its
synthetic tests preserve incomplete evidence and visibility limits; they do not
establish unrestricted visibility. Unexposed columns and unsupported history
remain unknown.
It does not replace unresolved existing-target checks, complete reconciliation,
or the normal execution gate. Raw tenant evidence stays outside the checkout.

Compose the supported observations using
[business-outcome reconciliation](references/business-outcome-reconciliation.md).
Retained SOAP captures are recomputed using the pure task-owned
`customer_soap_contract` parser, with no core reader import or network fallback.
Recomputation does not make historical data fresh or qualify this revision;
historical projected summaries cannot substitute for recomputation. For existing targets use the exact entity-intent review;
for new logical targets use the scoped new-target review and separately establish
business authority over those identifiers. The observed lack of a conflict is
not creation authority. After execution combine exact attempt association,
source/number/parent identities, creation-time corroboration where applicable,
all supplied values and relevant effects. Preserve partial outcomes and use the
complete diagnostic identity/count partition only when its prerequisites pass.
No single component's PASS completes this composition or Journey synchronization.

## Loader Validation Acceptance

Disclose named business-rule gaps and allow an explicit decision to rely on the loader after hard gates pass. Missing business-rule evidence is not an automatic prohibition. Never bypass known-invalid values, package/identity/routing controls, or intended entity effects. Keep evidence unresolved after acceptance.

The central context JSON must contain environment_url, preview_id, registration_sha256 and arguments_sha256 from the actual governed preview. Fingerprint arguments as canonical UTF-8 JSON with sorted keys and compact separators. Run the local record check with:

```text
python <task-folder>/scripts/customers_package.py review --zip candidate.zip --operation create --context central-context.json
python <task-folder>/scripts/customers_package.py review --zip candidate.zip --operation create --context central-context.json --acceptance user-acceptance.json
```

Only after the user explicitly accepts the disclosed uncertainty, record schema_version fscr-fbdi-loader-validation-acceptance-v1, decision accept_loader_validation, the exact returned binding, accepted_by, timezone-qualified accepted_at, and decision_reference. The context and acceptance are run evidence, never reusable skill defaults. A local JSON record does not authenticate the actor or grant permissions. Changed candidate bytes, contract/gaps, intent, environment, registration, arguments or preview invalidate acceptance. The current helper continues to return nonzero from review because hard live gates remain open even when the record matches.

## Governed Execution and Results

Follow [the Task Hook phase contract](references/task-hook-handoff.md). Its
pre-import readiness terminal means ready for central preview, not completed
import. Require a reviewed readback plan before preview; collect actual process
and persisted-result evidence only after the approved submission.

Run Book owns the journey. Core Data Loader owns current metadata resolution, immutable preview, permission checks, normal candidate approval, upload, initiation, monitoring and diagnostics. After actual candidate checks and the normal decision pass, send only the approved exact candidate through that declared route. Do not introduce direct REST writes, importBulkData, UCM, ESS or browser-upload substitutes. Combine loader-gap acceptance with the normal approval prompt when the central workflow can retain both decisions; do not ask the user to approve the same import twice.

Application 222/interface 59 uses the five reviewed arguments: explicit batch name, null document ID, null batch ID, ESSCREATE, and the actual interface request ID. ESSCREATE is a product job mode, not a creation-only guarantee. Recheck current runtime registration and resolved arguments; never copy an unrelated ESS ID or tenant-specific registration ID from an example.

Persist sanitized request correlation and partial-result diagnostics in the selected project workflow. Reconcile all requested entities, relationships and values with authoritative persisted readback, including profile, receipt assignments and DFFs. Report Fusion results separately from Journey synchronization. No successful loader status alone proves the requested business outcome.

## Failure and Recovery Contract

- Input validation: return row/field codes; reject the whole invalid request before creating an artifact. Do not echo customer values.
- Calculate diagnostic lengths and row counts from the actual normalized input using local code and the source contract. If not calculated, report the actual field error and documented limit without an estimated count. Never truncate or correct an identifier without a business decision.
- Catalog/routing, authorization, transport or Fusion errors: use the declared central diagnostics and failure taxonomy; do not substitute an endpoint or invent a missing identifier.
- Process timeout or lost response: resume status on the same attempt; retain request IDs and last status. No automatic POST, import, ESS or loader resubmission.
- Partial failure: preserve successes and errors. Corrected input requires new preview and approval; a failed batch is not proof of rollback.
- Artifact persistence: refuse overwrite and report the local failure. Keep customer data and credentials out of tracked repository files.
- Recovery: no inverse-import rollback is promised. Staging purge does not undo customers, accounts or sites.
