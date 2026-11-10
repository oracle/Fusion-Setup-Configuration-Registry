# Error handling

These rules are reusable across target environments. Planner readiness means the execution rules are defined; all applicable runtime checks must still pass. The portable execution contract in ../references/execution-contract.md defines environment selection, input mapping, FSM compatibility checks and the maintenance Data Loader handoff. A missing product qualification is an explicit runtime blocker, never implicit approval.

Apply the selected executor's evidence-retention and disclosure contract. Maintenance Data Loader requires the protected candidate, retained preflight and Task Hook preview/approval envelope for exact-artifact submission. Preserve those records under core's retention policy, never in tracked source. Do not fabricate approval records or store raw customer inputs as diagnostics. Render failures using core guidance; save failure files only when explicitly requested and permitted. Handle requested status logs through the declared core status workflow.

## Error Situations

| Situation | What Should Happen |
|---|---|
| BU lookup cannot prove absence | Report unverified, ambiguous, inactive or unavailable as applicable; never say the BU does not exist or ask to create a duplicate on that evidence. Return the dependency blocker to the Run Book. |
| Missing BU prerequisite route unavailable | Report FUN_MANAGE_BUSINESS_UNIT, its discovered owner and the missing route/readiness contract. Preserve the original expense modification as pending; no direct API or browser fallback. |
| BU creation failed or is only accepted | Do not resume expense modification or claim setup completion. Use the owning workflow's confirmation/status contract; preserve partial success without retrying a write. |
| Required attribute or invalid code | Surface FND_CMN_REQ_ATTRIB_API_SERV or FND_CMN_INVALID_ATTRB_API_SRV2 only when actually returned; retain entity/field and redacted evidence only as permitted by the executor. |
| FSM row or readXML failure | readXML delegates to ADF and records row failures/undo behavior. Retrieve status and ProcessLog through an explicitly requested core status workflow. Do not infer whole-package atomic rollback. |
| Existing versus new key | updatePrimaryKeysInXML may reuse an existing writable key or apply an allowed sequence for a new row; this is not sufficient proof of every create/update input. |
| CSV empty/null values | CSVXmlTransform and ModelUtil have explicit-null handling. Preserve the distinction between an empty field, an absent node and an explicit null; do not invent a clear-value operation. |
| Live POST outcome unknown | Stop and preserve the known attempt identity within the executor's retention boundary. Reconcile only through the requested selected workflow. Never automatically retry an uncertain write. |
| Setup UI evidence requested | Source initHelperOrg/initDASetupTableVO can insert and commit defaults. Do not navigate as a supposedly read-only bypass. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input validation | Missing fields, unresolved code/value, unsafe key/audit intent | Report precise blockers; close source contract before candidate preparation. |
| catalog mismatch | Task or archive identity does not match | Stop and resolve exact catalog/metadata identity. |
| auth/authz | Selected route rejects identity or privilege | Use route-owned auth handling; never log tokens. |
| transport/environment | Network or environment failure | Report sanitized context under the core disclosure contract; no automatic mutation retry. |
| Fusion API | HTTP/API rejection | Report the failed stage and actionable error through core guidance; persist only explicitly requested, permitted diagnostics. |
| process timeout | Explicitly requested status workflow reaches its deadline | Return its timeout report and next-check route using the original accepted identity; no automatic post-initiation polling or resubmission. |
| process failed | Requested FSM status reports failure | Use the core status workflow for applicable ProcessLog and partial-success/error handling, within its retention rules. |
| artifact persistence | A required candidate or internal core approval record cannot be saved | Stop before additional side effects; never fabricate a replacement approval record. |
| approval blocker | Current preview-bound approval missing | Use Data Loader or Run Book approval workflow; do not duplicate it. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Authored rule plan | Report planner readiness separately from runtime checks. Applicable FSM_ALIAS_COLLISION and FSM_SERIALIZATION_UNQUALIFIED remain blocking until qualified; an already-satisfied setup option with both alias CSVs header-only makes alias selection not applicable, not universally qualified; never describe ready as completed setup. |
| Before eventual execution | Display the active executor's prescribed preview verbatim; retain its complete target, operation, candidate and approval binding internally under that executor's contract. |
| After failure | Render the active core failure report and one next action; keep internal identifiers and protected session material within its disclosure and retention boundaries. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Incomplete graph | No Data Loader handoff, guessed resolver endpoint, fabricated seed domain or omitted dependency. |
| Export package contains unrelated setup | Do not replay the full export or make unrelated changes. |
| Failure or uncertain result | Do not claim rollback, retry, or successful persistence without evidence. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUTO_HANDOFF | step | 60 | execution_gate | passed->AUTO_RETURN | AUTO_DESIGN | stop | Task validation before any Data Loader handoff |

The handoff node only returns validated task-rule results when every preceding contract is ready. It does not submit an import. AUTO_RETURN returns only validation results; it never reports a completed import.

## Result Terminal

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUTO_RETURN | terminal | 70 | terminal | none | AUTO_HANDOFF | stop | All task-rule gates passed; return validation results only |

## Evidence

Maintainer provenance IDs: `SRC-ORG-EO`, `SRC-OPTION-EO`, `SRC-FSM-MIGRATOR-HELPER`, `SRC-FSM-CSV-AM`, `SRC-FSM-CSV-TRANSFORM`, `SRC-FSM-NULL-MODELUTIL`, `SRC-UI-OPTIONS-AMIMPL`, `SRC-FSM-FRAMEWORK-FAQ`.

The reusable contract is the task-local field, scope and package rules. Maintainer source locations are excluded from distribution and are not runtime inputs. Historical review does not qualify a new target or authorize an import. Retain every current-target and approval check.
