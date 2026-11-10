# MPS errors and execution boundary



## Error Situations

| Situation | What Should Happen |
|---|---|
| Missing/unresolved field or reference | Return affected entity/field and required source or target evidence, without values; preserve other independent requests only after explicit scope review. |
| Bank or BU mismatch | Bank zero/multiple fails; BU zero removes child with error and first-match behavior needs ambiguity protection. Do not infer atomic rollback. |
| Invalid canonical code | Preserve source validation identity such as FND_CMN_INVALID_ATTRB_API_SERV without echoing sensitive values. |
| Sensitive input | Reject before persisting, logging or previewing any sensitive value. Record only safe field/category and manual step. |
| Import failed or outcome uncertain | Use original accepted request identity to reconcile through active core status workflow. No automatic retry or fresh export solely to recover context. |
| Rollback | Restore only reviewed ordinary baseline fields with sensitive rows excluded; no secret or secure segment replay. |
| Manual completion outstanding | Keep task In Progress. Successful import is not proof of business completion. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Validation | Affected field and actionable reason without credentials |
| Load approval | Use current core.data-loader immutable in-memory preview and contextual approval; retain same process; no file approval envelope |
| Completion | Reconciled intended changes, unchanged siblings and outstanding manual steps |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPS.GATE | step | 60 | execution_gate | pass->MPS.RETURN_SUCCESS;fail->MPS.RETURN_ISSUES | MPS.DEFAULTS | stop | always |

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPS.RETURN_ISSUES | terminal | 70 | terminal | none | none | stop | failure |
| MPS.RETURN_SUCCESS | terminal | 80 | terminal | none | MPS.GATE | stop | validation passed; no live success implied |
