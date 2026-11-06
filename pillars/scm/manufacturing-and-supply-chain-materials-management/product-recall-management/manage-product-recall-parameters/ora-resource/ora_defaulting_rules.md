# Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| ActiveFlag | true | A new recallContainmentTaskOwners record is explicitly requested and ActiveFlag is omitted | Yes | |
| Participating inventory organizations | All inventory organizations participate | No recallInventoryOrganizations rows exist after the approved reconciliation | No; add one or more selected organization rows to restrict scope | find_existing_recall_parameter_rows |

Any default that changes the prepared upload values requires Data Loader to rebuild the artifact and repeat validation before Task Hook preview. Record a default already represented in the artifact without modifying its bytes.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RECALL.PARAMETERS.APPLY-DEFAULTS | step | 40 | apply_default | applied->RECALL.PARAMETERS.ENFORCE-DESIGN | RECALL.PARAMETERS.DESCRIBE-CONTRACT | stop | A permitted omitted default applies; otherwise record no default and continue |
