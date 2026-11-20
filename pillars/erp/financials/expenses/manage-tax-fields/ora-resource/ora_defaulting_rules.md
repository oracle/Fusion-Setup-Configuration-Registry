# Manage Tax Fields defaults

Evidence: SRC-CS-UI-VO and SRC-CS-FSM-VO. UI defaults do not prove import defaults. Preserve explicit user values. These are authoring controls, not claims that Oracle defaults or clears omitted values. The input and execution gates enforce explicit business values and the Tax-specific alias qualification contract. Never infer ENABLE_TAX from a tax rule's EnabledFlag.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| EnableMerchantNameCode and EnableTaxClassificationCode | No automatic FSM default. Offer the source-backed UI choice ENABLED and obtain explicit intent before serialization | create through FSM | No | |
| EnableMerchantReceiptCode, EnableMerchantTaxRegCode, EnableMerchantReferenceCode, EnableMerchantTaxpayerCode | No automatic FSM default. Offer the source-backed UI choice DISABLED and obtain explicit intent before serialization | create through FSM | No | |
| Existing omitted business fields | Do not generate a value or a blank. Retain the existing value from the routed fresh export when constructing an explicit update; if unavailable, return a missing-baseline issue | update through FSM | No | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| TAX.DEFAULTS | step | 4 | apply_default | success->TAX.DESIGN;failure->TAX.ISSUES | TAX.DEPENDENCIES | stop | create or update |
