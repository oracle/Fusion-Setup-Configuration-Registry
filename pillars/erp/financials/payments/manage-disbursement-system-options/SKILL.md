---
skill_id: "erp.financials.payments.manage-disbursement-system-options"
name: "Manage Disbursement System Options Setup Task Guidance"
description: "Provides task-specific setup guidance for Manage Disbursement System Options under the Payments functional area."
layer: "pillar"
pillar: "ERP"
offering: "Financials"
functional_area: "Payments"
functional_area_code: "ORA_FIN_PAYMENTS"
task_code: "IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS"
task_name: "Manage Disbursement System Options"
parent_skill_id: "erp.financials.payments"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "setup_task_scope"
  - "setup_data_artifacts"
outputs:
  - "setup_task_plan"
  - "setup_data_routing"
  - "validation_checkpoints"
  - "skill_run_record"
  - "token_usage_record"
depends_on:
  - "shared.setup-export.task-level-export"
  - "shared.validation.setup-data-validator"
  - "shared.validation.reference-data-validator"
  - "core.data-loader"
uses_core:
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "setup_task_sequence"
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-disbursement-system-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-disbursement-system-options/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects: []
required_privileges: []
---

# Manage Disbursement System Options Setup Task Guidance

## Purpose

Provides task-specific setup planning, routing, export, import, and validation guidance for `Manage Disbursement System Options` under `Payments`.

## Setup Task Skill Contract

- task_code: `IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS`
- task_name: `Manage Disbursement System Options`
- parent_skill_id: `erp.financials.payments`
- pillar: `ERP`
- offering: `Financials`
- functional_area: `Payments`
- functional_area_code: `ORA_FIN_PAYMENTS`
- available_flag: `Y`
- export_import_supported_flag: `Y`
- csv_export_import_supported_flag: `Y`
- dataloader_import_mode: `FSM`
- businessObject: ``
- source_catalog: `knowledge/setup-task-catalog/effective/setupTasksAll.json`

## Usage

Use this skill when planning, sequencing, exporting, importing, or validating setup data for `Manage Disbursement System Options` under `Payments`.

## Setup Task Metadata

- Task name: `Manage Disbursement System Options`
- Task code: `IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export setup task data with `shared.setup-export.task-level-export`.
2. Validate setup task data with `shared.validation.setup-data-validator`.
3. Validate reference data with `shared.validation.reference-data-validator`.
4. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Financials`
- Functional area / Setup Object: `Payments`
- Setup task name: `Manage Disbursement System Options`
- Setup task code: `IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS`




## Inputs

- `implementation_objective`
- `project_context`
- `setup_task_scope`
- `setup_data_artifacts`

## Outputs

- `setup_task_plan`
- `setup_data_routing`
- `validation_checkpoints`
- `skill_run_record`
- `token_usage_record`

## Implementation Notes

Use the parent functional-area skill `erp.financials.payments` for functional-area sequencing and scope decisions. Track token usage for any generated project artifact or skill-run record using the manifest policy.

## Task-specific execution discipline



Read the six resources in this order: [input validation](ora-resource/ora_input_validation.md), [dependency readiness](ora-resource/ora_dependency_readiness.md), [reference lookups](ora-resource/ora_reference_lookups.md), [defaulting](ora-resource/ora_defaulting_rules.md), [design enforcement](ora-resource/ora_design_enforcement.md), and [error handling](ora-resource/ora_error_handling.md). Load the exact-task [compiled registry](ora-resource/ora_rule_registry.json), build its current plan, and inspect every reached source anchor. The [task contract](references/task-contract.json) records all 23 fields and unresolved operation boundaries; [evidence](references/evidence.md) distinguishes source claims from observed behavior.

The enterprise row has blank BuName. Explicit enterprise scope must select exactly one such row in a fresh exact-task export. Explicit business_unit scope uses the exact named BuName. Missing scope is a clarification, never enterprise by default. Do not synthesize a BU name, use audit fields as keys, rename a target, or turn an unknown BU into the enterprise row. CSV scope differs from the service-owned database primary identifier.

Keep create and update in intended business scope. Existing-row update is source-backed. Terminal processing and fresh-export reconciliation qualify only the observed enterprise AutomaticPprReportSubmit Y -> N -> Y and SraEmailSubject enterprise/two named-BU update/restoration contexts described in references/evidence.md and the task contract. Other field/value/scope contexts remain unresolved; these observations are not reusable mutation authority. For an unresolved field operation or lookup, identify the exact gap and expected application-validation boundary. Obtain an explicit field/candidate-specific decision to rely on application validation before progressing; preserve the warning and every other deterministic check. This decision cannot waive identity, protected fields, package integrity, proven-invalid input or normal mutation approval. Controlled terminal processing plus later supported55-row export qualify only the retained Vision ANZ BU / Vision APAC BU explicit-N create contexts in the task contract. Other create inputs, eligibility, defaults and serialization contexts remain unresolved. Preserve original m01/c01 failures and obtain current evidence rather than inventing defaults. No task CSV delete/end-date mechanism is established. Row omission never means deletion. Do not offer automatic cleanup without a proved reverse operation.

Use [the task-owned helper](scripts/disbursement_options.py) for separately authorized baseline inspection, atomic existing-row design review and exact fresh-export reconciliation. Its reader accepts the same-task two-member export and explicit target environment/release. It verifies 23 ordered CSV columns, metadata field types, unique identities and the enterprise singleton. The reader's 64 MiB memory bound is a local processing guard, not a Fusion business-volume limit. It creates no package, authenticates nowhere and cannot submit a load. Do not label a reviewed design or comparison result as import success.

For an update, preserve all unrequested business values, technical values and unrelated rows. Preserve blank PaymentsApprovalFlag when unrequested; it is not silently N. Only the three last-update audit fields may change on requested rows as reported service-owned deltas. Creation audit changes and unrelated-row changes fail reconciliation. No baseline values are create defaults. AutomaticPprReportSubmit=Y requires a nonblank valid PprReportFormat in the resulting design. Format display names must resolve to actual target format codes; do not serialize a display label as a code.

## Source-Backed Task Behavior

- One controlled27A absent-BU create persisted blank PaymentsApprovalFlag as N while all other requested business values and all pre-existing cells matched. Clarify the intended persisted value before proposing blank as an exact outcome. Never silently coerce blank to N, weaken reconciliation or apply this observation to existing-row updates/other contexts. Source: SRC-E2E-CREATE-C01-164773.

- Explicit enterprise scope selects the unique blank-BuName row; explicit BU scope selects one exact named row. Missing or ambiguous scope requires clarification. Sources: SRC-GOLD-VO-SNIPPETS, SRC-GOLD-EO-SNIPPETS, SRC-GOLD-SETUP-SEED, SRC-USER-ROUNDTRIP-153565.
- Preserve all unrequested business/context values and unrelated rows. Preserve blank PaymentsApprovalFlag rather than defaulting it to N. Report permitted last-update audit changes only on requested rows; do not excuse creation-audit or unrelated-row changes. Sources: SRC-GOLD-VO-SNIPPETS, SRC-GOLD-EO-SNIPPETS, SRC-USER-ROUNDTRIP-153565.
- Business update analysis covers PaymentMethodAtPayeeFlag, DocumentRejectionLevelCode, PaymentRejectionLevelCode, RequirePropPmtsReviewFlag, AllowExtAcctOverrideFlag, ExclusivePaymentFlag, SavePaymentFileInDb, BankChargeBearer, PprReportFormat, AutomaticPprReportSubmit, PaymentsApprovalFlag, SraEmailSubject and SraSendFrom. Source UI bindings identify these business options. Observed update/restoration qualification is limited to enterprise AutomaticPprReportSubmit Y -> N -> Y with PPR_STATUS_REPORT preserved and SraEmailSubject enterprise plus FGST-Auto Ltd / FGST-Service Ltd in the recorded values; all other contexts remain unresolved. Sources: SRC-GOLD-UI-FULL, SRC-GOLD-VO-SNIPPETS, SRC-GOLD-EO-SNIPPETS, SRC-E2E-OBSERVED-AUTOPPR-164493-164510, SRC-E2E-OBSERVED-SUBJECT-164559-164580.
- BuName is immutable CSV identity; five audit columns and BusinessUnitId1/ModuleId/ModuleKey are service-owned rather than business overrides. OrgType has unresolved context/mutability and is preserved pending evidence, not declared unsupported by Fusion. Sources: SRC-GOLD-SETUP-SEED, SRC-GOLD-VO-SNIPPETS, SRC-GOLD-EO-SNIPPETS.
- Apply corroborated requiredness and precision without converting VO hints or sample exports into universal user-input requirements. Seven flag/basis fields have precision1, four code fields precision30, and the two SRA fields precision1024. The complete field contract distinguishes source-requiredness, context and open operation evidence. Source: SRC-GOLD-EO-SNIPPETS.
- AutomaticPprReportSubmit=Y requires a valid nonblank PprReportFormat in the resulting configuration. Resolve the actual target format code; a display label alone is insufficient. Sources: SRC-GOLD-EOIMPL, SRC-GOLD-EO-SNIPPETS.
- No scalar task-owned create default is established. Unchanged exported values are preservation evidence, not create defaults. Sources: SRC-GOLD-EO-SNIPPETS, SRC-USER-ROUNDTRIP-153565.
- Keep create and update in intended scope. New-row requiredness/defaults/eligibility/serialization, unobserved changed-field contexts, CSV physical deletion and end-date behavior require their own evidence. Generic CanDelete does not prove a task CSV delete mechanism; omission never means deletion. Sources: SRC-GOLD-AM-SNIPPETS, SRC-GOLD-AMDEF-SNIPPETS, SRC-GOLD-VO-SNIPPETS.
- Four lookup validators and the PPR-format validator are source-backed. Reviewed DEV seed codes/labels and EO filters are recorded for the four lookup fields; BankChargeBearer is extensible and its seed list is not exhaustive. Deployed contents/revision and current format-code population remain unverified. Source label pairs do not implement automatic runtime normalization. Missing evidence is distinct from invalid data. A bounded eligible application-validation decision cannot waive proven-invalid constraints, package integrity, protected fields, identity or mutation approval. Sources: SRC-GOLD-EO-SNIPPETS, SRC-GOLD-EOIMPL, SRC-DEV-LOOKUP-SEEDS-20260924, SRC-DEV-INTERNAL-PAYER-EO-LOOKUPS, SRC-DEV-INTERNAL-PAYER-EOIMPL-PPR.
- The public BU LOV can corroborate exact visible BU existence; it does not establish new option-row eligibility or all import-helper failure semantics. Import owns Name plus EnterpriseId to OrgId resolution. Sources: SRC-REST-FIN-BU-26C, SRC-GOLD-AM-SNIPPETS, SRC-GOLD-BU-PVO, SRC-GOLD-BU-PEO.
- Bulk requests require atomic preflight, unique intended operations and a complete design. A failed or unknown mutation is never automatically resubmitted. Current Run Book/Data Loader own preview, approval, submission and retained-session policy; export comparison alone does not determine import outcome. Sources: active core.data-loader and task-owned error/design resources.
- Restoration requires an independently supported reverse design and a fresh approval. No cleanup by physical deletion is promised while that task CSV contract is unproved. Sources: SRC-GOLD-AM-SNIPPETS, SRC-GOLD-AMDEF-SNIPPETS and task-owned error/design resources.

- Controlled retained create evidence is limited to the exact Vision ANZ BU / Vision APAC BU explicit-N input contexts: terminal success and later supported55-row export matched all requested values and preserved1219pre-existing cells. Original m01 missing-identity and c01 blank-to-N comparisons remain FAIL; later retention/verification are separate outcomes. No universal default, automatic prerequisite repair, retry, deletion or cleanup-to-absence is established. Source: SRC-E2E-RETAINED-CREATE-55ROW-164877.

## Offline update preparation interfaces

### Explicit create and mixed preparation

`review_operations` adds absent-BU create and mixed create/update preparation.
It requires all 13 business values explicitly (including intentional blanks),
source-backed BU context, a current exact active/task-eligible reference and
bounded field-specific application-validation decisions. It never performs an
upsert, copies historical rows as defaults or accepts service-owned overrides.
The seven corroborated entity-required fields remain required. The automatic
report flag is not declared non-null in the reviewed EO or import VO; its
Y/format conditional rule still applies. The payment-approval hint discrepancy
remains context-specific: blank-to-N c01 is an original FAIL with later accepted retained N, not a default. The exact retained explicit-N ANZ/APAC creates have later supported export verification; unobserved new-row serialization/persistence contexts remain gaps.

Keep historical audit/BU metadata in source evidence only. Present proposed
blank service-owned serialization and expected service assignments in the full
design before confirmation. Reconcile the new identity and all requested values
while preserving every pre-existing row. Created rows have no before-values:
do not claim a reverse update can remove them. Obtain explicit retention intent
unless a separately proved cleanup contract is available. Preparation and UI
eligibility are not a successful Fusion import.

`scripts/disbursement_options.py` exposes `read_export`, `review_updates`,
`build_candidate`, `validate_candidate`, `determinism`, `reverse_review` and
`reconcile` as a task-owned Python library. Its inspection CLI is unchanged.
Candidate preparation accepts the exact baseline ZIP bytes and a separately
confirmed existing-row update design. It preserves metadata bytes, member
order, ordered headers, explicit trailing blanks, unrequested values and all
unrelated rows. Repeated preparation is byte deterministic within the pinned
runtime. A local memory bound is not a Fusion volume limit.

Prepare the native FSM source offline, before starting Core; never use the
helper to rewrite a pending session's captured input. Core then retains that
source unchanged and owns preview, approval, upload and submission. Offline
candidate filenames/hashes required for human review do not replace Core's
private in-memory bindings. Do not persist Core captured records, preview IDs,
execution-plan hashes, approval state or replay material.

Independent validation recomputes the atomic design against its baseline and
compares every candidate value. Reversal verifies the original design's
before-values and a fresh post-forward export, permits only disclosed service
audit deltas, and creates a new narrow design. It requires new exact-field
reliance decisions, business confirmation and candidate approval. None of these
functions authenticates, submits, grants approval or qualifies product behavior.
Unobserved create contexts, lifecycle, unobserved field/value/scope contexts and product volume limits
retain their evidence-specific qualification requirements. The two observed update
contracts do not waive exact-field runtime decisions, design confirmation, fresh
baselines, independent reverse approval or current Core execution gates.

## Governed workflow

1. Capture the user's intended operation, explicit enterprise/BU scope and requested values from text, spreadsheet, PDF or narrative. Ask bounded questions for missing or ambiguous facts. Show the full normalized design; obtain business-design confirmation. Reject protected-field overrides and conflicting operations atomically across the complete request.
2. Obtain a fresh exact-task baseline and validate target/release/package identity. Verify prerequisites and any newly requested lookup/format values from authoritative target evidence. Explain and resolve every material uncertainty before producing a candidate. A request to create a duplicate, update an absent target or perform a no-op needs a new business decision, not an implicit upsert.
3. Route through the active Run Book and core.data-loader. Read their current SKILL and session protocol at execution time. During an interactive session use only its captured records for task rules; never reopen sources, mutate retained records or persist source hashes, structured records, preview/approval envelopes or recovery state. If corrected data is needed, cancel and start a fresh session. The helper's proposed rows are design analysis, not permission to replace captured records.
4. Keep the exact process handle connected across confirmation. Obtain the active core's immutable preview and candidate-specific human approval. Submit once through that core. Changed input, lost handle, expiry, rejection or uncertain outcome requires reconciliation and a fresh approved attempt, never replay. The current core's memory/retention and preview contract governs the live handoff.
5. Require terminal import success with zero failed rows and no unresolved warnings. Obtain a fresh exact-task export; reconcile every requested value, unrequested value and unrelated identity. Show any permitted service-owned audit changes separately. A successful upload, initiation, UI view or export comparison alone is not a successful import. Restore only through an independently confirmed reverse design and fresh candidate approval; otherwise disclose retained changes.

Preserve all applicable human review and current execution-host gates. A source gap or local processing bound must not be reported as an unsupported Fusion product operation or a business-volume limit.

## Named-row export visibility and safe existence checks

Source: SRC-GOLD-VO-SNIPPETS, InternalPayerVO join/filter lines46–49; SRC-E2E-M01-EXPORT-VISIBILITY-164877. A named internal-payer row appears in this task export only when its BU joins to a PAYABLES_PAYMENT_BF usage record. A valid import can create an underlying row while this usage is absent. Payables Payment is necessary for this export visibility; it is not established as mandatory for physical insertion.

An omitted exported identity is not proof of physical absence. Before proposing an absent-BU create, consider this filter and obtain source-qualified current task selection/existence evidence. An active public BU match or selectable create target does not by itself prove export visibility. If existence or the verification route remains uncertain, ask a bounded question and do not retry create blindly.

When usage is missing, explain the visibility limitation and ask whether the implementor intends the prerequisite business setup or will retain an explicit verification limitation. Route an intended assignment through Assign Business Unit Business Function and its supported workflow. Never choose a ledger/legal entity, enable a business function automatically, or write derived usage values into this task CSV to manufacture visibility.

Preserve the exact failed comparison even when terminal processing succeeds. After a separately approved prerequisite repair, obtain a fresh exact-task export and reconcile without reimporting known existing rows. Developer-only SQL may explain a discovery; it is neither an implementor prerequisite nor an alternate supported runtime reconciler. Do not claim completion from SQL or weaken the existing all-cell comparison.
