# Manage Resource to Item Mapping Error Handling

Current capability gate: the task SKILL.md permits metadata/sample and explicitly requested status only. Complete business/reference reads and create/update/delete preparation are unsupported. Return blocked (invalid at input validation) before external activity or source preparation; the remaining domain contracts do not enable those operations.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Failed BO or reference reader | Block the affected read or identity-dependent write; name the failed core Data Loader read stage or exact live field/registration mismatch |
| Missing registration, template, adapter or operation | Stop core preparation; do not guess a source or switch executors |
| Authentication or authorization failure | Preserve the initial status and stage; use only core authentication recovery and stop on denied access |
| Invalid or ambiguous identities | Stop before preview; do not substitute another mapping, organization, resource or item |
| Failed or uncertain load | Do not retry upload/initiation; reconcile through core Data Loader when requested |
| Accepted initiation | Return the core report immediately; initiation is not completion |
| Later status or values request | Use core Data Loader status; require its supported BO reader for current values, otherwise report verification blocked |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RIM.EXECUTION_GATE | decision | 4 | execution_gate | ready->RIM.RETURN_PREPARED;blocked->RIM.RETURN_REFUSAL | RIM.CHECK_DEPENDENCIES | stop | Require supported Data Loader capabilities, applicable identity evidence, live template validation and actual project binding before core preview |
| RIM.RETURN_PREPARED | terminal | 5 | terminal | none | RIM.EXECUTION_GATE | continue | Return supported Data Loader results or its validated handoff; core approval remains mandatory |
| RIM.RETURN_REFUSAL | terminal | 6 | terminal | none | none | continue | Report the precise blocker and required core capability without substituting another route |
