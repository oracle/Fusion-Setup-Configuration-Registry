# Partial REST reconciliation contract


## Current route and historical evidence boundary

Follow [governed read routes](governed-read-routes.md) for the current executable
route, prerequisites and separate attempt-evidence requirements. Selected REST GET
projections use the existing core REST client. They do not provide an equivalent
for every source/account/profile/location obligation.

The complete mixed REST/SOAP collection described by the retained interpretation
contracts below used a central SOAP extension that is excluded from the cleaned
source. `customer_api_collect.py` preserves the combined read-only collection plan; its
explicit [partial REST identity/value mode](rest-identity.md) remains available.
`customer_api_replay.py` uses the task-owned pure SOAP parser and never loads the
removed central inspector. Do not call an arbitrary SOAP operation through a generic POST,
or use developer SQL/UI as an undeclared fallback. Pure injected-client routines
remain available for synthetic regression tests. References below to previously
qualified responses are historical observations, not qualification of this source.

## Declared read-only scope

Use only after the active workflow has selected this read operation and established the exact positive decimal SiteUseId from reviewed evidence. Route GET through `core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`; use the approved environment profile and normal shared OAuth flow. Do not embed an environment, client ID, token or sample customer ID in this task.

| Item | Contract |
|---|---|
| Path | /fscmRestApi/resources/11.13.18.05/customerAccountSitesLOV |
| Method | GET |
| q | SiteUseId equal to the reviewed positive decimal ID; reject arbitrary filter text |
| fields | SiteUseId,CustomerAccountId,PartyNumber,AccountNumber,PrimarySite,SetName |
| onlyData | true |
| Pagination | Start offset 0; preserve hasMore and follow pages before claiming completeness; conflicting or duplicate exact-ID records require review |
| Match | Exact SiteUseId; compare CustomerAccountId and supplied account/party numbers with independently reviewed expected values |
| Zero results | No visible result, not proof of global absence or permission to create; consider privileges and endpoint filtering |
| One result | Partial identity evidence only; missing required projected fields remain unknown |
| Multiple results | Ambiguous; do not take the first or collapse duplicates |
| Failure | Record auth/transport/API failure without interpreting it as no matching customer |

The developer's one-row discovery probe was an API accessibility check, not an implementor default or a complete export. Ordinary task reconciliation must scope queries to its candidate and retain complete results.

The pure offline `scripts/customer_rest_site_review.py` classifier checks a supplied first-page response against the expected site-use/account IDs. It distinguishes unexpected IDs, duplicate exact matches, incomplete pagination, no visible match and single-row partial evidence. It rejects malformed row counts, missing projected fields and noninteger IDs. It does not query Fusion, merge pages or complete reconciliation; a paginated response needs the declared collector before a whole-result conclusion.

## Coverage limits

SiteUseId and CustomerAccountId can corroborate site/account identity. PartyNumber and AccountNumber are display identifiers, not replacements for original-system references. PrimarySite and SetName are endpoint values; a set display name is not a verified set code/ID, and primary semantics need task-specific comparison.

This response does not establish all seven entity/source-reference mappings, party/location/account-site ownership, existing-profile effects, receipt assignments, BILL_TO links, all input values, DFFs or before/after changes. Keep the full existing-target resolver and persisted reconciliation incomplete until their remaining source-backed contracts and runtime tests are available. Do not promote HTTP 200 or this partial GET to a passed import, completed task or blanket update authorization.

## Current profile class and account-site set code

The selected central account and active-profile reads also feed
`scripts/customer_api_profile_set_review.py`. The account service returns SetCode
on CustomerAccountSite. Select the source-resolved account-site and use IDs,
validate their account/party-site parents and use purpose, and cross-check both
SetId values before comparing ACCT_ADDRESS_SET_CODE. Do not compare a display
SetName with an input code or select a sibling site with a matching value.

For getActiveCustomerProfile, require the exact account ID, account number and
party ID, one profile ID and explicit null SiteNumber for account-level scope.
Compare ProfileClassName with an explicitly supplied CUSTOMER_PROFILE_CLASS.
Missing values remain unobserved; explicit nulls remain null. Blank input is an
observation, not a fabricated DEFAULT expectation or proof of preservation.
The collector retains these results as `profile_set` without additional calls.

These comparisons do not validate the profile-class or set catalogs generally.
The profile service selects the active profile at service execution time;
retained effective dates are not complete history or raw database timestamps.
Use the [full profile/set evidence contract](profile-set-evidence.md) for its
separate history and effect obligations. Before-phase requested-value differences
describe changes to review, not a predicted failure. Neither phase authorizes
execution or completes persisted reconciliation.

## Additional qualified source-reference read

The documented [source-system references GET](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-hubsourcesystemreferences-get.html) at `/crmRestApi/resources/11.13.18.05/hubSourceSystemReferences` supports a separate partial identity check through the same central REST client. A scoped developer probe on the target release returned all seven entity references for a retained campaign customer. This qualifies the observed projection; it does not establish complete existing-target resolution.

Select this read only after the active workflow has a reviewed candidate, environment, authorized reader and exact source-system code/reference scope. Source-system display names are not codes. Filter by the full `SourceSystem`, `OwnerEntityObject`, `SourceSystemReferenceValue` tuple, using proper query-literal escaping and URL encoding rather than accepting arbitrary filter text. Request `SourceSystemReferenceId,SourceSystem,SourceSystemReferenceValue,OwnerEntityId,OwnerEntityObject,Status,StartDateActive,EndDateActive`, with `onlyData=true`. Retain request scope, environment, principal, capture time and every response page outside the reusable task. Preserve duplicates and inactive/history rows; an empty visible result is not global absence.

| OwnerEntityObject | Entity represented by OwnerEntityId |
|---|---|
| ORA_PARTIES | Party |
| ORA_LOCATIONS | Location |
| ORA_PARTY_SITES | Party site |
| ORA_PARTY_SITE_USES | Party-site use |
| ORA_CUST_ACCOUNTS | Customer account |
| ORA_CUST_ACCT_SITES_ALL | Account site |
| ORA_CUST_SITE_USES_ALL | Account-site use |

These API lookup codes are distinct from table names. The same reference text may identify both a party-site use and an account-site use; their owner types and IDs must remain separate. Compare IDs with independently reviewed expected identities, not expectations manufactured from the response itself.

The pure offline `scripts/customer_rest_reference_review.py` classifier checks a supplied first page and expected tuples/IDs. It rejects malformed fields/counts, preserves duplicate ambiguity, and distinguishes missing, inactive and mismatched observations. Any nonzero offset or `hasMore=true` leaves pagination incomplete. It does not collect or merge pages, authenticate provenance, resolve source names, determine effective dates, authorize execution or complete reconciliation. REST date-only bounds cannot be converted to fabricated Oracle DATE seconds for `customer_identity_review.py`.

`scripts/customer_api_snapshot.py` adds pure candidate-scoped planning and review
for API-native owner lookup. Its `plan` validates the candidate and binds its
hash, operation and environment to exact reference tuples. Supply source codes
only from the separately selected central source-name service. Equal tuples
share a query, while every input row and its seven entity roles remain in the
plan. Missing sources or unqualified finder literals remain unresolved.

The selected central collector must retain both unfiltered and active-finder
responses, their request scopes, hashes, capture times and authenticated
principal. Follow consecutive pages, with a maximum of twenty per query; a
remaining `hasMore=true` is incomplete. `review` preserves every row, including
duplicates across pages, and stops owner resolution on mismatched scopes,
ambiguity, inactive results or disagreement between the two reads. It requires
no SQL-derived IDs or fabricated expected values. These sequential reads are
not a transactionally consistent snapshot. A resolved owner is a lookup result,
not independent corroboration, physical-parent verification, permission to
create/update or complete persisted reconciliation.

The authoring qualification collected fourteen reference tuples for a retained
three-row/two-party candidate and used the resolved account IDs for the fixed
central account/profile reads. No SQL or prior resolved IDs were inputs.
This qualifies the lookup composition only. The pure module has no network,
authentication or import code; complete functional collection and value/effect
composition remain subject to the remaining coverage gates below.

`scripts/customer_api_hierarchy.py` then compares the seven API-resolved owners
with the fixed account SOAP response and organization Address/AddressPurpose
collections. It checks account-to-party, party-site-to-party/location,
account-site-to-account/party-site, both site-use parents/purposes and common
reference-set identity. It also compares the explicitly requested account
number/description/type/class and the documented basic address projection.
Duplicate selected targets, incomplete pages, missing fields, contradictory
XML nulls and wrong parents cannot pass. The authoring API-native three-row
case passed these selected checks without SQL inputs. This is not full
87-field reconciliation: omitted-field effects, all DFFs, profile history,
receipt/tax effects and sibling changes remain outside this helper.

The target-release resource metadata also exposes
`SSRByOsOsrOwnerEntityObject` with `OwnerEntityObject`, `SourceSystem` and
`SourceSystemReferenceValue` finder variables. Reviewed `SourceSystemReferenceVO`
uses server-side active-date and status criteria, with one-result limit and an
error on excess matches. A same-day campaign account reference returned its
expected owner through this finder. This is an additional server-evaluated
active-reference observation; retain the unfiltered exact-tuple query too, so
inactive/history/duplicate rows are not silently removed. Do not equate the
finder's active predicate with the loader's separate profile-update probe, which
does not filter reference status. No timestamp precision or database clock may
be fabricated from the returned dates.

Documented [organization addresses](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-huborganizations-partynumber-child-address-get.html), [address purposes](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-huborganizations-partynumber-child-address-addressnumber-child-addresspurpose-get.html), and [billing site activities](https://docs.oracle.com/en/cloud/saas/financials/26b/farfa/op-receivablescustomeraccountsiteactivities-get.html) can corroborate selected parents/values through the central client. In the address response, `AddressId` identifies the party site and `LocationId` the location. Address-purpose IDs identify party-site uses, whereas `BillToSiteUseId` identifies an account-site use. Do not equate `BillToSiteNumber` with the worksheet `PARTY_SITE_NUMBER`; the observed billing number matched the account-site-use location value in developer verification. Billing reads require appropriate AR access; a 403 is an authorization result, not absent customer data. None of these selected projections covers the complete account-site/ship-to hierarchy, all fields, profiles, receipts, tax, DFFs or before/after effects.

## Task-owned account and profile SOAP reads

The task adapter supplies `customer-account` and `active-customer-profile`
SOAP reads through unchanged core OAuth and byte transport. The following
interpretation obligations are unchanged from the earlier collector.
Never select an account by an unreviewed display-name match.

Target-release developer qualification returned the campaign account, its
Bill-to and Ship-to sites/uses, their actual account/party-site parents and set
IDs, and the Ship-to's existing Bill-to link. It also returned the active
account profile ID, class name and effective bounds. Retain the raw response
and central capture/hash manifest; compare each expected ID and relationship.
Do not map a missing element to null or assume missing child collections prove
global absence. The profile operation returns the active profile, not a full
history/future inventory. Flexfield exposure depends on deployed metadata;
unreturned segments remain unverified.

The documented [receipt assignments GET](https://docs.oracle.com/en/cloud/saas/financials/26b/farfa/op-receiptmethodassignments-get.html)
supports `receiptMethodSearch` scoped by the reviewed customer account number.
Use its finder rather than an undocumented queryable attribute. Preserve
pagination and returned account/site scope. A successful empty collection
means no visible assignments, not independent proof of global absence.

The former companion used `source-system-by-name` for source-name resolution,
using the documented FoundationSourceSystemService `findSourceSystem` operation
with a fixed exact-name filter. Its target-release read returned the configured
display name and code. The client rejects absent, ambiguous or non-active/TCA
results; effective dates and language applicability still require review.
Never replace an unresolved source name with a guessed code.

The target-release `/fscmRestApi/resources/11.13.18.05/partyTaxProfiles/describe`
exposes queryable `PartyId` and `PartyTypeCode`, plus
`RepresentativeRegistrationNumber`. A GET scoped to the independently reviewed
party ID and `THIRD_PARTY` type returned an empty complete visible collection
for the tested customers, agreeing with developer observations. Retain party
and party-site tax scopes separately. The later nonempty tax case also qualified
exact representative-number mapping. Neither observation establishes independent
asynchronous callback execution or global absence.

These reads expand the supported collection options. They do not yet compose
the complete candidate-bound before/after reconciliation bundle. Date precision,
all requested/omitted effects, historical profiles, asynchronous tax effects and
complete flexfield coverage must retain their explicit dispositions.
SQL/JDBC/Publisher remains developer testing only and cannot replace missing
functional collection steps.

## Full location projection

The removed companion's fixed `location` operation called
`getLocation(locationId)` on the documented
[Trading Community Location service](https://docs.oracle.com/en/cloud/saas/sales/oesws/tradingcommunitylocation-d41e153230.html).
A future approved equivalent must use the location owner resolved from the exact candidate source tuple, never an
account or party-site ID. Target-release WSDL/XSD and live FINUSER1 calls
qualified this read. It exposes all twenty-five location fields in the task's
persisted-value contract, including fields absent from the address REST
projection: timezone, short description and sales-tax location values.

`scripts/customer_api_location_review.py` projects these fields and compares
nonblank inputs with exact returned text. Missing XML fields remain unknown;
explicit nulls are retained; duplicate scalars, malformed/null identities and
unexpected response operations cannot pass. Blank inputs receive an omitted
input observation, not an assumption of null, preservation or a verified
default. MAIL_STOP remains a party-site field. The three-row API-native case
passed selected location comparisons using API-resolved IDs and no SQL inputs.
No location response certifies all customer fields, before/after effects or
historical location/profile coverage.

## Receipt assignment projection

The documented [receipt assignment GET](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-receiptmethodassignments-get.html)
supports the receiptMethodSearch finder with CustomerAccountNumber. Collect all
pages for the exact reviewed account; do not filter away other methods, sites,
primary flags or effective periods. Retain the request scope and response hashes.
The target-release positive case returned a nonempty BILL_TO assignment with its
account/site numbers, method name, primary indicator and date-only boundaries.

`scripts/customer_api_receipt_review.py` compares these selected values with
the validated candidate row. Explicit English response context is required for
the observed Yes/No representation. It does not rewrite Y/N input. Missing EndDate
is different from explicit null; duplicate IDs, unqualified language and wrong
account scope fail. Multiple matching periods require review. Other assignments
remain counted, even when the selected values match.

This projection cannot establish raw parent IDs, method/class business validity,
negative batch markers, before/after deltas or harmless replay. Date-only values
must not be padded into asserted database timestamps. Compose supported hierarchy
and before/after evidence separately; developer SQL corroboration cannot qualify
that functional composition. No receipt result authorizes execution or reports
complete persisted reconciliation.

Before-phase collection additionally calls `customer_api_receipt_review.review_before`.
It compares visible periods for the exact account/site/method with the proposed
start date derived from ACCOUNT_ESTABLISHED_DATE (the reviewed control default
is 1900/01/01 when omitted). This worksheet supplies no receipt end date. An
existing open period, or a period ending on/after the proposed start, requires
conflict review before approval. Other sites/methods remain retained. Missing
dates or scope and incomplete pagination cannot produce a clear result.

This deliberately reports a visible date-only conflict; it does not claim to
reimplement the loader's Oracle DATE/MONTHS_BETWEEN, T1/T2/T3 branches or prove
receipt-class eligibility. Reviewed 26D ar_customer_interface_pkg.pkb lines
629–757 validate overlapping existing assignments; lines10127–10210 insert
assignments rather than establish an update-in-place contract. Independently
bind the source references, account/site ownership and BILL_TO purpose. A
visible match after a successful load cannot authorize replay. Use the normal
design gate to resolve a conflict, without dropping input or submitting it to
discover a known conflict again.

## Tax profile projection

The deployed partyTaxProfiles GET contract exposes PartyId, PartyTaxProfileId,
PartyTypeCode, RepresentativeRegistrationNumber and boolean CustomerFlag,
SiteFlag and SupplierFlag. The reusable collector requests all profile types
for the API-resolved exact PartyId, with complete pagination; it never filters
to the expected representative number or a desired flag value.

`scripts/customer_api_tax_review.py` compares the supplied representative number
with exactly one THIRD_PARTY profile. It rejects foreign party IDs, duplicate
profile IDs, numeric value coercion and nonboolean API flags. Missing keys are
not explicit nulls. Other profile types remain counted. This is a selected-value
comparison only: an empty response is not callback completion, a match can
predate an update, and neither observation authorizes repeating an import.
Use the [tax evidence contract](tax-evidence.md) for asynchronous and
before/after effect obligations.

## Independent account-number search

The removed `customer-account-by-number` read used the documented
[findCustomerAccount operation](https://docs.oracle.com/en/cloud/saas/sales/oesws/Find-Customer-Accounts.html)
with literal AccountNumber equality, case preserved and no anticipated ID, party
or status filter. The collector compares the returned account and party IDs with
independently resolved source-reference owners, including before-phase captures
whose references are absent. A foreign number match stays a conflict to review.
The fixed two-result bound detects ambiguity; a saturated result is incomplete.
Zero records means no API-visible match, not unrestricted database absence or
permission to create. Party-number and party-site-number checks remain separate.

## Deployed account DFF mapping

The Flexfields Runtime Metadata Description Service provides a read-only
deployed-metadata describe route. The
account service's imported DFF XSD identifies the base locator used here:
`http://xmlns.oracle.com/apps/cdm/foundation/parties/flex/custAccount/CustAcctInformation`.
The collector delegates GET to core at
`/fscmRestApi/applcoreApi/latest/flexfields/runtime/x/describe`, with `x` set to
that locator and `mode=verbose`. This returns physical `segmentColumnName`
mappings. Do not infer physical columns from a segment's display/API name.

For a persisted non-null context, collect its exact `discrValue` with
`includesBaseType=true`. Require the same metadata revision, application,
flexfield and global mappings. Compare the actual context with the candidate;
do not substitute the candidate's expected context into an after-state read.
`customer_api_dff_review.py` checks the account/DFF parent identity and projects
deployed string mappings for ATTRIBUTE_CATEGORY and ATTRIBUTE1–30. Numeric/date
DFF columns are separate and outside these worksheet fields. Missing XML differs
from explicit null. Unexposed physical columns remain unknown; their absence
from deployed metadata does not prove blank storage or preservation on update.

Live read qualification established the metadata mapping and null observations;
nonempty campaign outcomes are retained separately. This read does not configure
or deploy flexfields, mutate customer data, certify all thirty stored columns,
or complete before/after reconciliation. Tenant context names and mappings are
runtime evidence, never reusable defaults or literals in the task implementation.


## Independent organization and party-site number searches

The collector selects `organization-by-number` and
`organization-by-site-number` SOAP reads for supplied Customers numbers. The task-owned adapter implements these reads over unchanged core transport. The fixed
findOrganization predicates search exact PartyNumber, or PartySite EXISTS with
nested PartySiteNumber equality, without anticipated parent or status filters.
The task compares actual returned party/site/location IDs with the separately
resolved source-reference owners. Foreign parents remain review conflicts;
multiple parents or matching children remain ambiguous. No first-match selection.

This service covers organizations visible to the authenticated principal, not
person parties or unrestricted database contents. An empty result is explicitly
scoped and cannot authorize creation. Returned children do not prove a complete
site inventory or history. These checks run even when source references are
unresolved; no SQL IDs or expected parent IDs are injected into searches.

The deployed OrganizationParty SDO also exposes PartyName, DUNSNumberC,
JgzzFiscalCode and boolean GSAIndicatorFlag. The fixed number reads select these
alongside the existing identity fields without adding a parent/status filter.
`customer_api_business_values.py` compares their exact source-bound values and
the selected PartySite number/name/identifying flag/Mailstop. The account service
provides account name/type/class/date, site language/translated name, and use
purpose/primary flag/location. Known boolean projections map true/false (or 1/0)
to worksheet Y/N. AccountEstablishedDate is compared as a date-only value; do
not infer Oracle DATE seconds or silently truncate another response format.

Current statuses, site Bill-to/Ship-to/Market flags, the use's BillToSiteUseId,
and party-site-use values are retained as observed metadata. They are not proof
of complete sibling coverage. A value match cannot replace identity, parent,
requested effect, history or source-reference checks.

## API before/after comparison

After both selected capture steps, compare retained directories using:

```text
python <task-folder>/scripts/customer_api_effect_review.py \
  --candidate <reviewed-candidate.zip> --operation <create|update|mixed> \
  --environment-url <selected-https-origin> \
  --before <private-before-directory> --after <private-after-directory> \
  --output <new-private-effect-report.json>
```

This verifies capture bytes and binding files, candidate/environment/operation,
phase order and row alignment. It compares 77 mapped fields only where actually
returned. Missing fields and unexposed DFFs remain unknown; explicit nulls stay
null. A changed owner ID prevents comparison as one entity. An omitted-input
value change and a status/flag metadata change require review. A before snapshot
whose requested values already match is distinguished from an observed update.

This is the API-native scoped counterpart of the supplied-evidence effect
reviewer. It does not convert date-only responses into fabricated SQL-shaped
history. Source references, receipt/tax effects, Bill-to target resolution,
unexposed columns, history, full sibling inventories and attempt causality retain
their separate checks. Its successful execution is not complete reconciliation
or import approval. Keep both source capture directories with the report.

Apply [business-outcome scope](business-outcome-reconciliation.md) to these
observations with `customer_reconciliation_scope.assess_values`. Supplied DFF
context/segments remain required. Unused hidden columns are disclosed rather
than imposing a blanket thirty-column prerequisite. Context or deployment
changes, missing requested values and visible unrequested changes still need
review. The scoped value result is separate from identity, relationship, relevant
supporting effects, attempt association and Journey completion.
