# UN Number Input Validation

The approved create/update authoring plan selects submitted business fields
as the local authority for these checks. Field types, nullability, and sizes
retain the existing Oracle [26D create contract](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingunnumbers-post.html)
and [26D update contract](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingunnumbers-unnumberid-patch.html)
baseline. Requiring name and code on every create/update row, blank rejection, and the field
allowlist are FSCR policies. Check each row independently and retain all issues.

The approved extension accepts HazardClass as preparation context and verifies
all non-null HazardClassId values against Fusion. UNNumberId remains unchecked
locally. Description is required for explicit creation and optional for update or
neutral apply; supplied null is always rejected.
Only a create/update empty CSV/XLSX InactiveDate cell becomes an omission.
The input phase must be known: preparation may derive a separate loader record;
Data Loader task validation must use captured records without modifying them.

## Captured Source Validation

For Data Loader validation, captured records are a read-only evaluation view of
the exact prepared ZIP after core mapping and conversion. Read its DAT members
losslessly, honoring escaping and record directives, and keep business fields
separate from RestAction/control metadata. Do not substitute mutable original
CSV/XLSX sources or a pillar replacement serializer. If the artifact cannot be
decoded losslessly, stop under the
[prepared artifact gate](ora_error_handling.md#prepared-artifact-gate).

## Operation Selection

Use each row's explicit prepared loader operation. Exact RestAction=DELETE
selects delete validation; RestAction is control metadata, not business data.
An explicit delete request must be represented by that marker during loader
preparation before these rules run. Missing or blank RestAction retains the
existing create/update rules; never infer deletion from UNNumberId alone.
Conflicting task intent and row operation are FAILED and block preparation.
For an explicitly mixed-operation input, validate each row by its own marker.
Other operation values remain subject to Data Loader's source contract and must
never be reinterpreted as DELETE by trimming or case conversion here.

The [Oracle DELETE contract](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingunnumbers-unnumberid-delete.html)
identifies UNNumberId as the path key. Presence-only local checking and the
ID-only business-field allowlist below are user-approved FSCR policies. The
Data Loader retains type, format, range, existence, and server checks.

Explicit create means user/task intent to create the row or an explicitly prepared
RestAction=POST. Explicit update means user/task intent to update or an explicitly
prepared RestAction=PATCH. Retain the intent, its source, and row scope in workflow
context through preparation and captured-source validation, never in business data.
A generic POST transport used for apply/upsert is not an explicit create marker.
Missing/blank operation context or neutral apply leaves operation selection to
Data Loader. Never infer create/update from IDs, code presence, or record existence.
In mixed input, apply row-scoped intent; a batch-wide explicit intent applies to
all rows in that scope. Contradictory task intent and explicit row operations fail;
neutral apply does not conflict with an explicit per-row operation. Do not assign
or normalize RestAction to implement these checks.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Required business fields | Both UNNumber and UNNumberCode | MISSING if either is absent; FAILED if either is null, blank, or invalid | Supply both nonblank strings within their field limits | Create/update rows only (RestAction is not DELETE) | |
| Explicit create description | Description in addition to UNNumber and UNNumberCode | MISSING if absent; FAILED if supplied but invalid | Supply a nonblank string of at most 240 characters; never generate a value | Explicit create intent or explicit prepared RestAction=POST | |
| Delete identifier | UNNumberId only | MISSING when absent; FAILED when null, empty string, or whitespace-only string | Supply the ID of the record to delete; do not resolve from name or code | Delete rows (RestAction=DELETE) | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| UNNumber | Require a string, maximum 20 characters, containing at least one non-whitespace character; reject null. Detect blanks without trimming or changing the value. | Create/update rows; required | |
| UNNumberCode | Require a string, maximum 30 characters, containing at least one non-whitespace character; reject null. Preserve case, leading zeros, surrounding whitespace, and Unicode. Pass it as supplied business data without assigning lookup-key or code-change semantics. | Create/update rows; required | |
| Description | Explicit create requires a nonblank string of at most 240 characters: omission is MISSING; null, empty, whitespace-only, non-string or overlong values are FAILED. For update or neutral apply, omission is allowed; supplied values must be strings of at most 240 characters, including empty or whitespace-only strings, and null is rejected. Check blankness without trimming accepted values. Data Loader retains downstream operation-specific checks. | Non-delete rows; required only for explicit create | |
| InactiveDate | Optional. Accept omission or an empty CSV/XLSX cell as not provided and omit InactiveDate from that record. Preserve explicit null. Otherwise require a valid Gregorian calendar date written YYYY-MM-DD; reject timestamps, malformed dates, impossible dates, and non-string non-null values. Do not impose a future-only rule. | Create/update rows; only when a nonempty value or explicit null is supplied | |
| UNNumberId | Optional. Preserve any supplied value exactly, including null, without type, range, format, or existence validation and without normalization. Defer ID acceptance and identity handling to Data Loader; local readiness makes no claim that the ID is valid. | Create/update rows; when supplied; omission is allowed and no ID is generated | |
| HazardClassId | Optional. Without a name, preserve omission or explicit null and skip lookup. Non-null values must be integers (not booleans) or strings matching [0-9]{1,18}; integer absolute value must be below 10^18. Reject floats, signs/whitespace in strings, exponent notation, arrays, objects and non-ASCII digits. Compare/query losslessly; preserve supplied representation. Subsequent lookup verifies existence. | Create/update rows | |
| HazardClass | Preparation-only display name. If supplied, require a nonblank string of at most 40 characters; preserve case and whitespace. Null or blank names fail. Name with explicit null ID fails as conflicting intent. With a non-null ID, both must agree during lookup. HazardClassCode and HazardClassName are not accepted aliases. | Create/update preparation; never a writable loader attribute | |
| Supported business fields | Accept UNNumber, UNNumberCode, Description, InactiveDate, UNNumberId, HazardClassId as writable business fields. Accept HazardClass separately as preparation context only; it must not appear in captured loader business records. Reject HazardClassCode and HazardClassName. Reject unknown business fields and response metadata such as links, CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, and @context; never silently drop them. Operation, environment, and loader control fields are separate workflow context, not business fields. | Create/update rows | |
| Delete UNNumberId | Require presence; reject null, empty string, and whitespace-only string. Preserve every other supplied value and type exactly, including malformed IDs; do not validate type, format, range, or existence locally. | Delete rows only | |
| Delete business fields | Accept only UNNumberId. Reject UNNumber, UNNumberCode, Description, InactiveDate, HazardClassId, response metadata, and all other business fields, even if blank or null. Do not silently discard them. RestAction remains separate control metadata. | Delete rows only | |
| Operation context | Intent is optional. Apply the explicit-create Description requirement from scoped user/task intent or an explicit prepared RestAction=POST; generic apply/upsert transport is insufficient. Preserve intent and its source outside business data through capture. Delete requires explicit RestAction=DELETE; contradictory intent and operation fail. Never select an operation from IDs or codes or rewrite the marker. | Every row | |


## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Row passes field checks | FIELD_VALID; no record-existence or server-acceptance claim | Run the conditional hazard-class resolver, then preservation and design checks before Data Loader handoff | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| UN.VALIDATE_INPUT | decision | 10 | validate_input | valid->UN.RESOLVE_HAZARD_CLASS;missing->UN.HANDLE_ISSUES;invalid->UN.HANDLE_ISSUES;unsupported->UN.HANDLE_ISSUES | none | stop | Every row; evaluate scoped intent and conditional create Description requiredness before lookup, retain delete rules, collect all issues, and reject conflicting operation instructions |
