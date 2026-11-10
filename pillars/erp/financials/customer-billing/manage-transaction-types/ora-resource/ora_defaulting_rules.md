# Manage Transaction Types Defaulting Rules


## Task-Owned Defaults

These rules document entity-specific behavior. The generated adapter binds the executable create default from the reviewed Attributes and Evidence Workbook so it applies only to `AR_REF_ACCT_TRX_TYPE`.

| Field | Default Value | Applies When | Override User Value? | Resolver | Evidence |
|---|---|---|---|---|---|
| AR_REF_ACCT_TRX_TYPE.SourceRefTable | RA_CUST_TRX_TYPES_ALL | Every emitted reference-account child row | Yes; reject or replace any caller-supplied different value with the task-owned constant |  | SRC-CODE-REF-VO, SRC-CODE-AM-IMPL, SRC-EDM-AR-REF-26A |
| Parent and child audit fields | Omit | Every create candidate | Yes; caller values are never serialized |  | SRC-CODE-AM-IMPL, SRC-CODE-PRIMARY-EO, SRC-CODE-REF-VO |
| Optional fields | Omit | The request does not supply a source-backed value and the field is not create-required | No |  | SRC-FSM-PACKAGE, SRC-CODE-CREATE-VO |

No other business default is authorized. Required create fields must be explicit even when the UI may show a default; the prepared import contract does not establish that every UI default is applied by the FSM service path.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTT.APPLY_DEFAULTS | step | 30 | apply_default | applied->MTT.ENFORCE_DESIGN;not_needed->MTT.ENFORCE_DESIGN;invalid_override->RETURN_ISSUES | MTT.CHECK_DEPENDENCIES | stop | Dependency checks succeed |
