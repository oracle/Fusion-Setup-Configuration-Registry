# Content Type Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Define the content type | Supply its identity, department, and required localized values. |
| 2 | Define the schema | Retain the required title field and define additional attributes as needed. |
| 3 | Review advanced settings | Enable unrestricted JavaScript and HTML only when the business accepts the stated security risk. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Defining schema attributes | Error | | The title field is absent or not required | Define the title field as required. | Yes |
| Restricting attribute visibility | Error | resolve_department_user_groups | Department user groups have not been resolved | Resolve the department's user groups before applying visibility. | Yes |
| Enabling unrestricted JavaScript and HTML | Warning | | Business acceptance of the security risk is absent | Leave the setting disabled unless the business explicitly accepts the risk. | Yes |
| Creating or updating a content type | Error | | The selected department is not represented in the FSM package by a caller-supplied stripeCd of ORA_SVC_CRM, ORA_SVC_HRHD, or ORA_SVC_ISR | Use only the caller-supplied department-to-stripeCd mapping; do not infer or substitute another code. | Yes |
| Creating or changing counterPrefix on a content type | Error | | Customer-provided counterPrefix is absent | Ask the customer to provide the required counter prefix; do not generate or infer it. | No |
| Creating localized content-type or schema-attribute rows | Error | resolve_active_knowledge_locales | A localized row lacks the exact active locale code or is orphaned from its parent | Link the row to the exact parent referenceKey or xpath and use the active locale code, such as en_US. | Yes |
| Creating a schema attribute | Error | | The parent referenceKey, generated xpath, or approved unique referenceKey is absent | Link to the exact root content-type referenceKey and generate xpath from the attribute referenceKey and parent key. | Yes |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_department_user_groups | Restricting attribute visibility | Available user groups for the selected department | ora_reference_lookups.md |
| resolve_active_knowledge_locales | Creating localized content-type or schema-attribute rows | Exact active locale codes | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CONTENT_TYPES_REDWOOD.DESIGN | step | 12 | design_enforcement | passed->CONTENT_TYPES_REDWOOD.BASELINE_CONTRACT;blocked->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.DEFAULTS | stop | Evaluate every applicable Design Rule with prior evidence: required title, supplied stripe mapping/counter prefix, exact active-locale coverage, parent/xpath linkage and resolved restricted-visibility groups. Require business acceptance before allowing unsafe HTML/JavaScript; unresolved or conflicting evidence blocks. |
