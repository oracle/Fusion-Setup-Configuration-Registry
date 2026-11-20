# Work Definition Names — Defaults

## Public references and compatibility

- [Oracle Fusion Cloud Manufacturing 26D: Work Definition Names](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faumf/work-definition-names.html) explains the business fields and usage restrictions.
- [Oracle Fusion Cloud SCM 26D: WorkDefinitionName business object](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fabsm/bo_oraScmCoreManufacturingWorkDefinition_WorkDefinitionName.html) lists the business type codes. This is a different API model; do not copy its field names, children or write contract into V2.

The public references support business terminology. They do not establish a public compatibility guarantee for workDefinitionNamesV2. Verify its availability, operations and schema in the selected environment through the owning workflow. The rules below distinguish service behavior, request preparation and adopted FSCR policy. They are not evidence of successful create/update testing.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| WorkDefinitionType | STANDARD | Omitted on create; leave omission for Fusion | No | |
| UsedInPlanningFlag | false | Omitted on create; leave omission for Fusion | No | |
| WorkDefinitionNameId | Framework-generated identity; confirm generation in target-environment acceptance testing | Omitted on create | No | |

EffectiveFromDate has no V2 create default. Request an explicit intended date; do not copy a UI current-date default or use the agent clock. No start-date-today/future restriction is added.

Leave optional description/end date omitted when unspecified. On update, omit unchanged fields rather than resending create defaults. An explicit null is distinct from omission; verify supported clearing semantics before a clear. Use JSON true/false for UsedInPlanningFlag, never its internal Y/N representation. Code/name normalization remains server-owned; preserve intended casing.

The apply_default node records server-default intent only. It does not generate IDs, silently change dates, or resolve conflicting type/planning choices. Design enforcement owns the type/planning and actual-change policies.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WDNAME.DEFAULTS | step | 40 | apply_default | passed->WDNAME.DESIGN;failed->WDNAME.ERROR | WDNAME.DEPENDENCIES | stop | Preserve server-default omissions and explicit user intent |
