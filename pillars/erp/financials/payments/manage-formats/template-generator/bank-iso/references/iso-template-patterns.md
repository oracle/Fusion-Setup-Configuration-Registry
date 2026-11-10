# ISO Template Pattern Reference

This file captures reusable message-generation patterns from the bundled Oracle seed XSL templates. It intentionally excludes raw JPM/PNC partner specification workbooks and bank-derived mapping workbooks.

## Generic CGI And SEPA Patterns

- `references/template-generation/iso/ISO20022CGI2019.xsl` emits `pain.001.001.09` and is the default base when a bank asks for CGI 2019 or a V09 credit-transfer profile.
- `references/template-generation/iso/ISO20022SEPAV7_0.xsl` is the default base when a bank asks for SEPA credit transfer and does not require a heavily bank-customized CGI profile.
- Generic templates use `xsl:template match="OutboundPaymentInstruction"` and group `OutboundPayment` rows into `PmtInf` blocks by `LogicalGrouping/LogicalGroupReference`.
- Generic templates are suitable for schema scaffolding, control totals, debtor/payment-info structure, and standard source paths. Do not let generic optional branches override explicit bank rail/country rules.

## JPM Seed XSL Patterns

Use the bundled JPM seed XSLs as implementation precedent only when the runtime bank specification permits the target element or is silent on a schema-required element.

- JPM CGI seed templates emit `pain.001.001.03`.
- They include large country, service-level, delivery-channel, and payment-mode branch structures.
- They show how to gate local instruments, card-like/SUA behavior, country-specific bank routing, DFF `Extend` fragments, withholding-tax data, and remittance blocks.
- They use explicit `xsl:choose` branches and substring limits for bank-specific formatting.
- Treat DFF and country/local-tax fragments as examples of source gating, not as default output for another bank.

## PNC Seed XSL Patterns

Use the bundled PNC seed XSL as implementation precedent only when the runtime bank specification permits the target element or is silent on a schema-required element.

- PNC CGI seed emits `pain.001.001.03`.
- It shows account-setting overrides for initiating party and debtor name, including `CGI_INITIATING_PARTY_NAME` and `DEBTOR_NAME`.
- It maps sender-style setup data from `InstructionGrouping/BankAccount/EFTUserNumber/EFTRequesterId`.
- It contains examples for check output with `ChqInstr`, intermediary-agent handling, purpose-code formatting, remittance truncation, and credit-note absolute amount handling.
- Treat proprietary scheme names, sender IDs, and purpose-code formats as bank-specific patterns that require matching runtime bank evidence.

## Mapping Matrix Style

For a new bank, keep these columns in the mapping matrix:

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

Keep Oracle/OOB mappings and bank-specific overrides separate. Mark every row as `OOB`, `Override`, `Constant`, `Setup`, `DFF/Extend`, `Unsupported`, or `Open`.

Do not copy a seed-bank output rule into a new bank template unless one of these is true:

- the target bank specification explicitly requires or allows it;
- the element is schema-mandatory and the generic Oracle mapping is the only available supported source; or
- the user accepts the assumption and the mapping matrix documents it.
