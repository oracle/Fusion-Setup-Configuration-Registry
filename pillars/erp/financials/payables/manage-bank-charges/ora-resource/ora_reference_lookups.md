# Manage Bank Charges — Reference Lookups

## Reference lookup policy

This step evaluates references in a validated create request. The option/name
consistency policy below also applies to update assessment. Local choice
resolvers normalize fixed FSCR choices without an endpoint. Public REST
resolvers perform read-only reference verification only through the active
workflow and its configured authentication. They do not authorize import,
create related setup or turn returned surrogate IDs into task CSV keys.

### Additional REST Availability Policy

Legal entity, currency, bank, country and branch REST checks are additional
validation. The user-approved policy permits preparation and preview when the
declared core REST client reports an access failure, inaccessible endpoint,
timeout or service outage. The Run Book catches the sanitized failure after
core's permitted authentication handling and records
UNVERIFIED_API_UNAVAILABLE. Preserve every supplied reference, continue to
dependency assessment, and disclose the warning in shared validation and
Data Loader's immutable preview. Do not require a separate waiver, infer IDs,
report the check as passed or automatically submit an import.

Create intake and snapshot-bound update requests accept an optional
reference_check_results array. Each unavailable result has exactly these
fields: resolver, side, status (unavailable), failureClass, httpStatus,
method (GET), endpointPath, requestContext and evidence. Use one applicable
public resolver from the table below; side is blank for legal entity/currency
or Transferring/Receiving for bank/country/branch. endpointPath is the exact
table path without query parameters. evidence identifies a sanitized workflow
diagnostic; do not include response bodies, credentials or headers.

A successful result uses the same fields with status `verified`, failureClass
`""`, httpStatus `200`, plus matchCount `1` and hasMore `false`. Record success
only after checking the returned record against the supplied values using the
resolver's match rule below; HTTP 200 alone is insufficient. The offline adapter
validates the recorded outcome and requestContext; it does not repeat the lookup.

Without an unavailable-check warning or an explicit offline waiver, create
preparation requires verified results for currency, a named legal entity, each
Specific bank and Specific branch, and each supplied bank country, separately
for each bank side. All-scope choices require no entity/bank/branch lookup.

`assess-intake` reports reference_validation_verified and retains successful
reference_validation_evidence. The create helper preserves this evidence and
reports VERIFIED only with complete successful coverage. Mixed outcomes retain
availability warnings and are not reported as fully verified.

Accepted failures are auth_authz (401/403), endpoint_unavailable
(404/405/410/501) and transport_environment (null for network/timeout failure,
408/429/500/502/503/504). A 400/422 rejection, successful no-match response or
ambiguity is not an availability failure. requestContext contains environment
and referenceValues: all legal entity, currency and transferring/receiving
bank/branch selector fields from the normalized create header or raw update
header, with omitted values represented as empty strings. Its exact fields are
LegalEntityName, LegalEntityIdentifier, CurrencyCode, and each side's
BankOption, BankName, BankNumber, BankCountry, BranchOption, BranchName and
BranchNumber. Bind these values to the current request; do not reuse a record
after changing the environment or references.

The preparation review retains reference_validation_warnings. Supplied values
and required identifiers still undergo local checks and Fusion validation.
Only recorded unavailable checks are classified this way; unrecorded checks
are not claimed verified. Fixed choices, option/name consistency, required
CSV inputs, snapshot identity, group/range checks and Data Loader approval
retain their requirements. Completed invalid or ambiguous results still stop.

An omitted value with a standard create default is returned as
`default pending`; the lookup step does not apply the default. Evaluate
transferring and receiving bank and branch references independently.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BKC.LOOKUPS | step | 20 | reference_lookup | pass->BKC.DEPENDENCIES;unverified_api_unavailable->BKC.DEPENDENCIES;fail->BKC.ERROR | BKC.INPUT | stop | Validate local choices and public references; continue unavailable additional REST checks with disclosed warnings |

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_bank_option | An effective transferring or receiving bank option is available | `ALL`, `ONE`, `All banks`, `Specific bank` | Local choice; no endpoint | Corresponding BankOption | Case-insensitive fixed-choice match | Normalize to `All banks` or `Specific bank`; Specific invokes resolve_bank | Reject an unknown choice |
| resolve_branch_option | An effective transferring or receiving branch option is available | `ALL`, `ONE`, `All branches`, `Specific branch` | Local choice; no endpoint | Corresponding BranchOption | Case-insensitive fixed-choice match | Normalize to `All branches` or `Specific branch`; Specific invokes resolve_bank_branch | Reject an unknown choice |
| resolve_settlement_priority | Settlement priority is supplied | `EXPRESS`, `NORMAL`, `Express`, `Normal` | Local choice; no endpoint | SettlementPriorityDisplay | Case-insensitive fixed-choice match | Normalize to `Express` or `Normal` | Reject an unknown choice |
| resolve_legal_entity | A legal-entity name or identifier is supplied | LegalEntityName, LegalEntityIdentifier | `GET /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV`; `All` is a local sentinel choice | LegalEntityId, LegalEntityIdentifier, Name, EffectiveFrom, EffectiveTo | `All` requires a blank identifier; otherwise require one exact name/identifier match with a nonblank identifier | LegalEntityName and LegalEntityIdentifier; never serialize `-99` | Stop on no exact match, ambiguity or conflicting name/identifier |
| resolve_currency | CurrencyCode is supplied | CurrencyCode | `GET /fscmRestApi/resources/11.13.18.05/currenciesLOV` | CurrencyCode, Name, EnabledFlag, CurrencyFlag, StartDateActive, EndDateActive | Require one exact CurrencyCode match | CurrencyCode | Stop on no exact match or ambiguity |
| resolve_bank | The corresponding bank option is Specific bank | BankName, BankNumber, BankCountry | `GET /fscmRestApi/resources/11.13.18.05/cashBanksLOV` | BankPartyId, BankName, BankNumber | Require one exact post-filtered match for every supplied value | Corresponding BankName, BankNumber and BankCountry context; BankPartyId is evidence only | Stop on no exact match or ambiguity |
| resolve_bank_country | A bank country is supplied for the corresponding side, including All banks or All branches | BankCountry | `GET /fscmRestApi/resources/11.13.18.05/territoriesLOV` | TerritoryCode, TerritoryShortName, EnabledFlag, ObsoleteFlag | Require one exact TerritoryCode match | Corresponding BankCountry code | Stop on no exact match or ambiguity |
| resolve_bank_branch | The corresponding branch option is Specific branch | BankName, BankCountry, BranchName, BranchNumber | `GET /fscmRestApi/resources/11.13.18.05/cashBankBranchesLOV` | BranchPartyId, BankBranchName, BranchNumber, BankName, BankNumber | Require one exact post-filtered match for bank, branch and every supplied number | Corresponding BranchName and BranchNumber context; BranchPartyId is evidence only | Stop on no exact match or ambiguity |
| resolve_header_dff | Never | Native header DFF scalar | No lookup | None | Supplied values receive native type checks during input validation; Fusion may apply additional validation at import | Preserve supplied value | No lookup result required |
| resolve_line_dff | Never | Native line DFF scalar | No lookup | None | Supplied values receive native type checks during input validation; Fusion may apply additional validation at import | Preserve supplied value | No lookup result required |

Apply the option/name consistency rules in `ora_input_validation.md` to the
resulting values for both create and update requests. Resolve omitted inputs
according to the requested operation before checking the pair:

- For create requests, if both the option and its corresponding name are
  omitted, return the internal status `default pending`. The later defaulting
  step applies `All banks` or `All branches` and leaves the name blank. If a name
  is supplied without its option, input validation requests an explicit option
  and stops before lookup.
- For update assessment, preserve verified current values for omitted fields,
  combine them with the explicitly requested changes, and validate the resulting
  pair. A supplied name with an omitted option can pass this consistency check
  when the preserved option is `Specific`. Do not apply a create default. If
  the required current values cannot be established, return `evidence_unresolved`.

For either operation, an `All` option with a populated name conflicts, and a
`Specific` option requires a nonblank name. Request correction before lookup;
do not silently clear a name or infer an option. An explicitly blank update
value is a request to clear, distinct from omission. Check the resulting value
against the field's requiredness and option/name consistency rules.

## Local choices

These choices require no LOV, REST request or environment verification:

| Local choice | Input aliases | Serialized display value |
|---|---|---|
| `resolve_bank_option` | `ALL`, `All banks` | `All banks` |
| `resolve_bank_option` | `ONE`, `Specific bank` | `Specific bank` |
| `resolve_branch_option` | `ALL`, `All branches` | `All branches` |
| `resolve_branch_option` | `ONE`, `Specific branch` | `Specific branch` |
| `resolve_settlement_priority` | `EXPRESS`, `Express` | `Express` |
| `resolve_settlement_priority` | `NORMAL`, `Normal` | `Normal` |

The task importer consumes these display values. Unknown choices are rejected.
The English mappings are source-observed package values and do not establish a
cross-language contract.

## Public REST reference requests

Prefix each path with the selected environment's `restBaseUrl`. URL-encode
query values, send no request body, inspect `items` and `hasMore`, and follow
pagination before deciding that a result is absent or unique.

### Legal entity

```text
GET /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV
q=LegalEntityIdentifier='<identifier>'
fields=LegalEntityId,LegalEntityIdentifier,Name,EffectiveFrom,EffectiveTo
onlyData=true
```

When only a name is available, query or retrieve candidates by Name and apply
an exact client-side Name comparison. Require one match with a nonblank
LegalEntityIdentifier. LegalEntityId is reference evidence and does not replace
the task CSV identifier.

### Currency

```text
GET /fscmRestApi/resources/11.13.18.05/currenciesLOV
finder=CurrencyCodeAllRowsFinder;CurrencyCode=<currency-code>
fields=CurrencyCode,Name,EnabledFlag,CurrencyFlag,StartDateActive,EndDateActive
onlyData=true
```

Require an exact CurrencyCode match. EnabledFlag and CurrencyFlag can be
reported, but this public finder is not proof that the task importer applies the
same UI eligibility rules.

### Bank

```text
GET /fscmRestApi/resources/11.13.18.05/cashBanksLOV
finder=BanksLOVSearchFinder;bindBankName=<bank-name>,bindBankNumber=<bank-number>,bindHomeCountryCode=<country-code>
fields=BankPartyId,BankName,BankNumber
onlyData=true
```

The public finder uses prefix matching, so post-filter BankName and every
supplied number or country value exactly. Country is a finder input and is not
returned by this compact field list. BankNumber is distinct from
BankPartyNumber.

### Bank branch

```text
GET /fscmRestApi/resources/11.13.18.05/cashBankBranchesLOV
finder=BankBranchesLOVSearchByBankFinder;bindBankName=<bank-name>,bindBankHomeCountry=<country-code>,bindBranchName=<branch-name>,bindBranchNumber=<branch-number>
fields=BranchPartyId,BankBranchName,BranchNumber,BankName,BankNumber
onlyData=true
```

Require exact post-filtered bank and branch names and every supplied number.
The public finder and task importer have different case and blank-input
criteria, so a public match establishes reference existence, not identical task
matching.

### Bank country

```text
GET /fscmRestApi/resources/11.13.18.05/territoriesLOV
finder=TerritoryCodeAllRowsFinder;TerritoryCode=<country-code>
fields=TerritoryCode,TerritoryShortName,EnabledFlag,ObsoleteFlag
onlyData=true
```

Require an exact TerritoryCode match. Do not replace the code with
TerritoryShortName or infer extra enabled/obsolete requirements from this
AllRows reference. The Bank Charges importer has no separate country lookup; it
passes the supplied code into its bank and branch criteria.

## Result handling

| Result | Required handling |
|---|---|
| Exactly one exact match | Record the resolver, normalized input, selected public fields, environment identity, timestamp and source version; continue to dependency assessment |
| No exact match | Return invalid supplied value or unresolved verification according to the declared contract; do not guess a correction |
| Multiple exact matches | Return ambiguous and stop; do not silently select the first public row |
| Endpoint unavailable, timeout or service outage | Record UNVERIFIED_API_UNAVAILABLE with the sanitized availability failure; preserve values and continue; do not treat it as zero matches |
| Authentication or privilege failure on an additional reference GET | Record UNVERIFIED_API_UNAVAILABLE after core's permitted authentication handling and continue; never persist or print credentials |
| Successful response is malformed or untrusted | Report evidence_unresolved; do not fabricate a match or classify a successful response as an outage |
| Verification exception explicitly covers the reference | Record the check as overridden with its limitation; do not report it as passed |

## Task importer matching boundary

The reviewed importer behavior is narrower and sometimes different from the
public REST finders:

| Reference | Source-backed importer behavior | Boundary |
|---|---|---|
| Legal entity | `All` resolves through an internal `LITERAL` lookup to sentinel `-99`; a named entity binds LegalEntityIdentifier, and LegalEntityName is not unique | Never serialize `-99`; zero/multiple-match handling is not an exactly-one contract |
| Bank | Matches bank name, bank number and home-country code with equality against the eligible bank view, then consumes the first row | Optional-blank and duplicate behavior remain unsafe for portable matching |
| Branch | Matches bank name, bank home-country code, branch name and branch number with equality against the eligible branch view, then consumes the first row | BankNumber is not a branch selector; case, blank and duplicate outcomes remain bounded |
| Country | Uses HOME_COUNTRY or BANK_HOME_COUNTRY territory code as bank/branch query context | Country label translation is not part of the task selector |
| Options and settlement | Resolves the serialized display Meaning to an internal lookup code | Zero matches leave derived values unchanged and multiple matches are not explicitly rejected |

Eligible banks are effective-dated organization parties with a recognized
territory and supported institution type. Eligible branches and their parent
banks are effective-dated; the reviewed branch view also requires the linked
organization party to be active. These source facts do not convert a public
REST candidate into a guaranteed importer match.
