# Intrastat Rules Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Registered business object | `intrastatRules` parent data and zero or more supported child collections | Stop before Data Loader preparation | Use the registered `intrastatRules` business object and its published metadata | Every request | |
| Rule set identity | `RuleSetCode` | Stop before Data Loader preparation | Provide the rule-set code | Every parent create | |
| Intrastat Catalog | `CategorySetName` (friendly catalog name) | Stop before Data Loader preparation when a supplementary-UOM child supplies `CategoryCodeName` | Provide an exact Intrastat Catalog name | Parent plus affected `supplementaryUOMRules` child | resolve_intrastat_catalog |
| Rule type | `RuleType` or `RuleTypeName` | Stop before Data Loader preparation | Provide the rule-type code or an exact friendly rule-type meaning | Every parent create | resolve_intrastat_rule_type |
| Attribute-validation source type | `SourceType` | Stop before Data Loader preparation | Provide the source-type code or an exact friendly source-transaction meaning | Each `attributeValidationRules` row | resolve_intrastat_validation_source_type |
| Attribute-validation attribute | `AttributeCode` | Stop before Data Loader preparation | Provide the attribute code or an exact friendly required-attribute meaning | Each `attributeValidationRules` row | resolve_intrastat_validation_attribute_code |
| Fiscal-regime source type | `SourceTypeCode` or `SourceTransactionName` | Stop before Data Loader preparation | Provide the source-type code or an exact friendly source-transaction meaning | Each `fiscalRegimeCodeRules` row | resolve_intrastat_fiscal_source_type |
| Fiscal-regime trading-partner type | `TradingPartnerType` or `TradingPartnerTypeName` | Stop before Data Loader preparation | Provide the trading-partner-type code or an exact friendly trading-partner-type meaning | Each `fiscalRegimeCodeRules` row | resolve_intrastat_fiscal_trading_partner_type |
| Freight terms | `DeliveryTermsCode` | Stop before Data Loader preparation | Provide the delivery-terms code or an exact friendly freight-terms meaning | Each `statisticalValueRules` row that supplies freight terms | resolve_intrastat_delivery_terms |
| Mode of transport | `TransportModeCode` or `ModeOfTransport` | Stop before Data Loader preparation | Provide the transport-mode code or an exact friendly transport-mode meaning | Each `statisticalValueRules` row that supplies a transport mode | resolve_intrastat_transport_mode |
| Rounding rule | `SupplemetaryQuantityUOMRoundingMethod` or `RoundingRuleName` | Stop before Data Loader preparation | Provide the rounding-method code or an exact friendly rounding-rule meaning | Each `supplementaryUOMRules` row that supplies a rounding method | resolve_intrastat_rounding_rule |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Data Loader metadata ownership | Use only fields and child collections present in the registered `intrastatRules` metadata. Leave requiredness, lengths, domains, keys, uniqueness, and cross-record validation to Data Loader and Fusion. | Every request | |
| Parent friendly fields | Do not locally normalize `EstablishmentName`. Resolve `CategorySetName` supplied as Intrastat Catalog through the approved catalog resolver. | A friendly parent value is supplied | resolve_intrastat_catalog |
| Intrastat-catalog normalization | Resolve the parent `CategorySetName` as an exact Intrastat Catalog name, then fill canonical parent `CategorySetId`. When a `supplementaryUOMRules` child supplies `CategoryCodeName`, copy that same canonical ID to its `CategorySetId` before Data Loader preparation. Reject no match, ambiguity, and supplied-ID conflicts. | A parent row supplies `CategorySetName` | resolve_intrastat_catalog |
| Rule-type normalization | Resolve a supplied `RuleType` or `RuleTypeName` as an exact rule-type code or friendly meaning, then fill canonical `RuleType` from the returned `LookupCode`. Reject no match, ambiguity, and code/name conflicts. | A parent row supplies `RuleType` or `RuleTypeName` | resolve_intrastat_rule_type |
| Attribute-validation source-type normalization | Resolve `SourceType` as an exact source-document code or friendly source-transaction meaning, excluding the `ALL` lookup value, then fill canonical `SourceType` from the returned `LookupCode`. Reject no match or ambiguity. | An `attributeValidationRules` row supplies `SourceType` | resolve_intrastat_validation_source_type |
| Attribute-validation attribute normalization | Resolve `AttributeCode` as an exact attribute code or friendly required-attribute meaning, then fill canonical `AttributeCode` from the returned `LookupCode`. Reject no match or ambiguity. | An `attributeValidationRules` row supplies `AttributeCode` | resolve_intrastat_validation_attribute_code |
| Fiscal-regime source-type normalization | Resolve `SourceTypeCode` or `SourceTransactionName` as an exact source-document code or friendly source-transaction meaning, excluding `ALL`, then fill canonical `SourceTypeCode` from returned `LookupCode`. Reject no match, ambiguity, and code/name conflicts. | A `fiscalRegimeCodeRules` row supplies either field | resolve_intrastat_fiscal_source_type |
| Fiscal-regime trading-partner-type normalization | Resolve `TradingPartnerType` or `TradingPartnerTypeName` as an exact trading-partner-type code or friendly meaning, then fill canonical `TradingPartnerType` from returned `LookupCode`. Reject no match, ambiguity, and code/name conflicts. | A `fiscalRegimeCodeRules` row supplies either field | resolve_intrastat_fiscal_trading_partner_type |
| Child friendly fields | Preserve published child friendly fields (such as organization, category, item, transaction-code, country, UOM, and trading-partner names) for Data Loader/Fusion processing. Do not infer identifiers or codes locally. | A child row is supplied | |
| Blank child-field preservation | Emit an empty XLSX/DAT cell for every child attribute that the source does not supply. Do not emit numeric sentinels, column counts, or placeholders such as `15` or `16`. For `supplementaryUOMRules`, leave `SupplemetaryUOMRuleSetId`, `CategoryId`, `ObjectVersionNumber`, `SupplementaryUOM`, `RestAction`, `LastUpdateLogin`, `Description`, and `UOMDescription` empty unless the source explicitly provides an approved canonical value. Populate child `CategorySetId` only from `resolve_intrastat_catalog` when the child supplies `CategoryCodeName`. | Every child source row | resolve_intrastat_catalog |
| Freight-terms normalization | Resolve a supplied `DeliveryTermsCode` as an exact delivery-terms code or friendly meaning, then replace it with the returned canonical `LookupCode`. Reject no match, ambiguity, and code/meaning conflicts. | A `statisticalValueRules` row supplies `DeliveryTermsCode` | resolve_intrastat_delivery_terms |
| Transport-mode normalization | Resolve `TransportModeCode` or `ModeOfTransport` as an exact transport-mode code or friendly meaning, then fill canonical `TransportModeCode` from returned `LookupCode`. Reject no match, ambiguity, and code/name conflicts. | A `statisticalValueRules` row supplies either field | resolve_intrastat_transport_mode |
| Rounding-rule normalization | Resolve `SupplemetaryQuantityUOMRoundingMethod` or `RoundingRuleName` as an exact rounding-method code or friendly meaning, then fill canonical `SupplemetaryQuantityUOMRoundingMethod` from returned `LookupCode`. Reject no match, ambiguity, and code/name conflicts. | A `supplementaryUOMRules` row supplies either field | resolve_intrastat_rounding_rule |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INTRASTAT_RULES.VALIDATE_INPUT | step | 10 | validate_input | valid->INTRASTAT_RULES.RESOLVE_CATALOG;invalid->RETURN_ISSUES | none | stop | Before preparing an Intrastat Rules Data Loader source. |
