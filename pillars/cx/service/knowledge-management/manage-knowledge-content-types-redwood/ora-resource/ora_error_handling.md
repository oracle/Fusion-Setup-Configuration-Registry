# Content Type Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| A completed same-task export baseline is unavailable, invalid, or has unclear required relationships | Stop before execution and obtain a completed export of the Redwood task. Inspect its metadata, CSV headers, identities, and parent-child relationships before preparing a package. |
| A visibility lookup has no documented request contract | Stop before applying restricted visibility and obtain the authoritative lookup contract. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| The exported baseline is unavailable or a required parent relationship is unclear | Do not construct or import a package from guessed member names, CSV columns, identifiers, or relationships. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CONTENT_TYPES_REDWOOD.BASELINE_CONTRACT | decision | 13 | execution_gate | ready->CONTENT_TYPES_REDWOOD.COMPLETE;unavailable_or_unclear->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.DESIGN | stop | Require evidence for all reached validation, source, locale, dependency, default and design nodes plus the matching active Run Book/core.data-loader FSM preflight and immutable source. Return intent only; core owns exact-artifact preview, approval, import and verification. |
| CONTENT_TYPES_REDWOOD.COMPLETE | terminal | 14 | terminal | none | CONTENT_TYPES_REDWOOD.BASELINE_CONTRACT | stop | Return the validated intent and accumulated node evidence to the owning Run Book/core.data-loader FSM workflow; no direct import, POST, PATCH, retry or duplicate approval is authorized. |
| CONTENT_TYPES_REDWOOD.REVIEW_COMPLETE | terminal | 90 | terminal | none | CONTENT_TYPES_REDWOOD.REVIEW_EXPORT | stop | Return the requested task-export review result without mutation handoff. |
| CONTENT_TYPES_REDWOOD.BLOCKED | terminal | 99 | terminal | none | none | stop | Stop on any missing/ambiguous source, invalid input, lookup failure, unresolved reference, declined policy acceptance or unavailable owner binding; persist sanitized diagnostics and the missing prerequisite. |
