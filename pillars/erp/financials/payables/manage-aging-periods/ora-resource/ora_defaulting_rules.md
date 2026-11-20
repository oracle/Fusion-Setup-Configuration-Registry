# Defaulting Rules

Task scope: AP_MANAGE_AGING_PERIODS / Manage Aging Periods. Use a fresh exact-task export to match existing records. Run Book supplies inputs. Create and update are supported. Submit the validated package through Data Loader after its required approval.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| AP_AGING_PERIOD.Status | A; EO default, explicitly serialize if omitted | new header with Status omitted | No; only fill omitted value |  |
| AP_AGING_PERIOD_LINE.PeriodSequenceNum | For a new parent with all detail orders omitted, assign 1, 2, 3… in listed order and disclose in preview. Preserve explicit numbers. Mixed supplied/omitted orders require clarification; existing parents require explicit orders | detail create under a new parent | No; preserve explicit order |  |
| AP_AGING_PERIOD_LINE.Type | Fusion assigns PAST when DaysStart + DaysTo > 0, otherwise CURRENT. Create package leaves Type blank; update package preserves its export value. Check the calculated value after import | line insert or update | No; direct independent Type input unsupported |  |
| Audit history | Framework-owned; never implementor input | create or update | No |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AGING.DEFAULTS | step | 20 | apply_default | pass->AGING.MATCH;invalid->AGING.RETURN_ISSUES | AGING.INPUT | stop | create or update |
