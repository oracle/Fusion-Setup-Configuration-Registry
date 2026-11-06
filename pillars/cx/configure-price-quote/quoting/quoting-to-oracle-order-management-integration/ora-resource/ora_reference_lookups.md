# Reference Lookups

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_order_management_offering | Before planning native CPQ to OM integration | Active Run Book Fusion environment; Order Management; exact code DOO_ORCHESTRATION | GET /fscmRestApi/resources/latest/features?fields=FeatureName,FeatureCode,FeatureType&q=FeatureType='OFFERING';FeatureName='Order Management'&onlyData=true; then GET /api/boss/extraction/queries/ora/commonSetup/features/v1/$en/searchOfferings?$filter=featureShortName='DOO_ORCHESTRATION'&$limit=50; then GET /api/boss/extraction/queries/ora/commonSetup/features/v1/featureSelectedChoices?featureShortName=DOO_ORCHESTRATION&$limit=50 | Standard: FeatureName, FeatureCode, FeatureType; BOSS identity: featureId, featureShortName, classification; choices: choiceShortName, choiceName, checkedFlag, choiceEnabledFlag, hasMore | Require one exact standard identity and one exact BOSS ROOT_NODE identity with hasMore=false; choices must have hasMore=false and exactly one checked, enabled Yes with choiceShortName=YES_DOO_ORCHESTRATION; reject any second checked choice | Offering identity, featureId and enabled Yes evidence | Missing, ambiguous, malformed, paginated or non-Yes selection blocks readiness; do not infer enabled state from identity |
| verify_cpq_offering | Before planning native CPQ to OM integration | Active Run Book Fusion environment; Configure Price Quote; exact code ORA_CONFIGURE_PRICE_QUOTE | GET /fscmRestApi/resources/latest/features?fields=FeatureName,FeatureCode,FeatureType&q=FeatureType='OFFERING';FeatureName='Configure Price Quote'&onlyData=true; then GET /api/boss/extraction/queries/ora/commonSetup/features/v1/$en/searchOfferings?$filter=featureShortName='ORA_CONFIGURE_PRICE_QUOTE'&$limit=50; then GET /api/boss/extraction/queries/ora/commonSetup/features/v1/featureSelectedChoices?featureShortName=ORA_CONFIGURE_PRICE_QUOTE&$limit=50 | Standard: FeatureName, FeatureCode, FeatureType; BOSS identity: featureId, featureShortName, classification; choices: choiceShortName, choiceName, checkedFlag, choiceEnabledFlag, hasMore | Require one exact standard identity and one exact BOSS ROOT_NODE identity with hasMore=false; choices must have hasMore=false and exactly one checked, enabled Yes with choiceShortName=ORA_CONFIGURE_PRICE_QUOTE_YES; reject any second checked choice | Offering identity, featureId and enabled Yes evidence | Missing, ambiguous, malformed, paginated or non-Yes selection blocks readiness; do not infer enabled state from identity |
| get_populate_bom_part_attributes | Before Book Order integration configuration after CPQ OAuth scope validation | Target Fusion environment | GET /cpq/rest/v19/settings/COMMERCE/enableBomPartAttributesOnModelLine with Accept application/json | Current Commerce setting value | Accept only an unambiguous returned value of Yes or No; if not Yes, generate a live-metadata-validated CpqCommerceSettings Data Loader source for the fixed Yes setting | Current setting value, read evidence, and bound Task Hook preview when required | 401 or 403: stop as auth or privilege failure. Missing or malformed value: stop as a CPQ API contract failure. A non-Yes value proceeds only through the documented Data Loader route. |
| verify_fusion_account_integration | Before preparing the Generic Integration Data Loader source | Target Fusion environment | GET /cpq/rest/v19/integrationVendors with Accept application/json | integrationType, vendorName, properties.items name, requestUrl, enabled | Select items where integrationType and vendorName are genericIntegration and properties.items name is Fusion Account Integration; require zero or one match | Presence, requestUrl, enabled state | Zero matches: prepare create source. More than one: stop as ambiguous. |

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| verify_native_flow_prerequisites_confirmation | Before final native Book Order setup readiness | Administrator evidence for the active environment and current native integration guide | Require confirmation of current Book Order actions; enabled Fusion Order Integration connection targeting the active environment; Collaboration Messaging Gen2 with the OM Simplify Configuration and Processing for B2B Messaging opt-in, outbound B2BMessageProcessingResult and inbound PurchaseOrder enabled; FOM_CPQ_NATIVE_INTEGRATION_ENABLED=Yes at Site; applicable sales-order approval policy. This is local evidence only, with no API or browser route | Confirmed prerequisites and environment-specific evidence refs | Missing, contradictory or stale evidence blocks readiness; route missing setup separately and stop if no supported workflow exists |
| verify_om_process_assignment_rule_user_confirmation | Before native CPQ--OM orders are submitted | Order Management administrator confirmation for the active environment | Require the exact documented rule name, Oracle CPQ source-system condition, selected DOO_ProductFulfillmentWithIntegratedSubscription action, active state, and deployed state; no API lookup | Administrator-confirmed rule readiness or manual-task blocker | Missing, partial, inactive, undeployed, or contradictory confirmation blocks order submission and requires the documented UI procedure |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| The source lacks an exact REST contract | Treat the lookup as TBD and do not perform an external call. |
| A lookup returns 401 or 403 | Stop as an auth or privilege failure; refresh only as the selected workflow permits. |
| A lookup is ambiguous or has no exact result | Stop and request the required environment or offering clarification. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQOM.VERIFY_OM_OFFERING | step | 20 | reference_lookup | verified->CPQOM.VERIFY_CPQ_OFFERING;unavailable->CPQOM.HANDLE_ISSUE | CPQOM.VALIDATE_SCOPE | stop | Before native CPQ to OM integration planning |
| CPQOM.VERIFY_CPQ_OFFERING | step | 30 | reference_lookup | verified->CPQOM.CHECK_COMMERCE_SETTING;unavailable->CPQOM.HANDLE_ISSUE | CPQOM.VERIFY_OM_OFFERING | stop | Before native CPQ to OM integration planning |
| CPQOM.CHECK_COMMERCE_SETTING | step | 35 | reference_lookup | compliant->CPQOM.CHECK_GENERIC_INTEGRATION;update_required->CPQOM.COMMERCE_CHANGE_GATE;lookup_failed->CPQOM.HANDLE_ISSUE | CPQOM.VERIFY_CPQ_OFFERING | stop | Before Generic Integration Data Loader validation |
| CPQOM.CHECK_GENERIC_INTEGRATION | decision | 45 | reference_lookup | present->CPQOM.CHECK_READINESS;absent->CPQOM.GENERIC_CHANGE_GATE;ambiguous->CPQOM.HANDLE_ISSUE;lookup_failed->CPQOM.HANDLE_ISSUE | CPQOM.CHECK_COMMERCE_SETTING | stop | Before preparing or uploading Fusion Account Integration |

## Client and Response Contracts

Route standard identity requests through `fusion_rest_client.py` with the standard
OAuth scope. Route both BOSS requests through `boss-rest_client.py` with the BOSS
scope; do not inherit a Run Book or Data Loader header. Pass each query parameter
with a separate `--query` argument; quote shell-sensitive `$filter` and `$limit`.
Use the literal, catalog-resolved offering code in the declared request, never
an inferred name filter. The BOSS search response establishes identity; only the
separate choice response establishes enablement. Boolean fields must be true
JSON booleans or the exact string `true`; absent, false or malformed fields fail
closed. Do not follow response links, alternate origins or guessed pagination
routes when hasMore is true: report the incomplete lookup and stop.

## Offering Lookup Request Protocol

For the two standard REST offering lookups above, use the declared
semicolon-separated query through core.fusion-api.rest-api-client without a
REST-Framework-Version override. Pass onlyData=true and require exactly one
matching item with hasMore=false before BOSS hydration. Do not inherit the
Run Book client's REST-Framework-Version: 9 header: that header selects a
different query parser and rejects these semicolon-separated expressions.

Oracle documents the protocol distinction in
[Set the REST Framework Version](https://docs.oracle.com/en/cloud/saas/sales/faaps/Set_the_REST_Framework_Version.html).
A future change to an explicit framework version must validate its corresponding
query syntax before replacing this lookup contract.
