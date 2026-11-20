# Standard Operations — Errors and Handoff

## Release and evidence boundary

Reviewed 29 October 2026. The [Oracle SCM documentation hub](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/) identifies 26D as current. The 26D overview/setup topics were retrieved; detailed Standard Operations REST pages could be retrieved only in 26C, and the detailed creation guide in 26B. These are retrieval gaps, not proof that newer topics do not exist. Use the cited release for each rule and verify the deployed contract before execution.

Public contract, request-preparation policy and deployment-dependent behavior are distinguished below. Public citations establish only what the linked pages document. No live create/update tests were performed. Keep supplied intent separate from the persisted result; the owning core workflow controls reads, preparation, authorization, writes and result verification.

## Public references

- [26C: Standard Operations endpoints](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/api-manufacturing-standard-operations.html): public create/read/update/delete surface.
- [26C: Create operations](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-standardoperations-post.html): request/response contract.
- [26C: Create resources](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-standardoperations-standardoperationid-child-standardoperationresource-post.html): resource response contract.

## Execution boundary

This graph prepares create/update rules for CUSTOM_MANUFACTURING_STD_OPERATIONS and BO standardOperations. It does not write to Fusion. core.data-loader owns declared preparation/import capabilities and approval. Header, child, nested or extension writes require the owning workflow to support that exact scope; an API path alone is not a route. If child handling is unsupported, stop and report the capability gap rather than flattening it into the header.

The public API also supports DELETE, with server guards; that is not permission or an established deletion route for this preparation graph. Do not infer deletion from omission, use end-dating as deletion, or submit DELETE through a client without an explicit selected workflow. DFF DELETE is disabled. Do not assume a separate ERES/global helper is a CRUD action.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Boolean or numeric attribute conversion failure | Report the exact attribute, submitted value and nested diagnostic. A CountPointOperationFlag error with True text suggests a conversion problem but does not prove the outgoing REST type. Preserve count-point intent; apply the Boolean input normalization and canonical text formatting defined in input validation, then follow normal validation and approval before retry |
| Singleton/simultaneous principal failure | Recognize WIS_WD_OP_RSC_NSIM_NPRIN for principal on a singleton and WIS_WD_RS_PRIN for invalid principal selection in a simultaneous group. Preserve sequences and explain the conflict; do not silently flip an explicitly approved flag |
| Generic loader error with MESSAGE placeholder | Inspect the owning Data Loader workflow's returned object/failed-line diagnostic or error log for the concrete nested message. Do not treat the generic wrapper as the root cause or infer full rollback from failed counters |
| Header duplicate code | Preserve WIS_SO_DUP_CODE and organization context; ask whether reuse/update or another code is intended. No auto-rename or duplicate-existence preflight |
| Organization access/validity | Preserve WIE_REST_AUTH or actual returned validation details; distinguish access denial from invalid organization. Do not use privileged SQL or another environment as fallback |
| Work-center change with resources | Preserve WIS_WD_OP_WC_CHG; request an intended supported correction, never delete children automatically |
| Inactive/date error | Preserve WIS_STD_OPN_INACTIVE_DT or WIS_SO_STD_OP_CODE_INACT and field details; let server evaluate database date/time. Do not assert today is valid |
| Count-point/automatic-transact/default conflict | Preserve WIS_WD_OPER_CP_AT, WIS_SOP_DEF_CP_MUST_BE_YES or WIS_SOP_DEF_AWD_EXISTS. Ask for business correction; no silent flag change |
| Protected code/count-point/type change | Preserve WIS_SO_REF_OP_CODE_UPD, WIS_SO_REF_OP_CP_UPD or WIS_STD_OP_TYPE_NOT_UPDATEABLE; do not collapse their distinct usage scopes |
| Supplier conflict | Preserve WIS_OSP_DETAILS_ERROR, WIS_WSWD_SUP_OPN_NO_RSRCE, WIS_CM_OP_TYP_SUP_INV, WIS_SUP_OPN_COUNT_POINT, WIS_SUP_OP_CP_AT or WIS_REST_STD_OPR_004; identify the actual conflicting inputs |
| Supplier/site or lead-time issue | Preserve WIS_INVALID_SUPPLIER, WIS_REST_STD_OPR_006, WIS_REST_STD_OPR_002 or WIS_REST_STD_OPR_007; request only the indicated correction |
| OSP-item validation error | Preserve WIS_OSP_ITEM_MAND/WIS_OSP_ITEM_CHECK when returned and request the correction indicated by the server |
| Resource amount/association/lookup | Preserve WIS_WD_RSRC_UAV and FND_CMN_* field details; do not reproduce capacity or active-association queries |
| Resource charge/scheduling/principal | Preserve WIS_WD_OP_RES_CTYPE_INVLD2, WIS_WD_UPD_SCHD_NO_TIME_UOM, WIS_WD_HP_DP_CLASS_NMATCH, WIS_WD_RSC_SCHD_N_NTU, WIS_RES_ONCE or WIE_WEWO_OP_PRN_RES1; do not rearrange the requested group automatically |
| Alternate priority/identity/UOM | Preserve WIS_WIS_SO_PRIO_UNIQUE, WIS_WIS_SO_PRIO_POS_INT, WIS_WC_ALT_RSC_SAME_WC_PRM_RSC or FND_CMN_REC_COMB_VALS_EXST; distinguish rank conflict from resource conflict |
| Alternate rate not persisted | Report intended versus returned rate even if HTTP succeeded; do not mark a no-op as applied, substitute a rate, or retry blindly |
| Feature/profile/yield | Preserve RCS:::RCS_OPT_IN_ATTRIBUTE, WIS_WD_OP_YIELD_RANGE, WIS_SD_RES_EQUIPMENTJOBPROFILE, WIS_SD_RES_PROFILE, WIS_SD_RES_JOBEQUIPMENTPROFILE or WIS_WD_RES_EQPPROFILE_INACTIVE; do not auto-enable features |
| Campaign restriction | Preserve WIS_NO_CAMPAIGN_RES_IN_WD_PL or WIE_NO_CAMPAIGN_RES_IN_WD_PL if returned. Primary and alternate enforcement scopes differ; do not claim identical work-order coverage |
| Global/protected deletion | Preserve WIS_STDOP_GLOBAL_CANT_UPD_DEL, WIS_SO_DELETE_CHK or WIS_RESOURCE_VAL_SET_PARAM; no internal-flag bypass, implicit unlink or automatic compensating delete |
| Unexpected system ID on create | Preserve WIE_REST_CMN_UNEXP_ATTRIBUTE if returned and verify the generated identity; preparation should omit the system ID |
| DFF/attachment failure | Preserve segment/context/category and framework error details after redaction; never fill tenant values from guesses |
| Data Loader section, column or parent-key mismatch | Report the exact affected section/column and core validation result. Apply the input contract without silently renaming discriminators, merging distinct DFF IDs, dropping parent context or converting loader controls into product REST fields. A template-only comparison is not proof of successful live metadata retrieval or load readiness |
| Failed, partial or uncertain load requiring retry | Stop blind retry. Through the owning workflow, reconcile the header by original organization/code and any returned resource children before choosing missing/failed operations. A failed aggregate count alone does not prove no records persisted. Normalize supplied Boolean values, resolve principal conflicts, prepare a fresh artifact and obtain approval for that corrected load; never replay the old approval |
| Missing field or unknown response | Preserve actual backend identifiers, nested details and field paths. Message families here are recognition hints, not an exhaustive HTTP-status/envelope mapping |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Missing intent, conflicting representations or a narrow unsupported-rate request | Request precise correction |
| catalog_mismatch | BO, deployment schema or selected scope does not match the contract | Resolve capability/metadata mismatch before execution |
| auth_authz | Authentication or privilege failure | Follow owning core auth/privilege handling; do not bypass |
| transport_environment | Network, deployment or service availability failure | Preserve redacted diagnostics and use only core-permitted retries |
| fusion_api | Server rejects the operation or returned state does not match intended effect | Report actual outcome and necessary correction |
| process_timeout | Owning execution/polling reaches its deadline | Stop with operation, task, request/process ID, last status and next-check path |
| process_failed | Owning loader/import process fails | Preserve partial results and available process log/status |
| artifact_persistence | Owning preparation or evidence cannot be saved safely | Stop before dependent execution |
| approval_blocker | Exact execution approval or route is absent | Complete owning workflow gates; no direct REST substitution |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Preparation handoff | Task code/name, operation and hierarchy scope, selected environment, actual changes, expected defaults and any missing capabilities. Verify normalized final-artifact values and complete applicable task and core Data Loader validation; no separate adapter-conversion evidence gate applies |
| Post-write verification by owning workflow | Actual IDs/current values and child outcomes; compare forced/cleared completion fields, default flags, reference values, yield and reciprocal rates with intent |
| No-change request | Record already matching; no write occurred |
| Failure or partial outcome | Redacted stage, actual returned identifiers/messages, completed portions, missing facts and safe next action; never claim full success from an HTTP status alone |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing route, capability or metadata | No direct API/UI/global-helper fallback, guessed schema or hidden context bypass |
| Duplicate, date or graph validation | No auto-rename, local-clock correction, forced uppercase or repeated database validation |
| Mixed permitted/blocked changes | No silently reduced payload reported as complete; obtain a scope choice or follow an established partial-execution policy |
| Unknown or partial write | No automatic POST/PATCH/DELETE replay or blanket duplicate-as-success assumption |
| Version-dependent behavior | No claim that static compatibility expectations prove the target deployment's implementation. Skill edits alone do not prove an upload error resolved; require a corrected load success and verification of resulting header/resource values |

## Acceptance boundary

Before enabling the requested scope, the owning workflow must confirm its target contract and perform appropriate separate acceptance checks: minimal create and generated IDs; code versus ID and conflicting references; default omission versus explicit null; supplier count-point/OSP behavior; date boundaries; header/child resource flags, principal groups and immediate validation timing; primary and alternate reciprocal rates including zero/negative/null behavior; yield/profile features; campaign-resource protections; global-link protection; and requested DFF/attachment metadata. These checks are not per-request duplicate validations and are not authorized by resource authoring.

Recognize process-terminology variants ending _PM for WIS_SOP_DEF_CP_MUST_BE_YES, WIS_SO_REF_OP_CP_UPD, WIS_SOP_DEF_AWD_EXISTS, WIS_SO_REF_OP_CODE_UPD and WIS_SO_DELETE_CHK. Preserve namespaces when returned. Exact HTTP mapping and deployment-specific message coverage remain runtime evidence, not assumptions.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| STDOP.HANDOFF_GATE | step | 60 | execution_gate | passed->STDOP.RULES_COMPLETE;failed->STDOP.ERROR | STDOP.DESIGN | stop | Return preparation only when applicable evidence and declared core capability gates pass; no-write requests do not require mutation |
| STDOP.RULES_COMPLETE | terminal | 70 | terminal | none | STDOP.HANDOFF_GATE | stop | Return prepared rule results and verification requirements, not a claim of a Fusion write |
| STDOP.ERROR | step | 90 | error_handler | reported->RETURN_ISSUES | none | stop | Classify reached failure or missing evidence and preserve whole-request intent |
| RETURN_ISSUES | terminal | 100 | terminal | none | none | stop | Return precise blockers, partial outcome if any, and safe next action |
