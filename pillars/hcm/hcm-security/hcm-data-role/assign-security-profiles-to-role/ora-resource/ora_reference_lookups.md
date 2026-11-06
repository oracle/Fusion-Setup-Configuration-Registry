# Assign Security Profiles to Role Reference Lookups

Source: HCMDS Assign Security Profiles to Role Skill, version 5.

Execute every documented Fusion REST call in this file through
`core.fusion-api.rest-api-client`; do not issue a direct REST request. The
`get_security_profile_mappings_for_role` POST is an explicitly named
configuration-retrieval lookup; it is distinct from any role or
security-profile create, update, or import operation.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_delegation_allowed_yes_no | Delegation Allowed is supplied or defaulted for a new data-role row | Delegation Allowed and lookup code YES_NO from manage-common-lookups | Resolve the supplied or defaulted value through the named common lookup | Validated Delegation Allowed value | Stop before import and ask the user to provide a valid value |
| derive_available_data_role_name_and_code | A new data role is created | Final data-role Role Name; inherited job-role business name or code and at least one security-scope descriptor only when Role Name is absent | Build the display name from the base role and scope only when Role Name is absent; keep it below 100 characters. After resolving the final Role Name, derive the technical Role Code only as `role_name.upper().replace(" ", "_") + "_DATA"`. Replace every literal space as is; do not trim, collapse spaces, remove punctuation, or use the inherited job role as the code source. Ignore every user-supplied data-role Role Code. | Derived Role Name and internally derived Role Code | No Role Name and no scope descriptor, overlength display name, or an invalid derived code: stop and request a meaningful scope descriptor or alternate Role Name; do not request a data-role Role Code |
| resolve_data_role_csv_context | A Data Roles FSM CSV package is prepared | Current target-environment template-only export produced by the task-level template-export workflow | Read the package and metadata to identify the CSV members, exact header arrays and order, parent and child field mappings, parent-child linkage, and any declared ViewInstanceName or GroupingKey pattern. When the template does not declare either value, apply the member-specific fallback: PER_HCM_DATA_ROLE.csv uses DataRoleMigration and the resolved data-role name; ORA_PER_HCM_DATA_ROLE_PROFILE.csv uses DataRoleProfileMigration and DataRoleName,HrSecuringObject with resolved values substituted. Copy ASM_SETUP_CSV_METADATA.xml without changing any byte. | Immutable layout context: parent and child member names; exact header arrays; parent and child field mappings; parent-child link; template-derived or fallback ViewInstanceName and GroupingKey values; metadata member bytes and node order | Missing, ambiguous, or inconsistent member, header, field-mapping, linkage, or metadata evidence: stop before preview or import and obtain a fresh template package from the target environment. A missing ViewInstanceName or GroupingKey declaration alone uses the documented fallback. |
| resolve_existing_data_role_csv_baseline | Updating an existing data role | Current populated exact-role CSV export or user-supplied package explicitly identified as extracted from the target environment | Require one parent row and child rows for the resolved role; use baseline values for all unchanged fields | Parent values, child start dates, migration names, grouping pattern, and identifier blank/populated state | Stop before preview when the baseline is missing, ambiguous, or inconsistent. |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_active_inherited_job_role | Creating or updating a data role | Exact RoleName and, when needed to disambiguate, RoleCode of the inherited role | GET /hcmRestApi/resources/{version}/rolesLOV?q=JobRole='Y'&ActiveFlag=true with RoleName and RoleCode matching at runtime | RoleId, RoleName, RoleCode, JobRole, ActiveFlag | Require exactly one active job role. Match RoleName exactly; when duplicate names exist require RoleCode | Eligible inherited RoleId and role evidence | No exact role or multiple matches: stop and request the correct Role Name or Role Code |
| check_derived_data_role_identity_availability | A new data role has its internal Role Code derived or its Role Name derived | Derived Role Name and internally derived Role Code | GET /hcmRestApi/resources/{version}/rolesLOV with exact RoleName lookup, then exact RoleCode lookup | RoleName, RoleCode, ActiveFlag | Continue only when both exact lookups return zero roles; do not append numeric or timestamp suffixes | Availability evidence for the derived Role Name and internally derived Role Code | Any match: stop and request an alternate Role Name or scope descriptor; do not request a data-role Role Code |
| resolve_active_direct_assignment_role | Directly assigning a security profile to an existing role, including Line Manager or Employee abstract roles and customer-defined roles | Exact RoleName and, when needed to disambiguate, RoleCode | GET /hcmRestApi/resources/{version}/rolesLOV with RoleName and RoleCode matching at runtime | RoleId, RoleName, RoleCode, ActiveFlag, JobRole, AbstractRole, DataRole | Require exactly one active role. Match RoleName exactly; when duplicate names exist require RoleCode. AbstractRole is accepted for a direct assignment; role classifications must not cause data-role creation. | Eligible direct-assignment RoleId and role evidence | No exact active role or multiple matches: stop and request the correct Role Name or Role Code |
| get_security_profile_mappings_for_role | Creating or updating a data role, or directly assigning a security profile to an existing role | Eligible RoleId from the applicable role resolver | POST https://{hostname}/hcmRestApi/resources/{version}/hcmDataRoles/action/getSecurityProfileMappingsForRole with JSON body {"roleId":"<idvalue>"} and Content-Type application/vnd.oracle.adf.action+json | Returned security-profile types | Invoke for the inherited job role for data-role create/update, or the role itself for a direct assignment. Accept only returned types | Allowed security-profile types | No returned mapping: stop and correct the role target or selected security-profile types |
| get_inherited_job_role_security_profiles | Creating a new data role after the inherited job role has passed eligibility | Inherited job RoleId as JobRoleId | GET /hcmRestApi/resources/{version}/hcmDataRoles?q=RoleId={JobRoleId}&expand=securityProfiles | Parent data-role result and securityProfiles child records with business-visible security-profile names | Treat a zero-result collection or a parent with no securityProfiles child records as no inherited profile access. Collect distinct business-visible child names from every returned parent | Distinct associated security-profile names and whether direct access is configured | Stop before preview when the query, expansion, or child profile names cannot be determined. Do not expose internal identifiers |
| resolve_country_security_profile | A returned COUNTRY mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/countrySecurityProfilesLOV | CountrySecurityProfileId, Name | Require exactly one Name match | CountrySecurityProfileId | Stop before import and request the correct value |
| resolve_person_security_profile | A returned PERSON mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/personSecurityProfilesLOV | PersonSecurityProfileId, Name | Require exactly one Name match | PersonSecurityProfileId | Stop before import and request the correct value |
| resolve_public_person_security_profile | A returned PUBLIC_PERSON mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/personSecurityProfilesLOV | PersonSecurityProfileId, Name | Require exactly one Name match | PersonSecurityProfileId | Stop before import and request the correct value |
| resolve_document_type_security_profile | A returned document-type mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/hrDocumentTypeSecurityProfilesLOV | DocumentTypeSecurityProfileId, Name | Require exactly one Name match | DocumentTypeSecurityProfileId | Stop before import and request the correct value |
| resolve_organization_security_profile | A returned ORGANIZATION mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/organizationSecurityProfilesLOV | OrganizationSecurityProfileId, Name | Require exactly one Name match | OrganizationSecurityProfileId | Stop before import and request the correct value |
| resolve_position_security_profile | A returned POSITION mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/positionSecurityProfilesLOV | PositionSecurityProfileId, Name | Require exactly one Name match | PositionSecurityProfileId | Stop before import and request the correct value |
| resolve_legislative_data_group_security_profile | A returned legislative-data-group mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/legislativeDataGroupSecurityProfilesLOV | LegislativeDataGroupSecurityProfileId, Name | Require exactly one Name match | LegislativeDataGroupSecurityProfileId | Stop before import and request the correct value |
| resolve_payroll_security_profile | A returned payroll mapping has an explicit selection or needs a View All default | Security profile Meaning | GET /hcmRestApi/resources/{version}/payrollGenericLOV?finder=findByWord;PayRestName=Enabled_PayrollSecurityProfilePVO,FilterAttributes=Name,SearchTerms={SearchString} | Code, Meaning | Require exactly one Meaning match | Code | Stop before import and request the correct value |
| resolve_payroll_flow_security_profile | A returned payroll-flow mapping has an explicit selection or needs a View All default | Security profile Meaning | GET /hcmRestApi/resources/{version}/payrollGenericLOV?finder=findByWord;PayRestName=Enabled_FlowSecurityProfilePVO,FilterAttributes=Name,SearchTerms={SearchString} | Code, Meaning | Require exactly one Meaning match | Code | Stop before import and request the correct value |
| resolve_element_security_profile | A returned element mapping has an explicit selection or needs a View All default | Security profile Meaning | GET /hcmRestApi/resources/{version}/payrollGenericLOV?finder=findByWord;PayRestName=Enabled_ElementSecurityProfilePVO,FilterAttributes=Name,SearchTerms={SearchString} | Code, Meaning | Require exactly one Meaning match | Code | Stop before import and request the correct value |
| resolve_talent_pool_security_profile | A returned talent-pool mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/talentPoolSecurityProfilesLOV | PoolSecurityProfileId, Name | Require exactly one Name match | PoolSecurityProfileId | Stop before import and request the correct value |
| resolve_job_requisition_security_profile | A returned job-requisition mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/recruitingReqSecurityProfilesLOV | RequisitionSecurityProfileId, Name | Require exactly one Name match | RequisitionSecurityProfileId | Stop before import and request the correct value |
| resolve_candidate_security_profile | A returned candidate mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/recruitingCandidatesSecurityProfilesLOV | CandSecProfileId, Name | Require exactly one Name match | CandSecProfileId | Stop before import and request the correct value |
| resolve_transaction_security_profile | A returned transaction mapping has an explicit selection or needs a View All default | Security profile Name | GET /hcmRestApi/resources/{version}/transactionSecurityProfilesLOV | TransactionSecurityProfileId, Name | Require exactly one Name match | TransactionSecurityProfileId | Stop before import and request the correct value |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A data role is created or updated | Resolve the inherited role through active-job-role rolesLOV search; continue only when exactly one active job role is returned, then invoke the mapping action with its RoleId |
| A new data role is created | Resolve the final Role Name through derive_available_data_role_name_and_code: retain a supplied Role Name, or derive it from the inherited job role and at least one security-scope descriptor only when absent. Then derive the data-role Role Code only as `role_name.upper().replace(" ", "_") + "_DATA"`, preserving every space replacement as is. Ignore any supplied data-role Role Code. Require the display name to be shorter than 100 characters, then use check_derived_data_role_identity_availability to check the exact Role Name and internally derived Role Code through rolesLOV. Continue only when both are available; do not create suffix variants. |
| A new data role is created | After resolving the eligible inherited job role, query hcmDataRoles with q=RoleId={JobRoleId} and expand=securityProfiles. Disclose the distinct associated security-profile names before preview and require explicit acknowledgment when names are returned |
| A security profile is assigned directly to an existing role | Resolve the active existing target role through rolesLOV, then invoke the mapping action with its RoleId. Line Manager or Employee abstract roles and customer-defined roles are acceptable direct-assignment targets; do not create a data role solely to assign their security profiles. |
| The mapping action response is evaluated | Permit only security-profile types returned by the action, and resolve each explicit selection or View All default through its documented accessor |
| A Data Roles FSM package is generated | Resolve the current target-environment template-only layout first. Generate parent and child rows from its member, header, field-mapping, ViewInstanceName, GroupingKey, and linkage outputs. When the template omits ViewInstanceName or GroupingKey, use the resolver's documented member-specific fallback. Retain ASM_SETUP_CSV_METADATA.xml byte-for-byte without any change. |
| An existing data role is updated | Resolve the existing-role baseline first. Use the role code for DataRoleName, DataRoleIdResolverName, child parent links, and child DataRoleName; preserve all other baseline values except explicit selections. |

## Profile Selection Defaulting

For every security-profile type returned by the mapping action, use an explicit user-provided security profile when one is supplied. For every remaining type, use the documented View All profile below and resolve it through the applicable documented accessor. Do not invent a profile name. If the accessor has zero or multiple matches, stop before creating a preview or import package. Record returned types, explicit selections, defaulted selections, and unresolved types in the project run artifact.

| Security Profile Type | Default Profile Name |
|---|---|
| Person | View All People |
| Public Person | View All People |
| Country | View All Countries |
| Legislative Data Groups | View All Legislative Data Groups |
| Position | View All Positions |
| Organization | View All Organizations |
| Document Types | View All Document Types |
| Payroll | View All Payrolls |
| Payroll Flow | View All Flows |
| Element | View All Elements |
| Transaction | View All Transactions |
| Job Requisition | View All Job Requisitions |
| Candidate | View All Candidates |
| Talent Pool | View All Talent Pools |

## Security Profile Accessor Routing

| Security Profile Mapping | Resolver | Values to Fill |
|---|---|---|
| Country Security Profile | resolve_country_security_profile | CountrySecurityProfileId |
| Person Security Profile | resolve_person_security_profile | PersonSecurityProfileId |
| Public Person Security Profile | resolve_public_person_security_profile | PersonSecurityProfileId |
| Document Type Security Profile | resolve_document_type_security_profile | DocumentTypeSecurityProfileId |
| Organization Security Profile | resolve_organization_security_profile | OrganizationSecurityProfileId |
| Position Security Profile | resolve_position_security_profile | PositionSecurityProfileId |
| Legislative Data Group Security Profile | resolve_legislative_data_group_security_profile | LegislativeDataGroupSecurityProfileId |
| Payroll Security Profile | resolve_payroll_security_profile | Code |
| Payroll Flow Security Profile | resolve_payroll_flow_security_profile | Code |
| Element Security Profile | resolve_element_security_profile | Code |
| Talent Pool Security Profile | resolve_talent_pool_security_profile | PoolSecurityProfileId |
| Job Requisition Security Profile | resolve_job_requisition_security_profile | RequisitionSecurityProfileId |
| Candidate Security Profile | resolve_candidate_security_profile | CandSecProfileId |
| Transaction Security Profile | resolve_transaction_security_profile | TransactionSecurityProfileId |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASPR.LOOKUP_MAPPINGS | decision | 3 | reference_lookup | resolved->ASPR.LOOKUP_INHERITED_JOB_ROLE_ACCESS;unresolved->ASPR.ERROR | ASPR.APPLY_DEFAULTS | stop | Valid security-profile mappings must be identified for the applicable role target |
| ASPR.LOOKUP_INHERITED_JOB_ROLE_ACCESS | decision | 4 | reference_lookup | profiles_assigned->ASPR.ACKNOWLEDGE_INHERITED_JOB_ROLE_ACCESS;no_profiles->ASPR.RESOLVE_SECURITY_PROFILES;not_applicable->ASPR.RESOLVE_SECURITY_PROFILES;unresolved->ASPR.ERROR | ASPR.LOOKUP_MAPPINGS | stop | A new data role is being created from an eligible inherited job role |
| ASPR.RESOLVE_SECURITY_PROFILES | decision | 6 | reference_lookup | resolved->ASPR.RESOLVE_CSV_LAYOUT;unresolved->ASPR.ERROR | ASPR.LOOKUP_MAPPINGS | stop | Every explicit security-profile selection and required View All default is resolved through its documented accessor |
| ASPR.RESOLVE_CSV_LAYOUT | decision | 7 | reference_lookup | resolved->ASPR.READINESS;unresolved->ASPR.ERROR | ASPR.RESOLVE_SECURITY_PROFILES | stop | A Data Roles FSM CSV package is generated from a current target-environment template |
