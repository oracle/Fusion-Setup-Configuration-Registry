---
task_code: "PO_MANAGE_PURCHASING_DOCUMENT_APPROVALS"
task_name: "Manage Purchasing Document Approvals"
parent_skill_id: "scm.procurement.approval-management"
pillar: "SCM"
offering: "Procurement"
functional_area: "Approval Management"
functional_area_code: "ORA_PO_APPROVAL_MANAGEMENT_FA"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Purchasing Document Approvals

**Manual task — guidance only.** State this up front. The user makes approved
changes in Fusion; no automated export/import, API calls, or browser actions.
Catalog flags and generated loader metadata do not authorize automation.

- Task code: `PO_MANAGE_PURCHASING_DOCUMENT_APPROVALS`
- Purpose: Configure rules that route purchasing documents for approval.

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
3. Select **Approval Management** in **Functional Areas**, set **Show** to **All Tasks**, and open **Manage Purchasing Document Approvals**. Alternatively, use **Search Tasks** or the **Tasks** panel search to find the exact task name and select **Go to Task**. Confirm the exact task name before editing; requisition, purchasing document, and supplier approvals use distinct tasks.
4. Review the existing rules before applying the approved change. If the task is unavailable or cannot be opened, ask the Fusion security or setup administrator to confirm access, offering enablement, and required privileges. Do not substitute another approval task.

## Configuration versus migration

The effective catalog marks both export/import and CSV export/import as
unsupported (`N`). Do not generate a Data Loader sample or route this task to
FSM or Data Loader.
For migration, refer the implementer to the workflow administrator's approved
manual procedure for the target release. Require administrator review of the
migration scope and existing target rules. This skill does not create or import
migration artifacts.

## Manual steps

Verify stage names/order, participants, and routing against the target
environment and current-release Oracle documentation. If they differ, consult
the workflow administrator; do not recreate stages or substitute routing to
match an example.

1. Review existing rules and the approved document scope, including purchase orders, agreements, or change orders as applicable. Preserve unrelated configuration.
2. Select the applicable stage and **Edit Rules**. Create or edit only the approved rule; use the available conditions and actions to define routing.
3. Review document attributes, amount boundaries, approver groups or hierarchies, and serial or parallel routing as applicable to the approved change. Confirm referenced approvers with the administrator; do not assume seeded groups or fallback behavior.
4. Save the approved changes using the controls available in the target environment. Disable a rule or participant only when included in the approved change.

## Manual validation

Submit a safe purchasing document that matches a changed rule. Where safe and
authorized, test relevant amount boundaries, a nonmatching document, and any
changed agreement or change-order scenario. A nonmatch does not imply automatic
approval. Check resolved approvers, routing order, and the approval action
history; confirm unrelated rules remain unchanged. Record the environment,
implementer, changed/matched rule identifiers, document identifier, and expected
versus actual outcome. Record validation as deferred when a safe test is
unavailable. Refer routing failures to the workflow administrator before retrying.

## Sources and release verification

Repository pattern: [Manage Supplier Registration Approvals](manage-supplier-registration-approvals.md).
Repository product guidance: [Procurement references](../../../../knowledge/product-guidance/pillars/scm/procurement/reference.md).

Oracle Procurement **26D** was verified on **2026-10-19** through the
[All Books catalog](https://docs.oracle.com/en/cloud/saas/procurement/26d/books.html).
The following 26D PDF guides provide the task navigation and rule behavior;
individual HTML topic pages were unavailable during verification:

- [Implementing Procurement](https://docs.oracle.com/en/cloud/saas/procurement/26d/oapro/implementing-procurement.pdf), Approval Management for Procurement and Purchasing Configuration: stage selection and approval rule editing.
- [Using Procurement](https://docs.oracle.com/en/cloud/saas/procurement/26d/oaprc/using-procurement.pdf), How Purchase Order Approval Is Processed: task location, document conditions, and routing behavior.

The manual-only execution boundary follows the repository reference pattern.
Scoped changes, boundary tests, migration review, and deferred validation are
implementation recommendations. Recheck the latest available Oracle release
and target-environment behavior when using this guidance.
