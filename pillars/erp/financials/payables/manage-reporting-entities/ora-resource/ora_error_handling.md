# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Missing header fields | Report FND_CMN_CMPLT_FLDS or required-attribute diagnostic with the exact missing input. |
| Missing balancing child | Report AP_AT_LEAST_ONE_CHILD. |
| Invalid BU/location/BSV | Preserve AP_INVALID_BU or FND_CMN_INVALID_ATTRB_API_SERV and exact field context; do not retry automatically. |
| Duplicate | Preserve AP_DUPLICATE_IN_BU, FND_CMN_RCRD_VAL or FND_CMN_REC_COMB_VALS_EXST as applicable; request a new business decision. |
| Import exception | Service sets processing error to localized message; retain process diagnostics and return partial outcomes. |
| Unresolved contract | Report evidence_unresolved separately from invalid value; exact candidate acceptance does not waive integrity, identity, known validation or normal approval. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Preview | Selected environment, exact task/target, proposed differences, preserved scope, reference status and any accepted evidence uncertainty |
| Submission | Active Run Book and core.data-loader own approval, memory-only session and single submission. Static generation provides no execution approval. |
| Verification | Fresh same-task export; compare requested changes and all untouched rows. No success claim from initiation alone. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRE.GATE | step | 60 | execution_gate | success->MRE.DONE;failure->MRE.ERROR | MRE.DESIGN | stop | Validation returns to active Run Book/Data Loader; no direct writes |
| MRE.DONE | terminal | 70 | terminal | none | MRE.GATE | stop | Task-rule evaluation complete; return to workflow owner |
| MRE.ERROR | terminal | 80 | terminal | none | none | stop | Any earlier rule fails |
