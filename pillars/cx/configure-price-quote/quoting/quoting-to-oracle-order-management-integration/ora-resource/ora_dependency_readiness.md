# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Offerings | Configure Price Quote and Order Management must be enabled. |
| 2 | CPQ provisioning | CPQ Setup Assistant must have completed and the Standard Process must contain current Book Order artifacts. |
| 3 | Generic Integration | Check the named CPQ Generic Integration; stage it through Data Loader only when absent. |
| 4 | Native flow prerequisites | Require current administrator confirmation through verify_native_flow_prerequisites_confirmation; this task does not configure missing prerequisites. |
| 5 | OM process assignment rule | An Order Management administrator must create or confirm the active, deployed Oracle CPQ orchestration rule manually. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| CPQOM.OM_OFFERING | Order Management offering | Yes | Every request | Verify | Fusion FSM offering details | verify_order_management_offering | OM must be enabled before native integration setup | Resolve through the routed offering workflow if absent | OM offering state |
| CPQOM.CPQ_OFFERING | Configure Price Quote offering and CPQ Setup Assistant | Yes | Every request | Verify | Fusion FSM offering details and CPQ provisioning evidence | verify_cpq_offering | CPQ Book Order artifacts are required | Complete CPQ provisioning if unavailable | CPQ offering state and artifact readiness |
| CPQOM.GENERIC_INTEGRATION | Fusion Account Integration | Yes | Every native CPQ--OM setup validation | Verify | CPQ IntegrationVendors collection and read-only Integration Center confirmation | verify_fusion_account_integration | Prevent duplicate creation and prove the saved connection is usable | If absent, prepare the documented Data Loader source; if ambiguous, stop; if present, require the active Run Book URL and enabled state | Presence, target URL, enabled state |
| CPQOM.NATIVE_FLOW_PREREQUISITES | Native flow prerequisites | Yes | Final native Book Order setup readiness | User confirmation | Administrator evidence for the active environment | verify_native_flow_prerequisites_confirmation | Account connection readiness alone does not prove full native flow readiness | Supply the current guide prerequisite confirmation; missing setup requires a separately routed workflow | Confirmation and safe evidence refs |
| CPQOM.OM_PROCESS_ASSIGNMENT_RULE | Oracle CPQ process assignment rule | Yes | Native CPQ--OM Book Order | User confirmation | Order Management administrator confirmation | verify_om_process_assignment_rule_user_confirmation | Routes Oracle CPQ source orders to the required orchestration definition | Confirm the exact name, condition, action, active state, and deployed state through the documented OM UI | Confirmation or manual-task blocker |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Blocked | A required offering or CPQ prerequisite is absent | Lookup only; create or enable through the separately routed workflow |
| Ready | Offerings and Commerce setting are compliant, and the single named Generic Integration has the active Run Book URL and is confirmed enabled; native flow prerequisites are confirmed | Lookup only |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQOM.CHECK_READINESS | step | 50 | resolve_dependency | ready->CPQOM.VERIFY_OM_PROCESS_ASSIGNMENT_RULE;blocked->CPQOM.HANDLE_ISSUE | CPQOM.CHECK_GENERIC_INTEGRATION | stop | Before manual OM process-assignment-rule confirmation; require verify_native_flow_prerequisites_confirmation |
| CPQOM.VERIFY_OM_PROCESS_ASSIGNMENT_RULE | step | 75 | resolve_dependency | confirmed->CPQOM.PROCESS_ASSIGNMENT_RULE_READY;manual_action_required->CPQOM.HANDLE_ISSUE | CPQOM.CHECK_READINESS | stop | Before native CPQ--OM orders are submitted |
