# Reference Organization Items Import Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 0 | Item Index | Retain available from the declared Core REST lookup before preparing input. |
| 1 | Source and task | Pass input validation against the current template using captured data. |
| 2 | Readiness evidence | Evaluate supplied business context and Core-returned routing evidence in ora_reference_lookups.md. |
| 3 | Business objects | Confirm existing item/organization context and conditional structures from supplied business evidence. |
| 4 | Scope | Apply task-local organization/structure policy before preview. |
| 5 | Core handoff | Return rule results to the selected Core workflow for approval and submission. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| item_search_index_readiness | Item Index availability | Yes | Before preparation and approval | Verify | Same-validation-cycle Core REST result | verify_item_search_index_readiness | Require the declared Item Index availability gate | Continue only for available; unknown index returns a separate orchestration handoff | index_readiness_status |
| reference_org_readiness | Existing items, organizations and conditional structures | Yes | Before preview | Verify | Named project baseline/business-scope evidence | verify_reference_org_readiness | This process assigns existing items and must preserve intended organization/structure scope | Supply missing business identities and association/structure context | Business-scope result |
| exact_loader_route | Reference Organization Items FBDI registration and CSV batch/scope | Yes | Before preview | Verify | Core-returned successful native-FBDI routing/preflight, Core-bound final native CSV members and selected Run Book/task context | verify_reference_org_loader_route | Core owns registration, filename coverage, account/adapter resolution and configured mode; the pillar checks returned route/source/task consistency | Stop on missing/conflicting evidence; do not guess an adapter or mode code | Core-validated BO route, CSV Batch ID, requested mode intent and active task context retained in ordered Core rule results; no claim of independent deployed-mode verification |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| REF_ORG_ITEMS.CONFIRM_DEPENDENCIES | step | 5 | resolve_dependency | ready->REF_ORG_ITEMS.VALIDATE_SCOPE;blocked->REF_ORG_ITEMS.FAILED | REF_ORG_ITEMS.RESOLVE_CONTEXT | stop | Require both resolved prerequisite results to pass; missing or conflicting business/route evidence blocks preview; environment checks remain with core. |
