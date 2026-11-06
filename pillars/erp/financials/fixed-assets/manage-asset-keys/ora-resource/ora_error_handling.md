# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| System Controls row or matching enabled KEY# structure is unavailable | Stop and report the Asset Key structure setup dependency. |
| Asset Key segment-value validation is attempted outside the required Fixed Assets value-set workflow | Stop before artifact preparation. Re-run `resolve_asset_key_segment_values` through `manage-fixed-assets-flexfield-value-sets`; do not treat a direct generic value-set REST result as valid evidence. |
| BOSS Asset Key read is denied, unavailable, malformed, or incomplete | Do not retry BOSS or infer no existing key. Obtain one new same-environment `FA_MANAGE_ASSET_KEY` setup-data export and inspect its complete `FA_ASSET_KEY.csv` as the duplicate-check source. Stop when that export fails, is incomplete, or has ambiguous rows. |
| Value-set evidence is incomplete, stale, or from another environment or structure | Report the values as unverified, retain the parent request, and stop before preview or import. |
| KEY# value is missing, disabled, ineffective, ambiguous, or parent-unmapped | Identify the exact value set, value, and parent. Route only that prerequisite through Manage Fixed Assets Flexfield Value Sets when authorized; resume only after fresh verification. |
| Date ordering or duplicate validation fails | Stop before persistence and report the field or exact combination. |
| A Create request matches an exact existing key | Stop before artifact preparation and request an explicit update-versus-new decision. A previous or later import approval does not authorize converting Create to Update. |
| Persisted key deletion is requested | Stop and direct the requester to disable the key. |

## Prerequisite Continuation

After a prerequisite change, obtain fresh structure, value-set, and
existing-combination evidence for the retained parent batch. Batch optimization
does not bypass the separate immutable-artifact approval gate.

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
| Input validation | Required input, date ordering, length, or immutable-field rule fails. | Correct the input and restart validation. |
| Catalog or dependency mismatch | System Controls, structure, value set, value, parent, or exact existing-key evidence cannot resolve. | Resolve through its approved task, then gather fresh evidence. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| On validation failure | Failing business key or row, rule, and required correction; never reveal credentials or tokens. |
| Existing-key Create collision | `{AssetKey}` already exists in `{StructureInstanceCode}`. The requested operation is Create. Choose: (1) Update the existing key's Enabled Flag, Effective Start Date, and/or Effective End Date; or (2) provide a new Asset Key identity to create. No artifact or import is permitted until the requester explicitly selects one option. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing or ambiguous structure/value-set/combination contract | Do not invent a delimiter, value set, endpoint, payload, or validation result. |
| Persisted key deletion | Do not submit a delete action. |

## Batch Recovery

Report each invalid value or dependent parent once with its affected record
numbers. Only confirmed missing or invalid values may enter the prerequisite
handoff; unverified reads stop for evidence repair. After prerequisite changes,
collect fresh references and existing combinations for the retained parent batch.

## Validation and Execution Boundary

This graph returns read-only validation findings to the calling workflow.
VALIDATED means validated_for_import for the current stage, never a successful
Fusion import. Approval is not required to run Task Hook validation.
Subsequent approval, submission, and accepted-import handoff follow the
parent-owned continuation defined in Prerequisite Continuation above. The task
template/spec export starts
only at `MAK.PREPARE_ARCHIVE`, after the design node passes. Before calling
`shared.setup-export.task-level-export`, verify the ordered rule-result record.
Do not request an export, prepare an archive, or continue to the import gate
unless it records the exact prior outcomes `valid`, `resolved`, `ready`,
`create_new` or `update_existing`, `applied`, and `pass` for the input,
reference, dependency, operation, default, and design nodes respectively.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MAK.PREPARE_ARCHIVE | step | 60 | execution_gate | prepared->MAK.IMPORT_GATE;blocked->MAK.HANDLE_READINESS | MAK.ENFORCE_DESIGN | stop | Verify the completed validation sequence, then obtain and inspect the template/spec package for the immutable FSM artifact. |
| MAK.IMPORT_GATE | decision | 70 | execution_gate | ready->MAK.VALIDATED;incomplete->MAK.HANDLE_READINESS | MAK.PREPARE_ARCHIVE | stop | Read-only design validation and immutable archive preparation are complete. Approval is owned by the surrounding Data Loader workflow. |
| MAK.HANDLE_INPUT | step | 80 | error_handler | handled->MAK.ISSUES | MAK.VALIDATE_INPUT | stop | Input is invalid. |
| MAK.HANDLE_DEPENDENCY | step | 90 | error_handler | handled->MAK.ISSUES | MAK.CHECK_DEPENDENCIES | stop | A dependency is blocked or ambiguous. |
| MAK.HANDLE_OPERATION_DECISION | step | 95 | error_handler | decision_requested->MAK.OPERATION_DECISION_REQUIRED | MAK.RESOLVE_OPERATION | stop | An existing exact key conflicts with the requested operation. |
| MAK.HANDLE_LOOKUP | step | 100 | error_handler | handled->MAK.ISSUES | MAK.RESOLVE_REFERENCES | stop | A required reference cannot resolve. |
| MAK.HANDLE_DESIGN | step | 110 | error_handler | handled->MAK.ISSUES | MAK.ENFORCE_DESIGN | stop | A design rule blocks the request. |
| MAK.HANDLE_READINESS | step | 120 | error_handler | handled->MAK.ISSUES | MAK.ENFORCE_DESIGN | stop | Validation evidence, archive guard, template package, or immutable artifact required at this stage is incomplete. |
| MAK.VALIDATED | terminal | 130 | terminal | none | MAK.IMPORT_GATE | stop | Return validated_for_import for the current validation scope; no approval, submission or Fusion completion is implied. |
| MAK.ISSUES | terminal | 140 | terminal | none | none | stop | A request stopped for correction, dependency, lookup, design, approval, or process issue. |
| MAK.OPERATION_DECISION_REQUIRED | terminal | 145 | terminal | none | none | stop | No artifact or import is permitted until the requester explicitly selects Create-new or Update-existing. |
