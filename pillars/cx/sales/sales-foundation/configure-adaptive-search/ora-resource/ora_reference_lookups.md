# Adaptive Search Publish Reference Lookups

ABO initialization reuses these read-only catalog/concurrency/exact-job lookup
services with its separate receipt and status entry point; see
[ora_abo_initialization.md](ora_abo_initialization.md). After its successful
exact job, require fresh ABO pair catalog presence, not enabled state.
Initialization remains ineligible for ESS; Partial Publish rules are unchanged.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| Document objects catalog lookup | Before publish-status preflight for every request, including CPQ-only requests | Authenticated Fusion environment | /crmRestApi/searchResources/latest/entities?language=en&limit=-1&isDocument=true | items.localizedName, items.entityName, items.isDocument, items.isEnabled | A nonempty items array validates non-CPQ requested display names and maps them for a Partial Publish payload; recognized CPQ aliases contribute both direct CPQ entities without lookup validation; HTTP 400 `Could not find active meta model`, a null response, null items, or an empty items array establishes a new environment and uses the defined OOTB full-publish entity array after confirmation | valid object display names, active object display names, internal payload names, and publish mode | Other HTTP 400 responses and other errors stop; duplicate labels require user disambiguation |
| Adaptive Search latest-status lookup | After entity validation and before the combined confirmation | Authenticated Fusion environment | /crmRestApi/searchResources/latest/publishStatus | mmuuid, jobId, status, publishSource, submittedBy, message | Use the single latest-publish response; treat HTTP 404 with exactly `{"Error":"Cannot parse null string"}` as no prior publish | latest job and status | Reject any other malformed or ambiguous response |
| Data Loader status lookup | Only when the user explicitly requests the current publish status | Data Loader Request ID returned by accepted initiation | `core.data-loader` exact status handoff | Data set status, counts, and safe errors | Require the exact stored Data Loader Request ID | Data Loader outcome | If the status is not successful, show the Data Loader result and stop; do not query Adaptive Search publishStatus |
| Adaptive Search latest-status lookup after Data Loader success | Immediately after a user-requested Data Loader status lookup reports success | Same-request Data Loader success receipt | /crmRestApi/searchResources/latest/publishStatus | mmuuid, jobId, status, publishSource, submittedBy, message | Use one latest-status response only; do not poll | Publish Job ID, current status, source, and metamodel UUID | Stop if the response is malformed; do not retry or infer another job |
| Fusion ABO private Data Loader status lookup | Only on explicit user status request | Exact private request for the operation | `core.data-loader` exact status handoff | status, counts, errors | Exact project/target/request binding | Terminal evidence | Pending stops; failure/unknown blocks; no automatic retry. |
| Fusion ABO post-loader Adaptive Search job discovery | Only after the private exact Data Loader request succeeds and before a job ID is pinned | Persisted exact operation and fresh pre-submission status baseline | `/crmRestApi/searchResources/latest/publishStatus` | mmuuid, jobId, status, publishSource, submittedBy, message | Require a safe job ID and recognized status, reject the job ID in the fresh pre-submission baseline, persist the new ID privately, and return pending without evaluating ESS | Pinned job ID and normalized pending state | An absent job ID stays pending; malformed or unknown response is terminal indeterminate |
| Fusion ABO exact Adaptive Search status lookup | Only after post-loader job discovery pins a job ID | Persisted exact operation and pinned Adaptive Search job ID | `/crmRestApi/searchResources/latest/publishStatus?jobId={jobId}` | mmuuid, jobId, status, publishSource, submittedBy, message | Require the response job ID to equal the pinned job ID, then use it for every later status read | Normalized child state and final readiness evidence | A mismatched or malformed response is terminal indeterminate; parent checks once unless the user currently chooses bounded 15-second exact-job monitoring. Check-later stops. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Latest status is WAIT, READY, RUNNING, or PAUSED | Block a new publish |
| Latest status is terminal, including SUCCEEDED, ERROR, or CANCELLED | Do not treat it as a no-op, a redundant-publish result, or an authorization to skip the workflow. Continue silently to payload mapping and the combined confirmation. |
| Latest status returns HTTP 404 with exactly `{"Error":"Cannot parse null string"}` | Treat it as an expected no-prior-publish concurrency pass and continue to payload mapping and the combined confirmation. This includes the Entities HTTP 400 `Could not find active meta model` new-environment path. |
| Latest status returns any other HTTP error or malformed response | Stop with the status and redacted error message; do not submit. |
| Every requested object is already enabled | Show it only in Current Active Objects. Keep every validated requested object in the final publish selection and continue to the combined confirmation. |
| Explicit Full Publish with a nonempty catalog | Before preflight, show Current active objects and Newly Requested Objects to enable, then require the retain-current-active-objects decision. Yes makes the final selection the ordered union; No keeps only requested objects. |
| Persisted project state records a prior WAIT or RUNNING submission | Do not treat it as current and do not display it; perform the latest-status lookup only after entity validation |
| Entities lookup returns HTTP 200 with a nonempty items array | Validate non-CPQ requested objects against all returned nonempty localizedName values; map confirmed labels to entityName internally; add both direct CPQ entities when a recognized CPQ alias was supplied; for each direct CPQ entity, use an exact `entityName` match only to obtain its localized presentation name and `isEnabled` active state; use `publishType: selective` |
| Every requested object is a recognized CPQ alias and Entities is nonempty | Use `oraclecpqo_transaction` and `oraclecpqo_transactionLine` directly without catalog validation. Show matching enabled localized names as Current active objects; show disabled or absent direct entities as Additional Objects Added; use exact direct entity names for an absent record and keep the final selection count at two. Continue to publish-status preflight. |
| Every requested object is a recognized CPQ alias and Entities is null or empty | Classify the target as a new environment and follow the defined OOTB Full Publish path |
| Entities response is null, has null items, or has an empty items array | Classify the target as a new environment; do not validate or map the OOTB list, show no active-object list, and prepare the defined OOTB full-publish entity array after confirmation |
| Entities lookup returns HTTP 400 `Could not find active meta model` | Classify the target as a new environment; do not validate or map the OOTB list, show no active-object list, and prepare the defined OOTB full-publish entity array after confirmation |
| Entities lookup returns HTTP 400 other than `Could not find active meta model`, or any other non-200 status | Stop with status and redacted error message |
| Requested names are absent from the isDocument=true response localizedName set | Show all invalid names and up to three nearest returned display-name suggestions for each, collect and validate a corrected list before publish preflight; never show the full catalog or a separate selection review |
| A localizedName maps to multiple entityName values | Show the duplicate choices as `localizedName (entityName)` and require the user to choose one; never guess |
| User explicitly asks to see internal names | Show choices as `localizedName (entityName)` without changing the payload selection |
| Latest status is terminal | Continue preflight without reusing that jobId |
| Explicitly requested job status is WAIT, RUNNING, or PAUSED | Report the nonterminal status once; do not schedule another lookup |
| Explicitly requested job status is SUCCEEDED, ERROR, or CANCELLED | Report and classify the terminal result once |
| User explicitly asks for current publish status and the Data Loader status is successful | Make exactly one latest Adaptive Search publish-status lookup; label its returned jobId as `Adaptive Search Publish Job ID`, never as Data Loader Request ID, and do not schedule another check |
| User explicitly asks for current publish status and the Data Loader status is failed or not successful | Show the Data Loader status and safe errors; do not call Adaptive Search publishStatus or retry the load |
| Status response contains sensitive stack or tenant details | Persist only a redacted diagnostic summary and safe external identifiers |
| Fusion ABO dependent operation is pending | Load pending: explicit next-check prompt and stop. Verified-load job pending: offer 15-second monitoring or check later; later status checks once. Never republish. |
| Fusion ABO dependent operation is terminal | Return final success/failure/blocked/indeterminate evidence to the controller; never submit ESS or another publish |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AS.ENTITY.FILTER | step | 20 | evaluate_result | filtered->AS.ENTITY.VALIDATE_REQUEST;invalid_response->AS.ERROR.HANDLE | AS.ENTITY.GET | stop | Entities GET returned HTTP 200 |
| AS.ENTITY.VALIDATE_REQUEST | decision | 25 | evaluate_result | valid->AS.ENTITY.REVIEW;corrected->AS.ENTITY.REVIEW;invalid->AS.END.CORRECTION_REQUIRED | AS.ENTITY.FILTER | stop | Compare every non-CPQ-alias requested object display name with all nonempty localizedName values returned by the isDocument=true Entities HTTP 200 response, without applying isEnabled; direct CPQ entities are excluded from this comparison; for invalid values suggest up to three nearest matches without displaying the full catalog; require explicit disambiguation when a display name maps to multiple entityName values |
| AS.ENTITY.REVIEW | step | 30 | evaluate_result | displayed->AS.PUBLISH.PREFLIGHT | AS.ENTITY.VALIDATE_REQUEST | stop | Enabled document entities were resolved and requested names are valid; do not ask for confirmation here |
