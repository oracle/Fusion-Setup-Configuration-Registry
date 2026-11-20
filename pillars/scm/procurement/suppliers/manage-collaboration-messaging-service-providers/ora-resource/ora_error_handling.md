# Service Providers FSM Task-CSV Import Gates and Error Handling

## Native Definition Creation Results

| Situation | What Should Happen |
|---|---|
| New external-format name is absent but its identification tuple already exists | Return an identification conflict before native preparation. A new name alone does not establish insertion because FSM can bind the equivalent format to its existing name. Keep the strict greenfield request; never count it as a new format |
| A requested external-format path has no column in the current native profile | Retain the business input and disclose the exact representation gap; do not drop the field, manufacture a column or switch write routes |
| Native message processing succeeds but exported file/scalar comparison fails | Report processing succeeded and saved-state verification failed with the specific differing field. Do not substitute an identity-only GET, omit an intended file or replay the import |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.EXTERNAL_EXPORT_VERIFIED | terminal | 99 | terminal | none | CMKSP.EXTERNAL_EXPORT_STATE | continue | Return successful native external-definition creation and exported intended-field comparison bound to the actual current request, final archive and completed import. State the exact creation scope; no collaboration-message transformation or delivery claim Apply Business Name Presentation. |
| CMKSP.MESSAGE_EXPORT_VERIFIED | terminal | 102 | terminal | none | CMKSP.MESSAGE_EXPORT_STATE | continue | Return native exported intended-field and literal-file comparison bound to the approved message row and successful current FSM import. Report strict creation and unrelated-row preservation separately; no transformation or business-delivery claim Apply Business Name Presentation. |

Oracle's task-CSV import flow starts an import with the task code, monitors the
returned process identifier, and retrieves the process log after completion.
The process log is the evidence for whether the import contains the required
setup data. [S1]

## Error Situations

| Situation | What Should Happen |
|---|---|
| A CMK lookup has no route binding in the selected task context | Apply Runtime Route Handoff and Recovery in ora_reference_lookups.md before declaring the binding missing. Preserve the customer's attachment and known project/environment; do not restart intake or ask for a technical URL. If recovery cannot establish provenance, report input validation, route_binding_missing or route_binding_unverified, and request_sent=false. No HTTP response exists and feature state remains unverified. |
| A recovered route was read successfully | Continue the owning resolver's normal field, scope, identity and pagination checks; do not call the rollout ready merely because the GET returned HTTP 200. Report only the tested collection and scope. |
| ORA_CMK_B2B_DOCUMENT_SETUP returns EnabledFlag: N on the operation host | Apply Feature State Presentation for a confirmed disabled feature. Stop before creating an export process or approving, uploading or submitting an import |
| ORA_CMK_B2B_DOCUMENT_SETUP is absent, stale, ambiguous, or unreadable on the operation host | Apply Feature State Presentation for an unverified feature. Stop before export or import; recheck only through the declared read-only resolver |

| ZIP is unreadable, not FSM setup data, or does not identify this task | Stop before upload and request a completed export for Manage Collaboration Messaging Service Providers. Retain the exact task-code mismatch in sanitized diagnostics |
| Preflight target differs from the intended environment | Stop before upload; select the intended target and repeat preflight for the same immutable ZIP |
| Data Loader preflight or Task Hook validation fails | Stop before approval; correct the reported validation issue and rerun the affected read-only gate |
| Upload or import submission has an uncertain result | Do not replay the write; retain the returned identifiers and reconcile through the selected import-status route |
| Import process completes with errors or warnings | Retrieve and retain the ProcessLog or result report; correct the documented errors before a new approved import |
| Import process polling times out | Stop polling. Apply Business Name Presentation: report the business task name, last status, elapsed wait and safe next action; retain the exact task code and process identifier in required operational diagnostics and disclose them when required. Resume status retrieval only when requested |

## Feature State Presentation

These FSCR rules govern presentation only; the existing feature resolver, execution scope and approval
gates remain authoritative.

| Situation | What Should Happen |
|---|---|
| Naming the feature in a customer message | Use Simplified B2B Messaging (Gen2). For the Opt In Features selection, use the exact label Simplify Configuration and Processing for B2B Messaging. Explain a technical code only when the user asks or needs diagnostic details |
| The existing resolver confirms the feature is enabled | If a progress message is needed, say "Simplified B2B Messaging (Gen2) is enabled in {environment}." Continue the existing workflow checks; feature enablement alone does not establish task completion |
| The existing resolver confirms the feature is disabled | Say "Simplified B2B Messaging (Gen2) is disabled in {environment}. The requested {operation} for Service Providers is blocked. Have an authorized administrator enable Simplify Configuration and Processing for B2B Messaging in Opt In Features and wait for opt-in processing to finish, then retry." Fill operation with the actual requested operation. Enabling the feature requires its separate authorized workflow; never enable it automatically |
| The existing resolver cannot establish current feature state | Say "We could not verify whether Simplified B2B Messaging (Gen2) is enabled in {environment}. The requested {operation} for Service Providers is blocked until this check succeeds." Include the sanitized reason and safe next step for the actual failure; do not call an absent, stale, ambiguous or unreadable result disabled |
| Reporting the scope of a feature blocker | State only the selected task and operation governed by the existing feature gate. Do not claim that all CMK tasks or classic/Gen1 messaging are disabled, and do not substitute a classic, browser or direct API execution route |
| Retaining technical evidence | Keep ORA_CMK_B2B_DOCUMENT_SETUP, FeatureType, EnabledFlag, selected host and read time in sanitized diagnostics and rule results. Do not remove or rename technical query values. A code appearing in diagnostics is an identifier, not an error by itself |

## Opt-In Recovery Steps

1. Navigate to **Navigator → My Enterprise → Offerings**.
2. Select the **Procurement** offering, then select **Opt In Features**.
3. Find **Simplify Configuration and Processing for B2B Messaging**.
4. Select its enable icon and complete the opt-in flow.
5. Wait for the opt-in migration or background processing to finish.
6. Rerun the Service Providers export.

## Connection Verification Failures

| Situation | What Should Happen |
|---|---|
| A previously successful connection import is resumed | Preserve its processing result and approved immutable intent. Run post_import_verify_connection through the declared graph; do not request another import approval or resubmit the connection. Report setup as verified only after all intended target fields match. |
| Verification cannot read the declared collection or metadata | Classify auth/authz, transport/environment or Fusion API according to the actual failure. Retain successful import processing separately. Missing or incompatible source/target schema is input validation; do not use a browser or guessed endpoint to bypass it. |
| Target row is absent, ambiguous or different | Return blocked verification with field labels and sanitized comparison coverage. Do not silently correct the target, create another name or claim setup complete. A corrective mutation requires a separate explicit intent and the normal immutable-package approval workflow. |
| Connection verification read times out | Preserve environment, resolver, request fingerprint, last status, elapsed wait and next offset in sanitized diagnostics, with raw rows private. Return process timeout; resume the same query-bound read after revalidation, never replay import. |


## Customer Setup Review

| Situation | What Should Happen |
|---|---|
| Setup request matches an existing connection | Say the requested connection already exists and supplied settings were verified. List preserved unspecified settings once under retained settings, using business labels; no clear/preserve question solely for a blank input and no import approval for a no-op. Report requested-state verification separately from any historical strict-import mismatch. |
| New connection is needed | Present one concise planned create to the invoking Run Book; retain valid inputs and tri-state evidence. Continue only through existing creation/template/Data Loader gates. The create_needed terminal is a handoff, not proof that a record was created. |
| Explicit values differ or explicit clearing is requested | Group meaningful differences and independent missing decisions into one review where possible. Show current/requested business values in the authorized private review, exact target and supported operation. Explain an unsupported update/clear as that precise gap, without asking the customer to write a technical prompt or reconfirm a clear intent already supplied. |
| Attachment cell is blank | Use Business Attachment Input Semantics. Do not equate it with a clear request, raise an optional-field question or edit the existing setting. A populated approved FSM CSV and strict post-import verification retain their original semantics. |
| Live lookup fails | Report the actual failure class and resume step. Do not label customer data invalid because authentication, transport, permissions or schema validation failed. |


## Outbound Delivery Selection Recovery

| Situation | What Should Happen |
|---|---|
| A provider-owned delivery method is missing from a null-provider-only list | Do not ask the customer to select a replacement from that incomplete scope. Use the source-backed selected-provider-or-unassigned resolver and current metadata qualification first; preserve the original method and all other valid inputs. |
| Requested method is absent from the complete qualified provider scope | For predefined_business_event_fsm apply its current witness qualification; a missing provider-owned delivery row alone is not absence and must not hand off to delivery-method creation. Outside that selected branch, preserve the method, provider and supplied transport settings and hand ensure_delivery_method_setup intent back to the invoking Run Book for the standalone delivery graph. Email and standard File Export use their selected DM4/DM5 preparation profiles; Business Event creation follows its failed-qualification restriction; ask only for missing applicable business inputs. Keep the original connection pending until the requested method is verified and the connection delivery lookup is refreshed. This continues the selected objective; it does not complete the connection. Do not substitute a different method or channel. |
| Scoped finder or required provider field is unsupported | Return the specific lookup-contract/schema blocker. Do not fall back to a broad/null-only list, another endpoint or a browser to force a selection. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Catalog mismatch or auth/authz | The exact feature item is absent, malformed, or unauthorized | Stop before side effects; verify release, feature identity, configured host, and read privileges through the declared route |
| Input validation | Archive shape, task identity, export provenance, or target binding fails | Correct the source or target and repeat preflight |
| Authorization | Fusion rejects the supported Data Loader operation | Obtain the required task-import and Data Loader privileges; do not guess role assignments |
| Process failed | The import process completes with errors | Retrieve ProcessLog, correct the reported data issue, and obtain approval for a new import |
| Process timeout | The import process has no completion result within the polling window | Preserve the process identifier and use the status retrieval path; do not resubmit |
| Approval blocker | The immutable ZIP, target binding, or task validation envelope is absent or changed | Repeat preflight and obtain approval for the exact validated ZIP |

## Business Name Presentation

Apply this FSCR implementer-message
policy to every task terminal and permitted progress, validation, approval and
error handoff. Preserve existing execution, approval and executor-report contracts.
The unchanged shared execution guide remains authoritative for required response
fields. Include its task code, rule identity, outcomes and resume context in
validation/execution responses; group them as Technical details when permitted.
The routine-message rules below never suppress these required disclosures.

| Situation | What Should Happen |
|---|---|
| Normal implementer-facing message | Identify the task by its business name and the requested component by its business name. State the actual outcome, practical blocker and one relevant next action. Omit internal task codes, rule IDs, resolver names and raw execution fields from routine messages; do not merely move them to the end of the same message |
| Business codes versus internal codes | Retain business identifiers the implementer needs, such as a supplied supplier number, account number, document name or connection name. Keep technical task and feature codes internal unless requested or required for diagnosis or an authoritative disclosure |
| Task selection or missing identity | Resolve task codes from the selected task and retained workflow context. If selection is ambiguous, offer business task names with offering or scope context; never ask the implementer to supply an internal task code |
| Task search, export or validation tool returns technical output | Consume task codes and raw CLI or validator fields internally. Present the matching task names, export or validation outcome and relevant next action. Do not paste a raw technical table or diagnostic into a normal message; preserve any exact executor-owned report required by its contract |
| Approval preview | Lead with the exact environment, operation, affected business objects and proposed changes. Preserve every required task, process and immutable-artifact disclosure from the owning approval workflow; place technical identifiers and artifact evidence in a separate Technical details section only when its layout contract permits. Never alter or suppress a Core Data Loader preview or introduce a second approval |
| Failure or timeout | Explain the affected business task, practical impact, last status and safe next action first. Retain exact task code, failure class, process or request references, elapsed wait and evidence in the existing sanitized operational record where required. Show necessary troubleshooting identifiers in Technical details when permitted, or directly when requested; preserve any mandatory exact error or executor report |
| Internal execution handoff and audit evidence | Retain exact task identity, rule IDs, action types, outcomes and sanitized evidence in the existing internal record under the shared execution guide. Keep task codes unchanged in manifests, catalogs, queries, payloads and compiled registries. This presentation policy grants no new persistence or execution authority |

## Customer Result Presentation

These FSCR task-result presentation rules apply to the current request. The invoking Run
Book owns any permitted consolidated journey report; this file does not start
another task, perform a lookup or bypass an executor's response contract.

| Situation | What Should Happen |
|---|---|
| Requested setup is verified but business-document exchange is untested | Report only the verified requested component and any remaining gaps. Provider, connection or partner-property success does not prove transmission, receipt, transformation or business acceptance. Return test needs to the invoking planner; without a separately qualified and approved test workflow, report business verification as not run or blocked and send no test message |
| Normal customer-facing handoff | Return a short customer_message in plain business language: what is ready for the requested scope, what was created/changed/reused, what still needs verification, and one relevant next action when any remains. Use the actual business document/direction and supplier/customer terminology. Apply Business Name Presentation. Use business labels for the requested component; keep internal task/rule codes and runtime fields out of routine messages. Retain technical terms only when requested or required by the owning approval/error contract. |
| A named connection was requested | Identify the actual requested connection name once in the result when it distinguishes this setup from an earlier run. A missing or unverified new name cannot be replaced by a general already-configured statement about the supplier. Derive the name from the validated current private input; do not hardcode any example name into the response. |
| Existing setup was reused | Say that the required settings were already in place and were checked, so no changes were needed for this scope. Never say created, enabled or imported when the actual disposition is reuse. Mention retained unspecified settings only when relevant to understanding a result or a meaningful business difference; do not list routine blanks or unchanged technical fields by default. |
| New setup was prepared but not imported | Say that the requested setup is prepared and awaiting the required approval, or name the exact missing decision. Do not describe a prepared package, ready plan or create_needed terminal as a completed configuration. Preserve the exact approval preview and authoritative Data Loader approval workflow. |
| An import was submitted or accepted | Preserve core.data-loader's required terminal response unchanged. Submission is in progress, not setup ready. Do not replace its required IDs, status information or next-check instructions with a friendly completion message. A concise business summary may be composed only at a later permitted journey handoff from actual verification evidence. Apply Customer Progress and Continuation Disclosure; make any explanatory progress handoff before delegation or at a later permitted response, never by altering the Core-owned initiation report. |
| Creation/change and target verification succeeded | State the actual action and verified result for this component, naming the requested connection when applicable. State no-change/reuse for other components only when their own current-request evidence supports it. Do not aggregate another task's status from this task terminal or translate multi-object package counts into new record counts. |
| Setup is verified but invoice processing has not been tested | Say that the requested messaging settings have been checked. Then say We have not yet tested receiving an invoice and processing it in Payables. Explain the next business milestone as a test invoice with agreed expected results. Do not say invoices will now arrive, that Payables processing is ready, or promise to send a test unless its separate approved test workflow exists. |
| Some selected components remain unverified | Describe exactly what is checked and what remains: for example, the invoice connection is checked while the supplier settings still need verification. Do not lead with overall ready or complete. Say whether any changes were made using actual side-effect evidence, not a canned no-changes sentence. |
| Validation failed because supplied data conflicts | Name the business field and problem, offer eligible choices when available and ask only for the necessary correction. Preserve valid supplied values. Do not ask the customer to resolve a resource contract, supply internal IDs or write an execution prompt. |
| A system read, permission or service check failed | Explain that the check could not finish and identify the practical impact and safe next action. Do not describe it as wrong customer data, expose a raw JSON/stack trace, or ask the customer to investigate repeated database IDs. The full actual failure class and recovery details remain in diagnostics; recovery uses only the declared workflow. |
| Summary belongs to a different attachment or earlier request | Reject it as evidence of current success. Report that the new requested setup has not yet been verified and resume the owning task's declared checks. Never relabel the earlier summary or say already matches your workbook without matching the current source fingerprint, actual requested identity and target. |
| Evidence and usage reporting | Keep the full operational record and token-usage figures in the prescribed project logs and reports. Provide one optional readable View setup details link at a permitted handoff, with technical evidence available behind it; do not make the link the explanation or put raw paths/token counts in the main business message. Supply technical or usage details directly when requested. |
| Mandatory diagnostic or approval disclosures apply | Preserve all required target, artifact, task/process identity, status and approval information in their authoritative operational result/preview. This presentation policy does not suppress mandatory safety disclosures, rewrite Data Loader terminal output, weaken explicit import approval or override a task-specific exact-error-message rule. |


## Customer Progress and Continuation Disclosure

These disclosures explain existing task state only. They add
no execution node, cross-task sequencing, export authorization, import batching
or change to Core Data Loader response, approval or monitoring contracts.

| Gate | What Must Be Shown |
|---|---|
| Every CMK terminal and permitted handoff | Apply Business Name Presentation and all applicable Customer Progress and Continuation Disclosure rules at every CMK terminal and permitted handoff. Preserve Core-owned reports unchanged. |
| Permitted CMK handoff before delegating an import | Explain which requested component the current immutable package contains and which requested components remain pending or unverified. Derive this from the retained current business requirement and actual package scope; do not ask the implementer to repeat the document or invent a fixed list. This disclosure is not another approval gate and does not replace or append to a Core-owned preview or report |
| Explain the submission boundary before the Core-owned terminal response | State that the submission response confirms initiation only. At this permitted earlier handoff, offer the plain-language continuation prompt: Check the import I just approved, verify the saved setup, and resume the remaining requirements in my business document through the supported workflow. The prompt is an example, not a required keyword, an approval, a new operation or permission to poll automatically |
| Core Data Loader returns accepted initiation | Return its complete prescribed Data Load In Progress report unchanged. Do not prepend or append a CMK progress summary, request another approval, poll status, start a dependent import or claim the business requirement is complete. Retain current-request scope and actual returned job references through existing private and sanitized project records; no new persistence mechanism or customer data in reusable guidance |
| A later explicit status or continuation request | Resolve the existing submission from retained current-request evidence through the declared status workflow. Do not ask the implementer to provide a known server-generated request ID or resubmit the business document. If the reference is missing or ambiguous, disclose that exact gap and ask only the material clarification; never guess or replay the import |
| A permitted handoff after status and saved-state verification | Distinguish submitted, processing succeeded, saved setup verified, pending, failed or blocked for the requested component. Summarize other requirements only from the invoking Run Book's current evidence, without running or sequencing another task from this task terminal. Keep unresolved dependencies visible and return the next action to the existing workflow; do not restart intake or infer delivery |
| Failure, uncertain outcome or partial success | Preserve verified completed components and the original business requirement. State the affected component, practical blocker and one safe next action. Never translate a failed or unverified job into completion, automatically retry it, or silently replace the target, package or business scope |

## Customer Message Examples

The examples are conditional patterns, not fixed responses. Fill business names
from the verified current request in the authorized user-facing message only.
Do not persist protected business labels in tracked repository/project reports.

| Situation | What Should Happen |
|---|---|
| This task verified an existing incoming invoice connection | The incoming invoice connection {actual requested name} already exists and matches your request. No changes were needed. Report supplier settings separately unless that task also returned current verified evidence. |
| Both selected setup components were verified and reused | The messaging settings for receiving your supplier invoices match your request. The required settings were already in place, so no changes were needed. We have not yet tested receiving an invoice and processing it in Payables. Use this combined example only when the invoking workflow has current evidence from both selected tasks. |
| A new incoming invoice connection was created and verified | Created and checked your incoming invoice connection {actual requested name}. State whether supplier settings were reused or changed only from their verified component result. Receiving and processing a test invoice is still a separate next milestone unless that test has passed. |
| The connection is checked but supplier validation stopped | Your incoming invoice connection is checked. We could not finish checking the supplier settings, so the full setup is not yet confirmed. Explain the actual safe next step and any changes already made from evidence. |
| New connection requested but only an old result is available | We have not yet verified the connection {actual new requested name}. The earlier result covers a different request. Continue through the declared current-request workflow; do not ask the customer to resupply unchanged business values. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Preflight result | Show the business task name, validated target and whether upload is approved or blocked. Preserve exact task identity and source ZIP evidence under Business Name Presentation and the owning preview contract |
| Accepted import | Returned request or process identifier and the next status-check path |
| Completed import | Process status and ProcessLog or result-report outcome |
| Duplicate provider error CMK:::CMK_B2B_PROVIDER_DUPE | Display only the message text, omitting the trailing error code: There's already a provider with that name. |
| Other failure or timeout | Failure class, redacted evidence, identifiers available for reconciliation, and one safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| The target opt-in state is not freshly verified as enabled | Do not start an export process, upload a package, initiate import, infer enabled state from prior exports, or enable the feature implicitly |
| A ZIP was changed after preflight | Do not reuse approval or submit the changed bytes |
| Target identity is different from preflight | Do not upload or initiate the import |
| Import outcome is uncertain | Do not submit a duplicate import |
| Process log reports errors | Do not claim configuration was imported successfully |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.IMPORT_GATE | step | 21 | execution_gate | ready_for_approval->CMKSP.READY_FOR_APPROVAL;blocked->RETURN_ISSUES | CMKSP.CHECK_CONNECTION_ACTIVATION | stop | Before upload or import initiation |
| CMKSP.READY_FOR_APPROVAL | terminal | 31 | terminal | none | CMKSP.IMPORT_GATE | continue | All read-only import gates have passed Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| RETURN_ISSUES | terminal | 117 | terminal | none | none | continue | A validation or execution gate blocks import. Apply Feature State Presentation when the blocker concerns the Simplified B2B Messaging feature. Apply Business Name Presentation. |
| CMKSP.PROVIDER_TYPE_REQUIRED | terminal | 59 | terminal | none | CMKSP.RESOLVE_PROVIDER_TYPES | continue | Provider Type is missing or invalid; return MISSING with live choices and preserved other inputs Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.ID_TYPE_REQUIRED | terminal | 60 | terminal | none | CMKSP.RESOLVE_PROVIDER_ID_TYPES | continue | Required ID Type is missing or invalid; return MISSING with live choices and preserved other inputs Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.CONNECTION_DOCUMENT_REQUIRED | terminal | 42 | terminal | none | CMKSP.CONNECTION_DOCUMENT | continue | Return MISSING: apply Connection Choice Presentation for Document in ora_reference_lookups.md; preserve other supplied values and derive Direction only after selection Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.CONNECTION_PROVIDER_REQUIRED | terminal | 43 | terminal | none | CMKSP.CONNECTION_PROVIDER | continue | Return MISSING: apply Connection Choice Presentation for Provider in ora_reference_lookups.md; retain selected Document and derived Direction when applicable; standalone delivery setup retains its provider request without asking for Document Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.CONNECTION_MESSAGE_REQUIRED | terminal | 44 | terminal | none | CMKSP.CONNECTION_MESSAGE | continue | Return MISSING: ask only for missing transformation mode, then apply Connection Choice Presentation for Message Definition in ora_reference_lookups.md; do not create a definition Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.CONNECTION_STATUS_REQUIRED | terminal | 45 | terminal | none | CMKSP.CONNECTION_STATUS | continue | Return MISSING: apply immediate Status choices under Connection Choice Presentation in ora_reference_lookups.md; retain resolved Document, Provider and Message Definition Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.CONNECTION_DELIVERY_REQUIRED | terminal | 46 | terminal | none | CMKSP.CONNECTION_DELIVERY | continue | Return MISSING for outbound only: apply Connection Choice Presentation for the requested primary/alternate Delivery Method in ora_reference_lookups.md, retaining applicable skip behavior Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.VERIFICATION_DONE | terminal | 24 | terminal | none | CMKSP.VERIFY_CONNECTION_STATE | continue | Return verified requested connection state and per-field coverage for the existing completed import. No claim of new insertion, whole-environment preservation or business invoice exchange; no import replay Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.REUSE_DONE | terminal | 27 | terminal | none | CMKSP.RECONCILE_SETUP | continue | Return reused_and_verified for this requested-state scope with matched and preserved coverage, no changes and no broader historical-import claim Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.CREATE_NEEDED | terminal | 28 | terminal | none | CMKSP.RECONCILE_SETUP | continue | Return create_needed and the validated private request/evidence to the invoking Run Book's existing create workflow; no mutation or import approval here Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.REVIEW_REQUIRED | terminal | 29 | terminal | none | CMKSP.RECONCILE_SETUP | continue | Return meaningful differences, exact missing decision or unsupported change and safe next action; no implicit update or create replay Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSP.DELIVERY_REUSED | terminal | 47 | terminal | none | CMKSP.DELIVERY_STATE | continue | Return reused_and_verified only for ensure_delivery_method_setup with current matched/preserved coverage. No import was required for this scope. Do not use this terminal for strict post-import verification or infer no historical changes; apply Customer Result Presentation Apply Business Name Presentation. |
| CMKSP.DELIVERY_CREATE_NEEDED | terminal | 48 | terminal | none | CMKSP.APPLY_DELIVERY_DEFAULTS | continue | Return create_needed with supported DM4/DM5 preparation scope and retained private business inputs/evidence to the existing Run Book Prepare Delivery Method CSV ZIP step. End this rule evaluation only: the invoking Run Book continues the selected task into source_export or preparation without asking whether to proceed. Obtain a missing exact-task template through the shared exporter and its approval, then prepare the single-row ZIP and run Data Loader preflight. No creation or import approval is claimed; existing operation-specific approval gates remain mandatory. Unsupported settings follow RETURN_ISSUES instead Apply Business Name Presentation. |
| CMKSP.DELIVERY_REVIEW_REQUIRED | terminal | 49 | terminal | none | CMKSP.DELIVERY_RECONCILE | continue | Return review_required with supplied/current business differences and supported next action; no overwrite, duplicate create or fabricated update Apply Business Name Presentation. |
| CMKSP.DELIVERY_INPUT_REQUIRED | terminal | 50 | terminal | none | CMKSP.DELIVERY_TYPE | continue | Return MISSING with readable fresh Type choices and preserved other inputs; ask only for that business choice Apply Business Name Presentation. |


## Sources

[S1]: https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/Task_CSV_Import.html

## Create/Update Preparation Failures

| Situation | What Should Happen |
|---|---|
| Required business inputs are missing | Follow the selected BO's intake in ora_input_validation.md. For connections, follow Document-first live selection and derived direction, retaining resolved fields; ask for missing Name before export. For providers, ask only for missing Provider, Provider ID, Provider Type or ID Type. Do not prompt for every optional field. Report preparation findings separately from customer input questions |
| A public provider REST schema is used as a creation shortcut | Retain the FSM route. The reviewed 26C POST documentation labels the action unsupported; a request-schema example or general privilege table does not establish a supported provider-create route. Do not attempt that POST or use its defaults as CSV rules |
| A populated export is supplied but provider creation rules remain unresolved | Acknowledge that baseline evidence is now available; return input validation for the exact missing mapping, create requirement or Run Book preparation step. Do not ask for another template or claim that an existing-row export proves creation readiness |
| Provider ID repeats in the reviewed baseline | Do not treat Provider ID alone as unique. The supplied entity duplicate-validation rule uses ProviderName plus UserDefined; keep CSV importer matching separate from this known rule |
| Provider-create target duplicate check finds an existing name | Display only: There's already a provider with that name. Preserve supplied inputs and create intent; do not select the existing provider, switch to update or prepare an import for that conflicting name |
| Provider-create duplicate lookup is incomplete, stale, ambiguous or fails | Stop before package preparation or import approval and report the specific sanitized lookup failure. Do not infer target uniqueness from a header-only template or request a populated export as a fallback |
| Provider create supplies UserDefined other than Y | Preserve the supplied value and report that the declared duplicate lookup covers user-defined provider creation only; do not change the value or broaden the captured request |
| Fusion returns CMK:::CMK_B2B_PROVIDER_DUPE | Display only: There's already a provider with that name. Omit the trailing parenthesized error code from the matching o:errorDetails title. Do not add the top-level Bad Request title, HTTP status, detail text, error path, technical key explanation, diagnostics, next steps or progress commentary to the displayed error. Retain sanitized diagnostic evidence internally. Preserve other supplied inputs and create intent; do not silently switch to update or retry the write. For an import, retain the process result and resolve the conflict before a new approved submission |
| Provider references do not all resolve inside the baseline | Report catalog mismatch or input validation according to the selected reference rule; do not invent missing records or assume external references are invalid without evidence |
| CSV representation, release evidence, or the declared Run Book preparation step is absent | Return the exact input-validation/workflow finding before package editing. For connection creation, allow completed lookup intake and the declared approved populated export to provide mapping evidence; do not block those stages solely because final ZIP evidence does not yet exist |
| Prepared archive lacks baseline provenance or final schema evidence | Stop before Task Hook preview; preserve the original export and regenerate the derived package and preparation record |
| Source export is incomplete, unrelated, or header-only without a declared create profile | Stop preparation for incomplete or unrelated exports. A completed exact-task header-only export is allowed only as the selected declared create-profile seed, including XSL-message and native external-definition creation; validate the derived row and immutable ZIP, never import the unchanged template |
| Duplicate create key, ambiguous update target, or unrelated data changes | Stop before approval; show redacted affected-key evidence and resolve the requested scope, except that CMK:::CMK_B2B_PROVIDER_DUPE displays only its message text without the error code under the specific rule above; never silently turn create into update |
| Final archive or preparation-evidence persistence fails | Return artifact persistence; do not approve or upload a partial artifact |
| Submission returns an uncertain outcome | Preserve safe identifiers and follow the existing status route; do not replay the import |

These preparation failures are not recoverable by guessing CSV values, using a
browser, or bypassing Data Loader. Contract-only documentation and registry
readiness are not proof of an executable or tested record-creation capability.

## Business Object Preparation Boundaries

| Situation | What Should Happen |
|---|---|
| Create connection has no inbound/outbound direction | Run resolve_cmk_connection_document first and ask for Document using its live choices. Derive direction from the selected row; do not ask for direction separately or default outbound. Unsupported or conflicting document direction blocks with a plain explanation |
| Delivery-method inputs are supplied for an inbound connection | Display only: Delivery methods apply only to outbound connections. Stop that create before package preparation and preserve inputs for correction; do not fetch delivery methods or silently switch direction |
| One changed BO has an unresolved required input or source rule in a mixed request | Stop the entire package preparation; do not emit a partial import ZIP |
| Supplied source is the header-only task template | Apply the confirmed provider-create seed exception in ora_input_validation.md: a completed exact-task header-only export may seed that flow, but its derived ZIP must contain the validated new provider row. Never import the unchanged template. Connection preparation still requires a completed populated export; other BOs retain their own source requirements |
| UI label has no source-backed CSV mapping or derived-value rule | Retain the user's input and report the missing mapping; do not invent codes or IDs |
| XSL/payload file representation is unresolved | Block the affected message definition before package preparation; do not insert an attachment path into a clob column by assumption |
| An update has no declared processing route | Stop and select a supported Run Book update step; never append a duplicate or replace an existing row |

## Provider Dropdown Failures

| Situation | What Should Happen |
|---|---|
| First resources GET fails for an observed UI lookup | Return transport/environment, auth/authz or catalog mismatch as supported by Core evidence; stop, without probing another path or replaying captured browser credentials |
| Lookup pagination, application context, date or enabled state is invalid | Return catalog mismatch and block selection; do not present incomplete or stale choices |
| Selection is unknown, disabled, expired, rejected by an evidence-backed runtime applicability predicate, or ambiguous | Show the freshly resolved eligible Meaning choices and ask only for that field |
| Caller supplies an offline response file | Use it for development mapping and tests only; require fresh same-target runtime evidence before provider-create import approval |

## Connection Intake Failures

| Situation | What Should Happen |
|---|---|
| A current connection selection is missing or ambiguous | Follow its selection_required terminal and Connection Choice Presentation in ora_reference_lookups.md; preserve other supplied values. Do not substitute provider-create Type or ID Type questions |
| A connection name search has no matches or only partial-name matches | Keep selection_required and follow the presentation rule's correction or selection prompt; do not treat a partial match as a validated identity or a no-match search as a Fusion read failure |
| A Document has Direction Any or conflicts with explicit requested direction | Explain that the selected document does not establish the requested connection direction; preserve the choice for correction and do not silently choose inbound or outbound |
| Message Definition scope is missing, changed or the scoped read fails | Block the message lookup or invalidate its prior choices and selection; retrieve the complete current Document/Provider-or-unassigned/mode scope through Core. Never fall back to an XSLT-only list or reuse its option references |
| Transformation mode is missing | Offer XSLT style sheet and Mapping file before the message-definition GET; accept readable labels through Connection Transformation Mode Selection. The supplied XSLT-filtered request is not a defaulting rule |
| The selected transformation mode has no source-backed lookup contract | Retain the selection and report the exact lookup-contract limitation. Use the explicit mapping-file adapter code and its Document/provider/mode query. A schema failure is a target compatibility issue; a complete empty result is no eligible definition. Do not execute the XSLT query, ask for the same mode again or create a message definition implicitly |
| The corrected connection status lookup is available | Use ORA_CMK_EXT_PTNR_MSG_STATUS and preserve its exact code for OverrideStatus; do not ask for the earlier Enabled/Disabled/Hold conversion again |
| A connection read fails or pagination is incomplete | Report the specific sanitized auth/authz, transport/environment or Fusion API failure and stop that lookup. Do not reuse captured credentials, old response lists or guessed endpoints |
| A lookup-selected reference has unverified document/provider compatibility or CSV identity | Retain completed business intake, use the declared populated export for available evidence and block only unsafe ZIP preparation. Do not tell the customer to edit resource files or supply the same capture again |

## Documentation Review Source

The public provider POST page explicitly labels the operation unsupported:
https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bserviceproviders-post.html

The 26D task import procedure establishes task identity, process-status polling
and ProcessLog retrieval; it does not define this provider CSV's create fields:
https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/Task_CSV_Import.html

## Supplied Duplicate Rejection Evidence

The duplicate-rejection response has title Bad Request,
status "400", and an o:errorDetails entry containing the message
"There's already a provider with that name. (CMK-4215359)". Its detail adds
"Enter a different name."; o:errorCode is CMK:::CMK_B2B_PROVIDER_DUPE and
o:errorPath is /ProviderName. This confirms duplicate rejection and the
field-specific correction for the observed request, consistent with the
entity uniqueness rule recorded in ora_input_validation.md.

The response alone supplies no request method, endpoint, submitted values,
release or FSM import process result. Do not generalize the observed rejection
to every CSV import, infer automatic update behaviour, or treat /ProviderName
as proof that UserDefined is excluded from the entity uniqueness rule.

The display policy is to show only the error message without its
error code: "There's already a provider with that name." Remove the trailing
parenthesized code from the matching o:errorDetails title for display. Preserve
the original title, response metadata and additional detail sentence as
diagnostic evidence only.


## Delivery Method Failure and Resume Rules

| Situation | What Should Happen |
|---|---|
| Method is absent and the selected DM4/DM5 preparation checks pass | Continue through DELIVERY_CREATE_NEEDED to Run Book preparation. Say that the requested delivery method needs to be created and its details are ready for preparation. Do not report an unqualified creation workflow, ask whether to continue, or mark the business objective complete at this handoff. Shared export and Data Loader retain their existing approval gates; no approval is inferred from preparation readiness |
| Method is absent and a supplied setting is outside the selected preparation profile | Report the exact setting or transport contract that blocks this request and retain valid business inputs. Distinguish this from missing input and supported preparation. Do not apply this blocker to all absent methods or to another supported request |
| Unlisted REST resource advertises create | Preserve capability evidence for execution-contract qualification only. Do not treat POST annotations or describe metadata as support, authorization, a route change or a completed creation contract |
| Previous creation/import result is uncertain | Preserve operation IDs privately and check status through the original declared route. Then use post_import_verify_delivery_method; no automatic replay or invented idempotency key |
| Customer resumes connection after method verification | Invoking Run Book refreshes the existing provider-scoped connection delivery lookup for the same attachment/provider/target. Do not reuse a stale missing-list result or substitute a differently named method |


## Delivery Method Preparation Failures

| Situation | What Should Happen |
|---|---|
| A matching name exists outside the selected provider | Explain that the delivery-method name is already used and retain the selected provider and recipient. Ask for a different name only for strict creation of a new independent method; do not reuse another provider's method or call a write to test the collision |
| The global name read is incomplete or unauthorized | Return the actual failure and execution_blocked. Explain that name availability could not be verified; do not describe it as a missing customer field or widen credentials/visibility |
| A supplied option is absent from the selected delivery import profile | Name the retained setting and the preparation limitation. Do not silently omit it, change transport, ask the customer to edit CSV/resource files or claim the delivery method is ready |
| Supported Email or standard File Export inputs pass but no template exists | Continue the source_export handoff to the invoking Run Book shared-export workflow and its approval gate. After a completed compatible template export, resume preparation with retained inputs. Do not ask the customer for a developer-generated ZIP, treat the missing template as missing business input, or end the task merely because preparation has another stage |
| A prepared delivery-method package changes | Return through normal Data Loader preflight and Task Hook approval for the new immutable artifact. Do not reuse name/type checks or approval from different bytes or a different target |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.DELIVERY_NAME_CONFLICT | terminal | 51 | terminal | none | CMKSP.DELIVERY_NAME_CHECK | continue | Return the exact delivery-name collision or case-review result in business terms; preserve other supplied choices, disclose no protected collection rows and make no changes Apply Business Name Presentation. |


## Delivery Transport Results

| Situation | What Should Happen |
|---|---|
| Email has several comma-separated recipients | Validate each mailbox and the total stored length. Preserve the supplied list; do not reject it as a single malformed address or silently keep only the first recipient |
| Email or File Export includes a supported file extension | Preserve and verify the exact extension. Explain only when relevant that changing the extension keeps ZIP content; it does not implement an uncompressed-PDF request |
| File Export has no supplied account | Do not ask the customer for an undocumented constant. Prepare only qualified fields and report the actual repository account after requested verification; do not claim that it matches a fixed account inferred from internal implementation |
| Business Event user-defined creation is requested | Explain that this FSM create profile failed qualification because Fusion treats this type as predefined. Block before preparation or approval; retain the business requirement. An enabled type lookup is not create eligibility. Do not ask for another name, provider flag or template as a fix, or propose a REST/UI write |
| A prior DM6 import reports the predefined-type restriction | Retain the actual failed native process result separately from the Data Loader badge and counts. Completed with errors in the native process log cannot be reported as successful creation while a dataset still says in progress. Do not automatically retry or claim rollback; saved effects remain unverified until supported current comparison |
| An existing predefined Business Event method is proposed | Select the bounded predefined_business_event_fsm connection branch before lookup only when its outbound-invoice/XSLT/Inactive/existing-provider scope fits. Qualify the native reference witness without demanding a separate provider-owned method row. Outside that scope, or when current witness/identity/message eligibility is missing, record the exact qualification gap. Do not invent a method name, change provider scope or treat the failed method-creation test as proof of an alternate route. OIC flow setup and event delivery remain separately scoped |
| B2B Adapter is supplied to the selected FSM-only profile | Keep that profile boundary and return the precise native preparation or external-prerequisite gap, retaining nonsecret business choices. This task provides no executor for the external setup. Do not call the product option unsupported, treat the gap as a missing customer field, collect secrets, disable the feature or select another executor |
| A supported type lacks a required business field after type resolution | Ask only for that field and retain name/provider/type/other valid choices. The returned MISSING state is distinct from an unsupported template field or creation route |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.DELIVERY_FIELDS_REQUIRED | terminal | 52 | terminal | none | CMKSP.DELIVERY_PREPARATION_CHECK | continue | Return MISSING with only the unresolved transport-specific business field, such as email recipients after Email was selected. Retain all current selections; do not request a developer ZIP, task code, internal ID or unsupported setting Apply Business Name Presentation. |


## Delivery Import and Verification Results

| Situation | What Should Happen |
|---|---|
| Import initiation is accepted | Return the required Core Data Loader in-progress report unchanged. Do not run status or verification reads automatically; accepted initiation is terminal for that request |
| Requested status is running or no data set exists yet | Preserve the actual current state and the Core status report. Do not describe setup as created, verified or failed solely because the data set is not yet visible |
| Requested results include row errors, warnings or partial success | Preserve all actionable diagnostics and distinguish processing from saved-state coverage. A successful read of this method does not clear unrelated failures or make the whole import successful. Never replay the archive or replace a processing failure with a verified-state success |
| Completed import and every intended method setting matches | Return verified through DELIVERY_VERIFIED with processing outcome and saved-state comparison separately. Describe creation only when the bound operation evidence supports it; otherwise state that the saved settings match. Do not return reused_and_verified or a canned no-changes message |
| Completed import but method is absent, ambiguous or different | Preserve the completed processing result and report the exact saved-state verification failure. Keep a dependent connection pending. Do not prepare a duplicate, auto-correct the record or request approval to repeat the same uncertain change |
| Verification read fails after completed import | Classify the actual auth/authz, transport/environment, Fusion API or schema/input failure and retain the import outcome separately. Resume only the declared read after its prerequisites pass; do not resubmit the import or claim no configuration changed |
| Approved intent is unavailable on resume | Report missing verification evidence and recover the private approved intent through the original workflow when available. Do not reconstruct intended values from the current target, another request or an aggregate process count |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.DELIVERY_VERIFIED | terminal | 53 | terminal | none | CMKSP.DELIVERY_STATE | continue | Only strict post_import_verify_delivery_method: return verified saved settings with bound processing outcome, intended-field comparison coverage and actual prior side-effect evidence. Apply Delivery Import and Verification Results and Customer Result Presentation. This read performs no new mutation and does not imply reuse, a fully successful multi-object import or proven business-document delivery Apply Business Name Presentation. |


## Public Guidance Recovery

| Situation | What Should Happen |
|---|---|
| New outbound connection lacks primary delivery | Ask only for the primary method using current eligible names. An optional alternate does not satisfy it; retain other selections |
| Activation conflicts with existing setup | Explain the conflict and retain the requested setup for review. Do not deactivate the other message or request permission to import a known conflict |
| New definition lacks transformation content | For the documented XSL workflow, request the XSL and validation XML sample when missing. Existing-definition reuse does not require uploading those files again |
| Public guidance lacks a technical CSV mapping | Finish independent checks and retain supplied inputs. Report the exact execution-contract gap; do not request internal documents, invent IDs/encoding, or switch to a published POST without a selected execution workflow |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.MESSAGE_PREPARATION_READY | terminal | 55 | terminal | none | CMKSP.MESSAGE_REFERENCES | continue | Return validated private definition inputs and reference fingerprints to the existing Run Book CSV/ZIP processing step for the selected XSL message or native external definition; continue preparation without another proceed question. Keep the selected object and exact one-row scope. This is not creation or import approval Apply Business Name Presentation. |
| CMKSP.MESSAGE_REFERENCE_EXPORT | terminal | 56 | terminal | none | CMKSP.MESSAGE_REFERENCES | continue | Return source_export_required to the invoking Run Book: obtain the missing exact-task populated reference or header-only create template through the shared exporter and its normal approval, keep the create seed separate from populated reference rows, then resume MESSAGE_REFERENCES with retained inputs. Do not ask for an internal document or developer-generated ZIP Apply Business Name Presentation. |
| CMKSP.MESSAGE_FIELDS_REQUIRED | terminal | 57 | terminal | none | CMKSP.MESSAGE_REFERENCES | continue | Return only the unresolved readable Document/original/external-definition selection or native external-format business field, retaining valid inputs. Do not request DocOperationId or reinterpret a failed read as invalid customer data Apply Business Name Presentation. |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.MESSAGE_VERIFIED | terminal | 58 | terminal | none | CMKSP.MESSAGE_STATE | continue | Return verified saved message settings and intended scalar/file coverage, preserving import processing status separately. Do not call this reuse, PO delivery success or approval to configure another object Apply Business Name Presentation. |


## Declared REST Processing Gate

| Situation | What Should Happen |
|---|---|
| Preflight passes | The invoking Run Book prepares and reviews the exact private payload through its declared Core workflow. Readiness is not mutation approval |
| A write is accepted | Preserve the actual action result and use the declared safe read for requested-state coverage. Do not start an import afterward, infer reuse or report delivery of a business document |
| Dispatch is rejected or uncertain | Preserve the exact operation/stage and sanitized result; no automatic write retry, route substitution, rollback or fresh create. Reconcile only through the selected read before another approved action |
| Verification is incomplete | Retain accepted mutation separately from the failed comparison. State exactly what was verified; do not suppress a write-only or credential coverage gap |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.REST_GATE | step | 62 | execution_gate | ready->CMKSP.REST_APPROVAL_READY;blocked->RETURN_ISSUES | CMKSP.REST_PREFLIGHT | stop | Retained historical node only. FSM-Only Route Enforcement rejects new REST or assisted setup before this node; return the task failure outcome if reached for a new write. No Core helper, approval handoff, dispatch or operator Save is authorized. |
| CMKSP.REST_APPROVAL_READY | terminal | 63 | terminal | none | CMKSP.REST_GATE | continue | Retained historical node only. FSM-Only Route Enforcement rejects new REST or assisted setup before this node; return the task failure outcome if reached for a new write. No Core helper, approval handoff, dispatch or operator Save is authorized. Apply Business Name Presentation. |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.REST_VERIFIED | terminal | 65 | terminal | none | CMKSP.REST_VERIFY | continue | Return actual action outcome and verified requested-state coverage separately. Preserve any credential/connectivity or partial-result boundary; do not claim another component is ready, infer no changes or report a PO delivered Apply Business Name Presentation. |


## Assisted Delivery Outcomes

| Situation | What Should Happen |
|---|---|
| The requested PDF option or credential setup selected the assisted route at intake | Continue through its context/design/review nodes and the documented operator step. Do not report an API/CSV field gap for this route or demand an existing credential binding |
| Current screen, provider or method context has not been confirmed | Return the precise nonsecret operator step and retain the business request; do not ask for credentials, internal documents, REST routes or a developer-generated archive |
| Save is failed or uncertain | Preserve the actual action outcome. Stop writes, reopen the same row for safe confirmation and use the verification branch; do not automatically click Save, submit REST or import a ZIP |
| Credential replacement has no direct-entry/save confirmation | Return the credential confirmation step without asking for the value. A masked password or pre-existing record is insufficient; do not label credentials or authentication verified |
| PDF setting was not observed after reopen | Return the explicit reopened-screen checkbox confirmation. A REST response without the field or a renamed ZIP extension cannot pass verification |
| Configuration matches after an uncertain save | Report state confirmed with action uncertain; retain that outcome and do not infer creation or replay the save |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.ASSISTED_CONTEXT_REQUIRED | terminal | 67 | terminal | none | CMKSP.ASSISTED_CONTEXT | continue | Return the exact current-screen identity/before-state confirmation step to the implementer through Core Run Book, retaining supplied nonsecret values. No mutation or secret collection Apply Business Name Presentation. |
| CMKSP.ASSISTED_GATE | step | 69 | execution_gate | ready->CMKSP.ASSISTED_APPROVAL_READY;blocked->RETURN_ISSUES | CMKSP.ASSISTED_DESIGN | stop | Retained historical node only. FSM-Only Route Enforcement rejects new REST or assisted setup before this node; return the task failure outcome if reached for a new write. No Core helper, approval handoff, dispatch or operator Save is authorized. |
| CMKSP.ASSISTED_APPROVAL_READY | terminal | 70 | terminal | none | CMKSP.ASSISTED_GATE | continue | Retained historical node only. FSM-Only Route Enforcement rejects new REST or assisted setup before this node; return the task failure outcome if reached for a new write. No Core helper, approval handoff, dispatch or operator Save is authorized. Apply Business Name Presentation. |
| CMKSP.ASSISTED_VERIFIED | terminal | 79 | terminal | none | CMKSP.ASSISTED_TRANSPORT_RESULT | continue | Return the actual saved outcome and every requested field's reopened-screen comparison, with operator-confirmed credential entry separately. Authentication/connectivity and supplier receipt are not inferred Apply Business Name Presentation. |
| CMKSP.ASSISTED_REUSED | terminal | 73 | terminal | none | CMKSP.ASSISTED_RESULT | continue | Return unchanged with all requested nonsecret fields confirmed and no credential replacement. Do not claim a new method or new password was saved Apply Business Name Presentation. |
| CMKSP.ASSISTED_CONFIRMATION_REQUIRED | terminal | 74 | terminal | none | CMKSP.ASSISTED_RESULT | continue | Return the exact missing reopened-screen field/environment/scope confirmation and retain actual action outcome; no new save or approval step Apply Business Name Presentation. |
| CMKSP.ASSISTED_STATE_ONLY | terminal | 75 | terminal | none | CMKSP.ASSISTED_RESULT | continue | Return requested configuration confirmed while action remains uncertain. Do not report creation, credential replacement, connectivity or receipt as proven and never replay Apply Business Name Presentation. |
| CMKSP.ASSISTED_CREDENTIAL_CONFIRMATION | terminal | 76 | terminal | none | CMKSP.ASSISTED_RESULT | continue | Ask only whether the authorized credential owner entered the values directly in Fusion and the save succeeded, without disclosing values. Retain action uncertainty; never infer this from masking or save again automatically Apply Business Name Presentation. |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.EXTERNAL_TRANSPORT_REQUIRED | terminal | 78 | terminal | none | CMKSP.ASSISTED_TRANSPORT_RESULT | continue | Return saved CMK method coverage plus external_prerequisite_required to the shared roadmap. Retain the requested scope and report the missing external transport evidence. This task provides no executor for the external prerequisite; do not select an undeclared task or operation. Do not mark transport/delivery complete or replay the CMK save Apply Business Name Presentation. |

## Customer Acceptance Outcomes

| Situation | What Should Happen |
|---|---|
| Login, missing privilege or unreachable app | Record auth/authz or transport/environment blocked with actual evidence. Authentication is not a failed CMK business rule. Do not count queued cases as executed |
| Process response is uncertain | Keep the attempt uncertain; read the same message/history context. Never retry Process or resubmit as a test recovery |
| Negative input is rejected | Pass only that case and only at its observed validation level. Record the actual message; do not claim an unobserved downstream rejection |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.ACCEPTANCE_UI_READY | terminal | 81 | terminal | none | CMKSP.ACCEPTANCE_INPUT | continue | Return the declared read-only browser preflight handoff. This is not approval, a Process action or a live test pass Apply Business Name Presentation. |
| CMKSP.ACCEPTANCE_GATE | step | 83 | execution_gate | ready->CMKSP.ACCEPTANCE_PROCESS_READY;blocked->CMKSP.ACCEPTANCE_BLOCKED | CMKSP.ACCEPTANCE_DESIGN | stop | Require exact current environment, existing test recipient, document, payload hash, destination/effect and approval under active project rules. The separate SKILL workflow owns a single UI Process; the graph does not dispatch |
| CMKSP.ACCEPTANCE_PROCESS_READY | terminal | 84 | terminal | none | CMKSP.ACCEPTANCE_GATE | continue | Return exact browser processing handoff and immutable scope. No implicit retry or completion claim Apply Business Name Presentation. |
| CMKSP.ACCEPTANCE_PASSED | terminal | 86 | terminal | none | CMKSP.ACCEPTANCE_RESULT | continue | Record the positive case passed only at its observed execution level, with receipt separately Apply Business Name Presentation. |
| CMKSP.ACCEPTANCE_REJECTED | terminal | 87 | terminal | none | CMKSP.ACCEPTANCE_RESULT | continue | Record the negative case passed only when the expected rejection actually occurred; preserve its validation or processing level Apply Business Name Presentation. |
| CMKSP.ACCEPTANCE_BLOCKED | terminal | 88 | terminal | none | none | stop | Record the actual input, auth/authz, transport/environment, catalog mismatch or approval blocker and one concrete resume action. No synthetic passing result Apply Business Name Presentation. |
| CMKSP.ACCEPTANCE_UNCERTAIN | terminal | 89 | terminal | none | CMKSP.ACCEPTANCE_RESULT | stop | Preserve uncertain processing and reconcile through current visible history; never replay the action Apply Business Name Presentation. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.PROVIDER_REVIEWED | terminal | 91 | terminal | none | CMKSP.PROVIDER_REVIEW | continue | Return observed matching identity/type and limited coverage; provider reuse, delivery and receipt remain unverified Apply Business Name Presentation. |
| CMKSP.PROVIDER_NOT_FOUND | terminal | 92 | terminal | none | CMKSP.PROVIDER_REVIEW | continue | Return business provider name not found after complete live read; preserve request and ask for corrected name or separately scoped create, never create a supplier Apply Business Name Presentation. |
| CMKSP.PROVIDER_SELECTION_REQUIRED | terminal | 93 | terminal | none | CMKSP.PROVIDER_REVIEW | continue | Return readable current choices or ambiguity for the business user; no arbitrary first-row selection or technical IDs Apply Business Name Presentation. |

## All Object Error Situations

| Situation | What Should Happen |
|---|---|
| Customer choice/access/existing master data is missing | State the concrete business choice or administrator action needed; retain other supplied input and never request credentials in chat |
| Object mapping or executor is unqualified | Record a skill defect with object, operation, missing contract and public research performed. Do not reclassify it as a customer prerequisite or claim full customer readiness |
| Schema validation passed but live execution was not performed | Record validation-only coverage and live status not_run or blocked, with the exact missing step; no passing CRUD or delivery claim |

## Provider Coverage Errors

| Situation | What Should Happen |
|---|---|
| Public collection omits Direct provider scope | Return the complete-namespace evidence requirement to the invoking source-export/preparation stage; never report globally unique or create a provider solely from the public no-match |
| Completed export conflicts with public provider identity | Preserve both observations privately; classify catalog mismatch and stop before preparation or approval. Do not change provider type or reinterpret the proposed name |
| Source-export prerequisite fails | Preserve the actual export failure and job status; the dependent create remains blocked. Do not return to UI discovery, invent a key or submit an empty template |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.PROVIDER_VERIFIED | terminal | 95 | terminal | none | CMKSP.PROVIDER_STATE | continue | Return provider requested-state comparison coverage, actual processing result and separately qualified created-versus-existing disposition. No claim of a connection, supplier setup or document delivery Apply Business Name Presentation. |

## File Export Read Coverage

| Situation | What Should Happen |
|---|---|
| File Export create accepted, item GET 404 and child list omits the row | Retain the accepted dispatch and both read observations. Use only the declared complete exact-task export verification step for its mapped business fields; never replay the create or claim the public list is the complete File Export namespace |
| Fresh export verifies requested method fields but does not contain repository account or REST ID | Report the exact export comparison coverage and mark those technical/account saved values unverified. An account observed in the accepted response is response evidence only; a requested custom account remains blocked pending a qualified saved read |
| Export omits the intended method or differs from approved values | Keep saved-state verification blocked with field-level differences and the original dispatch reference. Do not import another package, create again, or use a successful job count as row-level proof |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.CONNECTION_EXPORT_VERIFIED | terminal | 97 | terminal | none | CMKSP.CONNECTION_EXPORT_STATE | continue | Return successful import processing and exact exported business-state coverage separately, including matched fields, strict-create before/after identity counts and preserved rows. Do not report unobserved REST IDs, credentials, external delivery or PO receipt. Apply Business Name Presentation. |

## Published REST XML File Rejection

Public file contract: [Create message definitions](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bmessagedefinitions-post.html).

| Situation | What Should Happen |
|---|---|
| Fusion returns CMK_MSG_DEFN_VALID_XSL_FILE or CMK_MSG_DEFN_VALID_TEMPLATE | Preserve the rejected result and private immutable request. Decode the approved byte fields according to the public contract and check exact UTF-8/declared encoding, well-formed XML and the required XSL root without executing transformations or fetching external resources. Report actual local validation and Fusion rejection separately; do not call valid customer XML malformed solely because the generic server message says so |
| Locally valid base64 XML is still rejected | Classify a Fusion API/deployed-contract compatibility blocker for the selected operation, with exact field/error identifiers, target release, framework version and sanitized proof. Reconcile current name/state before any separately approved correction. Do not guess another encoding, double-encode, change REST framework version, strip customer content, remove a requested file or switch to UI/import after the failed public operation |
| A compatibility hypothesis changes owned synthetic inputs | Retain the original and corrected immutable requests separately, compare their XML trees and exact bytes, bind any distinct test to its own current preview/approval and send once. A repeated same rejection does not establish a fix. Never turn a hypothesis into an automatic customer-file rewrite |
| Customer message creation remains blocked | Name the unresolved target file-acceptance contract and continue independent tests. Do not substitute an empty transformation, claim message creation from an export/read, ask for internal documents or present this as a customer business-data correction. A working supported current contract or environment correction is required before this positive case passes |
| New connection import returns CMK-4215069 for an existing association | Preserve final job status, counts and ProcessLog, reconcile actual saved state through the declared task export, and retain partial results. Add/recheck the exact-association preapproval guard; a distinct name or Inactive status does not remove this known conflict. Do not replay the failed archive or silently alter the existing connection |


## Qualified LOB Rejection After Local Validation

The existing error-handler and REST result nodes classify a current HTTP 400
on XsltFile or PayloadTemplate with CMK-4215327 / CMK-4215326 as a Fusion API rejection,
separately from local XML/JSON well-formedness and request acceptance.
Preserve the exact immutable hash, environment, current schema and tuple,
file origin/hash/encoding, explicit request headers, error code/path and
fresh same-scope absence/preservation result. Local validity or an Oracle
exported sample does not override the actual rejection or prove a server
root cause. A rejected export-sourced file test must remain visible alongside
an earlier synthetic-file test. Do not strip requested content, omit files,
change byte encoding/protocol, use UI/import as a fallback, or count an export,
reuse or preservation check as new configuration creation.

After a confirmed rejection, the owning declared verification branch may
read the complete exact-name/scope resource to establish absence and compare
prior readable state. An uncertain result instead remains uncertain until
reconciled. No write replay is permitted. One explicitly selected immutable
media-type compatibility test is governed by its separate input profile;
failure of that test ends that hypothesis. The integration owner must obtain
supported current write-contract or environment-repair evidence before a
new preparation and separately approved attempt. Report the operation as
blocked for this target while preserving working independent task routes.
Customer guidance names the failing configuration operation and correction
owner; it never asks the customer to invent IDs, use private documentation,
change application code or repeat the failed request.


## Combined Import Qualification Failures

| Situation | What Should Happen |
|---|---|
| Combined native job partial, failed or uncertain | Preserve the immutable ZIP and actual per-object results; retrieve the Fusion ProcessLog through the existing report/status route. Reconcile every intended and prior row using fresh full export before considering another package. Do not replay the complete ZIP, auto-split it, assume rollback, allocate IDs or edit metadata sequence. Report the exact dependency/import diagnostic and successful objects separately. Unsupported native parent resolution remains a product-contract blocker until evidence supports a correction |
| Combined job accepted | Report initiation separately from processing and business-state qualification. Follow only the existing Core status workflow when the user requests that next step; the end-to-end qualification request includes that requested follow-up. Never call acceptance a passed test |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.COMBINED_LOAD_READY | terminal | 114 | terminal | none | CMKSP.COMBINED_PACKAGE | continue | Return the validated four-row immutable ZIP, request/intent/reference/source hashes and completed rule evidence to the invoking Run Book and Core Data Loader. This terminal establishes preapproval readiness only; the current run remains unverified until actual successful processing and complete before/after comparison. No import, polling or retry is performed by this node Apply Business Name Presentation. |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.COMBINED_VERIFIED | terminal | 116 | terminal | none | CMKSP.COMBINED_STATE | continue | Return verified configuration for exactly the original four-component request with bound import/snapshot hashes, created component dispositions and preservation evidence. Report one combined import and actual per-object outcomes separately. This proves saved setup, not partner delivery, invoice processing, arbitrary batching or rollback Apply Business Name Presentation. |


## Provider Identifier Update Outcomes

| Situation | What Should Happen |
|---|---|
| Preparation required | Return prepare_needed to the invoking active Run Book with the exact selected existing row and one-field correction contract. No creation, defaults or write occurs in the resource graph |
| Immutable correction ready | Return loader_ready to Core Data Loader with exact existing-row intent and final archive binding. Its own preflight, Task Hook and single approval remain mandatory |
| Already matching | Return unchanged with current verified business-identifier evidence. No historical update or new import is claimed |
| Saved correction verified | Return updated_and_verified only after successful bound native job, all thirteen saved fields and all-object preservation pass |
| Changed before state, conflicting documents or failed processing | Preserve original intent and actual result; report exact conflict or failure and safe resume point. Never switch update to create, replay the package or silently change another document |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.IDENTIFIER_UPDATE_PREPARE | terminal | 106 | terminal | none | CMKSP.IDENTIFIER_UPDATE_PACKAGE | continue | Return prepare_needed and bounded existing-row correction contract; invoking Run Book owns assisted local preparation Apply Business Name Presentation. |
| CMKSP.IDENTIFIER_UPDATE_LOAD_READY | terminal | 107 | terminal | none | CMKSP.IDENTIFIER_UPDATE_PACKAGE | continue | Return loader_ready with immutable artifact and current reference evidence; Core Data Loader owns approval and submission Apply Business Name Presentation. |
| CMKSP.IDENTIFIER_UPDATE_VERIFIED | terminal | 109 | terminal | none | CMKSP.IDENTIFIER_UPDATE_STATE | continue | Return updated_and_verified for the original correction only; no new operation Apply Business Name Presentation. |
| CMKSP.IDENTIFIER_UPDATE_UNCHANGED | terminal | 110 | terminal | none | CMKSP.IDENTIFIER_UPDATE_REFERENCES | continue | Return unchanged with current field equality; no import required or submitted Apply Business Name Presentation. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.COMPOSITION_PREPARE | terminal | 403 | terminal | none | CMKSP.COMPOSITION_PACKAGE | stop | Return qualified retained nine-row business intent to active Run Book assisted Prepare Provider Task Composition CSV ZIP. This is preparation-needed, not creation or approval. Continue owning workflow without another proceed question; preserve all blocked components |
| CMKSP.COMPOSITION_LOAD_READY | terminal | 404 | terminal | none | CMKSP.COMPOSITION_PACKAGE | stop | Return the one nine-row immutable native ZIP, exact task/target, all component rule outcomes and bound source/intent/reference hashes to Core Data Loader and Task Hook. Preserve their authoritative approvals and initiation terminal. A controlled qualification candidate is not a passed live import |
| CMKSP.COMPOSITION_VERIFIED | terminal | 406 | terminal | none | CMKSP.COMPOSITION_STATE | stop | Return actual single-job result, all nine component dispositions, per-object ProcessLog evidence, exact requested/saved cell comparisons and six-object full preservation evidence. Verify saved setup only; no transformation execution, activation, delivery, arbitrary batching or rollback claim |
| CMKSP.COMPOSITION_ISSUES | terminal | 407 | terminal | none | CMKSP.REQUEST_SHAPE | stop | Return the exact failing composition input/reference/package/job/cell check, actual per-component saved side effects and errors, complete source/request fingerprints and safe resume context. Do not omit scope, infer approval or retry a mutation |
