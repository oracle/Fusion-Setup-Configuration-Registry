# MPS defaults



## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| ORA_IBY_PAYMENT_SYSTEM_ACC_NAME.SecuredFlag | N | New definition only; source EO default; sensitivity policy still applies | No |  |


## Default Boundaries

No credential placeholders are allowed. Supply root dates, account owner type and definition display order explicitly. UI defaults do not prove import defaults. A blank root UI end-date display corresponds to its sentinel; a blank CSV cell may instead become an explicit null. Preserve unchanged dates during updates. Source: SRC-MPS-ADE-004, SRC-MPS-META-006, SRC-MPS-META-012, SRC-MPS-FW-CSV.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPS.DEFAULTS | step | 50 | apply_default | pass->MPS.GATE;fail->MPS.RETURN_ISSUES | MPS.DEPENDENCIES | stop | always |
