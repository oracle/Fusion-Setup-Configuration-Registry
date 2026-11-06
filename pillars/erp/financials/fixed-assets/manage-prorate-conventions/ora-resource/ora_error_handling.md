# Manage Prorate Conventions: Error Handling

Use the owning resource's classified result below; do not repeat its validation
algorithm. All responses follow Disclosure Rules, and continuation follows
[Conversation State and Resume](ora_dependency_readiness.md#conversation-state-and-resume).

## Error Situations

| Situation | What Should Happen |
|---|---|
| Missing or proven invalid business input | Use Correction Question Contract in ora_input_validation.md. |
| Create-name conflict | State that the Name already exists and ask only for a different Name. Mention update only if explicitly requested; do not ask a generic create-versus-update question. |
| Configured connection settings are missing, unreadable, malformed, or incomplete | Explain the observed settings problem and required correction. Do not fall back to another target. |
| Shared authentication fails | Ask for sign-in only if the shared capability actually reports an interactive-sign-in requirement. Otherwise explain the observed connection failure and corrective action. Sign-in is not an approval; resume the blocked phase through Conversation State and Resume. |
| Required access is missing | Explain which business verification or submission the account lacks access to perform. |
| Read-only lookup has an API or transport failure | Allow at most three total attempts, including the initial attempt. Do not retain a failed page or advance its offset. After the third failure, report the affected check and observed reason. |
| Collection result is incomplete, repeated, non-progressing, or unreadable | Explain the observed collection problem; partial results cannot verify the value. |
| No matching fiscal-year cycle | Say No fiscal year found for the requested start–end month period. For create/update ask for another period or the exact Fiscal Year Name; for an inquiry ask which period to check instead. |
| Required latest-update comparison or last-updated information is unavailable | Explain the missing/unreadable update information. For automatic create/update selection, ask for an exact Fiscal Year Name. For an inquiry, report the limitation. Do not call the period invalid, report no matches, or request manual timestamps. |
| Required refresh fails while older evidence exists | Apply Fiscal-Year Lookup Freshness and explain the current failure. If relevant, distinguish the retained selection's recorded check time from the unverified current result using Disclosure Rules. |
| Fiscal-year name/cycle conflict | State the observed boundary-month mismatch, including mixed month pairs when present, and ask for a corrected name or cycle. |
| Fiscal-year boundary or non-null midpoint evidence is malformed, out of range, or conflicting | Identify the affected fiscal-year evidence and ask for its setup to be checked. |
| Returned fiscal-year sequence has a gap or overlap | State the observed missing period or overlap and ask for that Fiscal Year Name's setup to be checked. |
| Date generation, fallback, or integrity fails | Identify the normalized basis, affected fiscal-year range, and observed failure. Preserve supplied values and use [Design Rules](ora_design_enforcement.md#design-rules) to distinguish a genuine conflict from remaining unused fiscal-year coverage. |
| Existing-ZIP basis resolution fails | Report the resolution gap during Task Hook validation and apply the Immutable artifact rule in Design Enforcement. |
| Validation export is missing or stale | Resume automatic verification through the shared export route. Reuse an existing process instead of starting a duplicate. On terminal failure, explain why checking existing conventions failed from the returned evidence. |
| Reference Data Set name is valid but code mapping fails | Use the validity result from validate_reference_data_set_name in [Live Lookups](ora_reference_lookups.md#live-lookups); explain why the code could not be determined, stop preparation, and ask for the Reference Data Set setup to be checked. |
| Convention Info mapping fails | Identify the unresolved supplied entry and stop preparation. |
| Export-only or inquiry enters create/update processing | Return to its route in Required Dependency Order. |
| Existing-ZIP route changed or replaced the archive | Discard the rebuilt path and resume Core validation with the original archive. |
| Prepared package fidelity fails | Retain approved configuration and report one package-correction action, not a submission-approval prompt. |
| Shared export, ZIP preparation, upload, import, or result check fails, remains unfinished, or completes partly | Use the existing owner from Parent Workflow Continuation or SKILL.md, then translate its returned outcome through Disclosure Rules. Do not add an executor, retry policy, or approval gate. |
| Fusion reports gaps/overlaps after a sorted copy passed coverage | Check Actual package row order in Design Enforcement and use the declared live existing-convention lookup to check exact parent/detail state before a correction. Do not infer fiscal-year setup gaps from that message alone. Preserve the failed archive and approved business values; corrections use existing parent gates. Describe an ordering defect as locally verified, not server-side recovery until a corrected approved import succeeds. |

## Parent Import Handoff

After `core.data-loader` accepts the exact approved immutable FSM package,
report **accepted — pending parent verification** and hand off the archive
identity, target, and request ID to the Fixed Assets parent. The parent owns
terminal-status polling, FSM ProcessLog review, fresh target-state read-back,
and any dependent-task progression. This child skill must not poll the request,
declare the prorate convention complete, or start a dependent task from the
accepted state.

## Disclosure Rules

For preview field labels, use
[Business Review Mapping](ora_dependency_readiness.md#business-review-mapping).

| Gate | What Must Be Shown |
|---|---|
| All user-facing responses | Use concise plain business language. Fusion and ZIP are acceptable; keep API/BOSS/FSM/HTTP/OAuth, resolver/schema/Task Hook terminology, technical field names, internal paths, error codes, request IDs, retry counts, CSV/XML details, raw errors, and stack traces out of replies. Preserve business values and usable ZIP links. |
| Inherited report wording | Core Data Loader owns its approval preview and accepted-initiation report; preserve those required outputs. Keep task explanations concise and include actionable diagnostics and requested deliverable links. |
| Failed or blocked operation | State what could not complete, the observed reason, what is known about the outcome, and one safe next action. Use the owning task/parent/Core evidence; never invent a cause or replace a known reason with a generic blocked message. If no usable reason is available, say so and suggest the appropriate support action. |
| Unfinished, partial, or uncertain outcome | Distinguish failure, running work, a check that did not finish, partial completion, and unknown completion. Do not claim success, no submission, or unchanged Fusion configuration without verification. Use the owner's safe status/recovery action under Conversation State and Resume. |
| Post-import handoff | Owner: Fixed Assets parent and `core.data-loader`; state: `accepted — pending parent verification`; immutable archive fingerprint, target, requested prorate convention name and fiscal-year scope, and request ID. |
| Internal failure evidence | Keep the resolved target, lookup name, failure class, attempt count, authentication outcome, process reference, and last status in sanitized workflow evidence, not normal replies. |
| Fiscal-year freshness or timestamps | Answer under Fiscal-Year Lookup Freshness. A latest claim includes actual check time and timezone; historical selection is labelled as of its recorded check. Distinguish checked from last updated. Last updated proves neither creation time nor absence at an earlier lookup without separate evidence. If a past check time is unavailable, say so; never infer it from an artifact filename/date. Use plain labels, not field names. |
| Secrets | Never display or persist passwords, access tokens, authorization headers, or token-cache content. Never request credentials or reuse pasted credentials/tokens in a token-relay request. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Connectivity/authentication blocks live evidence | Do not offer a user-provided export ZIP as a substitute for required live lookup/existing-state validation or the declared create/update export-acquisition route. For update date retrieval, resolve_existing_prorate_dates explicitly requires a fresh skill-acquired export directly, without a BOSS date request. |
| Only business intake is complete | Do not claim the convention details are correct and complete before all applicable lookups and fresh same-target export dependencies succeed. |
| Submitted import without verified matching target state | Do not report the prorate convention as created solely because an archive was accepted or a related job succeeded. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PRC.DONE_EXISTS | terminal | 43 | terminal | none | PRC.LOOKUP_CONTEXT | stop | Create-name conflict: report Convention name already exists and ask only for a different Name. No equivalence claim, package preparation, or submission. |
| PRC.DONE_FISCAL_YEARS | terminal | 44 | terminal | none | PRC.LOOKUP_CONTEXT | continue | Complete nonempty inquiry finding; report the read-only result through Parent Workflow Handoff in ora_dependency_readiness.md. |
| PRC.HANDLE_INPUT | step | 45 | error_handler | handled->PRC.ISSUES | PRC.VALIDATE_INPUT | stop | Input is missing or invalid; use Error Situations. |
| PRC.HANDLE_LOOKUP | step | 50 | error_handler | handled->PRC.ISSUES | PRC.LOOKUP_CONTEXT | stop | An applicable lookup is invalid, unresolved, or failed; use Error Situations. |
| PRC.HANDLE_GENERATION | step | 60 | error_handler | handled->PRC.ISSUES | PRC.GENERATE_DATES | stop | Basis matching or date calculation failed; use Error Situations. |
| PRC.HANDLE_DESIGN | step | 65 | error_handler | handled->PRC.ISSUES | PRC.ENFORCE_DESIGN | stop | Date-integrity checks failed; use the generation-failure Error Situations. |
| PRC.HANDLE_PACKAGE | step | 70 | error_handler | handled->PRC.ISSUES | PRC.RESOLVE_PACKAGE | stop | Package readiness, evidence, or target-state decision is unresolved; use Error Situations. |
| PRC.IMPORT_GATE | decision | 75 | execution_gate | approved->PRC.HANDED_OFF_TO_PARENT;approval_missing->PRC.HANDLE_APPROVAL | PRC.RESOLVE_PACKAGE | stop | The Final ZIP Preview identifies one validated immutable package for live import. |
| PRC.HANDLE_APPROVAL | step | 76 | error_handler | handled->PRC.ISSUES | PRC.IMPORT_GATE | stop | Import approval is missing. |
| PRC.ISSUES | terminal | 80 | terminal | none | none | continue | An input, lookup, generation, or package-readiness issue remains |
| PRC.HANDED_OFF_TO_PARENT | terminal | 170 | terminal | none | PRC.IMPORT_GATE | continue | Prorate Conventions import is accepted — pending parent verification. |
