# Sales Motions Read Lookups

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| list_sales_motions | The normalized operation is LIST. | Target environment and optional documented bounded query parameters such as $limit and $offset | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions | items, hasMore, and the Sales Motion fields returned by the endpoint | Return the service collection in response order after applying only the approved query parameters. | sales_motion_list and has_more | An empty items array is a successful empty result; preserve every returned item up to the requested bound. |
| get_sales_motion_by_id | The normalized operation is GET and sales_motion_id is exact. | Target environment and sales_motion_id | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions/{salesMotions_id} | Full Sales Motion representation returned by the endpoint | Match the exact path ID; do not resolve by display name. | sales_motion_detail | Treat HTTP 404 as not found; never substitute another ID or a name match. |
| query_sales_motions | The normalized operation is QUERY and the validated advanced-query body is bounded. | Target environment; fields; optional nested accessors; collection.filter, collection.limit, collection.offset, collection.includeTotalItems, collection.sortBy, and documented collection.privilege; optional parameters and $effectiveDate | POST /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions/$query | items, hasMore, totalItems when requested, and only the selected Sales Motion and accessor fields | Apply the validated filter and bound exactly; use sortBy only when the user supplies a sort criterion, otherwise preserve service order. | sales_motion_list, has_more, total_items when present, and effective_read_access_result | An empty items array is a successful empty result; never broaden the filter, change the requested status, or invent a sort criterion. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| LIST succeeds with records | Return the bounded items collection and hasMore value when present; record effective read success. |
| LIST succeeds with no records | Return an empty list and hasMore false; record effective read success. |
| GET succeeds | Return the record and record effective read success for the exact ID. |
| GET returns 404 | Return not found without inferring authorization failure or another record identity. |
| QUERY succeeds with records | Return items up to collection.limit, hasMore, totalItems when requested, the applied filter, and the applied sort or service-order disclosure. |
| QUERY succeeds with no records | Return an empty list and record effective read success without weakening the filter. |
| A natural-language QUERY contains supported predicates, projections, child accessors, bounds, pagination, a total-count request, ordering, or an effective date | Translate every explicit constraint into the corresponding documented query-body field or $effectiveDate parameter; derive intent from the complete request rather than matching a canned phrase. |
| A QUERY contains multiple predicates | Preserve every supported predicate in collection.filter; do not drop, broaden, or weaken a condition. |
| A QUERY asks for the first or top N records without an order | Set collection.limit to the bounded positive N, preserve service order, and disclose that no explicit sort was applied. |
| A QUERY requests ordering | Set collection.sortBy only when the sortable field and direction are explicit or unambiguous; otherwise stop and request one short clarification. |
| A QUERY includes an unsupported or ambiguous field, accessor, operator, predicate, or ordering choice | Stop before the API call and identify the unsupported part or required clarification; do not silently approximate the request. |
| BOSS LIST or GET returns 403 after its one cache-managed refresh, or QUERY returns 403 without an automatic refresh or retry | Return an authorization or privilege failure; do not infer the missing role or permission group. |
| A mutation operation is requested | Return unsupported and do not invoke a BOSS endpoint; the exact POST salesMotions/$query operation is a semantic read, not a mutation. |
| A response contains more rows than the approved bound | Return only the approved bound and disclose whether more records are available. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SM.LIST | step | 4 | reference_lookup | success->SM.LIST_DONE;empty->SM.LIST_DONE;unauthorized->SM.ERROR;failed->SM.ERROR | SM.SELECT_READ | stop | The selected read operation is LIST. |
| SM.GET | step | 5 | reference_lookup | found->SM.GET_DONE;not_found->SM.NOT_FOUND;unauthorized->SM.ERROR;failed->SM.ERROR | SM.SELECT_READ | stop | The selected read operation is GET. |
| SM.QUERY | step | 6 | reference_lookup | success->SM.QUERY_DONE;empty->SM.QUERY_DONE;unauthorized->SM.ERROR;failed->SM.ERROR | SM.SELECT_READ | stop | The selected read operation is QUERY. |
