# MPS dependency readiness



## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Owning system and account | Resolve unchanged portable identity and safe baseline |
| 2 | Setting definition | Classify using owning system plus option code |
| 3 | Referenced setup | Resolve eligible choices or record manual completion |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| MPS.PARENT | Owning system/account | Yes | child changes | Blocked | Verified target identity and sanitized matching baseline |  | Missing or ambiguous parent prevents safe matching | Resolve exact parent before packaging | Unchanged portable parent identity |
| MPS.DEFINITION | Setting definition | Yes | account option values | Blocked | Verified target definition keyed by owning system and option code |  | Unknown sensitivity cannot be guessed | Complete unresolved or sensitive option manually | SecuredFlag and reviewed semantics; never secret values |
| MPS.REFERENCE | Existing referenced configuration | Conditional | reference-valued options | Blocked | Successful documented lookup or reviewed import validation/resolution contract |  | No prerequisite creation through MPS | Use reference-contracts.json; UI-only choices remain manual | Canonical ordinary code only |


These rows describe blocking prerequisites when absent; satisfied evidence clears only the corresponding condition. Do not treat their existence as a blanket task prohibition. Source: SRC-MPS-ADE-001, SRC-MPS-OPTION-006 and registered resolver evidence.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPS.DEPENDENCIES | step | 40 | resolve_dependency | pass->MPS.DEFAULTS;fail->MPS.RETURN_ISSUES | MPS.LOOKUPS | stop | always |
