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

## Source Authority

This restoration uses the historical Smart Operations task rules in the FSCR source repository at commit efd2e765b2dc89533646189bc44fbcf3eec96427, under pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/ora-resource/. Its five ora_* Markdown sources were verified as existing blobs and byte-identical to the historical source read for this restoration. Dated September 2026 procedure snapshots in docs/SMART-OPERATIONS-CONFIGURATIONS-FSCR-DEVELOPMENT-STORY.md and docs/SMART-OPERATIONS-CONFIGURATIONS-FSCR-QA-GUIDE.md supply the approved historical run context; the latter is the complete guide named by the QA-GUIDE.md pointer. Current published procedure context is the parent and demo versions cited below. None of these dated sources establishes a fresh target result.

The parent [Smart Operations guidance](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452541), version 11, and [demo](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452542), version 6, were read on 2026-10-05 by the coordinating agent. The parent confirms the fresh-template, approved-row, second-reviewer and administrator handoff and distinguishes task CSV results from the separate Run Book load and completion. No reusable rule below supplies a demonstration organization, UOM, percentage, reason code, language choice, row count, or approval as a new implementation default.
