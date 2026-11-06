# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| The prompt requests CPQ as source and Fusion as target, or gives conflicting directions | Stop before any live step. Explain the supported Fusion-to-CPQ flow and ask the user to confirm that direction. Do not reverse the request silently. |
| REST routing and DAT source are both present | This combination is the declared adapter workflow, not a failure. Continue the actual core metadata and source checks. |
| The generated chargeId is an integer placeholder | Apply the optional-field contract in ora_input_validation.md; do not reject it for lacking a business-record match. |
| The Run Book is unbound, failed, unknown, or missing the exact task | Return to the parent core Run Book handoff. Stop before Data Loader steps and never create or submit a duplicate to bypass the state. |
| Data Loader metadata, DAT, or Task Hook validation fails | Stop before preview or upload and report the exact command stage and redacted structured error. Distinguish an agent workflow blocker from a helper rejection or a submitted Fusion job failure. Correct or regenerate through core.data-loader without bypassing validation. |
| The immutable-artifact approval is missing, declined, or invalidated | Stop before the UCM upload. |
| A UCM upload or initiateDataLoad request may have been dispatched | Do not retry automatically; preserve the initiation identifiers and reconcile from durable evidence. |
| CpqChargeSetSync initiation fails or is indeterminate | Preserve the approved artifact context and redacted initiation diagnostic; do not retry automatically. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Prompt direction is unsupported or ambiguous | Stop before live steps and request confirmation of Fusion as source and CPQ as target. |
| input_validation | DAT, archive, or required approval is invalid | Correct the source through core.data-loader or complete a new approval lifecycle; do not request charge-set rows. |
| catalog_or_metadata_mismatch | A required business object is not an exact registered match | Correct the business-object selection and regenerate the DAT through core.data-loader. |
| process_failed | CpqChargeSetSync initiation is rejected or indeterminate | Review the redacted initiation result; do not retry automatically. |
| approval_blocker | A write requires fresh approval or a prior write is indeterminate | Stop until explicit approval or reconciliation is available. |

## Disclosure and Refusal Rules

- Return the core Data Loader approval-required report without adding a duplicate task-level approval prompt.
- Do not expose tokens, credentials, authorization headers, UCM content, or raw Data Loader and CPQ response bodies.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| DATA_LOADER_SYNC.SUBMIT_CHARGE_SET_LOAD | step | 30 | execution_gate | submitted->DATA_LOADER_SYNC.DONE_SUCCESS;failed->DATA_LOADER_SYNC.HANDLE_ISSUE | DATA_LOADER_SYNC.VALIDATE_CHARGE_SET_LOAD | stop | Upload the approved CpqChargeSetSync archive and initiate the fixed IMPORT_AND_LOAD action |
| DATA_LOADER_SYNC.DONE_SUCCESS | terminal | 40 | terminal | none | DATA_LOADER_SYNC.SUBMIT_CHARGE_SET_LOAD | stop | The Data Loader initiation succeeded |
| DATA_LOADER_SYNC.HANDLE_ISSUE | step | 100 | error_handler | handled->DATA_LOADER_SYNC.RETURN_ISSUES | none | stop | Any metadata, validation, approval, or initiation issue |
| DATA_LOADER_SYNC.RETURN_ISSUES | terminal | 110 | terminal | none | none | stop | A blocking issue was classified and disclosed |
