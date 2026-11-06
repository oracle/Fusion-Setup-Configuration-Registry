# Workstations FSM Dependency Readiness

## Source Evidence

| Source | Verified Fact | Source Anchor |
|---|---|---|
| Authoring skills for resources using FSM import/export | An import ZIP must be prepared only from a newly fetched live template. A static or previously downloaded template must not substitute for the target-environment template. Validate ZIP contents, filenames, directory structure, and manifest requirements before import. Import requires explicit approval after package validation. | [Authoring skills for resources using FSM import/export](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21459835549), Step 2 — Author Task Resources |


Template fetching and package preparation are owned by their selected core/shared workflows. These task resources verify documented prerequisite outcomes only; an unresolved verification contract does not become a local operation. Import approval is owned by ora_error_handling.md, not a blank dependency resolver.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Validated input and current CSV contract | Require the input/contract checks before accepting package preparation |
| 2 | Fresh live Workstations template | Require verification of the selected target/task's fresh template through its named contract |
| 3 | Prepared FSM ZIP and layout validation | Require verification of template linkage, changed files and complete layout/manifest validation |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| WORKSTATIONS.CSV_SUPPORT | Current target task CSV support | Yes | Before accepting FSM processing | Verify | Current exact same-target Fusion setupTasks flag response | verify_workstations_csv_support | Current task support is separate from CSV semantics, template provenance and package layout | Use the documented live flag lookup; never substitute a local catalog result | Exact task identity, raw flags, selected flag and CSV-support finding |
| WORKSTATIONS.FRESH_TEMPLATE | Fresh target-environment Workstations template | Yes | Before accepting FSM package preparation | Verify | Actual approved task-level template export and downloaded template_package from the selected shared.setup-export.task-level-export or supported native FSM UI, bound to the exact task/target/process/artifact; carry its complete original provenance into this continuation as specified by verify_workstations_fresh_template | verify_workstations_fresh_template | Source requires newly fetched target-environment template | Require verify_workstations_fresh_template findings from the selected shared helper or supported native FSM UI; an approved current-target download with complete adopted original provenance remains usable across a continuation; static or unlinked prior templates cannot substitute | Fresh export archive identity/hash, target/task/process, actual original download-before-preparation ordering adopted by this validation; report Activity Start Time separately from unavailable precise download timestamp |
| WORKSTATIONS.PACKAGE_FROM_TEMPLATE | Prepared ZIP derived from the fresh template | Yes | Before accepting package validation | Verify | Actual prepared setup_data_zip and explicitly authorized local shared.validation.setup-data-validator validation_report bound to the verified fresh-template and package hashes | verify_workstations_package_contract | Source requires preserving fresh template layout and manifest | Require verify_workstations_package_contract complete linked findings; supplied files or a bare ready label alone are insufficient | Package identity, fresh-template link and changed-file list |
| WORKSTATIONS.PACKAGE_LAYOUT | ZIP layout validation | Yes | Before import approval | Verify | Actual complete local shared.validation.setup-data-validator findings for the exact template/package member, header and unchanged manifest comparisons | verify_workstations_package_contract | Detects altered members, folders or manifest requirements | Require all verify_workstations_package_contract structural findings; no Oracle parser acceptance or current import readiness inferred | Complete validation finding |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WORKSTATIONS.FSM_PREPARE | step | 15 | resolve_dependency | ready->WORKSTATIONS.RESOLVE_DESIGN_REFERENCES;missing->WORKSTATIONS.RETURN_ISSUES | WORKSTATIONS.CHECK_PACKAGE_CONTRACT | stop | Evaluate the named Dependency Rules from prior verified outcomes only; do not fetch/export, prepare an archive or infer local readiness. Apply these FSM package dependencies only to explicitly selected FSM input. For an explicitly selected REST workbook, ready records that these FSM-only dependencies are not applicable. Missing or ambiguous route context or an unmet applicable dependency returns missing. Continue common domain checks; no REST validation or approval is waived. |
