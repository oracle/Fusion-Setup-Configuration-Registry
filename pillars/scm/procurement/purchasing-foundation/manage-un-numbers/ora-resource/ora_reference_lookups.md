# UN Number Hazard Class Resolution

Fusion is the authority for Hazard Class identity. Submitted names are exact
selection criteria, not evidence of existence. The user-approved lookup plan
replaces unchecked HazardClassId pass-through for create/update. UNNumberId
and deletion retain their existing contracts.

Source: [Oracle 26D Get all hazard classes](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasinghazardclasses-get.html).
No tenant URL, real response, credential, or customer identifier is retained here.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_hazard_class | Create/update with HazardClass or non-null HazardClassId; also verify captured non-null ID during Data Loader task validation | Validated exact HazardClass and/or validated integer/string HazardClassId; selected environment; preparation phase or captured-record validation phase | GET /fscmRestApi/resources/11.13.18.05/purchasingHazardClasses through the shared core REST client; q, fields, onlyData, limit and offset as specified below | HazardClassId,HazardClass,HazardClassCode,InactiveDate plus items,count,hasMore,limit,offset | Complete pagination; compare exact case-sensitive name with no trimming and numeric ID equivalence when supplied; require exactly one distinct matching ID and agreement of all supplied identifiers | Verified ID, matched name/code/inactive date and scoped lookup evidence; only during preparation fill an omitted HazardClassId and separate HazardClass context from loader business data | Zero exact matches or supplied-key disagreement: blocked; multiple exact IDs: ambiguous and blocked; incomplete/auth/transport/malformed response: failed, never treated as no match |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Before first read | Require selected target environment, authenticated core client, read privilege and exact task scope. Use core/fusion-api/rest-api-client/scripts/fusion_rest_client.py with GET. No write or alternate client is authorized. Use the selected environment; do not hardcode an origin from examples. |
| No association or delete | Return not_applicable without authentication or a GET for a valid delete row, omitted name and ID, or null ID with no name. Delete inputs with association fields already fail input validation. |
| Query selection | When a non-null ID is supplied, query q=HazardClassId=<validated decimal integer>. Otherwise query q=HazardClass='<exact name>'. With both keys, query by ID and check the returned name exactly. For a string ID, use a separate lossless base-10 integer for comparison/query; retain the original supplied value for handoff. |
| Literal and URL handling | Escape an apostrophe inside a name as two apostrophes in the quoted query literal. Pass the full q value as one --query argument in a structured argument list, never interpolate into a shell command. Let the shared client URL-encode parameters once; preserve ampersands, percent signs, plus signs, Unicode, and whitespace. |
| Query parameters | Use fields=HazardClassId,HazardClass,HazardClassCode,InactiveDate, onlyData=true, limit=100, offset=0 initially. Keep the same filter and fields on all pages. Do not filter on InactiveDate. |
| Response and pages | Require a JSON object with items array, boolean hasMore, integer count/limit/offset, count equal to the item count, positive limit, and the requested offset. Advance offset by the returned limit until hasMore=false. Empty pages with hasMore=true, non-advancing/repeated pages or duplicate numerically equivalent IDs (including integer/string or leading-zero variants), missing envelope fields, and failed pages block as incomplete evidence. Never accept the first match before pagination completes. |
| Traversal bound | Read at most 100 pages for one resolver invocation, including preparation or captured-record verification. Apply the shared core client's bounded request timeout and authentication recovery to each GET; do not add task-level retries or reset the page budget after recovery. A valid page 100 with hasMore=false completes the traversal. If page 100 still has hasMore=true, stop without requesting page 101, return failed with incomplete evidence, and block resolution and enrichment even when an exact match was observed earlier. Never infer absence or uniqueness from partial results. |
| Returned records | Require each item to contain non-null HazardClassId as either a JSON integer (excluding booleans) with absolute value below 10^18 or an ASCII decimal string matching [0-9]{1,18}; also require string HazardClass and HazardClassCode, and null or valid YYYY-MM-DD InactiveDate. Reject floats, exponent notation, signs or whitespace in strings, non-ASCII digits, empty strings, arrays, objects, and out-of-precision values before comparison. Reject malformed evidence. Compare strings exactly; exclude nonmatching results even if the server uses broader collation. |
| Lossless ID comparison | After validating both supplied and returned ID shapes, use arbitrary-precision base-10 integers for ID agreement, distinctness, duplicate detection and query literals; never use floating-point conversion. Keep original representations separately. |
| Exact outcome | Require one distinct exact match across all pages. If ID and name were supplied, both must agree with that record. No match or multiple matches blocks; never choose the first or create a missing class. |
| Inactive record | A unique exact match is resolved even if InactiveDate is in the past. Keep the value as evidence and leave eligibility to Data Loader/Fusion. |
| Preparation phase | Preserve the original input; create a separate loader-ready record. If ID was omitted, fill it with the authoritative returned ID, preserving its validated value/type. Preserve a supplied verified ID's original value/type even when the response uses a different representation. Keep HazardClass as lookup context/evidence, not a writable UN Number field. Do not overwrite explicit null. |
| Captured-record phase | Verify the captured non-null HazardClassId using a fresh read for this validation. Never alter captured records through ruleResults or changes. If correction/enrichment is needed, block, cancel the pending validation cycle, prepare corrected input, and validate the new artifact. |
| Evidence boundary | Keep phase, environment binding, row association, supplied selectors and resolved identity in the current preparation/artifact context as needed. Durable repository guidance and diagnostics must not retain customer payloads, IDs, opaque links, tokens, or credentials. No cross-environment or cross-artifact lookup cache. |
| Failure | Distinguish no match, ambiguity, key disagreement, authentication, transport and malformed/incomplete evidence. Use core-client auth recovery only; never turn read failure into absence or fall back to a write. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| UN.RESOLVE_HAZARD_CLASS | decision | 15 | reference_lookup | resolved->UN.PRESERVE_VALUES;not_applicable->UN.PRESERVE_VALUES;blocked->UN.HANDLE_ISSUES;ambiguous->UN.HANDLE_ISSUES;failed->UN.HANDLE_ISSUES | UN.VALIDATE_INPUT | stop | Use resolve_hazard_class for applicable create/update associations; otherwise return not_applicable without a read; never mutate captured records |
