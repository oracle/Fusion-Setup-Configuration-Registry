# Standard Operations — Defaulting

## Release and evidence boundary

Reviewed 29 October 2026. The [Oracle SCM documentation hub](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/) identifies 26D as current. The 26D overview/setup topics were retrieved; detailed Standard Operations REST pages could be retrieved only in 26C, and the detailed creation guide in 26B. These are retrieval gaps, not proof that newer topics do not exist. Use the cited release for each rule and verify the deployed contract before execution.

Public contract, request-preparation policy and deployment-dependent behavior are distinguished below. Public citations establish only what the linked pages document. No live create/update tests were performed. Keep supplied intent separate from the persisted result; the owning core workflow controls reads, preparation, authorization, writes and result verification.

## Public references

- [26C: Header create schema](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-standardoperations-post.html): literal defaults and API representations.
- [26C: Primary-resource create schema](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-standardoperations-standardoperationid-child-standardoperationresource-post.html): resource defaults.
- [26C: Alternate-resource create schema](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-standardoperations-standardoperationid-child-standardoperationresource-standardoperationresourceid-child-standardoperationalternateresource-post.html): required alternate choices.
- [26B: Create a Standard Operation](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/faumf/create-a-standard-operation.html): UI context; its yield default must not be assumed to be a REST default.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Header OperationType | IN_HOUSE; leave omitted for server default | Omitted on create | No | |
| Header CountPointOperationFlag | false | Omitted on create; optional-operation intent must be understood | No | |
| Header AutoTransactFlag | false | Omitted on create | No | |
| Header DefaultforAutomaticWorkDefinition | N as string | Omitted on create | No | |
| Header AddlMtlAtManualIssue | ALLOW; compatibility behavior also restores ALLOW for null on insert/update | Omitted create value or explicit null processed by server | No client substitution; disclose reset behavior | |
| Header OperationComplWithOpenExceptions and OperationComplWithUnderIssue | Server clears to null for non-count-point; for count-point, null becomes ALLOW | Server insert/update completion handling; verify returned state | No client override; resolve conflicts before handoff | |
| Header StandardOperationId | Server-generated identity | Header create | No; omit supplied ID | |
| Header descriptions, InactiveDate, supplier/site/item and lead-time fields | No literal default is assumed | Unspecified optional values | No | |
| Header OperationYield | No REST literal default established; do not copy UI default 1 | Omitted create value | No | |
| Primary AssignedUnits | 1 | Omitted on primary-resource create | No | |
| Primary BasisType | 1 as string | Omitted on primary-resource create | No | |
| Primary UsageRate and InverseUsageRate | 1 when neither rate supplied; server derives reciprocal from an explicit selected rate | Primary-resource create | No | |
| Primary ChargeType | MANUAL for optional parent; otherwise AUTOMATIC | Omitted/null during primary-resource create | No; server derivation | |
| Primary ScheduledIndicator | NO for optional parent; otherwise YES only when time-UOM/profile checks allow it, else NO | Omitted/null during primary-resource create | No; server derivation | |
| Primary UOMCode | Derived from selected resource | Primary-resource create | No; read-only | |
| Primary StandardOperationId and WorkCenterId | Propagated by parent relationship | Nested or child create | No; omit manual context fields | |
| Primary sequence and PrincipalFlag | Preserve supplied sequence. For a wholly new singleton sequence with omitted PrincipalFlag, prepare false as FSCR policy; simultaneous groups require explicit principal selection | Primary-resource create | Never override an explicit true; resolve that conflict through design enforcement | |
| Alternate UOMCode | Inherited from primary operation resource | Alternate create | No; read-only | |
| Alternate AssignedUnits, rate and PriorityRanking | No literal defaults; collect intended values | Alternate create | No guessing | |
| Job/equipment profiles and resource activity | No literal default | Unspecified optional resource fields | No | |

## Defaulting Boundaries

The apply_default node records expected server defaults and preserves omission except for the explicit singleton PrincipalFlag=false preparation policy above; it does not generate identities. That policy is not a claim about the server literal default. Preserve CountPointOperationFlag=true for count-point intent. For a count-point create, AutoTransactFlag=false is the compatible effective value: retain the documented false default when omitted, or serialize an explicitly supplied false correctly. Apply the Boolean normalization in ora_input_validation.md before source preparation, including the singleton false policy; it changes representation, not the user's logical choice. Never change count-point intent to false to bypass an error. On update, omitted fields remain unchanged and create defaults are not reapplied by the client. Header flag changes do not imply that existing resource charge/schedule values will be recalculated.

Conditional compatibility behavior requires target verification. A supplied header ID is removed by the create path; omit it rather than relying on that behavior. Supplier creation forces the automatic-work-definition default to N; do not silently accept conflicting explicit intent. Completion controls can clear or reset during persistence. Invalid lookup values can fail before a later clearing step.

A supplied yield can be rounded or forced to 1 for supplier, automatic-transact or optional operations, and setters are feature-sensitive even for null. Do not promise a rounding scale or optional-operation yield support. Primary positive rate derives reciprocal, zero sets both rates to zero, and negative rates are server-invalid. Alternate nonpositive rates may be ignored instead of rejected; the narrow intent guard is in design enforcement. A null inverse rate is not a supported universal clear. Confirm persisted outcomes through the owning workflow.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| STDOP.DEFAULTS | step | 40 | apply_default | passed->STDOP.DESIGN;failed->STDOP.ERROR | STDOP.DEPENDENCIES | stop | Preserve default omissions and explicit intent; record conditional server behavior without synthesizing payload values |
