# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Validate connector selection | Retain one supported connector type, connector name, and exact seeded source type name. |
| 2 | Query seeded connector | Run the read-only BOSS connectorDefinitions query through the approved core client. |
| 3 | Classify result | Use query_seeded_epm_connector_definition readiness; proceed only when setup is confirmed, stop for no ready match, and block malformed evidence. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Every request | Error | query_seeded_epm_connector_definition | The exact BOSS seeded-connector query has not completed | Run the approved read-only lookup before any downstream workflow | Yes |
| Seeded-connector query returns an empty collection | Error | query_seeded_epm_connector_definition | No ready predefined data source matched; a pending connector may exist | Ask the user to complete seeded connector setup through the Fusion UI; do not create it from this task | No |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| query_seeded_epm_connector_definition | Before any downstream workflow | Selected source type; returned matching id; seeded-connector readiness | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EPMDS.ENFORCE_DESIGN | decision | 40 | design_enforcement | ready->EPMDS.SEEDED_READY;not_seeded->EPMDS.SEEDED_CONNECTOR_MISSING;blocked->EPMDS.HANDLE_ISSUE | EPMDS.QUERY_SEEDED_CONNECTOR | stop | After seeded-connector lookup |
