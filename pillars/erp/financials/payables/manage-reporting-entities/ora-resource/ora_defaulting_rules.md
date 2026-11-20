# Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| SetCode | Required nonblank on create; no implicit default; use exact selected location context | New header requires location matching context | No |  |
| EnterpriseId | Derived from the selected existing BU; no fabricated enterprise ID | Create with BU name | No | resolve_reporting_entity_bu |
| Child OrgId | Inherited internally from ReportingEntityHeader.OrgId; not a CSV input. | New child line | No |  |
| Audit columns | System managed; preserve export technical columns. | All operations | No |  |
| Unspecified existing fields | Preserve baseline values exactly; no inferred global-attribute, date or location defaults; update explicitly requested global attributes and preserve all others | Update | No |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRE.DEFAULT | step | 40 | apply_default | success->MRE.DESIGN;failure->MRE.ERROR | MRE.LOOKUP | stop | Apply only source-backed derivation or preserve existing values |
