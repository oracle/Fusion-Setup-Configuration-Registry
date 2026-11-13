# Sales Orchestration Security Console Role Provisioning

## Contents

- [Purpose and Boundary](#purpose-and-boundary)
- [Enable Permission-Group Integration](#enable-permission-group-integration)
- [Enable Permission Groups for the Predefined Role](#enable-permission-groups-for-the-predefined-role)
- [Configure a Custom Job Role](#configure-a-custom-job-role)
- [Add Task Permission Groups and Security Views](#add-task-permission-groups-and-security-views)
- [Add Functional Privileges](#add-functional-privileges)
- [Add Duty Roles](#add-duty-roles)
- [Add Knowledge Data Security Policies](#add-knowledge-data-security-policies)
- [Save, Synchronize, and Verify](#save-synchronize-and-verify)
- [Sources](#sources)

## Purpose and Boundary

Use this procedure when an administrator needs to prepare
`ORA_ZBS_SALES_ADMINISTRATOR_JOB` or a custom job role for Sales Motions,
Sales Plays and Content, or Data Capture Rules. Use
`ZBS_SALES_ADMINISTRATOR_CUSTOM_JOB` only as a synthetic example; search for
the actual custom role in the target environment.

This procedure is advisory. The three task skills may explain these steps but
must not change a profile option, edit a role, add a grant, submit a Security
Console change, or run a synchronization process.

## Enable Permission-Group Integration

Ensure the site-level profile option is enabled before configuring permission
groups:

1. Open the **Setup and Maintenance** work area.
2. Open the **Tasks** panel and select **Search**.
3. Search for **Manage Administrator Profile Values**.
4. Select the **Manage Administrator Profile Values** task.
5. In **Search: Profile Option**, enter
   `ORA_ASE_SAS_INTEGRATION_ENABLED` in **Profile Option Code**, and select
   **Search**.
6. Locate the row whose profile level is **Site**.
7. If **Profile Value** is not already **Yes**, select **Yes**.
8. Select **Save and Close**.

Do not create a duplicate profile value when the Site value is already
**Yes**. This profile option prepares the Security Console to evaluate
permission groups and related objects.

## Enable Permission Groups for the Predefined Role

Use this path when the administrator assigns the predefined Sales
Administrator job role:

1. Go to **Navigator** > **Tools** > **Security Console**.
2. Select **Roles**.
3. Search for `ORA_ZBS_SALES_ADMINISTRATOR_JOB`.
4. From the search result, select **Edit Role**.
5. Select **Enable Permission Groups**, and confirm the choice.
6. Go to **Summary**. Select **Next** until **Summary** if necessary.
7. Select **Save and Close**.

If permission groups are already enabled, the enablement button may no longer
appear. Do not interpret its absence alone as an error; inspect the role's
Permission Groups step before changing the profile option again.

## Configure a Custom Job Role

Use the remaining sections when a custom job role is used instead of
`ORA_ZBS_SALES_ADMINISTRATOR_JOB`:

1. Go to **Navigator** > **Tools** > **Security Console** > **Roles**.
2. Search for the actual custom job role, such as the synthetic example
   `ZBS_SALES_ADMINISTRATOR_CUSTOM_JOB`.
3. From the search result, select **Edit Role**.
4. If permission groups haven't been enabled for the custom role, select
   **Enable Permission Groups** and confirm before continuing.
5. Add only the task-specific permission groups, functional privileges, duty
   roles, and data security policies required by the role's intended scope.

## Add Task Permission Groups and Security Views

Read the selected task's security reference in full before adding permission
groups. It is the authoritative list for Sales Motion, Sales Play, or Data
Capture Read/Create/Update/Delete grants.

For every required permission group:

1. In **Edit Role**, go to the **Permission Groups** step.
2. Select **Add Permission Groups**.
3. Search for one exact permission-group name from the selected task security
   reference.
4. Select the matching result, select **Add Selected Permission Groups**, and
   close the search dialog with **Cancel**.
5. Select the newly added permission group in the upper table.
6. In **Details**, open the **Security Views** tab.
7. Select **Add Security View**.
8. Select **All Rows**, select **Add Security View**, and then close the dialog
   with **Cancel**.
9. Repeat these steps for every permission group required for the operations
   the custom role must support.
10. Select **Next** until **Summary**, and then select **Save and Close** after
    all required role changes are complete.

Do not infer permission-group names. Use the task-specific security matrix
retained in the local references. The task skills execute read operations
only, but their security references intentionally include Create, Update, and
Delete provisioning guidance.

## Add Functional Privileges

1. Edit the custom role in **Security Console** > **Roles**.
2. Go to the **Function Security Policies** step.
3. Select **Add Function Security Policy**. The UI may label this action **Add
   Functional Security Policy**.
4. Search for the privilege required by each task in the custom role's scope:

   | Task | Functional privilege |
   | --- | --- |
   | Sales Motions | `ZCA_VIEW_SALES_MOTIONS_PRIV` |
   | Sales Plays and Content | `ZCA_VIEW_SALES_PLAYS_PRIV` |
   | Data Capture Rules | `ZCA_VIEW_DATA_CAPTURE_RULES_PRIV` |

5. Select the matching result and select **Add Privilege to Role**.
6. Repeat for the other task privileges only when the custom role supports
   those tasks.
7. Select **Next** until **Summary**, and then select **Save and Close** after
   all required role changes are complete.

## Add Duty Roles

1. Edit the custom role in **Security Console** > **Roles**.
2. Go to **Role Hierarchy** and open **Roles and Permission Groups**.
3. Select **Add Role**.
4. Search for and select both common duties:
   - `ORA_DR_FAI_GENERATIVE_AI_AGENT_RUNTIME_DUTY`
   - `ORA_ZCA_ACCESS_GROUPS_ENABLEMENT_DUTY`
5. Select **Add Role Membership**, and then close the search dialog with
   **Cancel**.
6. For a custom Sales Plays and Content administrator that authors Knowledge
   articles, also add `ORA_CSO_KNOWLEDGE_AUTHORING_DUTY`.
7. Select **Next** until **Summary**, and then select **Save and Close** after
   all required role changes are complete.

## Add Knowledge Data Security Policies

This section applies to Sales Plays and Content administration and Content
Intelligence consumption. Do not require these Knowledge policies solely for a
Sales Motion or Data Capture Rule role.

For a custom Sales Plays and Content administrator role:

1. Edit the custom role in **Security Console** > **Roles**.
2. Go to the **Data Security Policies** step.
3. Select **Create Data Security Policy**.
4. Enter a descriptive policy name.
5. Set **Start Date** to the previous day's date.
6. Set **Data Resource** or **Data Source**, depending on the UI label, to
   **Knowledge Content Types**.
7. Set **Data Set** to **All Values**.
8. Select these actions:
   - **View Article of a content type**
   - **Publish Article of a content type**
   - **Update Article of a content type**
   - **Delete Article of a content type**
9. Select **OK**.
10. Create the remaining administrator and end-user policies exactly as listed
    in `sales-plays-and-content/references/sales-plays-and-content-security.md`,
    including the **Sales Play Consumer** user-group and **Sales Force
    Automation** department access policies.
11. Keep product short code `ZBS` unchanged where the policy definition exposes
    it.
12. Select **Next** until **Summary**, and then select **Save and Close**.

Do not copy Knowledge policies into unrelated task roles. Apply each policy to
the administrator or end-user role identified by the approved policy matrix.

## Save, Synchronize, and Verify

1. Review the role's **Summary** before saving. Confirm that only the intended
   permission groups, `All Rows` security views, privileges, duty roles, and
   data security policies are present.
2. Select **Save and Close**.
3. Follow `security-synchronization-processes.md` after changing roles,
   privileges, permission groups, or data security policies.
4. Do not report the role as ready until the applicable synchronization and
   import processes complete successfully.
5. Treat role membership as unknown until authorized administrator evidence
   confirms it. A successful task read proves effective access only for that
   request.

## Sources

The security grants supplied when this reference was authored are reproduced
here and in the task-specific security references. Verify them against the
target release during a release-freshness review.

- Oracle profile-option and permission-group enablement guidance:
  `https://docs.oracle.com/en/cloud/saas/sales/faekt/security-and-privileges-to-setup-and-extract-key-terms-from-contract-documents.html`
- Oracle AI Agent Studio permission-group guidance:
  `https://docs.oracle.com/en/cloud/saas/fusion-ai/26b/aiaas/access-ai-agent-studio.html`
