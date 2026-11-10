# Source XML Data Definition

## Provenance

This skill-local source contract is the durable reference for Oracle Payments funds-disbursement ISO template generation. It was derived from reviewed Oracle Payments extract logic, the `IBY_XML_FD_INS_1_0_V` view contract, nested generated XML fragments, bundled working templates, and masked source XML samples. Do not browse external documentation to rediscover this contract during normal generation.

`IBY_FD_EXTRACT_GEN_PVT.Create_Extract_1_0_Main` generates the source XML by setting the `PMT_INSTR_ID` view parameter and reading `XMLType.getBlobVal(instruction, IBY_UTILITY_PVT.G_NLS_CHARSET_UTF8)` from `IBY_XML_FD_INS_1_0_V` for the requested `payment_instruction_id`.

The extracted view exposes the XML payload as `INSTRUCTION` and the key as `PAYMENT_INSTRUCTION_ID`. The top-level view query uses `IBY_EXT_FD_INS_1_0_V ins` and `FND_CURRENCIES_VL fnd_curr`; nested XML fragments are produced through helper logic for ledger currency, payment-instruction account settings, payer, payer bank account, payer instructions, flexfield values, branch extensions, and payment-level details.

The root source XML is un-namespaced:

```xml
<OutboundPaymentInstruction>...</OutboundPaymentInstruction>
```

## Top-Level Structure

```text
OutboundPaymentInstruction
  RecordHistory
    CreatedBy
    CreationDate
    LastUpdateDate
    LastUpdateLogin
    LastUpdatedBy
  LedgerCurrency?                              # when ORA_IBY_FETCH_TRX_TAX_DETAILS is enabled
    Currency
      Code
  PaymentInstructionInfo
  PaymentProcessProfile
  PaymentFormat
  CheckFormatInfo?
  InstructionTotals
  InstructionGrouping
  AcknowledgementDetails?
  FederalPFExtend?
  OutboundPayment*                             # from payment-level generated XML view
  Extend*                                      # extension fragments when extension packages return XML
```

## PaymentInstructionInfo

```text
PaymentInstructionInfo
  InstructionReferenceNumber
  FormatProgramRequestID
  InstructionCreationDate
  MultiOrgAccessControl
    HasBlockedData
  InstructionStatus
    Code
    Meaning
  ProcessingType
    Code
    Meaning
  ProcessType
  UserAssignedRefCode
  PaymentMode
  BankAssignedRefCode
  PaymentSequence*                             # three sequence nodes may be emitted
    SequenceName
    LastValue
  BankInstruction*                             # bank instruction 1 and 2
    BankInstructionCode
    Meaning
    FormatValue
  BankInstructionDetails
  PaymentTextMessage*                          # message 1 and 2
  RegulatoryReportingOption
  CCRemitFileSequenceNumber?
  CCRemitFileVersionNumber?
  PaymentSystemAccount
    AccountName
    AccountSettings*                           # from IBY_XML_FD_ACCT_SETTINGS_1_0_V
      Name
      Value
    DescriptiveFlexField
      Extend*
  Notes
  DescriptiveFlexField?
    Extend*
```

Common account setting names used by working templates include:

- `ISO20022_IP_NAME`, `ISO20022_IP_BICORBEI`, `ISO20022_IP_OTHERID`
- `ISO20022_DR_BICORBEI`, `ISO20022_DR_OTHERID`, `ISO20022_DR_ID_SCHME_NAME`
- `CGI_INITIATING_PARTY_NAME`, `DEBTOR_NAME`

Do not add a new account-setting dependency unless the bank setup page or source XML sample proves it is emitted as `PaymentSystemAccount/AccountSettings`.

## PaymentProcessProfile And PaymentFormat

```text
PaymentProcessProfile
  PaymentProcessProfileInternalID
  PaymentProcessProfileName
  BatchBookingFlag
  LogicalGrouping
    GroupByPaymentDateLogical
    GroupByBankAccountLogical
    GroupBySettlementPriority
    GroupByServiceLevel
    GroupByBankChargeBearer
    GroupByUltimateDebtor
    GroupByCategoryPurpose
    GroupByPaymentMethod
  DescriptiveFlexField
    Extend*

PaymentFormat
  PaymentFormatInternalID
  PaymentFormatName
  DescriptiveFlexField
    Extend*

CheckFormatInfo?
  PaymentDocumentName
  PaperStockType
    Code
    Meaning
```

## InstructionTotals And InstructionGrouping

```text
InstructionTotals
  PaymentCount
  TotalPaymentAmount
    Value
    Currency
      Code

InstructionGrouping
  PaymentDate?
  PaymentCurrency?
    Code
    Name
  PaymentServiceRequestID?
  Payer
  PayerOrganization?
    OrganizationInternalID
    OrganizationType
      Code
      Meaning
    OrganizationName
  BankAccount
  PaymentReason?
    Code
    Meaning
    FormatValue
  PaymentReasonComments?
  FunctionalCategory?
    Code
    Meaning
  FederalRFCIdentifier?
```

`Payer` is resolved by selecting a payment from `IBY_PAYMENTS_ALL`, then calling `Get_Payer_Denorm`, which fetches `payer` from `IBY_XML_FD_PAYER_1_0_V`.

`BankAccount` is resolved by selecting a payment from `IBY_PAYMENTS_ALL`, then calling `Get_PayerBankAccount_Denorm`, which fetches `int_bank_account` from `IBY_XML_FD_PRBA_1_0_V`.

## OutboundPayment

`OutboundPayment` fragments are returned by `Get_Ins_PayerInstrAgg`. For normal payment extracts the package aggregates `IBY_XML_FD_PMT_1_0_V.payment` filtered by payment instruction, run mode, process type, reprint state, and payment status.

Common source paths used by the generic, JPM, and PNC templates:

```text
OutboundPayment
  LogicalGrouping
    LogicalGroupReference
    PaymentInformationTotal
    PaymentInformationAmountTotal
  PaymentMethod
    PaymentMethodFormatValue
  PaymentDate
  SettlementPriority
    Code
  ServiceLevel
    Code
    FormatValue
  DeliveryChannel
    Code
    FormatValue
    Meaning
  BankCharges
    BankChargeBearer
      Code
  PaymentReason
    Code
    Meaning
    FormatValue
  PaymentSourceInfo
    EmployeePaymentFlag
  PaymentNumber
    PaymentReferenceNumber
    CheckNumber
  PaymentAmount
    Value
    Currency
      Code
  Payer
    Name
    LegalEntityInternalID
    LegalEntityName
    LegalEntityRegistrationNumber
    TaxRegistrationNumber
    Address
    ContactInfo
  BankAccount
    BankAccountNumber
    IBANNumber
    BankAccountName
    BankAccountType
      Code
    BankAccountCurrency
      Code
    EFTUserNumber
      EFTRequesterId
    SwiftCode
    BranchNumber
    BankName
    BankAddress
      AddressLine1
      City
      State
      Country
  InvoicingLegalEntity
  PayeeBankAccount
  SupplierorParty
  Payee
  DocumentPayable*
```

## Payee, Supplier, And Bank Account Fragments

Working templates rely on these paths. Verify exact availability from a sample XML if the bank spec makes them mandatory.

```text
PayeeBankAccount
  BankAccountNumber
  IBANNumber
  BankAccountName
  BankAccountType
    Code
  BankAccountCurrency
    Code
  SwiftCode
  BranchNumber
  BankName
  BankAddress
    AddressLine1
    City
    Country
  IntermediaryBankAccount*
    SwiftCode
    BranchNumber
    BankName
    Country

SupplierorParty
  Name
  SupplierNumber
  PartyNumber
  FirstPartyReference
  TaxRegistrationNumber
  LegalEntityRegistrationNumber
  PartyInternalID
  Address

Payee
  Name
  SupplierNumber
  PartyNumber
  FirstPartyReference
  TaxRegistrationNumber
  TaxOrganizationType
    Code
  LegalEntityRegistrationNumber
  PartyInternalID
  Address
  ContactInfo
    ContactLocators
      PhoneNumber
      FaxNumber
      EmailAddress
      Website
  PersonInfo
    BirthDate
    TownOfBirth
    CountryOfBirth
```

## DocumentPayable

```text
DocumentPayable
  DocumentNumber
    ReferenceNumber
    UniqueRemittanceIdentifier
      Number
  DocumentDate
  DocumentDescription
  DocumentType
    Code
  TotalDocumentAmount
    Value
    Currency
      Code
  DiscountTaken
    Amount
      Value
      Currency
        Code
  TotalDocumentTaxAmount
    Value
    Currency
      Code
  AmountWithheld
    Value
    Currency
      Code
  PaymentAmount
    Value
    Currency
      Code
  DeliveryChannel
    Code
    FormatValue
    Meaning
  RemittanceMessage*
  PONumber
  Extend*
  DocumentPayableLine*
    LineNumber
    PONumber
    LineType
      Code
    LineDescription
    LineGrossAmount
      Value
      Currency
        Code
        NumericCode
    Tax
      TaxCode
      TaxRate
      TaxRateCode
```

## Extension And Conditional Fragments

- `FederalPFExtend` is only populated for federal payment or summary extract run modes through `FV_PAY_INTEGRATION_PUB_PKG.gen_instr_extract_tags`.
- `iby_fd_extract_ext_pub.get_ins_ext_agg` may append instruction-level extensions.
- `Get_Ins_BR_Ext_Agg` calls `JG_FD_EXTRACT_EXT_PUB.Get_Ins_Ext_Agg` only when the country-specific collection document feature is enabled for the business unit.
- DFF values are exposed under `DescriptiveFlexField/Extend` or document-level `Extend` fragments. Treat DFF field names as implementation-specific and verify in a source XML sample.

## Practical Mapping Rules

- Use source XML paths from this reference or from inspected sample XML. Do not invent paths.
- Prefer existing setup-derived values for bank-assigned IDs: `PaymentSystemAccount/AccountSettings`, `BankAccount/EFTUserNumber/EFTRequesterId`, `DeliveryChannel/FormatValue`, and DFF `Extend` values.
- For ISO output fields with strict lengths, use `substring(...)` in XSL and document the truncation in the mapping matrix.
- For values conditioned by country, service level, delivery channel, or payment method, encode the condition directly in XSL and add a mapping row for each branch.
- Mark unresolved source gaps explicitly so the user can decide whether to add setup fields, DFFs, or upstream extract extensions.
