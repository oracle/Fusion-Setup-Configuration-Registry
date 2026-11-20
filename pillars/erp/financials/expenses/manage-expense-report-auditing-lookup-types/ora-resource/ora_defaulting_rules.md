# Auditing lookup defaults

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| EnabledFlag | Y | New code and Enabled? omitted; EO-CODE DefaultValue Y | No | |
| ChangeSinceLastRefresh | N | New code only; LookupGenericEO and LookupGenericTranslationEO DefaultValue N | No; technical field is not workbook input | |
| Existing optional values | Retain target value | Existing code with blank worksheet field | No | |

Do not default lookup type, code, set, meaning, dates, sequence, tag, module ID,
view ID, translation language or customer intent. Yes/No maps explicitly to Y/N.
No null clearing is claimed without a verified import-null contract.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUDLK_DEFAULT | step | 4 | apply_default | success->AUDLK_DESIGN | AUDLK_LOOKUP | stop | Always |
