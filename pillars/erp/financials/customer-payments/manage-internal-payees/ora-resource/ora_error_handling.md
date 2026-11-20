# Error handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| FND_CMN_TO_ERLY_EQ_FRM_DATE | Correct effective-date ordering; preserve request and baseline. |
| FND_CMN_REC_COMB_VALS_EXST or FND_CMN_RCRD_VAL | Disambiguate existing root/rule identity; do not retry as a new record. |
| IBY_RULES_FCPP_REQUIRED | Resolve the required PROCESSOR profile; do not fabricate a profile code. |
| IBY_ROUTINGRULE_COND_REQUIRED | Provide a valid routing condition. |
| FND_CMN_HINT_POSITIVE or FND_CMN_MUST_BE_POSITIVE | Correct original AMOUNT input; do not strip a minus sign and call it validated. |
| Uncertain import result | Stop; inspect the accepted attempt and fresh persisted state through the active workflow before any new submission. No automatic replay. |
| Missing resolver evidence | Return evidence-unresolved for the exact affected reference; do not report unsupported operation or invalid business value without proof. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before Data Loader handoff | Exact task, operation, identities, intended differences, related ownership effects, validation results and unresolved fields; keep secrets out of diagnostics. |
| Completion | Attempt success, persisted-state verification and Run Book synchronization are separate outcomes. Static rule evaluation is not business completion. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IP.GATE | step | 60 | execution_gate | pass->IP.DONE;fail->IP.ERROR | IP.DESIGN | stop | Return static checks to active Run Book/Data Loader; approval owned there |
| IP.ERROR | terminal | 90 | terminal | none | none | stop | A declared failure branch; disclose exact cause and safe next step |
| IP.DONE | terminal | 100 | terminal | none | IP.GATE | stop | Static task-rule result only; no Fusion completion claim |
