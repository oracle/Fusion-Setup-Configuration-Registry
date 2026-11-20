# Reference Lookups

## Source

- Oracle readiness: Redwood: Configure Collaboration Messaging, 26B, https://docs.oracle.com/en/cloud/saas/readiness/erp/26b/fins26b/26B-fin-wn-f43222.htm
- Oracle readiness: Streamline the Import and Export of Messaging Setup Data, 26C, https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46531.htm
- Oracle FSM 26C: migration preparation and setup security, printed pages 41 and 75–79, https://docs.oracle.com/en/cloud/saas/applications-common/26c/oafsm/using-functional-setup-manager.pdf
- Oracle readiness: Redwood with classic flows, 26D, https://docs.oracle.com/en/cloud/saas/readiness/scm/26d/proc26d/26D-procurement-wn-f50500.htm

## Shared Lookup Execution Contract

These resolver definitions are read-only contracts selected by the invoking
task workflow. They do not independently authorize a Fusion request. Before
any GET, complete that workflow's input, environment identity, privilege,
source-route and diagnostic checks. Missing or stale route evidence blocks
execution; do not use browser navigation, captured authentication, guessed
endpoints or another integration as a fallback.

| Lookup Family | Common Skill | Execution Contract |
|---|---|---|
| CMK partner identifier standard lookup | core.fusion-api.apps-common.lookups, references/standard-lookups.md | the qualified field contract and the qualified field contract identify LookupPVO/FND_LOOKUPS. Read the exact ORA_CMK_EXT_PTNR_ID_TYPE standard lookup and its returned lookupCodes child through the shared client. Do not require generic ApplicationCode or switch views after an authorization failure |
| CMK and partner UI LOV collections | core.fusion-api.rest-api-client, references/fusion-rest-api.md | Bind each collection below to its source-confirmed runtime path in the selected environment. Retain the supplied finder, parent scope and projection. These business-object LOVs are not Application Common lookup types |
| Feature state | core.fusion-api.rest-api-client, references/fusion-rest-api.md | Use the explicit Features collection path and filter in the owning resolver; this is not an Application Common lookup-code request |

Read the selected common skill and its routed reference before execution. All
requests use core/fusion-api/rest-api-client/scripts/fusion_rest_client.py
with the selected environment properties, method GET, no body, and
REST-Framework-Version: 9. Pass each parameter as a separate --query key=value
argument; let the client encode it once. Use structured argument values rather
than interpolating selections or search text into shell commands. Shared Core
owns OAuth, token caching, configured HTTPS host validation, redirect rejection
and its single 401/403 refresh retry; do not implement these in a pillar adapter
or add another authentication retry loop.

Follow only validated same-target resource links. Preserve query and parent
scope across REST pages and require a complete, well-formed response before
claiming uniqueness or absence. A runtime route is required input, not a
permanent captured URL. Record sanitized status, stage, failure class, message,
recommended action, environment and evidence references in the invoking
project run; keep tokens, headers and raw protected responses out of durable
artifacts. Classify lookup failures as input validation, catalog mismatch,
auth/authz, transport/environment, Fusion API, process timeout or artifact
persistence as applicable. No lookup performs a write or bypasses the invoking
workflow's approval and immutable-artifact gates.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_simplified_feature_state | Automatically before simplified configuration export/import or bounded supplier qualification; do not ask the user to check the feature | Configured source or destination host and ORA_CMK_B2B_DOCUMENT_SETUP | Route through core.fusion-api.rest-api-client using its references/fusion-rest-api.md and scripts/fusion_rest_client.py; GET /fscmRestApi/resources/11.13.18.05/features with q=FeatureCode='ORA_CMK_B2B_DOCUMENT_SETUP', fields=FeatureCode,FeatureType,EnabledFlag, and onlyData=true | FeatureCode,FeatureType,EnabledFlag | Exactly one same-host item with the exact feature code, FeatureType: FEATURE, and EnabledFlag: Y; a Redwood page profile is not evidence | Feature code, enabled flag, source or destination host, environment, UTC read time | Stop before export or import if disabled, absent, ambiguous, unreadable, or cross-environment |
| resolve_cmksc_customer | Customer partner-property create intake or final reference validation; supplier and unchanged-package operations skip; applies to ensure_partner_setup selections as well | Selected target, source-confirmed runtime route, partner kind and optional customer selection | For reference_profile native_customer_account_fsm selected before intake, apply the Public Existing-Customer Account FSM Profile below: qualify a represented native CustomerNumber/PartnerKey1 through the current public organization read. All other profiles retain the following contract. Through core.fusion-api.rest-api-client, GET b2bCustomersLOV with onlyData=true; fields=CustomerId,CustomerName,CustomerNumber; limit=25; offset=0 | CustomerId, CustomerName, CustomerNumber and pagination | Require explicit customer/supplier choice before GET; exact returned identity or one exact number or case-insensitive exact name within the complete response. Partial text narrows displayed choices only | Selected CustomerId, exact CustomerName and CustomerNumber; derive customer number without another question | selection_required for missing partner kind or customer choice, with no GET until kind is known; not_applicable for supplier/unchanged import; blocked on invalid response or route |
| resolve_cmksc_customer_account | Customer partner-property intake after selected customer; specific-account scope only; applies to ensure_partner_setup selections as well | Verified CustomerId, customer-wide or specific-account scope, optional account selection and source-confirmed runtime route | For reference_profile native_customer_account_fsm, apply the declared current customerAccountSitesLOV read and exact party/account join below; coalesce repeated site projections of the same account. All other profiles retain the following contract. Through core.fusion-api.rest-api-client, GET b2bCustomerAccountsLOV with finder=customerAccountFinder;bindCustomerID=<selected CustomerId>; onlyData=true; fields=CustomerAccount,CustomerAccountDescription,CustomerAccountId; limit=25; offset=0 | CustomerAccount, CustomerAccountDescription, CustomerAccountId and pagination | Require selected customer before GET; exact CustomerAccountId or one exact CustomerAccount in the complete customer-scoped response. Reject an account from another customer; do not use account description as an identity | Retain CustomerAccountId, exact CustomerAccount and CustomerAccountDescription with parent CustomerId; display account number plus description | selection_required without GET if account scope is missing; not_applicable without GET for explicit customer-wide scope, supplier or unchanged import; selection_required for an unresolved account; blocked on malformed or incomplete scoped read |
| resolve_cmksc_supplier | Supplier partner-property intake or final reference validation; customer and unchanged-package operations skip; applies to ensure_partner_setup selections as well; also when explicitly invoked by create_account_number_fsm, create_ship_to_assignment_fsm or the account/ship-to REST preflight | Selected target, supplied supplier number or name, optional previously resolved identity and source-confirmed runtime route; Partner Properties Public Sources | Through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/suppliersLOV with onlyData=true; fields=SupplierId,SupplierName,SupplierNumber; limit=25; offset=0. When SupplierNumber is supplied, add q=SupplierNumber='<escaped exact number>'. Otherwise use q=SupplierName='<escaped exact name>' for an explicitly exact name, or the unfiltered request only for Browse. Apply Supplier Exact Selection and Resume below | SupplierId,SupplierName,SupplierNumber and pagination | Complete the current filtered scope to hasMore=false; coalesce identical repeated SupplierId projections using Partner Lookup Execution. Require exactly one distinct identity and agreement with every supplied number, name and retained ID. A filtered result need not complete the unfiltered supplier universe; it establishes only the selected supplier. No substring, first-row or number-to-ID inference | Retain SupplierId, exact SupplierName and SupplierNumber with target, query fingerprint, read time and scoped completeness; derive internal identity without asking for it | selection_required for absent input, complete zero-match or multiple distinct candidates; blocked for conflicting supplied references, unexpected filter results, incomplete or malformed response, or failed request; no automatic unfiltered fallback |
| resolve_cmksc_supplier_site | Supplier intake after supplier selection; applies to ensure_partner_setup selections as well; also create_account_number_fsm, create_ship_to_assignment_fsm and the selected account/ship-to REST preflight after supplier resolution; explicit supplier-level create_supplier_property with no requested site/BU returns not_applicable without GET. Never infer this scope from a no-match or failed site read | Verified SupplierId, optional site selection and source-confirmed runtime route | Through core.fusion-api.rest-api-client, GET suppliersLOV/<selected SupplierId>/child/sitesLOV with fields=ProcurementBU,ProcurementBUId,SupplierSite,SupplierSiteId; limit=25; offset=0 | ProcurementBU, ProcurementBUId, SupplierSite, SupplierSiteId and pagination | Exact SupplierSiteId or one case-insensitive exact SupplierSite within the complete selected-supplier scope; use ProcurementBU as disambiguating context. Require nonempty returned ProcurementBU and ProcurementBUId for the selected site | Retain SupplierSiteId, exact SupplierSite, ProcurementBU and ProcurementBUId with parent SupplierId; derive Business Unit rather than asking again | selection_required for missing or ambiguous site; not_applicable for customer/unchanged import; blocked for mismatched parent, missing BU or incomplete read |
| resolve_cmksc_provider | Partner-property create intake after partner resolution; revalidate provider passed by Run Book; applies to ensure_partner_setup selections as well | Selected target, source-confirmed b2bProviders runtime route and optional retained Provider selection | For reference_profile native_customer_account_fsm, qualify the existing Service Provider through the public exact-name tuple and matching complete native provider-task export specified below. No attachment/category setting is inferred; requests needing those extra settings do not qualify for this limited profile. All other profiles retain the following contract. Through core.fusion-api.rest-api-client, GET b2bProviders with finder=hcmSearch;bindUserDefined=true,bindInput=; onlyData=true; totalResults=true; fields=AttchProcessMthd,ProviderId,ProviderName,ProviderType,ProviderTypeMeaning,SpCategory,UserDefinedFlag; limit=25; offset=0 After selection, GET the published /fscmRestApi/resources/11.13.18.05/b2bServiceProviders after describe confirms ServiceProviderId,ServiceProviderName,UserDefined. Use a safely escaped exact-name q filter and complete paging; require one exact name, matching retained provider ID and stored flag Y or N. This selected read is part of the resolver; never fallback to a write or UI boolean conversion. For a declared public supplier-property operation selected at intake with an existing Service Provider business name, qualify that supported scope through the documented b2bServiceProviders read and a fresh complete no-criteria same-target provider-task export obtained by the invoking shared task-export workflow. Require one exact ProviderName/UserDefined/ProviderType export tuple with Service Provider type, then one exact public ServiceProviderName/UserDefined tuple and its current ID. The public tuple supplies only its documented identity/stored flag; the export qualifies provider type. This separately selected profile does not call an unpublished b2bProviders route, does not infer Direct-provider absence, and does not supply partner identifiers. Direct providers, unknown/multiple type tuples or missing export evidence retain their precise capability block; do not substitute this Service Provider profile after a failed write. | ProviderId, ProviderName, ProviderType, ProviderTypeMeaning, SpCategory, AttchProcessMthd, UserDefinedFlag and pagination | Exact ProviderId or one case-insensitive exact ProviderName in the complete captured user-defined scope; verify same-target retained provider without reasking. Do not silently broaden the finder or infer PartnerId from ProviderId For the explicit existing-Service-Provider public-operation profile, require exact name/stored-flag/type export evidence and current unique public identity; never equate the public UserDefined flag with ProviderType or invent category/attachment fields not requested by that operation. | Retain ProviderId, exact ProviderName, ProviderType code, ProviderTypeMeaning and UserDefinedFlag. Display Provider Type without asking for it; these projected fields do not supply Partner ID or Partner ID Type Retain the public tuple and its evidence fingerprint for SPUserDefined; a missing or conflicting tuple blocks preparation. | selection_required for missing/invalid/ambiguous provider; not_applicable for unchanged import; blocked on incomplete read or conflicting retained identity |
| resolve_cmksc_customer_business_unit | Customer properties only when Business Unit supplied or requested; supplier BU comes from its site; ensure_partner_setup resolves only a set BU | Selected target, optional Business Unit choice or explicit omission, source-confirmed runtime route | Through core.fusion-api.rest-api-client, GET finBusinessUnitsLOV with onlyData=true; totalResults=true; fields=BusinessUnitId,BusinessUnitName; limit=25; offset=0 | BusinessUnitId, BusinessUnitName and pagination | Exact BusinessUnitId or one case-insensitive exact BusinessUnitName in the complete response; no default or first-row selection | Retain selected BusinessUnitId and exact BusinessUnitName as customer business input for the captured OrderProcessingBUId field; PartnerKey3 correspondence is established by the qualified field contract; apply the qualified field contract/the qualified field contract-backed preparation contract and current target checks | not_applicable without GET for explicit omission, supplier or unchanged import; selection_required for select/skip decision or unresolved supplied choice; blocked on incomplete or malformed read For ensure_partner_setup an unspecified or clear BU skips GET and customer questions; reconciliation records its state separately. |
| qualify_cmksc_supplier_property_state | Explicit read-only supplier-property qualification after feature and identifier-type checks | Configured project host and privately retained approved expected supplier/site/provider property; approved expected values are comparison inputs, never current-state authority | Through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bSupplierPartnerProperties with finder=getBySupplierIdAndSiteId;bindSupplierId=<retained SupplierId>,bindSupplierSiteId=<retained SupplierSiteId>; fields=PartnerPropertyId,SupplierId,SupplierSiteId,ProcurementBUId,ServiceProviderId,PartnerId,PartnerIdTypeCode,PartnerTypeCode,ApplicationPartnerCode,DvmGroup; onlyData=true; limit=25; offset=0. Source: Partner Properties Public Sources | Requested property fields and complete pagination | Read every page preserving supplier/site scope; require exact numeric supplier/site and provider equality and PartnerTypeCode Supplier. Compare returned key/BU and partner identifiers/type to the retained approved mapping fields; compare optional properties only when an expected value is available. Distinguish zero matches, multiple matches and field differences; never infer absence from an incomplete read | Fresh matching-property result, per-field compared/matched/different/not-compared status, target and UTC read time. This read verifies the observed supplier snapshot only; it does not prove customer mappings, create behavior or all unrelated setup unchanged | Stop with a precise no-match, ambiguous, difference, incomplete-read, schema or authorization outcome. Preserve earlier import status; do not create/update anything or substitute a browser/another endpoint |

## Lookup Operations

These read contracts use the qualified runtime routes, public field semantics
and current task-export profile below. Customer execution does not load
internal design pages or implementation archives. All selected reads remain
subject to current metadata, privileges, identity and pagination checks.

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_cmksc_partner_id_type | Identifier-type qualification, or partner-property preparation when a type is supplied; skip without GET for normal operations with no type; ensure_partner_setup always reads the complete eligible-code evidence before property reconciliation, even when the input type is unspecified | Configured same-target host, ORA_CMK_EXT_PTNR_ID_TYPE, supplied code if present and operation date; the qualified field contract and Partner Properties Public Sources establish standard lookup authority | For reference_profile native_customer_account_fsm, use the public genericLookups type/child contract below for the explicitly requested identifier type; the same code/effectivity checks apply. All other profiles retain the following contract. Through core.fusion-api.rest-api-client: GET /fscmRestApi/resources/11.13.18.05/standardLookups with q=LookupType='ORA_CMK_EXT_PTNR_ID_TYPE', limit=25, offset=0. Require one exact type and follow its same-target lookupCodes child link from @context.links for Framework Version 9 or links for the documented representation; reject conflicting duplicate links; retrieve all pages with fields=LookupCode,Meaning,EnabledFlag,StartDateActive,EndDateActive, onlyData=true, limit=25 and offset=0 | Parent LookupType and @context.links or links; child LookupCode,Meaning,EnabledFlag,StartDateActive,EndDateActive and pagination | Exactly one parent type; no duplicate code identities or malformed dates. Membership uses exact LookupCode. A supplied readable identifier type resolves to exactly one enabled effective case-insensitive exact Meaning when it is not an exact code; preserve the label separately from the returned code. For ensure_partner_setup retain the full same-target code set for later effective-identifier design validation, even when no type is supplied; never invent a code. A supplied code must be enabled and effective on the operation date; null dates are unbounded and an end date on/before that date is inactive. Qualification without a supplied code reports choices and eligibility metadata, not a default | Qualified code when supplied, returned choices and current membership/eligibility evidence. Provider-dependent identifier requirements remain in ora_design_enforcement.md For ensure_partner_setup a complete code read with no supplied type returns verified with the full code/eligibility evidence, not a default code; later reconciliation validates any retained effective code against that evidence. | Stop on absent/ambiguous type, incomplete pages, missing child link, invalid/disabled/inactive code, auth/authz or malformed data; preserve omission without inventing a code |
| check_cmksc_partner_property_duplicate | Before preparing a new partner property and again before final import preview; skip for source export, unchanged-package import and read-only qualification; ensure_partner_setup uses this read for reconciliation before any create | Exact target, selected partner/account or supplier/site, provider, intended identifiers and source profile; known model key and importer key are distinct | For reference_profile native_customer_account_fsm explicit create, consume the invoking shared workflow fresh completed same-target full configuration-task export, validate the exact native fifteen-column schema, and perform the complete native collision rules below. This profile neither calls a private customer-property collection nor supports update/reconciliation. All other profiles retain the following contract. Supplier: through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bSupplierPartnerProperties. Customer: GET the source-confirmed same-target b2bCustomerPartnerProperties collection in the supplied runtime route family; the qualified field contract identifies its resource and GET rowfinders. Read each applicable collection completely with onlyData=true, limit=25 and offset=0. Supplier reads must also pass orderBy=PartnerPropertyId:asc on every page under Supplier Property Ordered Pagination; customer scope retains its existing source-confirmed request. Do not use an account-only finder for cross-customer absence | Supplier: PartnerPropertyId,SupplierId,SupplierSiteId,ProcurementBUId,ServiceProviderId,PartnerTypeCode,PartnerId,PartnerIdTypeCode,ApplicationPartnerCode,DvmGroup. Customer: PartnerPropertyId,CustomerId,CustomerAccountId,OrderProcessingBUId,ServiceProviderId,PartnerTypeCode,PartnerId,PartnerIdTypeCode,DvmGroup. Require every requested attribute even when its value is null | Require valid pagination to hasMore=false and unique PartnerPropertyId values. Normalize IDs to exact decimal identity and null only to null; never equate null with zero. Conservatively block create for any existing same partner, nullable account/site, provider and type; separately check the qualified field contract importer alternate-key tuple PartnerId,PartnerIdTypeCode,PartnerKey1,PartnerKey2,PartnerKey3,PartnerTypeCode. Customer additionally blocks the same provider/PartnerId/PartnerIdTypeCode on a different CustomerId when the pair is present, under the declared collision policy. These checks protect create intent without claiming the older entity key equals the importer key For ensure_partner_setup apply Partner Reconciliation Comparison below to this complete snapshot instead of declaring a unique existing match a create collision. Explicit create retains the original collision rule. | No-collision or existing-match result, key profile, UTC time and a private complete before-snapshot for the applicable collection; bind evidence to exact intended row and target Reconciliation additionally retains absent/unique/conflicting-scope classification, requested-state comparisons and effective optional values, bound to the new request fingerprint. | Only complete zero-collision evidence permits create preparation. Existing or ambiguous matches block create and require an explicit update decision; absent route, missing fields, incomplete enumeration, auth/authz and schema mismatch stop without mutation For ensure_partner_setup return reconciled for complete absence or one exact-scope property with field comparisons; multiple scope matches or alternative-key conflicts block. No existing property is edited by this read. |
| verify_cmksc_partner_property_state | After a completed partner-property import, before claiming the requested property exists | Exact target and task, immutable approved package/row intent, completed Core Data Loader result, original selections and the complete before-snapshot from check_cmksc_partner_property_duplicate | For reference_profile native_customer_account_fsm after its successful import, consume completed fresh full before/after exact-task exports supplied by the invoking shared workflow and apply Native Customer Account Export Verification below. It initiates no export or network call and does not use a synthesized customer-property resource. All other profiles retain the following contract. Use the same source-confirmed supplier or customer collection and complete pagination contract as check_cmksc_partner_property_duplicate through core.fusion-api.rest-api-client; use its declared requested projection. Re-read the same target collection; never generate an opaque item key | All requested identity/property fields plus complete pagination; compare the current snapshot to the private before-snapshot | Require exactly one row at intended partner, nullable account/site, provider and type. Compare all intended keys, PartnerId,PartnerIdTypeCode,DvmGroup and supplier ApplicationPartnerCode; customer BU compares to OrderProcessingBUId and supplier BU to ProcurementBUId. Explicit create omissions must remain null/empty as declared in input validation; missing attributes are not null. Compare all other partner-property rows by returned identity and projected values to the before-snapshot. For create, intended row identity must be absent before and present after. Report separate matched/different/not-compared coverage; other BOs are covered only by immutable-package delta and per-BO import results, never a claim that the entire environment is unchanged | Verified requested property, create-versus-existing outcome, compared-field coverage, unchanged-compared-property result and sanitized evidence. Retain raw rows only in private runtime storage | Missing/multiple intended rows, field differences, unexpected changes, incomplete reads, missing before/approval evidence or schema mismatch return verification blocked/failed. A successful job alone is insufficient; never retry an import automatically |

## Supplier Property Ordered Pagination

Source Partner Properties Public Sources: Oracle Get all B2B supplier partners, 26C,
https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bsupplierpartnerproperties-get.html,
used as older-release field-reference evidence because the 26D page was
unavailable during qualification. The endpoint documentation supports orderBy and identifies
PartnerPropertyId as the supplier-property primary key. Installed behavior
must still be validated. The ordering and checkpoint rules below are FSCR
read-integrity policy, not permission to repair Fusion records.

| Situation | What Happens |
|---|---|
| Beginning a supplier-property collection read | check_cmksc_partner_property_duplicate requests orderBy=PartnerPropertyId:asc with its existing projection, scope and limit. Its post-import verifier uses the identical ordered contract. Do not change the endpoint, drop requested attributes or infer uniqueness from labels. |
| Validating each ordered page | Require integer-compatible nonnull PartnerPropertyId values, exact count/offset/limit and boolean hasMore. IDs must be strictly increasing within a page and greater than the previous page's last ID; compare arbitrary-precision decimal integers, not lexical strings or floating-point values. Require every projected field even when null. Advance offset by raw count; no-progress and duplicate identities remain failures. |
| An earlier unordered read repeated IDs across pages | Retain that read as incomplete integrity evidence. Begin the declared ordered read at offset 0 with a new fingerprint containing target, collection, projection, filter, orderBy and scope. Never combine unordered pages or their offsets with the ordered snapshot, and never deduplicate them to claim completeness. |
| Resuming an ordered read | Require the identical target, route, query/order, projection and request fingerprint. If snapshot continuity cannot be established or the checkpoint is stale, restart only this read at offset 0. This is not permission to resubmit an import or restart an otherwise verified connection. |
| Ordered pages still repeat IDs, go backwards or disagree on fields | Stop as a Fusion API/read-integrity failure. Preserve sanitized counts and private page evidence. Report possible collection instability or concurrent change without claiming the cause is proved. Do not coalesce duplicates, discard conflicting rows, increase the page size as a uniqueness shortcut, switch API/browser routes or delete supplier records. |
| Ordered enumeration reaches hasMore=false | Only a valid complete unique ordered snapshot may enter the existing collision/reconciliation comparisons. Ordering does not lock the collection or prove absence during concurrent writes; any detected continuity failure blocks the snapshot. Re-read freshness-sensitive evidence before final approval as already required. |

## Partner Reconciliation Comparison

| Situation | What Happens |
|---|---|
| ensure_partner_setup reads current properties | Use check_cmksc_partner_property_duplicate and its existing complete same-target collection contract. Select exact partner, nullable site/account, provider and type, retaining supplier BU or customer account scope as requested. Require zero or one exact-scope row and preserve all alternate-key and cross-customer conflict evidence. A same supplier/site/provider/type row with a different Procurement BU is an existing-scope difference, not evidence to append another row; compare that derived BU explicitly. Multiple scope rows or conflicting alternative keys block; a first page never proves absence. |
| Compare supplied properties | Compare set PartnerId, qualified PartnerIdTypeCode, DvmGroup, supplier ApplicationPartnerCode and customer BU through their declared mappings and exact resolved identities. Validate supplier BU against its selected site's derived identity. Record differences without changing intended scope or selecting another row to make it match. |
| Compare unspecified properties | For one unique row, require every projected attribute and retain its current optional value as preserved. With no row, keep the value absent for later create validation. A missing attribute is not a blank. Do not require unspecified fields to equal null and do not use values from another supplier, account, provider or target. |
| Compare clear directives | Record an explicit field-specific clear as already-empty or change-required, keeping that intent separate from absent customer input. Clear is not a route or update approval. For existing rows retain the proposed effective empty value for provider-design checks; do not mutate it. |
| Effective identifier | Pass the set resolved code, preserved current code or explicit empty effective state to CMKSC.RECONCILE_SETUP. Consume the complete same-target eligibility evidence already read by CMKSC.VERIFY_IDENTIFIER_TYPE; reject a missing, stale, disabled or inactive effective code without inventing a code or adding a hidden GET. Keep the actual and requested pair distinct. |
| Return coverage | Return per-field matched/different/preserved/already-empty/change-required coverage and absent/unique/conflict identity evidence. Bind results to target, time, source profile and new request fingerprint. Keep raw fields and IDs private; do not claim a historical import, a new insertion or whole-environment preservation from this comparison. |


## Source and Runtime Boundaries

The existing customer-resource adapter is not established as a public API by this workflow. Use the supplied
same-target runtime collection; a missing public catalog page does not make
it unsupported. The source customerProcessingFinder includes customer-wide
blank-account rows as well as account matches, so it cannot prove exact
account uniqueness. Full customer enumeration is intentional for the
cross-customer identifier check.

Entity identity and FSM matching are separate contracts. Use the qualified
alternate key and a wider database unique key. Retain their source/version
scope; neither is a universal replacement for the other. The conservative
collision check stops before an existing row can be silently overwritten.
FSM owns actual insert/update matching.

Release/model eligibility is a design gate consuming the existing live
feature/provider results and the declared source profile. There is no
separate source-backed Fusion eligibility endpoint in these materials.
Do not manufacture a lookup to answer a cross-task document-support question.
The invoking workflow owns document/connection scope and current release
applicability; this task owns partner-property validation and import gates.

## Partner Lookup Sources and Boundary

The lookup tables above are the complete FSCR read contracts. Qualify their
current response types, required projections, same-target links and complete
scope before accepting a selection. The public supplier/provider/lookup
references are listed under Partner Properties Public Sources in
ora_input_validation.md; Supplier CSV Mapping and Partner Key and Field
Contract own task-file correspondence. Customer OrderProcessingBUId is
separate from supplier ProcurementBUId. No private capture or internal
document is required from the customer to interpret these rules.

Use the supplied environment-specific /fscmRestApi/rest/rv:<opaque>/en/<version>/
route family through core.fusion-api.rest-api-client with configured OAuth and
REST-Framework-Version 9. Resolve the current route from private supplied
captures or validated same-target links; validate HTTPS host against the
selected environment and each collection against the contracts above. Never
copy captured cookies, bearer tokens, opaque route identifiers or selected
customer/supplier IDs into reusable resources. Do not invent a /resources
replacement or probe other endpoints when the route is stale. A missing route
is a lookup-input gap, not permission to bypass the workflow. Pass each finder
as a structured query value and URL-encode once. Bind parent values only from
the selected verified row, never raw customer text; validate numeric parent
identity before constructing the captured numeric finder/path shape.

## Supplier Exact Selection and Resume

| Situation | What Happens |
|---|---|
| A supplier number is supplied | Prefer the exact-number query in resolve_cmksc_supplier, even when a prior Browse checkpoint is incomplete. Keep leading zeros and case in the number string; do not coerce it to a numeric ID. If a name is also supplied, compare it case-insensitively and exactly to the returned name; disagreement is conflicting input, never permission to ignore one reference. |
| Only a complete exact supplier name is supplied | Use the exact-name query. Compare the returned name case-insensitively and exactly after response validation. A complete zero-match result asks for a supplier number or Browse; do not claim no supplier exists under every possible case variant. Several distinct matching suppliers require a choice using names and numbers. |
| A partial name or Browse is requested | Preserve existing complete-list Browse behavior. Do not invent LIKE syntax, fuzzy selection or a first-match shortcut. A complete filtered exact result does not represent all suppliers or establish absence of other partner properties. |
| Constructing an exact string query | Treat the supplied value as data. Double each apostrophe inside the single-quoted literal, reject control characters, and pass the complete q parameter as one structured Core-client argument for URL encoding once. Do not concatenate customer values into a shell command or accept customer-provided query operators as syntax. |
| A filtered response contains a different number or exact name | Return blocked for incompatible filter behavior or source/schema mismatch. Do not discard unexpected rows to make the result appear unique or silently broaden the request. |
| Switching from Browse to an exact selection | Start a new query-bound checkpoint at offset 0; preserve the old incomplete checkpoint separately. Never merge pages from different targets, query values, projections or route versions. Existing pages may inform display only; refresh the selected supplier through the exact query. |
| Resuming the same lookup | Require the same host, route/version, exact query, projection and request fingerprint. Advance offset by raw count and require hasMore=false for that scope. On timeout, preserve next offset and incomplete status; resume only that request or begin the declared exact-selection path. No supplier setup mutation or connection reimport is part of lookup recovery. |

Partner Properties Public Sources: Oracle Fusion Cloud Procurement 26D Get all suppliers,
https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-supplierslov-get.html,
explicitly lists SupplierNumber and SupplierName as
queryable attributes on suppliersLOV. Query precedence, reference agreement,
checkpoint isolation and failure behavior above are FSCR safety policy for the
declared bounded supplier resolution; documentation is not evidence
that this query has already run successfully on a selected target.

## Partner Lookup Execution

Each CMKSC.PARTNER_* node executes only its matching resolver named in its
Applies When cell. The six nodes run in order, using not_applicable for the
other partner kind. Before the first GET, ask "Who do you want to configure
messaging for: a supplier or a customer?" only if that choice is absent or
conflicting. A connection direction alone does not establish partner kind.
Unchanged ZIP export/import and other BOs skip all six without GET or questions.
No partner lookup creates a supplier, customer, account, site, BU or provider.

For each applicable lookup, preserve finder, fields and parent scope across
all pages; advance offset by returned count until hasMore=false. Validate
items, identities, labels, count/offset and pagination types. For suppliersLOV,
coalesce repeated SupplierId values only when SupplierName and SupplierNumber
are identical; retain one choice per SupplierId and validate selection against
that distinct list. Conflicting names or numbers for the same SupplierId still
block selection. Advance offset by the raw returned count, not the number of
distinct suppliers; a page containing only repeated rows is not a no-progress
failure when its raw count is positive and its offset advances. Record repeat
counts in sanitized diagnostics, without publishing duplicate choices. This
supplier-only read rule does not establish uniqueness of partner-property
records or authorize a write. Other lookup collections still reject duplicate
identities. Reject no-progress pagination, missing hasMore and malformed responses. A
limit of 25 or totalResults does not establish completeness. Do not validate
absence or unique names from the first page alone. If a bounded read cannot
finish, preserve its incomplete status and do not present a complete list.

Ask for a name/number or offer Browse choices. Use literal case-insensitive
substring filtering of display fields within the complete current response;
server-side search is permitted only by Supplier Exact Selection and Resume for suppliers; other collections retain their supplied requests. Show at most ten
choices with name/number and relevant parent context, total matches, Show more
and Refine options. Sort by display label then stable identity. A partial match
requires explicit selection even if only one candidate remains; an exact
unique supplied value may resolve without another question. Keep display
paging separate from REST paging. Never publish internal IDs as customer input
requirements or dump raw responses. Do not send invented search/finder syntax.

Retain valid user selections on resume. Changing customer invalidates account
results and option references; changing supplier invalidates site and derived
BU. Changing provider invalidates provider-derived property evidence. Changing
environment invalidates all references. Revalidate retained text within the
new scope and never silently substitute a first match. Refresh time-sensitive
evidence before final import; retain raw response data only in approved private
runtime storage and sanitize durable diagnostics.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A simplified configuration export or import is requested | Invoke resolve_simplified_feature_state automatically for the exact operation host through the central Core REST client. This read-only check needs no user confirmation. Continue only after EnabledFlag: Y; never ask the user whether the feature is enabled. |
| A documented UI procedure is available without an API contract | Preserve it as guidance; do not substitute browser automation or another endpoint |
| A Redwood configuration-page profile is enabled | Do not use it as a substitute for the Simplify opt-in; classic Redwood and simplified models are distinct |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.PARTNER_CUSTOMER | decision | 2 | reference_lookup | verified->CMKSC.PARTNER_ACCOUNT;not_applicable->CMKSC.PARTNER_ACCOUNT;selection_required->CMKSC.CUSTOMER_REQUIRED;blocked->CMKSC.RETURN_ISSUES | CMKSC.ROUTING_REFERENCE | stop | For assisted_configuration_setup and assisted_configuration_verify return not_applicable without GET or lookup questions. Otherwise: Partner-property intake: execute only resolve_cmksc_customer; missing kind asks supplier or customer before GET |
| CMKSC.PARTNER_ACCOUNT | decision | 3 | reference_lookup | verified->CMKSC.PARTNER_SUPPLIER;not_applicable->CMKSC.PARTNER_SUPPLIER;selection_required->CMKSC.ACCOUNT_REQUIRED;blocked->CMKSC.RETURN_ISSUES | CMKSC.PARTNER_CUSTOMER | stop | For assisted_configuration_setup and assisted_configuration_verify return not_applicable without GET or lookup questions. Otherwise: Execute only resolve_cmksc_customer_account; ask customer-wide or specific account when scope missing |
| CMKSC.PARTNER_SUPPLIER | decision | 4 | reference_lookup | verified->CMKSC.PARTNER_SITE;not_applicable->CMKSC.PARTNER_SITE;selection_required->CMKSC.SUPPLIER_REQUIRED;blocked->CMKSC.RETURN_ISSUES | CMKSC.PARTNER_ACCOUNT | stop | For assisted_configuration_setup and assisted_configuration_verify return not_applicable without GET or lookup questions. Otherwise: Execute only resolve_cmksc_supplier for supplier properties; prefer its exact supplied-number or exact-name scope and require completeness only in that scope |
| CMKSC.PARTNER_SITE | decision | 5 | reference_lookup | verified->CMKSC.PARTNER_PROVIDER;not_applicable->CMKSC.PARTNER_PROVIDER;selection_required->CMKSC.SITE_REQUIRED;blocked->CMKSC.RETURN_ISSUES | CMKSC.PARTNER_SUPPLIER | stop | For assisted_configuration_setup and assisted_configuration_verify return not_applicable without GET or lookup questions. Otherwise: Execute only resolve_cmksc_supplier_site after selected supplier |
| CMKSC.PARTNER_PROVIDER | decision | 6 | reference_lookup | verified->CMKSC.PARTNER_CUSTOMER_BU;not_applicable->CMKSC.PARTNER_CUSTOMER_BU;selection_required->CMKSC.PROVIDER_REQUIRED;blocked->CMKSC.RETURN_ISSUES | CMKSC.PARTNER_SITE | stop | For assisted_configuration_setup and assisted_configuration_verify return not_applicable without GET or lookup questions. Otherwise: Execute only resolve_cmksc_provider; reuse and revalidate retained provider |
| CMKSC.PARTNER_CUSTOMER_BU | decision | 7 | reference_lookup | verified->CMKSC.VALIDATE_INPUT;not_applicable->CMKSC.VALIDATE_INPUT;selection_required->CMKSC.CUSTOMER_BU_REQUIRED;blocked->CMKSC.RETURN_ISSUES | CMKSC.PARTNER_PROVIDER | stop | For assisted_configuration_setup and assisted_configuration_verify return not_applicable without GET or lookup questions. Otherwise: Execute only resolve_cmksc_customer_business_unit; supplier skips without GET |
| CMKSC.RESOLVE_FEATURE_STATE | decision | 20 | reference_lookup | enabled->CMKSC.VERIFY_IDENTIFIER_TYPE;blocked->CMKSC.RETURN_ISSUES | CMKSC.VALIDATE_INPUT | stop | Execute only resolve_simplified_feature_state to check the Simplify feature on the selected operation host |
| CMKSC.VERIFY_IDENTIFIER_TYPE | decision | 21 | reference_lookup |verified->CMKSC.CHECK_PROPERTY_COLLISION;not_applicable->CMKSC.CHECK_PROPERTY_COLLISION;qualification_verified->CMKSC.QUALIFY_SUPPLIER_STATE;verification_ready->CMKSC.VERIFY_PROPERTY_STATE;blocked->CMKSC.RETURN_ISSUES;routing_verification_ready->CMKSC.VERIFY_ROUTING_STATE | CMKSC.RESOLVE_FEATURE_STATE | stop | For qualify_existing_document_routing after its input and feature checks, return routing_verification_ready without identifier-type lookup. Otherwise Execute only verify_cmksc_partner_id_type. For operation qualify_existing_supplier_property, inspect codes and validate any retained supplied code, then use qualification_verified. For post_import_verify, return verification_ready after any applicable code check; other operations use verified or not_applicable according to applicability |
| CMKSC.QUALIFY_SUPPLIER_STATE | decision | 22 | reference_lookup | verified->CMKSC.QUALIFICATION_DONE;blocked->CMKSC.RETURN_ISSUES | CMKSC.VERIFY_IDENTIFIER_TYPE | stop | Only operation qualify_existing_supplier_property: execute qualify_cmksc_supplier_property_state after all qualification preflight checks. Differences, missing/ambiguous records and incomplete reads are blocked outcomes |
| CMKSC.VERIFY_PROPERTY_STATE | decision | 23 | reference_lookup | verified->CMKSC.VERIFICATION_DONE;blocked->CMKSC.RETURN_ISSUES | CMKSC.VERIFY_IDENTIFIER_TYPE | stop | Only post_import_verify: execute verify_cmksc_partner_property_state after completed import and approved-intent/before-snapshot checks |
| CMKSC.CHECK_PROPERTY_COLLISION | decision | 25 | reference_lookup | clear->CMKSC.VERIFY_PARTNER_DEPENDENCIES;not_applicable->CMKSC.VERIFY_PARTNER_DEPENDENCIES;blocked->CMKSC.RETURN_ISSUES;reconciled->CMKSC.RECONCILE_SETUP | CMKSC.VERIFY_IDENTIFIER_TYPE | stop | Execute check_cmksc_partner_property_duplicate for create preparation/final validation or ensure_partner_setup reconciliation. Source export and unchanged-package operations skip without GET; explicit create retains strict collision blocking |


## Public Provider Reference Source

[Oracle service-provider fields](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bserviceproviders-get.html)
document the stored UserDefined Y/N value. The owning provider resolver reads
it directly and checks its identity against the selected supplier/customer
context; a customer needs no internal reference page or provider flag input.


## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_cmksc_runbook_rest_preflight | Only runbook_rest_operation before Run Book payload review and dispatch | Exact selected project/Run Book/task, environment, declared public operation ID, typed business intent and existing reference selections | Through core.fusion-api.rest-api-client first GET the selected declared resource describe. For supplier-property operations retain the owned supplier/site/BU/provider and property reads, current feature evidence and complete same-scope collision check. For create_account_with_ship_to GET /fscmRestApi/resources/11.13.18.05/b2bAccountNumbers with fields=AccountNumber,AccountNumberId,SupplierNumber,SiteName,ProcurementBU;onlyData=false;limit=25;offset=0 and every page; confirm current POST supports the requested nested shipToAssignments fields. Resolve supplier/site/BU and ship-to codes through current supported owning reference evidence before payload readiness. For create_location_code GET /fscmRestApi/resources/11.13.18.05/b2bLocationCodes with fields=B2BLocationCode,CustomerNumber,PartySiteNumber;onlyData=false;limit=25;offset=0 and every page. Resolve current customer/site parent evidence through the owned customer lookup before readiness. For location_reference_profile native_customer_party explicitly selected at intake, execute qualify_cmksc_native_customer_party_site using the separately declared Public Native-Customer Party Reference Profile below rather than requiring an opaque customer-LOV route. This profile is limited to an existing customer already represented in a fresh completed same-target full configuration-task export supplied by the invoking shared workflow; it does not resolve an unrepresented customer or change the partner-property intake route. Preserve returned same-host self/child links privately. Require exact requested identity/code absence and no case-only or duplicate ambiguity. Stop on missing schema/reference/privilege evidence; no write, finder invention or alternative route. For create_account_with_ship_to invoke the owned resolve_cmksc_supplier and resolve_cmksc_supplier_site contracts for the exact current business references, without provider selection. For CMK ship-to eligibility use the documented B2B-specific resource, not an HCM location browse: GET /fscmRestApi/resources/11.13.18.05/b2bShipToLocationsLOV/describe through the same Core client, require readable LocationId,LocationCode,LocationName,SetName and queryable LocationCode, then GET that collection with fields=LocationId,LocationCode,LocationName,SetName;onlyData=true;limit=25;offset=0 for a bounded choice page. A supplied or delegated selected business code requires q=LocationCode='<escaped exact code>' with the same projection and complete paging to establish one exact identity and set scope. Missing or duplicate code matches cannot pass. For delegated non-production tests, record the business-code selection policy and chosen existing scope privately, then run that exact validation; a choice page does not prove uniqueness or absence. Do not map SetName to the account POST Set code, allocate a location ID or create a location. Unavailable HCM records do not prove the CMK B2B location list is empty; HCM validation is separate only when explicitly requested. Missing schema, privileges or intended reference coverage blocks before payload readiness. For update_processing_parameters GET /fscmRestApi/resources/11.13.18.05/b2bMessageParameters/describe and its complete collection with onlyData=false,limit=25,offset=0 and every page; select exactly one intended current parameter identity from the complete result and validate its actual same-host self link. GET that link before readiness to establish readable before-state and PATCH metadata. Require every requested field in the published PATCH schema and current writable attributes, with field-specific meaning/unit/range evidence from the owning validation rules. For update_delivery_type_limit GET /fscmRestApi/resources/11.13.18.05/b2bDeliveryMethodTypes/describe and its complete collection with fields=DeliveryMethodTypeId,DeliveryMethodType,MaximumMessageSize;onlyData=false;limit=25;offset=0 and every page. Resolve one exact type identity, validate and GET its returned self link, retain the existing type code and qualify MaximumMessageSize independently. Neither collection is a create-type or a general parameter-data endpoint. Missing supported item read, field semantics, unit/conversion/range, identity, metadata or privileges blocks that requested setting before approval. For explicit supplier-level create_supplier_property with no site/BU requested, retain the unique supplier identity and verify current POST makes SupplierSiteId and ProcurementBUId optional; leave them omitted. Read the complete supplier-property scope with a safely typed current SupplierId filter and every page, distinguishing actual null site/BU from site-level records. Require no existing supplier-level record before strict create; do not reinterpret a site-level collision as supplier-level permission. For partner role and identifier type, use the existing Core genericLookups/describe then LookupTypeFinder with ViewApplicationId=0 for ORA_CMK_PARTNER_ROLE and ORA_CMK_EXT_PTNR_ID_TYPE; follow only same-host returned lookupCodes links and complete active/date-effective pages. Resolve the exact readable Supplier role and requested identifier type to one current code. These lookups are read-only; no new lookup value or role is created. | Exact operation-specific identities, current writable fields/types/nullability and required/default metadata, complete scoped record evidence and intended-field coverage | Require exact operation-specific scope and current writable fields/types/nullability. For account creation, validate account number, existing supplier/site/BU and every explicit ship-to code; derived IDs are not allocated. For location creation validate existing customer/site and the requested location-code identity; only qualified business-reference fields enter the payload. Current collection presence is not proof of create privilege. Other operations retain their supplier/provider design rules. Processing/size updates require exact private before-state and explicit requested fields; same-value reapply is classified separately from changed-value execution. No reference to a new provider, supplier or account is needed for an independent global-setting update. If an intended account number already resolves, compare its current SupplierNumber/SiteName/ProcurementBU and qualified parent identities with the requested scope before reuse or create. A conflicting supplier/site/BU is an explicit parent-scope conflict; never bind the account to a different site, allocate a replacement account or silently reinterpret strict create as update. | ready with immutable operation/context/preflight fingerprints and resolved nonsecret field bindings; blocked with precise failure class and evidence | Missing/ambiguous identity, unsupported operation/field, missing secure binding, incomplete pages, privilege/schema/read failure or active conflict blocks before payload approval. A public document is not proof of current privileges or deployed behavior; no alternative write route is a fallback |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.REST_PREFLIGHT | decision | 11 | reference_lookup | ready->CMKSC.REST_GATE;blocked->CMKSC.RETURN_ISSUES | CMKSC.VALIDATE_INPUT | stop | Only the declared runbook_rest_operation: execute verify_cmksc_runbook_rest_preflight. This node performs reads only and cannot approve or dispatch a mutation |


## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_cmksc_runbook_rest_state | Only runbook_rest_verify after the declared dispatch or for safe uncertain-result reconciliation | Exact approved operation/target, private intent and result reference, observed self/child links and before-snapshot | Through core.fusion-api.rest-api-client GET only the validated same-target self link returned by the exact approved operation; if absent, use its qualified complete collection read and exact scope/name match. For account creation compare account/supplier/site/BU and each requested ship-to assignment from returned validated child links, including membership and count. For location creation compare B2BLocationCode,CustomerNumber,PartySiteNumber and intended scope. Supplier-property operations retain the declared current property comparison. Missing intended readable coverage blocks verification; no synthesized opaque key, retry, import or browser fallback. With REST-Framework-Version 9, read actual self/child links from @context.links as well as the supported top-level links form. Account shipToAssignments may be a paginated object containing items rather than a bare array. Read its complete items and current returned child link; never interpret the envelope as zero assignments or synthesize an opaque path from an unrelated key. Validate same HTTPS origin/port and exact account-resource family before every linked GET. For update_processing_parameters and update_delivery_type_limit, reopen only the exact qualified current self link and compare every requested set/clear with approved intent plus every unrequested readable configuration field against the before-snapshot. Exclude only server-maintained audit timestamps and links from the unchanged-field comparison. Preserve the existing parameter/type identity and full private change record; a same-value result verifies reapply only, not a changed business limit. No other field or backing parameter-data row is implicitly approved. | Every intended readable field, explicit nullable values, identity and qualified file comparison; safe result/coverage evidence | Require exactly one identity in the approved scope and compare every supplied set/clear against approved intent. Match file bytes using source-confirmed decoding; do not omit a requested comparison after read failure. Write-only credential values are never fetched or displayed: report accepted secure-binding coverage separately from connectivity. A read alone after an uncertain dispatch proves requested state only, not which write created it Require every requested ship-to code to be present exactly once under the returned AccountNumberId, with complete membership/count coverage. Where current parent and location identities were qualified before the write, confirm derived VendorId,VendorSiteId and ShipToLocationId against those private identities. Keep returned Set separate from a display SetName; do not invent a conversion. Generated int64 identities may be JSON integers in one qualified response and decimal strings in another, including POST versus GET. Validate a positive ASCII decimal identity within the current type range and compare its exact numeric identity without floating-point conversion; reject booleans, fractions, scientific notation and malformed text. This identity normalization never applies to business account/supplier numbers or location codes, whose leading zeros and text are preserved. | verified requested-state coverage, actual action result, target/time and artifact binding; no new mutation or blanket no-changes claim | Absent/ambiguous/different state, missing intended fields, incompatible links or failed/incomplete reads blocks verification without replay. Preserve accepted/partial/uncertain mutation separately; verified configuration does not prove business-document receipt |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.REST_VERIFY | decision | 13 | reference_lookup | verified->CMKSC.REST_VERIFIED;blocked->CMKSC.RETURN_ISSUES | CMKSC.VALIDATE_INPUT | stop | Only runbook_rest_verify: execute verify_cmksc_runbook_rest_state for the exact approved operation. No preparation, approval or dispatch |

## Lookup Operations

Product prerequisite: [26D messaging setup](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faclm/how-do-i-set-up-collaboration-messaging.pdf).
The reference authority is a current completed Fusion task-data export, not a
customer-authored numeric key or a stored dropdown list.

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_cmksc_routing_connection_reference | configure_document_messaging with an explicit requested connection; other operations return not_applicable without GET or artifact inspection | Configured target, current routing request/name/direction, and completed private full provider-task export supplied by the invoking shared export workflow | Consume only that declared completed shared.setup-export.task-level-export result for ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER; this resolver initiates no export or network request. Validate safe ZIP/unique members, metadata task/source/completion, no restrictive criteria and exact complete inbound/outbound connection headers/types before reading rows | PartnerMessageName,ServiceProviderName,SPUserDefined,MessageName,TransformMode and complete direction-specific row membership, plus export provenance/time | Match the exact requested connection name across complete applicable direction scope; zero across both full connection members establishes absence. One exact provider/name/flag/direction tuple is required when scoped. Case-only or multiple matches require selection and block preview. Do not decode or manufacture ORA_CMK_DECISION_DETAIL.Data, broaden provider scope or infer a missing connection from an API failure | verified with exact private reference tuple, missing with zero matches and precise connection prerequisite, not_applicable or blocked with provenance/schema/coverage diagnostic | Missing returns the connection-setup prerequisite before operator context or mutation. Unknown/stale/wrong-target/incomplete export blocks with the invoking workflow source-export next action; never assume absence, call an undocumented endpoint, fabricate a routing ID or mark routing saved |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.ROUTING_REFERENCE | decision | 1 | reference_lookup | task_composition->CMKSC.COMPOSITION_INPUT;task_composition_verification->CMKSC.COMPOSITION_VERIFY;native_combined_create->CMKSC.COMBINED_INPUT;native_combined_verify->CMKSC.COMBINED_VERIFY;verified->CMKSC.PARTNER_CUSTOMER;not_applicable->CMKSC.PARTNER_CUSTOMER;missing->CMKSC.RETURN_ISSUES;blocked->CMKSC.RETURN_ISSUES;native_account_create->CMKSC.FSM_ACCOUNT_INPUT;native_account_verify->CMKSC.FSM_ACCOUNT_VERIFY_INPUT;native_ship_to_create->CMKSC.FSM_SHIP_TO_INPUT;native_ship_to_verify->CMKSC.FSM_SHIP_TO_VERIFY_INPUT;native_location_create->CMKSC.FSM_LOCATION_INPUT;native_location_verify->CMKSC.FSM_LOCATION_VERIFY_INPUT;native_settings_configure->CMKSC.FSM_SETTINGS_INPUT;native_settings_verify->CMKSC.FSM_SETTINGS_VERIFY_INPUT;native_routing_create->CMKSC.FSM_ROUTING_INPUT;native_routing_verify->CMKSC.FSM_ROUTING_VERIFY_INPUT | none | stop | For qualify_configuration_task_composition_fsm return task_composition without GET; for verify_configuration_task_composition_fsm return task_composition_verification with original immutable intent and actual terminal job. Configuration Task Composition owns those independently bounded operations without broadening the old account/ship-to branch. After the FSM-only route check, create_account_ship_to_combined_fsm returns native_combined_create and verify_account_ship_to_combined_fsm returns native_combined_verify without GET; the bounded Combined Account and Physical Ship-To profile owns these operations. Otherwise create_account_number_fsm returns native_account_create and verify_account_number_fsm returns native_account_verify without a lookup; these operations use only their dedicated native account branch below. Likewise create_ship_to_assignment_fsm returns native_ship_to_create and verify_ship_to_assignment_fsm returns native_ship_to_verify without a lookup. create_location_code_fsm returns native_location_create and verify_location_code_fsm returns native_location_verify without a lookup. configure_initial_settings_fsm returns native_settings_configure and verify_initial_settings_fsm returns native_settings_verify without a lookup. create_document_routing_fsm returns native_routing_create and verify_document_routing_fsm returns native_routing_verify without a lookup. All other operations retain the following behavior. First apply FSM-Only Route Enforcement: runbook_rest_operation and assisted UI setup/execute return blocked locally without any external call. Otherwise only configure_document_messaging with an explicit connection invokes verify_cmksc_routing_connection_reference on the qualified current complete export supplied by its invoking workflow. Missing connection stops before operator context or routing preview. For assisted_configuration_setup outside that exact document/connection scope, assisted_configuration_verify and every other task operation return not_applicable without GET or artifact inspection. |

## Public Native-Customer Party Reference Profile

Sources: [public CMK partner-key definition, 25D](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25d/oedsc/cmkpartnerproperties-8177.html),
[public organization GET](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-huborganizations-get.html),
[public ship-to party-site GET](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-shiptopartysites-get.html),
and the [published CMK location-code POST](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2blocationcodes-post.html).
The older dictionary explicitly identifies customer PARTNER_KEY1 as a foreign
key to HZ_PARTIES. It is relationship background, not proof of current release
compatibility. Require the current export and both current public joins below;
do not infer current IDs, customer numbers or eligibility from that source alone.

The invoking Run Book selects the existing shared populated exact-task export
step before this intake profile. This resolver consumes its private result and
does not submit another task. Verify host, exact task, completion, full scope,
safe ZIP, exact headers and types. Only rows with an explicitly represented
customer role and nonblank CustomerNumber are candidates. Coalesce identical
CustomerNumber/PartnerKey1 pairs; conflicting identities block. Resolve the
Customer role through the current public genericLookups contract: GET
/fscmRestApi/resources/11.13.18.05/genericLookups with
Finder LookupTypeFinder, LookupType=ORA_CMK_PARTNER_ROLE and
ViewApplicationId=0; follow its validated lookupCodes child link through all
pages and require one enabled/effective exact Meaning Customer. Preserve the
returned LookupCode; do not infer it from a display label or another role.
The customer supplies business identity or delegates non-production fixture
selection; the exporter supplies technical candidates, never invented keys.

The existing verify_cmksc_runbook_rest_preflight node owns these profile reads
for its operation. The native create_location_code_fsm branch selects the same
read-only parent profile through qualify_cmksc_fsm_location_create; neither
selection permits a setup REST write.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_native_customer_party_site | Only create_location_code or create_location_code_fsm with native_customer_party selected before preparation | Fresh completed full exact-task export, represented customer role/number/key, selected target and delegated or explicit customer/site choice | Through core.fusion-api.rest-api-client GET /crmRestApi/resources/11.13.18.05/hubOrganizations/describe, then that collection with q=PartyId=<typed positive PartnerKey1>;fields=PartyId,PartyNumber,Status;onlyData=false;limit=25;offset=0 and every page. After one exact current organization, GET /crmRestApi/resources/11.13.18.05/shipToPartySites/describe and that collection with q=PartyId=<verified current PartyId>;fields=PartyId,PartySiteId,PartySiteNumber,Status,StartDate,EndDate;onlyData=false;limit=25;offset=0 and every page | Current organization identity/number/status; current party-site identity/number/parent/status/effective dates; metadata and pagination | Require current compatible readable/queryable attributes, one organization with exact decimal PartyId equal to the native customer key and exact PartyNumber equal to native CustomerNumber, plus active status. Require each returned site belongs to that verified party, positive unique PartySiteId, nonblank exact PartySiteNumber and current active/effective status. Resolve an explicit requested site by exact PartySiteNumber within that complete same-party result, or retain the delegated selected business site number and require exactly one current row in that same complete parent scope. The parent-scoped collection establishes the exact local match; do not add an unnecessary combined PartyId/PartySiteNumber query or treat an extra failed filter as missing master data. Retain any failed optional request separately and re-establish the declared complete parent-scoped read before accepting its current exact match. Never equate CustomerAccountId, a planning-customer key or an address label with PartyId or PartySiteNumber. This profile establishes ship-to scope only | Exact current CustomerNumber and PartySiteNumber with separate party/site identities and private export/read fingerprints. Preserve returned names as context only. The normal location-code metadata/collision and immutable-payload checks still apply | Missing, conflicting, inactive, ambiguous, unauthorized, unsupported or incomplete joins block before payload preparation. Retain source mismatch and never reinterpret a failed join as permission to create a customer/site, use another route or fabricate a location code |

This is a current-reference qualification profile, not a new write adapter.
The legacy create_location_code operation retains its declared route boundary;
the native create_location_code_fsm branch uses the reads before FSM package
preparation and its own native-export verification. No hub organization,
address or party-site write is permitted. An existing CMK property is only
candidate relationship evidence; the current public party and site reads are
mandatory before preparation.

## Public Existing-Customer Account FSM Profile

This is an explicitly selected reference profile for the existing partner-row
FSM preparation/import route, not a replacement write adapter. Select
reference_profile native_customer_account_fsm before new customer-account
intake, with a separately completed full configuration-task export and full
provider-task export from the invoking shared export workflow. Validate each
export's exact host/task/completion/full scope, ZIP safety, headers and types.
The existing header-only configuration-task template remains the create seed.
Existing runtime profiles and unchanged-package migration remain unchanged.

Public sources: [CMK partner-key relationships, 25D dictionary](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25d/oedsc/cmkpartnerproperties-8177.html),
[current public organization reference](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-huborganizations-get.html),
[26D customer account sites reference](https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/op-customeraccountsiteslov-get.html),
[public service providers](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bserviceproviders-get.html)
and [public lookup types](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-genericlookups-get.html).
The older dictionary is relationship background; fresh target joins below are
mandatory and prevent treating older reference material as release certification.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_native_customer_account | Only native_customer_account_fsm explicit create with an existing represented customer/account; no optional customer BU set | Complete current native customer-role CustomerNumber,CustomerAccountNumber,PartnerKey1,PartnerKey2 pairs, customer business selection or delegated non-production fixture selection | Through core.fusion-api.rest-api-client GET /crmRestApi/resources/11.13.18.05/hubOrganizations/describe and exact q=PartyId=<positive native PartnerKey1>;fields=PartyId,PartyNumber,Status;onlyData=false;limit=25;offset=0 and all pages. GET /fscmRestApi/resources/11.13.18.05/customerAccountSitesLOV/describe and that collection with q=PartyNumber='<escaped exact verified PartyNumber>';fields=PartyNumber,AccountNumber,CustomerAccountId;onlyData=true;limit=100;offset=0 and all pages | Current public party identity/number/status and account identity/number/party-number relationship | Require one active organization with exact native key/number equality. Every account projection must retain that exact PartyNumber. Coalesce identical PartyNumber/AccountNumber/CustomerAccountId projections from sites; conflicting number-to-ID or ID-to-number relationships block. Select one explicit or delegated account represented in the fresh native CMK export, requiring both native AccountNumber/PartnerKey2 equality and the current public relationship. Preserve business numbers as strings. This reference does not establish invoice processing, site eligibility or an optional BU | Current customer and account business numbers plus separately qualified party/account identities; CustomerId receives the verified party identity under the existing native key contract, never the account ID | Zero current joins, conflicts, inactive party, unsupported metadata, unauthorized or incomplete reads block before editing a package. No customer/account/site is created and no other namespace is substituted |
| qualify_cmksc_native_account_provider_type | Only native_customer_account_fsm provider and identifier-type qualification | Existing selected provider and explicit identifier type; native provider export and operation date | Through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bServiceProviders/describe and its exact-name collection with fields=ServiceProviderId,ServiceProviderName,UserDefined;onlyData=true;limit=25;offset=0 and all pages. Resolve ORA_CMK_PARTNER_ROLE and ORA_CMK_EXT_PTNR_ID_TYPE through genericLookups with finder=LookupTypeFinder;LookupType=<exact type>,ViewApplicationId=0;onlyData=false; follow the validated same-target lookupCodes child link and all pages with fields=LookupCode,Meaning,EnabledFlag,StartDateActive,EndDateActive;onlyData=true;limit=100;offset=0 | Current provider name/identity/stored flag; current customer role and identifier type codes with eligibility dates | Require one exact provider and stored flag, plus exactly one native ProviderName/UserDefined/ProviderType tuple identifying an existing Service Provider. Resolve the Customer role and explicit identifier type by exact code or one exact case-insensitive meaning among enabled/effective choices. No UI boolean conversion, implicit provider creation or attachment-mode/category inference | Exact native provider name/stored flag and current eligible Customer and identifier-type codes | Missing or conflicting provider tuple, unknown role/type, disabled/inactive code, absent metadata or incomplete reads blocks this profile |

## Native Customer Account Collision and Export Verification

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Limited create scope | Require explicit customer-account create, represented customer/account with both fresh public joins, existing Service Provider, explicit eligible PartnerId/PartnerIdTypeCode, no supplied OrderProcessingBU and no supplier-only fields. Customer-wide, update, clear, supplied BU and extra provider-dependent settings retain their existing qualified profiles; never silently omit them | native_customer_account_fsm intake | |
| Complete current native collisions | Across every ORA_CMK_PARTNER_PROP row, block any same customer/account/provider/stored-flag/customer-role scope, even when its trading-partner identifier differs. Also block the exact native alternate key PartnerId,PartnerIdTypeCode,PartnerKey1,PartnerKey2,PartnerKey3,PartnerTypeCode; block the same provider/stored-flag/PartnerId/PartnerIdTypeCode on a different customer. Preserve all existing rows. Missing or partial native evidence cannot prove absence | Before preparation and final preview | check_cmksc_partner_property_duplicate |
| Existing mapping only | Use the fifteen-column Partner Key and Field Contract: verified target party/account identities in PartnerKey1/PartnerKey2, exact business numbers in CustomerNumber/CustomerAccountNumber, verified provider name/stored flag and eligible role/type codes. Keep PartnerKey3 and all supplier fields empty because this profile requires explicit BU omission and customer scope. Optional DvmGroup remains subject to its own qualified contract. No source-host ID reuse, generated property key, zero/null markup or fabricated value | One-row create preparation | |
| Native saved-state evidence | Require the immutable approved row/ZIP hash, actual successful import status and fresh completed full same-target exact-task before/after exports. Before must contain no intended scope/key; after must contain exactly one intended row. Compare all fifteen cells including explicit create blanks, not just a selected subset. Compare every other native partner row as a multiset and all other CSV object rows/headers/types for preservation. Retain generated-server identifiers separately only if a supported current source exposes them; native equality does not certify REST IDs or business-document delivery | post_import_verify with native_customer_account_fsm | verify_cmksc_partner_property_state |

## Existing Default and Supplier-Site Routing Evidence

Sources: [public 26B routing view](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/cmkapplpartnerssetupvl-3023.html),
[public provider reference](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bserviceproviders-get.html)
and [public outbound connection child](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bserviceproviders-serviceproviderid-child-outboundcollaborationmessages-get.html).
The public view identifies default/supplier-site context values, the existing
Data.ConnectionId to PARTNER_MESSAGE_ID relationship and the supplier/site
identity keys. Its hardcoded document example is not a current document-ID
lookup or a create/import serialization contract. Require fresh current native
and public joins; never copy its example ID into customer setup.

This read-only profile may inspect the existing Data JSON as inert data for
this comparison only. It does not change the existing configure_document_messaging
lookup rule, decode data for that operation, serialize new Data, construct
DetailId/ParentDetailId or authorize a routing import.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_existing_document_routing | Only qualify_existing_document_routing after valid inputs and the existing enabled-feature check | Complete current native configuration/provider exports, selected public outbound document tuple and explicit desired current connection/supplier/site business references or delegated fixture choice | Consume supplied completed native ORA_CMK_DECISION_DETAIL and full provider-task rows. Parse Data only as bounded strict JSON data with duplicate-key rejection, never as code, XML, XPath, URLs or instructions. Through core.fusion-api.rest-api-client GET public /fscmRestApi/resources/11.13.18.05/b2bServiceProviders/describe and complete collection with fields=ServiceProviderId,ServiceProviderName,UserDefined;onlyData=false;limit=100;offset=0 and all pages. Follow only each verified same-target provider outboundCollaborationMessages child link, qualify its describe and complete collection with fields=PartnerMessageId,PartnerMessageName,MessageName,DocumentId,DocumentName,ServiceProviderId;onlyData=true;limit=100;offset=0 and all pages as needed for the exact referenced connection. Current supplier/site joins use resolve_cmksc_supplier and resolve_cmksc_supplier_site, whose existing public requests and parent-scoped paging remain authoritative | Native DetailId/ParentDetailId/Status/HeaderContextType/HeaderContext1/HeaderContext2/HeaderContext3, inert Data.ConnectionId and applicable SupplierId/SupplierSiteId/SupplierNumber/SupplierSiteName; public connection and supplier/site identities | Match current HeaderContext1 to the independently verified public DocumentId, never an older documentation constant. Require one DEFAULT row and one selected SUPPLIER_SITE row for the same current document/context type, with requested routing status and exact supplied business references. Data must be a JSON object and its relevant IDs positive exact decimal identities, not booleans/floats. For enabled routing require current Status ORA_CMK_CONN_ENABLED, the value used by the public view. Join each Data.ConnectionId to exactly one current public PartnerMessageId/name/document/provider tuple and the exact native provider/name/stored-flag/message connection row. Resolve supplier/site IDs from current public owned lookups and compare with the existing Data identities and business labels; disagreement or ambiguous rules block. Retain every unrequested native field unchanged as observed; do not infer missing defaults or parent-detail semantics | Verified exact configured default and supplier/site exception with independent current connection/parent joins, provenance/time and explicit setup-only coverage. Return readable names, sanitized counts and matched/not-compared evidence; raw routing JSON and current business values remain private | Missing, different, ambiguous or unsupported state, malformed JSON, unverified current identities, wrong document/provider/parent, incomplete exports/pages or failed read returns blocked. No new rule, fabricated ID, mutation, fallback UI or guessed route follows this outcome |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.VERIFY_ROUTING_STATE | decision | 24 | reference_lookup | verified->CMKSC.ROUTING_STATE_VERIFIED;blocked->CMKSC.RETURN_ISSUES | CMKSC.VERIFY_IDENTIFIER_TYPE | stop | Only qualify_existing_document_routing executes qualify_cmksc_existing_document_routing after current input and feature checks. Read-only; no preparation, approval, import or setup mutation |

## Current Public Setup Capability Assessment

For explicitly selected read-only CMK capability assessment before preparation,
reuse the unchanged core.fusion-api.rest-api-client GET transport and the
[published Oracle metadata contract](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/Resource_Methods.html).
Bind the active project Run Book, exact configured HTTPS target, both CMK task
identities and metadata-read privileges. Through that shared client request
/fscmRestApi/resources/11.13.18.05/describe with metadataMode=minimal and
REST-Framework-Version 9, retaining the response/errors privately. Keep default public visibility for the broad catalog inventory. Only on a
500/502/503 minimal-catalog failure may this task select one
metadataMode=list read. Stop after that bounded attempt; no mutation follows.

The current task explicitly needs the existing b2bDocuments, b2bConnections,
b2bMessageDefinitions, b2bApplicationPartners and b2bServiceProviders identities.
Apply the task-owned Runtime Route Handoff and Recovery rules in the Service Providers reference guidance to exact named returned links. This reuses declarative metadata checks, not another task execution route or a Core parser. A catalog
inventory may identify a current named routing or external-format candidate as
an authoring lead, but never constructs or probes a guessed resource path.
Before any candidate's data read or write, its owning task must separately
qualify and declare its current exact resource, fields/types/finders, scope,
model compatibility, operation, validation, immutable preview/approval and
saved-state contract. Catalog presence alone is neither a working create route
nor evidence that a classic-only operation changes simplified setup. Preserve
all existing routes and failed observations; never substitute discovery for a
missing task execution step or perform UI setup as an assessment side effect.

For a separately selected exact-resource metadata assessment, the public
resources query parameter may restrict describe to the five exact required
names above. The documented include=all option may be used together with
that exact resources filter to obtain their current metadata when the broad
public catalog does not advertise even independently documented resources.
This is one bounded read, not a private-resource inventory or a write route.
Do not conclude an endpoint is absent solely because the broad list omitted
it: retain catalog coverage separately from already successful per-resource
reads. A returned unlisted binding still needs its own public product/current
metadata business contract and all existing task preflight/approval checks;
no arbitrary returned resource or undocumented write is executed.

A separately selected authoring-only name inventory may make one documented
metadataMode=list,include=all catalog GET to identify current CMK resource
names and their returned links when the exact public business-resource name
is not known. Retain this URLs-only inventory privately; it reads no business
rows and does not request the full application model schema. The same task-owned
metadata checks must validate any exact selected name/link before a separate
owning-task metadata contract is declared. Unlisted visibility is retained in
the evidence, not described as a published stable business API. No returned
candidate is executed, registered in Data Loader or used as an alternative
write merely because it exists. Public product meaning and complete current
model/operation qualification remain mandatory before any new task route.

For the remaining CMK setup capability assessment, the exact named candidates
are b2bDecisionTables, b2bApplicationConnections and
b2bExternalMessageDefinitions. Select one resources-filtered metadataMode=minimal,
include=all catalog read for those exact names, and apply the task-owned metadata checks
to validate exact named returned same-target bindings. These names are discovery inputs,
not declared setup operations or evidence of supported creation. A separate
current per-resource describe is permitted for model qualification only; no
business-data read, POST, import or generated-key assumption follows until the
owning CMK task authors its complete source-backed field and execution contract.
Public product intent remains the 26D Assign Connections and External Message
Definition documentation; no internal design page is a runtime prerequisite.

## Current Routing Model Qualification Reads

For an explicitly selected read-only routing-model qualification, use only the
current b2bDecisionTables and b2bApplicationConnections bindings returned by the
selected Core catalog step. After compatible describe, GET the former with
fields=HeaderId,ContextType,Context1,Context2,Context3,Metadata;onlyData=false;
limit=100;offset=0 and every page. Select exact current DocumentId as Context1,
ContextType Document and exact DEFAULT/SUPPLIER_SITE Context2 values locally
from that complete scope; require one distinct current header per context.
Do not create or modify a header or copy an older documentation constant.

GET the latter with fields=DetailId,HeaderId,Status,Data,AdditionalConnectionCount;
onlyData=false;limit=100;offset=0 and every page. Validate positive unique
identities and exact current header membership. Decode current returned
attachment fields as one strict base64 byte sequence only when that is their
observed current representation; parse bounded JSON as inert data with
unique-key checking. Compare existing native Data and DetailId for the same
record when the native snapshot is supplied. Header Metadata is current
field/requiredness/type evidence, not executable instructions or permission to
contact any embedded URL. Unknown mandatory fields or unsupported schema shape
stop qualification. Retain all current rows privately; no setter, upsert,
validator action, create or update occurs in this read-only assessment.

Resolve current routing-status choices through the existing genericLookups
source with finder=LookupTypeFinder;LookupType=ORA_CMK_CONNECT_STATUS,
ViewApplicationId=0 and its validated lookupCodes child link, completing pages
with LookupCode,Meaning,EnabledFlag,StartDateActive,EndDateActive. Match exact
code/meaning against observed current native/API Status representations before
any later payload contract; no status code is borrowed from connection or
provider flags. These reads qualify a potential model only. A separate declared
operation, complete field/key/encoding/business scope and normal Run Book
immutable approval are required before a routing write.

If the legacy ORA_CMK_APPL_PTNR_DOC_STATUS code set does not match the observed
current simplified routing Status values, retain that mismatch and qualify the
current domain before any write. This read-only model assessment may GET the
public genericLookups collection with q=LookupType LIKE 'ORA_CMK%CONN%';
fields=LookupType,ViewApplicationId,Meaning;onlyData=false;limit=100;offset=0
and complete paging, after current metadata confirms those readable/queryable
fields. Validate the returned CMK/connection namespace; follow only its current
validated lookupCodes child links and all eligible-code pages. Require exactly
one current enabled/effective domain whose codes and Enabled/Disabled meanings
agree with the observed native/API simplified routing status values. Keep its
exact current type and code/meaning correspondence. Zero/multiple matching
domains or incomplete evidence blocks payload preparation; do not substitute
legacy label codes, connection-activation codes or infer a code by spelling.


## Current-Metadata Routing Detail Create Profile

The existing verify_cmksc_runbook_rest_preflight owns these read-only gates
when create_document_routing was selected at intake. Resolve the current exact
outbound document through the existing document lookup. Use only the current
filtered catalog bindings and compatible detailed metadata for
b2bDecisionTables, b2bApplicationConnections and b2bConnections. Read complete
header/detail collections using Current Routing Model Qualification Reads;
resolve the exact Document/DocumentId/DEFAULT or SUPPLIER_SITE seeded header.
HeaderId is an existing reference, never an allocated header or old constant.
Require current POST and server-generated DetailId metadata.

GET the current b2bConnections collection with onlyData=false, limit=100 and
every offset page. Request ConnectionId,ConnectionName,DocumentId,
ProviderId,ProviderName,Status,DirectionCode,MessageId,MessageName and
TransformMode; intersect fields with current
metadata. Match exact document identity and requested connection/provider
business names uniquely. Cross-check ConnectionId against PartnerMessageId
and the same document/provider/name in a fresh invoking-workflow provider-task
export, using the declared native connection verification. Preserve current
connection status; this operation never activates it. For a staged Disabled
rule an Inactive connection is permitted and is reported as staged only.
For an Enabled rule require the current enabled connection and current
provider-owned delivery-method qualification; never silently disable a
requested enabled rule to pass validation.

For Supplier Site, use the existing supplier/site-owned public reads:
suppliersLOV, matching exact existing SupplierId and SupplierNumber/name;
then its exact suppliersLOV/SupplierId/child/sitesLOV collection with fields
SupplierSiteId,SupplierSite,ProcurementBUId,ProcurementBU and complete pages.
Require one intended site under that supplier and its current BU ownership.
No supplier, site or BU master is created. Supplier display labels and number
are current values, not inferred from an identifier. Qualify all exact status
choices through current ORA_CMK_CONNECT_STATUS and effective lookupCodes;
legacy ORA_CMK_APPL_PTNR_DOC_STATUS labels are not writable current codes.

Decode the selected current header Metadata as bounded strict JSON, one
base64 layer as qualified from current returned attachment representation.
Require unique metadata names, understood number/varchar2 types and exact
required Y/N flags. For DEFAULT permit only ConnectionId,ConnectionName,
ServiceProviderName. For SUPPLIER_SITE permit the current header's SupplierId,
SupplierName,SupplierNumber,SupplierSiteId,SupplierSiteName plus those three
connection fields. Supply every mandatory field and the requested site pair;
reject unknown fields, missing/partial site pairs and mismatched master or
connection labels. Do not include ProcurementBU unless the current header
explicitly represents it. Business ownership is still verified separately.
Match full existing details under the exact header by default identity or
supplier/site identity before approval. Identical rows return reuse;
conflicting or duplicate scope blocks create and requires a separately
supported update, never a second POST.

The existing verify_cmksc_runbook_rest_state owns fresh exact self-link GET
and complete-detail readback after one dispatch. Compare generated positive
DetailId, exact HeaderId and Status and every intended Data field after the
same strict decoding; reject duplicate JSON keys or extra/missing fields.
Require exactly one intended scope row and all prior details unchanged,
excluding only server audit/link fields. No accepted/uncertain POST is
repeated. Preserve the real action result separately from verification.
The public routing view explains ConnectionId to PartnerMessageId and
supplier/site relationships; its example IDs are never inputs:
[CMK application partner setup view](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/cmkapplpartnerssetupvl-3023.html).

## Native Supplier-Site FSM Property Profile

Select reference_profile native_supplier_site_fsm at business intake. Existing
supplier, site, provider, identifier-type, collision and property-verification
nodes own this profile; no new execution service or write endpoint is added.
Use the declared suppliersLOV and exact parent sitesLOV GETs to resolve current
SupplierId/SupplierNumber/name and SupplierSiteId/SupplierSite/derived
ProcurementBUId/name. Complete every page and require exact current parent
ownership. Use the declared public b2bServiceProviders GET for current exact
name, ServiceProviderId and stored UserDefined Y/N; match that provider against
the supplied fresh full provider-task export's ProviderName, UserDefined and
ProviderType. Keep the existing role/type/feature and eligibility rules.

For check_cmksc_partner_property_duplicate and prepared-import collision
validation, consume the invoking workflow's completed fresh full exact-task
configuration export. Validate current host/task/completion, no restrictive
criteria, safe ZIP and complete ORA_CMK_PARTNER_PROP schema and rows. Apply the
existing Supplier CSV Mapping, Partner Key and Field Contract and alternate
identifier collision rules to the complete native namespace. Require intended
supplier/site/derived BU/type/provider scope absent and the proposed partner
identifier unambiguous across all rows. A changed identifier or status does
not evade an existing scope. Never copy source-host IDs or invent master IDs.

Prepare one row from the exact current header-only template using the existing
15-column supplier mapping, all required current references and explicit
business inputs. Keep customer/account fields and unspecified optional fields
empty. The normal Core Data Loader and Task Hook own preflight/approval/import.
For verify_cmksc_partner_property_state under this profile, require actual
successful approved FSM processing and fresh completed full before/after
configuration-task exports. Compare all 15 intended cells including create
blanks and exact existing supplier/site/BU relationship. Require zero before
and one intended row after, preserve every previous partner row as a multiset
and every row/header/type in the other seven objects. Generated property REST
IDs are not exported and are not invented or claimed as verified. This is
saved messaging-property creation, not PO routing or supplier delivery proof.

## Native FSM Account Number References

The invoking Run Book supplies current completed full task data for collision
checks and a separate genuine header-only template for creation. These are
private local artifact inputs from the already selected shared export workflow;
this resolver does not initiate an export or use a populated export as the
new-row import seed. Public account business-field meanings are linked in
Native FSM Account Number Creation; all setup mutations remain FSM imports.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_fsm_account_create | Only create_account_number_fsm after valid staged inputs, and again for final prepared-import validation | Exact task/target/active Run Book, business account number, supplier/site/optional BU selection or recorded delegated fixture, current template and complete full export from invoking shared workflow when available | Execute the existing resolve_simplified_feature_state contract first on this target. Then execute only the existing resolve_cmksc_supplier and resolve_cmksc_supplier_site read contracts for this account operation, preserving their exact-number/name scope and complete selected-supplier paging. Consume the supplied full export and template only after task/host/completion/safe ZIP/schema checks. No provider lookup or account REST write | Verified supplier ID/name/number, selected child site ID/code and derived Procurement BU ID/name; complete native account four-cell rows and all template member/header/type metadata | Require enabled feature and one current supplier/site/BU relationship consistent with every supplied value. A duplicate site label in different BUs needs the retained exact BU/identity, never first-row selection. Require current four-string-column account schema. Across the complete account export, zero occurrences of the requested AccountNumber permits strict create; the same number at the intended tuple is a duplicate-create block, and another parent tuple is a parent-conflict block. Missing source artifacts return source_required rather than assuming absence. Missing reference choices return blocked with readable selections; incomplete/failed reads never prove absence | Exact AccountNumber plus current SupplierNumber, VendorSiteCode and ProcurementBU; separate private live IDs; complete before-snapshot, template/source fingerprints, requested scope and current no-collision evidence | source_required for a missing genuine template or full baseline; blocked for disabled feature, unknown/ambiguous/cross-parent references, existing account number, incompatible schema, incomplete pages, auth/authz or transport/Fusion errors. No substitute route or generated customer ID |

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| verify_cmksc_fsm_account_state | Only verify_account_number_fsm after its successful-import and immutable-intent checks | Invoking Run Book's explicitly supplied approved four-cell intent and ZIP hash, completed successful Core Data Loader result, private complete before-export and fresh complete same-target after-export from shared.setup-export.task-level-export | Validate exact task/host/completion/full scope and safe ZIP for both exports. Require matching current native account schema and exactly zero intended AccountNumber before, exactly one account row after with all four cells equal to approved intent. Match all previous account rows as a preserved multiset and every row/header/type of each unrelated CSV member unchanged. Verify exactly one added account row and no extra changes. Native export establishes the natural tuple, not an unexported generated AccountNumberId | Verified newly created account business tuple, four-field comparison, complete preserved-row/object coverage, bound result/hash/provenance/time and setup-only result | Block on missing/duplicate/different intended row, wrong target/task, changed approved bytes, incomplete or stale exports, extra rows/changes or unsuccessful/uncertain import. Preserve actual import outcome separately; do not retry or mutate |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_ACCOUNT_REFERENCES | decision | 101 | reference_lookup | verified->CMKSC.FSM_ACCOUNT_PACKAGE;source_required->CMKSC.FSM_ACCOUNT_SOURCE_REQUIRED;blocked->CMKSC.FSM_ACCOUNT_ISSUES | CMKSC.FSM_ACCOUNT_INPUT | stop | Only create_account_number_fsm: execute qualify_cmksc_fsm_account_create. This is the selected read-only feature/parent/source/collision step; no provider selection, export submission or setup mutation |
| CMKSC.FSM_ACCOUNT_VERIFY_STATE | decision | 111 | reference_lookup | verified->CMKSC.FSM_ACCOUNT_VERIFIED;blocked->CMKSC.FSM_ACCOUNT_VERIFY_ISSUES | CMKSC.FSM_ACCOUNT_VERIFY_INPUT | stop | Only verify_account_number_fsm: execute verify_cmksc_fsm_account_state on the bound completed-import and supplied before/after evidence. No external call or setup mutation |

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_fsm_ship_to_create | Only create_ship_to_assignment_fsm after valid staged inputs and again at final prepared-import validation | Exact target/task/active Run Book; intended existing account and supplier/site/BU; physical location code or recorded delegated fixture; supplied genuine template and completed full same-target configuration export | First execute resolve_simplified_feature_state, then the existing resolve_cmksc_supplier and resolve_cmksc_supplier_site read contracts. Consume the current full native account and assignment rows and seven-column template. Through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bShipToLocationsLOV/describe and its collection with q=LocationCode='<escaped exact selected code>';fields=LocationId,LocationCode,LocationName,SetName;onlyData=true;limit=25;offset=0 and all pages. Require describe confirms readable fields and queryable LocationCode. No location master or account creation | Current feature, supplier/site/BU identities and business references; exact physical LocationId/LocationCode/LocationName/SetName; complete native account/assignment rows and template types | Require one current supplier/site/BU and exactly one saved AccountNumber row under that exact natural parent tuple; a number under another tuple conflicts. Require one exact physical code/positive identity in the complete eligible location response. Across all current assignments, block the same physical LocationId or exact code under that supplier/site/BU regardless of AccountNumber, distinguishing duplicate from an attempted reassignment; never move a location to the new account silently. Reject a populated customer-location variant. Require the current seven-field profile and no requested assignment before. Missing template/baseline returns source_required; missing parent or ambiguous references blocks before preparation | Qualified seven-cell assignment intent with ShipToCustLocationId empty, current private reference identities, parent existence and assignment-absence evidence, full before-snapshot and source/template fingerprints | source_required for absent artifacts; blocked for missing parent, existing/conflicting assignment, unknown/ambiguous code or parent, cross-BU relation, schema mismatch, disabled feature, incomplete read or auth/transport/Fusion error. No broadened lookup, invented ID or fallback route |

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| verify_cmksc_fsm_ship_to_state | Only verify_ship_to_assignment_fsm after successful-import/immutable-intent checks | Invoking Run Book's approved seven-cell intent/hash, successful completed Core Data Loader result and complete fresh same-target before/after task exports from shared workflow | Validate exact task/target/completion/full scope, safe ZIP and compatible complete schemas. Require zero matching physical assignment under the intended supplier/site/BU before and exactly one after with every cell equal to intent and exact saved AccountNumber parent. Preserve all earlier assignment rows as a multiset and every account/other-object row/header/type unchanged. Require one added assignment only | Verified new physical ship-to assignment and exact seven-field/account-parent/preservation coverage. No generated assignment-ID or PO-delivery claim | Block on missing/multiple/different assignment, moved existing assignment, missing parent, extra changes, incomplete evidence or failed/uncertain import. Preserve actual import outcome separately; no replay |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_SHIP_TO_REFERENCES | decision | 121 | reference_lookup | verified->CMKSC.FSM_SHIP_TO_PACKAGE;source_required->CMKSC.FSM_SHIP_TO_SOURCE_REQUIRED;blocked->CMKSC.FSM_SHIP_TO_ISSUES | CMKSC.FSM_SHIP_TO_INPUT | stop | Only create_ship_to_assignment_fsm executes qualify_cmksc_fsm_ship_to_create. Read-only parent/source/location/collision qualification; no account or assignment mutation |
| CMKSC.FSM_SHIP_TO_VERIFY_STATE | decision | 131 | reference_lookup | verified->CMKSC.FSM_SHIP_TO_VERIFIED;blocked->CMKSC.FSM_SHIP_TO_VERIFY_ISSUES | CMKSC.FSM_SHIP_TO_VERIFY_INPUT | stop | Only verify_ship_to_assignment_fsm executes verify_cmksc_fsm_ship_to_state on supplied immutable before/after evidence. No external call |

## Native FSM Customer Location References

Sources for the read-only purpose and account-site joins are the public
[customer addresses](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-huborganizations-partynumber-child-address-get.html),
[address purposes](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-huborganizations-partynumber-child-address-addressnumber-child-addresspurpose-get.html)
and [bill-to sites](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-billtosites-get.html).
The current thirteen-column native profile owns its distinct CSV mapping.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_fsm_location_create | Only create_location_code_fsm after valid business_intake/source_export inputs and again for final prepared_import | Exact target/task/active Run Book, current request fingerprints, location_reference_profile native_customer_party or native_customer_bill_to, new business location code, represented customer/site choice, genuine current template and completed full same-target configuration export supplied by the invoking workflow | First execute resolve_simplified_feature_state. For native_customer_party execute qualify_cmksc_native_customer_party_site, including its current Customer-role and customer/site identity joins. For native_customer_bill_to execute qualify_cmksc_native_customer_bill_to_site below instead; do not require shipToPartySites for a bill-to-only site. Through core.fusion-api.rest-api-client GET /crmRestApi/resources/11.13.18.05/hubOrganizations/<URL-encoded verified PartyNumber>/child/Address/describe then the same Address collection with fields=PartyId,PartyNumber,AddressId,AddressNumber,LocationId,Status,StartDateActive,EndDateActive;onlyData=false;limit=25;offset=0 and all pages. Match the selected same-parent site in that complete scope. GET its documented Address/<URL-encoded selected AddressNumber>/child/AddressPurpose/describe then the complete collection with fields=AddressId,AddressNumber,Purpose,Status,StartDate,EndDate;onlyData=false;limit=25;offset=0 and all pages. GET /crmRestApi/resources/11.13.18.05/billToSites/describe, confirm queryable PartySiteId and required readable fields. When bill_to_reference_profile is customer_account_finder, execute Customer Account Bill-To Reference Qualification below with the same projection and complete paging, then match the exact selected site locally; otherwise GET that collection with q=PartySiteId=<verified positive site ID>;fields=CustAccountId,CustAcctSiteId,SiteUseId,PartySiteId,PartySiteNumber,LocationId,SiteUseCode,Status,Status1,StartDate,EndDate,StartDate1,EndDate1;onlyData=false;limit=25;offset=0 and every page. Never send a setup or master write | Current parent/site identities, matching current Address/Location identity and effective status, complete purpose set and complete same-site bill-to account/site-use tuples, native full location rows, thirteen-field template/types and source provenance | Require compatible metadata, one exact active/effective same-party address agreeing with selected site number/identity, and the purpose required by the selected profile: native_customer_party requires effective SHIP_TO; native_customer_bill_to requires effective BILL_TO and no effective SHIP_TO. Evaluate only effective A purposes and retain complete raw evidence. A context-dependent zero from billToSites without qualified BU context is inconclusive, including under the existing exact-site query profile; stop reference qualification and require the explicitly selected customer_account_finder profile before declaring bill-to absence. BILL_TO requires exactly one distinct active/effective same-site BILL_TO tuple with positive CustAcctSiteId/SiteUseId and matching location; these become the native account-site references. Complete absence of BILL_TO plus zero effective bill-to tuples establishes ship-only empty fields. Conflicting purposes, wrong site, incomplete read or multiple tuples block rather than picking first. Require the standard customer profile in Native FSM Customer Location Code Creation and compatible same-target native evidence. Require no exact/case-only requested LocationCode and no existing customer-number/site mapping in the complete before-export. The template may not contain surrogate identity headers excluded from the current profile | Current thirteen-cell intent with exact customer/site, source-qualified standard constants, SHIP_TO/BILL_TO flags and account-site references, current scope-absence and all-object before snapshot, bound read/source/template/request fingerprints. Preserve optional fields or return their precise profile gap | source_required for missing genuine template/full before-export; blocked for schema/profile mismatch, disabled feature, unavailable/unrepresented customer, missing/ambiguous site/purpose/account tuple, existing code/site mapping, explicit unqualified setting or any incomplete/auth/transport/Fusion read. Never silently remove a bill-to purpose, invent keys or use another create route |


## Bill-To-Only Customer Location Reference Profile

Public scope boundary: the [published Redwood location-code behavior](https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/inv26c/26C-inventory-wn-f46527.htm)
limits site selection to sites without a location code and reflects the site
address purposes in the ship-to/bill-to fields. This does not establish an FSM
contract for two different codes on one site or for overriding those purposes.
Distinguish an unqualified requested mapping from an absent eligible fixture;
do not change the customer document or master data to conceal that gap.

Select location_reference_profile native_customer_bill_to and
bill_to_reference_profile customer_account_finder before the first location
qualification pass. This is an FSM-only reference profile for a represented
existing customer/account and a bill-to-only address. It does not change the
thirteen-column native standard-field contract or enable a REST write.
The [26D location-code guide](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/configuring-and-managing-b2b-messaging.pdf),
printed pages 472–474, distinguishes bill-to and ship-to address use. The
public address, purpose and bill-to-site reads linked above supply independent
parent references; the current exact-task native template and deployed field
contract remain mandatory for preparing an FSM row.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_native_customer_bill_to_site | Only create_location_code_fsm with native_customer_bill_to and customer_account_finder selected at intake | Current exact-task full export, represented Customer-role party/account, current request and explicitly selected or delegated bill-to site and lookup-context BU | Execute the existing public Customer-role qualification and qualify_cmksc_native_customer_account; read complete bill-to candidates using Customer Account Bill-To Reference Qualification for that account and qualified BU, retaining them as unqualified until the address intersection below succeeds. Through core.fusion-api.rest-api-client GET /crmRestApi/resources/11.13.18.05/hubOrganizations/<URL-encoded verified PartyNumber>/child/Address/describe and the complete Address collection with fields=PartyId,PartyNumber,AddressId,AddressNumber,LocationId,Status,StartDateActive,EndDateActive;onlyData=false;limit=25;offset=0 and all pages. For the exact matched address GET Address/<URL-encoded AddressNumber>/child/AddressPurpose/describe and its complete collection with fields=AddressId,AddressNumber,Purpose,Status,StartDate,EndDate;onlyData=false;limit=25;offset=0 and all pages | Verified party/account; complete eligible bill-to tuple including PartySiteId,PartySiteNumber,LocationId,CustAcctSiteId,SiteUseId; address identity, same-party relationship, active dates and complete effective purposes | Require one active same-parent address whose AddressId equals the verified tuple PartySiteId, AddressNumber equals PartySiteNumber and LocationId equals LocationId under compatible current metadata. Keep party, account, site, location and site-use identities distinct. Require one distinct active/effective same-account BILL_TO tuple with positive CustAcctSiteId and SiteUseId, and complete effective address-purpose evidence containing BILL_TO and no SHIP_TO. Deduplicate identical projections only; conflicting IDs, dates or purposes block. Resolve any delegated selection by a recorded business policy and exact unique match, never by first conflicting row. A site with both purposes cannot satisfy a bill-to-only request by suppressing SHIP_TO. No shipToPartySites membership is required | Exact customer and account numbers, bill-to business site number and qualified same-parent address/site/location/account-site/site-use identities; Billto=Y and Shipto empty with populated CustAcctSiteId/CustAcctSiteUseId under the existing thirteen-field contract; retain complete current evidence and native source contract | Block for absent/inactive/ambiguous address or account tuple, wrong parent/BU/site/location, incomplete purpose evidence, any effective SHIP_TO, incompatible current identity join or missing native field contract. Do not create masters, guess an ID, suppress a real purpose or substitute another write route |

## Customer Account Bill-To Reference Qualification

Select `bill_to_reference_profile=customer_account_finder` at business intake
for `native_customer_party` or `native_customer_bill_to` when a represented existing customer account is
available. Preserve any earlier empty site-query result separately; selecting
this documented finder changes reference qualification only, not the native
write route or the customer's requested purposes.

First execute the current party/account join from
`qualify_cmksc_native_customer_account` for the selected represented customer
and account. Do not copy an account key from the native export without that
current public relationship check. Qualify `BillToSiteFinder` and its
`BindCurrentDate`, `BindCustAcctId`, `BindSiteUseCd`, `BindStatus`, and `bu_id`
variables in current `billToSites/describe`. Through the Core REST client GET
that collection with
`finder=BillToSiteFinder;BindCurrentDate=<current YYYY-MM-DD>,BindCustAcctId=<verified account ID>,BindSiteUseCd=BILL_TO,BindStatus=A,bu_id=<verified lookup-context BusinessUnitId>`,
the resolver's same complete field projection, `onlyData=false`, `limit=25`
and `offset=0`, retaining the exact finder across every page. The qualified
BU is a finder variable inside the same finder value, not a separate URL
query parameter; a standalone bu_id is rejected by the service. Resolve it
as described below. An
optional metadata marker alone does not establish useful unscoped behavior;
a complete zero result without qualified BU context is inconclusive for
customer account-site existence. Never invent a BU, negative sentinel or
another customer's account to obtain rows.

Resolve the explicitly selected or delegated non-production business-unit
name through the Core client: GET
`/fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV/describe`, require
readable BusinessUnitId/BusinessUnitName and queryable BusinessUnitName, then
GET that collection with `q=BusinessUnitName='<escaped exact selection>'`,
`fields=BusinessUnitId,BusinessUnitName`, `onlyData=false`, `limit=25`,
`offset=0` and all pages. Require one exact current name and positive integral
ID; retain selection provenance before dispatching the bill-to finder. The
[public Financials business-unit read](https://docs.oracle.com/en/cloud/saas/financials/26b/farfa/op-finbusinessunitslov-get.html)
qualifies identity only. The finder must independently return the selected
customer/account's eligible site tuple under that exact BU context. This is
reference-lookup context, not a requested customer OrderProcessingBU setting;
do not add PartnerKey3 or a new column to the location CSV. No arbitrary
first-unit, cross-account or label-similarity match is permitted.

Require each row's `CustAccountId` to match the verified account. Intersect
the complete results with the verified same-customer address scope by
exact site ID, business site number and location ID. For native_customer_party
retain its ship-to qualification; for native_customer_bill_to use the independent
bill-to address join below and do not require a ship-to row. Preserve all original
purpose, effective-date, uniqueness and account-site/site-use checks. A
qualified delegated site selection may be made within that intersection,
recorded before final purpose validation; never choose the first conflicting
account tuple. Zero results or a BILL_TO purpose without one qualifying
same-site account tuple remains blocked. No account/site/master is created.

Sources: the [published bill-to-site finder](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-billtosites-get.html)
and the existing public customer-account-site reference above. Availability,
matching rows and optional-variable behavior remain current-target checks;
public documentation alone does not prove them.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| verify_cmksc_fsm_location_state | Only verify_location_code_fsm after successful completed import and current-request/immutable-intent checks | Invoking Run Book's exact approved thirteen-cell intent/ZIP hash and current request fingerprints, completed successful Core Data Loader result, complete same-target full before-export and fresh full after-export from shared.setup-export.task-level-export | Verify safe ZIP, exact target/task/completed/full-scope provenance and compatible complete native headers/types. Require zero requested code and zero selected customer/site mapping before, then exactly one added matching code/customer/site row with all thirteen cells equal to approved intent, including Y/empty Billto and Shipto, exact CustAcctSiteId/CustAcctSiteUseId and all intentional blanks. Preserve every earlier location row as a multiset and every row/header/type in all unrelated CSV objects. A current export lacking XrefLocValueId cannot prove its numeric generated value; do not require or invent an absent column | Verified new customer location code, thirteen-field purpose/account-site comparison, complete prior-row/other-object preservation and bound actual FSM/result/source/request evidence; setup-only customer result | Block on missing/multiple/different row, lost purpose flag or account reference, incomplete/current-request mismatch, extra changes or failed/uncertain import. Preserve the actual import outcome independently; do not hide failed field comparisons in a broad success count or replay the import |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_LOCATION_REFERENCES | decision | 141 | reference_lookup | verified->CMKSC.FSM_LOCATION_PACKAGE;source_required->CMKSC.FSM_LOCATION_SOURCE_REQUIRED;blocked->CMKSC.FSM_LOCATION_ISSUES | CMKSC.FSM_LOCATION_INPUT | stop | Only create_location_code_fsm executes qualify_cmksc_fsm_location_create. Read-only exact source/customer/site/purpose/account-site/collision qualification; no setup or master mutation |
| CMKSC.FSM_LOCATION_VERIFY_STATE | decision | 151 | reference_lookup | verified->CMKSC.FSM_LOCATION_VERIFIED;blocked->CMKSC.FSM_LOCATION_VERIFY_ISSUES | CMKSC.FSM_LOCATION_VERIFY_INPUT | stop | Only verify_location_code_fsm executes verify_cmksc_fsm_location_state on the bound actual import and complete immutable before/after evidence. No external call |

## Native FSM Initial Settings References

The invoking Run Book supplies the completed current full exact-task export
and genuine header-only template as private local evidence. Global parameter
and document-parameter rows are existing target configuration; their current
identities are preserved. This profile performs no export or setup mutation.
Public product meanings are linked in Native FSM Initial Settings Inputs.
Current metadata and the exact native/API joins below qualify the selected
deployment; an older dictionary or a matching number alone is insufficient.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_fsm_initial_settings | Only configure_initial_settings_fsm after valid business_intake/source_export inputs and again for prepared_import | Exact configured target/task/active Run Book, current source/request fingerprints, explicit initial-setting field states and units, selected existing delivery-type or document/property business labels, current full native export and template supplied by the invoking shared workflow | First execute resolve_simplified_feature_state. Validate safe ZIP, same task/host/completed/full-scope provenance and exact native schemas before interpreting rows. For selected processing settings, through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bMessageParameters/describe and its complete collection with onlyData=false;limit=25;offset=0 and every page; request MsgParamId plus only the current readable API fields listed by the native field mapping. For selected delivery limits, first through core.fusion-api.apps-common.lookups and the same Core client GET /fscmRestApi/resources/11.13.18.05/genericLookups/describe, then genericLookups with finder=LookupTypeFinder;LookupType=ORA_CMK_DEL_METHOD_TYPE,ViewApplicationId=0;onlyData=false; follow its validated same-target lookupCodes child link and all pages with fields=LookupCode,Meaning,EnabledFlag,StartDateActive,EndDateActive;onlyData=true;limit=100;offset=0. Require one exact lookup context and valid complete code/effectivity evidence. Then GET /fscmRestApi/resources/11.13.18.05/b2bDeliveryMethodTypes/describe and its complete collection with fields=DeliveryMethodTypeId,DeliveryMethodType,MaximumMessageSize;onlyData=false;limit=25;offset=0 and all pages. For selected document properties, qualify the existing task-bound b2bDocuments metadata and complete collection with fields=DocumentId,DocumentName,DocumentType,Direction;onlyData=false;limit=100;offset=0. Resolve the exact selected document/direction. Follow only its actually returned same-target additionalConfigs child link after the declared Core GET describe confirms this child and readable ParamDataId,ParamName,ParamNameMeaning,ParamNumericValue,ParamStringValue,ReadOnlyFlag. Read that entire parent-scoped child with those fields;onlyData=false;limit=100;offset=0 and all pages. Accept links in @context.links or the supported links form. Do not synthesize opaque document/item keys, infer a child from an unavailable public URL, request PATCH capability or dispatch a write | Current parameter identity/selected values and field metadata; current type identities/codes/limits; current document identity/direction and exact property IDs/names/meanings, typed values, read-only eligibility; complete native before rows and template metadata | Require exactly one global parameter row in native export and exactly one current public MsgParamId matching it; compare each selected native/API before-value pair by the qualified mapping. Resolve an exact eligible LookupCode or one case-insensitive exact Meaning among enabled date-effective codes on the operation date; null dates are unbounded and an end date on/before that date is inactive. Require one matching DeliveryMethodType code in the complete current public/native rows, with the same current ID. Independently qualify the exact native/public MaximumMessageSize field binding and MB unit from the 26D product guide plus current metadata or source-qualified representation evidence; equal before values only corroborate that mapping and never prove units. Missing independent field/unit binding blocks this setting. Preserve ModuleId. Resolve a property by exact ParamName or one exact case-insensitive ParamNameMeaning within the complete selected document child; require one positive unique ParamDataId, ReadOnlyFlag false and exactly one native row with that same ID. Require native DefltNumericValue equals ParamNumericValue and native DefltStringValue equals ParamStringValue using current typed/null representation, retaining MaxNumericValue as unchanged bounds metadata. Reject a document/property whose meaning, unit, enum, length or effective eligibility is unqualified. Native ID presence alone does not identify a property. No source ID is copied across environments | Existing qualified row identities, exact current full rows, selected field mappings/units/constraints and effective requested state, complete before/template/read fingerprints and per-object comparison coverage; no new global identity | source_required for absent genuine full export/template; blocked for disabled feature, unavailable/ambiguous parent/property, read-only property, missing metadata/link, native/API mismatch, unsupported requested field/unit, malformed/incomplete pages or auth/transport/Fusion error. No arbitrary numeric ID, new global row, guessed route or fallback |

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| verify_cmksc_fsm_initial_settings_state | Only verify_initial_settings_fsm after current-request/immutable-intent and actual successful-import checks | Invoking Run Book's exact approved full intended selected rows, per-field business state/unit map, immutable ZIP hash and successful completed Core Data Loader result, complete full before-export and fresh full same-target after-export from shared.setup-export.task-level-export | Validate safe ZIP, exact task/host/completed/unrestricted scope and complete compatible member/header/type sets. Match selected processing row by preserved MsgParamId, selected type rows by preserved DeliveryMethodTypeId plus DeliveryMethodType and selected property rows by preserved ParamDataId with their approved semantic parent binding. Require exactly the same identities/counts before and after: no additions, removals or duplicate identities. Compare every approved changed cell with exact intended value, every unspecified cell of each selected row with its before value, and every unselected row/object as a preserved multiset. Preserve metadata/header/type shape. Classify actually changed values separately from already matching values; same-value import is not changed-value coverage | Exact selected initial settings with per-field before/approved/observed results, unchanged identity/row counts and preserved unrelated settings/objects, actual import and source/request bindings, setup-only evidence | Block on missing/extra/different selected row or field, an unrequested delta, changed parent/key/module/bounds metadata, failed/uncertain import, incomplete/stale evidence or mismatched request/approved bytes. Preserve actual process outcome separately. No retry or scheduler/message-delivery claim |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_SETTINGS_REFERENCES | decision | 161 | reference_lookup | verified->CMKSC.FSM_SETTINGS_DESIGN;source_required->CMKSC.FSM_SETTINGS_SOURCE_REQUIRED;blocked->CMKSC.FSM_SETTINGS_ISSUES | CMKSC.FSM_SETTINGS_INPUT | stop | Only configure_initial_settings_fsm executes qualify_cmksc_fsm_initial_settings. This is the declared read-only source/identity/semantic/field qualification; no provider/supplier creation, export initiation or setup mutation |
| CMKSC.FSM_SETTINGS_VERIFY_STATE | decision | 171 | reference_lookup | verified->CMKSC.FSM_SETTINGS_VERIFIED;blocked->CMKSC.FSM_SETTINGS_VERIFY_ISSUES | CMKSC.FSM_SETTINGS_VERIFY_INPUT | stop | Only verify_initial_settings_fsm executes verify_cmksc_fsm_initial_settings_state on supplied approved actual-import and full before/after evidence. No external call |


## Native FSM Document Routing References

The [public routing view](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/cmkapplpartnerssetupvl-3023.html)
explains document/context and connection/supplier relationships, not target
IDs. The [26D purchasing integration guide](https://docs.oracle.com/en/cloud/saas/procurement/26d/fainp/pch-collaboration-messaging-framework-outbound.html)
explains supplier-site B2B communication. Current runtime metadata and genuine
exact-task exports qualify this native profile. No internal source-search
service or local research capture is a customer runtime prerequisite.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_fsm_routing_create | Only create_document_routing_fsm after its input gate, including prepared_import revalidation | Current request/target/active Run Book, exact selected document/provider/connection, DEFAULT or SUPPLIER_SITE business scope, full current provider/configuration exports and genuine header-only configuration template supplied by the invoking shared export workflow | Execute resolve_simplified_feature_state and the current public document lookup. Through core.fusion-api.rest-api-client use only current catalog-qualified b2bDecisionTables, b2bApplicationConnections and b2bConnections GET/describe bindings and Current Routing Model Qualification Reads above. Use the qualified provider outboundCollaborationMessages child GET and native connection join from qualify_cmksc_existing_document_routing. Resolve eligible Disabled status through current ORA_CMK_CONNECT_STATUS lookupCodes. For supplier scope use resolve_cmksc_supplier and resolve_cmksc_supplier_site plus their current parent/BU check; the declared read-only recovery supplier-site GET records its current B2B communication method. This resolver issues no import, POST, PATCH, validator action or UI write | Current generated DetailId type/default, complete current header Metadata and contexts, all current detail rows, exact document/provider/connection identity and direction, native connection tuple, eligible status and applicable supplier/site/BU ownership and current communication method | Require exact eight-column native profile and generated precision-18 integer DetailId metadata, accepting the current string/BigInt wire representation only as exact positive decimal text without floating-point conversion; derive one existing Document/document-ID/DEFAULT or SUPPLIER_SITE header. Decode only qualified current API attachment representations; native Data remains strict plain JSON. Reject duplicate keys, unsupported required metadata/types or nonunique identities. Match one current connection across native/public identity/name/provider/document/direction; Inactive is permitted only for the requested Disabled staged rule. For DEFAULT require no existing same header/connection rule; for SUPPLIER_SITE require no existing same header/supplier/site/connection rule, regardless of status. Verify selected site ownership and all provided labels. No absence conclusion from an empty partial read | Qualified current header contexts and exact native Data map, blank new DetailId/ParentDetailId, eligible Disabled code, same-target absence and coupled-effect evidence; source_required only when exports/template are absent | Missing/incompatible generated-key or field contract, malformed JSON, wrong target/task, incomplete reads, collision or uncertain prior mutation returns blocked with exact diagnostic. No fabricated IDs, fallback setup route or replay |
| verify_cmksc_fsm_routing_state | Only verify_document_routing_fsm after successful completed approved FSM import and verification input gate | Bound current business request, immutable approved eight-cell row/ZIP hash, full before and fresh full after configuration exports, current connection/header/supplier reference evidence and actual successful job result | Consume only genuine complete same-target exact-task export results supplied by the invoking shared exporter and reapply the read-only joins in qualify_cmksc_fsm_routing_create for identity verification without its create-absence requirement; no export initiation or mutation here | All eight native fields, every Data field including generated target references and retained business labels, fresh positive DetailId, Status, parent/context fields, all prior rows and other seven objects, applicable supplier-site communication state | Require zero intended before rows and exactly one after row, new unique positive DetailId absent from before, blank ParentDetailId, exact requested Status/contexts, strict unique-key Data object with every intended resolved field equal and no unexplained extra/missing field. Compare each representation separately: the native CSV may reintroduce ProcurementBU as the portable exact current BU label, while persisted public Data omits that preparation-only field after importer site resolution. Qualify that difference against current complete native/public before rows; compare the after native row with the exact approved native fields and the public Data without ProcurementBU. Verify the final site and BU through the current public parent relation. No other extra, missing or changed field is exempt. Preserve every prior routing row and all seven unrelated object datasets as multisets with unchanged headers/types. Compare supplier communication method separately; report any coupled change without claiming rule activation or delivery | verified per requested rule with generated-key and complete field/preservation coverage, actual import IDs and setup-only result; combined routing acceptance needs both default and supplier-site passes | Missing/different/duplicate rule, wrong generated ID, unexpected field/state changes or incomplete evidence returns blocked; preserve successful job status separately and do not reimport |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_ROUTING_REFERENCES | decision | 181 | reference_lookup | qualified->CMKSC.FSM_ROUTING_PACKAGE;source_required->CMKSC.FSM_ROUTING_SOURCE_REQUIRED;blocked->CMKSC.FSM_ROUTING_ISSUES | CMKSC.FSM_ROUTING_INPUT | stop | Only create_document_routing_fsm executes qualify_cmksc_fsm_routing_create; fully qualified current native/reference evidence is required at prepared_import. No mutation |
| CMKSC.FSM_ROUTING_VERIFY_STATE | decision | 191 | reference_lookup | verified->CMKSC.FSM_ROUTING_VERIFIED;blocked->CMKSC.FSM_ROUTING_VERIFY_ISSUES | CMKSC.FSM_ROUTING_VERIFY_INPUT | stop | Only verify_document_routing_fsm executes verify_cmksc_fsm_routing_state; exact one-rule result and all-object preservation, no replay |


## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_combined_account_ship_to | Only create_account_ship_to_combined_fsm after valid staged inputs | Exact configured task/target/active Run Book, original business request, selected new account, existing supplier/site/BU and physical location code, genuine template and fresh complete native configuration export from shared workflow | Execute resolve_simplified_feature_state, resolve_cmksc_supplier and resolve_cmksc_supplier_site with their existing exact-number and complete selected-parent scope. GET b2bShipToLocationsLOV/describe and its declared collection through core.fusion-api.rest-api-client with REST-Framework-Version 9, q=LocationCode='<escaped exact business code>',fields=LocationId,LocationCode,LocationName,SetName,onlyData=true,limit=25,offset=0 and all pages. Consume the complete exact-task before-export locally; no account REST, master write or exporter call belongs to this resolver | Current supplier identity/number, site identity/code and derived Procurement BU, current positive physical LocationId/exact code/set, feature state, all eight native before object rows and compatible template schemas | Require current enabled feature, exact selected supplier/site/BU parent, one unambiguous current physical location and current native four/seven-column mappings. Require requested AccountNumber absent globally. Require same physical location ID or code absent under the intended supplier/site/BU regardless of existing AccountNumber. Resolve the new assignment parent to exactly the one intended package-local account row with identical AccountNumber,SupplierNumber,VendorSiteCode,ProcurementBU; its absence from target is expected for this bounded trial and is not a missing saved-account error. Never weaken the standalone saved-parent profile | Qualified four-cell new account and seven-cell assignment intent, zero collisions, current private parent/location evidence and source fingerprints | Block entire package for missing, ambiguous, conflicting or partial references, existing account or assignment, incompatible schema, disabled feature, wrong parent, auth/transport/Fusion failure or absent source. Do not reassign, invent keys, split a failed package or infer native execution order |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.COMBINED_REFERENCES | decision | 195 | reference_lookup | qualified->CMKSC.COMBINED_PACKAGE;blocked->CMKSC.COMBINED_ISSUES | CMKSC.COMBINED_INPUT | stop | Only create_account_ship_to_combined_fsm: execute qualify_cmksc_combined_account_ship_to and all applicable Combined Account and Physical Ship-To rules. Package-local intended account is not a claim of prior saved setup |

## Configuration Task Composition References

The invoking active Run Book supplies authoritative local row intent/field
states and private genuine shared-export source artifacts. The existing named
resolvers remain the only authorities for target identities, codes, fields,
units, collision evidence and saved references. No new endpoint or importer
lookup behavior is introduced.

Evaluate each existing component contract against its own typed component
projection and stage while retaining the whole composition operation, request
fingerprint and row vector in the authoritative context. Component validation
is not a separate import, a narrower whole-request label, or component approval.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmksc_task_composition | Only qualify_configuration_task_composition_fsm after COMPOSITION_INPUT | Exact task/target/active Run Book, seven-row business/cell intent and current request/source hashes, complete full native baseline and header-only template, currently saved verified provider evidence and existing supplier/site/BU/customer/account/address/physical location choices | Execute qualify_cmksc_combined_account_ship_to for account plus physical assignment. Execute resolve_cmksc_supplier, resolve_cmksc_supplier_site, resolve_cmksc_customer, resolve_cmksc_customer_account, resolve_cmksc_provider, verify_cmksc_partner_id_type and check_cmksc_partner_property_duplicate separately for their applicable Supplier or Customer component scope, preserving all native portable-reference joins. Execute qualify_cmksc_fsm_location_create for the one customer code and qualify_cmksc_fsm_initial_settings for both existing selected settings rows. Use only each resolver's declared Core GET, qualified describe/actual returned child links, projections and complete paging. One fresh source from this run may be shared only when exact scope/target/schema/freshness and fields satisfy every consumer | Existing component resolvers' typed master/provider/account/site/location keys and numbers, current properties/collisions, selected complete processing/type rows with units/ranges and all native field-state mappings | Require all five create components absent at their exact grains, both property variants distinct and each provider already saved/verified, exact account-to-physical-assignment local four-cell relation, all customer/site purpose and collision checks, and both selected existing settings identities uniquely matched. Check every requested unit/encoding and effective-state dependency using current unselected values. A preflight source, partial job or package-local provider row is not proof of a saved provider. A requested unsupported cell blocks the whole seven-row package; do not clear omitted settings or infer new IDs | Seven per-row qualification results with source/target/intent/reference fingerprints, five unambiguous create identities, two retained full-row settings intents and exact bounded account/assignment relationship | Any failed, incomplete, ambiguous, unqualified-unit or conflicting component blocks the entire package. Retain valid choices and exact failing field/scope, avoid duplicate reads when this run's complete source is reusable, and never substitute another parent or issue setup writes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.COMPOSITION_REFERENCES | decision | 401 | reference_lookup | qualified->CMKSC.COMPOSITION_PACKAGE;blocked->CMKSC.COMPOSITION_ISSUES | CMKSC.COMPOSITION_INPUT | stop | Only qualify_configuration_task_composition_fsm: execute qualify_cmksc_task_composition and retain separate evidence for every component; no saved-provider or other standalone-parent rule is waived |
