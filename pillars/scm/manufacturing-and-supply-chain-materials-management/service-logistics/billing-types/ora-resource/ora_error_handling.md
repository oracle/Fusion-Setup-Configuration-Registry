# Billing Types Create and PATCH Gates

## Source and Scope

Source: the explicit flag-update request, live billingTypes describe, registered Data Loader template and this branch's core Data Loader immutable-artifact, persisted-preflight and Task Hook approval workflow, inspected 2026-10-20. Supported mutation scope is a one-record POST with resolved lookup codes and zero existing type-code matches, or PATCH of EnabledFlag on exactly one current Billing Type. A ready rule graph means the contract is complete, not that a particular load is approved or already executed.

Task checks apply to the exact final immutable upload artifact verified by core's persisted preflight. "Captured source" in these task resources means the records in that artifact. Core owns Task Hook preview construction, approval, archive verification and submission using its approved preflight and task-validation envelopes. Follow `core/data-loader/SKILL.md`; do not reconstruct or edit those envelopes. Read-only lookup responses remain ephemeral and are not upload artifacts.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BILLING_TYPES.EXECUTION_GATE | step | 30 | execution_gate | passed->BILLING_TYPES.PREVIEW_READY;blocked->BILLING_TYPES.RETURN_ISSUES | BILLING_TYPES.RESOLVE_REFERENCE | stop | Before core constructs the Task Hook preview for the supported PATCH against the final immutable upload artifact |
| BILLING_TYPES.CREATE_GATE | step | 32 | execution_gate | passed->BILLING_TYPES.PREVIEW_CREATE;blocked->BILLING_TYPES.RETURN_ISSUES | BILLING_TYPES.CHECK_CREATE_UNIQUENESS | stop | POST only: validate create-specific schema, explicit flag, zero duplicates, source and project binding before core preview |
| BILLING_TYPES.PREVIEW_READY | terminal | 40 | terminal | none | BILLING_TYPES.EXECUTION_GATE | stop | All applicable contract, identity, schema and final-artifact rules passed; return findings to core for its own preview and approval |
| BILLING_TYPES.PREVIEW_CREATE | terminal | 42 | terminal | none | BILLING_TYPES.CREATE_GATE | stop | POST rules passed; return findings to core for its own preview and approval |
| BILLING_TYPES.NO_CHANGE | terminal | 45 | terminal | none | BILLING_TYPES.RESOLVE_REFERENCE | stop | The uniquely resolved current record already has the requested flag; return no change needed and do not submit |
| BILLING_TYPES.RETURN_ISSUES | terminal | 90 | terminal | none | none | stop | Any validation, identity, environment, privilege or execution-route blocker |

## Error Situations

| Situation | What Should Happen |
|---|---|
| Preview readiness | Require exact billingTypes registration, live support for the selected POST or PATCH action, schema-valid records in the final immutable upload artifact, matching persisted preflight and environment/Run Book/task context, and required privileges. For POST require resolved category/type codes, an explicit Boolean flag, no surrogate or audit fields and zero duplicate codes. For PATCH require the flag-only source and one current target. Return passed findings only when all applicable checks succeed. Core constructs the Task Hook preview and owns submission authorization. |
| Unsupported operation or changed field | Return blocked with the unsupported operation/field. Supported paths are one-record POST and flag-only PATCH. Reject DELETE, changes to an existing category/code, null clearing and bulk mutations. |
| Target absent or ambiguous | Stop with the resolver's match result. Never create a missing target or choose the first record. |
| Auth, privilege, transport or schema failure | Report the failed stage and sanitized error; preserve distinctions. Use only core auth's documented once-only cached-token refresh for eligible read requests. |
| Mutation result uncertain or failed | Follow core's retry and reconciliation policy; do not add a task-level automatic retry. Preserve known partial results and core-required artifacts/envelopes for reconciliation. Use the selected core status workflow on request. |
| Completed loading | For POST, requested verification requires exactly one fresh matching BillingTypeCode and agreement with the requested category/flag, then retains its server-generated BillingTypeId in memory. For PATCH, a requested verification uses a fresh complete core BO read and the retained exact BillingTypeId. Confirm the requested flag and preservation of omitted business fields. Exclude normal audit/version changes from the business-field preservation comparison. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Rule blocker | Exact task identity, rule/action, failure reason, verified effects and one safe next action. |
| Approval preview | Display core.data-loader's own Business Object Validation report and approval question verbatim. Follow core's approval policy, including its explicit same-request auto-approval exception. Prior plan approval or a generic affirmative does not authorize a different artifact, environment or Run Book binding. Do not add a second task-level approval. |
| Accepted initiation | Return core's accepted-initiation report without claiming completed loading or automatically polling. |
| No-op | If the current flag already has the requested value, report no change needed and do not submit. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing task binding, schema, identity, privilege or preview approval | Do not submit or substitute a direct REST mutation, browser, alternate uploader, guessed key, stale or modified approval envelope, or another task's Run Book binding. Use only core's verified envelopes for the exact approved artifact and binding. |
| Source or target correction | Invalidate the previous preview and approval when the source, target or material observed state changes. Return through core's validation and Task Hook preview/approval workflow for a fresh immutable artifact and binding. Do not edit approved artifacts/envelopes or reread/rebuild the original source after approval to submit under an earlier approval. |
| Secret or customer-data disclosure | Never persist credentials or tokens in repository/project artifacts, or real customer data in tracked files or project workspaces. Keep live lookup response bodies and diagnostic payloads ephemeral or redacted. Core-required immutable upload artifacts and approval envelopes must use only repository-policy-permitted local paths and follow core's integrity, retention, reconciliation and cleanup rules; persistence does not authorize sensitive-data disclosure. |

PREVIEW_READY and PREVIEW_CREATE return validation findings only. It does not itself execute a PATCH or report that the flag changed. RETURN_ISSUES has no side effects.
