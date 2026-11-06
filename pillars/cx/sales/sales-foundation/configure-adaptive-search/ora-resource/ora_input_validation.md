# Adaptive Search Publish Input Validation

ABO initialization uses [ora_abo_initialization.md](ora_abo_initialization.md),
not the normal selective-pair row/status rules below. Require its nine-object
Full scope, blank workbook `publishType`, four exact operation/header values,
known catalog blocker, distinct receipt and independent Core Task Hook approval.
Only presence of the ABO pair after successful initialization is needed to
propose Partial Publish; ESS still requires the later pair enabled.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve |
|---|---|---|---|
| Target environment | environment | Stop | Ask for the non-production Fusion environment intended for the publish |
| Publish selection | objects | Stop | Supply at least one exact Adaptive Search business object display name |
| Standalone live authorization | live_approval | Stop before POST | Present the final preview and obtain explicit approval |
| Fusion ABO parent provenance | V2 workflow identity and verified CPQ predecessor | Stop before companion preflight | Match exact project/target/fixed pair; Core Task Hook approval is separate. |

## Dependency-Aware Validation

| Applies When | Result | Next Action |
|---|---|---|
| Latest publish status is WAIT, READY, RUNNING, or PAUSED | Blocked | Wait for or resolve the existing publish; do not submit another POST |
| Entities response is null, `items` is null, or `items` is empty | New environment | Continue to preflight and payload mapping, then display the defined OOTB object list in the single combined full-publish confirmation |
| Fusion reports a sandbox conflict from the publish POST | Fusion API error | Report the response and require sandbox resolution; do not retry automatically |
| Entities HTTP 200 response is unavailable or malformed | Blocked for object-name comparison | Follow the documented HTTP branch; never invent a valid-choice list |
| All preflight checks pass | Ready | Generate the mapped request artifact and preview it |
| Environment, endpoint, normalized entities, or validated contract binding differs from current mapping metadata | Mapping invalidated | Archive the old mapping when supported, remove its executable-current designation, write an invalidation record, revoke its preview and approval, then regenerate the mapping after semantic contract validation |

## Field Validation

| Check | What Happens |
|---|---|
| entities must be a nonempty array of nonempty strings | Invalid input stops before side effects |
| Requested object is `Quote`, `Quotes`, `Standard Quotes`, `Standard Quote Process`, `oraclecpqo`, `oraclecpqo_transaction`, or `oraclecpqo_transactionLine` (case-insensitive) | Resolve it directly to both `oraclecpqo_transaction` and `oraclecpqo_transactionLine`; skip Entities validation for those two CPQ entities because a newly provisioned custom CPQ environment may not yet expose them in its active metamodel |
| Object names must exactly match a nonempty `localizedName` value returned by the `isDocument=true` Entities HTTP 200 response | Report all unmatched values, show up to three nearest display-name suggestions for each invalid value, ask whether a suggestion is required, replace the requested list, and compare again; do not show the full catalog or use `isEnabled` to determine validity |
| HTTP 200 Entities response has a nonempty items array | Validate each non-CPQ requested name and construct a selective payload with its mapped entities plus any direct CPQ entities and `publishType: selective` |
| Explicit Full Publish with a nonempty items array | After validation, require the retain-current-active-objects decision before preflight: Yes creates an ordered, deduplicated active-plus-requested selection; No uses requested objects only. Neither response is approval to submit. |
| Entities returns HTTP 400 `Could not find active meta model`, a response is null, has `items: null`, or has `items: []` | Classify as a new environment; on OOTB confirmation Yes, prepare the defined OOTB internal-entity array without `publishType`; on No, collect and validate a replacement list |
| Each selected display name must resolve to one nonempty `entityName` | For duplicate display names, show numbered `Display Name (entityName)` choices and require an exact selection; missing mappings are a catalog mismatch |
| Current-active display entries must satisfy isEnabled=true | The request already limits results to isDocument=true; apply isEnabled only to the active display and never to object-name validation |
| Every requested object is a recognized CPQ alias and Entities is nonempty | Skip catalog validation for the CPQ entities, construct the payload from `oraclecpqo_transaction` and `oraclecpqo_transactionLine`, then continue to publish-status preflight |
| Every requested object is a recognized CPQ alias and Entities is null or empty | Classify the target as a new environment and follow the existing OOTB Full Publish confirmation and payload path |
| A current exact Fusion ABO `workflow_authorization` accompanies `Consolidated Asset(s)` / `ConsolidatedAsset` and `Serialized Asset(s)` / `SerializedAsset` | Resolve only that fixed pair to `ConsolidatedAsset` and `SerializedAsset` after the Entities response confirms both are current document entities; do not treat these aliases as a general bypass of entity validation |
| A Fusion ABO dependent submit lacks exact v2 identity, verified CPQ predecessor or current Core load approval | Block before submission; require the current bound Core preview, ordered task results, and explicit load approval; never prepare a replacement automatically. |
| Fusion ABO companion input or Core validated row lacks exact `RestAction=POST`, canonical approval-bound `entities`, `publishType=selective`, `Content-Type=application/json`, `REST-Framework-Version=9`, or `Preference=transient` | Input validation blocker before approval. Operation/header fields belong to the Data Loader row, not the REST body. Correct source generation and validate a fresh preflight without reloading verified CPQ; after possible submission use reconciliation only. |
| A Fusion ABO dependent status request lacks the same opaque `publish_operation_id` identity | Return indeterminate; never accept a caller-supplied Data Loader Request ID or submit again. The child alone performs the approved post-loader discovery and later exact-job status reads. |

## Object Name Correction

| Situation | What Happens |
|---|---|
| One or more requested names are absent from the returned localizedName set | Display the invalid names and up to three nearest localizedName suggestions for each; retain no implicit partial approval |
| User supplies corrected names | Build one revised nonempty requested list and compare every name with the same current Entities response |
| Corrected list still contains invalid names | Repeat the correction iteration and show the remaining invalid names |
| Corrected list is fully valid | Render the corrected resolved list, then continue to preflight and payload mapping; obtain the only confirmation in the combined final review |
| User declines or supplies an empty corrected list | Stop with correction_required and perform no publish POST |
| A display name matches multiple objects | Show those choices as `Display Name (entityName)`, require an exact disambiguated selection, and map the chosen internal name to the payload |
