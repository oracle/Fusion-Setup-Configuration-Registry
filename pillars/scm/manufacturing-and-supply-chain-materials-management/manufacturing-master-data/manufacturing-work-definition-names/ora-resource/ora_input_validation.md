# Work Definition Names — Input Validation

## Public references and compatibility

- [Oracle Fusion Cloud Manufacturing 26D: Work Definition Names](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faumf/work-definition-names.html) explains the business fields and usage restrictions.
- [Oracle Fusion Cloud SCM 26D: WorkDefinitionName business object](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fabsm/bo_oraScmCoreManufacturingWorkDefinition_WorkDefinitionName.html) lists the business type codes. This is a different API model; do not copy its field names, children or write contract into V2.

The public references support business terminology. They do not establish a public compatibility guarantee for workDefinitionNamesV2. Verify its availability, operations and schema in the selected environment through the owning workflow. The rules below distinguish service behavior, request preparation and adopted FSCR policy. They are not evidence of successful create/update testing.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Create intent | WorkDefinitionCode, WorkDefName and an explicit EffectiveFromDate | Ask for missing business input | Collect the intended code, display name and date; do not derive code from name or assume today's date | Create preparation | |
| Existing target | Original WorkDefinitionNameId or original WorkDefinitionCode | Ask which existing name is intended | Resolve identity before preparing a change | Update or uncertain-outcome reconciliation | |
| Requested changes | Explicitly intended writable attributes only | Ask what should change | Collect supplied intent; design enforcement compares current values and removes unchanged fields; distinguish omission from explicit clearing | Update | |
| Loader operation | RestAction supplied by core.data-loader preparation | Return to owning loader preparation | Keep loader controls out of the product REST body | Loader artifact preparation | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Request shape | Use text for names/type, a date for effective dates, and JSON boolean for UsedInPlanningFlag; core.data-loader owns file-to-service serialization | Supplied values | |
| Payload allowlist | Eligible business fields are WorkDefinitionCode, WorkDefName, WorkDefNameDescription, WorkDefinitionType, UsedInPlanningFlag, EffectiveFromDate and EffectiveToDate. WorkDefinitionNameId is identity, normally server-generated on create and never updated | Request preparation | |
| Derived/hidden values | Omit WorkDefinitionTypeMeaning, IsUsedInWorkDefinition, SeededFlag, ObjectVersionNumber, audit attributes, language and DFF fields; never replay a full GET record as a write body | Request preparation | |
| Type representation | Map explicit Standard, Rework and Transform intent to STANDARD, REWORK and TRANSFORM; preserve canonical codes. Ask about any other value; do not claim REST has a lookup-membership validator | Explicit type supplied | |
| Omission versus null | Preserve omission. Explicit null means an intended clear and requires supported clearing semantics; do not silently restore a default | Optional clear or omitted value | |
| Server-owned validation | Leave required/precision, uniqueness and end-date validity checks to Fusion. Do not build a second local length/date engine or duplicate-existence preflight | Create/update preparation | |
| Naming | Preserve submitted casing; do not force uppercase or create a reserved-prefix/character rule | Code or display name supplied | |

Use supplied task values for request-shape and intent checks. Fusion is authoritative for existing records and usage. Work definition names are not work definition structures: do not require a plant or item for this resource. Runtime payload composition and writes remain owned by core.data-loader.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WDNAME.INPUT | step | 10 | validate_input | passed->WDNAME.LOOKUPS;failed->WDNAME.ERROR | none | stop | Check request intent, safe shape and supported field selection; do not replicate server validators |
