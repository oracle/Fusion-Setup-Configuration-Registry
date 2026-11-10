# Manage Formats errors and handoff

Source-backed static guidance; live qualification remains separate.

## Error Situations

| Situation | What Should Happen |
|---|---|
| ProcessingError/import failure | Preserve the exact attempt identity and logs; show affected fields; require corrected preview and new approval before retry |
| Overlength value | Show entity/field, actual size, source-backed maximum/unit; request corrected text, never truncate |
| Auth or transport failure | Distinguish failure from zero matches; follow central one-refresh policy and preserve request identity |
| Timeout or uncertain mutation | Poll/reconcile the same attempt; never resubmit automatically |
| Run Book sync failure after import | Keep Fusion outcome and sync outcome separate; parent stays In Progress until reconciled |
| Template child failure | Retain useful artifacts and diagnostics; return guided-manual mode without asserting success |
| Missing attachment/runtime evidence | Report exact pending manual action or runtime test; metadata success is not business completion |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Preview | Exact environment, target keys, operation, requested changes, source/qualification gaps and immutable candidate hash |
| Completion | Persisted-state diff, unaffected-row preservation, template attachment and runtime verification separately |
| Retry | Original attempt identity, failure, correction and fresh approval requirement |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FMT-GATE | step | 60 | execution_gate | ready->FMT-READY;missing->FMT-MISSING | FMT-DESIGN | stop | Return validated preparation to Run Book/Data Loader; never perform writes here |
| FMT-ERROR | step | 70 | error_handler | reported->FMT-FAILED | none | stop | Validation or contract failure |
| FMT-READY | terminal | 80 | terminal | none | none | stop | Preparation ready for central preview; not proof of import or completion |
| FMT-MISSING | terminal | 90 | terminal | none | none | stop | Required candidate fact or evidence missing |
| FMT-FAILED | terminal | 100 | terminal | none | none | stop | Failure disclosed; no automatic retry |

