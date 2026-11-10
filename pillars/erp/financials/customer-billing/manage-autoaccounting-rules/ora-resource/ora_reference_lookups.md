# Manage AutoAccounting Rules Reference Lookups


All resolvers are read-only or local normalization. The exact-task FSM resolver remains authoritative.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_auto_business_unit | BuName is supplied | Fresh exact-task BuName values | Require one exact case-insensitive business-unit name | Canonical BuName | Block zero matches; block multiple matches and request exact scope |
| resolve_auto_account_type | Type or label is supplied | Seeded AUTOGL_TYPE codes and meanings | Require one exact code or unambiguous label | Canonical Type code | Block unsupported or ambiguous values and list evidenced choices |
| resolve_auto_segment | Segment or SegmentNum is supplied | Fresh child rows for selected BuName plus Type | Require one exact Segment and SegmentNum pair | Canonical Segment and SegmentNum | Block missing, duplicate, or inconsistent identity |
| resolve_auto_source | A table-derived segment is requested | Evidenced source labels/codes and selected Type | Require one compatible source | Canonical TableName; blank Constant | Block unsupported or incompatible source choices |
| resolve_auto_constant | A constant-derived segment is requested | Exact business unit, segment, and constant | Require TableName blank and one value accepted by deployed value set | Exact Constant; blank TableName | Block a missing, ambiguous, or invalid constant |
| resolve_auto_dff | Any DFF value is requested | Entity, context, deployed mapping, and value | Require one exact context and AttributeN mapping | AttributeCategory and mapped AttributeN | Block missing/multiple mappings; otherwise omit DFF change |

## Fixed Value Contracts

| Business Value | Package Value | Applies To |
|---|---|---|
| Factored Bills Receivable | BR_FACTOR | Type |
| Bills Receivable | BR_REC | Type |
| Remitted Bills Receivable | BR_REMITTANCE | Type |
| Unpaid Bills Receivable | BR_UNPAID_REC | Type |
| Charges | CHARGES | Type |
| Deferred Tax | DEFERRED_TAX | Type |
| Freight | FREIGHT | Type |
| Prepayment | ORA_PREPAYMENT | Type |
| Receivable | REC | Type |
| Revenue | REV | Type |
| AutoInvoice Clearing | SUSPENSE | Type |
| Tax | TAX | Type |
| Unbilled Receivable | UNBILL | Type |
| Unearned Revenue | UNEARN | Type |
| Transaction Types | RA_CUST_TRX_TYPES | TableName |
| Salesperson | RA_SALESREPS | TableName |
| Bill-to Site | RA_SITE_USES | TableName |
| Standard Lines | RA_STD_TRX_LINES | TableName |
| Tax | RA_TAXES | TableName |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AAR.LOOKUP_REFERENCES | decision | 3 | evaluate_result | resolved->AAR.APPLY_DEFAULTS;not_applicable->AAR.APPLY_DEFAULTS;blocked->AAR.RETURN_ISSUES | AAR.RESOLVE_DEPENDENCIES | stop | Evaluate task-local and fresh exact-task resolver results for identity, source, constant, or DFF values |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-CODE-AUTOGL-LOOKUP; SRC-CODE-VALUE-SOURCE-VVO | Seeded account-type and source contracts |
| SRC-CODE-BO-REFERENCES; SRC-CODE-UI-AM-IMPL | Business-unit and FSM reference resolution |
| SRC-CODE-SEGMENT-VO; SRC-CODE-SEGMENT-EO; SRC-FSM-PACKAGE | Segment, constant, DFF, and environment values |
