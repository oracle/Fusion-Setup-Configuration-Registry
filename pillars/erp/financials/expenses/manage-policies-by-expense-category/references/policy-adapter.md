# Standard offline Policies protocol

The task-specific adapter implements the standard manifest, normalize, build,
validate, determinism and reconcile commands through `scripts/fsm_task_adapter.py`.
It delegates candidate construction to the ordinary workbook builder and final
checking to the ordinary five task resource checks. It does not maintain a
second set of attendee, yearly-limit, currency or preservation rules.

The design input contains `resolvedScope.policyPreparation`, with exactly these
inputs: `workbook`, `runtime_contract`, `project_root`, `environment`,
`baseline_process_id`, `baseline_receipt`, `baseline_export_plan`,
`baseline_export_approval`, `currency_receipt`, `target_origin`, and
`validation_date`. File paths are absolute run inputs; no environment-specific
path belongs in this skill. The runtime contract must have the exact bytes of
the task-owned `references/fsm-runtime-contract.json`. Currency evidence may be
null only when the ordinary reference gate permits that operation without it.

Optional file inputs are `lookup_receipts`, `field_acceptances`, and
`reverse_update_of`. The last binds an explicit reverse workbook to the original
forward artifacts; see [reverse validation](reverse-update-validation.md).
It proves restoration locally and never authorizes cleanup or automatic rollback.
The field acceptance file
records the implementor's exact decision on a previously displayed eligible
field-uncertainty plan; see [the decision contract](field-uncertainty-validation.md).
It is included in immutable input bindings. Normalize preserves accepted exact
field overrides and warnings; validation/build/determinism recheck the same plan.
No unsupported operation, key/audit value or missing lookup evidence can use it.

The lookup receipt index is keyed by entity, exact policy name, operation and
field. A field may retain its legacy single absolute receipt path. When rates
under one policy consume different codes, it may instead contain a literal
code-to-absolute-path map. Each row selects only its exact code and independently
verifies the receipt's field, policy, operation, target and complete lookup
context. There is no fallback to a different code, default or wildcard selection.
Capture each lookup through the declared reference workflow into its immutable
output directory before assembling the index; never fabricate lookup values.
The entire index and every referenced receipt, including unconsumed code entries,
are bound in preparation and historical verification. A changed map or receipt
requires fresh preparation/review under the existing workflow.

Normalize re-runs ordinary validation and derives the immutable blueprint from
the workbook's actual changes. Supplied operations, when present, must match
that derived design exactly. It binds the workbook, baseline, contract and
evidence hashes. Build, validation and determinism recheck these bindings and
current-day policy validations. Changes require normalization and review again. Plain text
prerequisite claims cannot replace the ordinary reference receipts.

All 19 entities and 634 ordered columns remain in the package schema. Only the
sixteen policy/rate entities can be authored within their reviewed profiles.
Per Diem value rows participate only as bound dependent task effects in the
ordinary workflow, not as independent create targets. Exact identities come
from the existing reviewed runtime contract, including all rate key components.
The task-specific workbook parser and encoder govern optional typed determinant
components; the generic nullable-string/date helper is not the policy admission
path. Determinants remain outside the initial input scope.

The two determinant entities are preservation-only. Reconciliation compares complete non-audit
row multisets, preserving duplicate counts and detecting removal or alteration,
without inventing row IDs or portable business keys. Concurrent unrelated inserts
are allowed. Requested targets must resolve once; all requested values and other
non-audit target fields are checked. Declared calendar dates use the existing
strict date parser. Structural or undeclared metadata differences remain blockers.
The explicit source-reviewed export-local policy validates positive sequence
numbers and task-scoped XML file/level collisions, retaining raw verification
differences. Submission metadata stays byte-identical to the bound baseline.

Historical reconciliation accepts `--historical-proof` only on the read-only
reconcile command. Its `fscr-policy-historical-verification-v1` JSON contains
`sourceSnapshot` and an `artifacts` map with exact absolute path/SHA256 references
for baseline, template, candidate, blueprint, requirements, original PASS
validation report and native approved preview (`nativeApproval`). The archived
`taskSources` and `areaSources` directories must match the original blueprint's
complete source inventory. Every original input, candidate/design/requirement
binding, native preview and preparation/approval chronology is checked. Captured
currency pages are reclassified as of the original bound preparation date.
The preparation timestamp comes from the original native preview, never a caller
clock override. Candidate preparation, authentication and reference recapture
are not performed. The report binds both original and current verifier source
inventories and grants no import authority. Native process success, export
custody and any changed-verifier qualification remain independently governed.

Automatic rollback and deletion are unavailable. A reverse change needs its own
workbook, current baseline, operation-bound reference evidence and normal approval.
The rollback command refuses before writing an artifact. Candidate preparation,
offline tests and reconciliation do not confer import approval or establish a
new persisted-state qualification. Existing Run Book, Task Hook and Data Loader
workflows retain ownership of all live execution and candidate-specific approval.
