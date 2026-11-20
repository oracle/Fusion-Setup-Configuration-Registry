# Design Enforcement

## Source Boundary

This guidance is derived from Oracle's [How You Manage Work Areas](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faumf/how-you-manage-work-areas.html). It defines business scope only; core.data-loader owns source validation and execution for the selected import mode.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Existing plant validation | Confirm that the selected manufacturing plant exists in Fusion before creating a work area. |
| 2 | Centralized Data Loader boundary | Submit only the immutable source validated for the selected import mode through core.data-loader after approval. |

## Design Rules

| Rule ID | Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|---|
| WA.DESIGN.EXISTING_PLANT | Creating a work area | Blocker | | The selected manufacturing plant is absent or cannot be confirmed in Fusion. | Select a valid existing manufacturing plant before creating the work area. | Yes |
| WA.DESIGN.CREATE_VALUES | Creating or updating a work area | Blocker | | Work Area Name or Work Area Code is absent, or a supplied Inactive Date is not later than the current date. | Provide Name and Code; leave Inactive Date blank or provide a future date. | Yes |
| WA.DESIGN.FSM_ROUTE | Every FSM import | Blocker | | The source was not validated through core.data-loader or differs from the approved immutable artifact. | Use the centrally validated FSM source and approval workflow. | Yes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WA.DESIGN | step | 4 | design_enforcement | ok->WA.DONE;failure->WA.FAILED | WA.DEPENDENCIES | stop | Work-area design and selected-mode import review |
