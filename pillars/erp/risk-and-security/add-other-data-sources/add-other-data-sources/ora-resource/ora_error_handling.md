# Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Risk Cloud authentication fails | Stop before task handoff; restore the approved Add EPM Data Sources client scope and target binding, and retain sanitized evidence. |
| REST endpoint or payload contract is missing or ambiguous | Stop and report the contract gap; do not substitute another route. |
| Payload contains credentials or undocumented fields | Stop; remove the sensitive or unsupported values and rebuild the preview. |
| OpenAPI response schema cannot produce extraction attributes | Stop; correct the documentation-backed response schema and regenerate the REST-operation contract before creating a revised approval artifact. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Authentication blocker | Risk Cloud OAuth is rejected | Correct the approved shared client scope and target binding, then revalidate the task inputs. |
| REST contract gap | Endpoint, method, or payload contract is unavailable | Obtain supported REST guidance. |
| Payload validation gap | Payload is incomplete or contains prohibited content | Correct the payload and rebuild the approval artifact. |
| OpenAPI extraction schema gap | A selected successful JSON response has no derivable extraction attributes | Correct the OpenAPI response schema and regenerate REST Operations. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Contract verification | Sanitized contract-source status and one safe next action. |
| Authentication verification | Target environment and OAuth scope status; never tokens, client secrets, or private keys. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Registration outcome is uncertain or the predefined-source query is empty | Do not infer absence of pending registrations, rebuild a creation preview, replay POST, or complete the task from this evidence; reconcile the exact registration through the separate read-only recovery contract. |
| REST contract is unverified or payload validation is incomplete | Do not claim the task is ready for downstream execution. |
| OpenAPI response validation fails | Do not create, register, or update a connector definition from the incomplete contract. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CDS.READINESS_GATE | decision | 60 | execution_gate | ready->CDS.DONE_VALIDATED;blocked->CDS.HANDLE_ISSUE | CDS.ENFORCE_DESIGN | stop | After validation, dependency, design, and any required OCI verification checks and before task handoff |
| CDS.HANDLE_ISSUE | step | 70 | error_handler | handled->CDS.RETURN_ISSUES | none | stop | Any blocking issue |
| CDS.RETURN_ISSUES | terminal | 80 | terminal | none | none | stop | A blocking issue was classified |
| CDS.DONE_VALIDATED | terminal | 90 | terminal | none | CDS.READINESS_GATE | stop | All documented resource-authoring gates are satisfied |
