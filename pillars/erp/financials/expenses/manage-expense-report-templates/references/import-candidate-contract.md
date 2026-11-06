# Import Candidate Contract

Use this contract after complete intake passes validation. Preparation, baseline
verification and candidate construction proceed automatically. Candidate
construction is local and never authorizes import; obtain approval after CSV
review of the exact immutable ZIP.

## Normalized Design

Persist the validated workbook or chat intake as JSON before contracts are
produced. Bind it to the later baseline by adding `baseline_process_id` and the
exact `baseline_sha256` after the export succeeds. The candidate builder accepts
this shape:

Pass `--reference-evidence` with the core-captured destination category/BU/ledger
results described in `destination-reference-contract.md`. When provided,
`account_number` is an optional string on an expense type; omit it for an
unchanged Edit account. The implementor supplies no ledger name.

```json
{
  "schema_version": "1.5",
  "environment": "https://example.fa.example.com",
  "task_code": "EXM_MANAGE_EXPENSE_REPORT_TEMPLATES",
  "baseline_process_id": "123456789",
  "baseline_sha256": "64-character-lowercase-sha256",
  "templates": [
    {
      "business_unit": "Example Operations",
      "name": "Example Employee Expenses",
      "description": "Synthetic example cash expense template.",
      "start_date": "2026-01-01",
      "inactive_date": null,
      "default_template_intent": "No",
      "receipt_rules": {
        "cash_receipt_required": "No",
        "cash_receipt_threshold": null,
        "negative_line_receipt_required": "No",
        "allow_missing_receipt": "No",
        "receipt_warning": "Yes"
      },
      "field_behaviors": {
        "description": "Optional",
        "expense_location": "Optional",
        "merchant_name": "Optional",
        "number_of_days": "Hidden"
      },
      "expense_types": [
        {
          "name": "Meals",
          "description": "Synthetic example cash meal expense.",
          "start_date": "2026-01-01",
          "end_date": null,
          "category_value": "Meals",
          "category_code": "MEALS",
          "itemization": "Disabled",
          "prepaid": "No",
          "receipt_rules": {
            "cash_receipt_required": "Yes",
            "cash_receipt_threshold": 25,
            "negative_line_receipt_required": "No",
            "receipt_warning": "Yes"
          },
          "field_behaviors": {
            "description": "Optional",
            "expense_location": "Optional",
            "merchant_name": "Optional",
            "number_of_days": "Optional"
          }
        }
      ]
    }
  ]
}
```

For v1.5, persist a nonempty `templates` array. The workbook-derived design
must not contain an `operation` property. Every template owns its own
`business_unit` and `expense_types` array; every entry shares the top-level
target environment. Business units may differ between templates. The builder
derives operations from the exact fresh baseline: Business Unit + Template Name
for a template, and Business Unit + Template Name + Expense Type Name for a
type. A unique target match is an update and no match is a create. Stop on
multiple matches. Every candidate batch must contain one resolved template
operation class—create or edit—not a mixture. Do not submit the same
case-insensitive template name twice for the same business unit in one design.
For a target-resolved create, persist every field shown above even when its
approved value is null. Flatten the intake target so environment is a top-level
key. Normalize legacy display names as follows: template expense_fields to
template field_behaviors, and expense-type field_overrides to field_behaviors.
Normalize the V3 display model using references/workbook-intake.md. Tax
Classification Code and Tax Product Category are not fields in the v1.5 display
or execution model.
Do not pass a task-local seed-reference row or a document row directly to the builder. A source may contribute only validated, mapped, and supplemented business
values. Keep source locations and issue records in separate intake state. An
policy, relationship removal,
corporate-card change or guessed category code is a blocking issue, not a field
to silently omit. The builder rejects unknown design keys.

For a target-resolved update, include only fields the implementor approved
changing. Blank worksheet cells are omitted before building; the field-behavior
dropdown value `Blank` is normalized to the same omitted value. Permitted
`Clear` values become null only after the target confirms the identity exists.
For a target-resolved create, a selected field-behavior `Blank` is therefore
still missing and cannot satisfy the new-record requirement. Renames and removals are
blocked because related mapping-row behavior is not established by this
contract. The builder continues to accept legacy v1.0–v1.4 shapes, but all new
workbook and chat intake must produce v1.5.

For v1.5, provide an explicitly resolved `category_code` whenever a category
label is supplied. Resolve it using verified target evidence, not seed hints.
The builder does not infer a v1.5 code from a label.
Legacy v1.0/v1.1 behavior remains available for old designs. Persist explicit
start dates for created types; do not inherit the parent date silently.

Itemization uses Disabled, Enabled, Required (legacy Optional/Not required
labels are also accepted). Newly enabled itemization needs included child types.
Supply the top-level `itemizations` array as described in `child-mappings.md`.
The builder derives each mapping operation from the complete relationship
identity, applies additions after parent/type rows, and preserves unrelated
itemization mappings. Optional `account_number` is the account value as text,
mapped to Segment1; LedgerName is derived from the BU primary ledger using
destination REST evidence. Omitted accounts preserve existing values on edits.
It writes tax values as null and Projects as disabled; do not supply direct
ledger/segment, tax, project-control, default-expenditure, or
project-mapping fields in a v1.5 design.

For both template and expense-type receipt rules, `cash_receipt_threshold` is
required whenever `cash_receipt_required` is `Yes`.

For a target-resolved update, omit unchanged values. Convert explicit nullable Clear to null and
validate the resulting baseline-overlaid row. Setting cash receipts to Yes
does not require re-entry of an existing valid threshold. For Create, optional
blank fields may be normalized to null; the builder serializes them as empty
CSV values without supplying seeds. Created start dates remain required.
`itemization_only` accepts Yes/No and maps to the verified ItemizationOnlyFlag.
Cash-only v1.5 updates reject selected records with active card settings rather
than disabling them. Legacy designs retain their original compatibility rules.

## Build Command

Create new versioned output paths; the builder refuses to overwrite either
artifact.

```bash
python3 pillars/erp/financials/expenses/manage-expense-report-templates/scripts/build_import_candidate.py \
  --baseline-zip <fresh-export.zip> \
  --design-json <normalized-design.json> \
  --output-zip <candidate.zip> \
  --preview-output <candidate-build-preview.json>
```

The builder verifies the baseline checksum and required members, preserves the
archive inventory, leaves every unrelated ZIP member byte-identical, validates
the task CSV headers and every template/type identity, applies cash-only create
defaults, and writes per-template row hashes plus field-level before/after
values into the preview. Its preview is candidate-build evidence, not the Core
Data Loader approval record.

## Data Loader and Import Handoff

First read `core/data-loader/SKILL.md` and its `references/fusion-zip-rest.md`.
Preserve the selected task context; do not reselect a task or call Run Book REST
APIs. This task's generated `dataloader_import_mode` is `FSM`; its native ZIP
contains `ASM_SETUP_CSV_METADATA.xml`. Do not treat its CSVs as DAT inputs or
send the intake/review workbook to generic XLSX conversion.

After candidate construction, run Data Loader's read-only preflight:

```bash
python3 core/data-loader/scripts/upload_and_initiate.py <candidate.zip> \
  --task-routed \
  --preflight-envelope-output <internal-preflight.json>
```

This invocation must not include `--approve-upload`. Retain its preflight and
final immutable archive; do not show approval feedback yet. Let Data Loader
parse/verify its envelope. Require `taskRouted: true`, `mappingComplete: true`,
and `archiveSha256` matching the retained artifact before invoking Task Hook:

```bash
python3 core/data-loader/task-hook/scripts/task_hook.py data-load \
  --task-context <selected-task-context.json> \
  --task-name "Manage Expense Report Templates" \
  --sequence <selected-positive-sequence>
```

Follow the returned execution guide and evaluate read-only rules against the
candidate and retained intake/baseline evidence. `ready` means the plan is
executable, not that validation passed. Do not repeat intake, export or build
inside Task Hook. Build the preview using `build-data-load-preview --input-stdin`
with `taskContextPath`, `taskName`, `sequence`, `finalData.archiveSha256`, and
ordered evaluated `ruleResults`. Retain the returned preview unchanged.
Validation failures block approval feedback. Record execution gates as pending
external approval, not failed business validation and not permission to submit.

Extract every CSV from that final artifact and create its review workbook:

```bash
python3 pillars/erp/financials/expenses/manage-expense-report-templates/scripts/prepare_csv_review.py \
  --candidate-zip <candidate.zip> \
  --output-dir <new-review-directory>
node intake_workbook.mjs review \
  --input <new-review-directory>/csv-review.json \
  --output <csv-review.xlsx>
```

Use the bundled spreadsheet runtime as described in the V3 workbook intake
reference. Link the exact CSV files, ZIP and review workbook. An implementor's
review edits return to normalized intake; never round-trip the review workbook
into the import ZIP. Regenerate all review evidence after a candidate change.

Present the review links, business delta, target, requested operations and
protected scope before the loader's unchanged approval-required Markdown.
Keep internal preview/envelope paths and hashes out of user-facing reports.
Accept a clear contextual affirmative for the exact reviewed package; do not
require a fixed keyword or separate contract/build approval. Explicit
same-request auto-approval follows the core loader policy and never skips
validation or authorizes a later load.

After that approval, use Task Hook
`approve-data-load-preview` and `verify-approved-data-load-archive`. Persist the
returned `taskValidationEnvelope` object unchanged and pass it with the retained
Data Loader preflight to the authoritative loader:

```bash
python3 core/data-loader/scripts/upload_and_initiate.py \
  --approved-preflight-envelope <internal-preflight.json> \
  --task-validation-envelope <approved-envelope.json> \
  --approve-upload
```

Do not add a positional source, `--task-routed`, or other source/mapping/routing
arguments to this approved invocation; the CLI rejects them. Use the same
OAuth-properties and Run Book configuration context as preflight if explicit
overrides were selected. The loader verifies the saved archive, environment,
Run Book binding and task envelope without revalidating the original source.
Missing/changed artifacts or mismatched context require fresh validation and
approval. Do not fabricate envelopes, alter the approved artifact, directly
invoke the shared importer, or substitute another endpoint.

Return the accepted initiation report unchanged and stop without polling.
For a later explicit status/results request:

```bash
python3 core/data-loader/scripts/get_data_load_info.py <request-id-or-ucm-content-id>
```

Use `--status-only` for a status-only question. Never use the baseline export
ProcessId as the loader Request ID. Preserve partial successes and reconcile
errors before preparing a corrected package for new approval.
