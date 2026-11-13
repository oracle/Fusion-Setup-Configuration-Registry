# Test Scenario Generation

## Purpose

Use the bundled masked XML fixtures as bank-neutral validation inputs for generated ISO templates. They are not bank specifications and they do not define bank requirements.

The runtime bank specification and the derived country/rail matrix are authoritative. The fixtures only provide source XML structure and common rail/country/account patterns that can be adjusted for validation.

## Bundled Fixture Types

- `assets/validation/source-xml/DataTest_masked.xml`
  - A masked full source XML example for broad structural inspection.
- `assets/validation/source-xml/delivery-channel-samples/`
  - Masked delivery-channel source examples for branch coverage and source-shape review.
  - Do not treat these as positive-path fixtures for any specific bank.
- `assets/validation/source-xml/synthetic-scenarios/`
  - Bank-neutral synthetic positive-path fixtures for common ISO credit-transfer patterns.
  - The scenario catalog is `assets/validation/scenario-catalog/iso-source-scenarios.json`.

## Runtime Variant Rule

When generating or validating a template for a new bank, create bank-specific runtime copies of the neutral synthetic scenarios after the mapping matrix and country/rail matrix are complete.

For each supported bank rail/country/currency combination:

1. Select the closest neutral scenario from `iso-source-scenarios.json`.
2. Override source XML values to represent the reviewed source-to-bank mapping in the bank matrix (source setup codes may legitimately differ from bank output codes):
   - service level and delivery channel
   - debtor and creditor country
   - payment currency
   - local account versus IBAN
   - BIC versus local clearing member ID
   - local clearing system code and member ID shape
   - intermediary-agent presence and identifier type
   - postal address structure
   - remittance-related source values when the bank condition depends on them
3. Keep generated values masked and synthetic.
4. Save runtime variants outside the skill package unless the user explicitly asks to promote a new generic fixture into the skill.

## Validation Rule

Use neutral fixtures for basic structural validation and bank-specific runtime variants for offline bank-rule validation. These checks do not establish bank acceptance.

Do not hard-code a generated XSL to pass the bundled fixtures. If a fixture does not represent a supported rail in the bank specification, skip it and record that it is outside the bank matrix.

Fail validation when a generated template emits agent, clearing, account, or postal-address structures that are not traceable to the runtime country/rail matrix.

## Runtime-shape coverage

Use `assets/validation/scenario-catalog/runtime-shape-cases.json` after constructing a bank-specific baseline from the shipping fixtures. These are synthetic mutation recipes, not bank requirements or template mapping rules. Keep the baseline and create separate project copies. The supplied recipes target a single-payment baseline; for multiple payments, preserve equal/distinct group relationships when assigning synthetic group keys.

- Exercise long source grouping keys separately from bank-facing identifier limits. Check output length, uniqueness, grouping, counts and sums against the selected bank profile. Include two distinct keys sharing a prefix to detect accidental truncation or group merging; check the chosen identifier strategy at its length boundary and beyond. Do not impose a universal ten-character limit or prescribe a compact-ID algorithm.
- Exercise both standard and Fusion dotted timezone offsets, including fractional seconds and a negative offset. Verify the output against the exact ISO schema and check that the timestamp's time, precision and offset are preserved. Do not normalize the input before running the template under test.
- Where the source contract or supplied sample contains a service-level/delivery-channel combination that differs from the target bank code, test that source combination against the reviewed mapping. Do not rewrite the source service level to the expected output just to make the test pass. The URGP/CCD recipe applies only where that source combination is evidenced and its handling is reviewed; it does not authorize a universal URGP-to-NURG mapping. For other profiles, use the evidenced source combination or record a reason for exclusion.
- Run the applicable combination case as well as the individual cases so one failure does not hide another. Check exact bank rules in addition to XSD validity.

Record each applicable case's input recipe, mapping/specification basis, expected result and actual outcome in the project's offline validation report. An expected unsupported-input rejection is distinct from a supported case passing. Missing mapping evidence leaves a scoped gap and a useful draft candidate; it does not require abandoning generation. Do not claim the affected behavior is validated until resolved.

## Fixture Sanitization Rule

Before adding or updating a persistent XML fixture:

1. Replace personal or source-environment email addresses and aliases with unmistakably synthetic contacts such as `test-contact-001@oracle.com` or an `example.invalid` address.
2. Replace source-derived person, supplier, payee, legal-entity, business-unit, account, address, telephone, tax, payment-reference, and internal-ID values with synthetic equivalents.
3. Keep bank account, IBAN, BIC, clearing-member, currency, country, delivery-channel, and financial values synthetic while preserving the format and scenario characteristics required by the test.
4. Preserve relationships between repeated source values, raw and masked account fields, transaction references, currencies, and financial totals.
5. Remove credentials, tokens, secrets, connectivity endpoints, and environment-specific configuration values. Use explicit `TEST`, `SYNTHETIC`, or `MASKED` placeholders when a field must remain populated.
6. Parse every XML fixture, scan it for non-test contact and identity values, and run it through the bundled generic CGI and SEPA XSLTs before packaging it.
