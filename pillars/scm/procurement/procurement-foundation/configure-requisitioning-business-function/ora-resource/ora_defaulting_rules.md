# Defaulting Rules

## FSM CSV Defaults

Apply these defaults only while preparing the FSM task-level CSV package. Do not leave any listed field blank in the package preview.

| CSV field | Default value | Apply when | User override allowed | Notes |
|---|---|---|---|---|
| ReqimportGroupByCode | ITEM | Field is omitted or blank | Yes | Validate the final CSV value before packaging |
| ReapprovalRequiredFlag | N | Field is omitted or blank | Yes | Validate the final CSV value before packaging |
| CreateOrdersFlag | Y | Field is omitted or blank | Yes | Validate the final CSV value before packaging |
| CancelBackingReqCode | OPTIONALLY | Field is omitted or blank | Yes | Validate the final CSV value before packaging |
| MultipleLegalEntities | ERROR | Field is omitted or blank | Yes | Validate the final CSV value before packaging |

## Defaulting Guardrails

| Rule | Handling | Applies when | Notes |
|---|---|---|---|
| OrganizationCode | Never infer or default this value | Import package preparation | Require a CSV-ready value from the user or source data |
| LineType | Omit unless directly supplied as a CSV-ready value | Import package preparation | Optional |
| ShipToLocation | Omit unless directly supplied as a CSV-ready value | Import package preparation | Optional |
| Final preview | Show the final defaulted CSV values before approval | Before import | Approval must reference the exact package and target environment |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| POR.APPLY_FSM_DEFAULTS | step | 2 | apply_default | success->POR.ENFORCE_FSM_IMPORT_RULES;blocked->POR.BLOCKED | POR.VALIDATE_FSM_PACKAGE | stop | Import package preparation |
