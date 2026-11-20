# Error Handling

## Source

- Oracle readiness: Streamline the Import and Export of Messaging Setup Data, 26C, https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46531.htm
- [Oracle 26D export and import process results](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/review-of-export-and-import-process-results.html) identifies business-object details, logs and the supporting product for an import error.
- [Oracle 26D supplier procure-to-pay setup](https://docs.oracle.com/en/cloud/saas/procurement/26d/oapro/how-you-set-up-suppliers-for-procure-to-pay.html) identifies the business process, trading-partner association and document enablement steps.
- [Oracle 26D supplier-site read](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-suppliers-supplierid-child-sites-suppliersiteid-get.html) exposes the Enable B2B Messaging code as B2BCommunicationMethodCode.

## Supplier Resolution Recovery

| Situation | What Should Happen |
|---|---|
| Supplier Browse exceeds its bounded read window | Report process timeout with environment, resolver, request fingerprint, last status, elapsed wait and next offset. Preserve the private checkpoint. If an exact supplier number or name is already supplied, the declared resolve_cmksc_supplier exact-selection path can start a separate checkpoint; do not restart a full scan or ask again for supplied values. |
| Exact supplier filtering fails or returns inconsistent references | Preserve the supplied number and name and classify the actual auth/authz, transport/environment, Fusion API or input-validation failure. Do not fall back to an unfiltered scan, another endpoint or browser. Resume through the declared resolver after correction. |


## Error Situations

| Situation | What Should Happen |
|---|---|
| ORA_CMK_B2B_DOCUMENT_SETUP returns EnabledFlag: N on the operation host | Apply Feature State Presentation for a confirmed disabled feature. Stop before creating an export process or approving, uploading or submitting an import |
| ORA_CMK_B2B_DOCUMENT_SETUP is absent, stale, ambiguous, or unreadable on the operation host | Apply Feature State Presentation for an unverified feature. Stop before export or import; recheck only through the declared read-only resolver |
| A task-CSV upload or import has an uncertain response | Preserve every returned request/process ID; use Core Data Loader's status route to reconcile the same submission. Do not replay the write |
| Task-CSV import reaches terminal failure or warnings | Retrieve and retain Core Data Loader's ProcessLog or task-level result report, then correct the reported issue before a new approved import |
| Decision Detail task-CSV import reports a supplier-site B2B communication-method failure | Classify the import as process failed. Preserve the task and process IDs, affected business-object status details, ProcessLog and a fresh exact-task export; a processed-row count is not proof that a routing row was saved. Use only declared read checks to compare the selected supplier site's Enable B2B Messaging value and documented procure-to-pay setup with the intended scope. If the result contains no specific correctable validation error, keep the cause unresolved and refer the corresponding log to the product named in the business-object result for Oracle diagnosis. Do not change the supplier-site setting, assign a DetailId, or resubmit the import solely to suppress a generic exception. |
| Decision Detail reports Data must be valid JSON | Preserve the real failure and approved bytes. Separate strict JSON syntax failure from current header-field validation: a parsed JSON value can still fail for unknown names, missing required values or incorrect numeric/text types. Compare only against the qualified current document/header metadata and retain the exact field-level result. Do not tell the customer that valid JSON syntax proves valid routing data, change an ID, cycle encodings or replay a rejected import. Native CSV text and an inactive REST LOB representation are distinct contracts; neither supplies missing native new-row key or header-context rules. |
| Caller-requested task-CSV status checks reach ten minutes at intervals of at least thirty seconds | Stop polling; record environment, task code, request/process ID, last status, elapsed wait, and a status-only next check. Do not resubmit |
| Configuration-package export, upload, or import reports an error | Review that route's Export and Import Process Results page and stop before retrying |
| The execution contract is unresolved | Return the missing contract fields; do not use a browser, direct REST call, or substitute route |
| Feature or task-CSV ZIP, target, preview, or approval is incomplete | Return the blocker and required corrective action before import submission |
| Configuration-package project, package, or task scope is incomplete | Return the blocker and required corrective action on that route |

## Feature State Presentation

| Situation | What Should Happen |
|---|---|
| Naming the feature in a customer message | Use Simplified B2B Messaging (Gen2). For the Opt In Features selection, use the exact label Simplify Configuration and Processing for B2B Messaging. Explain a technical code only when the user asks or needs diagnostic details |
| The existing resolver confirms the feature is enabled | If a progress message is needed, say "Simplified B2B Messaging (Gen2) is enabled in {environment}." Continue the existing workflow checks; feature enablement alone does not establish task completion |
| The existing resolver confirms the feature is disabled | Say "Simplified B2B Messaging (Gen2) is disabled in {environment}. The requested {operation} for Simplified Collaboration Messaging Configuration is blocked. Have an authorized administrator enable Simplify Configuration and Processing for B2B Messaging in Opt In Features and wait for opt-in processing to finish, then retry." Fill operation with the actual requested operation. Enabling the feature requires its separate authorized workflow; never enable it automatically |
| The existing resolver cannot establish current feature state | Say "We could not verify whether Simplified B2B Messaging (Gen2) is enabled in {environment}. The requested {operation} for Simplified Collaboration Messaging Configuration is blocked until this check succeeds." Include the sanitized reason and safe next step for the actual failure; do not call an absent, stale, ambiguous or unreadable result disabled |
| Reporting the scope of a feature blocker | State only the selected task and operation governed by the existing feature gate. Do not claim that all CMK tasks or classic/Gen1 messaging are disabled, and do not substitute a classic, browser or direct API execution route |
| Retaining technical evidence | Keep ORA_CMK_B2B_DOCUMENT_SETUP, FeatureType, EnabledFlag, selected host and read time in sanitized diagnostics and rule results. Do not remove or rename technical query values. A code appearing in diagnostics is an identifier, not an error by itself |

## Opt-In Recovery Steps

1. Navigate to **Navigator → My Enterprise → Offerings**.
2. Select the **Procurement** offering, then select **Opt In Features**.
3. Find **Simplify Configuration and Processing for B2B Messaging**.
4. Select its enable icon and complete the opt-in flow.
5. Wait for the opt-in migration or background processing to finish.
6. Rerun the Simplified Collaboration Messaging Configuration export or import.

## Customer Setup Review

| Situation | What Should Happen |
|---|---|
| Supplier/customer messaging properties already satisfy supplied values | Return reused_and_verified for requested scope. Disclose retained unspecified optional settings once; no clear/preserve question solely for an empty spreadsheet cell, new package or no-op import approval. |
| A property is missing | Return create_needed to the invoking Run Book with validated inputs and current absence evidence. Complete the existing template, provider-dependent validation, immutable-package approval and target-verification workflow before claiming creation. |
| Supplied changes or clear directives differ from existing properties | Group meaningful current/requested differences and missing business decisions into one review where dependencies allow. Identify any unsupported update/clear field specifically; never ask for task codes, endpoint syntax or a new technical prompt. No duplicate create or silent update. |
| A blank attachment differs from a nonblank optional target field | Treat it as unspecified and preserve the current value under the reconciliation policy. Preserve strict approved-import verification independently; never retroactively reinterpret an approved CSV. |
| A read fails or current metadata is incompatible | Report the actual auth/authz, transport/environment, Fusion API or schema failure with a safe resume path. Do not call the customer's data wrong merely because a read failed. |


## Supplier Property Paging Recovery

| Situation | What Should Happen |
|---|---|
| Supplier property IDs repeat across an unordered multi-page response | Report a lookup-integrity failure, not invalid customer data or proven duplicate database records. Use the declared Supplier Property Ordered Pagination contract for a new read from offset 0; preserve the failed unordered evidence separately. |
| The ordered read is valid and complete | Resume the existing collision or requested-state comparison from the new snapshot. Keep the previously verified connection and its import history; no cleanup, new connection or supplier-property import is authorized by paging recovery. |
| Ordering is rejected or the ordered result remains nonunique/inconsistent | Stop with the actual Fusion API, auth/authz or transport/environment failure and safe resume path. Keep strict unique-identity validation; do not hide repeats or delete customer setup to satisfy the validator. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input validation | Route-specific operation, task ZIP, target, project scope, or package information is missing | Provide the missing information for the selected route |
| approval blocker | The task-specific execution contract or required approval is missing | Obtain the approved contract or approval |
| process failed | FSM export, upload, or import reports terminal errors | Retain ProcessLog/result evidence and correct the reported error before a new approved attempt |
| process timeout | The same returned process remains nonterminal after the bounded caller-requested status window | Preserve last status and continue status retrieval for that ID only |

## Business Name Presentation

Apply this policy to every task terminal and permitted progress, validation, approval and
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

These are task-result presentation rules. The invoking Run
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

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before task-CSV import approval | Show the business task name, exact target environment, operation and changes first. Preserve the exact Run Book/task identity, immutable ZIP path and SHA-256, export provenance, Task Hook result and Core Data Loader preview under Business Name Presentation; separate technical details only where the owning preview contract permits |
| Accepted task-CSV import | Preserve Core Data Loader's accepted-initiation report unchanged; no automatic polling, additional report or post-submission project write. Check status/results only when requested |
| On process failure or timeout | Apply Business Name Presentation: show the business task name, last status, practical impact and safe next action first. Retain exact task code, request/process ID, elapsed wait when timed out and ProcessLog/result path in the required operational record and any mandatory diagnostic disclosure |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Public documentation lacks an execution contract | Do not infer a writable API, payload, browser automation, or retry |
| A process result is incomplete or failed | Do not claim completion or retry automatically |
| ZIP bytes, target, task, or preview differ from approval | Do not upload; rerun preflight and obtain approval for the exact artifact |
| Import response is uncertain or a process ID exists | Do not submit a duplicate task-CSV import; reconcile status through Core Data Loader |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.GATE_EXECUTION | decision | 50 | execution_gate | ready->CMKSC.DONE;blocked->CMKSC.RETURN_ISSUES | CMKSC.ENFORCE_DESIGN | stop | Before live execution |
| CMKSC.RETURN_ISSUES | terminal | 60 | terminal | none | none | continue | Any blocking condition Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Feature State Presentation when the blocker concerns the Simplified B2B Messaging feature. Apply Business Name Presentation. |
| CMKSC.CUSTOMER_REQUIRED | terminal | 61 | terminal | none | CMKSC.PARTNER_CUSTOMER | continue | Return missing partner kind or customer selection with current readable choices Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.ACCOUNT_REQUIRED | terminal | 62 | terminal | none | CMKSC.PARTNER_ACCOUNT | continue | Return missing customer account scope or selection Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.SUPPLIER_REQUIRED | terminal | 63 | terminal | none | CMKSC.PARTNER_SUPPLIER | continue | Return missing supplier selection Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.SITE_REQUIRED | terminal | 64 | terminal | none | CMKSC.PARTNER_SITE | continue | Return missing selected supplier site Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.PROVIDER_REQUIRED | terminal | 65 | terminal | none | CMKSC.PARTNER_PROVIDER | continue | Return missing provider selection Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.CUSTOMER_BU_REQUIRED | terminal | 66 | terminal | none | CMKSC.PARTNER_CUSTOMER_BU | continue | Return optional BU select/skip decision or invalid supplied selection Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.VERIFICATION_DONE | terminal | 68 | terminal | none | CMKSC.VERIFY_PROPERTY_STATE | continue | Return exact verified property and compared-snapshot coverage after completed import; report no broader environment or document-exchange claim Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.QUALIFICATION_DONE | terminal | 69 | terminal | none | CMKSC.QUALIFY_SUPPLIER_STATE | continue | Return read-only supplier qualification evidence and per-field comparison coverage; preserve all runtime import, installed-build and target-wide qualification limits Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.DONE | terminal | 70 | terminal | none | CMKSC.GATE_EXECUTION | continue | Execution gate passed Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.REUSE_DONE | terminal | 67 | terminal | none | CMKSC.RECONCILE_SETUP | continue | Return reused_and_verified for current requested partner scope with matched/preserved coverage and no mutation; historical strict-import verification remains separate Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.CREATE_NEEDED | terminal | 71 | terminal | none | CMKSC.RECONCILE_SETUP | continue | Return create_needed and private normalized request/evidence to the invoking Run Book's existing create workflow, not approval or creation success Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |
| CMKSC.REVIEW_REQUIRED | terminal | 72 | terminal | none | CMKSC.RECONCILE_SETUP | continue | Return grouped meaningful differences, missing business decision or precise unsupported change; no implicit update or duplicate create Apply Customer Result Presentation using current-request evidence; preserve the full operational result. Apply Business Name Presentation. |

## Create/Update Preparation Failures

| Situation | What Should Happen |
|---|---|
| Business inputs are missing | Return input validation with the missing field labels; preserve supplied values and ask only for those missing |
| CSV representation, release evidence, or the declared Run Book preparation step is absent | Return an input-validation/workflow gap before package editing; report the exact missing source/rule/processing fact and its owning resource. Partner lookup intake and source export can precede row-mapping qualification |
| Prepared archive lacks baseline provenance or final schema evidence | Stop before Task Hook preview; preserve the original export and regenerate the derived package and preparation record |
| Source export is incomplete, for another task, or a header-only template is used | Stop preparation for incomplete or wrong-task exports. For partner-property creation, allow a completed exact-task header-only template as the seed; the derived ZIP must contain the validated new partner row and satisfy the preparation contract in ora_input_validation.md. Never import the unchanged empty template. Other operations retain their applicable source requirements |
| Duplicate create key, ambiguous update target, or unrelated data changes | Stop before approval; show redacted affected-key evidence and resolve the requested scope; never silently turn create into update |
| Final archive or preparation-evidence persistence fails | Return artifact persistence; do not approve or upload a partial artifact |
| Submission returns an uncertain outcome | Preserve safe identifiers and follow the existing status route; do not replay the import |

These preparation failures are not recoverable by guessing CSV values, using a
browser, or bypassing Data Loader. Contract-only documentation and registry
readiness are not proof of an executable or tested record-creation capability.

## Partner Properties Failures and Review

| Situation | What Should Happen |
|---|---|
| Supplier/customer kind, account scope or lookup selection is missing | Use the corresponding selection terminal and ask one business-facing question; preserve the supplied provider and other valid selections. No final ZIP is required to continue intake |
| Lookup has more than one exact name match | Show distinguishing customer number, account, site or BU context and request explicit selection; do not select the first result |
| A later REST page fails, repeats identities or makes no progress | Return transport/environment or Fusion API failure with incomplete lookup status; never report a missing/unique choice from partial data |
| Customer or supplier changes | Discard child lookup results and option references; resolve the retained child input under the new parent |
| Captured route is missing, stale or for another environment | Stop that lookup with its collection and safe corrective action; do not replay captured credentials, guess replacement paths or use the browser |
| Same-target lookup returns 401/403 | Use the existing Core auth policy for at most one authorized token refresh and read retry; distinguish authentication from insufficient privilege, and never fall back to captured credentials |
| Selected provider lacks partner identifier evidence | Preserve provider selection and name only the applicable unresolved representation. An omitted optional Partner ID remains blank under input validation and is not itself a missing-input error. Partner ID Type qualification uses verify_cmksc_partner_id_type; do not ask for provider-creation fields or assume the Direct-provider example applies |
| Customer BU or partner keys have no verified CSV representation | Return the exact field-mapping gap at preparation; do not place IDs in unrelated columns or ask customers to invent internal keys |
| Existing partner properties collide with create intent | Explain that properties already exist for the selected scope; do not overwrite them, claim creation or launch another import |
| Fusion returns a partner-property validation error | Show the human-readable error text, stripping error-code suffixes, JSON wrappers and duplicate detail text; keep technical classification and safe process references in diagnostics |

## Unresolved Contract Disclosure

| Situation | What Should Happen |
|---|---|
| Partner key, portable-reference, provider-flag or supplied optional-field mapping is unresolved | Return input validation with the exact unresolved contract and evidence reference from ora_input_validation.md. Reuse the confirmed supplier mappings under Partner Properties Public Sources; do not report those mappings missing or ask for their capture/export again. Customer mappings, unqualified provider encodings and populated optional values retain their own boundaries. Preserve resolved business selections; do not request customer values to solve an authoring gap |
| Identifier-type, existing-property or eligibility resolver is incomplete | Return the resolver name, unresolved authority/request/match fields and authoring next action. Do not execute another lookup, infer local authority, broaden the provider filter or substitute a captured save POST |
| Import completed but target-property verification is unresolved | Preserve the import result and safe process references; report import status separately from verification blocked. Use only a qualified verify_cmksc_partner_property_state contract before claiming verified properties; never repeat the import as a verification method |
| Planner reports authoring_incomplete for canonical TBD fields | Stop before runtime execution and report source file, contract and required evidence. Compilation success is not task readiness. Do not erase the blocker, use a readiness override without explicit authorization or weaken Task Hook/Data Loader approval |
| Historical supplier import rejects Partner with CMK_REST_INVALID_ATTRIB | Preserve optional Partner ID intake; report the observed requirement for a Partner value already defined in setup and establish the applicable current partner identity before a separately approved retry. Partner Properties Public Sources's successful retry changed both PartnerId and PartnerIdTypeCode, so do not infer a universal default, requiredness rule or which single field caused recovery. Never invent an identifier from the provider |
| Historical supplier ProcessLog reports one successful partner-property row | Record that one row was processed with its failed/warning counts; do not translate package object totals or this log into a newly created record count, fresh verification, invoice enablement or successful invoice processing. Partner Properties Public Sources qualifies historical import processing only |

Source: ora_input_validation.md, Partner Properties Public Sources, Partner Properties Public Sources
through Partner Properties Public Sources, and this file's existing refusal and uncertain-write rules.
These additions retain all export/import approval gates and status-only
recovery. No Fusion operation is performed by this authoring update.

The execution gate evaluates only the current declared stage. Intake completes
at the bounded boundary before CMKSC.VALIDATE_INPUT; it never executes export or
import. Source export retains the shared export gate. Preparation and import
require their own field, artifact and approval evidence. CMKSC.DONE returns
rule-check readiness for that stage, not a claim that Fusion records were
created. No partner-property import has been verified by this authoring change. post_import_verify ends at CMKSC.VERIFICATION_DONE only after its current comparison passes.

Classify catalog mismatches, auth/authz, transport/environment, Fusion API,
input validation, process failed, process timeout, artifact persistence and
approval blockers separately. For an uncertain write preserve process IDs and
use status-only recovery, never automatic resubmission. Keep raw captures,
partner values, IDs and credentials out of reusable and project files.

## Supplier Qualification Result Boundary

| Situation | What Should Happen |
|---|---|
| Operation qualify_existing_supplier_property reaches CMKSC.QUALIFICATION_DONE | Report fresh feature, identifier-code and supplier-property comparison results with exact coverage; do not claim task-wide readiness, customer qualification, a new create or successful business-document exchange |
| Registry readiness is incomplete before qualification | Obtain explicit user acceptance of the built-in registry-readiness override for this bounded read-only operation. Record the warning and unresolved source anchors; execute only fully specified reached reads, then stop at the qualification terminal. An override cannot supply missing values, authorize another operation or replace mutation approval |


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
| CMKSC.REST_GATE | step | 12 | execution_gate | ready->CMKSC.REST_APPROVAL_READY;blocked->CMKSC.RETURN_ISSUES | CMKSC.REST_PREFLIGHT | stop | Retained historical node only. FSM-Only Route Enforcement rejects new REST or assisted setup before this node; return the task failure outcome if reached for a new write. No Core helper, approval handoff, dispatch or operator Save is authorized. |
| CMKSC.REST_APPROVAL_READY | terminal | 81 | terminal | none | CMKSC.REST_GATE | continue | Retained historical node only. FSM-Only Route Enforcement rejects new REST or assisted setup before this node; return the task failure outcome if reached for a new write. No Core helper, approval handoff, dispatch or operator Save is authorized. Apply Business Name Presentation. |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.REST_VERIFIED | terminal | 82 | terminal | none | CMKSC.REST_VERIFY | continue | Return actual action outcome and verified requested-state coverage separately. Preserve any credential/connectivity or partial-result boundary; do not claim another component is ready, infer no changes or report a PO delivered Apply Business Name Presentation. |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.ASSISTED_GATE | step | 16 | execution_gate | ready->CMKSC.ASSISTED_APPROVAL_READY;blocked->CMKSC.RETURN_ISSUES | CMKSC.ASSISTED_DESIGN | stop | Retained historical node only. FSM-Only Route Enforcement rejects new REST or assisted setup before this node; return the task failure outcome if reached for a new write. No Core helper, approval handoff, dispatch or operator Save is authorized. |
| CMKSC.ASSISTED_APPROVAL_READY | terminal | 83 | terminal | none | CMKSC.ASSISTED_GATE | continue | Retained historical node only. FSM-Only Route Enforcement rejects new REST or assisted setup before this node; return the task failure outcome if reached for a new write. No Core helper, approval handoff, dispatch or operator Save is authorized. Apply Business Name Presentation. |
| CMKSC.ASSISTED_CONTEXT_REQUIRED | terminal | 84 | terminal | none | CMKSC.ASSISTED_CONTEXT | continue | Return the exact current-screen context/identity confirmation step; retain supplied values and request no internal document, runtime URL, secret or ZIP Apply Business Name Presentation. |
| CMKSC.ASSISTED_VERIFIED | terminal | 85 | terminal | none | CMKSC.ASSISTED_RESULT | continue | Return saved configuration and per-field operator verification. No whole-environment, transport-authentication or PO receipt claim Apply Business Name Presentation. |
| CMKSC.ASSISTED_REUSED | terminal | 86 | terminal | none | CMKSC.ASSISTED_RESULT | continue | Return unchanged requested configuration with current scope and field evidence; no setup write occurred Apply Business Name Presentation. |
| CMKSC.ASSISTED_STATE_ONLY | terminal | 87 | terminal | none | CMKSC.ASSISTED_RESULT | continue | Return requested state confirmed while the prior action remains uncertain. Never replay a save or infer creation Apply Business Name Presentation. |
| CMKSC.ASSISTED_CONFIRMATION_REQUIRED | terminal | 88 | terminal | none | CMKSC.ASSISTED_RESULT | continue | Return the exact missing fresh screen/field confirmation; preserve actual action outcome without a new save Apply Business Name Presentation. |

## All Object Error Situations

| Situation | What Should Happen |
|---|---|
| Customer choice/access/existing master data is missing | State the concrete business choice or administrator action needed; retain other supplied input and never request credentials in chat |
| Object mapping or executor is unqualified | Record a skill defect with object, operation, missing contract and public research performed. Do not reclassify it as a customer prerequisite or claim full customer readiness |
| Schema validation passed but live execution was not performed | Record validation-only coverage and live status not_run or blocked, with the exact missing step; no passing CRUD or delivery claim |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.ROUTING_STATE_VERIFIED | terminal | 94 | terminal | none | CMKSC.VERIFY_ROUTING_STATE | stop | Existing requested default and supplier-site routing verified. Return exact current setup-state coverage and preserved requested scope; do not claim new routing creation, document enablement, activation or business delivery Apply Business Name Presentation. |


## Qualified LOB Rejection After Local Validation

The existing error-handler and REST result nodes classify a current HTTP 400
on Data with CMK-4215315 / CMK_B2B_CONN_JSON_DETAIL as a Fusion API rejection,
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

## Native FSM Account Number Outcomes

| Situation | What Should Happen |
|---|---|
| Account source artifacts are missing | Return the exact-task header-only template and full-baseline export requirements to the invoking shared export workflow. Retain valid business choices. Do not ask the customer for a generated ID or use old-column-profile packages |
| A current native account import fails | Retain the exact approved row/ZIP hash, target and process IDs; retrieve ProcessLog and compare a fresh task export before any new attempt. A field or importer mismatch is not proof that the customer's business account number is invalid. No REST/UI fallback or automatic replay |
| A requested field is absent from the four-column account profile | Return the precise unsupported field/profile boundary without silently dropping it. Preserve any dependent ship-to requirement separately; successful account creation does not prove the assignment exists |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_ACCOUNT_SOURCE_REQUIRED | terminal | 103 | terminal | none | CMKSC.FSM_ACCOUNT_REFERENCES | continue | Return the precise source/template requirements to the invoking shared export step with retained account/supplier/site intent. No import or guessed package Apply Business Name Presentation. |
| CMKSC.FSM_ACCOUNT_PREPARE_NEEDED | terminal | 104 | terminal | none | CMKSC.FSM_ACCOUNT_PACKAGE | continue | Return the qualified four-cell business intent, source/template fingerprints and private before-snapshot to Prepare Account Number CSV ZIP. This is preparation readiness, not creation or approval Apply Business Name Presentation. |
| CMKSC.FSM_ACCOUNT_LOAD_READY | terminal | 105 | terminal | none | CMKSC.FSM_ACCOUNT_PACKAGE | continue | Return the exact immutable prepared account ZIP and rule evidence to Core Data Loader's preflight, Task Hook and approval workflow. Never claim submitted or created from this terminal Apply Business Name Presentation. |
| CMKSC.FSM_ACCOUNT_ISSUES | terminal | 106 | terminal | none | none | continue | Return stage/failure class, precise business/reference/profile issue, sanitized evidence and one safe resume step. Apply Native FSM Account Number Outcomes and Customer Result Presentation; no write or fallback Apply Business Name Presentation. |
| CMKSC.FSM_ACCOUNT_VERIFIED | terminal | 112 | terminal | none | CMKSC.FSM_ACCOUNT_VERIFY_STATE | continue | Return the new account mapping and exact fresh-export verification coverage. No generated numeric ID, ship-to assignment, routing or message-delivery claim Apply Business Name Presentation. |
| CMKSC.FSM_ACCOUNT_VERIFY_ISSUES | terminal | 113 | terminal | none | none | continue | Preserve the actual account import result separately from missing/failed saved-state verification; return safe comparison diagnostics without a new import Apply Business Name Presentation. |

## Native FSM Ship-To Assignment Outcomes

| Situation | What Should Happen |
|---|---|
| Selected account is absent or belongs to another parent | Return the concrete account/supplier/site/BU prerequisite or conflict. Do not create an account implicitly or substitute another saved mapping |
| Native import reports a missing ShipToLocationCode despite supplied data | Preserve exact current headers, seven-cell row/hash, validated physical reference and actual ProcessLog. Verify forwarded immutable bytes and current schema before diagnosing an importer mismatch; do not erase the supplied code, add old identity headers or reclassify a different historical profile as this test |
| A location already has an assignment at the same supplier site | Return duplicate or reassignment conflict without changing its account. Strict create does not authorize moving the existing location mapping |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_SHIP_TO_SOURCE_REQUIRED | terminal | 123 | terminal | none | CMKSC.FSM_SHIP_TO_REFERENCES | continue | Return exact-task full-baseline/template requirements to invoking shared export while retaining valid business choices; no guessed package Apply Business Name Presentation. |
| CMKSC.FSM_SHIP_TO_PREPARE_NEEDED | terminal | 124 | terminal | none | CMKSC.FSM_SHIP_TO_PACKAGE | continue | Return qualified seven-cell intent and private parent/location/absence evidence to Prepare Ship-To Assignment CSV ZIP; preparation readiness only Apply Business Name Presentation. |
| CMKSC.FSM_SHIP_TO_LOAD_READY | terminal | 125 | terminal | none | CMKSC.FSM_SHIP_TO_PACKAGE | continue | Return exact immutable assignment ZIP and validation evidence to Core Data Loader preflight, Task Hook and approval; no submitted/created claim Apply Business Name Presentation. |
| CMKSC.FSM_SHIP_TO_ISSUES | terminal | 126 | terminal | none | none | continue | Return exact input/reference/profile/process failure, safe evidence and resume stage. No implicit account creation, reassignment, setup REST/UI fallback or import retry Apply Business Name Presentation. |
| CMKSC.FSM_SHIP_TO_VERIFIED | terminal | 132 | terminal | none | CMKSC.FSM_SHIP_TO_VERIFY_STATE | continue | Return the newly saved assignment, verified account parent and seven-field/preservation coverage only; no document-routing or delivery claim Apply Business Name Presentation. |
| CMKSC.FSM_SHIP_TO_VERIFY_ISSUES | terminal | 133 | terminal | none | none | continue | Preserve actual import result separately from failed/missing assignment comparison; return safe diagnostics without reimport Apply Business Name Presentation. |

## Native FSM Customer Location Outcomes

| Situation | What Should Happen |
|---|---|
| Customer/site/purpose evidence is missing or conflicting | Retain the selected business requirement and name the exact missing parent, effective purpose or bill-to account-site relation. Complete the declared read-only joins; never create a customer/site, ask the customer for importer IDs, clear bill-to fields to force ship-only scope or select the first account tuple |
| Standard profile does not represent an explicit field | Preserve the supplied PartyType, SiteUseCode, SiteUseType, domain or other requested setting and return that exact field/profile qualification gap. The common standard customer-location branch does not authorize arbitrary classifications; do not omit the input and claim its requirement passed |
| Native import reports missing XrefLocValueId | Preserve current genuine header/metadata and exact immutable intent, actual ProcessLog, target/process IDs and fresh post-failure export. The thirteen-column portable profile deliberately excludes the generated identity. A historical full-ID workaround is a different profile; do not append an obsolete key, copy an existing ID, rewrite metadata or retry unchanged bytes |
| Import succeeds but purpose/account-site verification differs | Preserve actual successful job status separately from the failed thirteen-field comparison. Report the exact expected/observed flag, account-site reference or blank and keep the customer requirement incomplete. Do not reduce verification to code existence or overwrite the saved row without a separately qualified action |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_LOCATION_SOURCE_REQUIRED | terminal | 143 | terminal | none | CMKSC.FSM_LOCATION_REFERENCES | continue | Return exact-task header-only template/full-baseline requirements to the invoking shared export workflow with current customer/site/code intent and request fingerprints retained; no guessed package Apply Business Name Presentation. |
| CMKSC.FSM_LOCATION_PREPARE_NEEDED | terminal | 144 | terminal | none | CMKSC.FSM_LOCATION_PACKAGE | continue | Return the qualified thirteen-cell intent, complete purpose/account-site/collision evidence and bound source/target/request fingerprints to Prepare Customer Location Code CSV ZIP. Preparation readiness only Apply Business Name Presentation. |
| CMKSC.FSM_LOCATION_LOAD_READY | terminal | 145 | terminal | none | CMKSC.FSM_LOCATION_PACKAGE | continue | Return exact immutable native location ZIP and all-field validation evidence to Core Data Loader preflight, Task Hook and its approval. Never claim creation or submission from this terminal Apply Business Name Presentation. |
| CMKSC.FSM_LOCATION_ISSUES | terminal | 146 | terminal | none | none | continue | Return the exact current input/source/reference/profile/process failure, preserved requested fields, safe evidence and resume stage. Apply Native FSM Customer Location Outcomes and Customer Result Presentation; no setup REST/UI fallback, new master record or retry Apply Business Name Presentation. |
| CMKSC.FSM_LOCATION_VERIFIED | terminal | 152 | terminal | none | CMKSC.FSM_LOCATION_VERIFY_STATE | continue | Return the newly saved location code and exact thirteen-field purpose/account-site/preservation coverage, bound current customer request and actual FSM result. No generated-ID, inbound transaction or message-delivery claim Apply Business Name Presentation. |
| CMKSC.FSM_LOCATION_VERIFY_ISSUES | terminal | 153 | terminal | none | none | continue | Preserve actual import result independently from missing or failed saved-state comparison. Return exact field/current-request/evidence failure and safe next check without reimport Apply Business Name Presentation. |

## Native FSM Initial Settings Outcomes

| Situation | What Should Happen |
|---|---|
| Required current template/full before-export is absent | Return source_required to the invoking shared export step with the selected business fields retained. No source ID or historical value proves current identity |
| A global parameter or document-property ID is absent on this target | Stop before preparation. The native importer qualifies existing target parameter identities; do not allocate an ID, copy another environment's row or fabricate a global record |
| A document property lacks a semantic join | Return the missing current document/additionalConfigs link, readable field or unambiguous match. A four-column row without its name/parent join is not a safe customer choice; never ask the customer for ParamDataId |
| A setting lacks a qualified unit, encoding or constraint | Retain the requirement and report the precise field-level gap. Do not borrow a similarly named field's multiplier, invent an enum, reinterpret zero as blank or omit the field |
| Import skips invalid parameter IDs, partially fails or reports a commit error | Preserve immutable approved bytes, current reference/before evidence and actual task/process IDs; retrieve ProcessLog and a fresh task export through the owning services. Report each object's actual outcome and separate saved-state comparison. No REST/UI fallback or automatic replay |
| Requested values already match | Return per-field comparison coverage without a no-op import. This meets only the selected initial-setting requirement; it is not a changed-value test or proof of scheduler/message behavior |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_SETTINGS_SOURCE_REQUIRED | terminal | 164 | terminal | none | CMKSC.FSM_SETTINGS_REFERENCES | continue | Return full-before/template requirements and retained business intent to the invoking shared export step; no import or guessed row Apply Business Name Presentation. |
| CMKSC.FSM_SETTINGS_PREPARE_NEEDED | terminal | 165 | terminal | none | CMKSC.FSM_SETTINGS_PACKAGE | continue | Return qualified selected existing rows, field deltas/units and private source/reference fingerprints to Prepare Initial Settings CSV ZIP; preparation readiness only Apply Business Name Presentation. |
| CMKSC.FSM_SETTINGS_LOAD_READY | terminal | 166 | terminal | none | CMKSC.FSM_SETTINGS_PACKAGE | continue | Return exact immutable settings ZIP and rule evidence to Core Data Loader preflight, Task Hook and approval. No submitted/configured claim Apply Business Name Presentation. |
| CMKSC.FSM_SETTINGS_ISSUES | terminal | 167 | terminal | none | none | continue | Return exact input/reference/profile/effective-design issue, failure class, sanitized evidence and safe resume. No new global row, guessed ID, fallback or retry Apply Business Name Presentation. |
| CMKSC.FSM_SETTINGS_ALREADY_SATISFIED | terminal | 168 | terminal | none | CMKSC.FSM_SETTINGS_DESIGN | continue | Return requested initial settings as already satisfied with current comparisons and unspecified fields preserved. No import, new change, scheduler or delivery claim Apply Business Name Presentation. |
| CMKSC.FSM_SETTINGS_VERIFIED | terminal | 172 | terminal | none | CMKSC.FSM_SETTINGS_VERIFY_STATE | continue | Return actual FSM setup outcome and exact changed/same-value per-field comparison, preserved identities/counts/unrelated state and current request binding. No reprocessing or delivery claim Apply Business Name Presentation. |
| CMKSC.FSM_SETTINGS_VERIFY_ISSUES | terminal | 173 | terminal | none | none | continue | Preserve actual import result separately from failed/missing comparison. Return the exact issue and safe next read without another import Apply Business Name Presentation. |


## Native FSM Routing Outcomes

| Situation | What Should Happen |
|---|---|
| Missing current profile, generated-key or header mapping | Return the exact input-contract issue before preparation. The customer need not supply a technical ID or access an internal research service. Preserve the requirement; do not allocate DetailId or switch to setup REST/UI |
| Supplier-site B2B communication callback fails | Preserve actual process failure and approved bytes. Retrieve ProcessLog and business-object result through Core; the callback response/status and target/site relation are diagnostic facts. The generic exception alone does not establish bad JSON, bad DetailId or an operator permission failure. A generic Data Loader invalid-value summary is not a diagnosis when the native log identifies this callback. Record failure_class process_failed and root_cause unknown unless a specific underlying response proves another class. The product/environment owner must retrieve the correlated callback HTTP status, redacted response and service log for the same request and timestamp. Do not alter credentials, supplier settings or retry solely to suppress it |
| Native row processed but commit fails | A detail-object processed count, even with zero row failures, does not override a native Completed with errors result or commit exception. Keep the supplier-site positive test failed. Through the invoking shared workflow obtain a fresh full export and the declared supplier-site communication read; compare all eight object datasets and the coupled method with before state. Report verified no-change, partial commit or unknown separately. Preserve any independently successful default rule. Resume with fresh validation and a new explicit Core approval only after a documented cause or corrective change; never convert the failed import into a pass or replay unchanged input |
| Timeout, uncertain submission or partial commit | Reconcile the same external request using Core result retrieval and a fresh export before any new mutation. Retain a successful default rule separately from a failed supplier rule; no replay of either assumed failed request |
| Completed import but field/preservation check fails | Record the actual completed job separately from failed customer acceptance. Keep both rules incomplete until each intended row and all required state comparisons pass |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_ROUTING_SOURCE_REQUIRED | terminal | 183 | terminal | none | CMKSC.FSM_ROUTING_REFERENCES | continue | Return exact full-before/provider/header-only-template needs and retained business scope to the invoking shared export workflow; no speculative ZIP Apply Business Name Presentation. |
| CMKSC.FSM_ROUTING_PREPARE_NEEDED | terminal | 184 | terminal | none | CMKSC.FSM_ROUTING_PACKAGE | continue | Return qualified eight-cell intent, new-ID contract, complete references/collisions and coupled supplier effect to Prepare Document Routing CSV ZIP; preparation readiness only Apply Business Name Presentation. |
| CMKSC.FSM_ROUTING_LOAD_READY | terminal | 185 | terminal | none | CMKSC.FSM_ROUTING_PACKAGE | continue | Return exact immutable native rule ZIP and all-field/provenance validation to Core Data Loader preflight, Task Hook and its own approval. No submitted/created claim Apply Business Name Presentation. |
| CMKSC.FSM_ROUTING_ISSUES | terminal | 186 | terminal | none | none | continue | Return exact input/catalog/auth/transport/contract/process/artifact/approval failure, preserved request, safe evidence and resume step. No generated ID invention, master creation, setup REST/UI fallback or automatic replay Apply Business Name Presentation. |
| CMKSC.FSM_ROUTING_VERIFIED | terminal | 192 | terminal | none | CMKSC.FSM_ROUTING_VERIFY_STATE | continue | Return the saved requested routing rule, generated identity, exact all-field and all-object preservation coverage and actual coupled-effect comparison. Both default and supplier-site passes are required for combined completion; no activation or message-delivery claim Apply Business Name Presentation. |
| CMKSC.FSM_ROUTING_VERIFY_ISSUES | terminal | 193 | terminal | none | none | continue | Preserve actual job result separately from missing/different rule or unexpected state. Return exact comparison and safe next read without another import Apply Business Name Presentation. |


## Combined Account and Ship-To Outcomes

| Situation | What Should Happen |
|---|---|
| Native combined job failed, partial or uncertain | Preserve exact immutable package and per-object results. Retrieve status/ProcessLog through the existing Core workflow, then reconcile both intended rows and all prior objects through a fresh full approved export before considering another attempt. Never infer rollback, replay the ZIP, auto-split it, alter native ordering or allocate IDs. Report created/missing/conflicting components individually with the exact diagnostic |
| Native combined job accepted or reported successful | Accepted initiation is not completion. The explicitly requested end-to-end test includes the existing status and shared-export verification follow-up. Only the bound all-cell/two-row/preservation comparison establishes combined saved-setup acceptance; it does not prove PO delivery |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.COMBINED_PREPARE | terminal | 197 | terminal | none | CMKSC.COMBINED_PACKAGE | continue | Return qualified retained inputs to the active Run Book Prepare Combined Account and Ship-To CSV ZIP step and continue preparation without a new proceed question. This is not creation or approval Apply Business Name Presentation. |
| CMKSC.COMBINED_LOAD_READY | terminal | 198 | terminal | none | CMKSC.COMBINED_PACKAGE | continue | Return one immutable two-row native ZIP and complete source/reference/rule evidence to Core Data Loader and Task Hook for their authoritative approval/upload workflow. Preapproval readiness does not establish runtime acceptance Apply Business Name Presentation. |
| CMKSC.COMBINED_VERIFIED | terminal | 200 | terminal | none | CMKSC.COMBINED_VERIFY | continue | Return both created-and-verified business components, actual single job/result, bound intent/snapshot hashes and preservation coverage. This proves only the bounded account/physical assignment setup and not arbitrary batching, reassignment, routing or delivery Apply Business Name Presentation. |
| CMKSC.COMBINED_ISSUES | terminal | 201 | terminal | none | none | stop | Return the exact failed input/reference/package/job/verification check, completed path, actual partial side effects and one safe next action. Preserve unknown outcomes and do not submit another import Apply Business Name Presentation. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.COMPOSITION_PREPARE | terminal | 403 | terminal | none | CMKSC.COMPOSITION_PACKAGE | stop | Return qualified retained seven-row intent to active Run Book assisted Prepare Configuration Task Composition CSV ZIP and continue preparation without another proceed question. This is not creation or approval |
| CMKSC.COMPOSITION_LOAD_READY | terminal | 404 | terminal | none | CMKSC.COMPOSITION_PACKAGE | stop | Return one seven-row immutable native archive, exact task/target, component rule outcomes and source/intent/reference hashes to Core Data Loader and Task Hook. Preserve their authoritative approvals and initiation terminal. This is a qualification candidate, not saved-state acceptance |
| CMKSC.COMPOSITION_VERIFIED | terminal | 406 | terminal | none | CMKSC.COMPOSITION_VERIFY | stop | Return actual one-job/per-object outcomes, five created components, both selected settings dispositions, exact approved/saved cell comparisons and complete eight-object prior-row/unspecified-cell preservation. No activation, delivery, transform execution, arbitrary batching or rollback claim |
| CMKSC.COMPOSITION_ISSUES | terminal | 407 | terminal | none | CMKSC.ROUTING_REFERENCE | stop | Return the exact failing composition input/reference/package/job/cell check, actual per-component saved side effects and errors, complete source/request fingerprints and safe resume context. Do not omit scope, infer approval or retry a mutation |
