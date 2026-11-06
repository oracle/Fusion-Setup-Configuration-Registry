| Child create or update load completes successfully and saved details are requested | Execute verify_site_dedicated_location_relationship. Show the saved customer/site and parent/child linkage with the complete loader report, counts and request ID when available. For updates compare requested before/after values on the same child. Report verification failure separately from load status. |

Source: the task Data Loader Mutation Workflow and current core.data-loader immutable-artifact and result contracts.

Additional source: the supplied Site Dedication CSV import request, observed Data Loader authentication failures, and live FSCR_CDRM Data Loader metadata verified on 2026-10-12. That metadata registers siteDedicatedLocations as a child of stockingLocations and requires PartySiteId, PartySiteNumber, and RestAction for new child records.

## Error Situations

The parent's edit/delete restriction is supplied by the task owner: assigned Field Technician stocking locations cannot be edited or deleted by this task. Verify assignment state before dispatch using check_stocking_location_technician_assignment; this is separate from location-type validation.

Scope: Task Nodes validate captured Data Loader sources and return results to Task Hook. All parent/child creates, updates and deletions use core.data-loader; read-only reference and verification checks cannot authorize direct mutations. Unsupported operation rules block submission.

| Situation | What Should Happen |
|---|---|
| Parent edit/delete target is assigned to a field technician, or assignment state cannot be verified | Stop before mutation with the assignment-check outcome. Never remove or change technician assignments to make the parent operation pass. |
| Data Loader child deletion fails or returns an unclear outcome | Stop without replay. Reconcile the original child through read-only absence verification; retain redacted diagnostics and require a separately approved retry. Parent and customer master-address changes are outside this workflow. |
| The import mode is not REST or the business object is not stockingLocations | Stop resource routing and correct the Data Loader REST configuration. |
| A required create field is missing or invalid | Stop source validation and correct the documented required fields before preparing an import artifact. |
| Windows OAuth storage reports that pywin32 is missing | Stop before upload. Install a compatible pywin32 wheel into the interpreter used by Data Loader and verify win32api, win32cred, and win32security imports before resuming preflight. |
| OAuth trust enrollment is missing or cancelled | Stop before upload. Collect the user-supplied Fusion URL, environment name, and OAuth Client ID together and use the core OAuth trust-enrollment workflow; resume Data Loader preflight only after enrollment succeeds. |
| A Site Dedication child import fails contract validation | Stop before submission. Validate the registered stockingLocations root and siteDedicatedLocations child against the live Data Loader template. The confirmed mandatory child create fields are PartySiteId, PartySiteNumber, and RestAction=POST; the parent must be resolved exactly. When a customer/site pair is supplied, resolve it through the documented customer-site contract and require a matching active result. Confirm the site relationship is absent; do not create or modify a parent as part of this child-only import. |
| Data Loader parent update fails, times out, or returns an unclear result | Stop without replaying upload/initiation. Classify the response, retain redacted evidence, and reconcile the resolved item through read-only GET before fresh immutable-artifact preparation and its required submission authorization. |
| Data Loader Site-Dedicated Location child update has no resolved existing child, lacks PartySiteId for a customer-site association, fails, times out, or returns an unclear result | Stop without creating a child or replaying the load. Classify the result, retain redacted evidence, and reconcile the exact resolved child through read-only GET before fresh immutable-artifact preparation and its required submission authorization. |
| Location-type PATCH is rejected because the stocking location is assigned to a field service technician | Stop with the returned Fusion business error. Do not retry or change assignments through this workflow. Resolve the technician assignment outside this task, then start a new update request and approval cycle. |
| Organization or subinventory is absent, ambiguous, or inconsistent with supplied identifiers | Stop input/reference validation with the resolver and affected rows. Obtain an exact identifier or valid organization-scoped subinventory; never choose the first result or resolve globally. |
| Customer/site lookup is absent, inactive, ambiguous, or inconsistent with a supplied PartySiteId | Stop before preparing or dispatching the child change. Show the conflicting input fields and resolve one authoritative active customer-site pair. Do not substitute PartyId, address text, or another customer's site. |
| A requested child-create relationship already exists | Report the saved duplicate and stop create. An update requires the existing child selector and its own selected workflow; do not silently use PATCH or upsert. |
| Captured child-only source fails hierarchy validation | Report the captured section/linkage error using current Data Loader metadata. Prepare a corrected immutable artifact and rerun Task Hook before approval. Require the exact prepared ZIP for Task Hook validation. Never repair a child-only source by adding a parent data operation. |
| Prepared artifact or core preflight state is unavailable or inconsistent | Stop before upload. Use core to prepare and validate a fresh immutable artifact and its preflight/Task Hook envelopes. Never fabricate approval fields, repair an approved envelope or replay an uncertain submission. |
| Data Loader succeeded but child readback is absent or differs | Report load success separately from relationship verification failure, including expected/saved differences and request ID. Reconcile through safe reads; do not repeat the load. |

## Disclosure Rules

For an unresolved {MESSAGE} wrapper, read the linked Data Loader object-error log and disclose its resolved business message as supplemental detail without replacing the helper report. Multiple LOV_Subinventory rows indicate ambiguous selection: resolve and include OrganizationId, verify the organization-scoped subinventory, and prepare a corrected source. Do not assume OrganizationName alone constrains the loader LOV.

Source: the user's task-specific request to always display Stocking Locations and Site Dedication Data Loader results. Reporting is owned by the task's Data Loader Results workflow, not a pre-upload Task Node.

| Gate | What Must Be Shown |
|---|---|
| Data Loader Site-Dedicated Location deletion | Show the complete helper report and, when results are requested, actual load status/counts and available request ID. Verify child absence and parent/sibling preservation separately. Already absent without submission is a no-op. Uncertain load followed by absence is reconciled absence, not verified load success. Do not delete the customer master address. |
| Validation, mapping, or submission failed | Show the complete Data Loader helper report for the failed stage and its corrective action. Do not suppress errors or claim that data was loaded. |
| Initiation accepted | Show the helper's complete Data Load In Progress report and retain its returned request ID. Do not poll automatically; use the Data Loader status workflow when status/results are explicitly requested. |
| Load status checked | Show the helper's complete report with exact Data Set name, status, Total, Loaded, Failed, returned errors, and applicable error-log links. Preserve partial successes and failures. |
| Load remains pending at the bounded wait limit | Show the last available status and the next status-check action. Do not claim completion, continue indefinitely, or retry the import. |
| Child-only Site Dedication load succeeds | Attribute the loaded record to siteDedicatedLocations under the existing parent; do not claim the parent stockingLocations record was loaded or recreated. |
| Combined parent-child status is reported | Distinguish aggregate data-set success from per-component evidence. Do not invent separate parent and child counts or successes. |
| Parent load succeeds and created details are requested | Read back the exact organization/subinventory pair through check_stocking_location_identity. Show saved StockLocationName, organization, subinventory, condition/type meanings, and coordinates with counts and environment. Report differences as verification failures; do not restate input as saved data. |
| Child create or update load completes successfully and saved details are requested | Execute verify_site_dedicated_location_relationship. Show saved customer/site and parent/child linkage with the complete loader report, counts and available request ID. For updates compare requested before/after values on the same child. Report verification failure separately from load status. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Validation fails | Do not submit data, retry an import, or mutate Fusion setup data. |
| Only initiation or pending status is available | Do not state that the stocking location or its site dedication loaded successfully. |
| Authentication or Site Dedication contract validation is blocked | Do not bypass Data Loader with a direct REST import, substitute a parent business object, or infer a successful load from a prepared file. |
| Identity unresolved or conflicting | Do not submit, select the first candidate, change environment, or mark mandatory identity lookups not applicable because Data Loader header validation passed. |
| Correcting a failed import | Reconcile existing target records through the selected read-only workflow before fresh validation. Do not replay a submission or reuse the old preflight for changed bytes. Validate the corrected immutable artifact through a fresh Task Hook cycle and leave submission authorization to core.data-loader. |

## Immutable-Artifact Validation Gate

Use the exact final immutable upload artifact prepared by core for Task Hook validation. Captured records mean its parsed rows and validated operation/schema/mapping/target context. Require prepared DAT/ZIP bytes at this gate; do not reread the original source or edit approved bytes. Validate organization/subinventory, requested values, explicit RestAction, operation-specific keys, child linkage and preservation rules. Header validation alone is insufficient. A correction requires core to prepare a new artifact and rerun all applicable validation before approval.

Return ordered rule results to Task Hook; passed means validation complete, never approved, submitted or loaded. Core owns its immutable artifact, persisted internal preflight/Task Hook envelopes, preview and single approval workflow. After approval, core verifies the retained bytes and context without serializing again or repeating lookups. Missing or modified artifacts and context mismatch block upload. Keep core artifacts/envelopes in private ignored staging outside the project; retain them after partial or uncertain failure and let core clean up after accepted initiation. Record only permitted redacted outcomes in project evidence.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RCL.SLOC.GATE | decision | 13 | execution_gate | passed->RCL.SLOC.READY;no_op->RCL.SLOC.NOOP;failed->RCL.SLOC.ISSUES | RCL.SLOC.DEFAULT | stop | Require captured keys/action/values to match selected operation and all applicable checks; all rows noOp returns no_op, mixed noOp/actionable fails, otherwise passed; exact immutable artifact required; no approval prerequisite |
| RCL.SLOC.READY | terminal | 14 | terminal | none | RCL.SLOC.GATE | stop | Captured-record validation passed; return results to Task Hook without requesting approval or authorizing submission |
| RCL.SLOC.NOOP | terminal | 15 | terminal | none | RCL.SLOC.GATE | stop | All captured targets verified no-op; return no-op results and stop without approval, upload or initiation |
| RCL.SLOC.ISSUES | step | 16 | error_handler | reported->RCL.SLOC.RETURN_ISSUES | none | stop | Routing, authentication, identity, mapping, source, or child contract validation failed |
| RCL.SLOC.RETURN_ISSUES | terminal | 17 | terminal | none | RCL.SLOC.ISSUES | stop | An issue was reported |
