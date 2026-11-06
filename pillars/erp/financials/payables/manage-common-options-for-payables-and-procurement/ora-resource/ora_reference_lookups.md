# Manage Common Options for Payables and Procurement Reference Lookups

## Scope

This file defines reference resolvers and the receipts they must return. Package shape, fixed flags, and fields with only transport checks are governed by `ora_input_validation.md`; they are not lookup operations.

## Additional REST Availability Policy

The user-approved policy treats inaccessible supplemental REST verification as
a warning. It applies only to resolve_reference_set, resolve_bill_to_location,
resolve_conversion_rate_type and resolve_vat_country. Use the declared core
REST client and its normal read-only authentication handling; catch its
sanitized access/transport failure at the Run Book lookup step. Do not classify
an outage as no match, fabricate a successful receipt or infer missing CSV
values. Continue with a disclosed UNVERIFIED_API_UNAVAILABLE result when all
required CSV inputs are supplied. A name alone cannot replace a required
InternalLocationCode; request that code if HCM cannot resolve it.

A completed response proving no eligible match, ambiguity, disabled status or
conflicting values remains a failure. A missing lookup route or an unattempted
check is not an API failure. BU/ledger identity and SOAP account validation
retain their required successful receipts. No import or creation is authorized
by this policy.

For an unavailable supplemental check, add a prerequisite with exactly these
fields: operationId, entity, field, resolver, requestedValue, status
(unavailable), failureClass, httpStatus, method (GET), endpointPath,
requestContext and evidence. endpointPath is the called FSCM/HCM REST path
without query parameters, credentials or response bodies. evidence identifies
the sanitized workflow diagnostic. Accepted availability failures are
auth_authz (401/403), endpoint_unavailable (404/405/410/501), or
transport_environment (null for network/timeout failure, 408/429/500/502/503/504).
Bad input responses (400/422) and successful responses cannot be labeled
unavailable. Refresh authentication only as allowed by core; no retry loop.

requestContext must exactly contain environment (the export ProcessEnv),
baselineSha256, targetKey and requestedValues from the current normalized
operation after BU context resolution. Bind each field/value separately.
Rollback uses the current export and rollback operation IDs; forward records
cannot be reused. The adapter outputs referenceValidationWarnings in the
blueprint, preview and validation review; these records never satisfy a resolver
or supply SetId. Lookup and dependency nodes may continue with these warnings;
carry them into Data Loader's immutable preview and approval record.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| validate_gapless_identifier_dependency | GaplessInvNumFlag or BuyingCompanyIdentifier changes | Normalized requested values and the exact target row in the fresh current export | Use requested GaplessInvNumFlag when present, otherwise the current-export value; only exact Y confirms Yes. | Effective flag for validation only; never set Yes automatically. | Blank, missing, or unknown does not confirm Yes; apply the design guardrail. Target ambiguity remains blocked by the existing target-identity check. |
| validate_approved_option_choices | ExpenseAccrualCode or LiabilityPostLookupCode is supplied | User-approved fixed choices below; executable lists in e2e-adapter.json valueContracts | Trim whitespace; match exact code or case-insensitive listed UI label. | Canonical CSV code for the supplied field only. | Reject blank or unlisted inputs. Never query live LOVs or require a resolver receipt for these two fields. |
| resolve_reference_set | SetCode is supplied | Current authoritative reference-set receipt; the eligible selected HCM or FSCM bill-to-location response can supply its non-null SetId and exact SetCode as documented below | Require a non-null resolved set and returnedSetCode equal to the candidate SetCode; bind to the exact operation, entity, field, and value. | Validated SetCode and resolved SetId in evidence; never invent a set. | Missing, null, or mismatched evidence leaves validation incomplete. No standalone reference-set acquisition endpoint is declared here. Inaccessible additional REST checks continue with UNVERIFIED_API_UNAVAILABLE under the availability policy; missing required inputs and known invalid results still stop. |
| resolve_vat_country | VatCountryCode is supplied | Current authoritative territory-resolution receipt required by the adapter | Require at least one exact territoryCode with enabledFlag=Y and obsoleteFlag=N; bind to the exact operation, entity, field, and value. | Validated VatCountryCode in evidence. | Missing, mismatched, disabled, or obsolete evidence leaves validation incomplete. Additional exact eligible matches do not block. No territory acquisition endpoint is declared here. Inaccessible additional REST checks continue with UNVERIFIED_API_UNAVAILABLE under the availability policy; missing required inputs and known invalid results still stop. |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_bu_context_from_name | Every candidate row after input validation | BuName, optional explicit EnterpriseId, configured pod, and fresh exact-task export | GET /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV then GET /fscmRestApi/resources/11.13.18.05/ledgersLOV/{PrimaryLedgerId}; query shapes below | BusinessUnitId, BusinessUnitName, PrimaryLedgerId; LedgerId, Name | Select EnterpriseId by the precedence in ora_defaulting_rules.md. Require one exact BU, a non-null primary ledger, and matching ledger ID with nonblank Name. Bind the fresh export SHA, row count, actual distinct nonblank enterprise count, and selected EnterpriseId. | Selected EnterpriseId; SOBName from the matching ledger Name; retain BU and ledger IDs in evidence. ERP responses do not validate EnterpriseId. | Ask for EnterpriseId only when the precedence cannot resolve it. Block unavailable, zero, ambiguous, or inconsistent BU/ledger results; an explicit EnterpriseId does not bypass these checks. |
| resolve_bill_to_location | Bill-to Location name is supplied; or, after an HCM access or endpoint error, the user explicitly supplies InternalLocationCode | Requested location name; or, only after an HCM access or endpoint error, the InternalLocationCode explicitly supplied by the user; optional set and as-of date; configured pod | Primary: GET /hcmRestApi/resources/11.13.18.05/locationsLov then GET /hcmRestApi/resources/11.13.18.05/locationsV2. Fallback after HCM error and user response: GET /fscmRestApi/resources/11.13.18.05/contractBillToLocations. | HCM: LocationId, LocationName, LocationCode, SetId, SetCode, EffectiveStartDate, EffectiveEndDate, ActiveStatus, BillToSiteFlag. FSCM: LocationId, LocationName, InternalLocationCode, SetId, SetCode, EffectiveStartDate, EffectiveEndDate, ActiveStatus, BillToSiteFlag. | For a name, require one exact HCM match and verify the same record is active, bill-to enabled, and effective. For the fallback code, require one exact active FSCM bill-to record for the code, set, and effective-date composite. | InternalLocationCode, SetCode, EffectiveStartDate, EffectiveEndDate from the same verified record; retain LocationId and SetId in evidence. | Zero or ambiguous HCM matches require correction or disambiguation. An HCM access or endpoint error requires an explicit request for InternalLocationCode; do not invoke FSCM until the user supplies it. Block an absent, ambiguous, inactive, non-bill-to, or ineffective fallback result. Inaccessible additional REST checks continue with UNVERIFIED_API_UNAVAILABLE under the availability policy; missing required inputs and known invalid results still stop. |
| resolve_conversion_rate_type | UserConversionRateType or UserDefaultPmtExchangeRateType is supplied | Exact user conversion-rate type and configured pod | GET /fscmRestApi/resources/11.13.18.05/currencyConversionTypesLOV | UserConversionType, ConversionType | Require at least one exact current UserConversionType; bind its receipt to the supplied field and value. | Validated user rate type; retain the returned internal conversion type in evidence. | Block no exact current result or missing evidence; additional matching items do not block. Inaccessible additional REST checks continue with UNVERIFIED_API_UNAVAILABLE under the availability policy; missing required inputs and known invalid results still stop. |
| validate_account_segments_read_only | Any account-segment field is supplied | Exact field, segment string, resolved SOBName, and configured pod | POST /fscmService/AccountCombinationService using scripts/account_combination_preflight.py and validateAndCreateAccounts | Validation status and returned account result from the governed SOAP preflight | Require Valid with DynamicInsertion=No for the exact field, ledger, and one-through-30-part segment string. | Bound read-only validation receipt; retain any returned CCID in evidence, not as a CSV segment value. | Block invalid or missing evidence. This preflight cannot create a CCID; creation and import remain separately governed. |

## User-Approved Fixed Choices

| UI field | CSV attribute | UI label | Exact CSV code | Meaning |
|---|---|---|---|---|
| Offset Segments | LiabilityPostLookupCode | None | NONE | Use the invoice header liability account without substituting distribution segments. |
| Offset Segments | LiabilityPostLookupCode | Primary balancing segment | BALANCING_SEGMENT | Take the primary balancing segment from the invoice charge distribution; retain the remaining segments from the header liability account. |
| Offset Segments | LiabilityPostLookupCode | All segments, except natural account | ACCOUNT_SEGMENT_VALUE | Retain the natural account from the header liability account; take all other segments from the invoice charge distribution. |
| Accrue Expense Items | ExpenseAccrualCode | At receipt | RECEIPT | Accrue expense items when receipts are created; expense-destination purchase order schedules can override the accrual option. |
| Accrue Expense Items | ExpenseAccrualCode | Period end | PERIOD END | Accrue uninvoiced receipts at period close and reverse the accrual in the next period. |

## Receipt Binding Contract

Every required successful resolver receipt is bound to the operation, entity,
field, exact requested value, resolver, and result context. Before lookup, record
referenceContext in the design with exactly environment, baseUrl,
baselineSha256, runId and startedAt. Select these from the configured target and
fresh exact-task export: environment must equal ProcessEnv, baseUrl must be the
canonical HTTPS origin, and baselineSha256 must match that export. Use a stable,
nonblank safe runId and a timezone-aware ISO startedAt that is not in the future.
Current preparation requires the run to have started within the last 24 hours.

Each successful receipt must contain requestContext equal to that complete
referenceContext and a timezone-aware ISO observedAt from the actual response,
at or after startedAt and no later than now. For SOAP, retain the producer's
observedAt; map its request.environment and request.baseUrl only after checking
they match the selected target. Successful REST lookup records must retain the
same observed target and response time. Never replace an old observation time
or automatically rebind a receipt to another run, environment or export.

Historical reconciliation and checking the original forward plan during
rollback retain identity and observation-order checks without applying the
24-hour preparation limit. New rollback preparation requires a fresh
referenceContext supplied through --reference-context and fresh --prerequisites
for the current export and rollback operations. The unavailable supplemental
REST receipt contract above remains unchanged.

The adapter also requires the following resolver-specific context:

| Resolver | Required bound context |
|---|---|
| resolve_bu_context_from_name | baselineSha256, baselineRowCount, distinctEnterpriseIdCount (actual distinct nonblank count, including 0 or multiple), enterpriseId and requestedValue equal to the selected ID; exact BU, BusinessUnitId, PrimaryLedgerId, and matching ledger name. No tenantInvariant or singleton assertion is required. |
| resolve_reference_set | Returned set code equals the candidate SetCode; canonical receipt field SetId must contain the non-null, nonblank resolved ID from the same record (zero is allowed). |
| resolve_bill_to_location | Returned location, set, dates, active, and bill-to indicators equal the candidate composite. |
| resolve_conversion_rate_type | Exact UserConversionType; response cardinality is not a gate. |
| resolve_vat_country | Exact returned territory code, enabled flag, and non-obsolete flag; response cardinality is not a gate. |
| validate_account_segments_read_only | Exact ledger name, exact segment string, and DynamicInsertion=No. |

## ERP BU Request Shapes

```text
GET {pod}/fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV?q=BusinessUnitName='{BuName}'&fields=BusinessUnitId,BusinessUnitName,PrimaryLedgerId
GET {pod}/fscmRestApi/resources/11.13.18.05/ledgersLOV/{PrimaryLedgerId}?fields=LedgerId,Name
```

Use the SOAP account-combination preflight with `DynamicInsertion=No` for account segments. It is an import-path preflight, not a substitute for every UI-only KFF condition. Any remaining UI-only difference is disclosed, rather than treated as a missing field-level validation gate.

## Execution Rule

Obtain only the declared read-only receipts after their prerequisites. Future imports route through `core/data-loader` with immutable-artifact validation, Task Hook preview, approval, fresh export, and reconciliation.

## Bill-to Location Resolution

Use this read-only route for `resolve_bill_to_location` during
`APCO.RESOLVE_REFERENCES`, after input validation. Use the configured pod and
`core.fusion-api.rest-api-client` for OAuth and request handling.

### Primary Route for a Location Name

When the user supplies a location name, query HCM first:

```text
GET /hcmRestApi/resources/11.13.18.05/locationsLov
q=LocationName='{LocationName}'
fields=LocationId,LocationName,LocationCode,SetId,SetCode,EffectiveStartDate,EffectiveEndDate,ActiveStatus
onlyData=true
```

Follow pagination and require one exact name match. If the name identifies
multiple locations or sets, use an explicitly supplied set to disambiguate or
ask the user to choose. Then verify the selected record by ID:

```text
GET /hcmRestApi/resources/11.13.18.05/locationsV2
q=LocationId={LocationId}
fields=LocationId,LocationName,LocationCode,SetId,SetCode,EffectiveStartDate,EffectiveEndDate,ActiveStatus,BillToSiteFlag
onlyData=true
```

Require the same `LocationId`, `LocationCode`, and set from both responses,
`ActiveStatus=A`, `BillToSiteFlag=true`, and an effective interval containing
the requested as-of date. Map the verified HCM `LocationCode` to CSV
`InternalLocationCode`.

### Fallback After an HCM Error

An authentication, authorization, transport, service, or endpoint-access error
from either HCM request is not a no-match result. Stop the name-resolution path
and ask for `InternalLocationCode` only if it is missing. Do not derive or
guess the code from the location name. With the explicitly supplied code, query
FSCM to retrieve the remaining record information:

```text
GET /fscmRestApi/resources/11.13.18.05/contractBillToLocations
q=InternalLocationCode='{InternalLocationCode}';SetCode='{SetCode}';ActiveStatus='A';BillToSiteFlag='Y'
fields=LocationId,LocationName,InternalLocationCode,SetId,SetCode,EffectiveStartDate,EffectiveEndDate,ActiveStatus,BillToSiteFlag
onlyData=true
```

Omit the SetCode expression only when the request does not contain a set, then
require the remaining result to identify one unambiguous set. Pass escaped
filters as separate `--query` parameters through the shared client. Follow
pagination and post-filter every returned value exactly.

The FSCM resource also documents the `LocationAltKey` finder with
`InternalLocationCode`, `SetId`, `EffectiveStartDate`, and
`EffectiveEndDate`. Use it only when that complete alternate key is already
known:

```text
finder=LocationAltKey;InternalLocationCode={InternalLocationCode},SetId={SetId},EffectiveStartDate={EffectiveStartDate},EffectiveEndDate={EffectiveEndDate}
```

Require `ActiveStatus=A`, `BillToSiteFlag=Y`, the exact requested
`InternalLocationCode` and SetCode, and an effective interval containing the
requested as-of date. Normalize the verified flags to
`activeLocation=True` and `billToSite=True` in the resolver receipt.

| FSCM REST field | CSV field / use |
|---|---|
| InternalLocationCode | InternalLocationCode |
| SetCode | SetCode |
| EffectiveStartDate | EffectiveStartDate |
| EffectiveEndDate | EffectiveEndDate |
| LocationId | Expected resolved BillToLocationId in validation evidence |
| SetId | Resolved set evidence; 0 is valid |
| LocationName | Display evidence only; never substitute it for InternalLocationCode |

For the primary path, retain the requested name and both HCM responses as
resolution provenance. Bind the final receipt to the operation, entity,
resolved internal code, pod, queries, retrieval/as-of time, and selected
record. For the fallback path, also retain the HCM failure classification and
the user's explicit code response. Populate `returnedLocationCode`, `setCode`,
`effectiveStartDate`, and `effectiveEndDate` from one verified record. The
non-null SetId and matching SetCode also supply `resolve_reference_set`
evidence through `returnedSetCode`.

The FSCM Contracts bill-to-location LOV has the required alternate-key fields;
target-pod availability and privileges remain unverified. Zero matches,
ambiguity or an ineligible row require correction. Inaccessible APIs follow the
Additional REST Availability Policy; missing CSV values still require input.
Successful validation does not authorize upload or import.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| APCO.RESOLVE_REFERENCES | step | 20 | reference_lookup | resolved->APCO.CHECK_DEPENDENCIES;unverified_api_unavailable->APCO.CHECK_DEPENDENCIES;blocked->APCO.HANDLE_ERROR;failure->APCO.HANDLE_ERROR | APCO.VALIDATE_INPUT | stop | Resolve declared read-only contracts; continue unavailable supplemental REST checks with warnings under the availability policy |
