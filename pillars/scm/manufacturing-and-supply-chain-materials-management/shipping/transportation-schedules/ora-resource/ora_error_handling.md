# Transportation Schedules Error Handling

## Error Situations

| Situation | What should happen |
|---|---|
| Parent POST is rejected | Preserve the redacted Data Loader diagnostic. Correct the parent business attributes through the BO contract; do not add locally derived IDs. If Fusion reports a duplicate assignment, treat the requested parent business key as already assigned and do not retry the POST automatically. |
| Child POST reports a missing parent key or is rejected as an orphan child | Stop before submission. Correct the complete parent business key in the operation context so BO/Data Loader can resolve the parent route key; do not request a user-supplied technical ID or supply `SiteScheduleAssignmentId`. |
| Parent PATCH or DELETE cannot be addressed | Preserve the redacted diagnostic and correct the submitted parent business key. The BO resolves `TransportationScheduleAssignmentId`; do not perform a task-local REST lookup or add a locally derived ID. |
| Child PATCH or DELETE reports a missing parent key | Stop before submission. Correct the complete parent business key in the operation context. The BO resolves `TransportationScheduleAssignmentId`; do not supply or derive it locally. |
| Child PATCH or DELETE reports a missing child key | Stop before submission. Correct the child business key within the submitted parent context. The BO resolves `SiteScheduleAssignmentId`; do not supply or derive it locally. |
| Schedule name cannot be resolved | Preserve the redacted diagnostic and correct the value to the exact UI LOV display text, including capitalization. Do not replace it with a locally resolved `ScheduleId`. |
| Carrier and schedule-usage combination is rejected | Preserve the redacted diagnostic and correct the friendly carrier or schedule-usage input through the BO contract. Do not attempt a task-local lookup or substitute a backing ID. |
| Fusion Data Loader rejects a request | Preserve redacted diagnostics, classify the rejected attribute, correct the source, validate it, and require a fresh preview and approval. Do not retry a live operation automatically. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| TS.DONE | terminal | 40 | terminal | none | TS.VALIDATE_OPERATION | stop | Operation payload validation passed |
| RETURN_ISSUES | terminal | 50 | terminal | none | none | stop | Operation payload validation failed |
