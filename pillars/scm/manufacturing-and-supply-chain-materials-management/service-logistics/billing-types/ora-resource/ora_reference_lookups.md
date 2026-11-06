# Billing Types Reference Lookups

## Source and Authority

The developer supplied the billingTypes resource and selected SILVER_UNLOCKED. Authorized live describe and complete collection GET were retrieved through core Data Loader on 2026-10-19. No customer values or record IDs are stored here. Fusion is the authority for current identity and state; supplied selectors are request inputs, not authoritative record evidence.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BILLING_TYPES.RESOLVE_CATEGORY | step | 12 | reference_lookup | passed->BILLING_TYPES.RESOLVE_TYPE;failed->BILLING_TYPES.RETURN_ISSUES | BILLING_TYPES.VALIDATE_INPUT | stop | POST only: execute resolve_billing_category |
| BILLING_TYPES.RESOLVE_TYPE | step | 14 | reference_lookup | passed->BILLING_TYPES.READ_CREATE_DUPLICATES;failed->BILLING_TYPES.RETURN_ISSUES | BILLING_TYPES.RESOLVE_CATEGORY | stop | POST only: execute resolve_billing_type_option |
| BILLING_TYPES.READ_CREATE_DUPLICATES | step | 16 | reference_lookup | passed->BILLING_TYPES.CHECK_CREATE_UNIQUENESS;failed->BILLING_TYPES.RETURN_ISSUES | BILLING_TYPES.RESOLVE_TYPE | stop | POST only: execute check_billing_type_duplicate and return its match count |
| BILLING_TYPES.RESOLVE_REFERENCE | step | 20 | reference_lookup | passed->BILLING_TYPES.EXECUTION_GATE;no_change->BILLING_TYPES.NO_CHANGE;failed->BILLING_TYPES.RETURN_ISSUES | BILLING_TYPES.VALIDATE_INPUT | stop | Resolve the single current record for a supported EnabledFlag PATCH; return no_change when its current flag already equals the request |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_billing_type | Before source preparation and during captured-source rule evaluation; repeat after completed loading for requested verification | Selected environment and origin; explicit exact BillingTypeCode or BillingTypeId selector | GET /fscmRestApi/resources/11.13.18.05/billingTypes through core/fusion-api/rest-api-client/scripts/fusion_rest_client.py; apply Collection Read Contract below | All describe-declared scalar attributes; use BillingTypeId, BillingTypeCode, EnabledFlag, BillingCategory and ObjectVersionNumber for identity/state and preservation evidence | Read the complete unfiltered collection using onlyData=true, limit and offset until hasMore=false; filter the returned collection in memory by exact case-sensitive supplied code or exact supplied ID. If both selectors are supplied, both must identify the same record. Require exactly one match. | BillingTypeId to captured source identity; BillingTypeCode to selected identity evidence; EnabledFlag to current-state evidence; other scalar values to in-memory preservation evidence only | Zero matches: stop and report target not found; multiple matches: stop and request an unambiguous selection; no arbitrary first match and no implicit create |


## Lookup Operations

These create-authoring reads are selected from the live billingTypes describe LOV links. Use core/fusion-api/rest-api-client/scripts/fusion_rest_client.py with GET, the selected profile and REST-Framework-Version=9. Pass finder as a query parameter, never as a changed host. Read every page with onlyData=true, limit and offset; fail on malformed or nonadvancing pagination. The fields below come from describe's lookup attributeMap and displayAttributes. No mutation is authorized by these read-only steps. Each lookup is evaluated only by its named Task Node; do not run another node's resolver merely because its table is in the same file.

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_billing_category | Create contract authoring and create validation | User's exact category code or meaning; Fusion lookup type ORA_RCL_BILLING_CATEGORY | /fscmRestApi/resources/11.13.18.05/standardLookupsLOV with finder=LookupTypeFinder;LookupType=ORA_RCL_BILLING_CATEGORY | Full scalar response; LookupCode and Meaning for exact selection | Read complete finder result; exact code first, otherwise case-insensitive trimmed exact Meaning; require one match | LookupCode to BillingCategory | Stop on no or multiple matches; never synthesize a category |
| resolve_billing_type_option | Create contract authoring and create validation | User's exact type code or meaning; Fusion lookup type EGP_MATERIAL_BILLABLE_TYPE | /fscmRestApi/resources/11.13.18.05/standardLookupsLOV with finder=LookupTypeFinder;LookupType=EGP_MATERIAL_BILLABLE_TYPE | Full scalar response; LookupCode and Meaning for exact selection | Read complete finder result; exact code first, otherwise case-insensitive trimmed exact Meaning; require one match | LookupCode to BillingTypeCode | Stop on no or multiple matches; never synthesize a type |
| check_billing_type_duplicate | POST before source preparation and again during captured-source validation | Exact BillingTypeCode returned by resolve_billing_type_option; selected Fusion environment | GET /fscmRestApi/resources/11.13.18.05/billingTypes through core/fusion-api/rest-api-client/scripts/fusion_rest_client.py; apply Collection Read Contract below | All describe-declared scalar fields; compare BillingTypeCode and retain BillingCategory as conflict evidence only | Read every page; exact case-sensitive match by BillingTypeCode across all categories, including disabled records. Do not reduce the key to category plus code. | Exact duplicate count and matched identity/category evidence in memory for the design node | Zero matches returns count zero; one or more returns that count for the design gate. Incomplete/failed reads block rather than reporting zero. |

## Collection Read Contract

This is the assisted GET workflow selected by resolve_billing_type and check_billing_type_duplicate. It also serves an explicit Billing Types current-data request. Use the existing core REST client for each declared request; no standalone BO-reader script is required. The calling agent evaluates the returned pages and lookup evidence in memory. This selects reads only and does not change the core Data Loader route for mutations.

Read the core REST client's SKILL.md and references/fusion-rest-api.md before execution. The registration request shape below is already used by core Data Loader's discriminator-prefix lookup; the product describe and collection paths are the task's existing confirmed contracts.

| Step | Declared request or check | Required result |
|---|---|---|
| Target | Select the project environment and HTTPS origin; compare them with environment and restBaseUrl in the chosen profile before invoking the client | Exact environment/origin match; use --properties for every request. Core OAuth owns trust enrollment, credentials and service-origin enforcement. A mismatch blocks before authentication. |
| Registration | GET /hcmRestApi/resources/latest/dataLoaderBusinessObjects with q=BusObjTopDiscriminator LIKE 'billingTypes%', onlyData=true, limit=500 and offset=0; use the pagination rules below | From every returned page, retain exact BusObjTopDiscriminator=billingTypes matches with nonblank BusinessObjectId. Deduplicate only identical BusinessObjectId/discriminator identities with consistent metadata. Require one identity and ObjectType=ADF_REST. Missing, conflicting or ambiguous registration blocks. |
| Describe | GET /fscmRestApi/resources/11.13.18.05/billingTypes/describe | Require the exact billingTypes resource and nonempty described attributes. Require BillingTypeId, BillingTypeCode, BillingCategory and EnabledFlag. Do not infer fields from a sample or from loader columns. |
| Collection | GET /fscmRestApi/resources/11.13.18.05/billingTypes with onlyData=true, limit=500 and offset=0; use the pagination rules below | Read the unfiltered complete collection before applying either resolver's local exact-match rule. Require every product record to have a nonblank decimal-string BillingTypeId of at most 18 digits, nonblank BillingTypeCode and Boolean EnabledFlag. Keep described scalar fields, excluding links and context. |
| Pagination | Start each collection at offset=0. Require an items array of objects and a Boolean hasMore. If present, offset must equal the requested integer and count must equal the number of items. Reject pages larger than the requested limit. Increment offset by the returned item count while hasMore=true | Stop only on hasMore=false. A continuing empty page, a repeated record page or a repeated BillingTypeId in product records blocks completeness. Ignore response-supplied links. |
| Bounds and failures | Limit each paginated collection to 100 pages and the whole lookup to 300 seconds. Check elapsed time before each request and immediately after its response; use --timeout with at most 60 seconds or the smaller remaining time budget | On exhaustion, HTTP/auth/privilege failure, malformed response or missing described identity fields, discard partial records and stop. Report stage, environment, last offset and safe HTTP status; never report zero duplicates after a failed read. No blind retry or alternate client. |
| Output | Publish a collection/count for an explicit read, or retain complete current values in memory for the named resolver | Keep customer rows and response bodies out of files. Do not use --output. Only sanitized routing/status diagnostics may be persisted; no tokens, authorization URLs or sensitive body text. |

Pass relative request paths, --method GET, --header REST-Framework-Version=9 and repeated --query key=value options through the core client. The selected profile is the only target authority. These read contracts do not permit direct POST/PATCH requests or bypass mutation approval.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Environment selection | Require the expected environment and HTTPS origin to match the captured core OAuth profile before any network request. Never hardcode the sample host into another project. |
| Registration and describe | The Collection Read Contract requires one exact ADF_REST registration and matching describe attributes before product records are read through the shared REST client. It uses core OAuth and never follows response links. |
| Partial or failed collection | Stop; do not resolve identity or claim uniqueness from partial pages, sample enrichment, a cached read or job counters. |
| Changes after preview | If material request/source/target/observed state changes before submission, invalidate the earlier preview and approval. Return through core's read, validation and Task Hook preview/approval workflow with a fresh immutable artifact and matching preflight. Never edit an approved artifact/envelope or submit changed material under the earlier approval. |
| Data handling | Retain current values in memory for rule evaluation and verification; do not persist customer values, response bodies or tokens in repository/project files. |
