# ASL Status Input Validation

The approved developer requirements (2026-10-20) select submitted business records
and explicit operation context as local authority. Evaluate every row independently
and collect all issues. The existing import sections below apply only to the
data_load branch: no REST action, authentication, record lookup, or server-state
check is permitted there. Fetch criteria are validated separately on read_fetch;
only its subsequent lookup node may perform the declared read-only GET.

Oracle sources: [26D create](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingapprovedsupplierliststatuses-post.html),
[26D update](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingapprovedsupplierliststatuses-statusid-patch.html),
and [26D table](https://docs.oracle.com/en/cloud/saas/procurement/26d/oedmp/poaslstatuses-23902.html).
The approved plan supplies the intent matrix, exact-name allowlist, blank rejection,
and create/ID conflict policy. REST fields remain canonical; Description is not an alias.

## Operation Routing

Classify the explicitly selected user/task request before evaluating data.
Create, update, delete and standalone import validation select data_load,
including requests with no create/update intent yet. Only an explicit
get/list/fetch/search request selects read_fetch. Names, IDs, missing identity,
fetch_criteria presence, or a failed import rule never trigger fetching.
Clarify an ambiguous route before any GET. Keep separately requested reads and
mutations as separate scoped operations; a read never authorizes a mutation.

On data_load, follow only the existing import branch. In the core Task Hook
result list, include ora_reference_lookups.md as not_applicable with empty issues
and changes; do not execute its node. For resources shared by both branches,
evaluate only reached nodes and branch-scoped sections. On read_fetch, skip
import requiredness, normalization, defaulting, design and handoff rules.

## Fetch Criteria Validation

Apply only after read_fetch is explicitly selected. Supply fetch_criteria
separately from business records; do not apply import Required Groups or request
intent rules to these criteria or to fetched responses. These checks are local
and happen before authentication or a GET. Matching behavior belongs to
[the lookup resource](ora_reference_lookups.md#local-matching).

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Fetch mode | Accept exact_name with a nonblank name, text with nonblank literal terms, or list without a name/terms requirement. Reject unknown modes, empty required terms and incompatible mode arguments. | Explicit fetching | |
| Filter attributes and operators | Accept only StatusId, Status, StatusDescription, AslDefaultFlag, AllowPurchasingApprovalFlag, AllowSourcingFlag and InactiveDate. ID/name/flags accept eq; description accepts contains; date accepts eq, lt, lte, gt, gte, is_null and is_not_null. Reject unknown attributes or unsupported operators before GET. | Explicit fetching with filters | |
| ID filter value | Reuse the StatusId contract in Field Validation by reference, including lossless integer comparison; do not duplicate or relax it. | StatusId filter | |
| Name and description criteria | Require string values; exact_name name, text terms and description contains values must be nonblank. Preserve supplied text literally. Status eq is exact string equality without trimming. | Applicable criteria or filters | |
| Flag filter value | AslDefaultFlag requires a native boolean. AllowPurchasingApprovalFlag and AllowSourcingFlag accept native boolean or explicit null. Do not use import boolean-text normalization. | Flag filters | |
| Date filter value | Ordered/equality operators require valid Gregorian YYYY-MM-DD text. is_null/is_not_null have no date operand. Reject invalid dates or incompatible operands. | InactiveDate filter | |

Invalid criteria lead to ASL.RETURN_FETCH_INPUT_ISSUES with failed/complete=false
and no GET. Valid criteria alone authorize no write; continue only to the
explicitly selected read-only lookup.

## Local Validation Adapter

Start at ASL.NORMALIZE_INPUT with `../scripts/normalize_booleans.py`.
[Defaulting](ora_defaulting_rules.md#permitted-boolean-normalization) owns the
permitted preparation transformations. Use `normalize_record` for preparation
and `verify_captured_record` for a frozen capture's separate validation view.
Carry all helper issues into ASL.VALIDATE_INPUT and collect remaining row issues;
helper success never skips the contracts below. Encoding diagnostics follow
[handoff gates](ora_error_handling.md#representation-and-handoff-gates), even
when the business value is nullable. No adapter performs REST or a live lookup.

## Delete Validation

Delete requires explicit user intent, user-supplied StatusId for every row, and
exact RestAction=DELETE as separate loader control metadata. Captured controls
must already be canonical: blank, missing, differently cased, or conflicting
controls fail. Delete sources accept only delete rows. Any additional business
field fails, even when blank or null. An ID alone never selects delete; names,
markers, or fetched IDs do not satisfy the user-supplied-ID requirement.

Evaluate `validate_delete_records(records, rest_actions, intent='delete')` with
business records and controls separately. Caller context retains user-request
provenance; controls inside a business record are unknown attributes. The helper
checks delete inputs, not final artifact integrity, full task validation, or
execution. Ordinary ID-only rows without explicit delete intent retain update
behavior. Preparation is owned by
[defaulting](ora_defaulting_rules.md#delete-source-preparation); final directive
and control agreement is checked by the
[prepared artifact gate](ora_error_handling.md#prepared-artifact-gate).

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Delete identifier | StatusId only | MISSING when absent; FAILED when invalid | Ask for the user-supplied ID; no name lookup | Explicit delete with exact RestAction=DELETE | |
| Create fields | Both Status and StatusDescription | MISSING for each absent field | Supply both nonblank strings | Explicit create, with StatusId absent | |
| Undetermined fields | Both Status and StatusDescription | MISSING for each absent field | Supply both nonblank strings | Intent absent or undetermined and StatusId absent | |
| Update by identity | StatusId; Status and StatusDescription may be omitted | Invalid supplied identity is FAILED; do not fall back to name matching | Supply a valid integer or decimal-text identity or correct the request | StatusId present and intent is absent, undetermined, or update | |
| Update by name | Status; StatusDescription is optional | MISSING when Status absent | Supply existing Status; use StatusId when renaming | Explicit update and StatusId absent | |

## Record and Captured Source Validation

For Data Loader validation, "captured records" means a read-only evaluation view
of the exact prepared ZIP after core mapping and conversion. Read its DAT members
losslessly, honoring escaping and record directives, and separate business fields
from RestAction/control metadata. Do not substitute mutable original CSV/XLSX
sources or a pillar replacement serializer. If decoding is unsupported, follow the
[artifact decoding blocker](ora_error_handling.md#prepared-artifact-gate).
For standalone preparation, use caller-supplied lossless records with explicit
source-format and operation context.

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Business record shape | Require an object with exact string attribute names | Every row | |
| Exact business attribute allowlist | Accept only StatusId, Status, StatusDescription, AslDefaultFlag, AllowPurchasingApprovalFlag, AllowSourcingFlag, InactiveDate. Reject every unknown attribute including Description, status, links, and response audit fields, even if all required fields are present. Never alias, rename, or silently drop attributes. Delete rows instead accept only StatusId and reject all other business fields even blank/null. | Every row | |
| Captured representation | An absent column means not supplied; a blank cell is an empty string. Supplied non-null flags in a frozen capture must be canonical lowercase true/false text or native booleans; validate their typed view separately. | Captured prepared artifact headers and rows | |

## Request Context Validation

Validate caller instructions separately from business attributes. These checks
use only submitted records and scoped request context.

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Operation context | Accept absent, undetermined, create, update, or explicit delete in separate caller context. Unsupported intent is UNSUPPORTED; contradictory instructions fail. Delete intent/control requirements are defined in Delete Validation. Declared loader controls are separate from business data. | Every row | |
| Rename identity | Explicit rename intent requires StatusId; a name-only update supplies the existing Status | Rename intent in caller context | |
| Contradictory date instructions | A supplied nonempty date and a removal instruction for the same record conflict | Date value and scoped caller instructions both supplied | |
| Conflicting create identity | Reject explicit create with any supplied StatusId; report FAILED and require correction | Explicit create and StatusId attribute present, including null | |
| Empty-date operation context | An empty InactiveDate requires known create/update intent; unresolved intent requires clarification. Absence of StatusId does not establish create. A valid supplied StatusId supports update validation under Required Groups. | Empty InactiveDate supplied | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| StatusId | Accept an integer (not boolean) or ASCII decimal text matching -?[0-9]+ within signed int64 bounds (-9223372036854775808 through 9223372036854775807). Reject fractions, null, blanks, whitespace, plus signs, exponent notation and out-of-range values. Compare losslessly without floating point. | Only when supplied | |
| Status | Require a nonblank string of at most 25 characters when supplied; reject null, empty, and whitespace-only strings. | When supplied, or required by Required Groups | |
| StatusDescription | Require a nonblank string of at most 240 characters when supplied; reject null, empty, and whitespace-only strings. | When supplied, or required by Required Groups | |
| AslDefaultFlag | Require boolean true or false after declared normalization; reject null, unrecognized strings, and numeric substitutes | Only when supplied | |
| AllowPurchasingApprovalFlag | Accept boolean true, boolean false, or explicit null after declared normalization; reject unrecognized strings and numbers | Only when supplied | |
| AllowSourcingFlag | Accept boolean true, boolean false, or explicit null after declared normalization; reject unrecognized strings and numbers | Only when supplied | |
| InactiveDate | Accept explicit null, a valid Gregorian YYYY-MM-DD string, or an empty string subject to Request Context Validation. Reject whitespace, timestamps, impossible dates, and non-string values. Past dates are allowed. | Only when supplied | |

Preserve field values according to [defaulting](ora_defaulting_rules.md#source-preparation-and-preservation).
Business nullability above is independent of whether a loader source can encode
null. See [representation and handoff gates](ora_error_handling.md#representation-and-handoff-gates)
for file-preparation blockers and [design rules](ora_design_enforcement.md#design-rules)
for clearing authorization. These references do not resolve values or call REST.

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| All record, captured-source, request-context, field, and required-group checks pass | FIELD_VALID; no existence, uniqueness, or server-acceptance assertion | Apply preservation rules, then design checks | |
| Any row has issues | Return all row/field issues; valid rows remain identifiable | Block the batch from approval until corrected and revalidated | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASL.CLASSIFY_OPERATION | decision | 1 | evaluate_result | data_load->ASL.NORMALIZE_INPUT;read_fetch->ASL.VALIDATE_FETCH_CRITERIA;unsupported->ASL.HANDLE_ISSUES | none | stop | Classify the explicit request under Operation Routing; import/create/update/delete never select fetching implicitly |
| ASL.VALIDATE_FETCH_CRITERIA | decision | 2 | validate_input | valid->ASL.FETCH_STATUSES;invalid->ASL.RETURN_FETCH_INPUT_ISSUES;unsupported->ASL.RETURN_FETCH_INPUT_ISSUES | ASL.CLASSIFY_OPERATION | stop | Explicit read_fetch only; evaluate Fetch Criteria Validation locally before authentication or GET and do not apply import-required fields |
| ASL.NORMALIZE_INPUT | step | 5 | validate_input | normalized->ASL.VALIDATE_INPUT | ASL.CLASSIFY_OPERATION | stop | Check IDs/null encoding and normalize declared boolean text in a separate validation copy, retain raw records and changes, carry issues into full validation; use captured verification for frozen loader input and the ID-only delete helper for explicitly selected delete rows |
| ASL.VALIDATE_INPUT | decision | 10 | validate_input | valid->ASL.PRESERVE_VALUES;missing->ASL.HANDLE_ISSUES;invalid->ASL.HANDLE_ISSUES;unsupported->ASL.HANDLE_ISSUES | ASL.NORMALIZE_INPUT | stop | Evaluate every submitted row against Required Groups, Record and Captured Source Validation, Request Context Validation, and Field Validation using only local input and separate intent/source-format context |
