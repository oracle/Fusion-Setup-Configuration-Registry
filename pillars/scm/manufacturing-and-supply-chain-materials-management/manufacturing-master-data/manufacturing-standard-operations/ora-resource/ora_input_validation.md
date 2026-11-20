# Standard Operations — Input Validation

## Release and evidence boundary

Reviewed 29 October 2026. The [Oracle SCM documentation hub](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/) identifies 26D as current. The 26D overview/setup topics and Create operations REST page were retrieved. Other detailed REST references retained here use 26C, and the detailed creation guide uses 26B. These are retrieval gaps, not proof that newer topics do not exist. Use the cited release for each rule and verify the deployed contract before execution.

Public contract, request-preparation policy and deployment-dependent behavior are distinguished below. Public citations establish only what the linked pages document. No live create/update tests were performed. Keep supplied intent separate from the persisted result; the owning core workflow controls reads, preparation, authorization, writes and result verification.

## Public references

- [26D: Create operations](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fasrp/op-standardoperations-post.html): retrieved 29 October 2026; Boolean request types, header schema and code-based create example. Yes/no input normalization below is FSCR preparation behavior, not an additional Oracle REST enum.
- [26C: Create resources](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-standardoperations-standardoperationid-child-standardoperationresource-post.html): primary-resource inputs.
- [26C: Create alternate resources](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-standardoperations-standardoperationid-child-standardoperationresource-standardoperationresourceid-child-standardoperationalternateresource-post.html): alternate-resource inputs.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Intended action and level | Create/update and header, primary resource or alternate resource; explicitly requested optional extensions | Ask for intended scope | Distinguish adding a child from changing its parent; do not infer deletion or upsert | Preparation | |
| New header business intent | StandardOperationCode, StandardOperationName, OrganizationId or OrganizationCode, WorkCenterId or supported WorkCenterCode | Ask for missing intent | Collect intended organization and work center; joined display fields are not additional mandatory caller inputs | Header create | |
| Existing target | Original StandardOperationId or original code plus organization; child identity for child updates | Ask which record is intended | Use reference lookups after input collection; never use proposed new code as original identity | Update or child work beneath an existing parent | |
| Primary resource intent | ResourceId or supported ResourceCode, ResourceSequenceNumber and intended parent; principal selection for a simultaneous group | Ask for missing sequence or identity; ask for principal selection only when multiple resources share a sequence | Retain the intended sequential or simultaneous grouping; apply the principal preparation policy in ora_design_enforcement.md | Primary resource create | |
| Alternate resource intent | ResourceId or supported ResourceCode, AssignedUnits, PriorityRanking and one of UsageRate or InverseUsageRate | Ask for missing choice | No automatic ranking, assigned-unit or alternate-rate default is available | Alternate create | |
| Supplier details | Intended OperationType=SUPPLIER, explicit count-point intent and any intended OSP item, supplier/site and lead-time values | Clarify business intent where needed | Collect intended values and rely on server validation; do not assert every omitted supplier/site is an error | Supplier preparation | |
| Changes | Explicit writable field changes, preserving omitted versus null | Ask what should change | No full-record replay or create-default template on update | Update | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Source of intent | Use supplied task values for request-shape checks; Fusion remains authoritative for current records, reference facts and metadata | All preparation | |
| Data Loader section names | Preserve the exact case-sensitive discriminators standardOperations, StandardOperationDFF, StandardOperationResource, StandardOperationResourceDFF and StdOpAlternateResource. Do not rename the alternate DAT section to StandardOperationAlternateResource | Data Loader input | |
| Data Loader metadata scope | A METADATA header establishes section and column names only. Column presence does not establish requiredness, type, length, default, writability, supported action or feature enablement. A template Version V2 marker is not a Fusion release or REST API version | Data Loader input | |
| Data Loader parent identity | Preserve supplied parent identity for core validation: header/DFF OrganizationCode and StandardOperationCode; primary resource StandardOperationId or its header context; resource DFF StandardOperationResourceId, ResourceCode and ResourceSequenceNumber with header context; alternate StandardOperationResourceId or PrimaryResourceCode and PrimaryResourceSequenceNumber with header context. Do not infer that every identity column is required or that all combinations are interchangeable | Child or DFF Data Loader input | |
| DFF column spelling | Header DFF uses FLEX:WIS_STANDARD_OPERATIONS and its qualified __FLEX_Context/__FLEX_Context_DisplayValue columns. Resource DFF uses FLEX:WIS_STD_OPERATION_RESOURCES and its qualified context columns. Preserve StdOperationResourceId and StandardOperationResourceId as distinct resource-DFF column names; do not normalize one into the other. Discriminator is a DFF column, not a replacement section name | Requested DFF Data Loader input | |
| Loader controls and placeholders | RestAction and SourceRefTableName/SourceRef001 through SourceRef010 belong to the loader contract, not product REST business attributes. Leave their handling to core.data-loader; never treat source-table/source-column placeholders as business values or populate unused tracking fields | Data Loader preparation | |
| Boolean input normalization | For attributes confirmed Boolean in the deployed request schema, including CountPointOperationFlag, AutoTransactFlag and PrincipalFlag, accept native true/false and trimmed case-insensitive text true/false or yes/no. Also normalize the supplied-input aliases Y/N. Map true, yes and Y to Boolean true; map false, no and N to Boolean false. Never use generic truthiness conversion | Supplied Boolean task inputs | |
| Invalid or absent Boolean input | Reject other tokens, including numeric 1/0, rather than guessing. Preserve omission for defaulting and updates; do not convert blank or explicit null to false. Apply the existing field-specific clear contract to explicit null | Supplied Boolean task inputs | |
| Boolean preparation output | Retain typed booleans in normalized task data. When handing values to a text-only XLSX/DAT writer, explicitly format Boolean cells as lowercase true or false so generic language stringification cannot emit True/False. | Before core source preparation | |
| Boolean and string distinctions | At the product REST boundary, CountPointOperationFlag, AutoTransactFlag and PrincipalFlag must be JSON booleans true/false, never quoted strings such as True, true, Y or N. DefaultforAutomaticWorkDefinition remains a Y/N string, ScheduledIndicator a YES/NO string and BasisType a string | REST serialization | |
| Numeric representation | ResourceSequenceNumber, UsageRate and AssignedUnits must be JSON numbers at the product REST boundary. Preserve numeric meaning; do not quote them in the generated REST body | Resource REST serialization | |
| Serialized-artifact verification | Inspect the final prepared fields. Reject noncanonical Boolean text such as True/False or yes/no in the final artifact; accepted input aliases must already have been normalized to lowercase true/false. Keep logical Boolean input distinct from transport text. Apply normal core Data Loader validation; no separate adapter-conversion evidence is required | Final Data Loader artifact | |
| Header field selection | Eligible business inputs include organization on create, code/name/descriptions, WorkCenterId, OperationType on create, count-point/auto flags, InactiveDate, DefaultforAutomaticWorkDefinition, completion controls, supplier/item/site references, lead times/UOM, maintenance-code references and OperationYield. Confirm exact writability in target metadata | Header preparation | |
| Header system fields | Omit StandardOperationId on create, joined organization/item/work-area fields, derived descriptions, audit fields, ResourcesCount, ReplicatedFlag and internal controls. CommonStandardOperationId and LastReplicatedDate are outside ordinary create/update preparation | Header preparation | |
| Primary resource field selection | Eligible inputs are ResourceId or supported create ResourceCode, ResourceSequenceNumber, PrincipalFlag, AssignedUnits, one rate, BasisType, ChargeType, ScheduledIndicator, ResourceActivityCode and intended job/equipment profile reference | Primary resource preparation | |
| Resource derived fields | For product REST business values, omit generated child ID, parent/context IDs supplied by the relationship, UOMCode/UnitOfMeasure, joined names/descriptions, type/costed/alternate-exists flags and audit attributes. Preserve required Data Loader parent/key context for core handling; it is not an additional business-field change | Primary resource preparation | |
| Alternate field selection | Eligible business inputs are ResourceId or supported create ResourceCode, AssignedUnits, PriorityRanking and one rate. Omit generated alternate ID, propagated REST parent ID, derived UOM, joined/display and audit business-field changes. Preserve Data Loader parent/key context for core handling | Alternate preparation | |
| Reference representation | Resolve contradictory ID/code pairs with the user; do not rely on server precedence to choose business intent. Use update IDs where code fields are not writable | Reference inputs | |
| Rate selection | Supply one of UsageRate and InverseUsageRate, not both; request the intended representation if conflicting. The alternate nonpositive-rate behavior is owned by design enforcement | Primary or alternate explicit rate | |
| Omitted versus null | Omit absent values. An explicit null is a requested clear whose exact field semantics must be supported; null may derive, reset, fail, or leave an old value instead of clearing it | Optional and update fields | |
| Feature-sensitive input | Omit unused yield/profile fields, including explicit null placeholders. A schema field alone does not prove feature enablement | Optional feature inputs | |
| Server validation ownership | Collect meaningful input and use a minimal allowlist; delegate mandatory precision, duplicate checks, lookup membership, date comparisons, capacity and relationship validation to the server | All preparation | |
| Naming | Preserve intended casing; do not introduce uppercase, reserved-prefix, display-name uniqueness or case-insensitive code rules | Code/name input | |
| Extension fields | Accept only requested DFF/attachment fields whose deployed metadata and owning core support are established; never expose hidden execution context or treat displayed required joins as payload requirements | Optional extensions | |

Payload composition belongs to core.data-loader. These rules define input selection, not a resource-local payload builder or REST writer. Organization is create-only. Removing a resource, alternate or header is a distinct destructive intent; it is not inferred from omission or an empty child array.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| STDOP.INPUT | step | 10 | validate_input | passed->STDOP.LOOKUPS;failed->STDOP.ERROR | none | stop | Collect action, scope, identity and minimal typed intent; do not reproduce server validators |
