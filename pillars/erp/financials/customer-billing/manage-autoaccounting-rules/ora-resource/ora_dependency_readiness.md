# Manage AutoAccounting Rules Dependency Readiness


## Dependency Rules

| Dependency | Required When | Ready Evidence | Blocking Outcome | Resolver |
|---|---|---|---|---|
| Receivables-enabled business unit | Every operation | One exact BuName in fresh exact-task evidence | Ask for a valid exact business unit | resolve_auto_business_unit |
| AutoAccounting account type | Every operation | One seeded supported Type code | Ask the implementor to choose one supported account type | resolve_auto_account_type |
| Chart of accounts and segment structure | Every operation | Complete current Segment and SegmentNum inventory for the business unit | Request fresh evidence; build no candidate | resolve_auto_segment |
| Account-type/source compatibility | A table source is requested | Source is permitted for the selected account type | Ask for a permitted source or constant | resolve_auto_source |
| Accounting value-set membership | A constant is requested | Constant is valid for the exact deployed segment value set | Ask for a valid constant | resolve_auto_constant |
| Deployed DFF definition | A DFF value is requested | Exact context, AttributeN mapping, and value contract | Ask for evidence or omit the DFF change | resolve_auto_dff |

The skill never creates business units, ledgers, charts of accounts, value sets, or DFF deployments.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AAR.RESOLVE_DEPENDENCIES | decision | 2 | resolve_dependency | ready->AAR.LOOKUP_REFERENCES;blocked->AAR.RETURN_ISSUES | AAR.VALIDATE_INPUT | stop | After input validation |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-CODE-UI-AM-IMPL; SRC-CODE-UI-HEADER-VO | Business-unit context and account-type selection |
| SRC-CODE-UI-SEGMENT-VO; SRC-CODE-SEGMENT-EO | Segment identity and source/constant behavior |
| SRC-DOC-AUTOACCOUNTING-26D; SRC-FSM-PACKAGE | Prerequisites and target-environment identities |
