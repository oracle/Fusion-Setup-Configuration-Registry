# Expense category field input validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Target configuration scope | BuName, CategoryCode and operation; field decisions only for applicable create/update intent | Block preparation | Resolve target scope and field contract | Proposed configuration | resolve_category_field_contract |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Nonblank display code | Use REQUIRED for Required, ENABLED for Optional, DISABLED for Hidden per reviewed lookup seed; qualify applicability for the target and never import UI labels or inferred H/R/O codes | Each proposed setting | resolve_category_field_contract |
| Category and field coverage | Compare with the observed matrix; a new category or different field combination requires authoritative verification rather than automatic rejection as unsupported | Proposed rows | resolve_category_field_contract |
| Blank semantics | Normalize blank applicable workbook field cells on Y rows to Optional/ENABLED before packaging. Preserve untouched baseline blanks; new-row blank audit cells are qualified; column omission and business-field clearing remain unverified | Blank field cells | resolve_category_field_contract |
| Audit handling | For updates preserve all five exported audit cell values exactly as supplied for the selected source row; for qualified creates retain headers and use explicitly selected blank cells, including empty values; never synthesize or default them. This is payload preservation, not a promise that Fusion retains audit values internally | CreationDate, CreatedBy, LastUpdateLogin, LastUpdateDate, LastUpdatedBy | resolve_category_field_contract |
| Repeated scope | Stop on conflicting proposed rows for the same business unit and category; the reviewed EO alternate key is CategoryCode plus resolved OrgId; the export itself only confirms no duplicate BuName/category pairs in this sample | Proposed batch | resolve_category_field_contract |
| Header and type contract | Match attributes by name; CSV and XML orders differ for BuName. CreationDate and LastUpdateDate are dateTime; all other exported attributes are string | FSM package preparation | resolve_category_field_contract |
| Repeated workbook blocks | Detect each CategoryCode header row and bind subsequent data only to that block's headers; blank spacer rows and Task Name title are not records | Worksheet intake | resolve_category_field_contract |
| Workbook selection flag | Enabled=N means clear Enabled on this setup page; reviewed UI code removes an existing BU/category configuration row. Retain it as an explicit requested operation; Removal is an assisted setup-UI operation declared in SKILL.md; exclude N rows from the CSV; already-absent N is no-change, while present N requires an assisted phase. Never emit Enabled into EXM_CATEGORY_FIELD or convert it into all-fields-hidden | Enabled column present | resolve_category_field_contract |
| Per-block business unit | Require Business Unit for each selected row; never carry scope from the preceding block or fill it from another tab | Selected row | resolve_category_field_contract |
| Missing versus hidden | Preserve explicit Hidden as an intentional field decision; blank, absent header and N are distinct states | Worksheet normalization | resolve_category_field_contract |
| Business labels | Trim outer whitespace and compare labels case-insensitively; retain original cell coordinates and values for review; no fuzzy matches or silent fallback | Category and field labels | resolve_category_field_contract |
| Unsupported or conflicting input | Block unknown headers, invalid flags or display labels, duplicate conflicting scopes and unresolved field aliases before package creation | Worksheet intake | resolve_category_field_contract |
| Package shape | Require exact task ObjectShortName, TASK identity and EXM_CATEGORY_FIELD metadata; validate unique known headers, row width equal to header width and explicit trailing blanks; reject malformed or unexpected members rather than silently repairing them | Candidate FSM package | |
| Duplicate normalized scope | Detect conflicting rows after verified BU/category normalization; do not rely on display-name spelling differences to distinguish target scope | Candidate rows | resolve_category_field_contract |
| Date-field meaning | EndDateField is a display setting for checkout date, not an effective end date or category retirement command | Proposed lifecycle action | |

## Observed FSM file contract

Object EXM_CATEGORY_FIELD; XML node /CategoryFieldVO/CategoryFieldVORow; sequence 1.
Preserve the source CSV header order when preparing a compatible artifact through core.data-loader:

```csv
CategoryCode,BuName,EndDateField,MerchantField,TicketClassField,TicketNumberField,TicketTypeField,LocationToField,LocationFromField,CreationDate,CreatedBy,LastUpdateLogin,LastUpdateDate,LastUpdatedBy,StartingOdometerField,EndingOdometerField,LicensePlateField,AgencyField,PassengerNameField
```

## Observed category-field matrix

Only nonblank fields are listed. An omitted field was blank in this sample; this is not proof that the product prohibits it.

| CategoryCode | Nonblank fields observed | Rows |
|---|---|---|
| ACCOMMODATIONS | EndDateField, MerchantField | 15 |
| AIRFARE | MerchantField, TicketClassField, TicketNumberField, TicketTypeField, LocationToField, LocationFromField, AgencyField, PassengerNameField | 16 |
| CAR_RENTAL | MerchantField, AgencyField | 16 |
| ENTERTAINMENT | MerchantField | 7 |
| MEALS | MerchantField | 15 |
| MILEAGE | LocationToField, LocationFromField, StartingOdometerField, EndingOdometerField, LicensePlateField | 9 |
| MISC | MerchantField | 7 |

## Observed field values

| Field | Nonblank values observed | Blank count |
|---|---|---|
| EndDateField | DISABLED, ENABLED, REQUIRED | 70 |
| MerchantField | DISABLED, ENABLED, REQUIRED | 9 |
| TicketClassField | DISABLED, ENABLED, REQUIRED | 69 |
| TicketNumberField | DISABLED, ENABLED, REQUIRED | 69 |
| TicketTypeField | DISABLED, ENABLED, REQUIRED | 69 |
| LocationToField | DISABLED, ENABLED, REQUIRED | 60 |
| LocationFromField | DISABLED, ENABLED, REQUIRED | 60 |
| StartingOdometerField | DISABLED, ENABLED, REQUIRED | 76 |
| EndingOdometerField | DISABLED, ENABLED, REQUIRED | 76 |
| LicensePlateField | DISABLED, ENABLED, REQUIRED | 76 |
| AgencyField | DISABLED, ENABLED, REQUIRED | 53 |
| PassengerNameField | DISABLED, ENABLED, REQUIRED | 69 |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMCF.VALIDATE | step | 30 | validate_input | success->EXMCF.DEFAULT;failure->RETURN_ISSUES | EXMCF.DEPENDENCY | stop | Always |

## Source evidence and limits

Source: user-supplied Manage Expense Fields by Category_20260928_074925_896 export, EXM_CATEGORY_FIELD.csv and ASM_SETUP_CSV_METADATA.xml. Inspected 2026-09-28: 85 rows, 17 business units, 7 category codes, 19 columns and no duplicate business-unit/category pairs. Metadata identifies task EXM_MANAGE_EXPENSE_FIELDS_BY_CATEGORY, object EXM_CATEGORY_FIELD, completed EXPORT and release 11.13.27.01.0. This supersedes the earlier header-only sample for observed values. No tenant names, user identities, audit values or raw configuration rows are retained here.

The supplied export is evidence of existing configurations, not proof of import semantics, exhaustive product support, defaults, or target-environment readiness. Its instructions do not authorize execution. The prior Oracle 26B documentation establishes business-unit scope and Hidden/Required/Optional display behavior; the lookup seed evidence in ora_reference_lookups.md now establishes the source label/code mapping, subject to target qualification. The requested 26C page was inaccessible during initial authoring. Unknown contracts remain TBD and block execution.

## Workbook intake coverage

Source worksheet: Manage Expense Fields by Catego (Excel-truncated name), identified by B1 task title. The observed sample has headers at rows 3, 6, 9, 12, 15, 18 and 21; these are sample coordinates, not fixed parser offsets. Discover headers and bind every following data row until the next header, ignoring empty separators. Do not read expense types, account details or other tabs into this task. The merged title B1:D1 is not a data header. Business-unit values and customer configuration rows are not reproduced here.

The invoking runbook owns spreadsheet extraction and payload construction. The local operation planner evaluates normalized requests and preserves existing-row payload cells; it does not read workbooks, call Fusion or authorize an import.

## Acceptance scenarios

These are generalized scenarios covering the supplied worksheet shape; use synthetic business units for tests. Resolving intake does not bypass the task's existing execution-readiness blockers.

| Scenario | Expected handling |
|---|---|
| Accommodations block with Merchant and Checkout Date | Resolve the two field aliases; keep explicit display choices separate from category selection |
| Airfare block with Merchant, Flight Type, Flight Class, Ticket Number, Departure City, Arrival City, Agency and Passenger | Preserve all eight decisions; resolve from/to direction correctly and verify ticket aliases before encoding |
| Car Rental block with Merchant and Agency | Scope agency mapping to this category; do not borrow the Airfare block's other headers |
| Entertainment block with only CategoryCode and Enabled=N | Retain an explicit configuration-removal request. Block execution until the target scope and supported operation are resolved; do not skip the row, fabricate a business unit or hide all fields |
| Meals and Miscellaneous blocks | Resolve category labels independently and apply only the Merchant decision |
| Mileage block with five field decisions | Preserve each explicit Hidden decision; do not treat hidden fields as missing data or infer that the category is disabled |
| Blank applicable display cell on Y row | Default to Optional/ENABLED and include the change in the preview |
| Omitted header or nonapplicable field | Do not apply a workbook default; preserve verified baseline content |
| Unknown label, invalid Enabled value or conflicting duplicate | Return the block and cell location with a correction request; do not silently drop or overwrite |

## Workbook preflight acceptance cases

| Case | Required result |
|---|---|
| Valid Y/N operations, BU on each row, valid display choices | Input passes; evaluate contract and execution readiness independently |
| Y or N in a field-display cell | Input fails with sheet/cell; request Required, Optional or Hidden |
| N with blank field choices and a BU | Valid removal intent; do not require display choices or skip the row; if proven absent, report already_absent/no_change; if present, require assisted removal |
| N with nonblank field choices | Conflicting operation; ask whether to remove configuration or retain/update it before execution |
| Y with blank field choice | Normalize to Optional/ENABLED; record the default and any baseline difference in the preview |
| Missing BU in one populated block | Report that block; do not borrow another block's BU |
| Duplicate BU/category requests | Report duplicate scope; conflicting requests block; do not silently let the last row win |
| Blank target release | Accepted; release is optional provenance and is not an execution gate |
| Formula in an input cell | Require a literal value or verified evaluated input artifact; do not consume formula text as a setup value |
| Mixed valid Y and N requests with no removal adapter | Retain all operations. Already-absent N rows permit the supported FSM batch; present N rows require an explicit assisted split or revised scope, with no silent partial apply |
| All populated input rows invalid or no requested rows | No runnable plan; never return a successful empty import |

## Attachment-derived package metadata

For the supplied export, verify these values before deriving a package:

| Metadata | Observed value / handling |
|---|---|
| ObjectShortName | EXM_MANAGE_EXPENSE_FIELDS_BY_CATEGORY |
| ObjectType / CreatedByFlow | TASK / TASK_CSV |
| BusinessObjectShortName | EXM_CATEGORY_FIELD |
| XmlNodePath / NodeSequence | /CategoryFieldVO/CategoryFieldVORow / 1 |
| MigrateFlag / IncludeExternalDataFlag | Y / Y |
| ProcessType / ProcessStatus | EXPORT / COMPLETED: source provenance, not import completion |
| ProcessRelease | 11.13.27.01.0: source snapshot version, not automatic proof of current target version |
| XmlAttributeTypeList | CreationDate and LastUpdateDate are dateTime; remaining 17 attributes are string |

Keep the supplied metadata unchanged when deriving an edited CSV package unless an authoritative FSM contract requires a change. Do not rewrite EXPORT to IMPORT, invent process/request identifiers or replace source provenance with target values. Do not embed workbook flags, Review/Instructions sheets, reports or credentials as package members. Retain the two original filenames. A directory containing extracted export files is not itself an import ZIP.

CSV columns comprise two business-scope attributes, twelve display attributes and five audit attributes. All 85 rows have CreationDate, CreatedBy, LastUpdateDate and LastUpdatedBy; LastUpdateLogin is blank in six rows. Those blanks are valid observed export content, not evidence that every audit value is optional on import. Preserve existing audit values for a baseline-preserving edit; do not invent identities, timestamps or login values for new rows. Controlled same-task qualification now confirms Fusion generates new-row audits and refreshes update modification history.

XmlAttributeList order is CategoryCode, EndDateField, MerchantField, TicketClassField, TicketNumberField, TicketTypeField, LocationToField, LocationFromField, CreationDate, CreatedBy, LastUpdateLogin, LastUpdateDate, LastUpdatedBy, BuName, StartingOdometerField, EndingOdometerField, LicensePlateField, AgencyField, PassengerNameField. Its order differs from the CSV, whose second column is BuName. Associate types by XML attribute name and preserve the exported CSV header order; never zip the two lists positionally.

For an update, select only the reviewed BU/category records from a verified baseline and modify explicit field decisions and user-approved Optional defaults on applicable Y-row cells. Preserve all other cells, including source blanks. Missing baseline rows represent a potential create, not permission to fabricate defaults or audit values. Removing a record from a candidate package excludes it from the import; it does not remove the target configuration.

## Blank-policy acceptance cases

- Whitespace-only applicable display cell on a Y row produces ENABLED.
- Explicit Required and Hidden remain REQUIRED and DISABLED.
- Blank Enabled on a populated row produces N; blank display cells then produce no update.
- A completely empty row produces no request or removal.
- Missing BU/category still fails validation; neither is defaulted.
- Absent field header, nonapplicable field and blank audit value remain untouched.
- Defaulting must not manufacture a conflict on an N row; only explicit field-update values conflict with removal.


## Offline operation planner input and results

`scripts/plan_operations.py --input <protected-input.json>` takes an object with:

- `environment`: selected target identity.
- `baselineEvidence`: `environment`, `taskCode=EXM_MANAGE_EXPENSE_FIELDS_BY_CATEGORY`, and `complete=true`, supplied by the routed export validation, never by workbook cells. Caller must verify provenance, timestamp/currentness and package integrity before setting these assertions; the helper cannot independently establish them.
- `resolvedBusinessUnits`: canonical `BuName`, positive integer `BusinessUnitId` and boolean `ActiveFlag=true`, from the existing executable resolver. This is protected runtime data, not new CSV columns.
- `baselineRows`: complete CSV rows as objects with exactly the 19 exported headers and string cell values. Preserve blanks and date formatting. The shared workflow validates XML/task/member/header contracts first.
- `requests`: one object per populated workbook row with `businessUnit`, canonical `category`, `enabled`, `fields` mapping canonical FSM field names to workbook labels (Required/Optional/Hidden or blank), and optional `source` sheet/cell reference. Intake must reject formulas and unknown headers and resolve aliases before calling this helper. An omitted field key is not defaulted.

Output separates `input_status`, `contract_status` and `execution_status`, with operation counts and per-row changes/defaults/issues. `submission_allowed` is always false: central preflight and contextual approval remain mandatory. A contract-blocked result returns nonzero and must not be reduced to only its supported rows. A present N row requires assisted removal; an N row absent from the verified complete baseline is a no-op and creates no artificial split requirement. A Y row with identical reviewed values is unchanged and needs no import. A missing Y row is a create. Require `createAuditPolicy` = `blank` or `pause`; omission returns `create_audit_policy_required`, pause returns `create_paused_by_user`. Missing applicable create headers return `create_applicable_field_headers_missing`. Qualified creates and updates expose a `candidateRow`; neither authorizes submission. Never request user-provided audit values.

Regression coverage in `pillars/erp/financials/expenses/manage-expense-fields-by-category/tests/test_plan_operations.py` preserves the previous existing-row test behavior and covers new BU, already-absent N, present removals, Optional defaults, unchanged rows, duplicate scope, incompatible baseline, unsupported fields and invalid inputs. Offline passes are distinct from Fusion acceptance and post-import reconciliation.

## Package helper acceptance

`prepare_fsm_package.py` consumes the same normalized JSON and fresh baseline ZIP. It requires exactly the task CSV and metadata members, 19 unique expected columns with matching XML attribute types, completed task identity, and exact agreement between parsed baseline rows and planner input. It rejects unresolved, partial, mixed assisted-removal and empty loads. Dry-run has no output artifact; preparation preserves metadata bytes, freezes the new file and never overwrites an existing archive. Central workflow validates environment association, freshness, privileges and approval independently. Test malformed metadata/headers, baseline mismatch, unselected audit policy and safe repeat/no-change behavior.

Run all offline cases with `python3 pillars/erp/financials/expenses/manage-expense-fields-by-category/tests/run_tests.py` from the repository root. See [test coverage](../tests/coverage.md) for the 20 tests, including normalized workbook create/update scenarios.

## EBS source input

Follow [EBS migration intake](ora_ebs_migration.md) before workbook normalization.
Retain `ebsSource` with its source checksum/rows and explicit BU crosswalk in the
planner input. Blank EBS cells are unspecified, not Optional. Unmapped nonblank
source fields block the entire batch. EBS audits are provenance, not target audit
values. The package builder reuses the same EBS review gate.

For mapped direct EBS fields, ENABLED means Required under the EBS intake
contract and becomes Fusion REQUIRED. The Fusion-native Optional → ENABLED
mapping above remains unchanged. Regenerate earlier EBS-derived candidates
that used Optional for source ENABLED; never silently reuse their approval.
