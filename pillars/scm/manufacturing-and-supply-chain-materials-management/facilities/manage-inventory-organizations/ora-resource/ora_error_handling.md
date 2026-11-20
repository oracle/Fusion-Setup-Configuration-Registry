# Manage Inventory Organizations Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required organization identity, ownership, item-master, or location data is missing | Stop and request only the missing approved value |
| Exact organization lookup finds no source or more than one source | Stop and ask for an unambiguous OrganizationId, OrganizationCode, or OrganizationName |
| A duplicate OrganizationCode or OrganizationName is found | Stop and require a distinct identity; do not convert the request into an update |
| A definition/reference count, completed duplicate-check evidence, or requested organization type is unavailable | Stop creation and explain the missing information in business language using the Customer Messages and Design Rules in ora_design_enforcement.md; retain technical diagnostics in the execution handoff |
| The estimated projected reference-organization percentage is 80% or below | Stop creation pending a passing check or explicit user waiver. Follow the Customer Messages response contract in ora_design_enforcement.md: show the blocked outcome, estimated existing Definition versus Reference Organization counts, Best-practice reason:, and brief override option. Keep lookup times, proposed additions, projected counts, percentages, threshold, formulas, environment, and scope internal; do not explain each rule in the default response |
| Oracle returns a validation, authorization, transport, or process error | Preserve the redacted response and external identifier when available; stop before retry or a different execution route |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Required fields, lengths, or conditional information are missing or invalid | Correct the request and revalidate |
| Lookup | The required source or duplicate lookup is unavailable, ambiguous, or has no required match | Supply an unambiguous value or restore lookup access |
| Required design check unavailable | Definition/reference count data, completed duplicate-check evidence, or requested organization types are unavailable | Stop creation and resolve the missing value before rechecking |
| Design enforcement | The estimated projected reference-organization percentage is 80% or below | Show the blocked outcome, compact estimated Definition versus Reference Organization counts, unchanged best-practice reason, and brief override option defined in ora_design_enforcement.md. Retain the calculation internally and continue only after a passing check or scoped explicit waiver |
| Approval blocker | A mutation, copy, or parameter update lacks the required immediate approval | Present the exact target, operation, and immutable payload or artifact for approval |
| Fusion API or transport | Oracle rejects the operation or the environment is unavailable | Preserve diagnostics and stop before retry |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before any mutating operation | Exact target environment, operation, and immutable request payload or import artifact, followed by explicit approval |
| On a lookup failure | Resolver name, supplied identifiers, no-match or ambiguity result, and corrective action without secrets |
| On a definition/reference mix error | Follow Customer Messages in ora_design_enforcement.md: outcome, estimated Definition versus Reference Organization counts, Best-practice reason:, and brief next action. Omit percentages, the 80% rule, timestamps, projected-count breakdowns, and rule-by-rule explanations unless the user explicitly requests further detail |
| On an Oracle failure | Environment, operation, external ID when available, redacted message, and next safe action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| A required source or duplicate lookup is ambiguous or unavailable | Do not select a result, fuzzy-match, or proceed with create, copy, update, or parameter maintenance |
| The required definition/reference mix check fails or cannot be completed | Do not proceed until the check passes or the user explicitly waives the evaluated failure under core.data-loader.task-hook. Retain the failed result as overridden; the waiver does not clear remaining validation or load approval |
| Required validation input is missing | Do not bypass the missing input using a browser, direct REST write, loader, or another integration |
| A mutating operation lacks immediate explicit approval | Do not submit it or retry it |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INVORG.HANDLE_ERROR | terminal | 70 | terminal | none | none | stop | Invalid input, required lookup failure, unavailable definition/reference check, or blocked projected mix |
| INVORG.READY_NOT_REQUIRED | terminal | 80 | terminal | none | INVORG.COUNT_DEFINITION | stop | The request is not an inventory-organization create, so the definition/reference design check does not apply |
| INVORG.READY | terminal | 90 | terminal | none | INVORG.ENFORCE_DEFINITION_REFERENCE_MIX | stop | The internal organization-mix check passes; the request may continue to its separately approved execution workflow |
