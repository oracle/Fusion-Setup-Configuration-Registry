# Billing Types Input Validation

## Source and Supported Scope

Source: authorized live billingTypes describe and registered Data Loader template in SILVER_UNLOCKED, retrieved 2026-10-19 through core Data Loader. Describe advertises item update with method PATCH. BillingTypeId is the PrimaryKey finder attribute, a BigInt string of precision 18. EnabledFlag is Boolean, updatable and inputRequired. The loader template registers BillingTypeId as a local key with user-key attributes BillingTypeCode, BillingTypeId; RestAction is mandatory. Loader metadata labels EnabledFlag as String, so retain its Boolean meaning using canonical true/false text in loader records.

This graph supports one-record POST creation and PATCH of EnabledFlag on one existing Billing Type. GET and identity/duplicate evidence use the Collection Read Contract in ora_reference_lookups.md through core.fusion-api.rest-api-client. DELETE, changing an existing category/code, null-clearing and bulk mutations remain outside this validated contract. POST never means upsert or implicit update.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BILLING_TYPES.VALIDATE_INPUT | decision | 10 | validate_input | create->BILLING_TYPES.RESOLVE_CATEGORY;passed->BILLING_TYPES.RESOLVE_REFERENCE;failed->BILLING_TYPES.RETURN_ISSUES | none | stop | Validate one-record mutation input; create selects POST, passed selects the supported EnabledFlag PATCH, failed rejects all other operations or invalid inputs |

## Create Contract Source

Authorized live describe on 2026-10-19 advertises collection create with POST, separately from upsert. BillingCategory and EnabledFlag are inputRequired; BillingTypeId has a server default expression. This task also requires an explicit lookup-resolved BillingTypeCode to establish the requested mapping and enforce duplicate protection. Audit fields and meanings are not writable inputs. Category/type strings have maximum length 30. Loader metadata represents the flag as String; canonical true/false text retains the underlying Boolean contract. Do not infer or manufacture a BillingTypeId for POST.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Explicit new mapping | BillingCategory code or exact meaning; BillingTypeCode code or exact meaning; explicit EnabledFlag Boolean; RestAction=POST in the captured source | Block preview with the missing input; do not default EnabledFlag | Resolve the category with resolve_billing_category and type with resolve_billing_type_option; require the explicit flag selection before source preparation | POST create | |
| Exact existing target | BillingTypeId in the captured loader record; exact BillingTypeCode or BillingTypeId selected by the user and retained in task context | Block source preparation and preview | Resolve exactly one current Fusion record with resolve_billing_type and use its server-returned BillingTypeId | EnabledFlag PATCH | resolve_billing_type |
| Explicit update | RestAction=PATCH and EnabledFlag with the explicitly requested Boolean value | Block preview; never default a missing update value | Obtain the requested flag; encode Boolean true or false as canonical true/false text in the live loader template | EnabledFlag PATCH | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Operation and field allowlist | For POST, allow only BillingCategory, BillingTypeCode, EnabledFlag and RestAction=POST, with no BillingTypeId, audit/display fields or upsert. For PATCH, allow only BillingTypeId, EnabledFlag and RestAction=PATCH. Reject other operations, multi-record sources, arbitrary category/code updates, reference columns and null clearing. | Mutation validation | |
| Boolean shape | Accept the explicitly supplied Boolean true/false or exact canonical text true/false. Reject blank, null and other values; do not infer a default. | POST and EnabledFlag PATCH | |
| Create field shape | Require nonblank resolved category/type codes, each at most 30 characters; captured source must agree with the live LOV outputs and the user's explicit flag. Field-shape validation does not establish uniqueness. | POST create | |
| Identity shape | Require the live server-returned BillingTypeId, represented as a BigInt string with at most 18 digits. Never synthesize an ID or derive it from the display label. | EnabledFlag PATCH | resolve_billing_type |
| Captured-source agreement | Captured source identity equals the resolved record and the flag equals the user's requested value. Preserve every omitted business field. If the current flag already equals the request, report no change needed without submission. | EnabledFlag PATCH | resolve_billing_type |

No default is introduced for EnabledFlag. POST lookup mechanics and duplicate discovery belong to ora_reference_lookups.md; duplicate business policy belongs only to ora_design_enforcement.md. The existing PATCH preserves omitted fields. Core Data Loader still validates its complete live schema, action, privileges, source and environment/Run Book binding before preview. This task graph does not waive those checks.
