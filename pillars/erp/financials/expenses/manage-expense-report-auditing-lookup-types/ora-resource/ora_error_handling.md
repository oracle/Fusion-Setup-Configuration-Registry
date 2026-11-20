# Auditing lookup outcomes and recovery

## Error Handling

| Failure | Action |
|---|---|
| Input validation or catalog mismatch | Report all rows/cells and exact missing contract; no external action |
| Auth/authz or transport/environment | Let the selected core client own auth refresh once; retain safe diagnostic; do not infer missing setup |
| Process timeout | Stop; report environment, task, ProcessId, last status and elapsed wait; next check requires user decision |
| Fusion API or process failed | Retrieve ProcessLog when available; retain row warnings and partial successes; no automatic mutation retry |
| Artifact persistence | Stop before handoff; retain no credentials or partial artifact presented as complete |
| Approval blocker | Keep preparation separate from submit authority; use only Data Loader's current approval contract |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUDLK_HANDOFF | step | 6 | execution_gate | success->AUDLK_REVIEW | AUDLK_DESIGN | stop | Validated local design only; return to Run Book/Data Loader |
| AUDLK_REVIEW | terminal | 7 | terminal | none | AUDLK_HANDOFF | stop | Design handoff complete; execution not authorized by this graph |
