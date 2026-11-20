# Additional PPR reference checks

For the supplied fields below, use only the selected task's read-only Core REST
route, and retain a separate operation-bound receipt for each supplied value.
These checks establish exact reference matches within the returned scope; FSM
remains responsible for import eligibility and saved values. Do not create or
modify referenced master data.

Use the Core REST client to encode parameters. For `q` string values, escape a
literal apostrophe as two apostrophes; do not assemble shell commands from user
input. Use `onlyData=false` and follow advancing pages until an exact match is
found or the result is exhausted. One or more exact matches pass, including
duplicates. A successful exhausted result with no match requires correction;
an inaccessible service, malformed response, missing required context, or
incomplete paging makes validation unavailable. Keep the exact CSV value.

## Legal-entity identifier

For `ORA_PPR_LE_GROUP.LegalEntityIdentifier`, use resolver
`resolve_legal_entity_legal_entity_identifier`:

```text
GET /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV
fields=LegalEntityIdentifier,Name
```

Read advancing pages and compare returned `LegalEntityIdentifier` exactly with
the supplied identifier. Use a server-side identifier filter only when its
query contract is confirmed for the selected service.
Name is display context, not a substitute for the identifier. A matching public
LOV row does not prove import-time eligibility or a legal-entity name change.

## Payment and cross-currency rate types

For `PaymentConversionRateType`, use `resolve_payment_conversion_rate_type`;
for `CrossCurrencyRateType`, use `resolve_cross_currency_rate_type`:

```text
GET /fscmRestApi/resources/11.13.18.05/currencyConversionTypesLOV
fields=UserConversionType,ConversionType
```

Read advancing pages and compare the returned `UserConversionType` exactly with
the supplied alias. Apply a server-side filter only when its query contract is
confirmed for the selected service.
Serialize the alias, not the internal `ConversionType`. The separately named
Bank Conversion Rate Type remains a direct-user-input exception.

## Pay-group and source names

For `ORA_PPR_PAY_GROUP.VendorPayGroupName`, use
`resolve_pay_group_vendor_pay_group_name` with lookup context
`{LookupType: "PAY GROUP", ViewApplicationId: 200}`. For
`ORA_PPR_SOURCE_GROUP.InvoiceSourceName`, use
`resolve_source_group_invoice_source_name` with
`{LookupType: "SOURCE", ViewApplicationId: 200}`.

```text
GET /fscmRestApi/resources/11.13.18.05/genericLookups
finder=LookupTypeFinder;LookupType=<lookup type>,ViewApplicationId=200
fields=LookupType,ViewApplicationId
```

Confirm the returned lookup type and numeric view, then GET the returned
`lookupCodes` child link with `q=Meaning='<escaped supplied name>'` and
`fields=Meaning,LookupCode`. Check every matched parent's applicable child
pages until a match or exhaustion; do not construct the opaque parent ID or
require a unique parent or code. Compare `Meaning` exactly and serialize the
supplied name, not `LookupCode`. Do not add enabled/date or set filters.

## Receipt and coverage boundary

For each check record `operationId`, `entity`, `field`, the resolver above,
nonblank `evidence`, and `restResult` with `httpStatus` and returned `items`.
For pay groups and sources also record the exact `lookupContext` shown above.
The offline adapter checks these receipt fields and exact row values; the active
workflow owns request context, authentication and response provenance. A local
receipt check does not prove a live call occurred.

For every task REST check, use the independently selected Core workflow context
as the target authority. Retain the actual request and response artifact
references, selected Fusion environment identity and HTTPS origin, observation
time, operation/field/value and lookup context. Keep any authentication-profile
label separate from exported environment identity; do not infer a mapping from
the receipt or strip a profile suffix. Compare the recorded request target and
inputs with the selected context before accepting its match result. A receipt
cannot establish its own trusted target.

When retained values or a baseline affect the check, record the actual baseline
SHA-256 and relevant input values with that evidence. Carry the evidence
references through the existing ordered Task Hook rule results and final
preview, whose `finalData.archiveSha256` binds the exact candidate ZIP. Recheck
the applicable evidence when its target or relevant inputs change, following
the owner's existing validation and approval lifecycle. Use actual Core/Shared
outputs for acquisition evidence; a hand-written verified flag is insufficient.
Apply an owning workflow's defined freshness policy when present without
inventing a task-specific expiry period. These are assisted workflow checks;
the offline adapter does not authenticate remote acquisition or certify receipt
freshness.

No task-specific public REST response contract is declared here for payment
method, supplier or party, disbursement bank account, payment document, or
payment process profile. Apply their existing supported FSM reference contract;
do not claim a public REST check or invent its endpoint or matching field.
