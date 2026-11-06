# Defaulting Rules

## Defaults

| Field(s) | Default value | Applies when | Explicit request | Handling |
|---|---|---|---|---|
| Shared required flags: DisallowAttachmentDelFlag, AttachmentMandatorySsFlag, ValidateBeforeApprovalFlag, AllowForceApprovalFlag, ApprovalWorkflowFlag, AutoCalculateInterestFlag, RecalcPayScheduleFlag | `N` | New AP_SYSTEM_PARAMETER row | A conflicting value needs the Invoice Options task | Reuse the Invoice Options create defaults and write them in the preview and CSV. |
| TermsDateBasis | `Invoice` | New AP_SYSTEM_PARAMETER row | A different choice needs the Invoice Options task | Write the shared create default in the CSV. |
| GlDateFromReceiptFlag | `INVOICE` | New AP_SYSTEM_PARAMETER row | A different choice needs the Invoice Options task | Write the shared create default in the CSV. |
| PayDateBasisLookupCode | `DISCOUNT` | New AP_SYSTEM_PARAMETER row | A different choice needs the Invoice Options task | Write the shared create default in the CSV. |
| BudgetDateBasis | `ACC` | New AP_SYSTEM_PARAMETER row | A different choice needs the Invoice Options task | Write the shared create default in the CSV. |
| Other optional Payment Options fields | No inferred default | A field is omitted | Preserve on update | Do not invent values from another record or export. |

## Defaulting Boundary

Do not infer a Payment Options default from an observed export value. Preserve
unrelated exported values exactly. Apply the shared defaults only to creates.
Do not turn blank update fields into defaults. Uploaded creates must already
contain the documented values in their CSV cells; validation rejects missing
or conflicting defaults and never edits the ZIP.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PAYOPT.APPLY_DEFAULTS | step | 25 | apply_default | success->PAYOPT.ENFORCE_DESIGN;failure->PAYOPT.DESIGN_BLOCKED | PAYOPT.CHECK_DEPENDENCIES | stop | Always; apply documented shared defaults only to generated creates, verify exact default cells without editing uploaded ZIPs, and preserve update values without inferred defaults |
