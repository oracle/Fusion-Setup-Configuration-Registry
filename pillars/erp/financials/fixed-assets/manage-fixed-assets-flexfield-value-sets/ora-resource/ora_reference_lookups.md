# Reference Lookups

## REST Verification Source

Use `core.fusion-api.apps-common.value-sets` and its shared REST client.
Resolve definitions using grouped set-code filters, then retrieve requested
values in batches per returned parent link. Complete pagination and verify
visibility and filter coverage before any absence decision. Exports remain
the FSM package contract source.

Use the shared REST client unchanged. Do not add local scripts, embedded
helpers, or per-record REST loops.

## Empty-Environment Create Path

A current same-task FSM export with the expected members, headers, and
`ASM_SETUP_CSV_METADATA.xml`, but no data rows, is valid package-contract
evidence for a first-time Value Set create in an empty target environment. It
does not provide an existing definition to preserve. When complete grouped REST
retrieval also confirms the requested `ValueSetCode` is absent, use the
new-definition defaults and approved design to author the first parent row and,
when requested, its value rows.

Do not require a populated parent export for this path. `ValueSetIdentifier`
may be derived from the supplied `ValueSetCode` under
`ora_defaulting_rules.md`. The reference-parent package route remains only for
adding values to an already resolved existing definition; it must never be used
to fill missing first-time-create data.

## Lookup Operations

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| find_value_set | After grouped REST retrieval, before package generation | Explicit code, REST definitions and complete query coverage | One exact ValueSetCode with compatible material fields | returned definition, identifier, format, length, applicable Uppercase Only setting, flags and protection evidence | Missing coverage or ambiguous/differing definitions block. An exact code is absent only after complete, effectively filtered REST retrieval with verified visibility. Unknown protection blocks mutation. |
| resolve_existing_definition_export | Existing definition requires same-task package evidence | Exact ValueSetCode returned by find_value_set and current-task export result | Returned parent rows include the exact resolved ValueSetCode; additional rows are permitted | selected parent-row evidence and export process identity | Unavailable or unusable filtering records its reason and proceeds to Reference Parent Package Source; a returned package without the exact parent row is unusable as current-task package evidence. |
| verify_table_validated_value_set_metadata | ValidationType is Table | Exact set and returned validationTable metadata | Follow the returned child link and compare required table settings | table-validation compatibility | Missing or ambiguous metadata blocks. This does not verify underlying table membership. |
| verify_value_set_target_state | Terminal successful import | Completed FSM log and fresh complete grouped REST evidence | Compare every requested definition, typed value, dependent parent, eligibility and supplied field | verified state and REST retrieval identity | Missing coverage or mismatches prevent verified success; do not automatically retry. |
| list_compatible_independent_value_sets | Parent selection needed | Verified REST definitions | Independent definitions compatible with requested type | parent selection list | Missing coverage or no compatible candidates stops selection. |
| list_parent_values | Parent set resolved | Paginated REST values from the selected definition's returned link | Exact enabled/effective compatible values | parent value list | Incomplete coverage or ambiguous keys blocks selection. |
| resolve_value_set_metadata | Complete grouped REST responses available | Definitions, values, requested scope and coverage | Same exact-key comparison as find_value_set | definition, codes and returned identifiers | No match is unverified unless absence is proven by coverage; differences require update-or-new direction. |
| resolve_value_set_definition_fields | Type selected | CSV schema, Definition Field Matrix and requested fields | Exact supported matrix row, technical-code mapping, and optional-field support | required/optional/prohibited fields and export-supported technical codes | Unsupported or ambiguous mappings block generation. |
| resolve_export_package_inventory | Preparation and sealed-artifact validation | Downloaded member/header/metadata contract and approved rows | Apply parent [Import Scope](../../SKILL.md#import-scope); verify exact rows and one definition parent per set receiving values | per-file/total counts, parent relationships and scope comparison | Missing members, changed contracts, unexpected/missing rows or duplicate parents block submission. |
| resolve_parent_value | Dependent value requested | Returned Independent ValueSetCode, typed parent and fully checked parent values | Exact compatible enabled/effective parent set/value | parent readiness and typed field | Missing coverage or incompatible/ambiguous parents blocks creation. |

## Lookup Execution Rules

### Grouped REST Retrieval

Within this delegated Fixed Assets workflow, use
`core.fusion-api.apps-common.value-sets` only as its implementation client. A
consuming setup task must delegate to
`erp.financials.fixed-assets.manage-fixed-assets-flexfield-value-sets`; it must
not invoke the generic skill directly or treat its direct result as validation
evidence. Resolve the target environment and read privileges through that client.
Deduplicate exact set codes from current caller metadata or an explicit request;
preserve case, spaces, and leading zeros. Query the `valueSets`
collection with `REST-Framework-Version: 2` and a grouped `q` filter using the
exact REST field name `ValueSetCode`, for example
`q=ValueSetCode='{ValueSetCode}'`. Pass repeated query parameters through the
shared client for URL encoding and escape literals under the REST query grammar
before encoding.

Resolve each exact returned `ValueSetCode` with a case-sensitive comparison,
then retain its material fields, protection/security settings, and child links.
Use returned links unchanged; do not construct resource keys or paths. Use the
returned `values` child link for all value queries and the returned
`validationTable` link when applicable. Resolve Uppercase Only before value
queries and show supplied-to-canonical conversion in verification.

Group canonical requested values by resolved set and query each returned `values`
collection. Resolve dependent parents from `IndependentValueSetCode`, adding
sets and parent values until the chain resolves; reject ambiguous or cyclic
references. Apply the parent's own case setting to a dependent parent and retain
the exact canonical parent/value pair.

Follow root and child pagination independently until `hasMore=false`. Verify
HTTP success, response shape, effective filters, exact scope, and read
visibility. Missing pages, failed requests, unsupported filters, or insufficient
visibility are unverified rather than absent. Do not exclude disabled or
ineffective values from existence checks.

Record environment, retrieval time, business date, requested scope, filters,
framework version, returned identities, page coverage, and response fingerprints
in redacted project evidence. Reuse evidence only for the unchanged batch.

Use current Oracle documentation for the [value-set collection](https://docs.oracle.com/en/cloud/saas/applications-common/26b/farca/op-servername-fscmrestapi-resources-11.13.18.05-valuesets-get.html),
[child values](https://docs.oracle.com/en/cloud/saas/applications-common/26b/farca/op-servername-fscmrestapi-resources-11.13.18.05-valuesets-valuesets_id-child-values-get.html),
and [advanced query syntax](https://docs.oracle.com/en/cloud/saas/applications-common/25c/farca/Manage_Collections.html).

### Scoped Existing-Definition Export

When a value is to be added to an existing definition, prefer a current-task
export filtered by the exact `ValueSetCode` returned by `find_value_set`.
Preserve the returned code exactly, including case, spaces, punctuation, and
leading zeros. If that filtering is unavailable or unusable, record the reason
and follow the Reference Parent Package Source route.

When a current-task export is used as package evidence, verify that its parent
rows include the exact resolved `ValueSetCode`. Setup-data export criteria act
as stacked filters: the requested rows must be included, but additional rows
may also be returned. Those additional rows do not invalidate the export;
identify and use only the exact resolved `ValueSetCode` rows downstream. REST
evidence remains the proof of the target definition and its current settings.

### Complete-Batch Comparison

Index definitions by exact set code and values by their independent or dependent
keys, retaining source-record numbers. Compare validation/data type, format,
length, material settings, enabled state, inclusive effectivity, parent
eligibility, and explicitly supplied attributes. Use documented typed values and
date representations; do not infer conversions or blank-date semantics.

Table-validation metadata does not establish underlying table membership. Report
unsupported membership checks rather than treating an empty values collection as
missing data. Classify findings by exact set/value/parent as present, missing,
disabled, ineffective, differing, ambiguous, or unverified.

| Situation | What Happens |
|---|---|
| Character values require verification | Resolve Uppercase Only from the verified definition through find_value_set before grouped value queries. Use only the target-supported mapping to UppercaseOnlyFlag; a missing field does not mean No. For a new definition confirmed absent, use the resolved creation proposal instead, clearly labelled proposed rather than target-verified. |
| Uppercase Only is Yes | Convert supplied lowercase or mixed-case Value text to uppercase for the working value rows, grouped queries and exact matching. Retain the original input and affected record references. Show Value Set, Uppercase Only, Supplied Value, Value Used, and verification result; explicitly identify every changed value, including when the uppercase value already exists and no import is needed. |
| Uppercase Only is No, not applicable, or unresolved | Preserve case for No or a verified nonapplicable setting. If applicable but unresolved, report unverified and obtain the setting through the declared reference workflow before conversion, absence classification, or mutation; never guess Yes or No. |
| Dependent parent text is supplied | Resolve and apply the independent parent's own Uppercase Only setting to IndependentValue, separately from the child's Value setting. Match the resulting exact parent-child pair. Do not apply the child flag to its parent. |
| Conversion scope | Convert only applicable Character value text and typed Character parent text. Preserve ValueSetCode, identifiers, names, descriptions, translations, numbers, dates, spaces, punctuation and leading zeros. Do not rewrite source workbooks or change existing target rows. Do not silently uppercase returned Fusion values to conceal a target mismatch. |
| Canonical values are ready | Before classifying present or missing, apply the duplicate and length checks in ora_input_validation.md to the converted working rows. Keep canonical values and source-to-value mappings consistent in the approved package proposal and downstream reference handoff. Existing uppercase matches are no-ops, not new values. |
| Parent post-import verification criteria | After terminal import success and process-log review, the Fixed Assets parent retrieves fresh responses for affected sets, values, and required parents. Compare every requested definition, value, parent, and supplied attribute against the approved definition and canonical rows. A changed Uppercase Only setting or canonical value is a mismatch, not permission to reinterpret approved values. The child task hands off after accepted initiation and does not perform this verification. |

## Reference Parent Package Source

Use a template/spec package only to add approved value rows to one exact
existing value set when a scoped populated export is unusable because of volume
or process result. It does not remove the requirement for exactly one
`FND_APP_FLEX_VALUE_SET.csv` parent row for every changed value-row set.

Require all of the following before this route is selected:

1. Complete grouped REST evidence resolves one existing target definition and
   the requested missing values and dependent parents.
2. A scoped populated export was attempted or assessed as unusable, with its
   sanitized reason and process identity recorded when available.
3. The template/spec package is for this task, environment, and release and
   contains the required CSV members and `ASM_SETUP_CSV_METADATA.xml`.
4. The package source exposes the exact headers, field order, quoting, and
   metadata contract. It proves neither target state nor existing field values.

For the required same-package parent row, direct current REST mapping is
permitted only for `ValueSetCode`, `ModuleId`, `Description`,
`ValidationType`, `ValueDataType`, `ValueSubtype`, `MaximumLength`,
`Precision`, `Scale`, `UppercaseOnlyFlag`, `ZeroFillFlag`,
`SecurityEnabledFlag`, `DataSecurityObjectName`, minimum and maximum typed
range fields, and `IndependentValueSetCode`, and only when the exact returned
member is present. `ValueSetIdentifier` may be a true blank only when it is
optional in the target header and absent from the current REST response. Audit
columns are true blanks only when target metadata permits them.

Do not use first-time-definition defaults, derive a field from ValueSetCode,
copy an unmapped REST field, or leave a required or material existing field
unresolved. The package contains only required members, metadata, one validated
parent row per changed set, and approved changed value rows. Send its source
identity and field-source mapping to the parent approval workflow; fresh
post-import REST verification remains required.

## Existing Definition and Requested Values

A matching definition proceeds to VSET.CHECK_VALUE_SCOPE; it does not prove
the requested values exist. Compare every participating set against the covered
REST evidence and retain exact keys and affected source record numbers.

| Outcome | Condition | Output |
|---|---|---|
| definition_only | Compatible definition and no Manage Values scope | Reuse definition; no import. |
| values_present | All requested values, parents, eligibility and supplied material fields match complete REST data | Reuse definition and values; no import. |
| values_missing | A value is absent from proven complete coverage; all other requested values match, the definition is verified unprotected, and missing inputs/parents are resolved | Preserve definition and propose only confirmed missing values. |
| blocked | Coverage, protection or required fields unknown, or values disabled, ineffective, differing or ambiguous | Report grouped findings; no inferred creation or automatic partial import. |

Include exactly one unchanged exported definition parent per affected set in
FND_APP_FLEX_VALUE_SET.csv. Match the value CSV's
FND_APP_FLEX_VALUE_SET.ValueSetCode to that parent. Outside the validated
Reference Parent Package Source route, preserve exported identifiers and
settings; do not derive an existing identifier or reconstruct an omitted
definition from REST. An unavailable field is not automatically mandatory: use
the target schema to establish requirements and blank serialization semantics.
Exclude no-op sets from the change proposal. Any blocked set stops the batch.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| VSET.LOOKUP_EXISTING | decision | 30 | evaluate_result | match->VSET.CHECK_VALUE_SCOPE;absent->VSET.APPLY_DEFAULTS;different_or_ambiguous->VSET.HANDLE_LOOKUP | VSET.RESOLVE_DEPENDENCIES | stop | REST definition batch retrieved and pagination, filters and visibility verified |
| VSET.CHECK_VALUE_SCOPE | decision | 35 | evaluate_result | definition_only->VSET.DONE_MATCH;values_present->VSET.DONE_VALUES;values_missing->VSET.APPLY_DEFAULTS;blocked->VSET.HANDLE_VALUES | VSET.LOOKUP_EXISTING | stop | Existing definition matches; compare requested values against complete grouped REST responses |
