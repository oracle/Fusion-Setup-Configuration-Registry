---
task_code: "DOO_MANAGE_TASK_TYPES"
task_name: "Manage Task Types"
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

# Manage Task Types

- **Task code:** `DOO_MANAGE_TASK_TYPES`
- **Purpose:** Review and maintain task types that group tasks and services for status management, jeopardy, orchestration process definition, and runtime behavior.
- **Execution rule:** The user completes the approved change manually in Oracle Fusion **Setup and Maintenance**, on **Manage Task Types** and the related status setup pages, and performs manual validation in the applicable Oracle Fusion **Order Management** work area, with no API, import, automated configuration, or browser automation.

Use the [standard shared manual workflow](../../../../shared/common/manual-tasks/SKILL.md).

Provide manual steps directly from this task using the user’s supplied values. Stay within the documented guidance, identify missing details, and do not create separate guides or project artifacts solely to explain the steps.

## Manual steps

1. Confirm the approved change reference and execution path: review existing setup, add a task under an existing type, or create a custom type. Record the environment and tenant release, functional and integration owners, task type, task code/name/display name, required service operations, status mappings and terminal conditions, affected process/version/steps, integration and routing design, and rollback owner. Start in a nonproduction environment. Confirm that the supplied procedure applies to the tenant release and enabled controls. Resolve missing values or conflicting guidance with the relevant owner before editing; do not adopt example identifiers as required values.
2. Confirm access to **Manage Task Types** and separate access to test orders and fulfillment details. The related privilege is named **Manage Orchestration Task Types**; have the security administrator verify access rather than assuming a similarly named infrastructure privilege is sufficient. Identify processes that share the target setup and assess the change's effect on revisions, cancellation, holds, and other relevant business flows. Prepare a simple test order and agree with the integration owner on a controlled fulfillment test, expected initial/intermediate/terminal outcomes, and an observation window.
3. Open **Setup and Maintenance** and search for **Manage Task Types**. Task-search navigation depends on your tenant. Locate the exact type using the available search controls. **View > Query by Example**, entering **Task Type**, and pressing **Enter** are documented for the asset-management example; use those controls only where available. Capture the current tasks, services, identifiers, related status setup, and process references as a restoration baseline. If the wrong record appears, clear the search filters and recheck its identifiers. For review-only work, compare against the approved design, record discrepancies, and proceed to the applicable manual validation without changing setup.
4. Only when a new custom type is approved, select **Actions > Add Custom**, enter the approved **Task Type**, and leave the field. Inspect the generated **Create** and **Inbound** service rows and compare their names and operation codes with the design. Include other operations only where required and supported by the approved integration. If you rename the type before saving, align its service codes manually: renaming does not refresh them, and saved service codes become read-only. Create at least one task and complete the approved status setup in the following steps before saving the custom type.
5. For an approved task addition, select the intended parent type. In its details, use **Tasks > Actions > Add Row** and enter the approved **Code**, **Name**, and **Display Name**, if those controls are available for that type. These controls are documented for **DOO_AssetManagement**; they do not establish that every predefined type is editable. Use your approved identifiers, not the example type. Save with the applicable control; the asset example uses **Save and Close**. Reopen and confirm the task's exact identity and parent. If saved identifiers differ from the plan, stop and assess dependent references before further changes.
6. In **Setup and Maintenance**, open **Manage Status Values**. Review the required display names in **Status Codes**, then use **Task Types** to assign the approved status codes to the target type. Associate external-system statuses with the relevant fulfillment task type. Commit only approved changes using the tenant's available controls and reopen to verify them; the supplied overview does not specify row-entry or save-control labels.
7. Open **Manage Task Status Conditions**, select the target type, and review its **Status Conditions**. **Internal Status Value** is the status received from the fulfillment system; **Display Status Value** is the status presented to users; **Mark as Complete** treats the task as done when that condition is reached. Maintain only the approved mappings and completion indicators. Do not mark an acknowledgment or intermediate response as terminal simply to advance a test. Save using the tenant's available control and recheck the persisted values with the functional and integration owners.
8. For a new custom type, select **Save** after its required task and status setup are complete, then reopen and compare the type, tasks, services, operation codes, and identifiers with the approved design. For an existing type, reopen after the applicable save action and compare with the baseline. Capture validation messages rather than repeating unrelated edits. A saved definition alone does not establish runtime readiness.
9. Before runtime testing, obtain confirmation from the responsible owners that the deployed process version references the intended type, task, and service; the test order will use that process; the configured interface reaches the intended fulfillment system; and responses correlate to the correct order line and task instance. Confirm expected wait and exit behavior and completion of any separately required process or integration deployment. Integration construction, compensation authoring, and process deployment remain separate dependency activities. If this trace is incomplete, record the blocker and pause runtime testing.
10. In your tenant's **Order Management** work area, manually create the controlled order with the prepared customer, item, business unit, and quantity. Submit once and capture the order, revision, and fulfillment-line identifiers. Open the available fulfillment and orchestration details, record the actual navigation, and confirm the actual process/version before evaluating the target step. Have the integration owner confirm receipt of the corresponding request. Within the agreed controlled test, manually refresh and inspect the displayed outcome for each planned intermediate and terminal response, then verify progression to the expected next step and the downstream business result. This procedure does not perform integration operations; if the required fulfillment interaction cannot be exercised under the agreed test, keep the runtime case **Blocked**.
11. If no request is observed, compare actual process assignment, step execution, service reference, and routing with the approved design. For an incorrect displayed status, compare the response with assigned status values and conditions. For continued waiting or premature completion, have the owners check response correlation, completion indicators, and process exit expectations. Capture the exact error, timestamp and time zone, task identity, process/version/step, order and line, and expected versus actual outcome. Before any recovery retry, have the fulfillment owner inspect transaction evidence and confirm the agreed recovery procedure avoids duplicate business work.
12. If restoration is required, stop further test submissions and identify affected orders. Restore supported editable values against the baseline through the setup UI and coordinate dependent process and integration restoration with their owners. Remove a newly created record only if a supported UI action exists and the owners confirm that no required reference or active transaction depends on it; otherwise leave it unused and record the cleanup decision. Do not assume a universal deactivate, delete, or publish control. Reopen to verify restoration and run a fresh controlled validation. Review already affected orders individually; restoring setup does not demonstrate reversal of completed fulfillment work.

## Manual validation guidance

Start each case as **Not Executed**. Use separate controlled orders or clearly identified test runs, and mark irrelevant cases **Not Applicable** with a reason. For review-only work, record the design comparison and do not imply a configuration change or runtime test was performed.

| Case | Manual check | Acceptance criterion |
| --- | --- | --- |
| TC01 | Reopen persisted setup. | Type, task, services, and identifiers match the approved design, with only intended changes from baseline. |
| TC02 | Inspect actual process selection. | The test uses the expected process/version and task references. |
| TC03 | Confirm outbound receipt with the integration owner. | The intended system received the expected operation for the correct line. |
| TC04 | Inspect the planned intermediate response outcome. | Displayed status and continued waiting or progression match the design. |
| TC05 | Inspect the planned terminal response outcome. | Completion, next-step progression, and downstream outcome match the design. |
| TC06 | Observe an agreed controlled integration failure and recovery. | The failure is visible and approved recovery completes without unintended duplicate business work. |
| TC07 | Manually test a supported revision or cancellation, where applicable. | Behavior matches the process and integration owners' expectation. |
| TC08 | Manually test a supported hold and release, where applicable. | Order Management and fulfillment behavior match the design. |
| TC09 | Check representative existing processes sharing the setup. | Their observed results remain consistent with their owners' expectations. |
| TC10 | Reopen restored configuration and test a fresh controlled order. | Supported restored values match baseline and the expected prior behavior is observed. |

Define applicable specialized charge, asset, subscription, or partial-fulfillment tests before accepting those implementations. For each executed case, retain the case ID, operator, timestamp and time zone, environment/release, before-and-after setup captures, process/version/step, order/revision/line, correlated request and response evidence, expected and observed outcomes, and defect references in the approved change record. Mask credentials and sensitive customer data. Record **Pass**, **Fail**, or **Blocked**, assign unresolved discrepancies to owners, and document rollback status and affected-order disposition. A saved setup alone is not a passed fulfillment test; keep cases blocked when required access, data, dependencies, or integration evidence are unavailable. Have the functional owner record acceptance or required follow-up based on the observed applicable results.
