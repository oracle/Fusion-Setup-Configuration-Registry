# Manage Invoice Holds and Releases — Defaulting Rules

Task: AP_MANAGE_INVOICE_HOLDS_AND_RELEASES. This resource owns create defaults and explicit-input precedence for AP_HOLD_CODE.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AP_HOLD.DEFAULTS | step | 40 | apply_default | success->AP_HOLD.DESIGN;failure->AP_HOLD.ERRORS | AP_HOLD.DEPENDENCIES | stop | Apply the two recorded create defaults only to omitted fields, then validate the complete candidate. |

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| AP_HOLD_CODE.UserUpdateableFlag | Y | Omitted on create | No |  |
| AP_HOLD_CODE.PostableFlag | N (Accounting not allowed) | Omitted on create | No |  |

## Defaulting Policy

Apply only these two omission defaults. A valid explicit value takes precedence; supplied blank or null is not omission and must pass [input validation](ora_input_validation.md). Disclose applied defaults in the preview and preserve the original request separately. An approved default can supply a required value without asking the customer.

No other client defaults apply, and updates never receive create defaults. Omission and preservation follow the input contract. [Pre-import consistency rules](ora_design_enforcement.md#pre-import-consistency-rules) derive only omitted dependent values, separately from defaults. Reject a conflicting supplied value instead of replacing it.
