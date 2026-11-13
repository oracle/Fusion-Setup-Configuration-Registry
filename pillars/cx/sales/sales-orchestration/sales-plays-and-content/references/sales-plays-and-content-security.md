# Sales Plays and Content Security Requirements

## Contents

- [Source](#source)
- [Security Console Provisioning](#security-console-provisioning)
- [Out-of-Box Role](#out-of-box-role)
- [Custom Job Role Duty Roles](#custom-job-role-duty-roles)
- [BOSS Permission Groups](#boss-permission-groups)
- [Knowledge Authoring Administrator Alternative](#knowledge-authoring-administrator-alternative)
- [Knowledge Management Data Security Policies](#knowledge-management-data-security-policies)
- [Content Intelligence End-User Access](#content-intelligence-end-user-access)
- [Security Synchronization Processes](#security-synchronization-processes)
- [Complete Answer Requirement](#complete-answer-requirement)
- [Verification Boundary](#verification-boundary)

## Source

The out-of-box grants below reflect the security requirements supplied when
this reference was authored. Use this local reference for future skill runs;
verify the grants against the target release during an explicit
release-freshness review.

The custom-role duties and security-synchronization instructions below are
additional developer-provided requirements for this task skill.

## Security Console Provisioning

Read `../../references/security-console-role-provisioning.md` for the complete
step-by-step procedure to:

- set `ORA_ASE_SAS_INTEGRATION_ENABLED` to **Yes** at Site level;
- enable permission groups for `ORA_ZBS_SALES_ADMINISTRATOR_JOB`;
- add this task's permission groups and an **All Rows** security view to a
  custom job role;
- add `ZCA_VIEW_SALES_PLAYS_PRIV` and the required common and Knowledge duty
  roles; and
- create the administrator and end-user Knowledge data security policies.

## Out-of-Box Role

`ORA_ZBS_SALES_ADMINISTRATOR_JOB` is the supported out-of-box role containing
the documented functional privilege, BOSS permission groups, and data security
policies needed for Sales Plays, their content artifacts, Knowledge article
authoring, and Sales Play content consumption.

For access to the Sales Plays setup screen, the documented functional privilege
is `ZCA_VIEW_SALES_PLAYS_PRIV`. It is not required merely because this skill
invokes a BOSS read endpoint.

## Custom Job Role Duty Roles

When access is provisioned through a custom job role instead of
`ORA_ZBS_SALES_ADMINISTRATOR_JOB`, add both of these duty roles:

- `ORA_DR_FAI_GENERATIVE_AI_AGENT_RUNTIME_DUTY` for asynchronous API access
- `ORA_ZCA_ACCESS_GROUPS_ENABLEMENT_DUTY` for BOSS API access

These duty roles are required in addition to the operation-specific BOSS
permission groups and security view below.

For Knowledge article administration, also add the Knowledge authoring duty
and administrator data security policies in the Knowledge Management sections
below.

## BOSS Permission Groups

For a custom role, grant every permission group in the section for each
operation the user must perform. Every operation also requires the `All Rows`
security view.

`All Rows` is the supplied security-view display label. This reference does not
provide a separate technical identifier for it.

### Read

- `read:SalesPlay`
- `read:SalesPlayTranslation`
- `read:SalesPlayArtifact`
- `read:SalesPlayArtifactTranslation`

### Create

- `create:SalesPlay`
- `create:SalesPlayTranslation`
- `create:SalesPlayArtifact`
- `create:SalesPlayArtifactTranslation`

### Update

- `update:SalesPlay`
- `update:SalesPlayTranslation`
- `update:SalesPlayArtifact`
- `update:SalesPlayArtifactTranslation`

### Delete

- `delete:SalesPlay`
- `delete:SalesPlayTranslation`
- `delete:SalesPlayArtifact`
- `delete:SalesPlayArtifactTranslation`

## Operation Mapping

| Skill action | Security operation |
|---|---|
| List Sales Plays | Read |
| Get one Sales Play | Read |
| Query Sales Plays through `$query` | Read |
| Read content artifacts or translations through documented accessors | Read |

The Create, Update, and Delete rows are prerequisite guidance only. This skill
does not execute those operations even when the acting user has the grants.

## Knowledge Authoring Administrator Alternative

When `ORA_ZBS_SALES_ADMINISTRATOR_JOB` cannot be assigned to the administrator,
add this duty role to the custom administrator job role:

- `ORA_CSO_KNOWLEDGE_AUTHORING_DUTY`

Also reproduce all Sales Administrator data security policies below on the
custom role. The duty supplies Knowledge authoring functional access; the data
security policies supply access to the Sales Play article type, consumer user
group, and Sales Force Automation department.

## Knowledge Management Data Security Policies

The source identifies these policies for the Sales Administrator job role:

| Auxiliary Verb | Verb | Security Business Object | Attribute | Condition | Privilege Title |
|---|---|---|---|---|---|
| CAN | VIEW | Knowledge Content Types | Object Type | Sales Play articles | View Article of a content type |
| CAN | UPDATE | Knowledge Content Types | Object Type | Sales Play articles | Update Article of a content type |
| CAN | PUBLISH | Knowledge Content Types | Object Type | Sales Play articles | Publish Article of a content type |
| CAN | DELETE | Knowledge Content Types | Object Type | Sales Play articles | Delete Article of a content type |
| CAN | ACCESS | Knowledge User groups | Object Type | Access to Sales Play Consumer user group | Access Content with User Group |
| CAN | ACCESS | Knowledge Departments | Object Type | The Sales Force Automation Department | Access Content with Department |

Keep product short code `ZBS` unchanged when reproducing these policies.

## Content Intelligence End-User Access

An end user invoking `/api/knowledge-management/v2/contentIntelligence` may be
a Sales Representative, Sales Manager, or Sales Administrator. The acting
user's job role must include both content-consumption policies:

| End-User Job Role | Auxiliary Verb | Verb | Security Business Object | Attribute | Condition | Privilege Title |
|---|---|---|---|---|---|---|
| Sales Representative Job | CAN | ACCESS | Knowledge User groups | Object Type | Access to Sales Play Consumer user group | Access Content with User Group |
| Sales Representative Job | CAN | ACCESS | Knowledge Departments | Object Type | The Sales Force Automation Department | Access Content with Department |
| Sales Manager Job | CAN | ACCESS | Knowledge User groups | Object Type | Access to Sales Play Consumer user group | Access Content with User Group |
| Sales Manager Job | CAN | ACCESS | Knowledge Departments | Object Type | The Sales Force Automation Department | Access Content with Department |
| Sales Administrator Job | CAN | ACCESS | Knowledge User groups | Object Type | Access to Sales Play Consumer user group | Access Content with User Group |
| Sales Administrator Job | CAN | ACCESS | Knowledge Departments | Object Type | The Sales Force Automation Department | Access Content with Department |

`ORA_ZBS_SALES_ADMINISTRATOR_JOB` supplies these policies out of the box. For
a custom end-user role, reproduce both applicable access policies rather than
assuming that the user's sales persona supplies them.

## Security Synchronization Processes

Read `../../references/security-synchronization-processes.md` for the complete
step-by-step instructions. The shared procedure covers:

- the one-time **Retrieve Latest LDAP Changes** run before implementation;
- the daily **Import User and Role Application Security Data** schedule; and
- the requirement for the import start time to follow the daily **Send Pending
  LDAP Requests** process.

After any change to permission groups, roles, or privileges, do not treat the
security change as ready for verification until the applicable **Send Pending
LDAP Requests** run and the subsequent import complete successfully. This
read-only skill explains the processes but does not submit, schedule, poll, or
retry them.

## Complete Answer Requirement

When asked for Sales Play prerequisites, the permission-group profile option,
predefined-role enablement, custom-role provisioning, roles, duty roles,
privileges, permission groups, or access requirements, return the complete
contents of this security contract: the out-of-box job role, both custom-role
duties, the Knowledge authoring duty, setup-screen privilege, all
Read/Create/Update/Delete permission groups, the `All Rows` security view, the
administrator Knowledge
data policies, the end-user content-consumption policies, the one-time LDAP
retrieval procedure, the recurring application-security import schedule, and
its ordering after **Send Pending LDAP Requests**. Also include the shared
profile-option, predefined-role, custom-role, and Knowledge-policy Security
Console procedures. Do not return only the Read section because the task
skill's current API operations are read-only.

This reference establishes security prerequisites only. It does not establish
licensing, feature-opt-in, or offering-configuration prerequisites; report
those as undocumented rather than inventing them.

## Verification Boundary

Report role, permission-group, functional-privilege, data-security-policy, and
security-view membership as `unknown` unless authorized administrator evidence
confirms them.

A successful requested LIST, GET, or QUERY proves effective read access only
for that call. It does not prove role membership or any create, update, or
delete permission.

A successful Content Intelligence search proves effective search access only
for that call. It does not prove Knowledge authoring access or policy
membership.
