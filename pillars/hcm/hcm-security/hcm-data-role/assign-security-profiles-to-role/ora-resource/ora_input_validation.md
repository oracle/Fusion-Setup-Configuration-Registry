# Assign Security Profiles to Role Input Validation

Source: HCMDS Assign Security Profiles to Role Skill, version 5.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Data-role job role | Inherited active job role identified by exact Role Name; Role Code is required when duplicate names are returned | Stop | Supply an active job role; a data role cannot be created from another role type or an inactive role | Creating or updating a data role | resolve_active_inherited_job_role |
| Data-role identity | User-supplied Role Name, or a derived Role Name from the inherited job role plus at least one security-scope descriptor; internally derived Role Code | Stop | Supply a Role Name or a meaningful security-scope descriptor. Do not prompt for a data-role Role Code; ignore it when supplied and derive it internally | Creating a new data role | derive_available_data_role_name_and_code |
| Direct role assignment target | Existing active role | Stop | Supply the active existing role receiving the direct security-profile assignment. Line Manager or Employee abstract roles and customer-defined roles are valid direct-assignment targets; do not create a data role merely to assign their security profiles. | Assigning a security profile directly to an existing role that is not created as a data role | resolve_active_direct_assignment_role |
| Security-profile mapping request | Target role selected by the applicable request type | Stop | Select the inherited job role for a data role, or the role itself for a direct existing-role assignment, before resolving valid mappings | Creating, updating, or directly assigning security profiles | get_security_profile_mappings_for_role |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| A data role is being created or updated without an active inherited job role | Blocked | Stop; provide an inherited role with JobRole=true and ActiveFlag=true. Do not use an abstract role, data role, or inactive role as the data-role basis | resolve_active_inherited_job_role |
| A new data role has neither a supplied Role Name nor a meaningful security-scope descriptor for deriving its name | Blocked | Stop; request a meaningful scope descriptor. Do not prompt for a data-role Role Code or use a supplied one. Do not generate a generic, numeric, or timestamp-suffixed identity | derive_available_data_role_name_and_code |
| A direct security-profile assignment is requested for an existing role, including a Line Manager or Employee abstract role or a customer-defined role | Lookup required | Resolve the active role and then resolve mappings using the role itself. Do not route this request to data-role creation. | resolve_active_direct_assignment_role |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Data-role basis | Accept only an inherited role whose JobRole=true and ActiveFlag=true; use AbstractRole and DataRole only as resolved classification evidence, never as an acceptable basis | Creating or updating a data role | resolve_active_inherited_job_role |
| Derived data-role identity | Resolve the final display name first, retaining a supplied Role Name or deriving it from inherited job role plus scope when absent. Derive the technical Role Code only as `role_name.upper().replace(" ", "_") + "_DATA"`; replace every literal space as is without trimming, collapsing spaces, or removing punctuation; ignore any supplied data-role Role Code. The display name must be shorter than 100 characters and the derived display name and technical role code must both be available | Creating a new data role | derive_available_data_role_name_and_code |
| Direct assignment target | Accept an existing role whose ActiveFlag=true, including a Line Manager or Employee abstract role or a customer-defined role | Assigning directly to an existing role that is not created as a data role | resolve_active_direct_assignment_role |
| Mapping lookup target | Use the inherited job role for a data role; use the existing role itself for a direct assignment | Resolving valid security-profile mappings | get_security_profile_mappings_for_role |
| Existing data-role update rows | Require the resolved role code for parent DataRoleName and DataRoleIdResolverName and every child parent-link/DataRoleName; require inherited role code, baseline Y/N delegation value, DataRoleProfileMigration, baseline grouping pattern, nonblank baseline StartDate, and baseline identifier state | Updating an existing data role | resolve_existing_data_role_csv_baseline |

## Environment-Derived FSM CSV Layout

The current target-environment template-only export is the schema authority.
Resolve the package layout through resolve_data_role_csv_context before
generating any row. For the two supported members, use the template-declared
ViewInstanceName and GroupingKey pattern when available; otherwise apply the
documented fallback values below so package preparation can continue.

| Package Element | Validation and Row Mapping |
|---|---|
| PER_HCM_DATA_ROLE.csv | Use the resolver-identified header sequence and field mapping. Use the template-declared ViewInstanceName and GroupingKey pattern when present; otherwise set ViewInstanceName to DataRoleMigration and set GroupingKey to the resolved data-role name. Emit the parent row only through the resolved field mapping for the requested operation. |
| ORA_PER_HCM_DATA_ROLE_PROFILE.csv | Use the resolver-identified header sequence and field mapping. Use the template-declared ViewInstanceName and GroupingKey pattern when present; otherwise set ViewInstanceName to DataRoleProfileMigration and set GroupingKey to the resolved data-role name, a comma, and the resolved HR Securing Object value in that order. Emit one child row for each type returned by getSecurityProfileMappingsForRole, using the resolved parent link and field mappings. |
| Metadata member | Retain ASM_SETUP_CSV_METADATA.xml exactly once and byte-for-byte unchanged from the current template package. |

Every generated row must have the resolved member's exact header count and
order. Stop before preview or import when the template cannot determine a
unique parent/child layout, field mapping, or parent-child linkage; when a
generated member or header differs from the resolver result; when the metadata
bytes change; or when a profile type is not returned by the live mapping
action. Missing template declarations for ViewInstanceName or GroupingKey use
the member-specific fallback above, not a readiness blocker.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASPR.VALIDATE | decision | 1 | validate_input | valid->ASPR.APPLY_DEFAULTS;invalid->ASPR.ERROR | none | stop | A data role is created or updated, or security profiles are assigned directly to an existing role |
