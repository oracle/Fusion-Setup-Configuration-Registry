# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Workbook is missing, unreadable, or lacks the Time Slots worksheet | Stop and identify the workbook requirement that is not met. |
| A design rule fails | Stop before preview, identify the failed rule and affected time slot, and allow only the documented pre-preview correction. |
| Workbook authority is not documented | Stop before reporting the task ready; obtain the authoritative source and evaluation method for workbook values. |
| Read-only lookup is rejected or returns an ambiguous identity | Stop and report the resolver, sanitized response classification, and correction needed. |
| Describe metadata is absent for a requested write | Stop before preview; do not hand-build a payload or substitute an endpoint. |
| An independent live write fails | Persist only its sequence and allowlisted HTTP status/code/field/ECID; keep raw server detail transient. Do not retry that slot or change routes, then continue the remaining approved independent slots. Return `partial_failed` and a nonzero CLI exit code. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Workbook input is missing or cannot be read | Provide a readable workbook with the Time Slots worksheet. |
| Design enforcement | A supplied design rule has a blocking condition | Correct the affected time-slot design before preview. |
| Authoring blocker | Workbook authority or evaluation method remains TBD | Identify the authority and validation method, then recompile and plan again. |
| Lookup or dependency blocker | API access, identity, or required write metadata cannot be resolved | Correct the named prerequisite and rerun the read-only checks. |
| Contract blocker | Direct REST payload mapping lacks approved describe metadata | Supply the approved metadata contract before preview. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Blocked validation | Exact rule or input check, affected workbook row when known, and the required correction. |
| Incomplete authoring | The unresolved authority or evaluation-method gap and why no ready plan is available. |
| Blocked lookup | Resolver name, sanitized response category, and next corrective action. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Workbook values have no named authority | Treat workbook values as authoritative or claim the validation plan is ready. |
| A design rule fails | Continue to preview or make a live configuration change. |
| Direct REST payload mapping is unresolved | Hand-build a payload, retry a write, or switch routes automatically. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| TS.DESIGN_BLOCKED | terminal | 12 | terminal | none | none | continue | Workbook validation, dependency, lookup, or any design-enforcement rule fails. |
| TS.DESIGN_PASSED | terminal | 13 | terminal | none | TS.DESIGN_CHANGE_IMPACT | continue | All applicable design-enforcement rules pass. |
