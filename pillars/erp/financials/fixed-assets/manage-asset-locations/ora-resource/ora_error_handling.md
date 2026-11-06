# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| System Controls row or matching enabled LOC# structure is unavailable | Stop and report the Asset Location structure setup dependency. |
| Asset Location segment-value validation is attempted outside the required Fixed Assets value-set workflow | Stop before artifact preparation. Re-run `resolve_location_segment_values` through `manage-fixed-assets-flexfield-value-sets`; do not treat a direct generic value-set REST result as valid evidence. |
| BOSS Asset Location read is denied, unavailable, malformed, or incomplete | Do not retry BOSS or infer no existing location. Obtain one new same-environment `FA_MANAGE_FIXED_ASSET_LOCATION` setup-data export and inspect its complete Asset Location CSV as the duplicate-check source. Stop when that export fails, is incomplete, or has ambiguous rows. |
| Value-set evidence is incomplete, stale, or from another environment or structure | Report affected values and CSV records as unverified. Preserve the parent batch and stop before archive preparation until complete current evidence is restored. Do not classify values as missing or create prerequisites from incomplete evidence. |
| Location KFF value is missing, disabled, ineffective, ambiguous, or parent-unmapped | Identify the exact value set, value, and dependent parent value when applicable. If prerequisite creation is authorized, preserve the parent request fingerprint, route only the missing values through Manage Fixed Assets Flexfield Value Sets, and automatically resume fresh Asset Location validation after verified completion. Otherwise ask once for prerequisite authorization. Do not create the Asset Location until fresh verification passes. |
| Required FA_LOCATIONS DFF segment is absent or evidence is from another batch | Report the batch-current export process identity plus its Prompt, SegmentCode, ColumnName, and ValueSetCode. Stop before ZIP creation until the user supplies the exact value and the DFF definition is exported for the current immutable batch; do not treat a blank context as a waiver of a global segment or use a prior-batch definition. |
| Invalid dates, KFF segments, DFF context, or duplicate location | Stop before persistence and report the failing field or combination. |
| A Create request matches an exact existing Asset Location | Stop before artifact preparation and request an explicit update-versus-new decision. A previous or later import approval does not authorize converting Create to Update. |
| Attempt to delete an existing Asset Location | Stop and direct the user to disable it. |
| Parent location is disabled | Remove the mapping child row, report Enable Location to assign location mapping, and stop that row. |
| HR code and set do not resolve | Reject the row with FA_INVALID_HRCOMBINATION. |
| Asset Location segments do not resolve during import | Log Unable to find Location with segment values and stop further mapping-row processing in that CSV loop. |

## Prerequisite Continuation

After a prerequisite change is verified by its owning workflow, obtain fresh
structure, value-set, existing-location, and DFF evidence for the retained
parent batch. A prerequisite approval does not approve the later Asset
Locations artifact or import.

This skill ends at `validated_for_import`. The calling workflow follows the
parent Fixed Assets approval gates and uses `core.data-loader` for submission.
After acceptance, hand the target, immutable archive identity, request ID, and
child-specific verification criteria to the Fixed Assets parent. The parent
routes status and ProcessLog retrieval through `core.data-loader`, applies
fresh target-state verification, shows the Post-Execution Verification Preview,
and controls dependent-task progression.

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Dates, KFF, DFF, or required mapping input is invalid. | Correct the input and restart validation. |
| Dependency or reference mismatch | System control, LOC# value-set member, parent location, HR/TCA source, or mapping identity cannot resolve. | Resolve the exact prerequisite through its approved task. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| On validation failure | Failing business key or row, reason, and required correction; never expose credentials or tokens. |
| Existing-location Create collision | `{AssetLocation}` already exists in `{StructureInstanceCode}`. The requested operation is Create. Choose: (1) Update the existing location's Enabled Flag, Effective Start Date, and/or Effective End Date; or (2) provide a new Asset Location identity to create. No artifact or import is permitted until the requester explicitly selects one option. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Display-only Manage Asset Locations mapping popup | Do not claim it creates or updates FA_LOCATION_MAPPINGS. |
| Missing lookup execution contract | Do not infer a direct REST call, browser path, or payload. |

## Batch Recovery

Report each invalid value or parent once with its affected record numbers. Only
confirmed missing or invalid values may enter the prerequisite handoff;
unverified reads stop for evidence repair. After prerequisite changes, collect
fresh references and existing locations for the retained parent batch.

Treat DFF export and lookup work as internal preparation. Report those details
only when they block the batch or when the user requests them.

## Validation and Execution Boundary

This graph returns read-only validation findings to the calling workflow.
VALIDATED means validated_for_import for the current stage, never a successful
Fusion import. Approval is not required to run Task Hook validation.
Subsequent approval, submission, and accepted-import handoff follow the
parent-owned continuation defined in Prerequisite Continuation above. The task
template/spec export starts
only at `MAL.PREPARE_ARCHIVE`, after the design node passes. Before calling
`shared.setup-export.task-level-export`, verify the ordered rule-result record
and batch-current DFF-definition evidence. Do not request an export, prepare an
archive, or continue to the import gate unless the prior input, reference,
dependency, operation, default, and design outcomes have passed and the DFF
evidence is complete for the target environment and immutable batch. The
operation outcome must be `create_new` or `update_existing`.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MAL.PREPARE_ARCHIVE | step | 60 | execution_gate | prepared->MAL.IMPORT_GATE;blocked->MAL.HANDLE_READINESS | MAL.ENFORCE_DESIGN | stop | Verify the completed validation sequence and batch-current DFF-definition evidence, then obtain and inspect the template/spec package for the immutable artifact. |
| MAL.IMPORT_GATE | decision | 70 | execution_gate | ready->MAL.VALIDATED;incomplete->MAL.HANDLE_READINESS | MAL.PREPARE_ARCHIVE | stop | Read-only design validation and immutable archive preparation are complete. Approval is owned by the surrounding Data Loader workflow. |
| MAL.HANDLE_INPUT | step | 80 | error_handler | handled->MAL.ISSUES | MAL.VALIDATE_INPUT | stop | Input is invalid. |
| MAL.HANDLE_DEPENDENCY | step | 90 | error_handler | handled->MAL.ISSUES | MAL.CHECK_DEPENDENCIES | stop | A dependency is blocked or ambiguous. |
| MAL.HANDLE_OPERATION_DECISION | step | 95 | error_handler | decision_requested->MAL.OPERATION_DECISION_REQUIRED | MAL.RESOLVE_OPERATION | stop | An existing exact location conflicts with the requested operation. |
| MAL.HANDLE_LOOKUP | step | 100 | error_handler | handled->MAL.ISSUES | MAL.RESOLVE_REFERENCES | stop | A required reference cannot resolve. |
| MAL.HANDLE_DESIGN | step | 110 | error_handler | handled->MAL.ISSUES | MAL.ENFORCE_DESIGN | stop | A design rule blocks the request. |
| MAL.HANDLE_READINESS | step | 120 | error_handler | handled->MAL.ISSUES | MAL.ENFORCE_DESIGN | stop | Validation evidence, DFF-definition evidence, template package, or immutable artifact required at this stage is incomplete. |
| MAL.VALIDATED | terminal | 130 | terminal | none | MAL.IMPORT_GATE | stop | Return validated_for_import for the current validation scope; no approval, submission or Fusion completion is implied. |
| MAL.ISSUES | terminal | 140 | terminal | none | none | stop | A request stopped for correction, dependency, lookup, design, approval, or process issue. |
| MAL.OPERATION_DECISION_REQUIRED | terminal | 145 | terminal | none | none | stop | No artifact or import is permitted until the requester explicitly selects Create-new or Update-existing. |
