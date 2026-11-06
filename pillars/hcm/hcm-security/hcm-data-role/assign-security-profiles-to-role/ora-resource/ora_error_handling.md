# Assign Security Profiles to Role Error Handling

Source: HCMDS Assign Security Profiles to Role Skill, version 5.

## Error Situations

| Situation | What Should Happen |
|---|---|
| A data role create or update does not resolve to an active job role | Stop before preview. Display only: Unable to create the data role because the selected base role isn't an active job role. Please provide an active job role as the base role. |
| Security profiles are requested for a Line Manager or Employee abstract role, or for a customer-defined existing role | Treat this as an acceptable direct security-profile assignment. Resolve the active existing role and its mappings; do not create or propose a data role solely for this assignment. |
| A new data role has neither a supplied Role Name nor a meaningful security-scope descriptor for deriving its name | Stop before preview. Ask the user to provide a meaningful scope descriptor. Do not prompt for a data-role Role Code or use one when supplied. Do not generate a generic identity. |
| A derived Role Name or internally derived Role Code already exists, or the display name is 100 characters or more | Stop before preview. Ask the user for an alternate Role Name or scope descriptor. Do not prompt for a data-role Role Code or append numeric or timestamp suffixes. |
| The inherited job role's hcmDataRoles result cannot be retrieved or its associated security-profile names cannot be determined for a new data-role create | Stop before preview; preserve sanitized diagnostics and resolve the inherited job-role access lookup. Do not infer that no security profiles are assigned. |
| The inherited job role has associated security profiles | Before preview, show the associated security-profile names and explain that a data role created from this job role automatically inherits the configured access. Recommend revoking those security profiles from the job role. |
| The user has not explicitly acknowledged the inherited job-role access | Stop before preview and data-role creation. Retain the listed security-profile names and inherited-access disclosure, then request explicit acknowledgment. |
| The mapping action cannot resolve valid security-profile mappings | Stop before retry; preserve sanitized diagnostics and correct the role ID or selected security-profile types as applicable. |
| A proposed security-profile type is not returned by the mapping action | Stop before preview; remove the unsupported type. |
| A security-profile accessor returns no exact match or more than one match | Stop before import; ask the user to provide the correct security-profile value. Do not infer an identifier or code. |
| A Data Roles FSM package has missing, ambiguous, or inconsistent member, header, field-mapping, linkage, or metadata evidence; differs from the resolved CSV layout; or changes ASM_SETUP_CSV_METADATA.xml | Stop before preview or import. Obtain a current template-only export, resolve the member layout, headers, field mappings, and linkage from it, rebuild the package from the result, and retain ASM_SETUP_CSV_METADATA.xml byte-for-byte unchanged. A missing ViewInstanceName or GroupingKey declaration uses the documented fallback rather than stopping package preparation. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Blocked | Required job role, role target, valid mapping, allowed security-profile type, exact profile match, acknowledgment, or FSM CSV package contract is unavailable | Correct the role target, selected profile types, or package contract, then restart validation |
| Blocked | A data-role identity has neither a supplied Role Name nor a scope descriptor for deriving it, exceeds the display-name limit, or collides with an existing role | Supply an alternate Role Name or a different scope descriptor, then restart identity validation; do not request a data-role Role Code |
| Ready | The correct role target was used, inherited access was acknowledged when required, every proposed security-profile type is returned, and each profile resolves exactly | Continue to the separately authorized preview and execution workflow |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Data-role basis rejected | Display only the applicable prescribed polite rejection message and request an active job role. Do not disclose resolved field values, role classifications, role names or codes, identifiers, endpoints, API calls, mapping checks, or validation steps. |
| Any other user-facing response | Show only business-visible role names, selected security-profile names, outcome status, and a safe next action. Do not display internal identifiers, including role, data-role, security-profile, process, request, or API identifiers. |
| Mapping failure | Failure class, selected role context expressed by business name, sanitized diagnostic, and safe next action; do not disclose internal identifiers. |
| Inherited job-role access | Associated security-profile names, confirmation that the new data role automatically inherits this access, the recommendation to revoke the security profiles from the job role before data-role creation, and the required explicit acknowledgment. Do not disclose internal identifiers. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASPR.ACKNOWLEDGE_INHERITED_JOB_ROLE_ACCESS | decision | 5 | execution_gate | acknowledged->ASPR.RESOLVE_SECURITY_PROFILES;not_acknowledged->ASPR.ERROR | ASPR.LOOKUP_INHERITED_JOB_ROLE_ACCESS | stop | The inherited job-role access lookup returned one or more associated security profiles |
| ASPR.ERROR | terminal | 10 | terminal | none | none | stop | A validation, lookup, dependency, or design-enforcement rule is blocked |
| ASPR.READY | terminal | 11 | terminal | none | ASPR.ENFORCE_MAPPINGS | stop | The role target, selected security-profile types, and FSM CSV package layout comply with the documented rules |
