# Country And Rail Matrix

## Purpose

Build this matrix before generating XSL for any bank profile with country-specific or rail-specific routing rules. The matrix prevents the template from silently guessing agent identifiers, clearing codes, account identifiers, or postal-address shape.

If the matrix cannot be completed from the bank specification and source XML contract, stop and report the open rows unless the user explicitly asks for a partial draft.

## Required Columns

Use these columns for each supported rail or country branch:

- Bank/spec source file and page, sheet, section, or row.
- Rail name from the bank guide, such as ACH, Fedwire, CHIPS, SWIFT, SEPA, book transfer, check, or local country rail.
- Source predicate from `OutboundPaymentInstruction`, including `PaymentMethod/PaymentMethodFormatValue`, `PaymentMethod/Code`, `DeliveryChannel/FormatValue`, `DeliveryChannel/Code`, `ServiceLevel/FormatValue`, debtor bank country, creditor bank country, payment currency, debtor account currency, creditor account country, and account identifier availability.
- Debtor agent rule for `DbtrAgt/FinInstnId`: BIC, `ClrSysMmbId/ClrSysId/Cd`, `ClrSysMmbId/MmbId`, `Othr/Id`, name, branch id, and postal country.
- Creditor agent rule for `CdtrAgt/FinInstnId`: BIC, `ClrSysMmbId/ClrSysId/Cd`, `ClrSysMmbId/MmbId`, `Othr/Id`, bank name, bank address, and whether more than one identifier is allowed for the same rail.
- Intermediary agent rule for `IntrmyAgt/FinInstnId`: BIC, clearing-system member ID, bank name and address fallback, and the exact condition for inclusion.
- Creditor and debtor account identifier precedence: IBAN, `Othr/Id`, local account, virtual/card/pool account, and required scheme name if any.
- Local clearing-code mapping, including ISO clearing-system code such as `USABA`, `AUBSB`, `CACPA`, bank-proprietary code, or explicit unsupported/open status.
- Postal-address rule for debtor, creditor, creditor agent, and intermediary agent: structured fields (`StrtNm`, `BldgNb`, `PstCd`, `TwnNm`, `CtrySubDvsn`, `Ctry`) versus `AdrLine`, maximum lengths, required country/state behavior, and whether blank optional elements should be suppressed.
- Required source XPath from `OutboundPaymentInstruction`; if the source is not exposed, mark `Source gap`.
- XSLT implementation note, including truncation and fallback.
- Validation sample or synthetic scenario.
- Status: `Mapped`, `Suppressed`, `Source gap`, `Setup required`, or `Open`.

## Hard Gates Before XSL Generation

- Every rail/country branch in the bank guide must have at least one matrix row.
- Every generated `CdtrAgt`, `DbtrAgt`, `IntrmyAgt`, `ClrSysMmbId`, `Othr/Id`, BIC, local clearing code, and postal-address branch must point back to a matrix row.
- Do not use target output paths as source paths. Invalid source roots include `Document`, `CstmrCdtTrfInitn`, `GrpHdr`, `PmtInf`, `CdtTrfTxInf`, `CdtrAgt`, `DbtrAgt`, `IntrmyAgt`, `RmtInf`, and other pain.001 output structures.
- Valid source roots normally come from `OutboundPaymentInstruction`, such as `PaymentInstructionInfo`, `InstructionGrouping`, `InstructionTotals`, `OutboundPayment`, `Payer`, `Payee`, `BankAccount`, `PayeeBankAccount`, `DocumentPayable`, `PaymentMethod`, `ServiceLevel`, and `DeliveryChannel`.
- If a bank guide lists both BIC and local clearing member ID for a rail, record whether both may be emitted, whether one is preferred, or whether one is conditional.
- Do not emit a local clearing-system code only because a branch number exists. The matrix must identify the applicable rail/country code.
- Do not emit `Othr/Id` only because some source identifier exists. The matrix must name the bank row that permits it.
- For postal addresses, do not mix structured fields and `AdrLine` by accident. Pick the bank-specified shape for the party and rail. Suppress blank optional address fields unless the bank guide requires fixed structure and the value is truly mandatory.

## Common Clearing-Code Hints

Use these only when the bank guide explicitly supports the country/rail combination:

- US Fedwire or ABA routing: `USABA` with the 9 digit ABA/member ID.
- Australia domestic bank/state/branch: `AUBSB` with the BSB number.
- Canada CPA transit: `CACPA` with the Canadian transit/member ID when the guide requires CPA.
- Russia BIK: map as the guide specifies; do not substitute SWIFT BIC for BIK.
- If the guide says country-specific code or bank-proprietary `XXXXX`, record the exact rule and source. If it cannot be derived, mark `Open` or `Setup required`.

## Validation Checks

After XSL generation:

- Parse the XSL as XML.
- Run the transform on available masked sample XML.
- Confirm each non-empty sample branch used in output is present in the matrix.
- Confirm `CdtrAgt`, `DbtrAgt`, and `IntrmyAgt` identifiers are not empty and do not conflict with the matrix precedence.
- Confirm no generated amount is `NaN`.
- Confirm no mandatory leaf element is empty.
- Confirm no XPath in the XSL treats a target pain.001 path as input source.
- Compare against available working templates or seeded templates only after generation, and never use those comparison templates to fill the matrix unless the user explicitly permits using them as generation evidence.
