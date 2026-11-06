# Execution Contract

This task does not authorize hand-authored direct REST writes. Use the existing shared FDOS export, validation, authentication, FSM client, and import paths. Use the supported FSM task-CSV import contract for mapping headers, segment rules, rollup rules, and account rules; do not treat it as a public direct GL mapping REST endpoint.

## Runtime Sources

| Source | Purpose |
|---|---|
| shared.setup-export.task-level-export | Retrieve same-task setup evidence where supported |
| shared.validation.setup-data-validator | Validate supported setup data and generated artifacts |
| chartOfAccountsLOV | Read-only source and target COA lookup for mapping validation; independent template/spec export may occur at any time |
| valueSets and child values | Read-only value-set definition and referenced-value lookup after segment-to-value-set resolution |
| shared.validation.reference-data-validator | Validate charts, segments, values, and hierarchies |
| core.data-loader | Mandatory import orchestration, preflight, Task Hook, immutable package, and approval; shared import primitives never bypass it |
| Existing FDOS authentication skills | Supply environment-bound authentication without persisting secrets |
| Core FSM REST client | Shared execution primitive only; no task-local REST contract is invented |
| Same-task FSM CSV export | Establish the current task CSV contract; ORA_GL_AFF_MAP_RULE.csv and ASM_SETUP_CSV_METADATA.xml are required evidence for account-rule import |

## Execution Contract

| Situation | What Happens |
|---|---|
| Independent template export | Invoke shared.setup-export.task-level-export whenever needed in its default template/spec mode; it requires no COA or mapping-comparison prerequisite. |
| Read-only discovery | Retrieve the current template/spec whenever needed through the shared export workflow without COA or mapping-comparison prerequisites. Compare current target mapping evidence before submission; pending allows local preparation only |
| Source or target COA lookup | Use only GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV and GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV/{StructureInstanceId}; no write path is authorized |
| Value-set lookup | Use GET /fscmRestApi/resources/11.13.18.05/valueSets for an exact ValueSetCode, then follow the returned item link for GET child/values. No value-set write path is authorized by this skill. |
| Header absent | Preview the export-derived FSM task-CSV create action and require explicit approval |
| Header differs | Show field-level and rule-level differences; require update or distinct-name direction |
| Standard segment or single-source rollup import | Use the export-derived FSM task-CSV route after readiness passes unless the user explicitly selects FBDI |
| Multiple-source segment or rollup import | Use the current FBDI route; no public REST endpoint or export-derived FSM multiple-source CSV contract is confirmed |
| Account rule | Do not route through the FBDI workbook. Preview the export-derived FSM task-CSV action with ORA_GL_AFF_MAP_RULE.csv and matching metadata. |
| Update | Reread the mapping immediately before execution and stop on concurrent changes |
| Replace | Require separate explicit approval and complete-replacement proof |
| Delete | Require explicit target confirmation, impact disclosure, and approval |

## Endpoint

| Action | Method | Path |
|---|---|---|
| Resolve source or target COA | GET | /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV |
| Read resolved COA detail | GET | /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV/{StructureInstanceId} |
| Resolve value-set definition | GET | /fscmRestApi/resources/11.13.18.05/valueSets?q=ValueSetCode='{ValueSetCode}' |
| Read value-set values | GET | {returned value-set item link}/child/values |
| Read existing mapping | Supported read-only lookup or export | Manage Chart of Accounts Mappings; no public GL COA Mapping REST endpoint is confirmed |
| Submit FSM task-CSV package | core.data-loader only | Its approved FSM ZIP upload/initiation workflow; never invoke setupTaskCSVImports directly from this task |
| Upload segment and rollup rules | Shared import workflow | Manage Chart of Accounts Mappings, Actions, Upload Rules |
| Import segment and rollup rules | Shared import workflow | Manage Chart of Accounts Mappings, Actions, Import Rules |
| Import account rules | Shared FSM task-CSV import workflow | ORA_GL_AFF_MAP_RULE.csv in an export-derived setup-task CSV package |
| Review implemented rules | Read-only report | Chart of Accounts Mapping Rules Report |

## Preview Pattern

| Step | Requirement |
|---|---|
| 1 | Show environment, mapping, source and target charts, resolved SecurityFlag, resolved import mode, accounting date, whether each was user-supplied or defaulted, action, and execution route |
| 2 | Show existing-object comparison and concurrent-update baseline |
| 3 | Show rule counts by segment, single-source rollup, multiple-source rollup, and account rule |
| 4 | Show overlap results and the account-rule precedence outcome |
| 5 | Show selected-import-contract evidence, files, mode, unresolved values, and readiness decision; show ORA_GL_AFF_MAP_RULE.csv metadata when account rules are present |
| 5a | Show why FSM or FBDI was selected; disclose FSM availability when an explicit FBDI choice is honored |
| 6 | Show side effects, especially Replace omissions and any create, update, or delete |

## Live Pattern

| Step | Requirement |
|---|---|
| 1 | After all task checks pass, use core.data-loader preflight, Task Hook preview, and its approval workflow for the immutable artifact. Do not add a duplicate pillar approval. |
| 2 | Detect concurrent changes during preapproval validation; after approval follow the Data Loader persisted-envelope integrity check without rebuilding or revalidating source data. |
| 3 | Execute once through core.data-loader; its successful initiation is terminal for that request. |
| 4 | Persist request or process identifiers, status, logs, artifact references, and errors without secrets |
| 5 | On a requested result check, use Data Loader status and the Chart of Accounts Mapping Rules Report or equivalent read-only evidence. |
| 6 | Do not retry a live mutation without idempotency evidence or fresh approval |

## Submission Terminal and Requested Result Checks

On accepted Data Loader initiation, COAMAP.EXECUTE returns success and ends at COAMAP.DONE_SUBMITTED. Return the shared Data Loader initiation response immediately; do not poll, run COAMAP.VERIFY, or claim the mapping is fully loaded. This terminal means submission accepted, not import completion.

Only when the user later explicitly requests status, progress, results, counts, or errors, resume the accepted load at COAMAP.EXECUTE using its request/content identifier and prior submission context. Select status_requested without uploading, initiating, or requesting mutation approval again. If only an identifier is available, use the shared Data Loader status workflow directly; do not fabricate completed submission nodes or replay preparation. COAMAP.VERIFY delegates the requested read to that status workflow and classifies the returned result: verified only for confirmed successful completion, pending for an in-progress or not-yet-available result, and failed for a reported failure. Pending ends at COAMAP.DONE_PENDING after that requested check; it does not loop, resubmit, or start automatic polling. Perform a mapping report comparison only when the requested review requires it, and disclose incomplete evidence.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAMAP.PREVIEW | step | 11 | preview_gate | pass->COAMAP.APPROVAL;prepared_only->COAMAP.DONE_PREPARED | COAMAP.BULK | stop | Readiness passes |
| COAMAP.APPROVAL | decision | 12 | approval_gate | approved->COAMAP.EXECUTE;declined->COAMAP.STOPPED | COAMAP.PREVIEW | stop | A live mutation is requested |
| COAMAP.EXECUTE | step | 13 | execution_gate | success->COAMAP.DONE_SUBMITTED;status_requested->COAMAP.VERIFY;failed->COAMAP.ERROR | COAMAP.APPROVAL | stop | Exact mutation is approved; status_requested is only a later user-requested read using prior accepted submission context |
