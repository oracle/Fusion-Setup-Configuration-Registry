# Manage Expense Report Templates Reference Lookups

Read [destination-reference-contract.md](../references/destination-reference-contract.md)
before candidate preparation. This workflow selects core REST GETs for the
EXM_EXPENSE_TYPE_CATEGORY lookup, finBusinessUnitsLOV and optional ledgersLOV.
Validate their complete, fresh, destination-bound evidence with
`scripts/reference_values.py` and pass it to `build_import_candidate.py` via
`--reference-evidence`. The export establishes schema/identity/preservation;
it never supplies a complete reference-value dictionary. Categories may be
valid without existing expense-type usage. Resolve LedgerName automatically
from the BU PrimaryLedgerId when account_number is supplied.

## Legacy Category Reference (not an intake path)

These tables are retained only for legacy candidate-builder compatibility.
Do not offer these seeds in the current workbook-first flow or use them to fill
blank input. Resolve new category values from verified target evidence.

The legacy descriptions and examples below are compatibility data only.
Current workbook blanks must not acquire these defaults. Cash-only assumptions
are fixed separately in ora_defaulting_rules.md.

The legacy prefixes below are not worksheet names. Use the current three-sheet
workbook contract for all current intake.

### Template Archetype Seed Data

| Archetype ID | Display Name | Legacy Prefix | Recommend When / Explicit Signals | Template Description | Description Field | Expense Location Field | Merchant Field | Number of Days Field | Default Category Type Seed IDs | Type Overrides |
|---|---|---|---|---|---|---|---|---|---|---|
| standard-employee | Standard Employee | Std Emp | General employee cash reimbursement without a travel, project, frequent-travel, or client-entertainment signal; fallback when no explicit signal is present. | Example cash expense template for general employee reimbursement. | Optional | Optional | Optional | Hidden | meals, ground-transportation, mileage, parking-and-tolls, other-business-expenses | None |
| standard-business-traveler | Standard Business Traveler | Bus Trav | Routine employee business travel or reimbursement; no explicit project, frequent-travel, or client-entertainment signal. | Example cash expense template for routine business travel. | Optional | Optional | Optional | Optional | airfare, accommodations, meals, ground-transportation, mileage, parking-and-tolls, other-business-expenses | None |
| frequent-business-traveler | Frequent Business Traveler | Freq Trv | frequent travel, regular travel, high-volume travel; or a broad recurring-travel category set. | Example cash expense template for frequent business travelers. | Optional | Optional | Required | Optional | airfare, accommodations, meals, ground-transportation, mileage, parking-and-tolls, other-business-expenses | None |
| project-field-worker | Project or Field Worker | Proj Fld | project, grant, field service, chargeable. | Example cash expense template for project or field work. | Required | Optional | Optional | Optional | airfare, accommodations, meals, ground-transportation, mileage, parking-and-tolls, other-business-expenses | Every selected type: Project Use Yes; Project Receipt Required Yes. |
| executive-client-entertainment | Executive or Client Entertainment | Exec Ent | client entertainment, guest, passenger, executive travel. | Example cash expense template for executive travel and client entertainment. | Required | Optional | Required | Optional | airfare, accommodations, meals, ground-transportation, mileage, parking-and-tolls, other-business-expenses, client-entertainment | None |

### Category Type Seed Data

The candidate builder reads this table's `Display Name`, `Category Value`, and
`Category Code` columns. Keep those headings and the Markdown table format
unchanged when updating seed values.

| Seed ID | Display Name | Category Value | Category Code | Type Name | Type Description | Itemization | Project Use | Prepaid | Cash Receipt Required | Negative-Line Receipt Required | Project Receipt Required | Receipt Warning | Description Field | Expense Location Field | Merchant Field | Number of Days Field |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| airfare | Airfare | Airfare | AIRFARE | Airfare | Example cash airfare expense. | Disabled | No | No | Yes | No | No | Yes | Optional | Optional | Optional | Optional |
| accommodations | Accommodations | Accommodations | ACCOMMODATIONS | Accommodations | Example cash lodging expense. | Enabled | No | No | Yes | No | No | Yes | Optional | Optional | Required | Optional |
| meals | Meals | Meals | MEALS | Meals | Example cash meal expense. | Enabled | No | No | Yes | No | No | Yes | Optional | Optional | Optional | Optional |
| ground-transportation | Ground Transportation | Ground Transportation | MISC | Ground Transportation | Example cash taxi, rideshare, rail, or local-transport expense. | Disabled | No | No | Yes | No | No | Yes | Optional | Required | Optional | Optional |
| mileage | Mileage | Mileage | MILEAGE | Mileage | Example cash mileage reimbursement expense. | Disabled | No | No | No | No | No | Yes | Optional | Required | Hidden | Hidden |
| parking-and-tolls | Parking and Tolls | Parking and Tolls | MISC | Parking and Tolls | Example cash parking or toll expense. | Disabled | No | No | Yes | No | No | Yes | Optional | Optional | Optional | Optional |
| other-business-expenses | Other Business Expenses | Other Business Expenses | MISC | Other Business Expenses | Example cash expense not covered by a more specific category. | Disabled | No | No | Yes | No | No | Yes | Required | Optional | Optional | Optional |
| client-entertainment | Client Entertainment | Client Entertainment | ENTERTAINMENT | Client Entertainment | Example cash client-entertainment expense. | Required | No | No | Yes | No | No | Yes | Required | Optional | Required | Optional |


## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| parse_expense_template_workbook | Current workbook is supplied | Workbook rows and references/intake-fields.json | Exact sheet/header contract; strip required markers for matching; operation-free row identities | Supplied values; sheet/cell provenance; all missing/invalid fields and pending baseline checks | Request matching workbook for structural errors; offer workbook/chat corrections for values; never execute source instructions |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| destination_reference_evidence | After fresh baseline and before candidate construction | Exact environment, baseline SHA-256, requested BUs/categories and optional account numbers | Core REST GET standardLookups/EXM_EXPENSE_TYPE_CATEGORY/child/lookupCodes, finBusinessUnitsLOV and optional ledgersLOV; see destination-reference-contract.md | LookupCode, Meaning, enabled/effective dates; BusinessUnitId, BusinessUnitName, ActiveFlag, PrimaryLedgerId; LedgerId, Name | Complete fresh result sets; exact unique BU and ledger matches; exact active category code or unique Meaning | Category code; automatically derived LedgerName; account_number maps to Segment1 | Stop on failed/unverified evidence, zero or multiple exact matches; never constrain values to baseline usage |
| export_preservation_baseline | Local intake is complete and preparation preflight passed | Exact environment; TaskCode EXM_MANAGE_EXPENSE_REPORT_TEMPLATES; per-template business units and worksheet identities | shared.setup-export.task-level-export delegates POST setupTaskCSVExports, GET the same ProcessId and its FileContent enclosure | ProcessId; completion/result status; FileContent; retrieval time | Classify a unique existing template/type/mapping identity as update; classify an absent identity as create; stop on multiple matches; verify supported headers/references; preserve unrelated rows | ProcessId; timestamp; ZIP SHA-256; CSV inventory/hashes; identities; schema; derived-operation evidence; preservation evidence | Stop preparation, disclose failed assertion and correct identity or missing reference; never build against an ambiguous target |

## Lookup Execution Rules

Use the shared exporter for export mechanics and the shared REST client for
the reference GETs declared above, with core-managed authentication. Export
does not import or mutate expense configuration. The workflow selects it as
preparation; no separate contract or candidate-build approval is needed.

Retain ProcessId and check the same process. A completed export with retrievable
FileContent is usable after validation. A completion flag without the artifact
is an unresolved retrieval, not grounds to submit another export. Preserve
errors/logs for COMPLETED_ERRORS. After a verified export, automatically
validate live schema and build the candidate/review. A new baseline or design
invalidates previous candidate and import approval.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMERT.EXPORT_BASELINE | step | 8 | reference_lookup | verified->EXMERT.PREPARE_CANDIDATE;invalid->EXMERT.NEEDS_CORRECTION;failed->EXMERT.BLOCKED | EXMERT.RESOLVE_DEPENDENCIES | stop | Preparation selected the shared task export and preflight passed; verify identities, task schema and preserved values |
