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
   provenance and its input hash in finalData, disclose its values and origin,
   and keep acceptance pending the normal exact-candidate approval. A ZIP alone
   cannot establish input provenance. Never infer acceptance from preview success.
3. Run the normal core Data Loader validation-only flow for that final archive,
   using the approved authentication profile. Retain its real preflight envelope,
   including task routing, live action support for runBookTaskCode and FBDI
   interface/UCM metadata. Do not simulate an upload to test access.
4. Bind the actual core envelope and project Run Book control to a qualified
   deployment. `customer_registration_review.analyze` checks supplied full
   registration evidence against the reviewed argument/scope, validation and
   status/error recipe. For normal runtime use, `analyze_published` combines
   that retained deployment qualification with fresh complete core BO/FBDI
   metadata pages, exact IDs/routes/prefixes and the parent BO update marker.
   A reported update since qualification requires deployment review. The marker
   does not prove child/private recipe immutability; full configuration is not
   exposed by this REST response. Keep controlled registration changes and seed
   qualification as deployment responsibilities. Data Loader resolves the
   server recipe. Do not demand an implementor SQL query or claim the retained
   recipe was freshly read over REST. Preserve resulting final_data for the
   preview and use the corresponding `published_preview_context` or
   `preview_context` to recompute the same evidence binding. A known changed
   recipe or route must be reviewed before submission.
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
6. Use unchanged core Data Loader for one approved invocation. Preserve the exact
   ZIP, preflight, local Run Book binding, ContentId and returned RequestId.
   The exact-candidate preview and approval must cover core's documented bounded
   rejection recovery: one authentication refresh on 401/403 and one 27503
   recovery using the same ContentId without optional Run Book fields. If that
   recovery is not authorized, do not invoke a client that can perform it.
   Do not wrap core with task retries or resubmit after timeout/unknown outcome.
   A missing server Run Book association remains unverified and blocks verified
   completion, not permission to invent linkage. Keep the local approved binding;
   reconcile the exact retained attempt and obtain a specific decision before
   any further submission. Initiation acceptance means submitted, not loaded.

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
   later decision is bound to the actual preview using `preview_context`; do not
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

Use the core Task Hook `data-load` route after core has prepared the immutable
archive. Evaluate every returned rule resource in order. Only if all applicable
checks pass, invoke `build-data-load-preview` with the actual rule results and
registration-bound finalData. The preview is not approval. Present the exact
candidate, effects and eligible gaps through the normal core decision.

After that decision, core alone owns preview approval, exact archive verification,
UCM upload and initiation. Do not add a second upload client or direct ESS route.
Retain the exact approved envelopes and selected core revision so their scope can
be checked after interruption. Do not regenerate a candidate after approval.

Monitoring and reconciliation follow the phase and verification contracts.
Keep process status, business effects and Journey synchronization separate;
no pre-import terminal marks the task complete. Retain partial success and use
status-only recovery for an uncertain attempt.

## Implementation anchors

The selected repository's core contracts are `core/data-loader/SKILL.md`,
`core/data-loader/task-hook/scripts/task_hook.py` and
`core/data-loader/scripts/upload_and_initiate.py`. Inspect
`upload_approved_preflight`, `_require_approved_task_validation` and
`_initiate_data_load` plus their regression tests. These are authoring anchors,
not permission to bypass their declared workflow. The task helper intentionally
does not obtain tokens, perform network operations or grant privileges.
