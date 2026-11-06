# Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Target environment | Canonical Fusion environment identity | Stop | Provide the target Fusion environment before planning configuration | Every request | |
| Integration scope | Book Order requirement | Stop | Confirm the intended CPQ to OM flow | Every request | |
| CPQ readiness | CPQ offering enabled and CPQ Setup Assistant completed | Stop | Complete the prerequisite setup or provide verified readiness evidence | Every request | verify_cpq_offering |
| OM readiness | Order Management offering enabled | Stop | Enable the offering through its separately approved implementation workflow | Every request | verify_order_management_offering |
| Commerce setting access | CPQ OAuth scope assigned to the target client | Stop | Confirm CPQ scope assignment before the Commerce settings GET | Checking or changing the BOM-part attribute setting | |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| The selected environment does not have both offerings enabled | Blocked | Do not prepare CPQ--OM configuration; resolve the missing offering first | verify_order_management_offering |
| CPQ Setup Assistant or required Book Order artifacts are unavailable | Blocked | Complete CPQ provisioning before integration configuration | verify_cpq_offering |
| The Commerce setting is not Yes | Approval required | Prepare the exact CpqCommerceSettings source; validate the final immutable archive and complete Task Hook validation and approval before upload and initiation | get_populate_bom_part_attributes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQOM.VALIDATE_SCOPE | step | 10 | validate_input | valid->CPQOM.VERIFY_OM_OFFERING;invalid->CPQOM.HANDLE_ISSUE | none | stop | Before CPQ to OM integration planning or configuration |
