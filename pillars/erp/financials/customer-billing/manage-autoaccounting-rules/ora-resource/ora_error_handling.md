# Manage AutoAccounting Rules Error Handling


## Failure Classification

| Failure | Classification | Required Response | Retry Boundary |
|---|---|---|---|
| Missing or ambiguous business value | Business clarification | Ask one bounded question and create no candidate | Retry normalization only after the answer |
| Duplicate create target | Design conflict | Explain existing BuName plus Type and ask whether update is intended | Never reinterpret create silently |
| Missing update target | Design conflict | Request exact BuName, Type, and Segment | Create no candidate |
| No-op update | No change | Report the already-persisted state | Do not import |
| Populated audit field or package drift | Package-integrity failure | Reject offline and identify member/field | Rebuild from exact template; never patch ZIP manually |
| Optional preflight unavailable | Availability limitation | Record skipped preflight; retain authoritative FSM validation | Do not auto-retry |
| FSM validation returns zero or multiple matches | Data outcome | Surface exact key and request correction/disambiguation | Requires a new design and candidate |
| Import outcome unknown | Mutation uncertainty | Stop, preserve process evidence, obtain status and fresh export | Never resubmit uncertain request |
| Process has failed rows or unresolved warnings | Import failure | Collect logs and reconcile for partial persistence | Never reuse failed candidate |
| Fresh export differs from candidate or baseline | Reconciliation failure | Report requirement mismatches and failure owner | Repair owner, add regression, start fresh |

## Handoff Requirements

| Requirement | Required Evidence |
|---|---|
| Static handoff | Exact task/release/environment, source hashes, normalized design, compatible template, zero blockers |
| Candidate handoff | Candidate path, SHA-256, entity/row counts, business summary, warnings, repeat-build result |
| Import success | Data Loader terminal success with zero failed rows and no unresolved warning |
| Persisted success | Fresh exact-task export and zero requirement mismatches |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AAR.HANDOFF_GATE | decision | 6 | execution_gate | static_ready->AAR.STATIC_READY;blocked->AAR.RETURN_ISSUES | AAR.ENFORCE_DESIGN | stop | Before handing a request to offline package tooling |
| AAR.STATIC_READY | terminal | 7 | terminal | none | AAR.HANDOFF_GATE | stop | Static validation, dependencies, defaults, and design gates passed |
| AAR.RETURN_ISSUES | terminal | 90 | terminal | none | none | stop | Any blocking validation, reference, design, approval, or package-contract outcome |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-FSM-PACKAGE; SRC-CODE-SERVICE-IMPL | Package, process, and import/export boundaries |
| SRC-CODE-HEADER-EO; SRC-CODE-SEGMENT-EO | Audit, key, and persistence failures |
