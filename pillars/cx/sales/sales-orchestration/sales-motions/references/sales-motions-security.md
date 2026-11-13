# Sales Motions Security Requirements

## Contents

- [Source](#source)
- [Security Console Provisioning](#security-console-provisioning)
- [Out-of-Box Role](#out-of-box-role)
- [Custom Job Role Duty Roles](#custom-job-role-duty-roles)
- [BOSS Permission Groups](#boss-permission-groups)
- [Operation Mapping](#operation-mapping)
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
- add `ZCA_VIEW_SALES_MOTIONS_PRIV`; and
- add the two common duty roles.

Knowledge authoring and content-access policies in the shared procedure apply
to Sales Plays and Content, not to a role scoped only to Sales Motions.

## Out-of-Box Role

`ORA_ZBS_SALES_ADMINISTRATOR_JOB` is the supported out-of-box role containing
the documented functional privilege, BOSS permission groups, and data security
policy for Sales Motions.

For access to the Sales Motions setup screen, the documented functional
privilege is `ZCA_VIEW_SALES_MOTIONS_PRIV`. It is not required merely because
this skill invokes a BOSS read endpoint.

## Custom Job Role Duty Roles

When access is provisioned through a custom job role instead of
`ORA_ZBS_SALES_ADMINISTRATOR_JOB`, add both of these duty roles:

- `ORA_DR_FAI_GENERATIVE_AI_AGENT_RUNTIME_DUTY` for asynchronous API access
- `ORA_ZCA_ACCESS_GROUPS_ENABLEMENT_DUTY` for BOSS API access

These duty roles are required in addition to the operation-specific BOSS
permission groups and security view below.

## BOSS Permission Groups

For a custom role, grant every permission group in the section for each operation
the user must perform. Every operation also requires the `All Rows` security
view.

`All Rows` is the supplied security-view display label. This reference does not
provide a separate technical identifier for it.

### Read

- `read:SalesMotion`
- `read:SalesMotionTranslation`
- `read:ObjectiveDesignTime`
- `read:ObjectiveDesignTimeTranslation`
- `read:ObjectiveHighValueActivityDesignTime`
- `read:ObjectiveHighValueActivityDesignTimeTranslation`

### Create

- `create:SalesMotion`
- `create:SalesMotionTranslation`
- `create:ObjectiveDesignTime`
- `create:ObjectiveDesignTimeTranslation`
- `create:ObjectiveHighValueActivityDesignTime`
- `create:ObjectiveHighValueActivityDesignTimeTranslation`

### Update

- `update:SalesMotion`
- `update:SalesMotionTranslation`
- `update:ObjectiveDesignTime`
- `update:ObjectiveDesignTimeTranslation`
- `update:ObjectiveHighValueActivityDesignTime`
- `update:ObjectiveHighValueActivityDesignTimeTranslation`

### Delete

- `delete:SalesMotion`
- `delete:SalesMotionTranslation`
- `delete:ObjectiveDesignTime`
- `delete:ObjectiveDesignTimeTranslation`
- `delete:ObjectiveHighValueActivityDesignTime`
- `delete:ObjectiveHighValueActivityDesignTimeTranslation`

## Operation Mapping

| Skill action | Security operation |
|---|---|
| List Sales Motions | Read |
| Get one Sales Motion | Read |
| Query Sales Motions through `$query` | Read |

The Create, Update, and Delete rows are prerequisite guidance only. This skill
does not execute those operations even when the acting user has the grants.

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

When asked for Sales Motion prerequisites, the permission-group profile option,
predefined-role enablement, custom-role provisioning, roles, duty roles,
privileges, permission groups, or access requirements, return the complete
contents of this security contract: the out-of-box job role, both custom-role
duties, the setup-screen privilege, all Read/Create/Update/Delete permission
groups, the
`All Rows` security view, the one-time LDAP retrieval procedure, the recurring
application-security import schedule, and its ordering after **Send Pending
LDAP Requests**. Also include the shared profile-option, predefined-role, and
custom-role Security Console procedures. Do not return only the Read section
because the task skill's current API operations are read-only.

This reference establishes security prerequisites only. It does not establish
licensing, feature-opt-in, or offering-configuration prerequisites; report
those as undocumented rather than inventing them.

## Verification Boundary

Report role, permission-group, functional-privilege, and security-view
membership as `unknown` unless authorized administrator evidence confirms
them.

A successful requested LIST, GET, or QUERY proves effective read access only
for that call. It does not prove role membership or any create, update, or
delete permission.
