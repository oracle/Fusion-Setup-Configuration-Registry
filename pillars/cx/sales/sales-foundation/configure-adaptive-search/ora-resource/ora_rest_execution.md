# Adaptive Search Publish REST Execution

## Runtime Sources

| Source | Purpose |
|---|---|
| Oracle internal Entities REST page, page 15247618940 | Enabled-document entity endpoint, response collection, and entity fields |
| Oracle internal Elastic Indexing Publish REST design, page 2821068048 | Publish and status endpoints, request/response fields, states, and tested failures |
| Oracle Adaptive Search configuration documentation | Functional meaning and UI baseline |
| ora_publish_contract.json | Bundled runtime mapping authority for the internally documented custom publish action |

## Execution Contract

| Situation | What Happens |
|---|---|
| Entities GET returns HTTP 200 with a nonempty items array | Validate requested object display names against localizedName, map them uniquely to entityName for a Partial Publish payload, add `publishType: selective`, and show active and requested objects using localizedName |
| Request contains a recognized CPQ alias | Resolve `Quote`, `Quotes`, `Standard Quotes`, `Standard Quote Process`, `oraclecpqo`, `oraclecpqo_transaction`, or `oraclecpqo_transactionLine` case-insensitively to both direct entities `oraclecpqo_transaction` and `oraclecpqo_transactionLine`; skip Entities validation for those entities but still make one Entities call to detect a null or empty new environment |
| User explicitly requests Full Publish | Collect and validate the requested object list. With a nonempty Entities response, ask whether to retain current active objects with the newly requested objects; then perform publish-status preflight and prepare the selected full-publish entity array without `publishType` |
| Entities returns HTTP 400 `Could not find active meta model`, the response is null, has null items, or has an empty items array | Treat the target as a new environment, show the defined OOTB display list and confirmation. Before that combined confirmation, perform publish-status preflight. On Yes, submit its defined internal-entity array without `publishType`. On No, collect and validate a replacement list, then submit its mapped internal-entity array without `publishType`. |
| Validated object list | Check publishStatus and map the payload before rendering the one combined publish confirmation; HTTP 404 with exactly `{"Error":"Cannot parse null string"}` is an expected no-prior-publish concurrency pass; do not render a separate selection review, final preview, or approval prompt |
| User declines the displayed selection | Ask for a revised nonempty object list and repeat the object review as a new controlled iteration |
| Requested names are absent from the isDocument=true Entities response localizedName set | Display every invalid name with up to three nearest display-name suggestions, ask whether a suggestion is the required entity, collect corrections, and repeat comparison with the full revised list; do not publish the valid subset or display the full catalog |
| localizedName maps to multiple entityName values | Show numbered `localizedName (entityName)` choices and require an exact user selection; do not guess |
| Entities GET returns HTTP 400 `Could not find active meta model` | Treat as a new environment and continue to the OOTB Full Publish confirmation |
| Entities GET returns HTTP 400 other than `Could not find active meta model`, or any other non-200 status | Stop and return the HTTP status plus a redacted Fusion error message |
| Live requested without matching approval | Stop before POST |
| Publish accepted | Persist Data Loader correlation internally. For a standalone request display its Content ID and Request ID; for a Fusion ABO companion return only `publish_operation_id` and `SUBMITTED`. Do not claim a publish job ID. The dependent Fusion ABO controller pauses for an explicit user load-status request; standalone requests do not poll automatically. |

## Endpoint

| Action | Method | Path |
|---|---|---|
| Get document-entity catalog and active-state flags | GET | /crmRestApi/searchResources/latest/entities?language=en&limit=-1&isDocument=true |
| Get latest publish status | GET | /crmRestApi/searchResources/latest/publishStatus |
| Submit partial or full publish | POST | /crmRestApi/searchResources/latest/custom-actions/queries/publish |
| Get submitted publish status | GET | /crmRestApi/searchResources/latest/publishStatus?jobId={jobId} |

## Execution Adapter Binding

Use `core.fusion-api.rest-api-client` only for the read-only GET operations in
the Endpoint table. Invoke only
`core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`, which reads
`core/auth/fusionEnv.properties` and obtains OAuth through the shared
authentication service. Use `core.data-loader` as the executable adapter for
the approved publish operation through the registered REST business object
`publish`; it uses the same `core/auth/fusionEnv.properties` environment.

| Operation | Client invocation contract |
|---|---|
| Entity lookup | One GET to the declared Entities path; use the response only for this request's validation. |
| Publish-status preflight and later user-requested status | One GET to the declared publish-status path; block only `WAIT`, `RUNNING`, or `PAUSED`. During preflight, HTTP 404 with exactly `{"Error":"Cannot parse null string"}` is an expected no-prior-publish pass; other errors stop. |
| Fusion ABO companion status | Exact opaque operation. Data Loader inspection only on explicit request; after verified success discover/pin the new job. Parent checks once and offers monitoring choice; repeated 15-second job-only ticks require current consent. |
| Approved Partial or Full Publish | Create and validate the immutable Data Loader REST source for business object `publish` before the combined confirmation. That single confirmation is also the artifact approval, then initiate exactly one import. Do not retry automatically. |

The final publish request must not be submitted by a direct REST POST in this
branch. It is carried by the registered Data Loader REST business object. Do
not require a separate Adaptive Search adapter: a successful live metadata
resolution for `publish` is sufficient to proceed through the Data Loader
workflow.

## Data Loader REST Import Mapping

| Data Loader field | Value | Rule |
|---|---|---|
| Business object | publish | Registered Data Loader REST business object for this task; its live metadata is the execution authority |
| RestAction | POST | Required for the custom REST action |
| entities | Approval-bound mapped internal entity array | Require the live metadata to confirm a string source field; otherwise block. The REST payload remains an array. Preserve order and serialize the value as a compact JSON array of strings in the XLSX cell (for example, `["Account","Contact"]`), using the canonical form required by `ora_publish_source_serialization.json`. Decode it back and require an exact match before immutable-source approval. Never use a comma-delimited string or a Python list representation; any unexpected field type or failed round trip blocks. |
| publishType | selective for Partial Publish; blank for Full Publish | A blank value is omitted from the JSON body; never send `publishType` for Full Publish |
| Content-Type | application/json | Required REST header field |
| REST-Framework-Version | 9 | Required REST header field |
| Preference | transient | Required REST header field |
| searchPublishId | No Adaptive Search payload mapping | Non-required Data Loader surrogate metadata. Preserve a loader-generated value only when the validated source format requires it; never include it in the REST body and never block because no business value exists. |
| SourceRefTableName and SourceRef001 through SourceRef010 | No value | Optional Data Loader reconciliation metadata. Do not populate, serialize, or require a mapping for this publish. |

Generate the `publish` sample from live Data Loader metadata before preparing a
source when no current validated sample exists. The metadata read is read-only.
Do not add an adapter-readiness preflight after this successful resolution.
Validate only the mapped publish fields and source-format requirements. The
presence of non-required surrogate or reference metadata is not an unmapped
payload-field blocker.
Validate the source before the combined object-confirmation flow. Include its
operation and Full/Partial payload treatment in that one confirmation table.
The user's reply approves both the final object list and that exact immutable
Data Loader source; do not render a second Data Loader approval prompt.

## Object Review Pattern

| Step | Requirement |
|---|---|
| 1 | Call the Entities endpoint once with `isDocument=true` and without `isEnabled`, including for a CPQ-only request, to detect HTTP 400 `Could not find active meta model`, null, or empty new-environment responses; use the approved authentication service |
| 2 | On HTTP 200 with a nonempty items array, build the valid-choice set from every nonempty localizedName and its nonempty entityName mapping; separately filter isEnabled=true for the active display. Recognized CPQ aliases contribute both direct CPQ entities without catalog validation, but exact matching entityName records supply their localized presentation names and enabled state. |
| 3 | Show Current active objects, Additional Objects Added, and Final publish selection using localizedName when available. For a direct CPQ entity absent from the response, show its exact entity name rather than `Not inferred`; the CPQ final selection always has both direct entities and an object count of two. Additional Objects Added is the final selection minus the current active objects; render `None` when empty. Do not silently union or mutate the requested list. |
| 4 | Compare the entire requested list with all nonempty localizedName values returned under isDocument=true using exact matching; never apply isEnabled to name validation or display the full catalog |
| 5 | If invalid, show all unmatched names plus up to three nearest localizedName suggestions for each; ask whether a suggestion is the required entity. For duplicate labels show `localizedName (entityName)` and require an exact choice; validate the complete corrected list before showing the confirmation prompt |
| 6 | For an explicit Full Publish with a nonempty Entities response, before publish-status preflight, show Current active objects and Newly Requested Objects to enable. Ask exactly: `Should the current enabled objects be retained and combined together with the requested objects for a new publish ?` On Yes, use the ordered, deduplicated active-plus-requested selection; on No, use requested objects only. This selects objects and is not approval to submit. After publish-status preflight, payload mapping, and immutable Data Loader source validation, render the Combined Publish Confirmation Table. Its Yes confirms the final selection and approves that exact Data Loader source; do not render another approval prompt. |
| 7 | On No, collect a revised nonempty list and rerun the review iteration before publishStatus or POST |
| 8 | On HTTP 400 `Could not find active meta model`, a null response, null items, or an empty items array, display `Accounts, Contacts, Leads, Opportunities, Revenue Lines, Activities, Assets, Items, Product Group` and ask exactly: `No Prior publish was performed, Please provide your confirmation to proceed with full publish of these OOTB objects`. Perform publish-status preflight before this combined confirmation. On Yes, use `Account, Contact, Lead, Opportunity, Revenue, Activity, Asset, Product, CRMProductGroup` as entities without `publishType`. On No, collect and validate a replacement list, then use its mapped entities without `publishType`. On any other error, stop. |
| 9 | Treat only `WAIT`, `RUNNING`, and `PAUSED` as concurrency blockers. Treat HTTP 404 with exactly `{"Error":"Cannot parse null string"}` as an expected no-prior-publish pass. A terminal status, or a selection whose objects are already enabled, must continue to the combined confirmation; never suppress the requested publish as redundant. |
| 9 | On any other HTTP status, disclose status and redacted message and stop |

## Preview Pattern

| Step | Requirement |
|---|---|
| 1 | Confirm environment identity, authentication, final object list, and concurrency |
| 2 | Run `python3 scripts/validate_publish_contract.py --json` to load and semantically validate the bundled `ora_publish_contract.json`. Require the declared contract ID, POST method, publish path, JSON content type, `Preference: transient`, and both Partial and Full Publish payload schemas; stop only if this deterministic validation fails. |
| 3 | Before mapping, compare environment, endpoint, normalized entities, and the validated contract binding with any current mapping metadata. On any change or unverifiable match, archive the old artifacts when supported, remove their executable-current names, persist a non-executable invalidation record, and revoke prior preview/approval |
| 4 | For explicit Full Publish, determine the final entity selection from the retain-current-active-objects decision before mapping. Generate and persist new mapped request JSON and mapping report bound to the current fingerprints; publish them under executable-current names only after mapping succeeds |
| 5 | Render one Combined Publish Confirmation Table: current active objects, Additional Objects Added, final publish selection, environment, partial/full publish type, object list/count, action, expected response, and that the validated immutable Data Loader source is approved by this confirmation. Do not include a statement about Fusion-mandated internal objects. For the new-environment fallback, state that objects cannot be validated and the entire environment will be initialized. |
| 6 | Show that the operation changes Adaptive Search configuration and submits an ESS-backed partial or full publish through Data Loader REST import |

## Mapped Artifact Lifecycle

| Situation | Required Action |
|---|---|
| No prior mapped request exists | Continue to contract validation and mapping |
| Environment, endpoint, normalized entity list, or validated contract binding changed | Immediately revoke the old preview and approval; archive the old payload/report under versioned history when supported; remove executable `current` payload/report names; write an invalidation record without a request body |
| Prior metadata is missing or cannot prove an exact fingerprint match | Treat it as changed and invalidate it fail-closed |
| Contract or preflight blocks regeneration | Keep only the invalidation record in current state; do not restore or display the archived body as the current proposal |
| New mapping succeeds | Atomically publish the new payload, mapping report, binding metadata, and fingerprints as current |
| Final approval is requested | Require fingerprints matching the current payload and mapping metadata exactly |

## Live Pattern

### Standalone

| Step | Requirement |
|---|---|
| 1 | Use the combined confirmation as the mandatory Data Loader immutable-artifact approval bound to environment, endpoint, required fields, final entity list, and mapped source |
| 2 | Initiate one Data Loader REST import; do not retry automatically |
| 3 | Display the returned `ContentId` as `Data Loader Content ID` and `RequestId` as `Data Loader Request ID`. State that neither is an Adaptive Search Publish Job ID. |
| 4 | End the submission response without automatic polling or a Publish Job ID. |
| 5 | If the user later asks for current publish status, follow the Core status handoff for the exact stored Data Loader Request ID and apply its bound result. Only on Data Loader success, make one latest-status GET and report its returned Adaptive Search `jobId`, `publishSource`, `mmuuid`, and status. |

### Fusion ABO dependent invocation

For the separate initial Full Publish phase, use
[ora_abo_initialization.md](ora_abo_initialization.md): ordered nine-object JSON
cell, blank optional `publishType`, same four operation/header values, matching
consumed initialization permission and independent Core approval. Evaluate
this Full row from validated source records instead of the selective row below.
Its distinct exact-job status requires fresh catalog presence and never allows
ESS. The following flow describes normal Partial Publish after initialization.

The companion executor supplies all six mapped values for Core's workbook generation:
`RestAction=POST`, canonical `entities`, `publishType=selective`,
`Content-Type=application/json`, `REST-Framework-Version=9`, and
`Preference=transient`. The existing body serializer handles only `entities`
and `publishType`; the executor adds the operation and header columns, not
extra REST-body properties. Core populates only supplied values; sample
placeholders are not defaults for omitted population fields. Validate the
embedded API contract and complete input row before workbook generation.

The parent invokes `prepare_publish_load` after verified CPQ completion and
separate preparation permission. The companion returns fixed values in a
versioned Core workbook handoff, accepts the confirmed workbook path, and
returns the 26.10 persisted-preflight/Task Hook handoff. The returned Task Hook resources
must be evaluated against the exact six-field row, predecessor, target and
current-stage evidence. Initial Full uses its separately authorized nine-object
row and blank publishType. Do not validate OOTB names against a missing catalog.

Core creates the bound Task Hook preview; the coordinator's `build-load-preview`
accepts its structured result only after checking the source, archive and context.
Display the optional workbook link once, then Core's complete approval Markdown
verbatim. The frozen archive is the pending load; workbook edits do not alter it.
After a later independent load approval, `submit-data-load` reserves intent and
returns the Core submit handoff. Core approves and verifies the archive, uses its
unchanged taskValidationEnvelope, then submits the exact saved bytes once through
approved-preflight-envelope. `complete-data-load` accepts its bound receipt. No source rebuild,
retained process, repeated approval or automatic mutation retry is permitted.

Return Core's receipt and opaque publish_operation_id, retaining private
correlation. Pause for the explicit load-status request. Pending stops; verified
exact loader success permits post-loader job discovery/pinning and exact-job
checks. Subsequent ticks never query Data Loader. The parent repeats at 15 seconds
only on the current monitoring choice; check-later saves/stops. Final Partial
readiness requires both entities enabled; initialization only establishes catalog
presence and never authorizes ESS. Missing/changed/expired artifacts require
fresh validation/approval before submission; uncertain intent permits only status
or reconciliation. Confirmed legacy operations remain readable without replay.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AS.ENTITY.GET | decision | 10 | rest_get | populated->AS.ENTITY.FILTER;new_environment->AS.PUBLISH.PREFLIGHT;error->AS.ERROR.HANDLE | none | stop | Every requested-object Adaptive Search publish, including CPQ-only and explicit Full Publish requests; a recognized CPQ alias bypasses catalog validation but not the new-environment check |
| AS.FULL.SELECTION | decision | 35 | selection_decision | retain->AS.PUBLISH.PREFLIGHT;requested_only->AS.PUBLISH.PREFLIGHT | AS.ENTITY.REVIEW | stop | For explicit Full Publish with a nonempty Entities response, show active and newly requested objects and ask whether to retain active objects with requested objects; this is not live approval |
| AS.ENTITY.CONFIRM | decision | 40 | approval_gate | confirmed->AS.PUBLISH.PREFLIGHT;revise->AS.END.REVISION_REQUIRED | AS.ENTITY.REVIEW | stop | Legacy compatibility node retained for registry continuity; it has no inbound transition in the single-confirmation flow and must not render a user prompt |
| AS.NEW_ENV.CONFIRM | decision | 45 | approval_gate | confirmed->AS.PUBLISH.PREFLIGHT;rejected->AS.END.REJECTED | AS.ENTITY.GET | stop | Legacy compatibility node retained for registry continuity; it has no inbound transition in the single-confirmation flow and must not render a user prompt |
| AS.PUBLISH.PREFLIGHT | step | 50 | rest_get | ready->AS.REST.CONTRACT;blocked->AS.END.BLOCKED | none | stop | The requested list is valid, the user explicitly requested Full Publish, or a null or empty Entities result selected the new-environment full-publish path |
| AS.REST.CONTRACT | step | 60 | rest_describe_attribute_cache | resolved->AS.REST.PAYLOAD;blocked->AS.END.BLOCKED | none | stop | Semantically validate the bundled publish contract before payload mapping; this local node performs no Fusion describe request |
| AS.REST.PAYLOAD | step | 70 | rest_payload_contract | mapped->AS.REST.PREVIEW;blocked->AS.END.BLOCKED | AS.REST.CONTRACT | stop | Approved entity input and current contract are available |
| AS.REST.PREVIEW | decision | 80 | preview_gate | approved->AS.REST.APPROVAL;rejected->AS.END.REJECTED | AS.REST.PAYLOAD | stop | Assemble the combined confirmation content internally; do not render a separate user-facing preview |
| AS.REST.APPROVAL | decision | 90 | approval_gate | approved->AS.DATALOADER.RELEASE;rejected->AS.END.REJECTED | AS.REST.PREVIEW | stop | Render the one combined confirmation table after immutable source validation; its approval authorizes both selection and the exact Data Loader source |
| AS.REST.PUBLISH | step | 100 | rest_post | accepted->AS.END.SUBMITTED;failed->AS.ERROR.HANDLE | AS.REST.APPROVAL | stop | Legacy compatibility node retained for registry continuity. It has no inbound transition and must not execute. |
| AS.DATALOADER.RELEASE | step | 105 | execution_gate | accepted->AS.END.SUBMITTED;failed->AS.ERROR.HANDLE | AS.REST.APPROVAL | stop | Submit the standalone approved immutable source through the standard `core.data-loader` import flow for registered business object `publish`. The shared Data Loader upload and initiation flow is sufficient: Fusion resolves the registered business object's REST mapping. Do not require, discover, or block on a publish-specific release adapter. |
| AS.END.SUBMITTED | terminal | 110 | terminal | none | AS.DATALOADER.RELEASE | stop | Standalone Data Loader initiation returned ContentId and RequestId; display them with unambiguous Data Loader labels and do not poll |
| AS.COMPANION.PREPARE | step | 200 | execution_gate | prepared->AS.COMPANION.APPROVAL;blocked->AS.END.BLOCKED | none | stop | Fusion ABO only: verified CPQ predecessor; validate embedded API contract and all six mapped loader fields; follow Core workbook and persisted-preflight handoffs and validate rows through ordered task rules |
| AS.COMPANION.APPROVAL | decision | 210 | approval_gate | valid->AS.COMPANION.SUBMIT;invalid->AS.END.BLOCKED | AS.COMPANION.PREPARE | stop | Separate current Core preview approval on the exact validated archive |
| AS.COMPANION.SUBMIT | step | 220 | execution_gate | submitted->AS.COMPANION.SUBMITTED;failed->AS.ERROR.HANDLE;indeterminate->AS.END.FAILED | AS.COMPANION.APPROVAL | stop | Fusion ABO only: submit the prepared source exactly once through Data Loader and keep Data Loader IDs private |
| AS.COMPANION.SUBMITTED | terminal | 230 | terminal | none | AS.COMPANION.SUBMIT | stop | Return opaque `publish_operation_id` and `SUBMITTED`; it is not an Adaptive Search job result |
| AS.COMPANION.LOAD_STATUS | step | 235 | companion_operation | succeeded->AS.COMPANION.STATUS;pending->AS.COMPANION.SUBMITTED;failed->AS.END.FAILED | AS.COMPANION.SUBMITTED | stop | Explicit user loader-status request only; pending stops |
| AS.COMPANION.STATUS | step | 240 | companion_operation | pending->AS.COMPANION.STATUS;succeeded->AS.COMPANION.SUCCEEDED;failed->AS.END.FAILED;indeterminate->AS.END.FAILED | AS.COMPANION.LOAD_STATUS | stop | Verified exact loader success; one discovery/pinned-job tick; parent repeats at 15 seconds only on current monitoring choice, no loader reads |
| AS.COMPANION.SUCCEEDED | terminal | 250 | terminal | none | AS.COMPANION.STATUS | stop | Return final success and exact entity-readiness evidence to Fusion ABO; never submit ESS here |
| AS.END.BLOCKED | terminal | 150 | terminal | none | none | stop | Preflight, embedded-contract validation, or payload mapping is blocked |
| AS.END.REVISION_REQUIRED | terminal | 160 | terminal | none | AS.ENTITY.CONFIRM | stop | User declined the combined confirmation; collect a new list and start another review iteration |
| AS.END.CORRECTION_REQUIRED | terminal | 165 | terminal | none | AS.ENTITY.VALIDATE_REQUEST | stop | Invalid names and nearest display-name suggestions were displayed; collect and validate a corrected list before preflight |
| AS.END.REJECTED | terminal | 170 | terminal | none | none | stop | Final preview or live approval is rejected |
