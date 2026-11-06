---
skill_id: "scm.product-management.items.import-items"
name: "Import Items Setup Task Guidance"
description: "Prepares a validated immutable Item Import FBDI ZIP from the current public Oracle template and hands it unchanged to core.data-loader."
layer: "pillar"
pillar: "SCM"
offering: "Product Management"
functional_area: "Items"
functional_area_code: "ORA_EGP_FA_ITEMS"
task_code: "EGP_IMPORT_ITEMS"
task_name: "Import Items"
parent_skill_id: "scm.product-management.items"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
dataloader_import_mode: "FBDI"
businessObject: "item"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "import"
execution_mode: "hybrid"
owner_team: "SCM product management pillar team"
version: "0.1.2"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
  - "customer_item_source"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "normalized_item_mapping"
  - "generated_fbdi_zip"
  - "fbdi_preview"
  - "core_data_loader_handoff"
  - "skill_run_record"
  - "token_usage_record"
uses_core:
  - "core.data-loader"
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
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/items/import-items/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/scm/product-management/items/import-items/current/"
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
  - "Performs a read-only Fusion item-search readiness request through core.fusion-api.rest-api-client."
  - "Downloads the current public Oracle Item Import template for the current run."
  - "Creates transient CSV and ZIP artifacts outside tracked repository and project-workspace locations."
  - "Hands an immutable validated ZIP to core.data-loader without initiating a load."
required_privileges:
  - "Access to the target Oracle Fusion environment."
  - "Privileges required to invoke the Fusion item-search endpoint."
---

# Import Items Setup Task Guidance

## Purpose

Prepare an Oracle Item Import FBDI package from customer-supplied data. Fetch
the current public Oracle `ItemImportTemplate.xlsm`, map and validate the data
against that template, generate one ordered immutable ZIP, and hand the exact
same ZIP to `core.data-loader` for any later loader operation.

## Setup Task Skill Contract

- task_code: `EGP_IMPORT_ITEMS`
- task_name: `Import Items`
- dataloader_import_mode: `FBDI`
- businessObject: `item`
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Preparation and Validation Workflow

The item-index check establishes search availability only. It does not verify
index-build completion or completeness of indexed data; build completion belongs
to the separate index-management and ESS status workflow. A valid empty index
may pass. HTTP 200 alone is insufficient: require an empty `hits.hits` array,
explicit boolean `timed_out: false`, and an explicit integer `_shards.failed: 0`
with no response error. Missing or incorrectly typed health fields fail closed.

Read `ora-resource/ora_input_validation.md`,
`ora-resource/ora_dependency_readiness.md`,
`ora-resource/ora_error_handling.md`, and
`ora-resource/ora_rule_registry.json` before preparing a package.

## Template and Package Contract

For every run, fetch `ItemImportTemplate.xlsm` from the current public Oracle
File-Based Data Import Item page. Record the page URL, workbook URL, retrieval
time, SHA-256 digest, and sheet sequence. The workbook and its linked control
files are the sole schema authority for that run.

Read each populated sheet's ordered export columns, technical names, types,
required markers, validations, and allowed values. Preserve its complete column
order, trailing empty fields, encoding, delimiter, quoting, and null
conventions. For `EGP_SYSTEM_ITEMS_INTERFACE`, exclude only the workbook-only
`Name` metadata column; the first headerless CSV field is `TRANSACTION_TYPE`.

Stop on template drift: a changed sheet sequence, output filename, or export
contract requires updating this task skill before creating a package.

### Package Contract

Create headerless root-level CSV members only for populated sheets. Use the
current template's prescribed filenames and preserve this relative order:

1. `EgpSystemItemsInterface.csv`
2. `EgpItemRevisionsInterface.csv`
3. `EgpItemCategoriesInterface.csv`
4. `EgpItemRelationshipsIntf.csv`
5. `EgoItemAssociationsIntf.csv`
6. `EgoItemIntfEffb.csv`
7. `EgoItemIntfEfftl.csv`
8. `EgoItemRevisionIntfEffb.csv`
9. `EgoItemRevisionIntfEfftl.csv`
10. `EgoItemSupplierIntfEffb.csv`
11. `EgoItemSupplierIntfEfftl.csv`
12. `EgoStyleVariantAttrvsIntf.csv`
13. `EgpTradingPartnerItemsIntf.csv`
14. `EgpItemAttachmentsIntf.csv`
15. `EgpMpnSpnRelLinkageInt.csv`
16. `AcaItemCostInterface.csv`
17. `EgpItemOrgAssociations.csv`

Use one numeric Batch ID consistently in every populated member at its template
position; in `EgpSystemItemsInterface.csv` it is the second CSV field.


## Preflight Checks

Before any lookup, template retrieval, or transient file creation:

1. Confirm the exact target Fusion environment and that the requested operation
   is read-only readiness checking plus local package preparation.
2. Confirm access and privileges for the item-search lookup. Route the lookup
   only through `core.fusion-api.rest-api-client` after loading its applicable
   standard Fusion REST instructions.
3. Confirm a readable customer source or prebuilt ZIP and resolve the current
   public Oracle template URL for this run.
4. Confirm every transient destination is controlled, writable, and outside
   tracked repository and project-workspace paths.
5. Confirm no upload, import, ESS submission, monitoring, overwrite, deletion,
   or retry of a live mutation is requested in this skill.

Fail before side effects when any check is missing, ambiguous, unauthorized, or
outside the requested workspace boundary.

1. Accept customer item data or a prebuilt FBDI ZIP. Treat supplied facts as
   evidence, not as Oracle-ready mappings.
2. Run the item-search readiness lookup through
   `core.fusion-api.rest-api-client`, following
   `ora-resource/ora_reference_lookups.md` and the compiled task graph.
3. Fetch the current public Oracle `ItemImportTemplate.xlsm` for this run.
   Record its public page and workbook URLs, retrieval time, SHA-256 digest,
   and sheet sequence. Never use remembered or stale layout details.
4. Map each source fact to the current template. Resolve every required or
   ambiguous business value before generating CSV files. Source System Code is
   optional: use it when supplied; otherwise leave its template field empty
   without prompting or applying a default.
5. Generate headerless CSV members using the template's prescribed filenames,
   columns, field order, encoding, and ZIP-member order. Create the ZIP only
   in a customer-approved or controlled transient location.
6. Reopen and validate the ZIP against the same template: safe root-level
   members, exact member names and order, field counts including trailing empty
   fields, data types and constraints, coherent references, one numeric Batch
   ID, and SHA-256-bound preview. Use
   `scripts/validate_item_import_archive.py` with a contract derived from that
   run's current workbook for the deterministic archive checks; never use the
   synthetic test fixture as a production template contract.
   The validator uses strict CSV parsing. Invalid quoting or fields exceeding
   Python's configured `csv.field_size_limit()` (131072 characters by default)
   return a sanitized `csv_format` issue and `failed` status; the CLI exits 1.
   This parser limit does not replace the workbook's field-specific constraints.
7. Hand the validated ZIP unchanged to `core.data-loader` with task context,
   template provenance, ZIP digest, member manifest, row counts, mapping
   preview, and Batch ID. For the Data Loader preflight invocation, pass
   `--business-object item` so the registered Item Import object is selected
   when live FBDI metadata produces a tie. The loader must still match the ZIP
   CSV filenames to live metadata and reject `item` if it is not a
   highest-scoring candidate. Do not pass this option on the later approved
   submission, which reuses the preflight route and immutable artifact.

## Failure, Retry, and Recovery Contract

- Use the failure classes and disclosure rules in
  `ora-resource/ora_error_handling.md`.
- Permit one cached-token refresh after a 401 or 403 only through the core REST
  client. Do not replace an explicitly supplied token.
- Do not automatically retry the read-only GET, template retrieval, ZIP
  handoff, or any later live loader operation after an uncertain result.
- Bound each lookup and template retrieval to the caller-provided timeout. On
  timeout, stop and return the environment, operation, stage, elapsed time,
  last status, sanitized diagnostic, and one safe next action.
- Discard incomplete transient artifacts after local validation failure. A
  changed source, template, mapping, member, member order, Batch ID, basename,
  or digest requires a complete new validation cycle.
- Return a machine-readable status of `ready`, `blocked`, or `failed`, together
  with failure class, stage, sanitized message, recommended action, environment,
  artifact references, and available HTTP status or ECID.

## Redaction and Disclosure

Never print or persist credentials, access or refresh tokens, authorization
headers, token-cache contents, client secrets, private keys, certificates, full
base64 content, raw customer rows, complete customer payloads, or unsanitized
Fusion response bodies. Mapping previews and diagnostics must use synthetic,
masked, aggregated, or otherwise non-sensitive values. Record only the minimum
environment identity and external diagnostic identifiers needed for remediation.

## Immutable Handoff Boundary

The ZIP bytes, basename, members, member order, and SHA-256 digest must remain
unchanged after validation. Any alteration requires a new template-driven
validation cycle.

This skill must not upload the ZIP, call an ESS job, initiate or monitor an
import, poll a request, or directly call a Fusion execution endpoint. It must
not invoke a product-specific loader or construct transport parameters.
`core.data-loader` exclusively owns any subsequent validation, approval,
upload, import initiation, monitoring, and diagnostics.

## Reviewers

SCM Pillar Development Lead or SME and an FSCR A-Team/core reviewer;
functional, automation, and QA review as applicable.

## Deterministic Validation Evidence

Run the synthetic contract suite after changing package or task-graph behavior:

```text
python -m unittest discover -s pillars/scm/product-management/items/import-items/noship/tests -p "test_*.py"
```

The suite covers valid archives, member ordering, unsafe paths, field counts,
Batch ID consistency, digest changes, and lookup branches. Its fixture is
synthetic test evidence only and must not be used to prepare customer data.

## Outputs

Return local validation results and the immutable handoff evidence. Do not
store raw customer rows, intermediate CSVs, workbook copies containing customer
data, or the generated ZIP in the repository or project workspace.

## Boundaries

- Use Item Import FBDI; do not route through FSM CSV import.
- Do not invent missing customer values or silently discard source facts.
- Do not expose credentials, tokens, authorization headers, or UCM details.
- Do not call Fusion REST directly; use `core.fusion-api.rest-api-client` for the
  documented read-only readiness lookup.
- Use the parent skill `scm.product-management.items` for functional-area
  sequencing and scope decisions.
