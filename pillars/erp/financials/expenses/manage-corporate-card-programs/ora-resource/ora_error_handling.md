# Manage Corporate Card Programs Error Handling

> Execution scope: apply these task rules through the service handoffs in
> [live setup workflow](../references/live-setup-workflow.md). The rule registry
> performs validation only; core Data Loader owns import approval and submission.


Source-backed draft for EXM_MANAGE_CORPORATE_CARD_PROGRAMS. Public documentation is 26D; maintainer provenance is SOURCE-SNAPSHOT-147cfa7f931f. Source revision references do not establish compatibility with a deployed environment. The bounded CREATE preparation contract is defined in references/create-contract.md; unsupported requested features stop before preparation. Internal ADF calls do not establish callable preflight APIs.


## Error Situations

| Situation | What Should Happen |
|---|---|
| Source or execution contract is TBD | Stop normal planning with the exact canonical field and evidence needed; preserve business intent without inventing a route or value. |
| Duplicate program or invalid inactive date | Preserve the actual EXM_CC_CARD_PRGRM_EXISTS or EXM_CC_INACTV_DTE_ERLY_EQ_TDAY diagnostic and the sanitized field context; validation ownership is in input validation. |
| Issuer-site resolution fails | Importer records CardIssuerSiteId row error/severity1 and removes the affected company-account XML child before root processing; report partial outcomes (SITE-PARTIAL-ERROR). |
| Clearing-account procedure or statement cleanup raises an exception | The reviewed code catches locally without proving complete propagation; require actual process/row diagnostics and reconciliation before success (COMBINATION-ERROR-LIMIT). |
| Party/site number collision occurs | The reviewed branch may prefix/truncate site identifiers and defer correction; disclose actual resulting identities through sanitized verification. Do not claim preservation or rollback (PARTY-SITE-COLLISION). |
| Outer import processing raises an exception | Importer returns MigratorStatus processingError with localized message or Null Exception. A root commit or ImportReturn alone does not prove every child succeeded (IMPORT-STATUS). |
| Any eventual import fails or its outcome is uncertain | Stop before retry; retrieve available status/ProcessLog, preserve partial successes and errors, and reconcile the accepted request through its declared workflow. |
| Polling times out | Report environment, operation, task code, ProcessId/requestId, last status, elapsed wait and next-check path. Do not resubmit a live operation automatically. |
| A workflow-required durable artifact cannot be persisted | Stop the handoff and report artifact-persistence failure. Persist only sanitized evidence allowed by the owning workflow; transient session inputs, previews and approvals must not be saved. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Invalid supplied field or unsafe artifact shape | Correct only the reported input and repeat static validation |
| Catalog mismatch | Task, environment/release, member or header contract differs | Acquire qualified same-task evidence through the declared route |
| Auth or authorization | Principal or approved authentication context lacks access | Owning client may refresh a cached token once for401/403; stop on repeat denial |
| Transport or environment | DNS, TLS, connectivity or bounded read failure | Correct access; use only the owning workflow bounded safe-read retry policy |
| Fusion API | Oracle rejects a request or returns an unusable response | Preserve sanitized diagnostics; do not recast the failure as a missing reference |
| Process timeout | Polling exceeds the owning workflow bound | Stop and report accepted process identity and next-check path |
| Process failed | Terminal failure or partial/unverified business result | Review ProcessLog and child outcomes; require reconciliation before another live attempt |
| Artifact persistence | A durable artifact explicitly required by the selected workflow cannot be saved | Repair the approved destination before continuing. Do not turn a memory-only preview or session capture into a durable artifact |
| Approval blocker | Required readiness, immutable preview or approval is absent | Stop before handoff/mutation and satisfy the owning Run Book/Data Loader gate |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Draft readiness | Exact task, incomplete nodes and canonical fields, source/release boundaries, supported observations and required next evidence |
| Future package preview | Use the selected Data Loader approval report verbatim after its checks pass; retain target binding and integrity details only as its contract permits. Do not independently expose internal fingerprints or require an extra approval keyword |
| Accepted initiation | Return the owning Data Loader initiation report immediately and verbatim; do not poll as part of that accepted-initiation request |
| Later authorized status or verification | Use the original accepted request/process identity and the owning workflow report; distinguish partial results, errors and verification from initiation, and retain only permitted evidence |
| Completion | Task-rule readiness is separate from actual import completion; report import success only after the owning workflow verifies all requested effects |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Incomplete registry | Silently override readiness, invent an endpoint, guess defaults or copy GL product rules. Only an explicit user waiver may follow the owning core task-validation override workflow, preserving each finding; it does not authorize import or supply missing values |
| Uncertain mutation outcome | Replay import, POST/PATCH/DELETE or an ESS job without idempotency evidence or explicit approval under the owning workflow |
| Sensitive source data | Store credentials, tokens, private keys or encrypted-password values in repository/project files, or put customer rows in tracked/reusable artifacts. Authorized setup exports stay untracked under the active project exports directory; never persist memory-only session captures |
| Session handle is lost or expired | Reconstruct captured inputs, persist a recovery envelope, or replay a prior approval; restart validation and approval through the selected core |
| Task-rule graph is complete | Treat it as live import authorization; Data Loader still owns preview, approval, package processing and writes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CCP.EXECUTION_GATE | decision | 60 | execution_gate | ready->CCP.READY;blocked->CCP.HANDLE_ERROR | CCP.ENFORCE_DESIGN | stop | Require complete task contracts and normal ready plan before returning readiness to Run Book/Data Loader; this node performs no import. |
| CCP.HANDLE_ERROR | step | 70 | error_handler | reported->CCP.BLOCKED | none | stop | A reached validation, lookup, dependency, defaulting, design or readiness gate fails. |
| CCP.READY | terminal | 80 | terminal | none | CCP.EXECUTION_GATE | continue | Task rules are ready for the separate governed workflow; no import success is implied. |
| CCP.BLOCKED | terminal | 90 | terminal | none | CCP.HANDLE_ERROR | continue | Return classified blockers and a safe next action; no write was authorized by this graph. |

## Source Evidence

| Fact ID | Reviewed Source and Locator | Evidence Boundary |
|---|---|---|
| SITE-PARTIAL-ERROR | SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:786`); lines 786-800; SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:859`); lines 859-860; SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:1048`); lines 1048-1055 | Evidence of partial-row processing; do not claim package atomicity or count root success as all-child success. |
| COMBINATION-ERROR-LIMIT | SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:887`); lines 887-903 | No guaranteed detailed error propagation, successful combination resolution, rollback, or all-or-none guarantee. Draft verification must inspect process/row diagnostics and unresolved references. |
| IMPORT-STATUS | SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:1070`); lines 1070-1083 | No explicit rollback is shown in catch, and success of all child rows is not implied by returning ImportReturn or commit. Do not add automatic retries or claim idempotency. |
| PARTY-SITE-COLLISION | SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:398`); lines 398-405; SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:463`); lines 463-495; SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:499`); lines 499-505 | Collision is not simply rejected. Do not promise identity preservation, atomicity or transparent rollback; preserve diagnostic review and explicit entity reconciliation. |
