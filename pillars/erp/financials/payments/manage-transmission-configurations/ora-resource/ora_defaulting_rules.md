# Transmission defaulting rules



## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver | Source IDs |
|---|---|---|---|---|---|

## Source-backed default behavior

- IBY_TRANSMISSION_CONFIGURATION.StartDate: the entity initializes the current database date. Require an explicit date in offline preparation so the candidate is deterministic and reflects the intended start; do not substitute the workstation date.
- IBY_TRANSMISSION_CONFIGURATION.EndDate: the entity initializes4712-12-31 and supplies that sentinel when null during DML. Use the sentinel only for confirmed open-ended intent.
- IBY_TRANSMISSION_CONFIGURATION.EndDateDsp: derive the same finite EndDate, or blank for4712-12-31. Reject contradictory inputs because the setter changes EndDate.
- Preserve fields not requested for change. No bank endpoint or secret has a task-invented default. The explicitly approved, create-only SFTP USERNAME placeholder `changeit` is the sole username exception; see [the sensitive-field policy](ora_sensitive_fields.md).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTC.DEFAULT | step | 40 | apply_default | success->MTC.DESIGN;failure->MTC.ERROR | MTC.DEPENDENCY | stop | Always |

## Evidence

Source IDs: SRC-CODE-CONFIG-DATES; SRC-CODE-CONFIG-DML. TransmissionConfigurationEOImpl.initDefaults1125-1127, prepareForDML1131-1144, EndDateDsp setter375 onward.

## Sensitive setup boundary

Apply [the sensitive-field policy](ora_sensitive_fields.md): omit sensitive inputs, expose only field-name notices, and validate the final ZIP against the task-owned policy. Unknown/custom parameters require review.
