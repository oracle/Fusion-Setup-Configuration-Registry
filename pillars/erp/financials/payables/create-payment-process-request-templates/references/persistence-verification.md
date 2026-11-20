# Verify saved payment process request templates

Use this procedure when the active project workflow selects post-import
verification for `ORA_AP_MANAGE_PAYMENT_PROCESS_REQUEST_TEMPLATE`. It composes
existing Core status retrieval, Shared task-data export and the PPR adapter's
local comparison. The workflow performs the evidence checks and records the
final verification result; the adapter does not acquire live evidence or
automatically certify persistence.

Internal framework source and dependency labels are supporting evidence, not a
blanket prerequisite for ordinary create/update preparation. Apply the task's
known field, identity, preservation and approval rules. A material unknown
mapping or child operation remains scoped to that action; this procedure does
not infer deletion from omission, enable an unsupported child replacement, or
waive a protected field rule. Source review or a governed task-specific test may
establish additional behavior for its recorded scope.

## Acquire evidence through the owning workflows

1. Retain the baseline export, requested design, requirement matrix, validated
   candidate ZIP, candidate SHA-256, Task Hook result, Core preflight and
   initiation result for the same task and target. Use the submitted immutable
   ZIP, not a rebuilt candidate. Baseline and comparison scope must include the
   affected template and all five selection collections.
2. Follow [Core Data Loader](../../../../../../core/data-loader/SKILL.md) for
   import execution and status. Initiation alone is not completion. For a
   separately selected verification/status step, retrieve the matching data set
   and `dataSetErrors`, even when the top-level status reports success. Bind
   `RequestId`, `UcmContentId`, `FsmTaskCode` and `FsmMigRequestId` to the retained
   initiation. Inspect returned total/loaded/failed counts, object errors, row
   errors and relevant ProcessLog diagnostics. Missing counts or diagnostics
   must not be replaced with invented zeroes. Resolve warnings that affect
   coverage or saved values before verification.
3. After successful processing is established, use
   [Shared Task Level Export](../../../../../../shared/setup-export/task-level-export/SKILL.md)
   for a new populated data export of this exact task. Select its data mode,
   not template/spec mode, under the active workflow's authorization. Record
   the export process identity, request scope, observed status and actual
   `FileContent` download. Preserve the downloaded bytes under the current
   project's `exports/` directory; keep run diagnostics under its artifacts or
   state directory. Use the shared exporter for polling, download and logs.
4. Prefer an unfiltered exact-task export for full-snapshot preservation checks.
   A scoped export is sufficient only for assertions whose complete row
   population it demonstrably includes. It cannot prove preservation of
   excluded templates or missing child collections. Match baseline, candidate
   and readback coverage before comparing them.
5. Run the task adapter's existing `reconcile` command with the baseline,
   submitted candidate, confirmed blueprint, requirements and new export.
   Retain its complete requirement matrix and mismatches. A matching result
   remains `COMPARISON_ONLY`, `comparisonStatus: PASS` and
   `persistenceVerified: false` in that adapter report.
6. Evaluate the acquisition and comparison checks below together, then write a
   separate workflow verification record. Do not modify the adapter report to
   make it claim live verification. Link the workflow record, source evidence
   and comparison report in the project artifact register and run record.

This procedure does not add automatic monitoring to a Data Loader initiation
request. Status retrieval and a new data export must be selected by the active
workflow. Export and import authorization are separate operations; neither is
implied by a local candidate or comparison result.

## Acceptance checks

- The task, target environment identity and base URL match the approved load,
  Core status observation and Shared export. Use actual configured identity;
  never infer an environment match from a template name or ZIP filename.
- Baseline, submitted candidate and downloaded export SHA-256 values are
  calculated from their actual files. The readback has a distinct acquisition
  and export process; a candidate, baseline, copied archive or edited CSV is
  not readback evidence. Preserve the adapter's checks against reused paths,
  archive bytes and export process metadata.
- The successful import observation belongs to the retained request, content
  ID and FSM process. The new data export starts after that successful import
  observation and completes before its download is recorded. Retain timezone-
  qualified observation times and the corresponding workflow outputs; do not
  substitute file modification times or invent a server completion time.
- Export status and enclosure prove a successful, complete task-data download.
  Record and assess warnings rather than treating a completed process as
  sufficient by itself. Interrupted, failed or incomplete exports do not
  satisfy this check.
- Requested values match, expected source-backed effects match, and no
  unrequested business values or rows differ within the declared comparison
  scope. Preserve raw differences. Only the adapter's existing field-specific
  canonicalization contracts may accept a semantic equivalence.
- The root and every child collection are covered, including empty sets and
  the group option that controls each collection. Match the root by
  `TemplateName`; match each child by the exact parent `TemplateName` plus the
  following portable key. Verify missing and unexpected membership, not only
  requested members that happen to be present.

| Collection | CSV entity | Additional portable key |
| --- | --- | --- |
| Business units | `ORA_PPR_BU_GROUP` | `Name` |
| Currencies | `ORA_PPR_CURRENCY_GROUP` | `CurrencyCode` |
| Legal entities | `ORA_PPR_LE_GROUP` | `LegalEntityIdentifier` |
| Pay groups | `ORA_PPR_PAY_GROUP` | `VendorPayGroupName` |
| Sources | `ORA_PPR_SOURCE_GROUP` | `InvoiceSourceName` |

The exact parent column in each child is
`ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES.TemplateName`. Check the complete root
and five-collection state before and after each operation. An unchanged child
set requested by a root-only update is an assertion to verify, not an assumed
ADF merge behavior. A test of one collection does not qualify another
collection automatically. Root `OrgId` business-context eligibility is a
separate question from technical `TemplateId` handling.

## Workflow verification record

The assisted workflow records the following JSON fields. This is a reporting
contract, not a new executable command or automatic receipt generator. Store
actual evidence references and omit unavailable optional identifiers rather
than filling them with example values.

| Field | Content |
| --- | --- |
| `schemaVersion` | `ppr.workflow-persistence-verification.v1` |
| `status` | `PENDING`, `VERIFIED`, `FAILED` or `UNKNOWN` |
| `persistenceVerified` | Boolean; true only for `VERIFIED` |
| `taskCode` | Exact PPR task code |
| `environment` | Target identity and base URL used by the owning workflows |
| `operationRefs` | Design, requirements, Task Hook, approval, Core preflight and initiation artifact references |
| `artifacts` | Baseline, submitted candidate, fresh export and comparison-report paths with their actual SHA-256 values |
| `importObservation` | Request ID, content ID, FSM process ID, observed terminal status, returned counts/errors/warnings, observation time and source output references |
| `exportObservation` | Task-data scope, export process ID, observed status, enclosure, start/download observation times and source output references |
| `acquisition` | Owning workflow and executor identity; how the actual status and download outputs were obtained; evidence references |
| `assertions` | Requested values, declared effects, preservation, root identity and each of the five collections, with expected/observed values and pass/fail |
| `scope` | Observed environment/build metadata, templates, operations and collection coverage; unavailable build metadata remains explicitly unrecorded |
| `errors` | Classified failures, mismatches or unresolved evidence conditions; empty only when none remain |
| `nextAction` | The appropriate completion, status-resume, evidence-acquisition or correction action |

`VERIFIED` requires every acceptance check, zero unresolved material diagnostics
and a matching requirement matrix. It establishes the recorded request and
observed scope, not a universal framework guarantee for all builds or later
imports. The acquisition record is attributed workflow evidence, not a signed
server attestation. A hand-written success flag or caller-supplied timestamp
cannot replace the actual Core/Shared outputs. Local or simulated fixtures must
be identified as such and cannot produce a live `VERIFIED` result.

## Incomplete or unsuccessful outcomes

| Status | Meaning and action |
| --- | --- |
| `PENDING` | Processing is known to be incomplete, readback is not yet acquired, or the workflow has not completed its checks. Preserve identifiers and resume only the owning status/download step when requested. |
| `FAILED` | A terminal failure, invalid evidence binding or an observed business/preservation mismatch prevents verification. Identify whether the failure is in processing, evidence or comparison; do not imply all changes were rolled back. |
| `UNKNOWN` | Submission outcome, acquisition provenance or coverage is materially uncertain, or partial persistence cannot be resolved from the available evidence. Reconcile live state through the owning workflow before any retry. |
| `VERIFIED` | Processing, acquisition and all requested/preservation assertions passed for the recorded scope. Report the saved result with its evidence references. |

On polling timeout, report task, target, process/request identity, last status
and elapsed wait. A timeout does not cancel the process or authorize another
submission. Follow the exporter or Data Loader status-only resume path; do not
create another import/export merely to resume polling. Preserve partial
successes and diagnostics. Reverse updates, restoration of removed selections
and cleanup require their own supported design, validation and existing
approval workflow. Never infer rollback or physical deletion from an omitted
row, an inactive date, a test cleanup request or helper flags.
