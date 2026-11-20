# Error handling and execution gate


## Error Situations

| Situation | What Should Happen |
|---|---|
| AP-810285 / AP_DIST_PERCENT_NOT_100_OR_0 | Report exact owning-set aggregate and header value; stop for corrected design. |
| AP_AT_LEAST_ONE_CHILD | Require a child line; do not insert an invented balancing row. |
| AP-810410 | UI-based FSCR create policy: reject past inactive dates before package generation using the system clock and configured application time zone, or the runtime local zone by default. This is a local FSCR rule; do not claim a server restriction or apply it to updates. |
| AP_NO_DELETE / AP_CLEAR_CHILD_RECORD | Stop persisted deletion or BU relocation with children; do not clear records as a workaround. |
| FND_CMN_INVALID_ATTRB_API_SERV | Identify supplied Type1099 and active-code validation failure without substituting a label. |
| Lookup, flexfield, or uncertain import result | Stop and retain sanitized diagnostics. No automatic retry; fresh read/export reconciliation must establish state before considering a separately approved submission. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before candidate approval | Exact task, operation, environment, keys, intended values and side effects, unresolved-field decisions, dependency status, immutable preview fingerprint. Static build does not grant live authority. |
| Execution route | Run Book owns input/orchestration; core.data-loader owns FSM package, preview, approval and one submission. ObjectShortName is AP_MANAGE_DISTRIBUTION_SETS; businessObject remains empty. |
| Readiness | Incomplete dependencies block the compiled plan. Proceed only after required dependencies, package checks and import approval are complete. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Unapproved mutation | No task resource directly invokes an import, combination creation, delete, or write API. |
| Missing or ambiguous evidence | Do not invent identity, endpoint, field mapping, length units, or successful import behavior. |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DS.GATE | decision | 60 | execution_gate | validated->DS.READY;blocked->DS.ISSUES | DS.DESIGN | stop | Validation completion only; separate live preview/approval remains mandatory |
| DS.ISSUES | terminal | 70 | terminal | none | none | stop | Return exact missing or invalid facts; no write |
| DS.ERROR | terminal | 80 | terminal | none | none | stop | Return sanitized runtime failure; no retry |
| DS.READY | terminal | 90 | terminal | none | DS.GATE | stop | Return validation results to Run Book; never grant mutation authority |


Use exact COMPLETED package-process status; strings containing success/complete fragments are insufficient. Validate output destinations before writing, including failure reports, and create outputs exclusively. Never overwrite an input or existing output. Validate the independently selected physical environment against package metadata, check credential-free HTTPS origins and require boolean template flags consistent with populated members. Candidate and readback environment/release must agree with the selected baseline. Authentication-profile labels do not establish environment identity.

## Income tax lookup outcomes

A missing seed-reference entry is a lookup trigger, not proof of invalid input. Distinguish unavailable REST (disclose and continue with an explicit code, letting Fusion validate during approved import) from a successful no-match, confirmed inactive result or ambiguous description (ask for correction/selection). An unknown description cannot be passed as a code when REST is unavailable. Preserve unchanged existing Type1099 values without lookup. Do not automatically create tax types, retry imports or claim that a warning means validation passed. See [Income tax resolution policy](ora_reference_lookups.md#income-tax-resolution-policy).
