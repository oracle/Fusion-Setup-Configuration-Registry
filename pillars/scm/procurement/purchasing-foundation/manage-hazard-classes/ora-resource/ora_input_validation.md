# Hazard Class Input Validation

The approved operation-neutral authoring plan selects submitted business fields
as the local authority for these checks. Field types, nullability, and sizes
retain the existing Oracle [26D create contract](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasinghazardclasses-post.html)
and [26D update contract](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasinghazardclasses-hazardclassid-patch.html)
baseline. Requiring name and code on every row, blank rejection, and the field
allowlist are FSCR policies. Check each row independently and retain all issues.

User-confirmed API evidence (2026-10-16): POST succeeds both when InactiveDate
is omitted and when it is explicit JSON null. A missing field or an empty
CSV/XLSX date cell means not provided; omit that field rather than sending an
empty string. Explicit null remains null. Whitespace-only text is supplied
invalid input, not an empty cell.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Required business fields | Both HazardClass and HazardClassCode | MISSING if either is absent; FAILED if either is null, blank, or invalid | Supply both nonblank strings within their field limits | Every row, regardless of eventual loader operation | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| HazardClass | Require a string, maximum 40 characters, containing at least one non-whitespace character; reject null. Detect blanks without trimming or changing the value. | Every row; required | |
| HazardClassCode | Require a string, maximum 30 characters, containing at least one non-whitespace character; reject null. Preserve case, leading zeros, surrounding whitespace, and Unicode. Pass it as supplied business data without assigning lookup-key or code-change semantics. | Every row; required | |
| Description | Accept null or a string of at most 240 characters, including an empty string. | Only when supplied | |
| InactiveDate | Optional. Accept omission or an empty CSV/XLSX cell as not provided and omit InactiveDate from that record. Preserve explicit null. Otherwise require a valid Gregorian calendar date written YYYY-MM-DD; reject timestamps, malformed dates, impossible dates, and non-string non-null values. Do not impose a future-only rule. | Only when a nonempty value or explicit null is supplied | |
| HazardClassId | Optional. Preserve any supplied value exactly, including null, without type, range, format, or existence validation and without normalization. Defer ID acceptance and identity handling to Data Loader; local readiness makes no claim that the ID is valid. | When supplied; omission is allowed and no ID is generated | |
| Supported business fields | Accept HazardClass, HazardClassCode, Description, InactiveDate, HazardClassId. Reject unknown business fields and response metadata such as links, CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, and @context; never silently drop them. Operation, environment, and loader control fields are separate workflow context, not business fields. | Every row | |
| Operation context | No create/update input is required and neither changes these rules. Data Loader owns operation selection; the pillar does not assign RestAction or infer an operation from IDs or codes. This preparation graph does not authorize deletion or other mutations. | Every row | |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Row passes field checks | FIELD_VALID; no record-existence or server-acceptance claim | Continue through preservation and design checks to the local Data Loader handoff; no lookup is pending | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| HAZ.VALIDATE_INPUT | decision | 10 | validate_input | valid->HAZ.PRESERVE_VALUES;missing->HAZ.HANDLE_ISSUES;invalid->HAZ.HANDLE_ISSUES;unsupported->HAZ.HANDLE_ISSUES | none | stop | Every row; evaluate Required Groups and Field Validation against submitted business fields without requiring create/update intent |
