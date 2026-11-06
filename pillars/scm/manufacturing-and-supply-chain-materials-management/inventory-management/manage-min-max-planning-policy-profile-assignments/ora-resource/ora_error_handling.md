# Manage Min-Max Planning Policy Profile Assignments Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| IncludeInCal is supplied as a friendly value other than Yes or No | Stop before Data Loader handoff and request Yes or No. |
| minMaxPolicyAssignments metadata preflight is unavailable, fails, or does not resolve the business object | Classify the result as auth/authz or transport/environment as applicable, then stop. Restore the required access or registration and run a fresh preflight; do not use direct REST as a fallback. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | IncludeInCal has an unsupported supplied representation. | Supply Yes or No, then restart validation. |
| auth/authz | The selected environment does not authorize the metadata preflight. | Restore required access, then run a fresh preflight. |
| transport/environment | The selected environment or metadata service is unavailable. | Restore environment availability, then run a fresh preflight. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| The preflight fails or is unavailable | Do not hand off to Data Loader or substitute a direct REST operation. |
| A value is not Yes or No | Do not guess a numeric IncludeInCal value. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RETURN_SUCCESS | terminal | 30 | terminal | none | MIN_MAX_POLICY_ASSIGNMENTS.PREFLIGHT_DATALOADER_METADATA | continue | Input validation and the current-run metadata preflight succeeded. |
| RETURN_ISSUES | terminal | 40 | terminal | none | none | continue | Input validation or metadata preflight did not succeed. |
