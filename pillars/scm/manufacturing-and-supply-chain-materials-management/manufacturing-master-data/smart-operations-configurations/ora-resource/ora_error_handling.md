# Smart Operations Configurations Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required task identity, current CSV support, artifact, lookup or delegated post-validation approval contract is unresolved | Identify the exact missing contract and stop before preview, import, registration or completion claim; an actual administrator approval record is obtained by core.data-loader only after successful task validation |
| Lookup returns authorization/transport error, malformed response, no match or many matches | Preserve sanitized diagnostics and resolver identity; stop under the declared lookup contract without treating failure as readiness |
| Reviewed archive, metadata, mapping or target changes | Revalidate the changed immutable archive and obtain new second-reviewer findings; core.data-loader must obtain new administrator approval after task validation and before submission. Prior approval cannot be reused |
| A Fusion submission outcome is uncertain | Stop before retry; selected execution workflow must reconcile the existing submission through documented read-only status inspection |
| PerfLossThresholdLimit comparison appears to differ between stored seconds and displayed minutes | Compare seconds divided by 60 with displayed minutes. The dated procedure reports incorrect program-field wording; do not change correct stored values to match it or claim that wording fixed |
| A successful load did not automatically set In Progress | Report the observed status separately; do not repeat the successful load. Run Book task completion requires its own explicit approval and status read-back through core.runbook |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Returning successful task validation to core.data-loader | Exact target/task and immutable package hash; proposed effect; current validation; second-reviewer findings; explicit delegation of subsequent administrator approval to the existing core.data-loader Task Hook/preflight workflow. That workflow must obtain approval bound to this immutable operation after all task rules pass and before submission; no actual approval record is required to return these preapproval findings. The Task Nodes authorize no direct Fusion write |
| Reporting an import or load | Exact process/request result and comparison of all supplied saved values, including shared reasons and language rows. Historical zero-error results, compiler success and file selection do not prove this run |
| Reporting Run Book completion | Distinguish FSM task CSV result, separately approved Run Book/Data Loader load, saved-value comparisons and separately approved task-completion read-back. Do not infer automatic In Progress, percentage or whole-book completion |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Alternate REST/DAT route proposed | Do not substitute a fabricated endpoint or registration for catalog FSM mode; execution and payload preparation remain with the selected core.data-loader workflow |
| Desired values are absent | Do not import the historical empty baseline, copy example tenant choices as defaults, infer values from headers, or claim configuration complete |
| No current exact operation approval or earlier uncertain submission remains | Do not write, upload, import, retry or mark a Run Book task complete from this task graph |
| Historical small import is used as QA coverage | Do not claim larger-file, invalid-input, interruption, permission or performance tests passed; the dated QA guide records these as unrun |

The success terminal below returns task-rule validation results to the invoking workflow only. It is not an import, saved-value comparison, Run Book load or completion. The selected core/shared execution workflow owns mutation and its current approval contract.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SOC.CHECK_APPROVAL_BOUNDARY | decision | 90 | execution_gate | delegated->SOC.DONE;blocked->SOC.HANDLE_ERROR | SOC.ENFORCE_DESIGN | stop | Verify exact immutable-archive identity and second-reviewer findings and the mandatory delegation of POST-task-validation administrator approval to the existing core.data-loader Task Hook/preflight workflow. Do not request an approval envelope before all task rules pass; return these validation findings without performing a write. |
| SOC.DONE | terminal | 100 | terminal | none | SOC.CHECK_APPROVAL_BOUNDARY | stop | Required task-rule checks, immutable-package/second-review checks and delegated approval boundary passed; return their results only. Actual subsequent administrator approval and submission remain with core.data-loader; never claim approval, completed import, saved values or task completion from this terminal. |
| SOC.HANDLE_ERROR | step | 110 | error_handler | handled->SOC.BLOCKED | none | stop | A preceding node reports blocked or failed; disclose the exact issue and safe next action. |
| SOC.BLOCKED | terminal | 120 | terminal | none | SOC.HANDLE_ERROR | stop | Return the identified unresolved contract or task-rule failure without mutation. |

## Source Authority

This restoration uses the historical Smart Operations task rules in the FSCR source repository at commit efd2e765b2dc89533646189bc44fbcf3eec96427, under pillars/scm/manufacturing-and-supply-chain-materials-management/manufacturing-master-data/ora-resource/. Its five ora_* Markdown sources were verified as existing blobs and byte-identical to the historical source read for this restoration. Dated September 2026 procedure snapshots in docs/SMART-OPERATIONS-CONFIGURATIONS-FSCR-DEVELOPMENT-STORY.md and docs/SMART-OPERATIONS-CONFIGURATIONS-FSCR-QA-GUIDE.md supply the approved historical run context; the latter is the complete guide named by the QA-GUIDE.md pointer. Current published procedure context is the parent and demo versions cited below. None of these dated sources establishes a fresh target result.

The parent [Smart Operations guidance](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452541), version 11, and [demo](https://confluence.oraclecorp.com/confluence/pages/viewpage.action?pageId=21846452542), version 6, were read on 2026-10-05 by the coordinating agent. The parent confirms the fresh-template, approved-row, second-reviewer and administrator handoff and distinguishes task CSV results from the separate Run Book load and completion. No reusable rule below supplies a demonstration organization, UOM, percentage, reason code, language choice, row count, or approval as a new implementation default.

## Delegated Post-Validation Approval Contract

The 26.10 `core/data-loader/SKILL.md` and
`core/data-loader/task-hook/SKILL.md` require read-only task validation before
the Task Hook preview and operation-bound approval. The Data Loader supplies
the immutable final upload artifact and persisted preflight. These task rules
return validation findings and second-reviewer findings; they neither create
approval artifacts nor invoke submission. An actual approval envelope is not
a prerequisite for returning preapproval task findings.

Task Hook's `build-data-load-preview`, `approve-data-load-preview` and
`verify-approved-data-load-archive` commands own the preview, approval and
verified `taskValidationEnvelope`. Pass the returned envelope unchanged under
the Data Loader's instructions. Never construct or repair its approval flags,
archive digest or Run Book bindings in task rules.

After later approval, the Data Loader verifies its persisted preflight,
immutable archive, approved Task Hook envelope and selected environment/Run
Book context, then submits the same approved bytes. It does not reopen the
original source or rerun task rules at that stage. A changed or missing
approved artifact or mismatched approval context requires fresh validation
and approval. Retain partial or uncertain results for the owning workflow's
reconciliation; these task rules perform no retry or write.
