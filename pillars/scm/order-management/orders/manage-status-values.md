---
task_code: "DOO_MANAGE_STATUS_VALUES"
task_name: "Manage Status Values"
parent_skill_id: "scm.order-management.orders"
pillar: "SCM"
offering: "Order Management"
functional_area: "Orders"
functional_area_code: "ORA_DOO_ORDER_FULLFILLMENT"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Status Values

- **Task code:** `DOO_MANAGE_STATUS_VALUES`
- **Purpose:** Review and maintain status values, display names, and assignments used by Order Management tasks, fulfillment lines, and orchestration processes.
- **Execution rule:** The user completes the approved change manually in Oracle Fusion **Setup and Maintenance**, on **Manage Status Values**, and performs manual validation in the applicable Oracle Fusion **Order Management** user interface identified by the task guidance, with no API, import, automated configuration, or browser automation.

Use the [standard shared manual workflow](../../../../shared/common/manual-tasks/SKILL.md).

Provide manual steps directly from this task using the user’s supplied values. Stay within the documented guidance, identify missing details, and do not create separate guides or project artifacts solely to explain the steps.

## Manual steps

1. Confirm the approved change reference, environment and tenant release, functional owner, target tabs and records, exact existing and proposed values, affected task types and processes, and rollback owner. Start in nonproduction and confirm setup access. Verify that the supplied procedure applies to your tenant release and available controls. Agree on the business meaning and identifiers before editing; resolve missing details with the owner.
2. Inventory existing consumers, including reports and integrations where relevant, and capture baseline values, labels, parent records, and assignments. Have the process owner define the intended selectable values and runtime results. Prepare a controlled test order, integration-owner participation where external responses are involved, and an observation window. Preserve predefined final process and order-line conditions for shipment and invoice tasks; a display requirement does not justify altering those contracts.
3. Open **Setup and Maintenance** and search for **Manage Status Values**. The route to task search depends on your tenant. Select the relevant tab and locate the exact record using available search or table controls. If access is unavailable, have the security administrator verify task access. For review-only work, compare the captured setup with the approved design, record discrepancies, and proceed to the applicable manual validation without changing setup.
4. Select only the tabs required by the approved design: **Status Codes** maintains display names used in the Order Management work area; **Fulfillment Lines** defines selectable line statuses for orchestration; **Task Types** associates statuses with the relevant task type, including external fulfillment statuses; **Orchestration Process Classes** groups assignable statuses for relevant process configuration. Do not edit all four tabs merely because they are available. Task-level mappings and completion behavior belong to **Manage Task Status Conditions**.
5. For **Status Codes**, **Fulfillment Lines**, or **Task Types**, use the tenant's supported create, edit, or association controls for the approved record. The supplied overview does not establish all row-entry labels or imply that seeded records and codes are editable. Enter only approved fields and confirm the parent association before committing a child row. Check spelling, case, display wording, and scope. Save with the available control and record its actual label. Capture validation messages rather than substituting another value. Reopen and compare the persisted record and associations with the design and baseline.
6. Only when creating a process class is in scope, open **Orchestration Process Classes**, then select **Actions > Create** in the class list. Enter the approved **Code**, **Name**, and **Description**, then select **Save**. In **Status Values**, select **Actions > Add Row** and the required **Status Value**; repeat for each approved member. Select **Save and Close** and reopen to confirm exact membership. The process owner can select the class in **Process Class** on **Edit Orchestration Process Definitions**; class membership determines the statuses available in that process's **Status Conditions**. Process use and deployment remain separate dependency activities.
7. With the task or process owner, open the consuming configuration and confirm the intended selection is available in the correct context. Verify that unrelated selections and existing assignments match the baseline. Record any separately required process change or deployment and its owner. If a selection is missing, compare record identity, assignments, and consumer context before proceeding. If a record cannot be edited, capture the control state and involve the setup owner instead of changing another record. Resolve dependency gaps before runtime testing.
8. In your tenant's **Order Management** work area, prepare an order using the intended process and task configuration. Submit once and capture order, revision, fulfillment-line, process, and version identifiers. Observe the agreed checkpoint using the tenant's fulfillment and orchestration details and record the actual navigation. Where external responses are part of the agreed controlled test, obtain correlated response evidence from the integration owner and manually inspect the resulting behavior. Capture task, line, and process observations separately, compare each with its own expected result, and check the intended label or selection behavior and downstream progression.
9. Run a representative existing scenario that shares the changed setup. If runtime differs, verify the actual process/version and inspect correlated response and downstream evidence with the owner. If an existing scenario changes unexpectedly, stop further tests and compare shared setup with baseline. Retain the exact message, environment, timestamp, record, consumer reference, and expected versus actual behavior.
10. If restoration is required, stop further test submissions and identify affected orders. Restore supported editable values and associations from baseline through the setup UI. Remove a newly created record only if the UI supports removal and the owner confirms it has no required references; otherwise leave it unused and record cleanup. Coordinate separately changed process restoration with its owner. Do not assume a universal delete, deactivate, or publish action. Reopen the setup, run a fresh controlled restoration check, and review affected orders individually; restored setup does not establish reversal of completed fulfillment actions.

## Manual validation guidance

Start each case as **Not Executed**. Record observed results and mark irrelevant cases **Not Applicable** with a reason. For review-only work, distinguish the design comparison from changes or runtime tests that were not performed.

| Case | Manual check | Acceptance criterion |
| --- | --- | --- |
| SV01 | Reopen the saved record and assignments. | Exact values and associations match the approved change without unrelated modifications. |
| SV02 | Inspect the intended consumer's selection. | The required value is selectable in the correct context. |
| SV03 | Observe a controlled runtime order. | Display, task/line/process observations, and progression match the owner's predefined expectations. |
| SV04 | Test a representative existing consumer. | Behavior remains consistent with its baseline. |
| SV05 | Execute an approved invalid-input case, if in scope. | The validation result is observable without unintended persisted setup. |
| SV06 | Reopen restored setup and run a fresh controlled check. | Supported restored values and associations match baseline and expected behavior is observed. |

Retain the operator, timestamp and time zone, environment/release, before-and-after captures, target record and assignments, consumer and process/version references, order/revision/line, applicable correlated response evidence, expected and actual results, and case outcome in the approved change record. Record **Pass**, **Fail**, or **Blocked**; use **Blocked** when access, data, dependencies, or required integration evidence prevent evaluation. A saved record or selectable value alone does not establish correct fulfillment behavior. Assign blockers and defects to owners, record rollback status and affected-order disposition, and have the functional owner record acceptance or required follow-up.
