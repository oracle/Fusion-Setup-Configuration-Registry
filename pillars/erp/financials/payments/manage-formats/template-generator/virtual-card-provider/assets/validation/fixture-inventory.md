# Test Fixture Inventory

## Outbound Source XML

| File | Origin | Coverage | Handling |
| --- | --- | --- | --- |
| `assets/validation/source-xml/virtual_card_outbound_synthetic_masked.xml` | Fully synthetic Oracle `OutboundPaymentInstruction` | One generic virtual-card payment and the core virtual-card extensions | Safe for persistent regression use |
| `assets/validation/source-xml/virtual_card_outbound_full_extract_masked.xml` | Masked derivative of a two-payment Oracle test-environment extract | Two `OutboundPayment` records, payment instrument, card program, digital payment account, supplier-site attributes, invoices, remittance data, and account settings | Raw extract is not bundled; identifiers, names, addresses, emails, account numbers, amounts, dates, credentials, and connectivity/configuration values were replaced |

The full-extract fixture retains non-sensitive application codes, flags, meanings, country metadata, setting names, and extension names needed to preserve execution branches. Empty `ServiceLevel/FormatValue`, `CardProgramDetails/ExtMCCGroupCode`, and `PaymentInstrument/NetworkInstrumentIdentifier` fields were populated with synthetic values because the bundled seed XSLT emits their target elements unconditionally. A synthetic `BANK_IDENTIFIER` value and missing supplier `VendorId`, `PartySiteId`, or `SiteId` values were also completed so sender and registered-supplier mappings can be validated. This makes the fixture useful for schema-valid regression without changing its payment cardinality or contract topology.

FSCR packaging hygiene: six inherited contact-address occurrences were replaced with explicit `synthetic-contact-N@example.invalid` addresses. Repeated-value relationships are preserved. This sanitation changes fixture values only; source paths, cardinality, amounts, mappings and seed templates are unchanged.

## Inbound Fixtures

| File | Profile |
| --- | --- |
| `assets/validation/inbound/pain002_ack_accepted_synthetic.xml` | ISO `pain.002.001.03` acknowledgment |
| `assets/validation/inbound/payment_response_generic_xml_synthetic.xml` | Generic converted-XML payment response |
| `assets/validation/inbound/reconciliation_generic_xml_synthetic.xml` | Generic converted-XML reconciliation |

## Rules

- Never bundle the raw source extract.
- Do not use fixture values as provider requirements or mapping evidence.
- Validate generated templates against both outbound fixtures when the provider consumes the Oracle `OutboundPaymentInstruction` contract.
- Add future fixtures only after deterministic masking and a residual-value review.
