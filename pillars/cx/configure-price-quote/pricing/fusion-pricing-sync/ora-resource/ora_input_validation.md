# Input Validation

## Sync Direction From Prompt

Read the user's latest request and relevant conversation context before any
live metadata lookup, DAT generation, or Data Loader preparation. Identify the
source and target from explicit labels (`source: Fusion`, `target: CPQ`) or
directional wording (`Fusion to CPQ`, `sync CPQ from Fusion`). Normalize Oracle
Fusion/Fusion Cloud to `Fusion` and Oracle CPQ/Configure Price Quote to `CPQ`.
Do not infer direction from which system is mentioned first unless a direction
word or explicit role identifies it. Record the detected source and target in
the validation result without storing sensitive prompt content.
"Sync Fusion to CPQ" explicitly selects the supported direction. "Setup Fusion
Pricing" selects this task with direction omitted, so apply the supported
default. Do not require the user to say "pricing reference data" in the prompt.

| Prompt result | Response | Workflow gate |
|---|---|---|
| Source Fusion, target CPQ | State that Fusion pricing reference data is being synced; include the detected direction when helpful. | Pass direction validation; continue preflight. |
| Source or target omitted, and every stated role agrees with Fusion as source and CPQ as target | Recommend: "I'll sync Fusion pricing reference data to CPQ." | Use the supported direction for subsequent preflight; the recommendation is not Data Loader approval. |
| Source CPQ, target Fusion, including "sync CPQ to Fusion" | Explain that CPQ-to-Fusion is the wrong flow for this skill. Ask: "This skill syncs from Fusion to CPQ. Would you like to proceed with Fusion as the source and CPQ as the target?" | Stop before live steps until the user explicitly confirms the corrected direction. Do not silently reverse the request. |
| An explicitly stated source is CPQ or an explicitly stated target is Fusion, even if the other role is omitted | Explain that the stated role conflicts with this skill's direction and offer Fusion to CPQ. | Stop before live steps until the user explicitly confirms the corrected direction. |
| Conflicting or ambiguous source/target wording | Explain the conflicting directions and ask the user to specify Fusion as source and CPQ as target. | Stop before live steps until the direction is clear. |
| Explicit source or target names a different system | Explain that this skill supports only Fusion to CPQ and offer that direction. | Stop before live steps until the user explicitly confirms the supported direction. |

Direction confirmation is distinct from the later `core.data-loader` approval
for the exact immutable archive. Do not initiate a reverse sync through this
skill.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Load source | A validated immutable CpqChargeSetSync archive and core Data Loader preflight | Stop before UCM upload | Generate the internal DAT through core.data-loader, then validate every generated value against live metadata and package it through the same core workflow. | During step 2 | resolve_loader_business_object |
| Load approval | A current core Data Loader approval for the exact CpqChargeSetSync archive | Stop before UCM upload | Complete the core approval workflow | Before initiation |  |

## Field Validation

The pillar developer's supplied operation contract is POST with no business
payload. Apply these checks to the immutable source prepared by core.data-loader;
do not change the approved artifact. Live metadata and core source
validation still govern registered attributes, datatype limits, and schema.

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Trigger operation | Require POST when RestAction is present. PATCH, DELETE, or multiple trigger records block the preview. Generate with explicit operation create. | The DAT contains a trigger record |  |
| Optional chargeId | Accept omission or a blank optional value when core validation permits it. If populated, require an integer within live metadata limits; the specific value has no business meaning. A generic integer sample is valid and requires no charge existence or uniqueness lookup. | chargeId is present in the generated source |  |
| No business payload | Do not require charge-set rows, mappings, or a user-supplied chargeId. The DAT is a loader trigger; REST routing with DAT is supported by this declared workflow when core metadata and source checks pass. | Before the approval preview |  |
| Metadata agreement | Stop on an actual missing registration/template, schema error, or metadata contract contradicting POST and optional integer chargeId. Identify the exact failing stage; do not infer a route conflict merely from REST and DAT. | Core metadata or immutable-source validation fails | resolve_loader_business_object |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| CpqChargeSetSync metadata, POST trigger DAT, immutable ZIP, and Task Hook checks pass | Ready for approval | Show the core Data Loader approval report for the exact immutable archive. |  |
| Data Loader approval is missing or invalid | Blocked | Do not upload or initiate CpqChargeSetSync |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DATA_LOADER_SYNC.VALIDATE_CHARGE_SET_LOAD | step | 20 | validate_input | valid->DATA_LOADER_SYNC.SUBMIT_CHARGE_SET_LOAD;invalid->DATA_LOADER_SYNC.HANDLE_ISSUE | DATA_LOADER_SYNC.RESOLVE_CHARGE_SET | stop | Validate the single POST trigger, optional integer chargeId, immutable ZIP, and task context through core.data-loader; do not upload before approval. |
