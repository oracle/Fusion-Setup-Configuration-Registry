# Adaptive Search Publish Input Intake

The ABO-only initial Full Publish input is separately defined in
[ora_abo_initialization.md](ora_abo_initialization.md): known catalog blocker,
consumed parent preparation permission, fixed nine objects and `afi_` identity.
The fixed-pair companion inputs below apply only to normal Partial Publish.
Standalone input/approval behavior is unchanged.

## Accepted Input Formats

| Input Format | What Must Be Provided | Applies To |
|---|---|---|
| JSON object | environment, requested publish mode, and entities | Preview and live publish |
| Interactive values | Explicit environment and one or more exact Adaptive Search object display names for Partial or explicit Full Publish | Guided execution |

When object display names are missing, ask exactly: `Which business objects do you want to publish? Provide the object display names.`

## Dependency Inputs

| Field | Mandatory | Purpose | Send in Request Body? | Lookup Rule |
|---|---|---|---|---|
| environment | Yes | Identifies the intended Fusion target | No | Confirm the target before preview |
| entities | Conditional | Internal REST body field for a selected-object publish | Yes, for Partial and selected-object Full Publish | Validate non-CPQ user input against nonempty `localizedName` values, then map each display name to its corresponding `entityName`; recognized CPQ aliases add `oraclecpqo_transaction` and `oraclecpqo_transactionLine` directly before `publishType: selective` for Partial Publish |
| live_approval | Conditional | Authorizes the previewed selective or new-environment full publish | No | Must match the previewed environment, publish type, and payload |
| retain_current_active_objects | Conditional | Explicit-Full-Publish selection decision | No | After a nonempty Entities response, Yes retains active objects in the final selection; No uses only requested objects; this is not live approval |
| entity_selection_confirmation | Conditional | Confirms the requested list after active objects are displayed | No | Required only after Entities HTTP 200 with a nonempty `items` array; a No response collects a revised list |
| workflow_context | Conditional | Non-executable Fusion ABO parent provenance | No | Exact v2 project/target/fixed pair and verified CPQ predecessor; not approval. |
| handover_version | Conditional | Live ABO handover version | No | Must be 2.0; the current preparation and Core approval bindings remain distinct. |
| publish_operation_id | Conditional | Opaque public key for a companion status request | No | Required only by `get_partial_publish_status`; it must match a persisted companion operation owned by the same project and target. Never accept a Data Loader Request ID in its place. |

## Body Field Rules

| Situation | What Happens |
|---|---|
| entities is absent, empty, or contains blank values for Partial Publish | Stop before preview |
| User explicitly requests Full Publish | Collect object display names and validate them against a nonempty Entities response, then use the mapped internal-entity array without `publishType` |
| Explicit Full Publish has a nonempty Entities response | Show current active and newly requested display names, then require the retain-current-active-objects decision before preflight and mapping |
| New environment and user confirms the OOTB list | Use the defined OOTB internal-entity array without `publishType`; do not validate the OOTB objects |
| New environment and user declines the OOTB list | Collect a replacement object list, call the Entities endpoint again, validate it, then use the mapped internal-entity array without `publishType` |
| Duplicate object display names are supplied | Normalize duplicates while preserving first-seen order and disclose the normalized list |
| Input contains `Quote`, `Quotes`, `Standard Quotes`, `Standard Quote Process`, `oraclecpqo`, `oraclecpqo_transaction`, or `oraclecpqo_transactionLine` | Treat the match case-insensitively, add both direct CPQ entity names once, and skip Entities validation for them; still call Entities once to identify a null or empty new environment, then validate only any remaining requested objects when the response is nonempty |
| Optional fields outside the approved contract are supplied | Reject them before preview |
| Entities returns HTTP 400 `Could not find active meta model`, the response is null, `items` is null, or `items` is empty | Treat as a new environment; present the defined OOTB list before preparing its full-publish entity-array payload |
| Credentials are supplied in input | Use them only through the approved runtime authentication service; never print or persist them |
| Fusion ABO invokes preparation | Require verified CPQ success; prepare fixed values and follow Core workbook and persisted-preflight/Task Hook handoffs to freeze an immutable archive. |
| Fusion ABO invokes submission | Contextual approval of current Core preview on the exact validated archive; reserve once, return opaque operation and pause. |
| Fusion ABO invokes status | Exact opaque operation; Data Loader only on explicit user request. After verified success, one job tick; parent repeats only on current 15-second monitoring choice. Check-later stops. |
