---
task_code: "DOO_MANAGE_TASK_STATUS_CONDITIONS"
task_name: "Manage Task Status Conditions"
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

# Manage Task Status Conditions

- **Task code:** `DOO_MANAGE_TASK_STATUS_CONDITIONS`
- **Purpose:** Review and maintain the mapping from a received internal task status to its displayed status and the conditions that complete the task, then verify the observed task and process behavior.
- **Execution rule:** The user completes the approved change manually in Oracle Fusion **Setup and Maintenance**, on **Manage Task Status Conditions**, and performs manual validation in the applicable Oracle Fusion **Order Management** user interface identified by the task guidance, with no API, import, automated configuration, or browser automation.

Use the [standard shared manual workflow](../../../../shared/common/manual-tasks/SKILL.md).

Provide manual steps directly from this task using the user’s supplied values. Stay within the documented guidance, identify missing details, and do not create separate guides or project artifacts solely to explain the steps.

## Manual steps

1. Confirm the approved change reference, environment and tenant release, functional and integration owners, exact target task type, current and proposed conditions, affected process/version/steps, expected intermediate and terminal behavior, and rollback owner. Start in nonproduction and confirm access to the setup page and test orders. Confirm that the supplied procedure applies to the tenant release and available controls. Resolve missing values or conflicting guidance with the owners before editing.
2. Obtain the approved response-to-display mapping and inventory all processes sharing the task configuration. Agree on regression coverage, a controlled test order, integration-owner participation, and an observation window. Capture baseline conditions and dependent process settings. Confirm that prerequisite values and assignments are available through **Manage Status Values**. Preserve protected final process and line conditions for predefined shipping and invoicing flows; changing a task mapping does not remove that restriction.
3. Open **Setup and Maintenance**, then **Manage Task Status Conditions**, using the tenant's available task-search navigation. Select the intended task type. **Return** in the **Type** column is an example, not a prescribed target. If the page or target is unavailable, verify setup access, search context, and task identity. For a review-only change, compare existing conditions with the approved design and proceed to applicable manual validation without editing.
4. Review the target's **Status Conditions**. **Internal Status Value** is the status received from the fulfillment system through the task; **Display Status Value** is the status shown to the user; **Mark as Complete** indicates that reaching the condition completes the task. Add or modify only the approved condition using the supported tenant controls. The supplied procedure does not specify every add-row or save-control label. If the planned selection is missing, check prerequisite values and assignments through **Manage Status Values**; do not select an unrelated substitute.
5. Before saving, compare each applicable response scenario with its approved expectation: acknowledgment, work in progress, successful completion, supported cancellation, and supported failure. For each, confirm the exact received code, intended label, whether it should finish the task, and expected process observation. These scenarios are business categories, not prescribed status codes. Check case-sensitive identifiers against the integration contract where applicable. Have the functional and integration owners confirm whether each response is intermediate, terminal, or an error requiring recovery. Confirm wait-step exit and next-step dependencies with the process owner; process-level condition logic remains separate configuration. Do not alter a completion indicator merely to advance a test.
6. Save with the tenant's available control, record its actual label, then reopen the exact task type and condition. Compare internal status, display status, completion indicator, and unrelated rows against the approved change and baseline. Capture validation messages or discrepancies and resolve them before runtime testing.
7. In the tenant's **Order Management** work area, prepare a simple controlled order that reaches the relevant task without unrelated holds or data errors. Submit once and capture the order, revision, fulfillment line, and task-instance identifiers where available. Open the available fulfillment and orchestration details and record actual navigation. Confirm the actual process version and target step, and have the integration owner confirm the corresponding outbound request and correlation identifiers.
8. During the agreed controlled response test, manually refresh the order after the planned intermediate response and capture task behavior, displayed wording, and process position. Compare each with the predefined expectation and investigate unexpected advancement before continuing. After the planned terminal response for the same controlled execution, refresh and inspect task completion, next step, and downstream business outcome. Retain correlated request/response evidence, timestamps, and UI captures from the integration owner and your observations. If a required response cannot be exercised, record **Blocked**. A displayed label does not establish that all downstream work completed.
9. If the wrong label appears, compare the received value, selected task, and persisted mapping. For premature completion, inspect the completion indicator and response sequence; for continued waiting, confirm response receipt and correlation, then review task settings and process exit logic with the owners. Stop testing if a response affects another line and have the owners resolve correlation before further response tests. Preserve task and process observations separately when their outcomes differ. Before an agreed recovery retry, have the fulfillment owner inspect transaction evidence for duplicate-work risk.
10. If restoration is required, stop further submissions and response tests and identify affected executions. Restore supported editable conditions from baseline through the setup UI. Remove newly added rows only through supported controls after the owner reviews dependencies. Coordinate restoration of separately changed values or process configuration with their owners. Do not assume a generic delete, deactivate, publish, or replay action. Reopen and compare with baseline, run a fresh controlled restoration test, and review affected orders individually; configuration restoration does not establish reversal of completed external work or reprocessing of earlier responses.

## Manual validation guidance

Start each case as **Not Executed**. Use separate orders or clearly identified test executions as appropriate. Mark irrelevant cases **Not Applicable** with a reason. Define expected negative-test behavior with the integration owner before executing that controlled scenario.

| Case | Manual check | Acceptance criterion |
| --- | --- | --- |
| SC01 | Reopen the saved condition. | Internal status, display status, and completion indicator match the approved change without unrelated modifications. |
| SC02 | Inspect an intermediate response outcome. | Displayed label and progression match the predefined expectation. |
| SC03 | Inspect a terminal response outcome. | Completion and next-step behavior match the predefined expectation. |
| SC04 | Observe another supported mapped outcome. | Cancellation or failure behaves as designed. |
| SC05 | Observe an approved unexpected-response case, if in scope. | Handling matches the agreed observable expectation; no universal error text is assumed. |
| SC06 | Test a representative process sharing the task configuration. | Existing behavior still meets its baseline expectation. |
| SC07 | Inspect approved recovery. | Recovery completes without unintended duplicate business work. |
| SC08 | Reopen restored setup and test a fresh controlled order. | Conditions match baseline and expected prior behavior is observed. |

Retain the case ID, operator, timestamp and time zone, environment/release, exact task type and before-and-after conditions, process/version/step, order/revision/line and task-instance references, correlated responses, expected and actual outcomes, and defect references in the approved change record. Mask credentials and sensitive customer data. Record **Pass**, **Fail**, or **Blocked**, and keep cases blocked when access, missing data, dependencies, or response evidence prevent evaluation. Distinguish review-only findings from unexecuted runtime tests. Assign discrepancies to owners, document rollback status and affected-order disposition, and have the functional owner record acceptance or required follow-up after reviewing actual task progression and downstream results.
