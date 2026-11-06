# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required offering, feature, or provisioning prerequisite is unavailable | Stop and report the prerequisite, environment, and routed next action. |
| A source-required REST contract is TBD | Stop before any external request and record the authoring gap. |
| OM setup cannot be verified | Do not infer success; return the evidence required for follow-up. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Required environment or scope is missing | Request the missing value. |
| Catalog mismatch | Offering or feature selection is absent or ambiguous | Resolve through the offering workflow. |
| Auth/authz | Read-only verification is rejected | Confirm privileges and retry only as the selected workflow permits. |
| Approval blocker | A mutation is requested without its immediate, exact approval | Present the target, operation, and immutable preview for approval. |
| Manual-task blocker | The Oracle CPQ process assignment rule is missing, inactive, undeployed, or not administrator-confirmed | Direct the Order Management administrator to Manage Process Assignment Rules for Sales Orders; do not attempt an undocumented REST route. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before mutation | Return Core's complete approval-required Markdown verbatim; its preflight and Task Hook preview bind the final artifact, target and task. |
| On failure | Failure class, stage, redacted evidence, and safe next action. |

## Core Status and Recovery Contract

| Situation | What Should Happen |
|---|---|
| Upload and initiation accepted | Report accepted submission immediately and pause; no automatic status query or polling. |
| User requests status, progress, results, counts, errors or other load information | Use the Core status/error helper for the accepted request ID; pending or unavailable status blocks completion. |
| Requested status check confirms successful load | Resume declared read-backs; require compliant Commerce value or user-managed connection enablement before readiness. |
| Failed, timed-out or uncertain submission/load | Use Core recovery rules; no automatic retry. Retain sanitized task stage and external IDs in the project run, without credentials or sensitive raw responses. Retain only the Core-prescribed preflight, Task Hook and diagnostic artifacts through their owning workflows. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQOM.COMMERCE_CHANGE_GATE | step | 38 | execution_gate | preview_ready->CPQOM.COMMERCE_IMPORT_READY;payload_invalid->CPQOM.HANDLE_ISSUE | CPQOM.CHECK_COMMERCE_SETTING | stop | The Commerce setting is not Yes; require the exact validated final CpqCommerceSettings archive records and leave approval to the Core Data Loader and Task Hook preview |
| CPQOM.COMMERCE_IMPORT_READY | terminal | 39 | terminal | none | CPQOM.COMMERCE_CHANGE_GATE | stop | The fixed Commerce setting archive records are ready for the Core Data Loader approval preview; no upload or initiation has occurred |
| CPQOM.GENERIC_CHANGE_GATE | step | 48 | execution_gate | preview_ready->CPQOM.GENERIC_INTEGRATION_READY;payload_invalid->CPQOM.HANDLE_ISSUE | CPQOM.CHECK_GENERIC_INTEGRATION | stop | The named Generic Integration is absent; require live Data Loader metadata, validated final IntegrationVendors archive records, placeholder credentials, and enabled=false before Task Hook builds its approval preview |
| CPQOM.GENERIC_INTEGRATION_READY | terminal | 55 | terminal | none | CPQOM.GENERIC_CHANGE_GATE | stop | The validated Generic Integration archive records are ready for the Core Data Loader approval preview; no upload or initiation has occurred |
| CPQOM.PROCESS_ASSIGNMENT_RULE_READY | terminal | 78 | terminal | none | CPQOM.VERIFY_OM_PROCESS_ASSIGNMENT_RULE | stop | The Oracle CPQ process assignment rule is administrator-confirmed active and deployed |
| CPQOM.HANDLE_ISSUE | terminal | 80 | terminal | none | none | stop | Any validation, dependency, lookup, design, or execution blocker |
