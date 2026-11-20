# Smart Operations Configurations Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Task/package identity | Exact selected target; task-specific fresh template ZIP and export record; prepared immutable ZIP; approved row source and validation report | Stop before value preview or import | Configuration-package author supplies the named local artifacts and exact selected target; validate their contract through verify_fsm_artifact_contract | Any Smart Operations Configurations value preview or execution | verify_fsm_artifact_contract |
| UOM selection | Selected UOMCode for the same target | Stop before lookup or execution | Obtain the explicitly selected code; Fusion verification is owned by ora_reference_lookups.md | Any request changing configuration | |
| Organization selection | Selected OrganizationCode and optional expected string OrganizationId | Stop before lookup or execution | Obtain the explicitly selected organization; identity and plant verification are owned by ora_reference_lookups.md | Any request changing configuration | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Package completeness and current template shape | Require the four task CSV members and ASM_SETUP_CSV_METADATA.xml; preserve the fresh exported headers, column order and task metadata; validate_input node applies the local artifact contract for the complete supplied-input comparison | A prepared ZIP is supplied | verify_fsm_artifact_contract |
| CSV shape remains attached to its columns | Check supplied row width and identifying/related-key columns against the fresh template; preserve quoted fields and optional blank cells. Business approval and organization/shared-reason scope are owned by ora_design_enforcement.md | CSV rows are supplied | verify_fsm_artifact_contract |
| Empty components are explicit | A CSV with headers and no data rows means no supplied rows for that component; retain the required CSV member. A header-only package cannot establish desired business values | A component has no approved rows | verify_fsm_artifact_contract |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SOC.VALIDATE_SCOPE | step | 10 | validate_input | valid->SOC.VERIFY_ARTIFACT;blocked->SOC.HANDLE_ERROR | none | stop | A Smart Operations Configurations request is received; check presence of Required Groups only. Archive/shape/hash validation is performed by SOC.VERIFY_ARTIFACT. |
| SOC.VERIFY_ARTIFACT | step | 20 | validate_input | matched->SOC.VERIFY_CSV_SUPPORT;blocked->SOC.HANDLE_ERROR | SOC.VALIDATE_SCOPE | stop | Apply Field Validation to actual supplied local template/prepared archives and their named provenance records under verify_fsm_artifact_contract; record member/header/hash/row-shape checks. No Fusion call, export or archive preparation. |

## Configuration Scope

Use the fresh template, approved row values, second-reviewer findings and
administrator handoff defined in this skill's Scoped Preparation and Reviewer
Handoffs. Keep task CSV results separate from Run Book load and completion.
Example organizations, UOMs, percentages, reason codes, languages, row counts
and prior approvals are not defaults for a new implementation. Historical
results do not establish readiness or completion for the selected target.
