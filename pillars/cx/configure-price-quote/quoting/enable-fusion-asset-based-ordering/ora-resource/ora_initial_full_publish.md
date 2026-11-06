# Initial Adaptive Search Full Publish

## adaptive-initialization

This exception is ABO-only. Standalone Adaptive Search behavior is unchanged.

1. During approved Partial Publish preparation, only Entities' exact HTTP 400
   body `{"Error":"Could not find active meta model"}`, null response, null
   `items` or empty `items` selects initialization. Other errors, malformed
   responses and a nonempty catalog missing the ABO pair stop without fallback.
2. Retain verified CPQ and the safe catalog error. The consumed Partial Publish
   preparation permission cannot approve initialization. Show the full ABO
   template and exact initial Full Publish scope: Account, Contact, Lead,
   Opportunity, Revenue, Activity, Asset, Product, CRMProductGroup.
3. `preview-adaptive-initialization` returns the same pending preparation-only
   proposal. Ask: "Approve preparing the initial Adaptive Search Full Publish?
   Upload and submission will require a separate Data Loader approval."
   Bind its two-hour one-use permission to project/workflow, target, process,
   verified CPQ receipt and ordered nine-object scope. Cancellation/expiry stops.
   `--refresh-initialization` requires a stopped proposal with no publish intent
   or receipt. Do not reoffer Partial Publish while the blocker is unresolved.
4. `prepare-adaptive-initialization --approve-initialization-preparation
   --initialization-preparation-sha256 <current-proposal-digest>` rechecks
   CPQ/Fusion readiness and consumes permission before invoking the companion's
   `prepare_initialization_load`. If the catalog became ready externally,
   propose fresh Partial Publish without generating/submitting Full Publish.
   Otherwise check concurrency and return the Core workbook-generation handoff.
   Return its result through `accept-adaptive-workbook --load-stage initialization`,
   then follow the 26.10 Core persisted-preflight/Task Hook handoff. Do not
   validate OOTB names against the missing catalog.
5. Full REST body contains only the nine-object `entities` array, no
   `publishType`. Workbook `entities` is compact JSON; explicitly blank the
   optional `publishType` cell to prevent sample defaults. Require
   `RestAction=POST`, `Content-Type=application/json`, `REST-Framework-Version=9`,
   `Preference=transient`. Evaluate this initialization scope from Core validated workbook rows
   instead of the normal selective-pair rule. Keep Core’s saved preflight,
   immutable archive and task validation bound to this Full operation.
6. Return Core's preflight result through `build-load-preview --load-stage initialization`.
   Display the separate `workbook_access` link once for optional viewing before Core’s unchanged preview; viewing adds no approval gate and file edits do not alter the frozen archive. After ordered task rules pass, require separate affirmative approval of the exact saved preview. `submit-data-load --load-stage initialization` reserves intent and returns the Core submit handoff. Core verifies and submits that archive once; return its structured receipt via `complete-data-load --load-stage initialization`. Save a distinct `afi_` receipt under
   `adaptive-initialization`; it is never a normal `apo_` Partial Publish or ESS
   predecessor. Pause: "Check the Full Publish initialization status and continue."
7. `check-adaptive-initialization-status` requires an explicit user request.
   Follow its Core status handoff for the exact private loader request and
   return the bound result; pending stops. On load success,
   discover/pin a new publish job distinct from the baseline, then on a later
   check require the exact job response to echo its ID. Load success alone is
   not publish completion. After job success, freshly read Entities and require
   both ABO entities present; they need not be enabled yet. Failed, unknown or
   blocked results stop without resubmission. No continuous initialization
   polling is introduced. Initialization is never eligible for ESS.
8. Only exact successful load, pinned job and fresh catalog proof clear the
   blocker. Show a new normal Partial Publish preparation proposal, not its
   workbook. Require fresh preparation and independent Core approvals.
   Existing loader status, publish monitoring choice, enabled-entity readiness
   and separate exact-payload ESS approval remain unchanged.

Resume is local and cannot start Core or a mutation. A confirmed receipt resumes
exact status without new preparation approval. A possibly-sent intent without
receipt is indeterminate: reconcile, never replay. Preserve prior artifacts and
CPQ completion. No Core, CPQ executor, ESS adapter or general publish contract
changes are needed.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ABO.INITIALIZATION_PREPARATION_APPROVAL | decision | 11 | approval_gate | approved->ABO.INITIALIZATION_SESSION;declined_or_invalid->ABO.RETURN_ISSUES | ABO.CPQ_VERIFICATION | stop | Exact Entities missing-metamodel HTTP 400/null/empty only. Retain CPQ; show safe blocker/full ABO template and ordered nine-object Full proposal. Separate two-hour one-use preparation permission cannot authorize Core load. |
| ABO.INITIALIZATION_SESSION | step | 12 | companion_handoff | submitted->ABO.INITIALIZATION_STATUS;not_required->ABO.ADAPTIVE_PREPARATION_APPROVAL;failed_or_uncertain->ABO.RETURN_ISSUES | ABO.INITIALIZATION_PREPARATION_APPROVAL | stop | Recheck readiness, consume exact initialization preparation permission and use companion Full workbook/Core preflight. Ordered task validation, independent approval of the exact saved Core preview, and intent reservation precede the single submission. Either-stage intent/receipt prevents another submission. |
| ABO.INITIALIZATION_STATUS | decision | 13 | validate_result | pending->ABO.INITIALIZATION_STATUS;verified->ABO.ADAPTIVE_PREPARATION_APPROVAL;failed_or_uncertain->ABO.RETURN_ISSUES | ABO.INITIALIZATION_SESSION | stop | Explicit user-requested exact initialization status only; pending stops. Exact loader success, newly pinned job success and fresh ABO catalog presence permit a new Partial preparation proposal, never automatic submission or ESS. No resubmission on failure/uncertainty. |
