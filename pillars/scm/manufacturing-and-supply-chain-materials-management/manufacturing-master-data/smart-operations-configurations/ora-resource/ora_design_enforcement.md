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

## Configuration Scope

Use the fresh template, approved row values, second-reviewer findings and
administrator handoff defined in this skill's Scoped Preparation and Reviewer
Handoffs. Keep task CSV results separate from Run Book load and completion.
Example organizations, UOMs, percentages, reason codes, languages, row counts
and prior approvals are not defaults for a new implementation. Historical
results do not establish readiness or completion for the selected target.
