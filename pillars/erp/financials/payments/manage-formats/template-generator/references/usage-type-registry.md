# Oracle Payments Usage Type Registry

Use this registry to route template-generation work. Keep this file concise; detailed implementation belongs in the child skill for each usage type.

## Current Routes

| Usage type | Subtype | Source contract | Output type | Route |
| --- | --- | --- | --- | --- |
| Funds Disbursement | ISO 20022 credit transfer, CGI, SEPA, ACH/check/wire variants | `OutboundPaymentInstruction` XML generated from `IBY_XML_FD_INS_1_0_V` and related Oracle Payments package logic | Bank-specific XSLT producing ISO pain.001 XML | `generate-bank-iso-templates` |
| Account Validation Service | Bank account owner verification provider request/response | Generic AVS bank-account verification XML derived from `Create_Ba_Ownr_Verif_Extract_1_0` and AVS request views | Provider request/response XSLT, XML/JSON mapping notes, XSD/data-definition artifacts | `generate-avs-provider-templates` |
| Virtual Card Payments | Outbound payment, inbound acknowledgment, payment response, and reconciliation | Enriched `OutboundPaymentInstruction` for outbound; `AckResponse`, `records/record`, and `reconRcrd/reconDetls` as normalized inbound contracts | Provider XSLT for ISO pain.001/pain.002, XML, JSON-through-XML, CSV-converted XML, or eText profiles | `generate-virtual-card-provider-templates` |

## Future Route Placeholders

| Usage type | Subtype | Expected source/output | New child-skill direction |
| --- | --- | --- | --- |
| Funds Capture | Bank EFT / ISO direct debit | Source XML contract and generic template are TBD; likely ISO direct debit XML such as pain.008 or bank-specific debit output | Create a focused `generate-bank-direct-debit-templates` or similarly named child skill after source XML, generic templates, and validation samples are identified. |
| Funds Capture | Credit card payment gateway | Source contract, gateway request/response envelopes, and runtime conversion pattern are TBD; output may be JSON, XML, or eText depending on gateway integration | Create a focused payment-gateway child skill after reviewing existing gateway templates, provider specs, masking rules, and response normalization requirements. |

## New Category Checklist

Before generating a template for an unregistered category, collect:

- Oracle flow and product area.
- PL/SQL package, view, extract, or source payload that produces the generic source.
- Source XML/JSON/eText sample and a masked durable test sample.
- Target output format and runtime processor.
- Existing seeded/generic templates and at least one working provider or bank example.
- Provider/bank specification and expected sample outputs.
- Validation method, including compile/load checks and runtime transform checks.
- Security handling for account data, PII, credentials, endpoints, headers, and connectivity attributes.

Add a route only when these inputs are stable enough for repeatable generation.
