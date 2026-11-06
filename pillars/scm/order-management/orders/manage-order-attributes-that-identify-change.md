---
task_code: "DOO_MANAGE_ORDER_ATTRIBUTES_IDENTIFYING_CHANGE"
task_name: "Manage Order Attributes That Identify Change"
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

# Manage Order Attributes That Identify Change

- **Task code:** `DOO_MANAGE_ORDER_ATTRIBUTES_IDENTIFYING_CHANGE`
- **Purpose:** Review and maintain the attributes that identify order changes for an orchestration task type. The orchestration step's compensation pattern determines the resulting adjustment; attribute selection alone does not define that adjustment.
- **Execution rule:** The user completes the approved change manually in Oracle Fusion **Setup and Maintenance**, on **Manage Order Attributes That Identify Change**, and performs controlled order-revision validation in the applicable Oracle Fusion **Order Management** user interface, with no API, import, automated configuration, or browser automation.

Use the [standard shared manual workflow](../../../../shared/common/manual-tasks/SKILL.md).

Provide manual steps directly from this task using the user’s supplied values. Stay within the documented guidance, identify missing details, and do not create separate guides or project artifacts solely to explain the steps.

## Manual steps

1. Confirm the approved change reference, target environment and tenant release, task type, component, exact attribute, business reason, affected process/version/step, expected compensation and downstream effect, controlled test order and line, observation window, and rollback owner. Use a nonproduction environment first. Confirm that the supplied procedure applies to your tenant release and enabled experience; labels and save controls can vary. If necessary details are missing or the procedure conflicts with your application, pause and resolve them with the functional or setup owner before editing.
2. Confirm access to the setup task and permission to create and revise the selected sales orders. Have the process owner identify the processes and steps that use the task type and assess the impact of shared setup. Distinguish similarly named header and line attributes. Confirm that processing constraints permit the intended revision and that the test can reach the intended checkpoint without shipping, invoicing, or another irreversible business action.
3. Open **Setup and Maintenance** and use task search to locate **Manage Order Attributes That Identify Change**. The route to task search depends on your tenant. If the task is unavailable, have the security or setup administrator verify access and offering context. Capture the current task type, component, attribute list, and predefined indicators, together with the relevant step settings and expected downstream behavior. Identify the exact values approved to change and retain the baseline for comparison and recovery.
4. Select the relevant **Task Type** and edit the approved existing type. For the shipment example, select **Shipment**, then **Actions > Edit**, and select **Order Line** in **Orchestration Components**. Use your approved task type and component for other cases. Review **Attributes**: **Ordered Quantity** is already present in the supplied example, so do not add it again. An attribute marked **Predefined** cannot be removed.
5. Only if the required attribute is missing, select **Actions > Select and Add**, select the exact attribute in **Change Attributes**, then select **Apply > OK**. **Scheduled Ship Date** is an example, not a prescribed value. If the intended attribute is unavailable, recheck the component and attribute identity with the functional owner; do not substitute a similarly named attribute. **Actions > Edit All** applies an addition across listed task types, and **Actions > Create** creates a type requiring at least one change-identifying attribute. Use either only when explicitly included in the approved scope; creating a custom type is outside the primary existing-type procedure.
6. Commit using the save control presented by your tenant; the supplied setup procedure does not establish its final label. Reopen the exact task type and component and compare the saved configuration with the baseline. Confirm that only the approved change persists. If it does not, capture the validation message and investigate before making further edits.
7. Before runtime testing, have the process owner confirm the process and version used by the test order, that the intended step references the reviewed task type, and that its configured compensation matches the expected action. The supplied navigation for reviewing compensation is **Manage Orchestration Process Definitions > Process Details > Step Definition > Change Management**, in the **Compensation Pattern** column. Any process-definition change belongs to separate approved scope and must complete the tenant's required deployment procedure. Editing the attribute list does not create or deploy compensation rules. Pause testing if these dependencies or the expected result are unresolved.
8. Prepare a simple stock item and a single order line without shipment sets, configured-item dependencies, or partial shipments for the initial controlled test. Agree on a checkpoint where the target task is observable and the attribute remains editable. Create and submit the baseline order through your tenant's normal order-entry flow. At the checkpoint, capture the order number, revision, line, current attribute value, fulfillment status, and available downstream document reference. Choose an approved before-and-after value pair; **Ordered Quantity 10 to 12** is illustrative only and requires inventory and processing rules to permit it.
9. In the enabled sales-order experience, locate and open the current version of the baseline order. The supplied entry point is **Home > Order Management > Order Management (New) > Sales Orders**; use it only where your tenant exposes that experience. Create a revision, change only the planned value, capture it, and select **Submit Order** where available. Submit once. If confirmation is delayed or uncertain, query the order and inspect its revisions before any further submission. Capture a rejected revision's full message and line state and investigate the applicable constraint before changing setup.
10. Inspect the target step using your tenant's available fulfillment and orchestration details and record the actual navigation used. With the fulfillment owner, correlate the downstream result to the same order revision and line and compare it with the predefined compensation expectation within the agreed observation window. A saved order value alone does not establish that the downstream action occurred.
11. If recovery is required, stop further test submissions and identify already affected orders. Restore only supported editable values introduced or modified by this change against the baseline. Remove an added nonpredefined entry only if a supported removal control is available; otherwise involve the setup owner. Reopen and verify the restored setup. Have the process owner restore any separately changed process rules through the applicable deployment procedure. Review affected orders individually with the fulfillment owner; restoring configuration does not establish reversal of completed downstream actions.

## Manual validation guidance

Run applicable scenarios on separate controlled orders or clearly identified revisions. Start each case as **Not Executed** and record observed results.

| Case | Manual check | Acceptance criterion |
| --- | --- | --- |
| TC01 | Reopen saved setup. | The exact task type, component, and required attribute persist, with only the approved changes from baseline. |
| TC02 | Revise the selected attribute and inspect the target step and downstream outcome. | Observed behavior matches the compensation and business expectation defined before testing. Test a newly added attribute directly; an existing Ordered Quantity smoke test alone does not validate another addition. |
| TC03 | Review an attribute that already exists. | No duplicate or unrelated change is made. |
| TC04 | Test an owner-selected editable attribute outside the target task's change list. | Behavior matches the documented expectation after accounting for other tasks and rules; do not assume there can be no compensation elsewhere. |
| TC05 | Test a deliberately selected blocking constraint, where applicable. | The observed message matches the expected restriction and is recorded as a constraint result. |
| TC06 | Test representative additional processes that share the task type. | Their observed behavior matches their owners' expectations. |
| TC07 | After restoration, use a fresh controlled order. | Setup matches the baseline and observed behavior matches the expected prior behavior. |

For each executed case, retain the case ID, operator, timestamp and time zone, environment and release, setup before-and-after captures, predefined indicators, process/version/step, expected compensation, order/revision/line, old and new values, submission confirmation or error, fulfillment observations, and downstream evidence in the approved change record. Record **Pass**, **Fail**, or **Blocked**, actual versus expected behavior, defects and responsible owners, recovery status, and disposition of affected orders. Mark a case **Blocked** when access, missing data, or an unmet dependency prevents evaluation; do not substitute an expected result for an observation. Have the functional owner record acceptance or required follow-up after reviewing the applicable results.
