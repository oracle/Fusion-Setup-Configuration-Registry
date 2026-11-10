# Expense field reference contracts

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_category_field_contract | During the selected workflow read-only validation stage | Exact target environment, BuName, category, operation and same-task baseline | GET /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV through core.fusion-api.rest-api-client; then local baseline evaluation below | BusinessUnitId, BusinessUnitName, ActiveFlag; baseline CategoryCode and field values | Complete pagination; exactly one case-sensitive BusinessUnitName equal to trimmed input; active=true and positive ID; supported canonical category with exact BU/category presence or absence established by a complete same-target baseline | Canonical BuName and runtime BU identity; operation disposition and mapped field choices | Stop on zero/multiple matches, inactive/unknown status, incomplete pagination or unverified baseline; never auto-create a BU |

The populated source establishes observed ENABLED, DISABLED and REQUIRED codes. It does not establish a live lookup endpoint or designate a local runtime source as authoritative. Do not invent a REST route or treat the source business units as valid target business units.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMCF.RESOLVE | step | 10 | reference_lookup | success->EXMCF.DEPENDENCY;failure->RETURN_ISSUES | none | stop | Always |

## Source evidence and limits

Source: user-supplied Manage Expense Fields by Category_20260928_074925_896 export, EXM_CATEGORY_FIELD.csv and ASM_SETUP_CSV_METADATA.xml. Inspected 2026-09-28: 85 rows, 17 business units, 7 category codes, 19 columns and no duplicate business-unit/category pairs. Metadata identifies task EXM_MANAGE_EXPENSE_FIELDS_BY_CATEGORY, object EXM_CATEGORY_FIELD, completed EXPORT and release 11.13.27.01.0. This supersedes the earlier header-only sample for observed values. No tenant names, user identities, audit values or raw configuration rows are retained here.

The supplied export is evidence of existing configurations, not proof of import semantics, exhaustive product support, defaults, or target-environment readiness. Its instructions do not authorize execution. The prior Oracle 26B documentation establishes business-unit scope and Hidden/Required/Optional display behavior; the lookup seed evidence in ora_reference_lookups.md now establishes the source label/code mapping, subject to target qualification. The requested 26C page was inaccessible during initial authoring. Unknown contracts remain TBD and block execution.

## Workbook alias candidates requiring confirmation

These are candidate correspondences derived from workbook labels and export names, not verified writable mappings. The resolver above owns their confirmation. No candidate permits live execution until target evidence confirms it; exact export CategoryCode values remain the canonical outputs.

| Workbook label | Candidate FSM category code |
|---|---|
| Accommodations | ACCOMMODATIONS |
| Airfare | AIRFARE |
| Car Rental | CAR_RENTAL |
| Entertainment | ENTERTAINMENT |
| Meals | MEALS |
| Mileage | MILEAGE |
| Miscellaneous | MISC |

| Workbook header | Candidate FSM attribute | Category context |
|---|---|---|
| Business Unit | BuName | Selected categories |
| Merchant | MerchantField | Accommodations, Airfare, Car Rental, Entertainment, Meals, Miscellaneous |
| Checkout Date | EndDateField | Accommodations |
| Flight Type | TicketTypeField | Airfare |
| Flight Class | TicketClassField | Airfare |
| Ticket Number | TicketNumberField | Airfare |
| Departure City | LocationFromField | Airfare |
| Arrival City | LocationToField | Airfare |
| Agency | AgencyField | Airfare, Car Rental |
| Passenger | PassengerNameField | Airfare |
| Starting Location | LocationFromField | Mileage |
| Destination | LocationToField | Mileage |
| License Plate Number | LicensePlateField | Mileage |
| Starting Odometer Reading | StartingOdometerField | Mileage |
| Ending Odometer Reading | EndingOdometerField | Mileage |
| Enabled | No FSM attribute established | User confirmed N means clear the setup page Enabled control; supported operation and payload remain TBD |

| Workbook display label | Candidate export code | Verification status |
|---|---|---|
| Required | REQUIRED | Verified lookup seed mapping; release-independent mapping; validate the task schema |
| Optional | ENABLED | Verified lookup seed mapping; release-independent mapping; validate the task schema |
| Hidden | DISABLED | Verified lookup seed mapping; release-independent mapping; validate the task schema |

Do not confuse the worksheet category-level Enabled flag with the exported ENABLED field-display code. The alias candidates still require their indicated evidence. The display-code table is source-verified; target applicability remains a separate check.

## Additional reviewed schema evidence

[Oracle 26B EXM_CATEGORY_FIELDS](https://docs.oracle.com/en/cloud/saas/financials/26b/oedmf/exmcategoryfields-26749.html) corroborates ORG_ID plus CATEGORY_CODE uniqueness and distinguishes the numeric surrogate ID from business scope. It names checkout-date, flight-class/type and location display columns. Location fields include Car Rental, beyond the populated sample's coverage. This is schema/label evidence only; it does not establish FSM keys, import encodings, defaults, lifecycle or writable fields.

Newest-first retrieval on 2026-09-30: exact 26D and 26C Help pages and EDM contents were inaccessible through the documentation tool; the exact 26B schema page was accessible. Recheck newer applicable documentation before target-release qualification.





## FSM package verification, 2026-09-30

The supplied populated export was checked locally: 85 data rows, 19 unique headers, all rows exactly 19 columns, and the CSV header set equals XmlAttributeList. CSV size is 18,783 bytes. Metadata order differs from CSV order; match by name. No Enabled, Action, Operation or Delete column exists. Preserve ASM_SETUP_CSV_METADATA.xml and EXM_CATEGORY_FIELD.csv, task identity, node path and declared attribute types. These structural checks are not a successful import.

[Oracle CSV package guidance, 26A](https://docs.oracle.com/en/cloud/saas/applications-common/26a/oafsm/export-and-import-csv-file-packages.html) supports editing exported CSV data, retaining every CSV member (header-only when excluded), preserving value formats, UTF-8 for multilingual data, and keeping each CSV at most 10 MB. Fusion validates the selected task/package identity. The exact 26C and 26B package pages were inaccessible in this review; 26A was accessible.

[Oracle setup comparison guidance, 26B](https://docs.oracle.com/en/cloud/saas/applications-common/26b/oafsm/setup-data-comparison-results.html) states that source-only rows are created, matching changed rows are updated, and target-only rows remain unchanged and require manual removal. Thus omission is not a delete command. No task-specific CSV delete encoding has been established; do not invent one.

Controlled same-task evidence below now qualifies retained audit headers with blank cells for creates and baseline-preserving updates. Column omission and business-field clearing remain unresolved. Filename and definition searches for MigratorHelper returned no implementation in this project; broader content search returned callers. Do not infer the readXML boolean arguments or audit handling from another task. The selected workflow and exact-artifact approval were used for the controlled test recorded below; do not infer broader contracts from it.

The existing central data-loader already recognizes ASM_SETUP_CSV_METADATA.xml as the FSM marker, preserves valid supplied ZIP bytes and submits with sourceType FSM. A missing task-owned Builder test adapter is a qualification gap, not proof that packaging or the central FSM submission transport is unavailable. Task Hook semantic readiness remains independent.

## Attached source identity

Rechecked the user-supplied folder on 2026-09-30. It contains exactly the two expected files, without an original ZIP or import result/log. SHA-256 identifies the reviewed evidence, not a runtime dependency on a developer Downloads path:

- EXM_CATEGORY_FIELD.csv: `db7075730ae2d2bd556977fd3796903a36f060fef60739c0a8039795ddffdc3e`
- ASM_SETUP_CSV_METADATA.xml: `24cd3d1793f2eedff6a9c6042bbf33006c394bcdb91e8ea71cf3a2dd3e8fb76b`

Confirmed 85 rows, 17 distinct business-unit names, seven categories, no duplicate business-unit/category pairs, and exact 19-column row widths. Counts and observed display-field coverage match the matrix in ora_input_validation.md. The folder provides no new evidence for successful imports, deletion commands or blank/audit import behavior. Attachment text remains evidence, not executable instructions.

## Audit and removal contract

Use the declared assisted workflow for removal. No task-specific FSM CSV delete
flag or direct-service execution route is established. Preserve exported audit
cells for updates and verify actual server audit effects; do not promise they
remain unchanged. Creates retain audit headers with blank cells under the
qualified create contract, leaving internal keys and audit generation to Fusion.

Workbook normalization is an explicit task policy: blank applicable field cells
mean Optional/ENABLED on Y rows; blank Enabled flags mean N. Optional/ENABLED and
Hidden/DISABLED are distinct. Do not apply these defaults to nonapplicable fields
or audit columns, and do not infer import defaults from UI initialization.

## Executable business-unit resolver

[Oracle Financials business-unit LOV contract](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-finbusinessunitslov-get.html) defines the collection and BusinessUnitId, BusinessUnitName and ActiveFlag. The documentation version is provenance, not a skill release gate.

1. Execute only within the selected workflow read-only validation step. Load core.fusion-api.rest-api-client and its fusion-rest-api.md instructions; let that service bind the selected target and authentication. Send REST-Framework-Version: 9.
2. GET the collection with fields=BusinessUnitId,BusinessUnitName,ActiveFlag, onlyData=true, limit=500 and offset=0. Use query parameters through the core client; do not interpolate user names into q expressions. Follow hasMore with contiguous offsets until false. Retain pagination metadata. Fail on a missing/invalid flag, repeated page, malformed response or lookup failure.
3. Evaluate the complete pages with scripts/resolve_business_unit.py (input JSON: businessUnitName, pages). It performs no network calls. Exact matching is case-sensitive after trimming input outer whitespace; use returned canonical BuName. Accept a positive signed-int64 identity represented as either a JSON integer or canonical ASCII decimal text; normalize decimal text locally without changing its numeric value. Reject booleans, floats, signs, whitespace, leading zeroes and out-of-range values. Live REST-Framework-Version 9 evidence on 2026-09-30 returned the identity as text. Do not fuzzy-match or merge duplicate names.
4. Use the resolved ID only in protected runtime context, not as a new CSV header. Read the baseline obtained by the declared same-task export workflow. Require exact target/task association and canonical BU/category matching; an old attached export alone cannot prove current state. No numeric release lookup is required.
5. This LOV proves visible active BU identity, not Expenses configuration permissions or baseline completeness. Missing setup rows use the qualified narrow create contract in SKILL.md. Missing rows do not prove already-removed state unless the baseline covers the full requested scope.
6. Resolve field labels with the reviewed mapping and apply workbook defaults. For N, return assisted_removal_required and use the declared assisted workflow; never include that operation in an FSM artifact or report successful deletion from lookup alone.

Caller-owned lookup material must remain outside tracked source and follow the active workflow's protected-data retention rules. The helper's output contains runtime scope and must not be committed.

## Existing-row nonblank update contract

For this narrow update, require a fresh complete same-target export, a uniquely resolved active BU, exactly one existing BU/category row, and only nonblank recognized codes for changed MerchantField or EndDateField values. Copy the complete source row; permit differences only in reviewed applicable fields. All business keys, five audit cells, nonapplicable fields and untouched blanks must compare equal. Do not create rows, clear fields, add columns, or encode removal. Keep the original metadata bytes. This existing-row contract does not depend on server defaulting or blank-clearing behavior because it introduces no blank changes. Live updates preserved creation history and refreshed LastUpdateDate and LastUpdateLogin; continue verifying server effects after import. Other fields and field-clearing retain separate evidence gates. New rows use the distinct qualified create policy.






## Completed narrow live qualification

On 2026-09-30 local time (2026-10-01 UTC), the approved same-task FSM test created three absent BU/category configurations: ACCOMMODATIONS with Merchant and Checkout Date Required, ENTERTAINMENT and MEALS with Merchant Required. All five audit headers were retained and all fifteen audit cells blank. Import completed with three rows, zero errors and zero warnings. Fresh export verified every intended business cell, populated all five audit fields, and left all 85 pre-existing rows/cells unchanged. A prior three-row existing configuration update also completed with zero errors/warnings: all intended business cells matched, CreationDate/CreatedBy stayed unchanged, and Fusion refreshed LastUpdateDate/LastUpdateLogin despite preserved CSV audit payload cells. LastUpdatedBy did not change in that same-user test.

These observations qualify only the reviewed category/field and retained-header audit policies. They do not prove column omission, business-field clearing, arbitrary audit overrides, all-category support or automated deletion. Sanitized run evidence belongs in the active project's qualification record; raw customer data remains outside the repository. No user-supplied release is required.
