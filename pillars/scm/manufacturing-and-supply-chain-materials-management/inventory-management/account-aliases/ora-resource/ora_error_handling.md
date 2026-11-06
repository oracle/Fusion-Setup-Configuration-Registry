# Account Aliases Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| An Enable Date or nonblank Disable Date cannot be converted to a valid calendar date | Stop before FSM CSV and ZIP preparation. Ask the user to correct or clarify the date. |
| A supplied date has more than one valid calendar interpretation | Stop before FSM CSV and ZIP preparation. Ask the user for the intended date; do not select a date interpretation. |
| A date normalizes successfully | Continue with the central FSM ZIP-preparation workflow using the `YYYY/MM/DD` FSM CSV value. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | A supplied Enable Date or nonblank Disable Date is invalid, incomplete, or ambiguous. | Obtain an unambiguous intended date from the user, then normalize it before FSM ZIP preparation. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RETURN_SUCCESS | terminal | 20 | terminal | none | ACCOUNT_ALIASES.NORMALIZE_FSM_DATES | continue | Every supplied Account Aliases Enable Date and Disable Date is normalized to `YYYY/MM/DD`, or Disable Date is blank. |
| RETURN_ISSUES | terminal | 30 | terminal | none | none | continue | An Account Aliases Enable Date or Disable Date requires user clarification before FSM CSV preparation. |
