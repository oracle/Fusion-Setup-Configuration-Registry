# Acceptable input values

Use this reference by default when interpreting and validating supplied
dropdown, radio and checkbox choices for
`ORA_AP_MANAGE_PAYMENT_PROCESS_REQUEST_TEMPLATE`.

## Validation policy

- **Fixed code:** the listed domain is closed. Accept the canonical CSV code
  or an unambiguous listed label, case-insensitively, and serialize the shown
  code. Reject a supplied value outside this fixed domain.
- **Configured label:** use the listed names as default acceptable values for
  this task in every environment. Accept an exact listed name; an unambiguous
  case-insensitive match may be canonicalized to its exact spelling with the
  normalization disclosed in the preview. Serialize the field's exact import
  Meaning alias. Do not assume UI display text, exported text and import
  Meaning are interchangeable or invent a translation between them.
  Do not substitute a lookup code or browser option index.
  Apply these defaults without requiring a live lookup solely because the
  environment differs. For an unlisted value or an explicit reference check,
  use the active reference-validation route with the field's lookup context.
  Do not reject an unlisted configured value without that validation.
- Check only supplied/changed values. Omission preserves intent and existing
  update data. A blank UI option is recorded as `(blank)` below; whether to
  serialize a blank is governed by the field's existing requiredness and
  blank-clearing contract. Do not add blank choices to other rows, reject an
  unchanged retained blank, or turn omission into an explicit clear.
- These lists define acceptable values. Apply the [UI create-default policy](../ora-resource/ora_defaulting_rules.md) to omitted fields on new templates. Preserve explicit values and blanks, disclose defaults, and never apply create defaults to updates.

## FSM CSV representation

The FSM CSV format column is the serialization contract, not the browser
control's stored option index. Input interpretation and CSV serialization are
separate: a user may say Specific, but `PayGroupOption` must contain `SPECIFY`.
If a user supplies a raw lookup code for a Meaning-alias column, first resolve
that code's exact Meaning in the field's lookup context. Do not pass an
unmapped code through as text or infer its representation from the column name.
For the ten Meaning-alias columns, write the exact configured display Meaning
instead of the underlying lookup code. The task runtime normalizes its eleven
fixed domains and listed Supplier Type labels; other configured aliases pass through unchanged and must already have
the correct text before package construction.

**Template type is a displayed name.** `TemplateTypeValue` is the CSV alias for
the displayed `PAYMENT_TEMPLATE_TYPE` value, for example `Daily`. It is not the
stored `TemplateType` lookup code. Resolve the supplied Meaning within lookup
type `PAYMENT_TEMPLATE_TYPE` and view application ID `200` to derive the
internal code. A code-like string is valid only if it is itself the exact
configured Meaning; do not infer the representation from its spelling or
serialize the internal `TemplateType` attribute.

Preserve unchanged values and blanks when applying these rules. Do not
reformat an entire baseline from this table or validate unrelated fields
because a Description-only update was requested.

- Keep `AcceleratedInvoicesOption` Meanings distinct: No → `ORA_DD_NO`,
  Yes → `ORA_DD_YES`, Discounted Only → `ORA_DD_ONLY`, and Exclude →
  `ORA_EXCLUDE`. Serialize the Meaning on the left. Preserve retained Exclude;
  do not silently convert No to Exclude or Exclude to No.
- Accept only `RD` or `ED` for a new `PaymentDateOption` input. Do not infer
  additional input choices from existing data.

## Default acceptable-value table

| Attribute | CSV attribute | FSM CSV format | Acceptable values / label to CSV mapping | Domain |
|---|---|---|---|---|
| Type | `TemplateTypeValue` | Displayed Meaning (text) | `(blank)`; Daily; Loans; Expense reports; EFT | Configured label |
| Date Basis | `PayOnlyWhenDue` | Displayed Meaning (text) | Due date; Pay date | Configured label |
| Select Early Payment Invoices | `AcceleratedInvoicesOption` | Displayed Meaning (text) | No; Yes; Discounted Only | Configured label |
| Include Zero Amount Invoices | `ZeroInvAllowedFlag` | Code (text) | No → `N`; Yes → `Y` | Fixed code |
| Supplier Type | `SupplierType` | Displayed Meaning (text) | `(blank)`; Attorney; Carrier; Contractor; Federal; Government; Insurance Company; Internal; Manufacturing; PCF_Supplier_Type1; PCF_Supplier_Type2; PCF_Supplier_Type3; PCF_Supplier_Type4; PCF_Supplier_Type5; Public Sector; Services; Subcontractor; Supplier; Tax Authority; Trust; Utility | Configured label |
| Payment Mode | `PaymentMode` | Displayed Meaning (text) | `(blank)`; Virtual card | Configured label |
| Invoice Conversion Rate Type | `InvoiceConversionRateType` | Displayed Meaning (text) | `(blank)`; All others; User | Configured label |
| Pay Groups | `PayGroupOption` | Code (text) | All → `ALL`; Specific → `SPECIFY` | Fixed code |
| Currencies | `CurrencyGroupOption` | Code (text) | All → `ALL`; Payment → `PAYMENT`; Invoice → `INVOICE` | Fixed code |
| Business Units | `OuGroupOption` | Code (text) | All → `ALL`; Payment → `PAYMENT`; Invoice → `INVOICE` | Fixed code |
| Legal Entities | `LeGroupOption` | Code (text) | All → `ALL`; Specific → `SPECIFY` | Fixed code |
| Sources | `SourceGroupOption` | Code (text) | All → `ALL`; Specific → `SPECIFY`; Exclude → `EXCLUDE` | Fixed code |
| Payment Date | `PaymentDateOption` | Code (text) | Use request date → `RD`; Calculate based on request date → `ED` | Fixed code |
| Settlement Priority Override | `SettlementPriorityValue` | Displayed Meaning (text) | `(blank)`; Express; Normal | Configured label |
| Bank Charge Bearer Override | `BankChargeBearerOverride` | Displayed Meaning (text) | `(blank)`; Following Service Level; Payee; Payee pays express charges; Payer; Shared | Configured label |
| Apply credits up to zero amount payment | `ZeroAmountsAllowed` | Code (text) | No / unchecked → `N`; Yes / checked → `Y` | Fixed code |
| Review installments | `PayablesReviewSettings` | Code (text) | No / unchecked → `N`; Yes / checked → `Y` | Fixed code |
| Review proposed payments | `PaymentsReviewSettings` | Code (text) | No / unchecked → `N`; Yes / checked → `Y` | Fixed code |
| Create payment files immediately | `CreateInstrsFlag` | Code (text) | No / unchecked → `N`; Yes / checked → `Y` | Fixed code |
| Document — Validation Failure Handling | `DocumentRejectionLevel` | Displayed Meaning (text) | Reject all documents for payee; Reject all documents in request; Reject only documents with errors; Stop process for review | Configured label |
| Payment — Validation Failure Handling | `PaymentRejectionLevel` | Displayed Meaning (text) | Reject all payments in request; Reject only payments with errors; Stop process for review | Configured label |

Keep FSM blank handling separate from the three nonblank early-payment
choices; a blank is not an additional business choice.
For omitted fields on create, serialize the task defaults: early-payment
selection No (Meaning for `ORA_DD_NO`) and zero-amount invoices `N` (No).
The underlying early-payment default is `ORA_EXCLUDE` (Exclude), while a null
code in an imported row can display Yes in the UI. These distinct Meanings are
not interchangeable.
Use the [defaulting rules](../ora-resource/ora_defaulting_rules.md) for the
create and update boundaries.

## Coupled rules and searchable references

- `PaymentDateOption=ED` requires nonblank integer `AddlPaymentDays`. Do not
  impose a nonnegative bound on this offset.
- Include Zero Amount Invoices (`ZeroInvAllowedFlag`) and Apply credits up to
  zero amount payment (`ZeroAmountsAllowed`) are separate attributes.
- Virtual-card mode changes applicable payment attributes and forces immediate
  file creation through the documented task logic. Listing a label does not
  establish that every field combination is valid.
- `SPECIFY` requires members for pay groups and legal entities; `PAYMENT` or
  `INVOICE` requires members for currencies and business units. Sources requires
  members for `SPECIFY`; do not invent the same requirement for `EXCLUDE`.
- The Sources row defines the radio option. Its member names remain configured
  `SOURCE` lookup Meanings (application 200), serialized as `InvoiceSourceName`.
- Payment Method, Supplier or Party, bank account, payment document, payment
  process profile, payment/cross-currency conversion-rate LOVs and selected
  group members are contextual references. Their search results are not closed
  enums. Validate supplied keys/aliases using
  [reference contracts](../ora-resource/ora_reference_lookups.md).
  The four direct-user-input fields below are exempt from these checks.
- For every REST reference check in this task, a successful response containing
  at least one matching row is sufficient. Multiple matching rows are accepted;
  do not require uniqueness, fetch more pages solely to establish uniqueness,
  or reject a match because import-time duplicate/enablement behavior remains
  unproved. Query/filter using the supplied value and applicable reference
  context. Preserve the supplied CSV key or alias; accepting multiple rows does
  not authorize selecting an arbitrary internal ID. Empty results do not pass
  this REST check, and failed requests are not evidence of invalid input.
  Retain a receipt bound to the exact `operationId`, `entity`, `field`,
  `resolver`, nonblank `evidence`, and
  `restResult: {"httpStatus": 200, "items": [...]}`. For a conditional
  business-unit Name or CurrencyCode, the runtime matches that exact supplied
  value against the descriptor-declared `BusinessUnitName` or `CurrencyCode`
  response field. Other supported receipt mappings and required lookup context
  are declared in the task adapter; an undeclared mapping makes validation unavailable. The active read
  workflow owns query context, response authenticity and provenance. Existing
  authoritative FSM fallback and direct-user-input exceptions remain applicable.
- Payment Conversion Rate Type requires an intended resolvable alias for create.
  On update, apply the existing contract to an explicitly supplied or changed
  alias and preserve unchanged values; this choice table adds no requirement
  to a Description-only update. A blank import alias can clear the mandatory
  stored type despite the Corporate entity default. This is distinct from
  Invoice Conversion Rate Type.

## Payment-mode account and profile rules

### Payment document dependency

If Disbursement Bank Account (`BankAccountName`) is not selected, Payment
Document (`PaymentDocumentName`) must be blank. Check every create and any
update supplying either field or changing Payment Mode, using the supplied
changes plus retained values.
Clearing the bank while retaining a payment document is invalid; require an
explicit document clear or a selected bank. Do not silently clear either field.
A whitespace-only bank is not a selection, and a whitespace-only document is
not an empty CSV value. A selected bank does not by itself require a document.
Unrelated updates preserve existing values without reopening this check.

Apply these structural rules to the resulting template, using the exact CSV
attributes shown below. `PaymentMode` uses the displayed Meaning `Virtual card`;
a blank mode follows the nonvirtual branch.

| Payment Mode | Funding Card Account (`FundingCardAccount`) | Disbursement Bank Account (`BankAccountName`) | Payment Process Profile (`PaymentProfileName`) |
|---|---|---|---|
| Virtual card | Required | Unavailable; must be empty | Required |
| Blank / nonvirtual | Unavailable; must be empty | Optional | Optional |

Check every create. For an update, check this combination when Payment Mode,
either account or Payment Process Profile is supplied; merge the explicit
changes with the fresh baseline first. Retained values can satisfy required
fields. An unrelated Description-only update does not reopen these checks.
Required values must contain non-whitespace text. An unavailable account must
be empty, not a whitespace-only value left in the CSV. When switching modes,
require the now-inapplicable account to be empty in the resulting template.
If a retained or supplied account conflicts, request an
explicit clear rather than silently deleting it. Do not invent an account or
profile, or make the nonvirtual bank account/profile mandatory.

Funding Card Account presence and availability checks do not verify its
contents. Preserve an applicable supplied value exactly as entered, without a
lookup, eligibility check, normalization, conversion or companion derivation.
Keep profile/reference eligibility and documented import side effects separate
from these structural rules.

## Direct user inputs

For Transaction Calendar, First Approver, Funding Card Account and Bank
Conversion Rate Type, **use user inputs directly** when supplied. Take these
values as-is: do not verify or validate them, call a lookup or REST endpoint,
check eligibility, normalize spelling/case/whitespace, convert names to codes
or IDs, or derive missing companion values. Preserve omission rather than
defaulting or clearing a field. Preserve a separately supplied PersonNumber
as-is without requiring a name/number pairing check.

This policy takes precedence over general reference-validation guidance for
these four fields. The payment-mode presence and empty-account rules above
still apply before preparing a candidate; they do not validate Funding Card
Account contents. This policy defines input handling; it does not add a CSV column or
establish import assignment support. Keep supplied Bank Conversion Rate Type
in the request/blueprint and preview as-is until a supported serialization
field exists. Keep the Transaction Calendar assignment limitation explicit
without introducing a new input-verification step.

## Other UI inputs and membership CSV keys

Searchable LOVs select a display value but can serialize a different portable
key. Apply the field-specific rules below, including the direct-user-input
exceptions. Do not infer name-versus-code from the label alone or substitute
a REST response ID.

| Attribute | CSV attribute(s) | Required CSV representation |
|---|---|---|
| Payment Method | `PaymentMethodCode` | Actual configured payment-method code; not `PaymentMethodName`. |
| Supplier or Party | `SupplierOrParty`, `PartyNumber` | Display/name alias plus exact party number used by the resolver; a supplier number is not a party number. |
| Disbursement Bank Account | `BankAccountName` | Exact bank-account name alias; not the derived bank-account ID. |
| Payment Document | `PaymentDocumentName` | Exact document name in the resolved bank context; not document ID. |
| Payment Process Profile | `PaymentProfileName` | Exact profile name in the applicable context; not profile code or ID. |
| Funding Card Account | `FundingCardAccount` | Use user inputs directly. Retain the supplied value as-is; no verification, validation, lookup or conversion. |
| Payment Conversion Rate Type | `PaymentConversionRateType` | Exact `UserConversionType` alias, such as an existing Corporate display value; not internal `ConversionType` or REST `ConversionTypeId`. |
| Cross-Currency Rate Type | `CrossCurrencyRateType` | Exact `UserConversionType` alias; not internal conversion code or REST ID. |
| First Approver | `FirstApprover`, `PersonNumber` | Use user inputs directly. Retain supplied values as-is; no verification, validation, name/number pairing check or derivation. |
| Transaction Calendar | `TransactionCalendar` | Use user inputs directly. Retain the supplied value as-is without verification or validation; the existing import-assignment limit remains separate. |
| Pay-group members | `ORA_PPR_PAY_GROUP.VendorPayGroupName` | Exact `PAY GROUP` lookup Meaning, application 200; not the lookup code. |
| Currency members | `ORA_PPR_CURRENCY_GROUP.CurrencyCode` | Actual currency code; not currency name or combined UI display text. |
| Business-unit members | `ORA_PPR_BU_GROUP.Name` | Exact business-unit name in the enterprise context; not BU ID or the alternate UI binding name `XBuName`. |
| Legal-entity members | `ORA_PPR_LE_GROUP.LegalEntityIdentifier` | Exact legal-entity identifier used by the resolver; a legal-entity display name is not a substitute for this key. |
| Source members | `ORA_PPR_SOURCE_GROUP.InvoiceSourceName` | Exact `SOURCE` lookup Meaning, application 200; not `InvoiceSourceCode`. |
| Bank Conversion Rate Type | No confirmed CSV column | Use user inputs directly. Retain the supplied value as-is in the request/blueprint and preview without verification or validation; do not invent an import column. |

Each supplied membership row also carries the exact
`ORA_PAYMENT_PROCESS_REQUEST_TEMPLATES.TemplateName` parent-reference column.
Do not serialize an internal TemplateId. Root `TemplateName` is the exact
business identity/name; `Description` is free text. Dates and numeric fields
are typed input, not lookup codes or names: follow
[input validation](../ora-resource/ora_input_validation.md) for their accepted
formats, ranges and per-operation treatment. Keep DFF context/value-set gaps
explicit rather than constructing new dropdown lists.

For other fields, apply the resolver, eligibility and lifecycle limits in
[reference contracts](../ora-resource/ora_reference_lookups.md).

## Lookup contexts

Use the configured alias resolvers in
[reference contracts](../ora-resource/ora_reference_lookups.md) with these exact
lookup types and view application IDs:

| CSV attribute | Lookup type | View application ID |
|---|---|---:|
| `TemplateTypeValue` | `PAYMENT_TEMPLATE_TYPE` | 200 |
| `PayOnlyWhenDue` | `AP_SELECT_BASED_ON` | 200 |
| `AcceleratedInvoicesOption` | `ORA_ACCELERATED_INVOICES` | 200 |
| `SupplierType` | `POZ_VENDOR_TYPE` | 0 |
| `PaymentMode` | `ORA_IBY_PAYMENT_MODE` | 0 |
| `InvoiceConversionRateType` | `INVOICE_EXCHANGE_RATE_TYPE` | 200 |
| `SettlementPriorityValue` | `IBY_SETTLEMENT_PRIORITY` | 0 |
| `BankChargeBearerOverride` | `IBY_BANK_CHARGE_BEARER` | 0 |
| `DocumentRejectionLevel` | `IBY_DOCUMENT_REJECTION_LEVELS` | 0 |
| `PaymentRejectionLevel` | `IBY_PAYMENT_REJECTION_LEVELS` | 0 |

## Supplier Type secondary validation

For supplied SupplierType, first match the names in the acceptable-value table. Normalize an unambiguous listed name to its exact spelling; blank is allowed. Listed values require no REST call. Omission preserves an update and leaves a new template's Supplier Type blank.

If a nonblank name is not listed, use resolve_supplier_type_rest in Reference Lookups. Read the current POZ_VENDOR_TYPE lookup in view application 0 through the Core REST client, then check its lookup codes for the exact Meaning. Accept one or more matching rows, including duplicates; retain the Meaning as SupplierType, not LookupCode. Continue paging only until a match is found or the filtered result is exhausted. Do not reject a valid unlisted name just because it is absent from this file.

Retain a prerequisite receipt with operationId, entity, field=SupplierType, resolver=resolve_supplier_type_rest, lookupContext={LookupType: POZ_VENDOR_TYPE, ViewApplicationId: 0}, evidence (the response artifact reference), and restResult={httpStatus, items}. The items must include at least one exact Meaning matching the normalized candidate value. The offline adapter requires this receipt for an unlisted supplied value on create or update, including build and candidate validation. A receipt for another field, operation, value or lookup context cannot satisfy the check. Unrelated updates do not revalidate a retained Supplier Type.

An exhausted successful response with no matching Meaning fails secondary validation and requests a listed or returned valid name. Missing lookup visibility, unsupported API access, authentication, transport or malformed-response failures block validation with their own cause; they do not establish that the name is invalid. Do not silently fall back to import after the required secondary check is unavailable. The read-only workflow owns response acquisition and provenance; an offline receipt check is not live-source verification.
