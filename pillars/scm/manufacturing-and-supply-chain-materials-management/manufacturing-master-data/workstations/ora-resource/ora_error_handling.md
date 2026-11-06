# Workstations Error Handling

## Source Evidence

| Source | Verified Fact | Source Anchor |
|---|---|---|
| Oracle Setup Task CSV Imports REST API | Task CSV import status values are NOT_STARTED, IN_PROGRESS, COMPLETED, COMPLETED_WARNINGS, and COMPLETED_ERRORS. ProcessLog contains processing details for each imported business object and can be downloaded from the import-process result. | [Get an import process result](https://docs.oracle.com/en/cloud/saas/applications-common/26b/farca/op-11.13.18.05-setuptaskcsvimports-taskcode-child-setuptaskcsvimportprocess-processid-child-setuptaskcsvimportprocessresult-processid-get.html); [Get an import process log](https://docs.oracle.com/en/cloud/saas/applications-common/26b/farca/op-setuptaskcsvimports-taskcode-child-setuptaskcsvimportprocess-processid-child-setuptaskcsvimportprocessresult-processid-enclosure-processlog-get.html) |

## Error Situations

| Situation | What Should Happen |
|---|---|
| A required create field is absent or violates a sourced length limit | Stop before FSM package assembly. Identify the exact missing or invalid field. |
| The organization is not confirmed as a manufacturing plant, or the Work Center cannot be confirmed as one existing parent Work Center in that organization | Stop. Do not select an organization or Work Center by position or invent a lookup result. |
| The requested Workstation code is known to be in use in the target organization | Stop. Require a new code or an approved FSM update contract. |
| The requested Workstation Name is known to exist within the selected plant/organization, or its supported duplicate preflight cannot complete | Stop creation. Require a unique name and the documented duplicate-check contract. WIS-WS-004 defines the create duplicate-name error; WIS-WS-006 is update behavior, not permission to switch this graph to update. |
| An equipment-resource-instance association is inactive, not equipment type, belongs to another organization or Work Center, or is already associated with another Workstation | Stop the association. Do not infer task-CSV partial acceptance or import outcome from this entity rule. |
| The exact selected Workstations CSV authoring findings are missing or failed | Stop accepting the affected input. Identify the exact missing/failed chosen-format, field, parent/language, lookup or unchanged-manifest finding. Do not require all parser spellings, translation internals or future error-order results as local authoring prerequisites; keep actual import, recovery and saved-value results separate from local authoring findings. |
| A future approved FSM import reaches COMPLETED or COMPLETED_WARNINGS | Treat COMPLETED as success and COMPLETED_WARNINGS as success with warnings. Retrieve and retain ProcessLog; it contains processing details for each imported business object. |
| A future approved FSM import completes with errors | Treat COMPLETED_ERRORS as an issue outcome. Retrieve the process log; do not automatically resubmit the ZIP. |
| A future approved FSM import remains NOT_STARTED or IN_PROGRESS after the polling window | Stop polling and report the task code, process identifier, and last known status. Do not recheck the same process until a user explicitly asks to do so. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before handing a validated archive to the selected importer | Exact selected target/task, immutable package identity and complete validation; require core.data-loader to own subsequent current operation approval. Its persisted preflight and unchanged Task Hook-approved envelope are authoritative at submission; do not manufacture approval in this task graph |
| Returning successful task-rule checks | Return the rule findings only; no task-local upload/import occurs and no saved-value/runtime success is inferred |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WORKSTATIONS.IMPORT_APPROVAL | decision | 25 | execution_gate | approved->WORKSTATIONS.DONE;incomplete->WORKSTATIONS.RETURN_ISSUES | WORKSTATIONS.DESIGN_CREATE_CONTRACT | stop | Verify the mandatory core.data-loader handoff preserves the exact immutable artifact and delegates post-validation approval to its existing Task Hook/preflight workflow; do not request an approval envelope before task-rule evaluation finishes and do not perform a mutation. |
| WORKSTATIONS.DONE | terminal | 30 | terminal | none | WORKSTATIONS.IMPORT_APPROVAL | stop | Return successful documented task-rule checks and delegated approval boundary only; current submission approval remains with core.data-loader and this terminal is not import or saved-value proof. |
| WORKSTATIONS.RETURN_ISSUES | terminal | 40 | terminal | none | none | stop | Return exact unresolved authoring contract or failed rule; no mutation or implicit local readiness. |

## Delegated Approval Contract

core/data-loader/SKILL.md, Execute a data-loading request steps 5-7 and Task Hook routing, requires all task rules to pass before building the task preview and obtaining upload approval. It owns the unchanged Task Hook-approved envelope and persisted preflight; this resource neither generates one nor calls a writable helper.

The complete core/data-loader/scripts/upload_and_initiate.py functions load_preflight_envelope (297-315), _approved_artifact (2226-2248), _require_approved_task_validation (2177-2204), and upload_approved_preflight (2289-2423) establish the existing representation: preflight schema/fingerprint; approvedArtifactPath or archivePath; uploadFileName; archiveSha256; host/environment/runID and taskRouted context; Task Hook envelope preview and approval. The helper requires approved true, matching taskCode/executionRoute, and finalData.archiveSha256 matching the actual immutable bytes through approved_loader_payload in core/data-loader/task-validator/scripts/task_rule_execution.py:667-685. Missing or mismatched approval/artifact/context blocks submission. Reading these functions establishes the delegated contract only, not a current approval or permission to call upload_approved_preflight.
