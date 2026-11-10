# Oracle Virtual Card Contracts

This is a maintained knowledge extract from Oracle implementation code, seeded templates, and internal design material. It is not a copy of any Confluence page and has no runtime dependency on Confluence. The current implementation excerpts and revisions are bundled under [source-code/source-manifest.md](source-code/source-manifest.md).

## Contract Topology

Virtual-card processing has four template profiles:

1. Outbound payment initiation.
2. Inbound disbursement acknowledgment.
3. Inbound payment response.
4. Inbound reconciliation.

Card statements and settlement invoice creation are separate downstream flows.

## Outbound Source

The outbound XSLT consumes `OutboundPaymentInstruction`. Virtual-card payments reuse the Funds Disbursement source XML and add these nodes under each `OutboundPayment`:

```xml
<PaymentInstrument>
  <PaymentInstrumentInternalId/>
  <PaymentInstrumentName/>
  <NetworkInstrumentIdentifier/>
  <PaymentInstrumentCurrency><Code/></PaymentInstrumentCurrency>
  <BankDetails><BankCountry/></BankDetails>
</PaymentInstrument>
<CardProgramDetails>
  <ExtCompanyId/>
  <ExtMCCGroupCode/>
  <CardProgramSetup><Extend><Name/><Value/></Extend></CardProgramSetup>
  <TemplateSetup><Extend><Name/><Value/></Extend></TemplateSetup>
  <TemplateControls><Extend><Name/><Value/></Extend></TemplateControls>
  <AdditionalAttributes><Extend><Name/><Value/></Extend></AdditionalAttributes>
</CardProgramDetails>
<DigitalPaymentAccount>
  <DigitalPaymentAccountInternalId/>
  <Token/>
  <TokenTypeCode/>
  <Alias/>
  <AliasTypeCode/>
  <CurrencyCode/>
  <PaymentModeCode/>
  <STPEnabled/>
  <AdditionalAttributes/>
  <PayeeVCAttributes>
    <VCRegisteredSupplier/>
    <Alias2/><Alias3/><Alias4/><Alias5/>
    <VendorId/><PartySiteId/><SiteId/>
  </PayeeVCAttributes>
</DigitalPaymentAccount>
```

### Source Tables

| XML area | Main sources |
| --- | --- |
| Payment instrument | `CE_PAYMENT_INSTRUMENTS`, `IBY_PAYMENTS_ALL`, `CE_INDEX_BANKS` |
| Card program | `IBY_VCARD_PROGRAMS_B`, `IBY_VCARD_PROGRAM_FCA_USES`, `IBY_INSTR_CTL_TEMPLATES_B` |
| Setup extensions | `IBY_SETUP_EXTENSIBILITY` |
| Template controls | `IBY_INSTR_CTL_TEMPLT_OPT_VALS`, `IBY_INSTR_CTL_TEMPLT_OPTS_B`, `IBY_INSTR_CTL_TEMPLT_OPTS_TL` |
| Digital payment account | `IBY_DIGITAL_PAYMENT_ACCOUNTS`, `IBY_PAYMENTS_ALL` |

The code assembles these fields in `iby_fd_extract_gen_pvt.pkb`; `IBY_XML_FD_PMT_1_0_V` appends the returned XML to `OutboundPayment`. `BankDetails/BankCountry` and `CardProgramDetails/ExtMCCGroupCode` are emitted only by the current JPM virtual-card opt-in branch, so they are not unconditional source fields. See [outbound-contract-source.md](source-code/outbound-contract-source.md).

## Acknowledgment Normalized Output

Provider acknowledgment XSLT must produce:

```xml
<AckResponse>
  <PmtHeader>
    <MsgId/><MsgSts/><MsgStsCd/><MsgErrCd/><MsgErrDet/>
  </PmtHeader>
  <PmtDetls>
    <PmtRef/><PmtSts/><PmtStsCd/>
    <PmtMsgErrCd/><PmtMsgErrDet/>
    <PmtClearingNum/><InvHoldCd/>
  </PmtDetls>
</AckResponse>
```

`PmtDetls` repeats. `FDBatchAckParser` consumes these exact names using namespace-agnostic `local-name()` XPath. `MsgStsCd` and `PmtStsCd` are Oracle application statuses such as `ACKNOWLEDGED` or `REJECTED`; the raw provider status belongs in `MsgSts` or `PmtSts`. The consumer shortens error-detail values to 254 characters when their input exceeds 255 characters.

Relevant account options: `FD_ACK_FORMAT`, `FD_ACK_TRANS_CONFIG`, `FD_ACK_AUTO_VOID_OPTION`, `FD_ACK_VOID_INVOICE_ACTION`, and PCI transmission options where configured.

## Payment Response Normalized Output

Provider payment-response XSLT must produce:

```xml
<records>
  <record>
    <paymentRefNum/>
    <bepStatus/>
    <bepTrxnResponseId/>
    <bepErrorCode/>
    <bepErrorMessage/>
    <invHoldCode/>
  </record>
</records>
```

`FDAckProcessing.parseAndUpdatePaymentResponse` consumes these names using namespace-agnostic `local-name()` XPath and calls `iby_disburse_ui_api_pub_pkg.vc_pmt_response_update`. `paymentRefNum` is mandatory for correlation. The consumer shortens `bepErrorCode` to 29 characters when input exceeds 30 and `bepErrorMessage` to 254 when input exceeds 255. Relevant account options include `FD_PAYMENT_RESP_FORMAT`, `FD_PAYMENT_RESP_TRANS_CONFIG`, and `VC_INBOUND_FILE_DELIMITER`.

## Reconciliation Normalized Output

Provider reconciliation XSLT must produce:

```xml
<reconRcrd>
  <reconDetls>
    <authCode/>
    <paymentRef/>
    <settlmntDate/>
    <acquirerRef/>
    <settlmntCurr/>
    <transactionAmt/>
    <transactionDate/>
    <transactionId/>
  </reconDetls>
</reconRcrd>
```

`reconDetls` repeats. `VirtualCardPaymentReconciliation` consumes each record using namespace-agnostic `local-name()` XPath, updates AP settlement/reconciliation data, and updates IBY payment status. The provider specification must identify the payment correlation field and transaction uniqueness rule, including partial or multiple swipes.

Relevant settings include `FD_RECONCILIATION_FORMAT`, `FD_RECONCILIATION_TRANS_CONFIG`, `VC_RECON_PCI_TRANS_CONFIG`, `VC_INBOUND_FILE_DELIMITER`, and `VC_RECONCILIATION_FILE_EXTENSION`.

## Provider Behavior Knowledge

- JPM outbound virtual-card payments use an ISO `pain.001.001.03` pattern.
- JPM acknowledgment uses ISO `pain.002.001.03` normalized to `AckResponse`.
- The implemented JPM payment response and reconciliation flows convert delimited input to generic XML before applying XSLT.
- PNC design material proposes `pain.001` outbound, an existing `pain.002` acknowledgment pattern, and `pain.002` reconciliation. Treat unfinished design statements as candidates until confirmed by a provider specification and implemented seed data.
- Mastercard can use request/response APIs and notification payloads rather than JPM-style response files. Classify each operation by its actual runtime preprocessing contract.

## Generation Gates

Do not generate a final template until these are resolved for each profile:

| Gate | Required decision |
| --- | --- |
| Correlation | Exact source for payment instruction, payment reference, and provider transaction identifiers |
| Status | Provider-to-Oracle success, pending, partial, rejection, and error mappings |
| Repetition | File, batch, payment, transaction, and swipe cardinalities |
| Amount/date | Currency, decimal precision, sign, timezone, and date formatting |
| PCI | Whether PAN, token, authorization, or other PCI fields enter the template boundary |
| Input conversion | Raw XML, JSON-to-XML, CSV-to-generic-XML, fixed-width conversion, or eText |
| Error handling | Required rejection codes, invoice hold, auto-void, retry, and unknown-status behavior |

### Outbound Cross-Field Checks

- Validate uniqueness after every provider-required truncation or normalization. Schema-valid identifiers can still collide.
- Keep each payment-information group homogeneous for provider account/program, currency, and any account-pool rule. Split or reject mixed groups according to the provider specification.
- Map structured-remittance amounts from each `DocumentPayable`, including `DocumentPayable/PaymentAmount`; do not repeat the parent `OutboundPayment/PaymentAmount` for every invoice.
- Enforce provider and XSD repetition limits independently, including maximum documents per payment and `AddtlRmtInf` occurrences.
- Validate the provider-supported enrollment mode separately from identifier presence. Registered, registered-STP, and unregistered supplier branches are not interchangeable.
- Treat multiple authorization/swipe, partial settlement, force settlement, cancellation, and refund behavior as reconciliation contract requirements, not as incidental sample variations.
