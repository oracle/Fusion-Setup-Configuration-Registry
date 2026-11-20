# Work Definition Names — Reference Lookups

## Public references and compatibility

- [Oracle Fusion Cloud Manufacturing 26D: Work Definition Names](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faumf/work-definition-names.html) explains the business fields and usage restrictions.
- [Oracle Fusion Cloud SCM 26D: WorkDefinitionName business object](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fabsm/bo_oraScmCoreManufacturingWorkDefinition_WorkDefinitionName.html) lists the business type codes. This is a different API model; do not copy its field names, children or write contract into V2.

The public references support business terminology. They do not establish a public compatibility guarantee for workDefinitionNamesV2. Verify its availability, operations and schema in the selected environment through the owning workflow. The rules below distinguish service behavior, request preparation and adopted FSCR policy. They are not evidence of successful create/update testing.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_work_definition_name_by_code | Update identified by original code, or authorized uncertain-create reconciliation | Original WorkDefinitionCode | GET /fscmRestApi/resources/11.13.18.05/workDefinitionNamesV2 with encoded q=WorkDefinitionCode='<escaped original code>' | WorkDefinitionNameId,WorkDefinitionCode,WorkDefName,WorkDefNameDescription,WorkDefinitionType,UsedInPlanningFlag,EffectiveFromDate,EffectiveToDate,IsUsedInWorkDefinition | Exact intended identity; finish pagination; do not add an active-only or organization filter | Unique existing ID and current business values, including nulls; usage if returned | Zero: unresolved target, not proof a prior write failed; multiple: request disambiguation; never select first |
| find_work_definition_name_by_id | Update using immutable identity, including proposed code change | Original WorkDefinitionNameId | GET /fscmRestApi/resources/11.13.18.05/workDefinitionNamesV2 with finder=PrimaryKey;WorkDefinitionNameId=<encoded original ID> | WorkDefinitionNameId,WorkDefinitionCode,WorkDefName,WorkDefNameDescription,WorkDefinitionType,UsedInPlanningFlag,EffectiveFromDate,EffectiveToDate,IsUsedInWorkDefinition | Exact original ID; compare supplied original code if also present | Unique existing identity and current business values, including nulls; usage if returned | Stop on absent, ambiguous or conflicting identity |
| verify_work_definition_name_usage | Actual code, start-date or planning change on update; reuse adequate target-read evidence first | Original WorkDefinitionNameId | GET /fscmRestApi/resources/11.13.18.05/workDefinitionNamesV2 with finder=PrimaryKey;WorkDefinitionNameId=<encoded original ID> | WorkDefinitionNameId,WorkDefinitionCode,EffectiveFromDate,UsedInPlanningFlag,IsUsedInWorkDefinition | Exact ID; interpret IsUsedInWorkDefinition string Y as used and N as unused; any other representation is unknown | Original protected values and usage state; Y includes references without an active-date restriction | Mark usage unknown if missing, null or outside Y/N; do not coerce Boolean or 1/0. Design enforcement blocks only changes requiring usage; never hide identity, authorization or transport failures |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Ordinary new create | Do not run duplicate-code or duplicate-name existence checks. Fusion owns uniqueness, including transaction-time conflicts |
| Update identity | Prefer original ID when supplied; otherwise original code. Never use proposed new code as the original target |
| Conditional usage read | Resolve target first. Use the actual-change comparison owned by design enforcement to determine whether usage is needed; do not query usage for create, unchanged protected values, or only display-name/description/end-date changes |
| Missing returned attributes | Preserve the distinction between an omitted response attribute and an explicit null; a missing comparison value cannot establish that the request is unchanged |
| Seeded status | No seeded-status resolver is available in this resource contract. Do not invent an endpoint or accept an unverified supplied flag; design enforcement restricts the affected changes until an authoritative resolver is separately authored |
| Usage representation | IsUsedInWorkDefinition is a returned Y/N string; UsedInPlanningFlag is JSON boolean. Keep these contracts separate |
| Predicate choice | WorkDefNameDescription, WorkDefinitionTypeMeaning and IsUsedInWorkDefinition must not be q predicates |
| Type selection | The supported type codes are known; no speculative type-lookup endpoint is required. Type policies are owned by ora_design_enforcement.md |
| Runtime reads | Use the selected core read client and environment, OAuth and REST-Framework-Version: 9; encode user values and follow pagination |
| Idempotency | A reconciliation read identifies state; it is not a second uniqueness validator and does not make every duplicate a successful create |

## Lookup scope

These are task-owned runtime contracts. The caller may reuse matching evidence obtained earlier in the same run. No organization scope, default active filter, translation child or DFF child is assumed.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WDNAME.LOOKUPS | step | 20 | reference_lookup | passed->WDNAME.DEPENDENCIES;failed->WDNAME.ERROR | WDNAME.INPUT | stop | Resolve only applicable target/usage reads; ordinary create has no lookup |
