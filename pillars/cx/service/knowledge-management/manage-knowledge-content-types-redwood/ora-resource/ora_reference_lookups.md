# Content Type Reference Lookups

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_default_knowledge_locale | Preparing localized rows for a Content Types Redwood FSM package | defaultLocale in ORA_CSO_LOCALE_OBJECT.csv from the completed current Manage Knowledge Locales export | Read the single exported defaultLocale value and use its exact locale code | Default locale used for localized CSV row ordering | Stop if the export has no unambiguous defaultLocale value. |
| resolve_content_types_fsm_export | Review or prepare a Redwood content-type FSM change | Completed same-task export and ASM_SETUP_CSV_METADATA.xml | Require exactly one completed export for ORA_CSO_CONTENT_TYPES_INDEXING_MGMT_REDWOOD; reconcile its actual members, headers, node order and root/child links with the task FSM contract; use the export to resolve existing target identities | Current source reference, package contract, existing content-type identities and field/linkage evidence | Stop on absent/ambiguous baseline, unsupported structure or unresolved target identity; do not infer a schema from REST. |
| resolve_active_knowledge_locales | Localized content-type or schema-attribute rows are prepared | Completed current Manage Knowledge Locales export; ORA_CSO_ACTIVE_LOCALE_OBJECT.csv | Read active locale rows from the completed owner-task export; require unambiguous exported recordId values and retain them exactly | Exact active locale codes for required localized rows | Stop if the export or active-locale state is unavailable, ambiguous or incomplete; no REST state substitute. |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| get_content_type_by_id | Viewing a specific Knowledge content type | Content type record ID | /km/api/v1/contentTypes/{id} | recordId, name, referenceKey, counterPrefix, description, localizedAttributes, contentSchema, enableIndexing, indexStatus | Retrieve the object whose recordId exactly matches the supplied required id path parameter | Content type properties, localized values, schema attributes, indexing setting, and indexing status | Stop and report the invalid id; this single-object endpoint has no multiple-match result. |
| resolve_department_user_groups | Attribute visibility is restricted | Selected department and its caller-supplied stripe code | GET /km/api/v1/userGroups?mode=FULL&limit=<limit>&offset=<offset> | items.recordId, items.referenceKey, items.name, items.stripeCD, hasMore, limit, offset | Follow pagination while hasMore is true; retain only groups whose stripeCD exactly matches the supplied department stripe code; resolve each requested group by exact recordId or referenceKey | Available department user-group identities and names | Stop if the department stripe code is missing, the response lacks stripe data or is incomplete, or a requested group has no unique match in the selected department. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A content type is requested by record ID | Use the documented GET endpoint in FULL mode to retrieve the ContentType object. |
| A visibility lookup contract is not documented | Stop before applying restricted visibility and obtain the authoritative read-only lookup contract. |
| Localized rows are required | Resolve active Knowledge locales and write their exact locale code to localeId. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CONTENT_TYPES_REDWOOD.REVIEW_EXPORT | step | 2 | evaluate_result | found->CONTENT_TYPES_REDWOOD.REVIEW_COMPLETE;failure->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.VALIDATE | stop | Run local resolve_content_types_fsm_export for review and return exported setup data only; no mutation validation or title/default requirement is applied to a read. |
| CONTENT_TYPES_REDWOOD.BASELINE_LOOKUP | step | 5 | evaluate_result | found->CONTENT_TYPES_REDWOOD.LOCALES_LOOKUP;failure->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.VALIDATE_CHANGE | stop | Run local resolve_content_types_fsm_export; require the current exact task baseline, actual schema/member contract and one exported target for update, or an approved unique new identity for create. |
| CONTENT_TYPES_REDWOOD.LOCALES_LOOKUP | step | 6 | evaluate_result | found->CONTENT_TYPES_REDWOOD.DEFAULT_LOCALE_LOOKUP;failure->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.BASELINE_LOOKUP | stop | Run local resolve_active_knowledge_locales through completed owner-task export evidence; retain exact locale identifiers for required localization. |
| CONTENT_TYPES_REDWOOD.DEFAULT_LOCALE_LOOKUP | step | 7 | evaluate_result | found->CONTENT_TYPES_REDWOOD.DEPENDENCIES;failure->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.LOCALES_LOOKUP | stop | Run local resolve_default_knowledge_locale for the source-defined localized-row ordering; keep every locale row and value unchanged except approved edits. |
| CONTENT_TYPES_REDWOOD.VISIBILITY_LOOKUP | step | 10 | reference_lookup | found->CONTENT_TYPES_REDWOOD.DEFAULTS;not_found->CONTENT_TYPES_REDWOOD.BLOCKED;failure->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.VISIBILITY_REQUIRED | stop | Run resolve_department_user_groups only for requested restricted visibility; use the caller-supplied department stripe code, finish paging and resolve each selected group exactly once. |
