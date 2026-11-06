# Manage Resource to Item Mapping Input Validation

Current capability gate: the task SKILL.md permits metadata/sample and explicitly requested status only. Complete business/reference reads and create/update/delete preparation are unsupported. Return blocked (invalid at input validation) before external activity or source preparation; the remaining domain contracts do not enable those operations.

Use the exact task BO itemResourcesMappings and core Data Loader only. Capability checks precede source preparation; validation never authorizes submission.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Mapping identity | One exact ResourceItemMapId | Block identity-dependent operations | Require fresh identity verification from a future reviewed core reader and the task Reference Read Workflow | Read selection, update or delete | |
| Create references | InventoryItemId, OrganizationId, ResourceId | Block create | Require Data Loader reference evidence | Create | |
| Explicit changes | At least one requested writable reference field | Block no-op update | Change only supplied fields; retain omitted values | Update | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Integer identities | Reject fractional, Boolean, rounded or nondecimal identifiers | Supplied IDs | |
| Writable fields | Only InventoryItemId, OrganizationId and ResourceId may change; ResourceItemMapId selects the existing mapping | Create or update | |
| Display and audit values | Do not send item/resource descriptions, organization display values, audit fields or an undeclared version field as changes | All writes | |
| Registered source | Validate exact BO, live template, action support and the exact prepared immutable artifact through core preflight | All writes | |
| Failed reader capability or evidence | Stop before preparation or approval when live identity/reference verification needs an unavailable, failed or incomplete reader | Business reads and applicable writes | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RIM.VALIDATE_INPUT | step | 1 | validate_input | valid->RIM.RESOLVE_IDENTITIES;invalid->RIM.RETURN_REFUSAL | none | stop | Current business-read, verification or mutation request: return invalid before source preparation because the complete core reader is unavailable; do not proceed to identity resolution |
