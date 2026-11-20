# Central FBDI handoff evaluation



This is an assisted evaluation contract for ARCU.EXECUTION_GATE. A complete
compiled registry means the instructions can be planned. Each candidate still
requires actual evidence for every applicable check below. Neither compilation
nor a historical successful campaign supplies a passed rule result.

## Central compatibility gate

First read [governed read routes](governed-read-routes.md). The task-owned SOAP
mapping uses unchanged core authentication and transport; the original REST
reads and offline replay remain available under their declared preconditions.
Exact attempt evidence uses the task-owned collector described in
[attempt association](attempt-association.md), with unchanged core REST transport.
Submission uses the normal core approval and recovery contract below. Historical
imports do not qualify a new candidate. Do not add task-owned authentication,
submission, HTTP retry or generalized diagnostics infrastructure.

## Evaluate before the central preview

1. Use the selected project's existing active Run Book task context. Match task
   code ORA_AR_MANAGE_CUSTOMER_UPLOADS, business object customers, selected
   environment and Run Book binding. Do not create a replacement Run Book to
   avoid a failed or uncertain attempt.
2. Inspect the exact final archive with `customers_package.inspect_candidate`.
   Compare it with the reviewed business input, entity intent and blank/default
   expectations. Recompute the before-state target review through the declared
   assisted route. Review source, completeness and freshness; a match report
   alone is insufficient. Resolve all hard identity/effect conflicts.
   When receipt method input targets an existing account/site, inspect the
   before-phase API `receipt_before` result and independent source/parent binding.
   A visible overlapping period must be resolved before approval, not accepted
   as an uncertain business rule. Incomplete evidence is not a clear period.
   Do not resubmit just because the previous after-state values match.
   For a user-authorized data-design proposal, retain proposed-business-input
   provenance and its input hash in the Customer review, reference that review
   in supported rule evidence, disclose its values and origin,
   and keep acceptance pending the normal exact-candidate approval. A ZIP alone
   cannot establish input provenance. Never infer acceptance from preview success.
3. Delegate the final archive to the selected checkout's core.data-loader with
   the actual Run Book task context and explicit business object `customers`.
   Follow that skill's supported validation, captured-source, preview and approval
   workflow. Do not select old commands from task instructions or simulate an
   upload to test access. Verify Customer prerequisites through the read-only
   registration and capability checks below; core owns actual route resolution,
   source integrity and execution. Compare the captured native CSV with the
   reviewed ArUpdCustomers.csv before returning passing customer rule results.
4. Use `customer_registration_review.review_delegated_registration` to bind
   the exact candidate, active Run Book control and retained qualified recipe to
   fresh complete public BO/FBDI metadata and loader action-capability evidence.
   Follow [registration evidence](registration-evidence.md). This is customer
   prerequisite evidence, not proof of core approval or an exported core plan.
   A changed route or BO update marker requires deployment review. The marker
   cannot prove child/private recipe immutability. The full recipe remains a
   deployment qualification; do not require implementor SQL or claim REST read
   the private recipe. Core resolves and binds its own execution route.
5. Review authentication and authorization separately from metadata matching.
   Identify the actual core OAuth principal and retain the results of the
   applicable read-only preflight. Successful metadata reads establish read
   access only; Publisher's signed-in account does not identify the REST caller.
   Record UCM upload and initiation access as `not_yet_tested` until supported
   evidence establishes it. This does not block a non-mutating preview or claim
   permission. Do not require a prior successful upload to prepare the first
   governed test. Known access denial or failed required authentication/preflight
   blocks execution until resolved. After exact-candidate approval, core performs
   the upload and initiation with server-enforced authorization. A UCM access
   denial must stop before initiation, without upload retry, account substitution
   or another import route. This is an execution-access check, not a business
   validation gap that a user waiver can override. Do not request passwords or
   expand permissions as a workaround.
6. Use unchanged core Data Loader for one approved invocation. Preserve the
   exact ZIP, customer review, actual core public preview/decision/initiation
   evidence, local Run Book binding, ContentId and returned RequestId. Use only
   the selected core contract's recovery policy, disclosed in the candidate
   decision. Do not introduce task retries or assume an older core's recovery
   applies to another implementation. Unknown outcomes require status-only
   recovery. Missing server Run Book association blocks verified completion;
   never invent linkage or resubmit to obtain it. Submitted does not mean loaded.

7. Review the candidate's generated [verification plan](verification-plan.md),
   before-state and expected effects under the
   [business-outcome scope](business-outcome-reconciliation.md). Retain all 87
   worksheet columns, including supplied DFF contexts/segments. Identify supported
   runtime collection for every requested value and source-backed relevant effect,
   including partial persistence. Review visible omitted/default changes and any
   affected contexts, siblings or historical versions. Unused hidden storage and
   unrelated history are disclosed as unobserved, not unconditional blockers or
   assumed preservation. Resolve unavailable required readback contracts before
   execution; actual after-results are collected later. Detailed developer SQL
   comparator inputs are not implementor prerequisites.
8. Retain the [attempt association](attempt-association.md) and
   [request-scope](request-evidence.md) collection plan. Future IDs remain absent
   until returned. Any initial live mapping uncertainty must remain visible and
   require reconciliation; it never authorizes guessed IDs or resubmission.
9. Disclose eligible business-validation gaps for the exact candidate. The
   later decision is bound to the actual public core preview reference, environment,
   registration and arguments through the existing package review context; do not
   require a future preview ID to evaluate pre-preview readiness. Missing hard
   inputs and known-invalid data take the blocked transition.

Record each check's evidence references and disposition in the private campaign
workspace. A missing input, exception or unresolved hard check takes `blocked`.
Preserve the findings with `execution_authorized: false`; do not fabricate
passed resource results or invoke readiness override to complete development.

## Task Hook and submission

The reviewed 26D loader checks query text lexically: SELECT or WITH followed by
a space is accepted, but any semicolon, `--`, `/*`, or `*/` is rejected even
inside quoted messages. Registration review checks this before matching the
exact recipe. Use comma separators in error messages. A locally corrected
contract is prospective until deployment and fresh readback match; never repair
supplied evidence in memory or reuse a historical approval for the new recipe.

For a declared create operation, `ACCT_ADDRESS_SET_CODE=COMMON` is known invalid
for site-use insertion: 26D `HZ_CIMP_ACCTSITEUSES_VAL.CK_ASU_LKUP_SET_ID` rejects
COMMON when ACTION_FLAG is I. Do not replace it automatically or treat this as
an overridable evidence gap. Review an appropriate configured non-COMMON set.
For update/mixed, resolve per-entity insert/reuse/update intent under the existing
ownership contract; passing package inspection alone does not establish support.

Follow [core delegation](core-delegation.md). Evaluate every planned rule
resource in order against core's captured source. Only passing applicable checks
permit a preview; a preview is not approval. Present the exact candidate, effects
and eligible gaps through the selected core decision workflow. Preserve core's
required presentation, approval and source-integrity controls. Retain its public
evidence and revision; never manufacture a legacy envelope, an approval or a
passed resource. Lost session or changed source follows core's restart policy.

Monitoring and reconciliation follow the phase and verification contracts.
Keep process status, business effects and Journey synchronization separate;
no pre-import terminal marks the task complete. Retain partial success and use
status-only recovery for an uncertain attempt.

## Implementation anchors

The runtime entry point is the selected repository's `core/data-loader/SKILL.md`.
Its implementation and recovery mechanism are core responsibilities. Customer
helpers do not obtain tokens, submit loads or grant execution permission.
