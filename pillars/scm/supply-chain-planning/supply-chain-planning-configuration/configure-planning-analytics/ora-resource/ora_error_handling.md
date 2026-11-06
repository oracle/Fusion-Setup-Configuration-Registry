# Configure Planning Analytics Lookup Outcomes

## Error Situations

| Situation | What Should Happen |
|---|---|
| A requested catalog, dimension, hierarchy, planning measure, planning measure group, or requested planning level has no exact match | Stop the configuration selection and report the requested identity as missing. |
| A name-based lookup returns more than one exact match | Stop the configuration selection and require an exact identifier. |
| A lookup response identity differs from the supplied path identifier | Stop the configuration selection; do not use the returned record. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPA.DONE_LOOKUP_DIMENSION_CATALOGS | terminal | 100 | terminal | none | CPA.LOOKUP_DIMENSION_CATALOGS | stop | Return only the requested find_dimension_catalogs lookup result; no write |
| CPA.DONE_LOOKUP_DIMENSION_CATALOG | terminal | 101 | terminal | none | CPA.LOOKUP_DIMENSION_CATALOG | stop | Return only the requested find_dimension_catalog_by_id lookup result; no write |
| CPA.DONE_LOOKUP_CATALOG_HIERARCHIES | terminal | 102 | terminal | none | CPA.LOOKUP_CATALOG_HIERARCHIES | stop | Return only the requested find_dimension_catalog_hierarchies lookup result; no write |
| CPA.DONE_LOOKUP_CATALOG_HIERARCHY | terminal | 103 | terminal | none | CPA.LOOKUP_CATALOG_HIERARCHY | stop | Return only the requested find_dimension_catalog_hierarchy_by_id lookup result; no write |
| CPA.DONE_LOOKUP_DIMENSIONS | terminal | 104 | terminal | none | CPA.LOOKUP_DIMENSIONS | stop | Return only the requested find_dimensions lookup result; no write |
| CPA.DONE_LOOKUP_DIMENSION | terminal | 105 | terminal | none | CPA.LOOKUP_DIMENSION | stop | Return only the requested find_dimension_by_code lookup result; no write |
| CPA.DONE_LOOKUP_DIMENSION_HIERARCHIES | terminal | 106 | terminal | none | CPA.LOOKUP_DIMENSION_HIERARCHIES | stop | Return only the requested find_dimension_hierarchies lookup result; no write |
| CPA.DONE_LOOKUP_DIMENSION_HIERARCHY | terminal | 107 | terminal | none | CPA.LOOKUP_DIMENSION_HIERARCHY | stop | Return only the requested find_dimension_hierarchy_by_id lookup result; no write |
| CPA.DONE_LOOKUP_PLANNING_HIERARCHIES | terminal | 108 | terminal | none | CPA.LOOKUP_PLANNING_HIERARCHIES | stop | Return only the requested find_planning_hierarchies lookup result; no write |
| CPA.DONE_LOOKUP_PLANNING_HIERARCHY | terminal | 109 | terminal | none | CPA.LOOKUP_PLANNING_HIERARCHY | stop | Return only the requested find_planning_hierarchy_by_id lookup result; no write |
| CPA.DONE_LOOKUP_MEASURE_CATALOG | terminal | 110 | terminal | none | CPA.LOOKUP_MEASURE_CATALOG | stop | Return only the requested find_planning_measure_catalog lookup result; no write |
| CPA.DONE_LOOKUP_MEASURE_CATALOG_DETAILS | terminal | 111 | terminal | none | CPA.LOOKUP_MEASURE_CATALOG_DETAILS | stop | Return only the requested find_planning_measure_catalog_by_id lookup result; no write |
| CPA.DONE_LOOKUP_MEASURE_CATALOG_MEASURES | terminal | 112 | terminal | none | CPA.LOOKUP_MEASURE_CATALOG_MEASURES | stop | Return only the requested find_planning_measure_catalog_measures lookup result; no write |
| CPA.DONE_LOOKUP_PLANNING_MEASURES | terminal | 113 | terminal | none | CPA.LOOKUP_PLANNING_MEASURES | stop | Return only the requested find_planning_measure_by_id_or_name lookup result; no write |
| CPA.DONE_LOOKUP_PLANNING_MEASURE_GROUPS | terminal | 114 | terminal | none | CPA.LOOKUP_PLANNING_MEASURE_GROUPS | stop | Return only the requested find_planning_measure_group_by_id_or_name lookup result; no write |
| CPA.DONE_LOOKUP_GROUP_PLANNING_MEASURES | terminal | 115 | terminal | none | CPA.LOOKUP_GROUP_PLANNING_MEASURES | stop | Return only the requested list_planning_measures_in_group lookup result; no write |
| CPA.DONE_LIST_PLANNING_LEVELS | terminal | 119 | terminal | none | CPA.LIST_PLANNING_LEVELS | stop | Return only the requested list_planning_levels lookup result; no write |
| CPA.DONE_FIND_PLANNING_LEVEL_BY_NAME | terminal | 120 | terminal | none | CPA.FIND_PLANNING_LEVEL_BY_NAME | stop | Return only the requested find_planning_level_by_name lookup result; no write |
| CPA.DONE_FIND_PLANNING_LEVEL_BY_ID | terminal | 121 | terminal | none | CPA.FIND_PLANNING_LEVEL_BY_ID | stop | Return only the requested find_planning_level_by_id lookup result; no write |
| CPA.ITEM_ATTRIBUTE_VALIDATED | terminal | 130 | terminal | none | CPA.VALIDATE_ITEM_ATTRIBUTE | stop | Return successful item-level name and supplied datatype validation; no write |
| CPA.ORGANIZATION_ATTRIBUTE_VALIDATED | terminal | 131 | terminal | none | CPA.VALIDATE_ORGANIZATION_ATTRIBUTE | stop | Return successful organization-level name and supplied datatype validation; no write |
| CPA.LEVEL_ATTRIBUTES_COMPLETE | terminal | 132 | terminal | none | CPA.SELECT_LEVEL_ATTRIBUTE_NAMES | stop | Return existing attributes without creation validation or a write |
| CPA.DIMENSION_DELETION_CHECKED | terminal | 133 | terminal | none | CPA.ENFORCE_CATALOG_DELETION | stop | Return dimension-catalog deletion eligibility; no deletion or approval |
| CPA.MEASURE_DELETION_CHECKED | terminal | 134 | terminal | none | CPA.ENFORCE_MEASURE_CATALOG_DELETION | stop | Return measure-catalog deletion eligibility; no deletion or approval |
| CPA.LOOKUP_FAILURE | terminal | 999 | terminal | none | none | stop | Classify and persist the failure using Error Classifications and Disclosure Rules; return missing, unsupported, invalid, ambiguous, failed or blocked details and the corrective action; no write |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Missing identity, unsupported level, invalid attribute/datatype, no exact match or conflicting returned identity | Stop; identify the invalid or missing field and correction. |
| catalog_or_metadata_mismatch | Ambiguous identity or unsupported task metadata | Stop; request an exact identity or resolve catalog metadata. |
| auth_expired_or_invalid | Cached token rejected with 401/403 | Delegate one refresh retry to the REST client; never replace an explicitly supplied token. |
| authorization_or_privilege | Missing privilege or 403 after refresh | Stop; recommend role/access diagnostics. |
| transport_or_environment | Connection failure, request timeout or incomplete page retrieval | Stop; report the selected environment and safe next check. |
| fusion_api_error | Other HTTP error or malformed response | Stop; retain sanitized HTTP status, endpoint and ECID when available. |
| artifact_persistence | Diagnostic or validation artifact cannot be saved | Stop; report the failed destination without claiming persistence. |
| approval_blocker | Deletion gate blocked or execution approval absent | Stop; report the blocker; eligibility never authorizes a write. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Failure handoff | status, stage, failure_class, message, recommended_action, selected environment alias, task code, skill_id, current Rule ID, endpoint path, HTTP status/ECID when available, artifact_refs and safe resume stage. Preserve completed checks and an errors array for partial failures. |
| Durable evidence | With project context, save diagnostics.json and a schema-valid validation-result.json under the manifest's task artifact directory using its versioning policy. Register both through core.project-mgmt.artifact-registry-manager; record a failed run through core.project-mgmt.project-state-manager under project/{project_id}/state/runs/ and log token usage. |
| Schema and redaction | Keep failure_class and diagnostic details in the separate diagnostic artifact; validation findings link it through artifact, and skill runs through artifact_refs. Follow schemas/validation-result.schema.json and schemas/skill-run.schema.json. Omit credentials, tokens, headers, tenant URLs, sensitive payloads and customer values. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Before live lookup | Do not call Fusion until the active workflow selects the declared GET, confirms environment/privileges and supplies finite request timeout and pagination limits. Use core.fusion-api.rest-api-client; do not implement transport here. |
| Retry or retrieval failure | Do not retry transport failures automatically, exceed pagination limits, or treat incomplete retrieval as absence. After the client's single cached-token retry, stop on failure. Resume only after correction through the invoking workflow. |
| Failure or blocked deletion | Do not import, delete, substitute endpoints or replay a mutation. Data Loader owns mutation validation and approval. If persistence fails, retain sanitized failure details in the handoff and stop. |

These rules follow governance/error-handling-guidelines.md and apply at CPA.LOOKUP_FAILURE and preflight failures before graph entry. Without project context, return the same sanitized diagnostic handoff and state that it was not persisted; obtain project context before durable implementation work continues.
