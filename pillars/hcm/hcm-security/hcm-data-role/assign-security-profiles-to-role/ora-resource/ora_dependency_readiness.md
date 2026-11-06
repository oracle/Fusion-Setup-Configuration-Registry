# Assign Security Profiles to Role Dependency Readiness

Source: HCMDS Assign Security Profiles to Role Skill, version 5.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Role selection | Identify the inherited job role for a data-role create or update through active-job-role rolesLOV search with exact Role Name and Role Code disambiguation; for a direct assignment, use the active existing target role itself, including Line Manager or Employee abstract roles and customer-defined roles |
| 2 | Data-role identity | Retain a user-supplied Role Name or derive it when absent. Derive the data-role Role Code only from the final Role Name as `role_name.upper().replace(" ", "_") + "_DATA"`, ignore any supplied data-role Role Code, and verify that both values are available |
| 3 | Inherited job-role access | Before creating a new data role, query hcmDataRoles with the inherited job RoleId and disclose any directly assigned security profiles |
| 4 | Inherited-access acknowledgment | When security profiles are returned, obtain the user's explicit acknowledgment of the inherited access before continuing |
| 5 | Mapping lookup | Invoke the documented mapping action for the inherited job role or direct existing-role target |
| 6 | Profile resolution | Resolve explicit selections and View All defaults against the applicable documented security-profile accessor |
| 7 | Mapping enforcement | Associate only security-profile types returned by the mapping action |
| 8 | FSM package schema | Resolve the CSV context from the current target-environment template-only export, including member names, header arrays, parent/child field mappings, and linkage. Use its ViewInstanceName and GroupingKey pattern when declared; otherwise use the documented member-specific fallback. Retain ASM_SETUP_CSV_METADATA.xml byte-for-byte unchanged |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| data_role_inherited_job_role | Active inherited job role | Yes | Creating or updating a data role | Verify | Exact active-job-role rolesLOV result | resolve_active_inherited_job_role | The resolved role must have JobRole=true and ActiveFlag=true; AbstractRole and DataRole records are not eligible | Supply an active job role before preview | Eligible inherited job role and RoleId |
| data_role_identity | User-supplied or safely derived Role Name and internally derived Role Code | Yes | Creating a new data role | Verify | Final Role Name (supplied, or derived from inherited job role plus at least one scope descriptor only when absent); rolesLOV availability result | derive_available_data_role_name_and_code | A new role requires a distinguishable business identity and technical code; the technical code is always derived internally and values must be unique without automatic suffixes | Supply a Role Name or meaningful scope descriptor; ignore any supplied data-role Role Code and provide an alternate Role Name or scope descriptor if either derived value already exists | Role Name, internally derived Role Code, and availability evidence |
| direct_assignment_role | Active existing role | Yes | Directly assigning a security profile to an existing role, including Line Manager or Employee abstract roles and customer-defined roles | Verify | Exact rolesLOV result | resolve_active_direct_assignment_role | Direct assignments retain the existing active-role safeguard. Do not create a data role merely to assign security profiles to an existing role. | Supply an active existing role before preview | Eligible existing role and RoleId |
| inherited_job_role_security_profile_access | Direct security-profile access on inherited job role | Yes | Creating a new data role | Lookup | hcmDataRoles result for the eligible inherited job RoleId | get_inherited_job_role_security_profiles | A new data role automatically inherits security-profile access already directly configured on its inherited job role | Show all associated security-profile names, explain the inherited access, recommend revoking those job-role assignments, and obtain explicit acknowledgment | Associated security-profile names and disclosure outcome |
| inherited_job_role_security_profile_acknowledgment | Explicit acknowledgment of inherited job-role access | Conditional | The inherited job-role access lookup returns one or more associated security profiles | Verify | User acknowledgment after the associated security-profile names and inherited-access effect are shown |  | Data-role creation must not continue until the user explicitly acknowledges the inherited access | Ask the user to explicitly acknowledge the listed security profiles and that the new data role inherits their configured access | Acknowledgment record bound to the displayed profile names and inherited-access disclosure |
| security_profile_role_mappings | Valid security-profile mappings and resolved profile names | Yes | Creating, updating, or directly assigning security profiles | Lookup | Mapping action response and documented security-profile accessors | get_security_profile_mappings_for_role | Only returned security-profile types can be associated; all unrequested returned types default to a validated View All profile | Resolve the applicable RoleId and mappings before selecting profiles; stop when a View All default is missing or ambiguous | Allowed types, selected profile names, and mapped profile identifiers or codes |
| data_role_fsm_csv_layout | Current supported FSM CSV package layout | Yes | Generating or importing a data-role package | Verify | Current target-environment template-only export | resolve_data_role_csv_context | The package contract is environment-specific. Derive the layout and any declared migration values from the current template; when migration values are absent, apply the documented parent and child fallbacks. ASM_SETUP_CSV_METADATA.xml must remain unchanged | Export the current template and use its resolved members, headers, metadata order, parent/child field mappings, and linkage. Use template-derived ViewInstanceName and GroupingKey values, or the resolver fallback when they are absent | Immutable layout context, template/fallback value source, and metadata evidence |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Blocked | The required role cannot be resolved, inherited access cannot be determined or acknowledged, the mapping action is unavailable, a proposed type is not returned, or a profile accessor has no exact match | No |
| Ready | The role target and data-role identity were resolved, inherited access was disclosed and explicitly acknowledged when required, every selected type is returned by the mapping action, every unrequested returned type has one validated View All default, and the current FSM package layout is validated | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASPR.READINESS | decision | 8 | resolve_dependency | ready->ASPR.ENFORCE_MAPPINGS;blocked->ASPR.ERROR | ASPR.RESOLVE_CSV_LAYOUT | stop | A role target, inherited job-role access, security-profile mappings, and FSM CSV package layout have been evaluated |
