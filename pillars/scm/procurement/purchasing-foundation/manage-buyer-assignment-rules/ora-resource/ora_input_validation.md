# Buyer Assignment Rule Input Validation

Validate configurator-supplied display values locally. These are input shape,
type, length, enum, and required-value checks only. Do not resolve names to IDs,
clear dependent fields, or rewrite input.
The sole local default is owned by ora_defaulting_rules.md and runs after
validation passes.
Optional attributes remain optional; display-value intake does not require
populating every optional attribute.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Core assignment | ProcurementBusinessUnit and Buyer; RuleSequenceNumber when supplied | Block preparation | Provide the procurement BU and buyer display values. A missing RuleSequenceNumber is populated by the defaulting lookup. | Always | |
| Rule qualifier | RequisitioningBusinessUnit or Commodity | Block preparation | Provide at least one display value | Always | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Input row is a field-to-value record | Reject a scalar, list, or nested structure in place of a row | Always | |
| Required values are present | Treat null, empty text, or whitespace-only text as missing; do not trim or replace the original value | Required group is evaluated | |
| Display attributes are text | Reject numbers, booleans, objects, and arrays; do not substitute an internal ID for a display value | A display attribute is supplied and is not null | |
| Buyer, ProcurementBusinessUnit, RequisitioningBusinessUnit, DeliverToOrganization are at most 240 characters each | Report the field, observed length, and documented maximum; do not truncate | A nonblank value is supplied | |
| Commodity is at most 255 characters | Report an overlength value; do not truncate | A nonblank value is supplied | |
| Project is at most 25 characters | Validate the project number as text, preserving leading zeroes | A nonblank value is supplied | |
| Supplier is at most 360 characters | Report an overlength value; do not truncate | A nonblank value is supplied | |
| CostCenter is at most 150 characters | Validate as text, preserving leading zeroes | A nonblank value is supplied | |
| Currency is at most 15 characters | Validate as text only; do not assume a three-character code or derive a currency | A nonblank value is supplied | |
| RuleSet is at most 80 characters | Validate the supplied rule-set display meaning as text; do not require RuleSetCode | A nonblank value is supplied | |
| RuleSequenceNumber and ExceedsLineAmount are finite decimal numbers | Accept finite numeric values or decimal text from a spreadsheet/CSV; reject booleans, NaN, infinity, objects, arrays, and nonnumeric text; do not enforce sign, precision, scale, or uniqueness | RuleSequenceNumber is supplied; ExceedsLineAmount is optional | |
| NonCatalogFlag is a boolean or an explicit display choice | Accept true, false, Yes, No, Y, N, or blank/null; reject other values; preserve the supplied representation without coercion | NonCatalogFlag is supplied | |

## Validation Boundaries

| Situation | What Happens |
|---|---|
| Display-value contract | Buyer, ProcurementBusinessUnit, RequisitioningBusinessUnit, Commodity, DeliverToOrganization, Project, Supplier, CostCenter, Currency, and RuleSet are configurator-facing text attributes; RuleSequenceNumber and ExceedsLineAmount are numeric; NonCatalogFlag is a choice. |
| Internal identifiers and codes | Do not require BuyerId, ProcurementBusinessUnitId, RequisitioningBusinessUnitId, CommodityId, DeliverToOrganizationId, ProjectId, SupplierId, ChartOfAccountsId, RuleId, or RuleSetCode from the configurator. The registered `purchasingBuyerAssignmentRules` Data Loader business object derives its foreign keys and foreign user keys from the supplied display values. |
| Transport mapping | Submit the display attributes through the registered Data Loader business object. Map the configurator header `Procurement BU` to `ProcurementBusinessUnit`, leave `ProcurementBusinessUnitId` blank, and let the business object derive the ID from the supplied label. Do not replace display inputs with the FSM CSV template's code and email columns. The Data Loader session performs its required live schema validation before it creates an upload ZIP. |
| Numeric and relationship business rules | Do not enforce positivity, amount thresholds, sequence uniqueness, reference eligibility, BU relationships, or dependent-field clearing here. When RuleSequenceNumber is absent, the separately owned live lookup obtains the current highest sequence for defaulting. |
| Optional blank values | Leave them unchanged during validation. After validation passes, follow the RuleSet and RuleSequenceNumber defaults declared in ora_defaulting_rules.md; other optional blanks remain unchanged. |
| Noncatalog presentation | Yes/No and boolean acceptance is the local configurator contract. The Data Loader business object validates the serialized value before upload. |
| Text length | Count Unicode characters in the supplied text, including spaces; preserve the original text. Do not invent extra byte-length, character-set, precision, or scale restrictions. |

## Source and Release Boundary

The configurator display-value contract and validation-only scope come from the
developer instruction in this authoring session. Required assignment/qualifier
presence is documented in Oracle's [26D Buyer Assignment Rules](https://docs.oracle.com/en/cloud/saas/procurement/26d/oapro/buyer-assignment-rules.html).
Text types and maximum lengths above use Oracle's [26C buyer assignment rule
response schema](https://docs.oracle.com/en/cloud/saas/procurement/26c/fapra/op-purchasingbuyerassignmentrules-purchasingbuyerassignmentrulesuniqid-get.html).
The corresponding 26D and 27A REST topic URLs were inaccessible when checked on
2026-10-23. These are the verified 26C source limits, not proof of target-release
or Data Loader schema compatibility. The REST schema labels NonCatalogFlag as
boolean while describing Y/N/null; the explicit local presentation choices above
avoid silently coercing that inconsistency.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BAR.VALIDATE_INPUT | decision | 10 | validate_input | valid->BAR.LOOKUP_NEXT_SEQUENCE;invalid->BAR.INPUT_INVALID | none | stop | Always |
