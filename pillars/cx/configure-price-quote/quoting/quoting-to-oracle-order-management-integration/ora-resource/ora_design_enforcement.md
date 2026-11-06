# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm OM routing | An OM administrator confirms the active, deployed Oracle CPQ process assignment rule routes Oracle CPQ source orders to DOO_ProductFulfillmentWithIntegratedSubscription. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Configuring OM orchestration | Manual task | verify_om_process_assignment_rule_user_confirmation | The CPQ process assignment rule is absent, inactive, undeployed, or has a different condition/action | In Manage Process Assignment Rules for Sales Orders, create or correct the documented rule, activate it, and deploy it | No |
| Planning CPQ Book Order | Blocker | | Current Book Order artifacts are unavailable in the CPQ Standard Process | Complete CPQ Setup Assistant or provisioning first | No |
| Planning CPQ Book Order | Blocker | get_populate_bom_part_attributes | The BOM-part attribute setting is not Yes | Prepare the exact CpqCommerceSettings Data Loader source and use the Core Data Loader approval flow before changing it | No |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| get_populate_bom_part_attributes | Before Book Order integration configuration | Current Commerce setting value | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
