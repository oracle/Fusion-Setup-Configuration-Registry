# Reference Lookups

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_workday_pattern_by_name | PatternName is supplied for a schedule workday pattern | PatternName | GET /fscmRestApi/resources/11.13.18.05/workdayPatterns; q=Name='<PatternName>'; fields=PatternId,Name; onlyData=true; limit=100; offset=0 | items[].PatternId, items[].Name, hasMore, offset, limit | Across all result pages, require exactly one item whose Name equals the supplied PatternName exactly; no fuzzy or case-insensitive fallback | PatternId: matched items[].PatternId, kept internal; PatternName: matched items[].Name | Zero exact matches: unresolved; multiple exact matches: ambiguous. Stop before preview, retain the name-based lookup failure, and request a corrected pattern name; do not ask for an ID |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A workday pattern name is supplied | Map the supplied PatternName to the collection's Name attribute in the documented resolver; require a nonblank returned PatternId before reporting resolved. PatternName is the schedule association field, not a queryable attribute of workdayPatterns. |
| The active workflow reaches this read-only lookup | Use core/fusion-api/rest-api-client/scripts/fusion_rest_client.py with the relative collection path and repeated --query key=value options as defined in core/fusion-api/rest-api-client/references/fusion-rest-api.md. Use its configured restBaseUrl and standard Fusion OAuth handling; do not hardcode a host or introduce another client. |
| Building the name filter | Treat PatternName as one quoted Fusion q string literal, escaping embedded quotes according to Fusion query syntax before passing q as a query value. Let the central client URL-encode query parameters; never interpolate the name into a shell command or concatenate raw input into a URL. If safe literal construction is unavailable, return failed and stop. |
| A response has hasMore=true | Retrieve the next page with offset set to the returned offset plus limit, preserving the filter and fields. Do not report resolved until all pages have been checked; a page failure, missing paging metadata, or nonadvancing offset returns failed and stops preview. |
| The resolver returns no match or many matches | Stop before preview and request a corrected or more specific pattern name. |
| The documented resolver request fails or its response is malformed | Return failed through the existing issue handler. Preserve the central client's bounded authentication recovery and stop before any further retry or endpoint substitution; do not request an ID or guess another REST path. |

## Documentation Source

[Oracle Fusion Cloud SCM REST API 26C: Get all patterns](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-workdaypatterns-get.html), checked 2026-10-15, documents the collection path, queryable Name, returned PatternId and Name, and paging parameters. The exact-match, internal-ID, and stop-before-preview policies preserve this task's existing contract.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FAC_SCH.RESOLVE_WORKDAY_PATTERN | decision | 2 | reference_lookup | resolved->FAC_SCH.ENFORCE_NAME_INPUT;unresolved->FAC_SCH.HANDLE_ISSUE;ambiguous->FAC_SCH.HANDLE_ISSUE;failed->FAC_SCH.HANDLE_ISSUE | FAC_SCH.VALIDATE_INPUT | stop | Create schedule with a workday pattern |
