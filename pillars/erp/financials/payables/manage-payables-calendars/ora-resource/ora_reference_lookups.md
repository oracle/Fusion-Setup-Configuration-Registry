# Reference Lookups

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| validate_calendar_type | AP_OTHER_PERIOD_TYPE.CalendarType is supplied | Submitted CalendarType. | Accept only the canonical package code. Normalize the matching business labels case-insensitively to `GENERAL` or `PAYMENT TERMS`. | Canonical CalendarType code. | Block a value outside the two supported codes. |
| preserve_period_frequency | AP_OTHER_PERIOD_TYPE.PeriodFrequency is supplied | Submitted PeriodFrequency. | No task-owned allowed-code list or read-only service contract is documented. Preserve the supplied package code without label conversion or value invention. | Submitted PeriodFrequency code. | Do not select a substitute value. Fusion FSM Import remains authoritative for validation. |
| preserve_period_name_format | AP_OTHER_PERIOD_TYPE.PeriodNameFormat is supplied | Submitted PeriodNameFormat. | No task-owned allowed-code list or read-only service contract is documented. Preserve the supplied package code without label conversion or value invention. | Submitted PeriodNameFormat code. | Do not select a substitute value. Fusion FSM Import remains authoritative for validation. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| CalendarType is supplied as General or Payment Terms | Normalize it to the supported package codes `GENERAL` or `PAYMENT TERMS` before candidate generation. |
| CalendarType is supplied as any other value | Stop before candidate generation; no supported alternate code is evidenced. |
| PeriodFrequency or PeriodNameFormat is supplied | Preserve the exact supplied package code. Do not query a UI proxy, infer an allowed value, or derive a replacement. |
| Fusion later rejects a preserved PeriodFrequency or PeriodNameFormat value | Retain the sanitized FSM diagnostic as evidence and request a corrected business value; do not retry automatically. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CALENDAR.CHECK_LOCAL_VALUES | step | 15 | reference_lookup | ready->CALENDAR.CHECK_DEPENDENCIES;blocked->CALENDAR.INPUT_BLOCKED | CALENDAR.VALIDATE_INPUT | stop | Always; apply only the Local Lookups rules for supplied calendar fields, preserve codes without a task-owned allowlist, and make no live lookup calls |
