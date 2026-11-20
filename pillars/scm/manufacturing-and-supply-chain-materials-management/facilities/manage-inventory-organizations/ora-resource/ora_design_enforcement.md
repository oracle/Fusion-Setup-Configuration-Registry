# Manage Inventory Organizations Design Enforcement

Apply this gate to every request that creates inventory organizations, including copy-to-new and bulk creation. Preserve the existing task-local Rule IDs and lookup-backed evaluation route.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Receive lookup results | Require valid estimated counts from the count resolvers and completed duplicate-check evidence from find_inventory_organization_exact. Reuse the evidence produced by INVORG.RESOLVE_EXISTING; do not query submitted codes again. Use one target environment and identical scope for both counts: global or one MasterOrganizationId. For a scoped bulk request spanning multiple masters, evaluate each master separately and require every scope to pass. Do not mix scopes or environments. |
| 2 | Count proposed new organizations | Require completed duplicate checks for every proposed organization code and name. Any existing match blocks creation at INVORG.RESOLVE_EXISTING. After that gate passes, count each distinct proposed new code once in the design calculation; do not alter or consolidate submitted load rows. |
| 3 | Calculate projected counts | Set NewDefinitionCount to unique new codes with ORA_RCS_IGB_DFTN and NewReferenceCount to unique new codes with ORA_RCS_IGB_RFRC. D = ExistingDefinitionCount + NewDefinitionCount; R = ExistingReferenceCount + NewReferenceCount; T = D + R. Require T > 0. |
| 4 | Calculate and enforce the mix | Estimated reference percentage = 100 * R / T. Pass only when 5 * R > 4 * T; otherwise block. This unrounded integer comparison implements greater than 80%. Exactly 80% blocks. Retain the calculation and policy condition internally. Present the outcome, estimated Definition versus Reference Organization counts, and best-practice reason using the Customer Messages contract; do not explain the percentage or threshold in the customer response. Missing evidence follows unavailable to INVORG.HANDLE_ERROR. |
| 5 | Record validation evidence | Retain sanitized environment and scope references, lookup evidence and timestamps, reused checked-code, matched-code, and duplicate-check completion evidence, unique new counts, D, R, T, estimated percentage, and node outcome. Do not persist protected runtime identifiers or payloads. Missing evidence is a blocker, never zero. |
| 6 | Gate preview and revalidation | Include this resource in ordered ruleResults. A create cannot mark the check not_applicable. Blocked or unavailable results stop preview and creation. Recalculate using the final preview rows when the environment, scope, rows, grouping codes, or matches change. A workflow that omits task rules cannot bypass this gate. Disclose the supported explicit user-waiver option whenever this evaluated design gate blocks. Apply a waiver only when the user explicitly requests it, retaining the failed calculation and waiver reason under the core policy. A waiver remains scoped to the evaluated finding and request; execution approval alone is not a waiver, and a changed request requires fresh validation and approval. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| One or more inventory organizations are proposed for creation | Required input | count_definition_inventory_organizations | The estimated existing definition count is unavailable. | Resolve the definition count before creation. Use it as the base for D. | Yes |
| One or more inventory organizations are proposed for creation | Required input | count_reference_inventory_organizations | The estimated existing reference count is unavailable. | Resolve the reference count before creation. Use it as the base for R. | Yes |
| One or more inventory organizations are proposed for creation and the required counts, completed duplicate-check evidence, and requested organization types are available | Error | find_inventory_organization_exact | The estimated projected reference percentage is 80% or below. | Reuse the completed duplicate-check evidence and count each unique new organization once. Retain the calculation internally; show the blocked outcome, estimated Definition versus Reference Organization counts, static best-practice reason, and brief override option using Customer Messages. Creation may continue only after this gate passes or its evaluated failure is explicitly waived under the core policy; other validation and load approval remain required. | Yes |
| A count, completed duplicate-check result, requested organization type, consistent environment/scope, or positive projected total is unavailable | Error |  | The definition-versus-reference mix check cannot be completed. | Stop creation, state which required value is unavailable, and rerun the check when it is available. | Yes |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| count_definition_inventory_organizations | Before evaluating the projected mix for a creation request | ExistingDefinitionCount | ora_reference_lookups.md |
| count_reference_inventory_organizations | Before evaluating the projected mix for a creation request | ExistingReferenceCount | ora_reference_lookups.md |
| find_inventory_organization_exact | Reuse the completed duplicate check before adding unique new organizations to projected counts; do not run a second lookup | CheckedOrganizationCodes; ExistingSubmittedOrganizationCodes; DuplicateCheckComplete | ora_reference_lookups.md |

## Customer Messages

| Situation | What Happens |
|---|---|
| Evaluated organization-mix gate is blocked and has not been waived | Show: Creation is blocked by the organization design policy. Then show the estimated Definition versus Reference Organization counts, followed by Best-practice reason: and the reason below. End with the brief override option. |
| Best-practice reason accompanying an evaluated organization-mix failure | Show: Use Definition Organizations to differentiate one or a group of organizations where separate item attribute values are required. Use Reference Organizations for child organization grouping where item attributes can be inherited from a parent Definition Organization. |
| Override option following an unwaived blocked-design message | Show: You can explicitly override this check for this request; the finding will remain on record, and validation and data-load approval will still be required. |
| Evaluated organization-mix gate passed | Show: The organization design check passed. We can continue with the remaining validation before preparing the setup for your approval. |
| User explicitly waived the evaluated organization-mix failure | Show: Your override of the organization design check has been recorded. The finding remains on record. We will continue with the remaining validation; data-load approval is still required before submission. |
| Required design information is unavailable | Show: We cannot complete the organization design review because <missing-information> is unavailable. Once it is available, we can evaluate the design. |

Show the message matching the evaluated design result, copying the Show: text word for word and omitting Show:. Replace missing-information with the specific missing value. Keep the customer response focused on the outcome: one compact comparison of the estimated existing Definition and Reference Organization counts, then the best-practice reason and a brief next action. This contract applies to any single, copy-to-new, or bulk create request; use the actual completed lookup results and never hardcode names, codes, counts, or results from an earlier request.

| Response Part | Required Content |
|---|---|
| Outcome | Lead with the applicable creation outcome. Do not describe this repository check as an Oracle API rejection or claim that Fusion rejected an unsubmitted request. |
| Organization counts | Show one compact table with Organization Type and Existing Count (estimated) columns, and two rows: Definition Organizations and Reference Organizations. Use the completed live lookup counts. Do not add proposed-addition, projected-count, or total rows to the default customer response. |
| Best-practice reason | Immediately after the counts, show Best-practice reason: followed by the unchanged reason above. |
| Internal evidence | Retain lookup times, environment, scope, duplicate-check evidence, proposed additions, projected counts, percentage, threshold, exact comparison, and node outcome internally. Do not show timestamps, formulas, percentages, the 80% rule, or a rule-by-rule explanation in the default customer response. Supply further detail only when the user explicitly asks for it. |
| Next action | End with the unchanged brief override-option message when blocked, or the applicable continuation message when passed or waived. Do not prescribe a different grouping type or change the supplied setup. |
| Multiple evaluated groups | For requests evaluated separately by master organization, show the compact counts and outcome per group using a business-friendly label or ordinal. Do not combine counts across groups or obscure a failed group with an aggregate pass. |
| Missing evidence | If any required value is unavailable, use the missing-information message and identify the missing value. Never invent counts, substitute zero, or show unresolved placeholders. |

An override requires an explicit request-scoped user waiver; it does not make the check pass or replace remaining validation and data-load approval. Retain the failed calculation, evidence, and waiver reason under core.data-loader.task-hook. Keep the customer response limited to the outcome, estimated Definition versus Reference Organization counts, best-practice reason, and brief next action. When waived, acknowledge the retained finding without repeating the internal calculation or threshold.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INVORG.ENFORCE_DEFINITION_REFERENCE_MIX | decision | 60 | design_enforcement | blocked->INVORG.HANDLE_ERROR;passed->INVORG.READY;unavailable->INVORG.HANDLE_ERROR | INVORG.COUNT_REFERENCE | stop | Enforce the projected definition/reference mix for proposed inventory-organization creates using the completed lookups |
