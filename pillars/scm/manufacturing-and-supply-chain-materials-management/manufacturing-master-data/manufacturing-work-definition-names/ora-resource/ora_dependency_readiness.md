# Work Definition Names — Dependency Readiness

## Public references and compatibility

- [Oracle Fusion Cloud Manufacturing 26D: Work Definition Names](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faumf/work-definition-names.html) explains the business fields and usage restrictions.
- [Oracle Fusion Cloud SCM 26D: WorkDefinitionName business object](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fabsm/bo_oraScmCoreManufacturingWorkDefinition_WorkDefinitionName.html) lists the business type codes. This is a different API model; do not copy its field names, children or write contract into V2.

The public references support business terminology. They do not establish a public compatibility guarantee for workDefinitionNamesV2. Verify its availability, operations and schema in the selected environment through the owning workflow. The rules below distinguish service behavior, request preparation and adopted FSCR policy. They are not evidence of successful create/update testing.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Existing update target | Establish original identity when updating |
| 2 | Usage evidence | Require usage only for actual code, start-date or planning changes |
| 3 | Applicable policy checks | Evaluate actual changes in design enforcement; creation has no existing-record dependency |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| WDNAME.CODE_IDENTITY | Original-code identity | Conditional | Update without original ID or authorized reconciliation | Verify | Fusion V2 response | find_work_definition_name_by_code | Identify intended record | Supply original code | Existing ID and original values |
| WDNAME.ID_IDENTITY | Immutable identity | Conditional | Update with original ID | Verify | Fusion V2 response | find_work_definition_name_by_id | Preserve identity across changes | Supply original ID | Existing ID and original values |
| WDNAME.USAGE | Reference usage | Conditional | Actual code, start-date or planning change on update | Verify | Fusion V2 IsUsedInWorkDefinition | verify_work_definition_name_usage | Distinguish referenced and unreferenced names | Resolve target first | Usage state and original values |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Applicable identity/evidence is available | No dependent creation |
| Not applicable | New create has no existing target dependency | No lookup |
| Blocked | Required identity or applicable usage evidence is unavailable | Stop preparation |

There is no duplicate-existence dependency for new names. No plant, item, resource or work-center setup is introduced. Seeded status is not exposed by V2, so do not infer it from a code prefix, a single known seed or the usage flag. Design enforcement owns the refusal of code/end-date changes while authoritative non-seeded status is unavailable; it is not a dependency for other changes.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WDNAME.DEPENDENCIES | step | 30 | resolve_dependency | passed->WDNAME.DEFAULTS;failed->WDNAME.ERROR | WDNAME.LOOKUPS | stop | Evaluate applicable identity and usage evidence; no speculative creation dependencies |
