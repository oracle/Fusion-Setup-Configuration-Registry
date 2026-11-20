# Defaulting Rules

Apply the field mappings and resolver rules in [Reference Lookups](ora_reference_lookups.md).

## Create and update policy

For a new template, apply the explicit create defaults below, keeping UI initialization and CSV Meaning mappings distinct. Serialize the defaults explicitly in the FSM CSV so blank import aliases cannot clear them. Record each applied default in the blueprint and complete preview. Preserve every explicit value, including an explicit blank; validate it normally instead of replacing it. Never apply create defaults to an update.

The acceptable-value lists are validation domains. Only this policy and the descriptor's createDefaults declare omitted-field defaults. A saved template or prior export is not evidence of new-template defaults.

## Standard Defaults

| UI attribute | CSV attribute | Default CSV value | Source |
| --- | --- | --- | --- |
| Pay Groups, Currencies, Business Units, Legal Entities, Sources | PayGroupOption, CurrencyGroupOption, OuGroupOption, LeGroupOption, SourceGroupOption | ALL for each | Declared create defaults |
| Payment Date | PaymentDateOption | RD (Use request date) | Declared create defaults |
| Pay Through Days | AddlPayThruDays | 0 | Declared create defaults |
| From / To Payment Priority | HiPaymentPriority / LowPaymentPriority | 1 / 99 | Declared create defaults |
| Date Basis | PayOnlyWhenDue | Pay date (Meaning for stored N) | Declared create defaults |
| Payment Conversion Rate Type | PaymentConversionRateType | Corporate (business alias) | Declared create defaults |
| Select Early Payment Invoices | AcceleratedInvoicesOption | No (Meaning for ORA_DD_NO) | Task CSV default policy below |
| Include Zero Amount Invoices | ZeroInvAllowedFlag | N | Declared create defaults |
| Apply credits up to zero amount payment | ZeroAmountsAllowed | N (unchecked) | Declared create defaults |
| Review installments | PayablesReviewSettings | N | Declared create defaults |
| Create payment files immediately | CreateInstrsFlag | N for ordinary mode; the declared Virtual card branch forces Y | Declared create defaults |

## Review and validation-failure defaults

| UI attribute | CSV attribute | Default CSV value |
|---|---|---|
| Review proposed payments | PaymentsReviewSettings | Y (checked) |
| Document validation failure handling | DocumentRejectionLevel | Stop process for review |
| Payment validation failure handling | PaymentRejectionLevel | Stop process for review |

Use these task-owned defaults whenever the user omits the fields on a create. Serialize both rejection fields as displayed Meaning aliases, not internal lookup codes. Do not require a contextual-default receipt, live lookup or additional user confirmation to apply them. Preserve an explicit unchecked review flag or another valid rejection choice. Updates preserve retained values.

The UI initializes these fields from internal-payer configuration with ORG_ID IS NULL. That explains UI initialization; the task default policy fixes the omitted-input values above from the implementor-confirmed create UI defaults. It does not claim the backing payment setup is identical everywhere.

## Blank and conditional fields

Leave all other omitted fields blank, including Type, Description, Inactive Date, Supplier Type, Payment Mode, Invoice Conversion Rate Type, supplier/payment method, bank/document/profile, funding account, first approver, calendar, cross-currency rate, settlement/bank-charge overrides, optional offsets, voucher number and flexfields. Do not invent master-data selections or calculated date offsets. Defaulting Corporate removes the need to ask the user for a conversion type when it is omitted; an explicitly blank required conversion alias is still invalid.

Apply user selections and declared dependent behavior after initial defaults. Virtual card still requires a funding account and profile and empty bank/document; an omitted CreateInstrsFlag becomes Y through its declared effect. Explicit incompatible values must be corrected. A supplied calculated payment date still needs its offset. Updates preserve retained values and never receive create defaults.

For an omitted Select Early Payment Invoices field on create, serialize No as declared in the task descriptor's [createDefaults](../e2e-adapter.json). The [CSV Meaning contract](../references/acceptable-input-values.md#fsm-csv-representation) maps No to ORA_DD_NO and Exclude to ORA_EXCLUDE. The underlying default is ORA_EXCLUDE, while the UI can display Yes for a null code; neither behavior changes the task's explicit CSV default. Preserve these distinct Meanings and explicit user values; do not infer that No and Exclude are interchangeable.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PPR.APPLY_DEFAULT_POLICY | decision | 40 | apply_default | evaluated->PPR.ENFORCE_DESIGN;blocked->PPR.HANDLE_ISSUES | PPR.CHECK_DEPENDENCIES | stop | For create omissions, apply the task UI create defaults with preview disclosure; preserve explicit values and blanks and all update values |
