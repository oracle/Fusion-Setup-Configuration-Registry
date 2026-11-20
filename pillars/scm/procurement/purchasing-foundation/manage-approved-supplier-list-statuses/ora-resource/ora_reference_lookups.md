# ASL Status Explicit Fetch Lookup

This resource implements only the read_fetch branch selected by Operation
Routing in [input validation](ora_input_validation.md#operation-routing).
It is never an import prerequisite, identity resolver, create/update/delete
validation step, or fallback. On data_load, return not_applicable for this
resource without authentication, token refresh or GET. No write is authorized.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| fetch_asl_statuses | Explicit get/list/fetch/search request selected read_fetch and fetch criteria passed | Validated fetch_criteria and unambiguous selected Fusion environment | GET /fscmRestApi/resources/11.13.18.05/purchasingApprovedSupplierListStatuses through core.fusion-api.rest-api-client | StatusId,Status,StatusDescription,AslDefaultFlag,AllowPurchasingApprovalFlag,AllowSourcingFlag,InactiveDate and collection paging envelope | Apply Local Matching only after complete bounded traversal; retain exact matching and lossless numeric identity rules | fetch_result items, applied criteria, observed match count, completeness, pages read and diagnostics; never populate import records or operation controls | For complete exact-name reads, zero matches is not_found, one found, multiple ambiguous. Completed text/list reads return complete even with zero matches. Incomplete or failed reads never establish absence or uniqueness. |

## Local Matching

Supply fetch_criteria separately from business records. Apply matching locally;
user text never enters shell commands, endpoints, q, finder, or other REST
expressions. Include active and inactive records unless explicitly filtered.

| Criterion | Local matching |
|---|---|
| exact_name with nonblank name | Exact Status equality, including case and whitespace. After a complete read: zero = not_found, one = found, multiple = ambiguous; never substitute a similar name. |
| text with nonblank terms | OR literal Unicode-casefold substrings across Status and StatusDescription. Quotes, percent, underscore, and punctuation are literal. “Related to approvals” uses disclosed terms approval and approve, without an implicit flag filter. Otherwise use the user's literal terms; clarify ambiguous expansion. |
| list | All records satisfying explicit filters; no text terms required. |
| StatusId / Status filters | Exact numeric ID / exact case-sensitive Status equality; no text trimming. |
| StatusDescription filter | Nonblank case-insensitive literal substring. |
| Flag filters | AslDefaultFlag: boolean equality. AllowPurchasingApprovalFlag and AllowSourcingFlag: boolean or explicit null equality. False and null remain distinct. |
| InactiveDate filter | eq, lt, lte, gt, gte with valid YYYY-MM-DD dates, or is_null / is_not_null; ordered comparisons exclude null. |
| Combined criteria | AND each validated filter with the selected mode. Input rejection belongs to Fetch Criteria Validation. |

Fetch IDs and ID filters reuse the integer/decimal-text signed-int64 contract in
[Field Validation](ora_input_validation.md#field-validation).
Derive a lossless integer comparison key without floating point for filtering,
ordering, and duplicate detection: 3, "3", and "003" are one identity; "2" sorts
before "10". Preserve the original ID value and JSON type in returned items.
This shared ID constraint does not apply import-required-field rules to responses.

## Request and Pagination

Use the shared REST client's configured environment, authentication, timeouts
and bounded retry. Resolve an ambiguous environment before reading. GET only,
without a body or Data Loader submission. Do not add task-level retries.

Oracle's [26D collection GET](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingapprovedsupplierliststatuses-get.html)
provides the collection/paging contract; local matching and the 100-page bound
are FSCR policies. The latest Procurement landing release was verified as 26D
on 2026-10-28. From the repository root:

```bash
python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
  /fscmRestApi/resources/11.13.18.05/purchasingApprovedSupplierListStatuses \
  --method GET \
  --query onlyData=true \
  --query fields=StatusId,Status,StatusDescription,AslDefaultFlag,AllowPurchasingApprovalFlag,AllowSourcingFlag,InactiveDate \
  --query orderBy=StatusId:asc \
  --query limit=500 \
  --query offset=0 \
  --header REST-Framework-Version=9
```

1. Require an object with items array, boolean hasMore, integer count equal to
   len(items), positive integer limit, and nonnegative integer offset equal to
   the request; count <= limit. Booleans are not paging integers. Each item must
   contain the seven fields: valid ID as above, string Status/StatusDescription,
   boolean AslDefaultFlag, boolean-or-null permission flags, valid YYYY-MM-DD or
   null InactiveDate. Ignore extra response metadata for display only.
2. Require strictly increasing numeric IDs within/across pages; repeated IDs
   (including different representations), repeated pages, or lack of progress
   stop the read. Report that records may have changed; do not deduplicate or
   claim snapshot consistency.
3. While hasMore=true, require count > 0 and advance to returned offset + returned
   limit, including when the server caps 500. Keep method/fields/order/endpoint
   fixed. Continue after finding a match. Complete only at hasMore=false (an empty
   terminal page is valid), never from totalResults. Stop at 100 pages; if hasMore
   is still true, results are incomplete. Do not add task-level retries.

Malformed or unfinished traversal and HTTP/auth/access/transport failures stop
this lookup; use [Fetch Results and Failures](ora_error_handling.md#fetch-results-and-failures)
for result status and diagnostics. Return outcome complete, incomplete or failed
to ASL.RETURN_FETCH_RESULT. Do not start Data Loader or an import graph branch.

Examples: get status "Manager Approval Required" (exact_name); get statuses
related to approvals (text: approval, approve); get statuses allowing purchasing
approval (list, AllowPurchasingApprovalFlag=true); get ID 4 (list, StatusId=4);
get defaults without an inactive date (list, AslDefaultFlag=true AND InactiveDate
is_null).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASL.FETCH_STATUSES | decision | 15 | reference_lookup | complete->ASL.RETURN_FETCH_RESULT;incomplete->ASL.RETURN_FETCH_RESULT;failed->ASL.RETURN_FETCH_RESULT | ASL.VALIDATE_FETCH_CRITERIA | stop | Only explicit read_fetch after valid criteria; execute fetch_asl_statuses under Request and Pagination and Local Matching; never execute for create/update/delete or import validation |
