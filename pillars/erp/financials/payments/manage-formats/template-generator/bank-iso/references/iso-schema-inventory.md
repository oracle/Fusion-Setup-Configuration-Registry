# ISO Schema Inventory

Use these bundled XSD files for local schema awareness and output validation. Choose the schema that matches the namespace emitted by the generated XSL `<Document>` element; do not validate one pain version against another pain version.

## Bundled Schemas

- `references/iso-schemas/pain.001.001.03.xsd`
  - Customer Credit Transfer Initiation V03.
  - Common for legacy CGI and SEPA credit-transfer seed templates.
  - Use when the bank specification or chosen seed template emits namespace `urn:iso:std:iso:20022:tech:xsd:pain.001.001.03`.
- `references/iso-schemas/pain.001.001.09.xsd`
  - Customer Credit Transfer Initiation V09.
  - Use with the bundled generic CGI 2019 seed template.
  - Use when the generated output namespace is `urn:iso:std:iso:20022:tech:xsd:pain.001.001.09`.
- `references/iso-schemas/pain.001.001.13.xsd`
  - Customer Credit Transfer Initiation V13.
  - Use when a bank explicitly asks for V13 or when comparing current ISO structure against an older bank profile.
  - Do not upgrade a bank from V03 or V09 to V13 unless the bank specification says to do so.
- `references/iso-schemas/pain.008.001.12.xsd`
  - Customer Direct Debit Initiation V12.
  - Included for future Funds Capture / ISO direct-debit expansion.
  - Do not use as the default SEPA direct-debit schema unless the target requirement names this exact version.

## Validation Rules

- Match validation to the generated `Document` namespace.
- Treat schema validity as necessary but not sufficient; bank implementation guides may suppress optional ISO elements or require stricter conditional logic.
- Keep the country/rail matrix authoritative for `CdtrAgt`, `IntrmyAgt`, `ClrSysMmbId`, `Othr/Id`, BIC, local clearing codes, and postal-address shape.
- If a bank asks for classic SEPA direct debit and names `pain.008.001.02`, that schema is not currently bundled and should be added before generating that profile.
