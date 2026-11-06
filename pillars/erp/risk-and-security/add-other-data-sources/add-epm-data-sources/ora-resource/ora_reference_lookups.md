# Reference Lookups

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| query_seeded_epm_connector_definition | First workflow stage after connector selection and BOSS OAuth readiness | Resolved seeded_source_type_name: EPM-ARCS or EPM-FCCS | GET /api/boss/data/objects/ora/riskMgmtRisk/dataIntegration/v1/connectorDefinitions?$filter=creationStatus='COMPLETED' and connectorStatus='ACTIVE' and sourceTypeName='<seeded_source_type_name>'&$includeTotalItems=true&$limit=1&$fields=id | items containing id | Only sourceTypeName is dynamic; all other query parameters remain fixed; use the approved Core client to encode query values | Selected source type; returned matching id; seeded-connector readiness | At least one returned record confirms setup; an empty items array means no ready match and stops downstream work; malformed or failed responses block readiness |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Successful response contains at least one record with an id | The selected predefined data source is set up; continue to OpenAPI preparation. Status fields are not required in the projected record because the server filter establishes readiness. |
| Successful response contains an empty items array | No ready predefined data source matched. Stop and ask the user to complete setup through the Fusion UI; do not infer that no pending connector exists, invent a connector ID, or create a seeded connector. |
| Request fails, items is missing or malformed, or a returned record lacks an id | Block readiness and return sanitized diagnostics. |
| hasMore or a total count is present | Neither establishes readiness without a returned record. No pagination is needed for this limit-one existence check; multiple matching records do not make readiness ambiguous. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EPMDS.QUERY_SEEDED_CONNECTOR | step | 30 | reference_lookup | seeded->EPMDS.ENFORCE_DESIGN;empty->EPMDS.ENFORCE_DESIGN;incomplete->EPMDS.HANDLE_ISSUE;unauthorized->EPMDS.HANDLE_ISSUE;failed->EPMDS.HANDLE_ISSUE | EPMDS.CHECK_DEPENDENCIES | stop | After connector selection and BOSS OAuth readiness |
| EPMDS.SEEDED_READY | step | 90 | evaluate_result | ready->EPMDS.VALIDATE_RESPONSE_SCHEMA | EPMDS.ENFORCE_DESIGN | stop | At least one matching record with an id was returned by the filtered GET; proceed to OpenAPI preparation |
