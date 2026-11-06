# Reference Lookups

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_connector_source_type | Every request before dependency evaluation | Connector type supplied by the request | Match exact registry key OCI or USER-DEFINED in pillars/erp/risk-and-security/add-other-data-sources/connector-source-types.json | OCI maps to sourceTypeName OCI and sourceTypeCode 2; USER-DEFINED maps to sourceTypeName User-Defined and sourceTypeCode 10 | Stop and request one supported connector type; do not accept caller-supplied source type names or codes |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_oci_seeded_source | Resolved source type is OCI and BOSS OAuth readiness is confirmed | Centrally resolved sourceTypeName; OCI for this prerequisite | GET /api/boss/data/objects/ora/riskMgmtRisk/dataIntegration/v1/connectorDefinitions?$filter=creationStatus='COMPLETED' and connectorStatus='ACTIVE' and sourceTypeName='<source_type_name>'&$includeTotalItems=true&$limit=1&$fields=id | items containing id | Only sourceTypeName is dynamic; other parameters remain fixed; encode query values through the approved Core client | Matching id; predefined-source readiness | At least one returned record confirms setup; empty items stops downstream work; failed or malformed responses block readiness |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| The resolved source type is OCI | Continue to the conditional OCI seeded-source readiness dependency. |
| The resolved source type is USER-DEFINED | Skip the OCI seeded-source readiness dependency. |
| The successful filtered GET returns at least one record with an id | Treat predefined-source readiness as verified; status fields need not be projected because the server filter establishes readiness. No pagination or unique-match requirement applies to this existence check. |
| The filtered GET returns an empty items array | No ready match was found. Stop and request setup in the Data Integration UI; do not infer that pending connectors are absent. |
| The request fails, items is missing or malformed, or a record lacks an id | Block readiness. Neither hasMore nor a total count alone establishes setup. |
| Recovering a newly registered connector | The predefined-source existence check cannot verify the exact registration or authorize recreation; follow the separate registration recovery contract in SKILL.md. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CDS.RESOLVE_SOURCE_TYPE | step | 20 | evaluate_result | resolved->CDS.CHECK_DEPENDENCIES;invalid->CDS.HANDLE_ISSUE | CDS.VALIDATE_RESPONSE_SCHEMA | stop | After connector type and OpenAPI response schema validation and before dependency evaluation |
| CDS.VERIFY_OCI_SEEDED | step | 40 | reference_lookup | seeded->CDS.ENFORCE_DESIGN;empty->CDS.HANDLE_ISSUE;incomplete->CDS.HANDLE_ISSUE;unauthorized->CDS.HANDLE_ISSUE;failed->CDS.HANDLE_ISSUE | CDS.CHECK_DEPENDENCIES | stop | Resolved source type is OCI |
