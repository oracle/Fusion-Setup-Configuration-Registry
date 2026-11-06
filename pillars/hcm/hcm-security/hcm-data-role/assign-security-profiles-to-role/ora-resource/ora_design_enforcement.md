# Assign Security Profiles to Role Design Enforcement

Source: HCMDS Assign Security Profiles to Role Skill, version 5.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Restrict the data-role basis | Use an inherited role only when active-job-role rolesLOV search returns exactly one RoleId for its exact Role Name or Role Code |
| 2 | Disclose and acknowledge inherited job-role access | Before creating a new data role, disclose direct job-role security profiles, recommend revoking them because the data role inherits that access, and obtain explicit acknowledgment before continuing |
| 3 | Resolve mappings | Invoke the mapping action for the inherited job role or the active existing target role itself, as applicable. Direct assignment to Line Manager or Employee abstract roles and customer-defined roles is acceptable; do not create a data role for that purpose. |
| 4 | Default unresolved selections | Assign the matching validated View All profile through the applicable security-profile accessor to every returned type without an explicit profile selection |
| 5 | Restrict profile types | Associate only security-profile types returned by the mapping action |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Creating or updating a data role | Blocker | resolve_active_inherited_job_role | The inherited role does not resolve to exactly one active job role | Stop. Tell the user that a data role requires an active job role as its basis, then request an active job role or Role Code | Yes |
| Creating a new data role | Blocker | derive_available_data_role_name_and_code | Neither a Role Name nor a meaningful scope descriptor for deriving it is available, the display name is 100 characters or more, or the Role Name or internally derived Role Code already exists | Stop. Request an alternate Role Name or a scope descriptor; derive the data-role Role Code only from the final Role Name as `role_name.upper().replace(" ", "_") + "_DATA"` and ignore it when supplied. Do not append a numeric or timestamp suffix | Yes |
| Creating or updating a data role | Blocker | get_security_profile_mappings_for_role | The mapping action was not invoked for the inherited job role | Invoke the mapping action for the inherited job role before associating profiles | Yes |
| Creating a new data role from an inherited job role with directly assigned security profiles | Acknowledgment gate | get_inherited_job_role_security_profiles | Associated security-profile names have not been shown and explicitly acknowledged by the user | Show every associated security-profile name. Explain that the new data role automatically inherits the job role's existing access and recommend revoking those job-role assignments before creating the data role. Require explicit acknowledgment before continuing. | Yes |
| Directly assigning a security profile to an existing role, including Line Manager or Employee abstract roles and customer-defined roles | Blocker | get_security_profile_mappings_for_role | The mapping action was not invoked for the role itself | Invoke the mapping action for the role itself before associating profiles. Do not create a data role merely to assign its security profiles. | Yes |
| Associating a security-profile type with a role | Blocker | get_security_profile_mappings_for_role | The proposed security-profile type is not returned by the mapping action | Remove the unsupported type and select only a returned mapping | Yes |
| A returned security-profile type has no explicit selection | Blocker | get_security_profile_mappings_for_role | No exact matching View All security profile is available through its documented accessor | Resolve exactly one matching View All profile or obtain an explicit user selection | Yes |
| A Data Roles FSM package is prepared | Blocker | resolve_data_role_csv_context | The current target-environment template cannot establish an unambiguous member layout, header order, parent/child mapping, or linkage; the generated package differs from that result; or ASM_SETUP_CSV_METADATA.xml is changed | Re-export the current task template, rebuild all generated rows from the resolved layout context, validate the exact ZIP, and obtain fresh approval if it changes. Missing template ViewInstanceName or GroupingKey evidence uses the documented fallback. | Yes |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_active_inherited_job_role | Before creating or updating a data role | Exact active inherited job RoleId | ora_reference_lookups.md |
| derive_available_data_role_name_and_code | Before preview when a new data role is created | Role Name, internally derived Role Code, and availability evidence | ora_reference_lookups.md |
| get_security_profile_mappings_for_role | Before associating security-profile types | Allowed security-profile types for the applicable role target | ora_reference_lookups.md |
| get_inherited_job_role_security_profiles | Before creating a new data role | Associated security-profile names directly configured on the inherited job role | ora_reference_lookups.md |
| resolve_data_role_csv_context | Before a CSV package is generated or imported | Current template members, headers, parent-child linkage, migration views, grouping-key rule, and metadata contract | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASPR.ENFORCE_MAPPINGS | decision | 9 | design_enforcement | compliant->ASPR.READY;blocked->ASPR.ERROR | ASPR.READINESS | stop | A role, proposed security-profile types, and FSM CSV package layout are ready for preview |
