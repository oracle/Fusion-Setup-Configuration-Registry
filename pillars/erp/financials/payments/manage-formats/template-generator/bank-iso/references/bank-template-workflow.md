# Bank Template Workflow

## 1. Review The Bank Specification

Extract these facts before writing XSL:

- Message type and version: CGI, SEPA, `pain.001.001.03`, `pain.001.001.09`, or another bank profile.
- Required namespaces and schema locations.
- Supported payment methods: transfer, check, ACH, wire, cross-border, book transfer, virtual card, or local rails.
- Required service levels and local instruments, such as `NURG`, `URGP`, `BKTR`, `CCD`, `CTX`, `PPD`, `FWT`, `BOP`, or bank-specific values.
- Country-specific branches for debtor bank country, creditor bank country, resident/nonresident payments, tax IDs, phone numbers, and purpose codes.
- Required account identifiers: IBAN, account number, clearing member ID, BIC, bank name, branch ID, EFT requester ID, company ID, sender ID, pool ID.
- Required remittance format: structured, unstructured, invoice-by-invoice, one line per document, credit note handling, withholding tax, or bank-specific addenda.
- Field length constraints and character cleanup requirements.
- Constants, hard-coded proprietary codes, and bank-assigned IDs.

If the spec is a spreadsheet, build a row-wise mapping table. If it is a PDF or Word guide, first extract the tag requirement tables and implementation notes into a concise mapping table.

For spreadsheet specs, review every bank-specific requirement column for each ISO row. Capture whether the element is required, optional, conditional, not applicable, or only valid for a named rail. Do not collapse the workbook into one generic required/not-required flag when the bank distinguishes ACH, wire, check, SWIFT, cross-border, country, or currency behavior.

Before generation, extract every country, currency, delivery-channel, service-level, local-instrument, bank-agent, and clearing-code note into `references/country-rail-matrix.md` format. Do not treat these notes as narrative background; they are generation gates.

## 2. Choose A Base Template

Use the closest working template:

- Generic CGI: standard ISO 20022 credit transfer, currently `pain.001.001.09`.
- Generic SEPA: SEPA-specific payment rules.
- PNC CGI: useful for `pain.001.001.03`, check handling, sender ID from `EFTRequesterId`, `CGI_INITIATING_PARTY_NAME`, `DEBTOR_NAME`, country-purpose logic, and truncation.
- JPM CGI: useful for large country/payment-mode matrices, SUA/card-like local instruments, DFF placeholders, WHT/remittance handling, and extensive structured/unstructured remittance branching.
- JPM SEPA: useful when the target bank profile is SEPA-like but still has bank-specific overrides.

Prefer adapting the generic template when bank deltas are small. Prefer adapting JPM or PNC only when their branching structure closely matches the new bank's complexity.

Use `iso-template-patterns.md` for reusable message patterns observed from the bundled Oracle seed XSL templates. Do not expect raw JPM/PNC specification workbooks in the skill bundle.

## 3. Build The Mapping Matrix

Use these columns:

- ISO element number
- Structural sequence
- Message element
- XML tag
- Multiplicity
- OOB source XPath
- OOB behavior
- Bank instruction
- Bank source XPath
- XSLT rule
- Required setup/DFF/account setting
- Status
- Validation note

Classify every row:

- `OOB`: generic template already satisfies the bank.
- `Override`: source exists but mapping/rule differs.
- `Constant`: bank requires a literal or proprietary code.
- `Setup`: bank requires a setup value, such as account settings or EFT requester ID.
- `DFF/Extend`: value must come from a descriptive flexfield or extension fragment.
- `Unsupported`: source XML does not currently expose the required value.
- `Open`: needs clarification or sample XML.

Apply this seed-reviewable mapping discipline:

- Treat each bank row as the authority for whether an ISO element should appear. A source value being available is not enough to emit an optional bank tag.
- Use generic ISO behavior only for structural ancestors, schema-mandatory values, and bank-silent rows where the standard Oracle mapping is clearly applicable.
- Use an existing seeded JPM/PNC/generic XSL rule as precedent only after the target bank row permits the element or does not constrain it.
- For conditional rows, capture the exact predicate from the bank spec. If the predicate is ambiguous, set status `Open` and suppress the generated branch until clarified.
- For rail-specific rows, record the allowed source signals such as `PaymentMethod/FormatValue`, `PaymentMethod/Code`, `DeliveryChannel/FormatValue`, `DeliveryChannel/Code`, `ServiceLevel/FormatValue`, country, currency, or account identifier availability.
- Record a validation note for rows deliberately omitted from XSL because they are optional, not applicable, source-missing, or conditionally unclear.

## 3A. Build The Country/Rail Matrix

Create a separate matrix for rail and country behavior before generating XSL. This matrix is required when the bank guide mentions any country-specific clearing, local rails, domestic wires, intermediary banks, BIC versus member-ID choices, local clearing codes, or party/address format variants.

At minimum, cover:

- The source predicate for each rail: `OutboundPayment/PaymentMethod/PaymentMethodFormatValue`, `PaymentMethod/Code`, `DeliveryChannel/FormatValue`, `DeliveryChannel/Code`, `ServiceLevel/FormatValue`, debtor country, creditor country, account country, payment currency, and account identifier availability.
- `DbtrAgt`, `CdtrAgt`, and `IntrmyAgt` identification rules, including BIC, `ClrSysMmbId/ClrSysId/Cd`, `ClrSysMmbId/MmbId`, `FinInstnId/Othr/Id`, bank name, branch id, and postal country.
- Local clearing codes and qualifiers such as US ABA, Australia BSB, Canada CPA, Russia BIK, or bank-proprietary code values.
- Account identifier precedence for debtor and creditor accounts: IBAN, local account, `Othr/Id`, scheme name, virtual/card identifiers, or setup IDs.
- Postal-address output shape for each party and agent: structured fields versus `AdrLine`, maximum lengths, required country/state/postcode behavior, and blank optional field suppression.
- Unsupported or open rows where the source XML does not expose the bank-required value.

Hard gates:

- Do not generate `CdtrAgt`, `IntrmyAgt`, `ClrSysMmbId`, `Othr/Id`, BIC, local clearing codes, or postal-address branches unless the matrix has a row that authorizes the output for the current source predicate.
- Do not let a generic ISO default override a bank-specific country or rail rule. If the bank rule is unclear, mark the row `Open` and suppress the branch unless required for schema validity.
- Do not use pain.001 target paths as source XPaths. Source XPaths must come from `OutboundPaymentInstruction`; paths beginning with `PmtInf`, `CdtTrfTxInf`, `CdtrAgt`, `DbtrAgt`, `IntrmyAgt`, or `RmtInf` are output paths and are invalid as source roots.

## 4. Generate XSLT

Follow these patterns:

- Keep XSLT 1.0 unless the runtime and existing payment format infrastructure explicitly support another version.
- Keep `<xsl:template match="OutboundPaymentInstruction">`.
- Keep `<xsl:key name="contacts-by-LogicalGroupReference" match="OutboundPayment" use="LogicalGrouping/LogicalGroupReference"/>` when grouping payments into `PmtInf` blocks.
- Emit the target ISO namespace on `<Document>`.
- Use `xsl:choose` for bank precedence rules; avoid deeply duplicated branches when a variable captures the bank decision.
- Use `substring(value, 1, length)` for bank length limits and document the limit in the mapping matrix.
- Use `format-number(amount, '##0.00')` for two-decimal ISO amounts unless the bank spec says otherwise.
- For negative document amounts, map credit-note fields deliberately; do not let negative signs leak into fields that require absolute amounts.
- Prefer `Code`, `FormatValue`, then fallback paths exactly as the mapping matrix states.
- Preserve comments only when they help maintain bank-specific rules.

Defaulting policy:

- Generate the smallest template that satisfies required and clearly-supported bank rows.
- Do not pass through `DeliveryChannel`, `ServiceLevel`, local instrument, category purpose, clearing system, or proprietary bank codes merely because they exist in the source XML. Emit them only when the bank row allows the exact value set for the rail.
- Prefer suppressing optional elements over producing plausible but undocumented ISO content.
- Prefer explicit branch predicates over catch-all branches for bank-controlled codes. If a catch-all is needed for schema validity, document it in the mapping matrix.
- Keep country, currency, and rail matrices separate so one rail's rule does not leak into another rail.
- For account and agent identification, follow the bank row precedence exactly: IBAN versus other account, BIC versus clearing member ID, bank name, branch ID, and proprietary IDs should not be interchangeable unless the bank guide says so.
- For `CdtrAgt`, `DbtrAgt`, and `IntrmyAgt`, implement the country/rail matrix literally. If the matrix says US Fedwire uses an ABA member ID and the guide also permits BIC, encode that precedence explicitly rather than relying on the order in which source fields happen to be populated.
- For `ClrSysMmbId`, emit `ClrSysId/Cd` only when the matrix identifies the rail/country clearing system. Emit `MmbId` only from a source field the matrix names.
- For `Othr/Id` under `FinInstnId`, emit it only when the bank guide has a matching proprietary/member/bank-ID row for the rail. Do not reuse account numbers, payer IDs, or arbitrary setup fields as financial-institution IDs.
- For postal addresses, implement the bank-specified shape per party. Do not mix `AdrLine` and structured tags (`StrtNm`, `BldgNb`, `PstCd`, `TwnNm`, `CtrySubDvsn`, `Ctry`) unless the guide explicitly allows that combination for the same party and rail.
- For remittance, generate only the lines required or clearly allowed by the bank guide. Put invoice, credit note, tax, discount, phone, purpose, and payment-reason addenda in explicit branches instead of generic unstructured output.

Do not:

- Invent source XML paths.
- Hard-code a bank-assigned ID unless the user confirms it is fixed for all accounts.
- Remove generic branches that are still required for other payment methods in the same bank template.
- Treat a mapping note or workbook row as implemented before the XSL contains the matching rule.
- Expand the output with optional bank elements just because the source XML exposes a candidate value.

## 5. Validate

Minimum validation:

1. Parse the generated XSL as XML.
2. Run `scripts/extract_xslt_usage.py` and inspect:
   - target namespace and root tags
   - source XPath inventory
   - account setting dependencies
   - conditional expressions
3. Compare source XPath roots to `references/source-xml-data-definition.md`.
4. Confirm every mandatory bank tag is generated or documented as unsupported.
5. Confirm every unsupported requirement has an explicit source gap.
6. Confirm every runtime bank workbook/spec row is mapped, suppressed with a reason, or listed as open.
7. Confirm each supported rail has an explicit branch or a documented reason why the generic branch covers it.
8. Confirm optional elements that the bank marks optional, conditional, or not applicable are not emitted unless the condition is met.
9. Confirm every generated bank-agent, clearing-code, `Othr/Id`, BIC, and postal-address branch maps back to the country/rail matrix.
10. Confirm no XPath in the generated XSL uses pain.001 target output paths as source data.
11. Confirm no generated amount is `NaN` and no mandatory leaf element is empty in sample output.

When sample XML is available:

1. Transform the sample `OutboundPaymentInstruction` XML.
2. Parse the generated pain.001 XML.
3. Validate namespace, root structure, counts, control sums, debtor/creditor account identifiers, remittance blocks, and country/payment-method branches.
4. Compare output against the bank guide examples or expected sample output.

When the user does not provide bank-specific sample XML, use `references/test-scenario-generation.md` and `assets/validation/scenario-catalog/iso-source-scenarios.json`:

1. Select only neutral scenarios that correspond to rails, countries, currencies, and account/agent identifiers supported by the bank guide.
2. Create runtime copies outside the skill package and override service level, delivery channel, country, currency, account identifier, agent identifier, clearing-code, intermediary-agent, postal-address, and remittance inputs from the completed country/rail matrix.
3. Transform those runtime variants and validate the generated output against both the ISO schema and the bank matrix.
4. Do not alter the XSL merely to pass a bundled neutral fixture whose rail is outside the bank specification.

## 6. Final Deliverable Checklist

- `.xsl` template is well-formed.
- Mapping matrix covers mandatory and conditional bank requirements.
- All source paths are available in source XML or listed as gaps.
- Bank setup dependencies are called out.
- Validation output is summarized with exact checks.
- Remaining assumptions are concise and actionable.
