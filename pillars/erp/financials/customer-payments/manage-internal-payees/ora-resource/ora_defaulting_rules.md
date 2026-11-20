# Defaulting rules

Only explicit create defaults below may be proposed. Update always overlays accepted changes on a fresh full baseline. Blank/missing mapped CSV values become XML null; they do not mean preserve.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| IBY_INTERNAL_PAYEE.Ecappid | 673 | Create with omitted Ecappid and accepted reviewed default | No |  |
| IBY_INTERNAL_PAYEE.Activestatus | Y | Create with omitted status and accepted reviewed default | No |  |
| ORA_IBY_FC_INT_PAYEE_MAP.OrgType | OPERATING_UNIT | Create BU mapping with omitted OrgType | No |  |
| IBY_FC_ROUTING_RULE.Configured | 1 | Create rule with omitted Configured | No |  |

## Derived Values and Date Intent

| Condition | Behavior | Evidence |
|---|---|---|
| Payee effective dates | Default start dates use the database date; open-ended EndDate sentinel is 4712-12-31. EndDateDsp blank maps to sentinel. Serialize accepted date intent consistently; do not use workstation date as database date. | Task operating contract |
| Payee end-date alias | `EndDateDsp` must remain consistent with `EndDate`; a blank display alias resets the end date to 4712-12-31. For an approved finite end date, serialize `EndDate` and `EndDateDsp` as the same calendar day. For updates, carry forward their consistent current values unless a date change was requested. Reject conflicting supplied aliases; never blank the display alias to mean unchanged. | Task operating contract |
| Payee UI Status | The search page derives `Status` from the database date and inclusive StartDate/EndDate bounds. `Activestatus=N` alone does not establish UI Inactive. If the requested outcome is date-based UI inactivation, obtain the intended effective end date and verify both persisted dates and the date-based UI result. Do not invent an InactiveDate or write the calculated Status. | Task operating contract |
| Condition sequence | An omitted sequence can become the maximum sibling sequence plus one when its parent is available. Require deterministic unique sequence within the selected rule. | Task operating contract |
| IsValueString | Derived from ParameterCode and Value. N for AMOUNT/PY_BANK/PY_BANK_ACCOUNT/AR_RECEIPT_METHOD_ID/ORG_ID, Y otherwise. It is not an independent business override. | Task operating contract |
| Condition display fallback | When display input is omitted, `PayerBankRoutingNumDisp` can return the current `Value`, including for AMOUNT. An omitted display input can therefore export the current amount. Reconcile this derived output with the intended current Value rather than requiring blank or treating the display as an extra customer choice. An explicit display value, and the ABA-specific write behavior, still require their own applicable validation. | Task operating contract |
| Account payment status | No default is assumed. Use explicit 1 for enabled or 0 for disabled; verify the intended state in the current target. | Task operating contract |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IP.DEFAULTS | step | 40 | apply_default | pass->IP.DESIGN;fail->IP.ERROR | IP.DEPENDENCIES | stop | Selected Manage Internal Payees request; evaluate only applicable source rows |
