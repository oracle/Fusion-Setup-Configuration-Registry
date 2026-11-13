# Data Capture Rules Read Lookups

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| list_data_capture_rules | The normalized operation is LIST. | Target environment and optional documented bounded query parameters: $limit, $offset, $includeTotalItems, raw $filter, $sortBy, $fields, and $effectiveDate. Equality filters use ((field = 'value')); do not use eq or pre-encoded text. | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules | items, hasMore, totalItems when requested, and the selected Data Capture Rule fields | Return the service collection after applying every approved query parameter exactly. For one active rule use raw $filter=((statusCode = 'ACTIVE')) and $limit=1. | data_capture_rule_list, has_more, total_items when present, and effective_read_access_result | An empty items array is a successful empty result; preserve every returned item up to the requested bound. |
| get_data_capture_rule_by_id | The normalized operation is GET and data_capture_rule_id is exact. | Target environment, data_capture_rule_id, and optional documented $fields and $effectiveDate | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules/{dataCaptureRules_id} | Full or field-selected Data Capture Rule representation returned by the endpoint | Match the exact path ID; do not resolve by display name. | data_capture_rule_detail and effective_read_access_result | Treat HTTP 404 as not found; never substitute another ID or a name match. |
| query_data_capture_rules | The normalized operation is QUERY and the validated advanced-query body is bounded. | Target environment; one top-level JSON object; optional fields, accessors, subTypes, and parameters; required bounded collection object containing filter and limit plus optional offset, includeTotalItems, sortBy, and documented privilege; optional $effectiveDate outside the body. Equality filters use ((field = 'value')). | POST /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules/$query | items, hasMore, totalItems when requested, and only the selected Data Capture Rule and accessor fields | Apply every validated filter and bound exactly. For one active rule, collection is {filter: ((statusCode = 'ACTIVE')), limit: 1}. Do not add query, payload, or data wrappers; use sortBy only when explicitly requested, otherwise preserve service order. | data_capture_rule_list, has_more, total_items when present, and effective_read_access_result | An empty items array is a successful empty result; never broaden a filter, change a requested value, omit a condition, invent a sort criterion, or retry an invalid body. |

## Validated BOSS Filter and QUERY Shape

Use raw BOSS equality expressions with double parentheses, `=`, and
single-quoted string literals:

```text
((statusCode = 'ACTIVE'))
```

For one active Data Capture Rule, the validated semantic-read `$query` body is:

```json
{
  "fields": ["id", "name", "statusCode"],
  "collection": {
    "filter": "((statusCode = 'ACTIVE'))",
    "limit": 1
  }
}
```

Do not use OData `eq`, double-quoted string literals, pre-encoded filter text,
or a `query`, `payload`, or `data` wrapper. The shared client performs JSON and
URL encoding.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| LIST succeeds with records | Return the bounded items collection, hasMore, and totalItems when requested; record effective read success. |
| LIST succeeds with no records | Return an empty list and hasMore false; record effective read success. |
| GET succeeds | Return the record and record effective read success for the exact ID. |
| GET returns 404 | Return not found without inferring authorization failure or another record identity. |
| QUERY succeeds with records | Return items up to collection.limit, hasMore, totalItems when requested, every applied filter, and the applied sort or service-order disclosure. |
| QUERY succeeds with no records | Return an empty list and record effective read success without weakening the filter. |
| A natural-language read request contains supported predicates, projections, child accessors, bounds, pagination, a total-count request, ordering, or an effective date | Translate every explicit constraint into the corresponding documented LIST parameter, GET parameter, QUERY body field, or $effectiveDate parameter; derive intent from the complete request rather than matching a canned phrase. |
| A request asks for one ACTIVE Data Capture Rule | Use QUERY with fields limited to the requested projection and collection {filter: ((statusCode = 'ACTIVE')), limit: 1}; preserve service order unless the user explicitly requests a supported sort. |
| A QUERY contains multiple predicates | Preserve every supported predicate in collection.filter; do not drop, broaden, or weaken a condition. |
| A QUERY asks for the first or top N records without an order | Set collection.limit to the bounded positive N, preserve service order, and disclose that no explicit sort was applied. |
| A QUERY requests ordering | Set collection.sortBy only when the sortable field and direction are explicit or unambiguous; otherwise stop and request one short clarification. |
| A request includes an unsupported or ambiguous field, accessor, subtype, operator, predicate, or ordering choice | Stop before the API call and identify the unsupported part or required clarification; do not silently approximate the request. |
| A LIST or QUERY filter uses eq, double-quoted string literals, pre-encoded text, or lacks the required BOSS parentheses | Reject it during input validation and rebuild the normalized read request once before any API call; do not send the malformed expression. |
| BOSS LIST or GET returns 403 after its one cache-managed refresh, or QUERY returns 403 without an automatic refresh or retry | Return an authorization or privilege failure; do not infer the missing role or permission group. |
| A mutation operation is requested | Return unsupported and do not invoke a BOSS endpoint; the exact POST dataCaptureRules/$query operation is a semantic read, not a mutation. |
| A response contains more rows than the approved bound | Return only the approved bound and disclose whether more records are available. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DCR.LIST | step | 4 | reference_lookup | success->DCR.LIST_DONE;empty->DCR.LIST_DONE;unauthorized->DCR.ERROR;failed->DCR.ERROR | DCR.SELECT_READ | stop | The selected read operation is LIST. |
| DCR.GET | step | 5 | reference_lookup | found->DCR.GET_DONE;not_found->DCR.NOT_FOUND;unauthorized->DCR.ERROR;failed->DCR.ERROR | DCR.SELECT_READ | stop | The selected read operation is GET. |
| DCR.QUERY | step | 6 | reference_lookup | success->DCR.QUERY_DONE;empty->DCR.QUERY_DONE;unauthorized->DCR.ERROR;failed->DCR.ERROR | DCR.SELECT_READ | stop | The selected read operation is QUERY. |
