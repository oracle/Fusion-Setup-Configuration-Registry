# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| The selected manufacturing plant is absent or cannot be confirmed in Fusion | Stop before source preparation; select or provide a valid existing plant. |
| Work Area Name or Work Area Code is absent, or a supplied Inactive Date is not later than the current date | Stop before source preparation; provide Name and Code, and either leave Inactive Date blank or provide a future date. |
| The Data Loader source for the selected import mode is missing, changed, or fails validation | Stop before import; correct it through core.data-loader and obtain a new approval preview. |
| An import result is uncertain or timed out | Stop and reconcile the result using the core Data Loader status workflow; do not resubmit the source automatically. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input validation | Task identity, Work Area Name, Work Area Code, operation intent, or a supplied Inactive Date is invalid | Correct the request before source preparation. |
| dependency | Existing plant cannot be confirmed or validated Data Loader source for the selected import mode is missing | Complete the prerequisite before approval. |
| Fusion API | core.data-loader reports a validation, upload, or initiation error | Review the sanitized diagnostic and correct the source; do not automatically retry a write. |
| approval blocker | The immutable Data Loader source has not received the required approval | Obtain approval for the exact reviewed artifact. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Failure | Failure class, stage, sanitized message, affected design rule or Data Loader validation status, and recommended action. |
| Data Loader approval preview | Immutable artifact name and SHA-256, target plant scope, work-area scope, and the approval required before submission. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| The selected plant is absent or cannot be confirmed | Do not create a work area for an unconfirmed manufacturing plant. |
| FSM is selected and its native package contract is unknown | Do not invent columns, archive layout, or import actions. |
| The artifact differs from the exact approved immutable source | Do not upload or initiate the load; restart validation and approval. |
| The Data Loader result is uncertain | Do not automatically retry or re-submit the artifact. |
| A direct REST write is proposed | Do not issue a direct REST write; use the centralized core.data-loader workflow. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WA.DONE | terminal | 5 | terminal | none | WA.DESIGN | continue | All applicable validation, dependency, and design checks pass |
| WA.FAILED | terminal | 6 | terminal | none | none | continue | A blocking validation, dependency, or design failure occurs |
