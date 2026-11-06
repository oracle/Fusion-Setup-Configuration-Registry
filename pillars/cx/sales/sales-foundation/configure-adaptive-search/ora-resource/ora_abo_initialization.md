# Fusion ABO Initial Full Publish Companion

## abo-initialization

This is an additional, separately approved ABO companion operation. It does
not change standalone Adaptive Search or relax the existing selective API.
The complete parent sequence is defined in
`../../../../configure-price-quote/quoting/enable-fusion-asset-based-ordering/ora-resource/ora_initial_full_publish.md`.

`prepare_initialization_load` accepts only `submit_initial_full_publish`, v2,
the exact project/HTTPS-origin target, `publish_type=full`, a distinct `afi_`
identity and this ordered OOTB array:
`Account, Contact, Lead, Opportunity, Revenue, Activity, Asset, Product, CRMProductGroup`.
Require the matching consumed two-hour parent preparation permission, known
missing-metamodel/null/empty catalog blocker and exact verified CPQ predecessor.
This permission is not Core upload approval. Do not ask for a replacement
entity list in this fixed ABO initialization boundary; cancellation stops.

Only Entities' exact HTTP 400 `{"Error":"Could not find active meta model"}`,
null response, null `items` or empty `items` permits offering initialization.
Classify the final status and parsed JSON body from the declared REST adapter;
authentication diagnostics and message substrings are not catalog evidence.
All other errors, malformed responses and nonempty catalogs missing the ABO
pair stop. Recheck before the Full workbook handoff; a now-ready catalog returns
`not_required` so the parent can propose fresh Partial Publish without a Full
submission. A running publish or either stage's submission intent/receipt
blocks a new submission.

For initialization only, replace the normal six-field selective row rule with:
`RestAction=POST`, compact JSON `entities` containing the exact nine objects,
blank `publishType`, `Content-Type=application/json`, `REST-Framework-Version=9`,
`Preference=transient`. A blank optional `publishType` cell is omitted from the
REST body; do not let generated placeholders populate it. Validate the embedded
Full payload contract. During Core rule evaluation use its validated source records;
do not validate OOTB names against a missing catalog or change the prepared
archive. Reuse the exact saved Core preview only while it is current and bound
to this Full operation. Before the unchanged Core preview, show the separate `workbook_access` link once for optional viewing only; no review gate is added and file edits do not update the load. Then
require independent approval of its current preview on the declared Core persisted-preflight route.
Reserve intent before sending approval; Core alone verifies and uploads the saved archive after load approval.

Save private correlation in `adaptive-initialization/operation.json`, purpose
`adaptive_search_initialization`, operation ID `afi_...`, status operation
`get_initial_full_publish_status`. Do not share private loader IDs with parent
JSON or use an initialization receipt on the normal selective status/ESS route.
Return submission and stop for an explicit initialization status request. Full
Publish can take 10 minutes or longer; ask the user to wait about 8–10 minutes
before requesting the same status again. Do not add automatic polling.

`initialization_status` returns a Core status handoff for the exact loader only
on that request and accepts its bound result. Loader
success permits new-job discovery distinct from the pre-submit baseline.
Persist the new job; on a later check require its exact echoed ID. After job
success freshly require both ABO catalog entries present (not yet enabled).
Persist a proof bound to operation/project/target/job and exact loader success.
Always return `eligible_for_ess=false`. Only this proof lets the parent present
a new Partial Publish preparation proposal; require new preparation and Core
approvals. Final enabled-entity checks and ESS still belong to the later
Partial Publish. Failed/blocked/uncertain outcomes stop without republish;
possibly-sent intent recovery is status/reconciliation only.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AS.ABO_INITIALIZATION.PREPARE | step | 300 | execution_gate | prepared->AS.ABO_INITIALIZATION.APPROVAL;not_required->AS.ABO_INITIALIZATION.READY;blocked->AS.END.BLOCKED | none | stop | ABO only: consumed exact two-hour initialization preparation permission, verified CPQ, known catalog blocker, distinct afi identity and fixed nine-object Full row. Blank publishType, same four operation/header values. Recheck catalog/concurrency; ready catalog returns not_required without load. Standalone unchanged. |
| AS.ABO_INITIALIZATION.APPROVAL | decision | 310 | approval_gate | submitted->AS.ABO_INITIALIZATION.STATUS;declined_or_uncertain->AS.END.BLOCKED | AS.ABO_INITIALIZATION.PREPARE | stop | Evaluate initialization validated workbook rows and ordered task rules; show the unchanged Core preview. Require independent approval of that exact current preview, reserve intent, then submit its verified immutable archive once. Expired or changed previews require fresh preparation; an uncertain submission must be reconciled. |
| AS.ABO_INITIALIZATION.STATUS | decision | 320 | validate_result | pending->AS.ABO_INITIALIZATION.STATUS;verified->AS.ABO_INITIALIZATION.READY;failed_or_uncertain->AS.END.BLOCKED | AS.ABO_INITIALIZATION.APPROVAL | stop | Explicit GET-only initialization status. Pending stops. Exact loader and newly pinned job success plus fresh ABO pair presence return catalog_ready, never eligible_for_ess. Parent proposes fresh Partial preparation; no automatic submission. |
| AS.ABO_INITIALIZATION.READY | terminal | 330 | terminal | none | none | stop | Return catalog-ready/not-required evidence only to ABO; it must present a new Partial preparation proposal. This is not a Partial submission, final enabled readiness or ESS authorization. |
