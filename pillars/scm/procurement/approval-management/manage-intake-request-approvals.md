---
task_code: "ORA_PO_MANAGE_INTAKE_REQUEST_APPROVALS"
task_name: "Manage Intake Request Approvals"
parent_skill_id: "scm.procurement.approval-management"
pillar: "SCM"
offering: "Procurement"
functional_area: "Approval Management"
functional_area_code: "ORA_PO_APPROVAL_MANAGEMENT_FA"
available_flag: "Y"
export_import_supported_flag: "N"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Intake Request Approvals

**Manual task — guidance only.** State this up front. The user makes approved
changes in Fusion; no automated export/import, API calls, or browser actions.
Catalog flags and generated loader metadata do not authorize automation.

- Task code: `ORA_PO_MANAGE_INTAKE_REQUEST_APPROVALS`
- Purpose: Author approval rules to route intake requests for approval.

Use the standard manual workflow in
[shared.common.manual-tasks](../../../../shared/common/manual-tasks/SKILL.md).

Give navigation, task-specific steps, and validation directly. Reuse supplied
context; clarify only an ambiguous task or scope. Do not request configuration
values, credentials, or completion confirmation in chat. The implementer obtains
missing approved values from the administrator and enters them in Fusion.
Do not invent defaults or create separate guides to repeat these steps.

## Access the task

1. Sign in to the target Fusion environment with access to Setup and Maintenance and the named approval task.
2. Open **Navigator** > **Setup and Maintenance**, then select **Procurement** in **Setup**.
3. Select **Approval Management** in **Functional Areas**, set **Show** to **All Tasks**, and open **Manage Intake Request Approvals**. Alternatively, use **Search Tasks** or the **Tasks** panel search to find the exact task name and select **Go to Task**. Confirm the exact task name before editing; intake-request approvals are distinct from supplier registration, supplier profile, spend authorization, and purchasing-document approvals.
4. Review the existing rules before applying the approved change. If the task is unavailable or cannot be opened, ask the Fusion security or setup administrator to confirm access, offering enablement, and required privileges. Do not substitute another approval task.

## Configuration versus migration

For rule migration, refer the implementer to the workflow administrator's
approved manual SOA Composer export/import procedure—not FSM or Data Loader.
Archives can replace complete files and affect other rules or tasks; require
administrator review of archive scope and existing target configuration.
This skill does not generate or import an archive.

## Manual steps

Verify stage names/order, participants, and seeded routing against the target
environment and current-release Oracle documentation. If they differ, consult
the workflow administrator; do not recreate stages or substitute routing to
match an example.

1. Review the approval stages, participants, and existing rules displayed for intake requests. Verify their order and behavior using current-release Oracle documentation.
2. Inspect the actual conditions and approver routes for the request types and templates in scope. Do not assume a particular seeded rule, participant, or approver group.
3. Configure the approved rule name, conditions, available participant, approver route or group, priority, and fallback behavior directly in Fusion.
4. Preserve unrelated rules, participants, and topology. Disable a rule or participant only when included in the approved change, then save.

## Manual validation

Submit a safe intake request that matches a changed rule. Where safe and
authorized, also test a nonmatching request and the configured fallback; a
nonmatch does not imply automatic approval. Confirm unrelated rules remain
unchanged. Record the environment, implementer, changed/matched rule
identifiers, resolved approvers, and expected versus actual outcome. Record
validation as deferred when a safe test is unavailable.
