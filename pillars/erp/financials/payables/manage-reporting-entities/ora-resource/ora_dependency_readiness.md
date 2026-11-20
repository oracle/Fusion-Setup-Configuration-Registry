# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Existing BU | Resolve intended BU/enterprise and Payables eligibility |
| 2 | Existing location and set | Validate exact location identity and matching context |
| 3 | Balancing children | Require supplied values, exact parent linkage and no duplicate child tuples; FSM validates eligibility |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| MRE.BU | Business unit | Yes | Create | Verify | Fusion | resolve_reporting_entity_bu | OrgId is required and validated against Payables BU | Select existing intended BU; do not create prerequisites implicitly | OrgId internally |
| MRE.LOCATION | Location and set | Yes | Create | Verify | Fusion | resolve_reporting_entity_location | LocationId is required | Use intended location; do not require bill-to eligibility from another task | Matching context |
| MRE.SET | Reference set | Yes | Header create requires nonblank SetCode; verify an explicitly supplied set | Verify | Fusion | validate_reporting_entity_set | Required location matching context | Obtain intended location set before candidate generation; never silently default COMMON | SetCode preserved |
| MRE.BSV | Primary balancing values | Yes | Create balancing lines | Local checks; eligibility by FSM | User input |  | Require a nonblank value, exact parent and no duplicate child tuple | Supply intended balancing values; report any FSM rejection | Supplied values unchanged |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRE.DEP | step | 20 | resolve_dependency | success->MRE.LOOKUP;failure->MRE.ERROR | MRE.INPUT | stop | Create or update within the approved task scope |
