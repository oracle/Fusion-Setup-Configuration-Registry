# Billing Types Create Design Rules

## Source

The live billingTypes describe confirms POST and its category/type lookup sources. Oracle's entity-specific published table reference documents unique index RCL_BILLING_TYPES_U2 on BILLING_TYPE_CODE alone: https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25c/oedsc/rclbillingtypes-26231.html . The 26B SCM tables catalog is available at https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/index.html ; its entity-specific successor page could not be resolved during this review. The cited uniqueness reference is therefore explicitly 25C, supplemented by current-environment registration/describe and complete duplicate reads; no quarterly release is inferred from API version 11.13.18.05.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BILLING_TYPES.CHECK_CREATE_UNIQUENESS | decision | 18 | design_enforcement | passed->BILLING_TYPES.CREATE_GATE;blocked->BILLING_TYPES.RETURN_ISSUES | BILLING_TYPES.READ_CREATE_DUPLICATES | stop | POST only: require duplicate count zero before source preparation/preview |

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Consume authoritative duplicate evidence | Require successful complete check_billing_type_duplicate output from the selected environment. |
| 2 | Enforce code uniqueness | Only zero existing exact BillingTypeCode matches permits POST preparation. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| POST create | Error | check_billing_type_duplicate | Any existing record with the resolved BillingTypeCode, regardless of category or enabled state; or incomplete/failed duplicate evidence | Select a genuinely unused registered billing type. If an existing mapping should change, require a separate explicit request and supported update contract. Never turn POST into upsert or overwrite a mapping. | No automatic correction |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| check_billing_type_duplicate | Every POST before source preparation and during captured-source validation | Complete exact-code match count; conflict identity/category held only in memory | ora_reference_lookups.md |

This gate does not create lookup values, change an existing category, or authorize a write. No customer values or record identifiers are persisted here.
