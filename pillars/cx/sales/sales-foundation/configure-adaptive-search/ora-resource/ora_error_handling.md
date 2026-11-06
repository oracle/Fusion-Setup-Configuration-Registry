# Adaptive Search Publish Error Handling

For ABO only, the known missing/null/empty catalog conditions return the safe
blocker to the parent for separate Full Publish preparation approval, not a
repeated selective proposal or automatic publish. Follow
[ora_abo_initialization.md](ora_abo_initialization.md). Other failures stop;
uncertain intent and failed initialization require exact reconciliation, never
automatic retry or ESS. Standalone fallback/approval behavior is unchanged.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Empty object list | Classify as input_validation and stop before preview |
| Recognized CPQ alias is not returned by Entities | Do not classify it as invalid; resolve it directly to `oraclecpqo_transaction` and `oraclecpqo_transactionLine` because a newly provisioned custom CPQ environment may not expose those entities in its active metamodel. A null or empty Entities response still selects the new-environment OOTB Full Publish path. |
| Requested names absent from the isDocument=true Entities response localizedName set | Classify as object_name_correction, display invalid names and up to three nearest display-name suggestions for each, ask whether a suggestion is required, and compare again; do not POST a partial list or expose the full catalog |
| localizedName maps to multiple entityName values | Classify as object_name_disambiguation, show numbered `Display Name (entityName)` choices, and require an exact selection before continuing |
| Entities GET returns HTTP 400 with parsed JSON body exactly `{"Error":"Could not find active meta model"}` | Classify the final status and body independently of known client authentication-retry diagnostics, then select new_environment_full_publish and display the OOTB Full Publish confirmation; do not use substring matching or attempt object-name validation |
| Entities GET returns HTTP 400 with any other body, or any other non-200 status | Classify the failure, show HTTP status and a safe Oracle business message parsed from allowlisted scalar JSON fields, and stop; never display the raw body, HTML, headers, credentials or stack trace |
| Entities response is null, has null items, or has an empty items array | Classify as new_environment_full_publish; display the OOTB confirmation, then prepare its internal-entity array without `publishType` on Yes or collect a replacement list on No |
| Authentication fails | Classify as auth_expired_or_invalid; refresh a managed cache once only when supported |
| User lacks publish privilege | Classify as authorization_or_privilege and stop |
| Another publish is active, including ZCA-210166 | Classify as approval_blocker or Fusion concurrency conflict and stop without retry |
| publishStatus GET returns HTTP 404 with exactly `{"Error":"Cannot parse null string"}` | Classify as no_prior_publish and continue through payload mapping and the combined confirmation; this is expected when the Entities GET established a new environment. |
| publishStatus GET returns another HTTP error or a malformed 404 body | Classify as fusion_api_error, show the status and redacted message, and stop; do not submit. |
| Publish POST reports that an active sandbox prevents metamodel synchronization | Classify as fusion_api_error, report it, require sandbox resolution, and do not retry automatically |
| Publish POST returns Invalid Preference Parameter | Verify the embedded contract requires `Preference: transient`, invalidate the prior approval if the header binding changed, regenerate the preview, and require explicit approval before one new POST |
| POST response is ambiguous or loses connection | Classify as transport_or_environment; check latest status read-only before any new submission and never retry POST automatically |
| Status becomes ERROR | Classify as process_failed; retain a redacted message, jobId, mmuuid, and recommended action |
| User-requested one-time status check returns CANCELLED | Record and report the terminal cancelled result |
| User-requested current status finds a failed or unsuccessful Data Loader request | Report the Data Loader status and safe error details; do not call Adaptive Search publishStatus, retry the load, or infer a Publish Job ID |
| Fusion ABO Core preflight lost/expired/cancelled before approval | Stop; fresh validation and approval. Only a current unchanged Core preview and immutable archive can be approved. |
| Fusion ABO parent provenance is missing or mismatched | Stop before companion preflight; require v2 workflow identity and verified CPQ predecessor matching the exact project/target/fixed pair. Live Core approval is separate. |
| Fusion ABO status finds a pending load or job | Load pending stops. Verified-load job pending offers 15-second monitoring or checking later; repeat only on current consent. Later status checks once. |
| Fusion ABO status finds failed/unknown load, failed/cancelled job, missing readiness or mismatched job | Return blocked/indeterminate without ESS or republish. |
| Fusion ABO post-loader discovery still returns the fresh pre-submit job | Return pending and repeat only the same GET-only status operation; do not pin the stale job, submit ESS, or re-publish |
| Fusion ABO restart occurs after a submission | Reopen only the persisted exact `publish_operation_id` record and use GET-only status reads. If the child has not yet pinned a job ID, it repeats only the approved post-loader discovery after its private Data Loader success; once pinned, it uses only the exact-job GET. Missing fresh baseline or invalid private state is indeterminate and never causes another submission. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Request shape or entity selection is invalid | Correct input and preview again |
| authorization_or_privilege | Fusion rejects publish authorization | Correct roles or use an approved account |
| transport_or_environment | Network or environment identity prevents a reliable result | Diagnose safely; use read-only status before considering another POST |
| fusion_api_error | Fusion returns a non-process REST error | Record status, endpoint path, safe response summary, and ECID when present |
| process_failed | Job reaches ERROR | Review the redacted message or approved ESS diagnostics |
| approval_blocker | Live execution, retry, or conflict resolution needs approval | Stop and request the missing decision |
| new_environment_full_publish | Entities lookup establishes that the target is new | Preview the full-publish impact and require explicit approval |
| entity_list_revision | User declines the displayed active/requested comparison | Collect a revised nonempty list and repeat the review iteration |
| object_name_correction | One or more requested names are absent from all nonempty localizedName values in the isDocument=true Entities response | Show invalid names and up to three nearest display-name suggestions for each, collect corrections, and compare the complete list again |
| object_name_disambiguation | A display name maps to multiple internal entityName values | Show internal names in parentheses for those duplicate choices and require the user to select one |
| catalog_mismatch | A display label or its internal entityName is missing | Stop and report that the object catalog entry is incomplete |
| indeterminate | A post-submit state or exact correlation cannot be safely proven | Persist redacted evidence and do not create a new submission automatically |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Preview | Environment, publish type, requested objects, object count, internal-object behavior, action, and expected response |
| Object review | Current active objects, requested objects, validation result, and whether confirmation is required |
| Submission | Data Loader Content ID, Data Loader Request ID, an explicit statement that neither is the Adaptive Search Publish Job ID, and that automatic polling is not performed |
| User-requested current status after Data Loader success | Data Loader status followed by Adaptive Search Publish Job ID, mmuuid when useful, initial status, and publish source |
| Fusion ABO dependent submission/status | Relay Core receipt, return opaque status and show the explicit load-status next action; no additional mutation approval. |
| Failure | Functional stage, failed or blocked result, safe Fusion message, and recommended action |

Apply `ora_user_presentation.md` to normal administrator output. Keep endpoint paths, failure classes, fingerprints, contract identifiers, and artifact references internal unless the user explicitly requests technical diagnostics; always show a safe functional stage, result, message, and recommended action.

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Credential or Authorization header is present | Do not print, persist, or commit it |
| Empty object list | Do not submit the publish |
| Some requested names are invalid | Do not discard them silently, publish only the valid subset, or continue without correction |
| Entities GET returns an unexpected status | Do not continue to publishStatus, preview, or POST |
| Existing job is nonterminal | Do not submit a concurrent publish |
| Live approval is missing or stale | Do not submit the POST |
| POST outcome is ambiguous | Do not automatically retry |
| Contract, payload, or mapping report is missing or stale | Do not preview or execute |
| A mapping input changes or prior binding metadata is unverifiable | Do not retain the old body as current; archive it when supported, remove executable-current names, persist an invalidation record, and revoke prior preview/approval |
| Fusion ABO dependent status is pending | No automatic loader polling, new operation or ESS. Job-only monitoring requires verified load success and current monitoring choice; check-later stops with saved checkpoint. |
| Fusion ABO dependent operation cannot complete safe post-loader discovery or exact-job validation | Do not submit another Data Loader import, use an invalid response, or permit ESS; return pending only while the approved discovery response has not yet supplied a new job ID |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AS.ERROR.HANDLE | decision | 180 | error_handler | failed->AS.END.FAILED | none | stop | Entity discovery, REST submission, or publish job fails |
| AS.END.FAILED | terminal | 190 | terminal | none | AS.ERROR.HANDLE | stop | Failure is terminal and diagnostics are captured |
