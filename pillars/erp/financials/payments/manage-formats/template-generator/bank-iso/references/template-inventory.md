# Template Inventory

## Closed Skill Reference Package

Use the bundled references as the authoritative local package when generating or reviewing bank ISO templates. The skill is intended to work as a closed unit: do not rely on external repositories, external web documentation, original workarea paths, SharePoint, Confluence, or raw bank partner documents during normal generation.

Bundled Oracle seed XSL templates:

- `references/template-generation/iso/ISO20022CGI2019.xsl`
- `references/template-generation/iso/ISO20022SEPAV7_0.xsl`
- `references/template-generation/jpm/jpm-templates/JPMCISO20022CGI.xsl`
- `references/template-generation/jpm/jpm-templates/JPMISO20022CGIV2.xsl`
- `references/template-generation/jpm/jpm-templates/JPMISO20022SEPA.xsl`
- `references/template-generation/pnc/PNCISO20022CGI.xsl`

Bundled ISO schemas:

- `references/iso-schemas/pain.001.001.03.xsd`
- `references/iso-schemas/pain.001.001.09.xsd`
- `references/iso-schemas/pain.001.001.13.xsd`
- `references/iso-schemas/pain.008.001.12.xsd`

Bundled reference notes and fixtures:

- `references/iso-schema-inventory.md`
- `references/iso-template-patterns.md`
- `references/test-scenario-generation.md`
- `assets/validation/source-xml/DataTest_masked.xml`
- `assets/validation/source-xml/delivery-channel-samples/`
  - 19 masked source XML fixtures extracted from the delivery-channel sample set.
  - Use these for broad source-contract and delivery-channel branch coverage. They are not all expected to pass every bank-specific template gate.
- `assets/validation/source-xml/synthetic-scenarios/`
  - 8 masked, bank-neutral synthetic source XML fixtures covering CCD, CCD+, US wire, Canada local clearing, Australia local clearing, New Zealand local clearing, EUR IBAN, and cross-border USD SWIFT scenarios.
  - Use these as neutral scenario seeds. For any runtime bank specification, create bank-specific validation copies by applying the completed country/rail matrix.
- `assets/validation/scenario-catalog/iso-source-scenarios.json`
  - Scenario metadata and dynamic override fields for deriving runtime bank-specific validation XMLs from the neutral fixtures.

Raw JPM/PNC specification workbooks, partner PDFs, and the combined PNC/JPM mapping workbook are intentionally excluded. Reusable guidance from the retained Oracle seed XSL templates is captured in `references/iso-template-patterns.md`.

Validation note: the bundled generic ISO, SEPA, PNC, and JPM templates are included as reference material and comparison anchors. `references/template-generation/jpm/jpm-templates/JPMISO20022CGIV2.xsl` is known to fail .NET XSLT loading because variable `endtoend` is declared twice in the same scope; keep that finding as a validation caveat rather than treating it as a packaging error.

## Generic ISO Folder

`references/template-generation/iso`

- `ISO20022CGI2019.xsl`
  - Generic CGI template.
  - XSLT 1.0.
  - Root match: `OutboundPaymentInstruction`.
  - Output namespace: `urn:iso:std:iso:20022:tech:xsd:pain.001.001.09`.
  - Groups `OutboundPayment` by `LogicalGrouping/LogicalGroupReference`.
- `ISO20022SEPAV7_0.xsl`
  - Generic SEPA template.

## JPM Seed Template Folder

`references/template-generation/jpm/jpm-templates`

- `JPMCISO20022CGI.xsl`
- `JPMISO20022CGIV2.xsl`
- `JPMISO20022SEPA.xsl`

Observed JPM template patterns are summarized in `references/iso-template-patterns.md`.

## PNC Seed Template Folder

`references/template-generation/pnc`

- `PNCISO20022CGI.xsl`

Observed PNC template patterns are summarized in `references/iso-template-patterns.md`.
