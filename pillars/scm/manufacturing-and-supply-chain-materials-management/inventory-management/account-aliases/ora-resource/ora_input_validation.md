# Account Aliases Input Validation

## FSM Date Normalization

| User Input | FSM CSV Column | Required Output | Applies When | Failure Handling |
|---|---|---|---|---|
| Enable Date | Enable Date | Convert an unambiguous valid date to `YYYY/MM/DD` before FSM ZIP preparation. | An Enable Date is supplied. | Stop and request clarification when the supplied date is invalid, incomplete, or ambiguous. |
| Disable Date | Disable Date | Convert an unambiguous valid date to `YYYY/MM/DD` before FSM ZIP preparation. Preserve a blank value as blank. | A Disable Date is supplied. | Stop and request clarification when the supplied nonblank date is invalid, incomplete, or ambiguous. |

## Normalization Rules

| Check | What Happens | Applies When |
|---|---|---|
| Canonical FSM date format | Emit every nonblank Enable Date and Disable Date in the FSM CSV as `YYYY/MM/DD`. | Before the central FSM ZIP-preparation workflow. |
| Ambiguous date | Do not guess a calendar interpretation when the supplied value could represent more than one date. Ask the user to provide the intended date in an unambiguous form. | A supplied date has more than one valid interpretation. |
| Invalid or incomplete date | Do not prepare the FSM CSV row. Ask the user to correct or clarify the date. | A supplied nonblank date cannot be converted safely to a calendar date. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ACCOUNT_ALIASES.NORMALIZE_FSM_DATES | step | 10 | validate_input | normalized->RETURN_SUCCESS;ambiguous-or-invalid->RETURN_ISSUES | none | stop | Before preparing an Account Aliases FSM CSV row with an Enable Date or Disable Date. |
