# Smart Operations Configurations Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Preserve approved package scope | Use the task-specific fresh template and approved row provenance; retain metadata and complete CSV membership |
| 2 | Preserve organization/work-center relationships | Keep organization settings distinct from work-center settings; keep fresh-template identifying and relationship columns |
| 3 | Review shared reasons and languages | Treat reason rows as globally shared; review every proposed shared reason and language row against its approved source |
| 4 | Evaluate verified setup | Require current UOM, organization and plant results through their declared resolvers |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| A prepared package proposes configuration values | Blocker | verify_fsm_artifact_contract | Proposed values lack approved source provenance, template match or validation | Configuration-package author supplies approved values for this implementation; blank exports never supply desired settings or demonstration defaults | Yes, by supplying approved source-backed rows and passing validation; no automatic rewrite |
| Organization or work-center settings are supplied | Blocker | verify_fsm_artifact_contract | Scope or related-record keys do not match the approved requirements and fresh template | Separate organization settings from work-center settings; preserve ORA_WIE_PRODUCTION_EXECUTION_PARAMETER.OrganizationCode and the fresh identifying columns | Only reviewed, approved mapping corrections |
| Shared workstation reason codes or their language rows are supplied | Blocker | verify_fsm_artifact_contract | Review treats reason rows as organization-local, filters/clones them by organization, omits a supplied language row, or changes approved optional blanks | Review all shared changes globally and every supplied language row, including parent key, Language, SourceLang and ReasonCodeName. Matching an approved name does not establish translation quality | Only reviewed, approved corrections; no inferred languages or names |
| Current setup is required before value preview | Blocker | verify_uom | UOM result is absent, stale, inactive or belongs to another selected target/code | Resolve the selected UOM under its declared lookup | Authorized read only; no prerequisite creation |
| Current setup is required before value preview | Blocker | verify_organizations | Organization identity/status/inventory result is absent or mismatched | Resolve the exact same-target organization | Authorized read only; no organization change |
| Current setup is required before value preview | Blocker | verify_manufacturing_plant | Plant/setup result is false, missing, ambiguous or has unrecognized encoding | Resolve the same organization; preserve raw types and encoding warnings | Authorized read only; no plant setup change |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| verify_fsm_artifact_contract | Evaluating proposed package scope, relationships, shared reasons or languages | Current template/prepared identity, actual rows, approved provenance and validator result | ora_reference_lookups.md / Local Lookups |
| verify_uom | Evaluating prerequisite fitness | Selected current UOM identity and active result | ora_reference_lookups.md / Live Lookups |
| verify_organizations | Evaluating prerequisite fitness | Current same-target active inventory organization identity | ora_reference_lookups.md / Live Lookups |
| verify_manufacturing_plant | Evaluating prerequisite fitness | Same organization plant/setup flags, raw types and encoding warning | ora_reference_lookups.md / Live Lookups |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SOC.ENFORCE_DESIGN | decision | 80 | design_enforcement | ready->SOC.CHECK_APPROVAL_BOUNDARY;blocked->SOC.HANDLE_ERROR | SOC.CHECK_DEPENDENCIES | stop | Evaluate Design Rules for the proposed task configuration; no Run Book selection or cross-task sequencing is owned here. |

## Source Authority

This restoration uses the historical Smart Operations task rules in the FSCR source repository at commit efd2e765b2dc89533646189bc44fbcf3eec96427, under pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/ora-resource/. Its five ora_* Markdown sources were verified as existing blobs and byte-identical to the historical source read for this restoration. Dated September 2026 procedure snapshots in docs/SMART-OPERATIONS-CONFIGURATIONS-FSCR-DEVELOPMENT-STORY.md and docs/SMART-OPERATIONS-CONFIGURATIONS-FSCR-QA-GUIDE.md supply the approved historical run context; the latter is the complete guide named by the QA-GUIDE.md pointer. Current published procedure context is the parent and demo versions cited below. None of these dated sources establishes a fresh target result.

The parent [Smart Operations guidance](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452541), version 11, and [demo](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452542), version 6, were read on 2026-10-05 by the coordinating agent. The parent confirms the fresh-template, approved-row, second-reviewer and administrator handoff and distinguishes task CSV results from the separate Run Book load and completion. No reusable rule below supplies a demonstration organization, UOM, percentage, reason code, language choice, row count, or approval as a new implementation default.
