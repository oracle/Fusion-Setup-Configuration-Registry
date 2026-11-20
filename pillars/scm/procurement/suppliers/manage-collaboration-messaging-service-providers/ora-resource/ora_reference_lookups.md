# Service Provider Prerequisite Lookups

## Collaboration Message Lookup Request Contract

The request shapes below provide read-only reference evidence for collaboration
message definition intake through the environment-specific UI route family
/fscmRestApi/rest/rv:<opaque>/en/<version>/. These GET requests have no body.
Request paths, filters and projections alone do not establish returned values,
response types, pagination completeness or permission to create configuration.
The owning resolver must qualify current same-target response evidence before
using a lookup result.

| Observed Collection | Observed Query | Requested Fields | Evidence Boundary |
|---|---|---|---|
| b2bDocuments | limit=500 | No fields projection supplied | Response identity, label, DocumentType and DocOperationId fields are not established by this request; limit=500 does not prove a complete result set |
| b2bExternalMessageDefinitions | onlyData=true; q=DocumentType='<selected DocumentType>'; totalResults=true; limit=25; offset=0 | DocumentType, ExternalMessageDefinitionId, ExternalMessageDefinitionName, MessageType, MessageSubtype, Standard, Version | The request filters by DocumentType and requests these fields; it does not establish their returned values/types, selected Document-to-DocumentType mapping, or absence of later pages |

The external-definition filter is DocumentType, not DocOperationId. Do not
substitute one for the other. A supplied request field named
ExternalMessageDefinitionName does not by itself establish its mapping to
the FSM CSV column ExtMessageTypeName. Document selection still needs a
source-backed mapping to the CSV's DocOperationId.

Require current same-target response evidence through the declared shared client.
Reuse retained evidence only after its identity, scope, freshness and
completeness checks pass; otherwise obtain it through the owning resolver.
Do not infer first-result selection, unique-label rules or eligibility from
one observed response. Require source-backed CSV mappings before preparation.

Keep tenant identifiers, selected filter values, opaque route identifiers,
cookies and authentication headers out of reusable guidance. Execute a lookup
only when the active workflow selects its declared read step through the
existing Core client. Use the exact qualified runtime route and query,
validate the configured HTTPS host and collection, and use configured OAuth
with REST-Framework-Version 9. Never reuse captured cookies or authorization
headers, hardcode an opaque route identifier, or invent a /resources endpoint.
Provider lookup and default rules remain scoped to provider creation.

## Verified Collaboration Message Dropdown Responses

Qualify current response identities, field types, scope and complete pagination
through the declared Core client. An HTTP success or request shape alone is
not message-definition creation evidence or proof that every lookup node is
implemented. Keep raw protected responses private; persist only sanitized
status and evidence references through the selected project workflow.

| Collection | Observed Identity and Display Fields | Observed Context Fields | Pagination Evidence |
|---|---|---|---|
| b2bDocuments | DocumentId and DocumentName are nonempty strings; qualify distinct identities and decimal-string DocumentId values in the current response | DocumentType, Direction, Description, EnabledValue, SimplifiedAvailable and SimplifiedEnabled are strings; this response does not establish DocOperationId | Validate count, limit and offset on every page; require hasMore=false for the complete requested scope |
| b2bExternalMessageDefinitions | ExternalMessageDefinitionId and ExternalMessageDefinitionName are nonempty strings; qualify distinct identities and decimal-string IDs in the current response | DocumentType, MessageType, MessageSubtype, Standard and Version are strings; require every DocumentType to match the requested filter | Validate count, limit and offset on every page; totalResults alone does not establish completeness; require hasMore=false |

DocumentType is a filter context, not a unique document identifier. Keep the
selected DocumentId and DocumentName distinct from it. The presence of
EnabledValue or Simplified fields alone establishes neither their status-code
meaning nor message eligibility. Revalidate current identities and scope;
never retain a fixed response inventory as the available choices.

A document response alone does not establish FSM cell mappings. Public REST
fields DocumentId and ExternalMessageTypeName still need compatible current
template/reference evidence before mapping to DocOperationId or
ExtMessageTypeName. Different-scope export/read results neither prove invalid
records nor authorize equating those fields. Do not request old browser
captures as a substitute for a missing mapping.

## Verified Connection Dropdown Evidence

Use the shared Core REST client with configured OAuth, without browser
cookies or authentication headers. These reference shapes document field
representation and scope limits; current response qualification remains
mandatory. They do not establish completed connection creation or import.

| Collection | Captured Request Scope | Returned Fields and Types | Complete Read |
|---|---|---|---|
| b2bProviders | finder=hcmSearch;bindUserDefined=true,bindInput=; onlyData=true; totalResults=true; limit=25; offset=0 | ProviderId, ProviderName and ProviderTypeMeaning are strings; UserDefinedFlag is boolean; AttchProcessMthd and SpCategory are nullable. Requested projection: AttchProcessMthd,ProviderId,ProviderName,ProviderTypeMeaning,SpCategory,UserDefinedFlag | Read every page; validate distinct identities and names within the qualified scope |
| b2bMessageDefinitions | q=TransformMode='ORA_CMK_XSLT'; limit=25; offset=0 | MessageId, MessageName and MessageStandard are strings; AttachmentsFlag and UserDefinedFlag are booleans. Requested projection: AttachmentsFlag,MessageId,MessageName,MessageStandard,UserDefinedFlag | Read every page; validate distinct identities and names; this broad mode-only shape is not connection eligibility evidence |
| genericLookups lookupCodes child | Validated same-target child path with opaque resource key; onlyData=true; totalResults=true | LookupCode, Meaning, EnabledFlag and ViewApplicationId; qualify enabled/effective values in the selected lookup/application context. LookupType is not returned by the child | Read every page; retain exact parent lookup context and validate code identities and dates |
| b2bDeliveryMethods | finder=hcmSearch;bindProvider=null; limit=25; offset=0 | DeliveryMethodId and DeliveryMethodName are strings; requested projection is DeliveryMethodId,DeliveryMethodName | Read every page; validate distinct identities and names; null-provider scope does not establish selected-provider ownership |

ORA_CMK_CONN_* with Enabled, Disabled and Hold meanings is unrelated to the
qualified connection-status lookup ORA_CMK_EXT_PTNR_MSG_STATUS below. Do not
translate between them or offer the former as connection Status.

A transformation-only message filter is superseded for connection intake by
Corrected Connection Message Scope below. A delivery finder binding Provider
to null does not establish selected-provider ownership. Delivery selection
and lookup apply only to outbound connections; inbound intake skips primary
and alternate delivery lookup and CSV mapping. Standalone delivery-method
management retains its own scope.

Resolve each selected ProviderId, MessageId and DeliveryMethodId uniquely
within its qualified current response and independently verify relationships
and request-to-CSV mappings. A matching name in an export is representation
evidence, not proof of eligibility. A missing message in a different-scope
snapshot does not make it invalid. A boolean UserDefinedFlag true observed
alongside exported UserDefined Y does not establish a universal conversion,
a false encoding, a connection SPUserDefined default, or permission to replace
CSV reference names with runtime IDs.

Use exact source-backed runtime paths through Core after validating the
configured HTTPS host, collection and request scope. Do not persist tenant
identifiers or opaque route keys as reusable endpoints, invent replacement
REST routes, or retain response rows as a permanent choice list. Preserve
pagination and matching checks on every read. Message selection belongs to
connection scope; message creation requires its separately declared operation,
input and approval checks under the task's supported execution boundary.

## Corrected Connection Message Scope

Connection message selection uses both Document and Provider scope. Bind
DocumentId and ProviderId to current verified selections and preserve the
explicit transformation-mode filter through complete pagination. This contract
qualifies read scope, not a fixed choice count or successful import. Keep
cookies, credentials, tenant URLs, opaque keys and selected IDs out of reusable
guidance.

| Parameter | Runtime Value | Source Meaning |
|---|---|---|
| finder | findByProviderOrNullProvider;bindProviderId=<selected ProviderId> | Definitions for the selected provider or with no assigned provider; do not claim exclusive provider ownership |
| q | DocumentId=<selected DocumentId> AND TransformMode='ORA_CMK_XSLT' | The selected Document and explicitly supplied supported transformation mode |
| fields | AttachmentsFlag,MessageId,MessageName,MessageStandard,UserDefinedFlag | Preserve the supplied projection |
| limit / offset | 25 / 0 initially, then advance offset by returned count | Read all pages with unchanged finder, Document and mode filters |

## Connection Transformation Mode Selection

Oracle 26D documents two UI choices: XSLT style sheet and Mapping file. Offer
both when transformation mode is missing; do not ask the user for an internal
code. Availability of Mapping file message definitions for a particular
Document must be established by its qualified scoped lookup, not inferred
from the presence of the UI option.

| Supplied Selection | Runtime Representation | Intake and Lookup Behavior |
|---|---|---|
| XSLT style sheet, XSLT or exact ORA_CMK_XSLT | ORA_CMK_XSLT, verified by the supplied connection GET | Retain the exact code and use the corrected Document/Provider-or-unassigned/XSLT lookup |
| Mapping file or exact ORA_CMK_MAPPING_FILE | ORA_CMK_MAPPING_FILE is this adapter's explicit mapping-file representation | Retain the selection and use the published message-definition collection with the same Document/provider scope and this exact mode filter. Require current schema/query support and verify every returned TransformMode. A complete empty list means no eligible definition, not an unimplemented lookup. Do not substitute XSLT or infer that this connection lookup authorizes creation of mapping-file content |
| Missing or unrecognized selection | No code resolved | Offer XSLT style sheet and Mapping file, ask only for the mode, and do not perform the message-definition GET |

Document, Provider and mode form the Message Definition response context.
For each qualified mode, use its verified code in the Document filter while
retaining the provider-or-unassigned finder and all pagination checks. A
Mapping file selection does not authorize reusing the XSLT request. Runtime
qualification must preserve import validation and approval gates.

Source: [Oracle 26D: Receive a sales contract from Oracle CPQ](https://docs.oracle.com/en/cloud/saas/readiness/scm/26d/proc26d/26D-procurement-wn-f50498.htm)
documents both display labels. The mode codes above are explicit FSCR adapter representations. Product
documentation supplies the two choices; the published message-definition GET
supports TransformMode filtering. Current target schema and returned codes
remain mandatory checks. No internal document is needed by the customer.

## Corrected Connection Status Source

ORA_CMK_EXT_PTNR_MSG_STATUS with ViewApplicationId 0 is the qualified lookup
for connection Status and CSV OverrideStatus. Preserve the exact current
LookupCode and capitalization; do not translate from the unrelated
Enabled/Disabled/Hold lookup. Labels such as Active, Entered, Inactive and
Loopback are not a fixed option inventory: offer only codes returned enabled
and date-effective by the current complete lookup. A code is not ineligible
merely because a historical export omitted it.

Use the declared generic discovery and fresh code read, not a pasted response
cache. No lookup response alone proves completed import. Keep credentials,
audit identities, tenant URLs and opaque resource keys private.

## Creation-Only Reference

The current FSM import graph owns request scope, Run Book input validation
and all declared dropdown resolvers. Obsolete creation-only rule names are
not runtime aliases or prerequisites. Unknown B2B-adapter applicability still
requires clarification; documentation examples are not customer values.
Unchanged exported-package migration is not restricted to a one-provider
creation request.

## Shared Lookup Execution Contract

These resolver definitions are read-only contracts selected by the invoking
task workflow. They do not independently authorize a Fusion request. Before
any GET, complete that workflow's input, environment identity, privilege,
source-route and diagnostic checks. Missing or stale route evidence blocks
execution; do not use browser navigation, captured authentication, guessed
endpoints or another integration as a fallback.

| Lookup Family | Common Skill | Execution Contract |
|---|---|---|
| Application Common generic lookup types and codes | core.fusion-api.apps-common.lookups, references/generic-lookups.md | Select the named generic view; validate its live describe contract and exact lookup identity before discovery and code retrieval. Use the shared REST client below for every GET; never construct an opaque key or switch lookup categories after an authorization failure |
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

## Runtime Route Handoff and Recovery

This task owns reference qualification; the unchanged Core REST client owns
GET transport and authentication. Select and retain the operation/reference
profile at intake before capability qualification. Only for operation
qualify_combined_provider_setup selected with Combined Provider Creation
Qualification at intake, apply Combined Provider Public Capability Bootstrap
below instead of the general root-discovery prerequisite. Other operations,
including operations that reuse this resolver, retain their own capability
contracts; no profile switch after failure is permitted.

For general runtime-resource discovery, require the active project/Run
Book, exact task/catalog identity, configured HTTPS target and metadata-read
privileges. Request only resource names required by the selected operation.
Through core/fusion-api/rest-api-client/scripts/fusion_rest_client.py GET
/fscmRestApi/resources/11.13.18.05/describe with metadataMode=minimal and
REST-Framework-Version 9. Capture responses and errors privately. Only after
HTTP 500/502/503 on that minimal catalog may this task select one lighter
metadataMode=list GET; stop after that read. No write is selected here.

| Binding Situation | Required Behavior | Evidence and Handoff |
|---|---|---|
| Current metadata exposes one exact required resource and link | Evaluate the exact named Resources/resources entry and its canonical/self/describe links. Require a nonempty unique HTTPS path on the configured host and port under /fscmRestApi/, without embedded credentials, query/fragment, traversal or control characters. Reject protocol-relative links, encoded traversal, a different terminal resource name (apart from /describe), malformed or conflicting entries. GET the returned per-resource describe through the existing Core client; validate the owning resolver's fields/types/finders and parent scope before its paginated data read | Keep private origin/path/time/schema evidence; persist only sanitized status. This is a task reference rule, not a new parser, client or cache |
| Current session has a verified same-target binding | Revalidate current host, version, resource and schema evidence before reuse; refresh metadata when any context changes or evidence is stale | No customer runtime URL, browser capture, cookie or technical code is required |
| Required resource is omitted from the metadata | Retain the omission separately from proven absence. For qualify_combined_provider_setup already selected at intake, use only Combined Provider Public Capability Bootstrap below; omission does not block its declared per-resource describe checks. Other public/native profiles retain their own declared prerequisites; general runtime profiles stop with the exact reference/capability gap before preparation | Preserve business inputs. No assisted setup, guessed endpoint, new profile or failed-write fallback |
| Metadata/describe/read is unauthorized, ambiguous, malformed or fails | Classify auth/authz, transport/environment or Fusion API failure and stop that automated read | Do not guess sibling routes, change BOs or infer no data from a failed request |
| Previously dispatched operation is uncertain | Reconcile only through its approved read-only verification route | Metadata qualification never replays a write or changes its approval/executor |

Use current private evidence within the selected run; no repository resource
binding cache or new Core helper is required. All resolver projections, complete
pagination, identity, field and scope checks below remain mandatory.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_cmk_connection_document | Create/add connection, ensure_connection_setup or post_import_verify_connection intake, before Provider; revalidate supplied selections | Selected target host and source-confirmed b2bDocuments runtime route; optional exact Document selection or description search text | For reference_profile public_provider_or_unassigned_fsm explicitly selected before connection intake, use this resolver existing public_message_backed_fsm document/provider/status/full-native-delivery contract, with the separately qualified provider-or-unassigned message resolver below. Preserve all original profiles. For reference_profile existing_connection_reference_fsm selected at intake, consume the invoking shared workflow completed same-target exact-task full export and require one existing direction-specific connection tuple matching exact ServiceProviderName,SPUserDefined,MessageName and TransformMode. Qualify the published b2bMessageDefinitions/describe and complete collection with MessageId,MessageName,DocumentId,DocumentName,DocumentDescription,Direction,DocumentType,TransformMode. Join the exact existing MessageName/TransformMode to one current document/direction/type tuple and require its direction agrees with the existing inbound/outbound CSV. Unknown or changed tuple blocks. For reference_profile public_message_backed_fsm selected at intake, instead GET the documented public b2bMessageDefinitions/describe and complete collection with fields=MessageId,MessageName,DocumentId,DocumentName,DocumentDescription,Direction,DocumentType,TransformMode;onlyData=false;limit=100;offset=0 and every page. Resolve the supplied existing document to one distinct DocumentId/DocumentName/Direction/DocumentType tuple across represented messages; repeated identical tuples are not ambiguity. Use DocumentDescription as readable context. In/Out determine direction; reject inconsistent tuples, Any, no match or an explicit direction conflict. This profile neither probes b2bDocuments nor establishes availability of an unrepresented document. Otherwise retain the existing runtime-route profile below. Through core.fusion-api.rest-api-client, GET b2bDocuments with finder=ExcludeBrazilDocs; fields=Description,Direction,DocumentId,DocumentName; limit=25; offset=0. For description search add q=UPPER(Description) LIKE '%<uppercase search text>%'; use Connection Document Description Search below for construction, browsing and pagination | Description, Direction, DocumentId, DocumentName and pagination | Exact returned DocumentId or one case-insensitive exact DocumentName in the complete current request scope; search text only narrows choices and never selects a row. Require one explicit selected row; Direction In maps to inbound, Out to outbound; Any does not identify a connection direction and cannot pass When the explicit public_message_backed_fsm profile applies, use its qualified source, field and match contract above; never combine incomplete observations from the two profiles or change profile after a write. | Show Description with DocumentName and Direction as readable context; retain DocumentId, exact DocumentName, Description and Direction. Derive inbound/outbound BO from the selected document; never ask for a resolved direction again | selection_required for missing/invalid Document with current scoped choices; blocked for malformed read, unqualified search escaping, Direction Any or conflict with explicit requested direction; preserve other input and never fall back to local DocumentName search |
| resolve_cmk_connection_provider | Connection intake after Document, or standalone delivery-method intake before type validation; provider creation and unchanged imports are not applicable | Selected target host, source-confirmed b2bProviders runtime route and optional existing Provider selection | For reference_profile public_provider_or_unassigned_fsm explicitly selected before connection intake, use this resolver existing public_message_backed_fsm document/provider/status/full-native-delivery contract, with the separately qualified provider-or-unassigned message resolver below. Preserve all original profiles. For reference_profile existing_connection_reference_fsm selected at intake, use the same public provider name/ID/stored-flag and completed-export provider-type contract as public_message_backed_fsm below, additionally requiring the exact existing connection/provider/flag association. Do not use a different provider or infer Direct coverage. For reference_profile public_message_backed_fsm selected at intake, use public b2bServiceProviders/describe and a safely escaped exact-name collection read with ServiceProviderId,ServiceProviderName,UserDefined;onlyData=true;limit=25;offset=0 and complete paging. Require one exact current identity/stored-flag tuple and a matching unique ProviderName/UserDefined/ProviderType tuple in the current full provider-task export from the invoking shared export workflow. This profile supports only an existing Service Provider type, qualifying the exported current code against the existing provider-type contract. It does not infer a Direct provider, attachment mode/category or missing provider fields. Retain exact current name/ID/stored flag and source fingerprints, without a b2bProviders call. Otherwise retain the existing runtime-route profile below. Through core.fusion-api.rest-api-client, GET b2bProviders with finder=hcmSearch;bindUserDefined=true,bindInput=; onlyData=true; totalResults=true; fields=AttchProcessMthd,ProviderId,ProviderName,ProviderTypeMeaning,SpCategory,UserDefinedFlag; limit=25; offset=0 After one selection, use the public provider reference read below to obtain its stored UserDefined representation; this is part of this resolver, not a fallback write route. | ProviderId, ProviderName, ProviderTypeMeaning, SpCategory, AttchProcessMthd, UserDefinedFlag and pagination | Exact returned ProviderId or one case-insensitive exact ProviderName across all pages; retain captured user-defined filter, not the provider-create type/ID-type lookups When the explicit public_message_backed_fsm profile applies, use its qualified source, field and match contract above; never combine incomplete observations from the two profiles or change profile after a write. | Ask which service provider to configure using current ProviderName choices; retain selected ProviderId, exact ProviderName, ProviderTypeMeaning and boolean UserDefinedFlag. Provider Type is derived display context, not another question Retain the verified public name/ID/stored-flag tuple and fingerprint separately from UserDefinedFlag; use the stored flag for SPUserDefined. | selection_required with live provider choices for missing, invalid or ambiguous selection; blocked on incomplete or malformed read. Do not invent a provider or silently broaden the captured filter |
| resolve_cmk_connection_message | Connection intake after Document and Provider; selecting an existing definition only | Verified selected DocumentId and ProviderId, explicit transformation mode, source-confirmed b2bMessageDefinitions runtime route and optional Message Definition | For reference_profile public_provider_or_unassigned_fsm selected before connection intake, execute qualify_cmk_provider_or_unassigned_message below. This explicitly qualifies provider-associated or unassigned definitions; hcmSearch exact-provider results do not establish unassigned eligibility or absence. Keep both existing profiles and their no-profile-switch-after-write boundary. For reference_profile existing_connection_reference_fsm selected at intake, require the exact current existing provider/stored-flag/MessageName/TransformMode association in the full completed provider-task export supplied by the invoking shared workflow. Join its MessageName and mode to the complete current public message namespace and exact selected document/direction, retaining one current MessageId/name tuple. Existing unrelated providers, new message choices, changed documents/modes or missing/multiple joins do not qualify. This profile reads the exact existing relationship rather than claiming a provider-finder no-match was an eligible result; preserve that other API observation separately. For reference_profile public_message_backed_fsm selected at intake, qualify the documented current hcmSearch finder and its bindDirection,bindDocumentId,bindServiceProviderId,bindTransformMode attributes in public b2bMessageDefinitions/describe. GET that same published collection with finder=hcmSearch;bindDirection=<current In or Out>,bindDocumentId=<typed selected DocumentId>,bindServiceProviderId=<typed selected provider ID>,bindTransformMode=<validated exact mode>; fields=AttachmentsFlag,MessageId,MessageName,MessageStandard,UserDefinedFlag,DocumentId,TransformMode;limit=25;offset=0 and complete every page. Preserve all four exact scopes and projection; no broadening, alternate finder or unfiltered selection after a zero result. Require every returned document/mode to match and one exact intended MessageName/ID in that eligible response. The profile uses this explicitly documented four-scope finder rather than treating a two-scope finder result as equivalent. Otherwise retain the existing profile below. Through core.fusion-api.rest-api-client GET the published /fscmRestApi/resources/11.13.18.05/b2bMessageDefinitions/describe, then that collection with finder=findByProviderOrNullProvider;bindProviderId=<selected ProviderId> and q=DocumentId=<selected DocumentId> AND TransformMode=<validated quoted mode>; fields=AttachmentsFlag,MessageId,MessageName,MessageStandard,UserDefinedFlag,DocumentId,TransformMode; limit=25;offset=0. Permit only ORA_CMK_XSLT or ORA_CMK_MAPPING_FILE from the owning mode table; construct queries with safe typed encoding. Preserve the complete scope/projection on every page | MessageId,MessageName,MessageStandard,UserDefinedFlag,AttachmentsFlag,DocumentId,TransformMode and pagination | Require current Document and public-qualified Provider identity before GET. Each returned DocumentId and TransformMode must match the request. Select exact MessageId or one case-insensitive exact MessageName across complete pages. Missing mode offers both labels; code/schema mismatch blocks rather than substituting another mode | Retain selected message identity, name and mode with current Document/provider-or-unassigned response context. Qualification of CSV references remains separate from this read | selection_required for missing/ambiguous selection or complete zero-match, with readable scoped choices. Block schema/query, identity, pagination or read failures. Never remove the Document/provider/mode scope or create a definition implicitly |
| resolve_cmk_connection_status | Connection intake after Message Definition and final prepared-row validation | Selected target host; declared LookupType ORA_CMK_EXT_PTNR_MSG_STATUS, ViewApplicationId 0, effective date and optional status | For reference_profile public_provider_or_unassigned_fsm explicitly selected before connection intake, use this resolver existing public_message_backed_fsm document/provider/status/full-native-delivery contract, with the separately qualified provider-or-unassigned message resolver below. Preserve all original profiles. Through core.fusion-api.apps-common.lookups and core.fusion-api.rest-api-client, GET genericLookups/describe and genericLookups with finder LookupTypeFinder;LookupType=ORA_CMK_EXT_PTNR_MSG_STATUS,ViewApplicationId=0 and onlyData=false; follow the validated same-target lookupCodes child link using the Dynamic REST Execution contract. When new-connection creation explicitly requests retention, or a requested-state comparison explicitly supplies a unit, also apply Connection Retention Unit Qualification below before returning verified. With retention omitted, or a duration-only requested-state comparison, make no additional unit lookup and preserve the original tri-state comparison behavior | LookupCode, Meaning, EnabledFlag, ViewApplicationId, StartDateActive, EndDateActive, DisplaySequence and pagination | Require one exact lookup type/application context; retrieve every page; keep enabled date-effective rows. Match exact code or one case-insensitive exact Meaning. Never use the superseded ORA_CMK_CONN_* response or a stored choice list | Offer fresh Meaning labels and retain exact LookupCode, including capitalization, as Status and CSV OverrideStatus; do not translate Active or restrict choices to codes present in an old export | selection_required with live choices for missing/invalid/ambiguous selection; blocked on lookup identity, context, dates, pagination or read failure |
| resolve_cmk_connection_delivery_methods | Only outbound connection intake after Status; a new outbound connection requires a primary selection, while alternate is optional; inbound follows not_applicable without GET; ensure_connection_setup resolves only explicitly set delivery selections | Verified selected outbound Document and ProviderId, current source-confirmed b2bDeliveryMethods route, supplied primary/alternate selections or tri-state omissions; qualified current metadata | When delivery_evidence_profile predefined_business_event_fsm is selected together with reference_profile public_provider_or_unassigned_fsm before intake, apply Predefined Business Event Connection References below first; its verified result supplies only the bounded primary predefined reference and does not require a delivery-method CSV row. Failure returns blocked without executing another delivery profile. Otherwise For reference_profile public_provider_or_unassigned_fsm explicitly selected before connection intake, use this resolver existing public_message_backed_fsm document/provider/status/full-native-delivery contract, with the separately qualified provider-or-unassigned message resolver below. Preserve all original profiles. For reference_profile existing_connection_reference_fsm selected at intake, use the completed-export name/provider/stored-flag delivery contract of public_message_backed_fsm below, requiring each intended outbound method belongs to the same verified existing provider. When delivery_evidence_profile public_provider_child is explicitly selected at intake for existing-connection reuse, obtain the verified public provider with links and follow its validated same-target deliveryMethods child link. GET its describe and the complete child collection with fields=DeliveryMethodId,DeliveryMethodName;onlyData=false;limit=25;offset=0 and every page. Require current readable attributes, unique identities and one exact requested name. Parent scope is established by the validated child link returned by that uniquely verified provider, retaining its exact provider item/child linkage and source fingerprint. The current child metadata may omit ServiceProviderId; do not request an unsupported attribute or invent a child-level parent value. If a provider identity is returned, require it equals the selected provider by exact decimal identity. Record that ownership came from the public parent-child navigation, not a child ServiceProviderId comparison. This separately selected read profile qualifies that provider-owned existing method even when the full task export omits its row; retain that omission as a distinct observation. It establishes only existing-method ownership for reuse, not complete global absence, shared-method eligibility, new-connection eligibility or verification of method settings. Missing/multiple/wrong-parent or unreadable results block without switching back to another profile after a write. The profile does not require a numeric ID absent from the export, guess shared scope, select another provider method or copy a source connection ID. Inbound skips delivery reads and fields. For reference_profile public_message_backed_fsm selected at intake, outbound named delivery references use the completed same-target full provider-task export obtained by the invoking shared export workflow. Validate task/host/completion/no restrictive criteria, exact delivery headers/types and complete rows. Require one exact DeliveryMethodName/ServiceProviderName/SPUserDefined row for each supplied primary/alternate in the selected verified provider scope. For this name-based FSM profile do not require or invent a DeliveryMethodId absent from the export. Current File Export ownership can be established by that qualified row even when the public child omits it. Do not infer shared/unassigned eligibility from another provider or a blank name. Inbound returns not_applicable without GET and rejects supplied delivery fields through the existing input rule. Otherwise retain the existing runtime-route profile below. Through core.fusion-api.rest-api-client GET b2bDeliveryMethods/describe on the supplied same-target runtime route and require findByProviderOrNullProvider with bindProviderId plus readable DeliveryMethodId,DeliveryMethodName,ProviderId. Then GET b2bDeliveryMethods with finder=findByProviderOrNullProvider;bindProviderId=<selected ProviderId>; fields=DeliveryMethodId,DeliveryMethodName,ProviderId; limit=25; offset=0. Preserve the provider-or-unassigned finder/projection on every page; inbound skips all calls | For predefined_business_event_fsm use only the typed native/public evidence in Predefined Business Event Connection References; no numeric method ID or method-owned parent field. Other profiles: DeliveryMethodId,DeliveryMethodName,ProviderId and complete pagination | For predefined_business_event_fsm apply only its bounded match and final binding rules below; a passing branch returns verified without the ordinary delivery-row/ID match. Other profiles: Require verified selected ProviderId before GET. Read every page and reject duplicate method identities or missing ProviderId attributes. Every nonnull ProviderId must equal the selected provider by exact decimal identity; null denotes unassigned scope, not proof of provider compatibility; qualify eligibility before selection. Resolve primary and alternate independently by exact ID or one case-insensitive exact name in the complete scoped response. A different provider method is invalid. Offer current eligible names. For a new outbound row, a missing primary returns selection_required; alternate omission remains allowed. Reconciliation preserves unspecified existing values When the explicit public_message_backed_fsm profile applies, use its qualified source, field and match contract above; never combine incomplete observations from the two profiles or change profile after a write. | For predefined_business_event_fsm retain its exact primary name, witnessed provider/document/mode scope and evidence fingerprints without inventing a method ID. Other profiles: Retain distinct selected primary/alternate IDs, exact names and returned provider scope bound to target, selected ProviderId, request fingerprint and read time. Do not inherit/default a method or expose IDs as customer input. For ordinary outbound create, require primary selection and offer alternate select/skip only; ensure_connection_setup does not ask about unspecified optional fields | For predefined_business_event_fsm return blocked on its specific missing/incompatible evidence without changing profile or running another method lookup. Other profiles: selection_required for a supplied method not present in the complete provider-or-unassigned scope, with readable current choices; blocked for incompatible describe/finder, unknown/null-string scope, wrong-provider result, incomplete pages or failed read. Never declare provider-specific absence from the superseded hcmSearch;bindProvider=null list, silently pick another method, switch endpoints or create a method. Inbound supplied delivery values remain invalid without GET. For ensure_connection_setup, unspecified or clear slots skip selection reads and questions while any set slot is resolved |
| verify_cmksp_b2b_document_setup_enabled | Automatically before the Service Providers export process is created, or during import preapproval Task Hook validation; do not ask the user to check the feature | Configured host for the source export or destination import; exact code ORA_CMK_B2B_DOCUMENT_SETUP | Route through core.fusion-api.rest-api-client using its references/fusion-rest-api.md and scripts/fusion_rest_client.py; GET /fscmRestApi/resources/11.13.18.05/features with q=FeatureCode='ORA_CMK_B2B_DOCUMENT_SETUP', fields=FeatureCode,FeatureType,EnabledFlag, and onlyData=true | FeatureCode,FeatureType,EnabledFlag | Exactly one same-target item with exact FeatureCode, FeatureType: FEATURE, and EnabledFlag: Y; do not infer enabled from checkedFlag or a catalog snapshot | Redacted host, exact code, enabled flag, read time; confirm the query returns this combination feature in the qualified release | Stop if absent, disabled, unauthorized, malformed, cross-environment, or ambiguous; do not create an export process or upload/import |
| resolve_cmk_provider_types | Provider business-input creation intake and final prepared-provider validation before approval | Selected target host; LookupType ORA_CMK_PROVIDER_TYPES; ViewApplicationId 0 from supplied REST evidence; environment effective date; optional supplied code or meaning | Route through core.fusion-api.apps-common.lookups generic handling and core.fusion-api.rest-api-client: GET /fscmRestApi/resources/11.13.18.05/genericLookups/describe; GET /fscmRestApi/resources/11.13.18.05/genericLookups with finder LookupTypeFinder;LookupType=ORA_CMK_PROVIDER_TYPES,ViewApplicationId=0 and onlyData=false; follow the validated returned lookupCodes child link | Discovery: LookupType, ViewApplicationId, links or returned genericLookups_Id; codes: LookupCode, ViewApplicationId, Meaning, EnabledFlag, StartDateActive, EndDateActive, DisplaySequence; collection count, hasMore, offset | Require one exact lookup type/application context, retrieve every code page, keep enabled date-effective rows; validate an exact case-sensitive LookupCode or exactly one case-insensitive exact Meaning match; never use a stored code inventory, fuzzy match, or first result | Missing input: present all eligible current Meaning labels with stable selection references. Supplied/selected input: retain exact returned LookupCode as resolved Provider Type business input for the qualified CSV mapper | Missing/ambiguous lookup identity, auth/read failure, incomplete pages or incompatible metadata: blocked with sanitized diagnostic. A missing/invalid customer selection follows selection_required with current choices; never use captured results as a fallback |
| resolve_cmk_provider_id_types | Every provider business-input creation intake and final prepared-provider create validation | Selected target host; LookupType ORA_CMK_EXT_PTNR_ID_TYPE; ViewApplicationId 0 from supplied REST evidence; environment effective date; optional supplied code or meaning | Route through core.fusion-api.apps-common.lookups generic handling and core.fusion-api.rest-api-client: GET /fscmRestApi/resources/11.13.18.05/genericLookups/describe; GET /fscmRestApi/resources/11.13.18.05/genericLookups with finder LookupTypeFinder;LookupType=ORA_CMK_EXT_PTNR_ID_TYPE,ViewApplicationId=0 and onlyData=false; follow the validated returned lookupCodes child link | Discovery: LookupType, ViewApplicationId, links or returned genericLookups_Id; codes: LookupCode, ViewApplicationId, Meaning, EnabledFlag, StartDateActive, EndDateActive, DisplaySequence; collection count, hasMore, offset | Require one exact lookup type/application context, retrieve every code page, keep enabled date-effective rows; match exact case-sensitive LookupCode or one case-insensitive exact Meaning. Any provider-specific restriction must come from a declared runtime predicate with verified evidence; absence from a screenshot is not a restriction | Missing/requested input: present all eligible current Meaning labels. Supplied/selected input: retain exact returned LookupCode as resolved ID Type business input for the qualified CSV mapper; preserve returned capitalization | Zero/multiple customer selection matches follow selection_required with current choices. Invalid context/date, incomplete reads or unresolved applicability restriction follow blocked; never guess, default ID Type, or apply a fixed code list |
| check_cmk_provider_duplicate | Provider business-input creation after defaults and before package preparation; rerun for the final immutable provider-create ZIP before import approval | Exact selected target, proposed ProviderName, effective CSV UserDefined, proposed ProviderType, immutable artifact binding when prepared_import, and a fresh completed same-target exact-task populated export when the public read does not establish the complete provider namespace | Through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bServiceProviders/describe, then that public collection with fields=ServiceProviderId,ServiceProviderName,UserDefined;limit=25;offset=0;onlyData=true. Require qualified collection access and complete pagination; do not use the calculated-flag hcmSearch finder The public Service Providers resource is not the complete Simplified Providers namespace: Direct providers are not established by that collection. For Simplified-model provider creation, the invoking Run Book obtains the current exact-task populated export through shared.setup-export.task-level-export before duplicate evaluation, after its feature/identity/privilege/catalog/export-approval gates. Consume that completed export privately as the current provider-name/flag namespace. Verify task, source host, completion, no restrictive export criteria, safe archive, exact provider headers/types and complete parse. This resolver never submits an export itself; missing evidence returns blocked with source_export_required to the invoking preparation workflow, not proof of uniqueness. | ServiceProviderId,ServiceProviderName,UserDefined and complete pagination; current exact-task provider CSV ProviderName,UserDefined,ProviderType, completed export provenance, full-scope criteria and UTC observation | For the supported provider-create UserDefined Y profile, compare exact proposed name plus actual stored UserDefined Y across every applicable current provider CSV row, including Direct and Service Provider types. Also consume the complete public collection for supported Service Provider identities; do not let a public no-match overrule a CSV match or infer Direct absence. Case-only variants require review. Reject duplicate namespace keys, missing required columns/flags, incomplete scope, stale source, cross-host evidence and contradictory observed identities. PartnerId is not the namespace key. Revalidate the final immutable row against current complete namespace evidence at prepared_import; unchanged imports and updates retain their separate operation rules. | unique only after a complete fresh current namespace no-collision result, bound to exact name/flag/type, target/time and final artifact when applicable; raw rows remain private | duplicate for the exact pair in either qualified source; blocked for case ambiguity, unknown/missing flag, incomplete public/model coverage without the completed full-scope source export, failed export/read, schema/permission/paging failure or unsupported create profile. Never infer update, public completeness for Direct, or submit to test uniqueness. |
| verify_cmk_connection_state | Operation post_import_verify_connection or ensure_connection_setup after its input checks and fresh same-host feature validation | Exact target and active Run Book task; fresh resolved Document, Provider, Message and Status; the workflow-qualified current read route. Strict verification additionally requires the completed approved import and immutable row intent; reconciliation requires the new business request fingerprint and tri-state inputs | For ensure_connection_setup with reference_profile existing_connection_reference_fsm selected at intake, consume only the invoking shared workflow fresh completed full same-target exact-task export after validating task/host/completion/no restrictive criteria, safe archive and exact connection headers/types. Match requested PartnerMessageName plus exact selected provider/stored flag and intended direction to one row or complete absence. Join current MessageName/TransformMode to its selected public document/direction tuple. Compare every supplied mapped status/message/mode and outbound primary/alternate name, preserving unspecified fields. No numeric ConnectionId or DeliveryMethodId is asserted when the export does not supply it. More than one identity, stale/incomplete scope, missing requested field mapping or a value difference cannot become verified reuse. Return reconciled with exact per-field business-state coverage and tri-state comparison; other profiles retain their read below. Through core.fusion-api.rest-api-client GET b2bConnections/describe and then GET b2bConnections under the supplied current same-target UI runtime route family /fscmRestApi/rest/rv:<opaque>/en/<version>/. Require model-compatible readable attributes first. For the collection use onlyData=true; fields=ConnectionId,ConnectionName,DocumentId,DirectionCode,ProviderId,MessageId,Status,TransformMode,ApplicationPartnerCodePath,RetentionDuration,RetentionDurationType,DeliveryMethodId,AlternateDeliveryMethodId; limit=25; offset=0. No name search or inferred finder; read every page to hasMore=false | For existing_connection_reference_fsm: exact direction-specific PartnerMessageName,ServiceProviderName,SPUserDefined,MessageName,OverrideStatus,TransformMode and every explicitly requested mapped setting, plus the current public document/direction/message tuple. No absent REST identity is required. For other profiles: All 13 requested attributes, including explicit nulls, and collection count, offset, limit and hasMore | For existing_connection_reference_fsm use its branch-specific exact business-key/field comparison above; differences remain reconciliation evidence for review and cannot become reuse. The following 13-attribute identity contract applies only to the other current-API profiles: Require complete valid pagination and distinct ConnectionId values. Match exact case-sensitive ConnectionName from the approved PartnerMessageName to exactly one row across the full collection. Compare DocumentId,ProviderId,MessageId by exact decimal identity against freshly resolved selections that still agree with the approved intent; DirectionCode to the selected document In or Out; Status to the exact selected lookup code; TransformMode to the explicit requested mode. Compare ApplicationPartnerCodePath to ApplPtnrCodeXpath and retention fields to the approved CSV values; declared blank optional fields must be null or empty, not missing. For outbound compare both delivery IDs or explicit omissions; for inbound require both null/empty. Never use hidden ConnectionStatus or transient display names as substitutes For ensure_connection_setup apply Connection Reconciliation Comparison below instead of the strict approved-CSV comparison; do not require a historical import for a read-only requested-state comparison. The explicit exported-state reuse profile compares its documented business-name relationships and requested fields only; it does not synthesize the 13-attribute API tuple or claim REST ID, credentials or delivery connectivity. | Return verified only for a complete single match with all intended fields equal. Retain private target row and per-field matched/different/not-compared evidence, target, UTC read time, approved ZIP hash and import-result reference; return sanitized comparison counts. Without a complete before-snapshot, claim requested state only, not proven insertion or an unchanged environment For ensure_connection_setup return reconciled with complete scoped absence or one exact current row, field-state comparison coverage and private existing-value evidence; no historical import success claim. | Missing/multiple name matches, any intended field difference, absent attribute, incompatible describe, missing/stale route, incomplete pagination or failed read return blocked with actual failure class. Preserve successful import processing as a separate fact; never resubmit, create another connection, switch endpoint families or treat job success as field verification In ensure_connection_setup, a complete no-match is an absent-state result and an intended set/clear difference is comparison evidence for design review, not a transport failure. Multiple matches and missing required attributes still block. |

## Connection Reconciliation Comparison

| Situation | What Happens |
|---|---|
| ensure_connection_setup reads the declared connection collection | Reuse verify_cmk_connection_state and its complete collection/metadata contract; do not add another endpoint. Select by exact case-sensitive connection Name with the resolved document/provider relationship retained. Zero exact matches after complete pagination is absent; one exact match is existing; multiple exact matches are ambiguous and blocked. A same-name row under another provider or document is an explicit conflict, not absence or permission to append. |
| Comparing a set input | Compare the supplied business value through its existing qualified field mapping: document/provider/message identities, direction code, status code and transformation as already declared; XPath and retention fields through their CSV-to-target mapping. Keep exact comparison for literals and qualified numeric comparison for typed fields. A different supplied value is recorded as an intended difference; no silent substitution. |
| Comparing unspecified optional input | Require the target attribute to be present and record its observed value as preserved, including nonblank XPath, retention or outbound delivery settings. Do not compare it to an empty expected value or count it as an explicit match. Missing target attributes remain schema failures. Independent documented design or relationship failures still block even when a field is unspecified. |
| Comparing clear input | Require field-specific explicit clear intent and record whether the current value is already null/empty or would change. A clear directive is not a request body, an update route or approval. Retain the requested effect for the design review. |
| Direction restrictions | Inbound delivery inputs explicitly set by the customer remain invalid. For reconciliation, any nonempty inbound primary/alternate delivery ID remains a direction-policy conflict even when not supplied; do not treat an unsupported relationship as a preserved optional setting. Outbound unspecified delivery values are preserved, with supplied values resolved normally. |
| Coverage and evidence | Return identity match/absence, each set field as matched/different, each clear field as already-empty/change-required, and each unspecified optional field as preserved. Bind this new requested-state result to target, UTC read time and request fingerprint. Never recalculate a prior approved import's strict comparison using these semantics. Raw target values remain private. |


## Connection Target Verification

Operation post_import_verify_connection is read-only and resumes an existing
completed connection import. It is not create intent. The normal connection
Document, Provider, Message Definition, Status and applicable outbound delivery
resolvers refresh the retained selections first; provider-create resolvers
skip. CMKSP.INPUT_CONTRACT then evaluates only Connection Verification Inputs
and follows verification_ready. It must not request another source export,
prepare a ZIP, apply create defaults or reach Data Loader approval.

### Verification source boundary

Public inbound/outbound guides establish business behavior. The existing
read adapter must independently pass current route, privilege, describe and
response checks. An unpublished implementation archive is not documentation
of a supported API. Retain the declared read route only when its workflow
prerequisites pass; this update does not add an API fallback or a write route.
Qualified package evidence must bind UI selections to imported cell values.

## Selected Provider Delivery Method Scope

The public outbound guide scopes delivery selection to the service provider.
The existing provider-or-unassigned finder is a runtime adapter contract,
not a public business eligibility rule. Require current metadata qualification
and provider compatibility; a null ProviderId alone does not prove that a
method is eligible. Do not consult internal documents to make the selection.

| Situation | What Happens |
|---|---|
| A provider has been selected for an outbound connection | Use resolve_cmk_connection_delivery_methods with that provider-or-unassigned finder. The historical hcmSearch;bindProvider=null capture is not a complete selection list for this provider and must not decide that a requested provider-specific method is missing. |
| Provider, direction or environment changes | Invalidate prior delivery choices, selected IDs and response fingerprints; refresh applicable set selections under the new declared scope. No stale selected method or shared-list evidence may enter package preparation. |
| The requested method resolves | Retain its exact name and current ID for the existing qualified outbound CSV mapper. Provider-specific means returned ProviderId equals selected ProviderId; shared means actual null. Neither name similarity nor appearance in an older export proves current eligibility. |
| Correct scoped read still lacks the requested method | Ask which eligible current method to use, showing readable choices. Do not select a convenient seeded service or change communication type on the customer's behalf. Preserve all other validated business values. |

## Provider Create Duplicate Check

CMKSP.CHECK_PROVIDER_DUPLICATE owns check_cmk_provider_duplicate after provider
defaults have been applied. Its Complete Provider Namespace contract requires
fresh full-scope exact-task export evidence when the public provider collection
does not establish every applicable provider type. A header-only template
supplies schema only; it cannot establish ProviderName plus UserDefined absence.
Use the resolver's qualified sources and retain its current coverage evidence.
At import preapproval, bind a new complete read to the final provider row and
target. Changed ProviderName, UserDefined, environment or ZIP invalidates prior
evidence. This precheck does not reserve the name; Fusion may still reject a
concurrent duplicate, which follows the existing error and no-replay rules.
No provider-create lookup selects an existing provider or asks for provider
selection. Unsupported non-Y create scope blocks without changing supplied
values. Provider updates and unchanged-package imports retain their own rules.

## Connection Lookup Execution

The new connection nodes own exactly their corresponding resolver:
CMKSP.CONNECTION_DOCUMENT uses resolve_cmk_connection_document;
CMKSP.CONNECTION_PROVIDER uses resolve_cmk_connection_provider;
CMKSP.CONNECTION_MESSAGE uses resolve_cmk_connection_message;
CMKSP.CONNECTION_STATUS uses resolve_cmk_connection_status;
CMKSP.CONNECTION_DELIVERY uses resolve_cmk_connection_delivery_methods.
Execute only that resolver at each node, not every row in Live Lookups.
For other BOs and unchanged exported-package imports, each connection node
returns not_applicable without GET or a customer question. Provider Type and
ID Type nodes likewise skip for connection creation, ensure_connection_setup and post_import_verify_connection. The latter operation refreshes only connection selections before the verification branch.

The runtime UI paths are resolved from the supplied captures or validated
same-target links in the selected environment; the opaque rv/version and lookup
keys are not permanent URLs. Keep source references in private runtime context,
validate the configured HTTPS host, use REST-Framework-Version 9 and configured
OAuth through the existing Core client, and never replay captured credentials
or POSTs. Refresh a stale binding through the declared Core discovery step; a failed
request remains its actual failure. Never probe guessed resource paths.

For every list, read all pages, preserve the captured finder/filter/projection,
advance offset by returned count, and stop only when hasMore=false. Reject
duplicate IDs, missing display/identity fields, no-progress pages or malformed
pagination. Present choices using Connection Choice Presentation below. Do not
select the first item, fuzzy-match a final selection, treat totalResults as
completion, or publish raw payloads/internal IDs.
For Documents, preserve the description search scope defined below; a complete
filtered response is not a complete unfiltered collection.
Request only the current missing selection, retaining supplied valid inputs.
Customer selection matches a row; it does not change the captured query scope.

On resume, revalidate changed/time-sensitive selections. Changing Document,
Provider or transformation mode invalidates the Message Definition response,
selection, name filter, display pages and option references; refetch using the
new complete scope before resolving any retained message input. Changing
Provider also invalidates delivery ownership evidence. Preserve the user's text for revalidation rather
than silently replacing values. Direction is derived from the verified selected Document; returned In and Out codes distinguish the two
connection BOs, while the observed Any code has no qualified connection mapping.

## Connection Document Description Search

Document description search uses the existing Core REST client. Its qualified
server-side request scope is
`finder=ExcludeBrazilDocs`, `fields=Description,Direction,DocumentId,DocumentName`,
`limit=25`, `offset=0`, and `q=UPPER(Description) LIKE '%<uppercase search text>%'`.
Only query structure is retained; the captured tenant path, cookies and
credential-bearing headers are excluded. Resolve the runtime path from private,
source-confirmed same-target context as before; do not hardcode the opaque path.

For a name fragment or readable business description, trim outer whitespace,
uppercase the text, surround it with percent signs inside the quoted LIKE
pattern, and pass the complete expression as one `--query` argument to the Core
client. For example, synthetic input `Invoice` yields
`q=UPPER(Description) LIKE '%INVOICE%'`. Let the client URL-encode query
parameters; do not interpolate user text into a shell command or pre-encode it.
This search contract does not establish literal escaping for apostrophes,
percent signs, underscores or control characters. If these occur in search
text, retain the input and stop before GET with the exact escaping-contract
limitation; ask for a plain description fragment rather than guessing SQL
escaping or permitting additional query syntax. Do not correct spelling,
replace spaces with underscores, or turn description text into a DocumentName.

For Browse choices, omit `q` and retain the same finder and field projection.
For an explicitly supplied exact code/name or ID, resolve it against the
complete current response; if needed, use that unfiltered browse scope to
revalidate it. A partial description match, even a single result, still needs
explicit selection. Show Description first, with DocumentName and Direction
so selections remain unambiguous. Preserve an explicit inbound/outbound
request and reject a conflicting selected document as input validation.

Read every page of the chosen query scope, retaining finder, fields and `q`
unchanged and advancing offset by returned count until hasMore=false. Validate
pagination and unique IDs before offering choices. A search result is complete
only for its description filter, not the entire collection. Changing search
text or choosing Browse choices requires a new scoped GET and invalidates
previous document option references and display paging. Keep response context
and search text private. No matches means no matching descriptions in this
scope; offer another description fragment or Browse choices, without a local
DocumentName fallback. Selecting a different Document invalidates downstream
Message Definition choices under Connection Lookup Execution.

## Connection Choice Presentation

This FSCR interaction policy applies only to the five connection resolvers
and their existing selection_required
terminals. It changes choice presentation within the assisted lookup flow;
Provider Type and ID Type intake for provider creation is unchanged.

Document uses Connection Document Description Search above for search, browse,
query refresh and readable labels. The local-filter and no-query-change rules
below apply only to Provider, Message Definition and outbound Delivery Method.

Fusion remains the authority. Local filtering means filtering the complete,
fresh response in the active private lookup interaction, not a Local Lookups
resolver or a stored catalog. Keep the declared REST path, projection, finder,
transformation-mode filter and full pagination unchanged. In particular, do
not put customer search text into bindInput, q or a finder, infer server-side
search support, or change bindProvider=null. This improves selection in chat;
it does not reduce the number of REST pages fetched.

| Situation | What Happens |
|---|---|
| Document selection or description search is requested | Apply Connection Document Description Search; show Description with DocumentName and Direction, use the captured server query, and require an explicit selection |
| Transformation mode is missing or unrecognized | Offer XSLT style sheet and Mapping file before retrieving Message Definitions. Accept their readable labels; apply Connection Transformation Mode Selection and preserve any supplied valid mode |
| Customer already supplies an exact name, ID or current choice reference | Apply the resolver's unique exact-match rule across the complete response first; preserve the exact returned value and continue without asking again. Resolve an option reference only within its original lookup, filter and response context |
| A Provider, Message Definition or outbound Delivery Method is missing and at most 10 choices remain | Show the readable names immediately, numbered with stable choice references, and ask only for that field. Also accept a name fragment to narrow the choices |
| A Provider, Message Definition or outbound Delivery Method is missing and more than 10 choices remain | Ask for the name or part of the name, with Browse choices as an alternative. On Browse choices, show the first 10 names and offer Show more; do not dump the entire collection |
| Customer enters a name fragment or explicitly requests filtering | Trim outer whitespace and apply a case-insensitive literal substring filter to ProviderName, MessageName or DeliveryMethodName as appropriate, within the complete current response. Treat punctuation literally; do not use fuzzy, wildcard or regular-expression matching. Filtering is for display only and never validates a partial name |
| A name filter returns one or more candidates | Show up to 10 matching names and their count; require explicit selection even when only one partial-name match remains. For an exact supplied selection, use the separate exact-match rule instead. Do not derive Direction or commit a reference from search text alone |
| More than 10 candidates match | Sort by case-insensitive display name, then exact display name and internal identity for deterministic ties. Show 10 per display page with a range and total match count, and offer Show more or Refine name. Display pagination is separate from REST pagination; every REST page has already been read |
| Customer asks Show more or changes the filter | Show the next display page, or reset display paging for the new filter, using the same complete response while its scope and freshness remain valid. Keep stable option-to-row references across pages; invalidate old option references when the filter or response changes. Do not refetch solely because the display page or text filter changed |
| A name filter returns no candidates | Say No matching names for this search, then offer a different name or Browse choices. Keep the current field unresolved and preserve all other supplied values. Do not report that no records exist in Fusion, broaden the REST scope or silently create a record |
| Two or more rows share a display name | Keep each distinct identity and use available readable context such as Document Direction, Provider Type or Message Standard to distinguish choices. If context cannot disambiguate the customer's intent, ask for a more precise selection; never collapse duplicates or choose by position |
| Status is missing or invalid | Show all current eligible Meaning labels immediately, ordered by DisplaySequence with a deterministic label/code tie-breaker; do not require a search term. Use resolve_cmk_connection_status for selection and retain the exact LookupCode for OverrideStatus |
| Response is incomplete, stale, cross-environment or its dependency scope changed | Do not offer it as a verified choice list. Follow the resolver failure or refresh rules, invalidate display-page references and revalidate retained inputs against the fresh response |
| Customer supplied several fields together | Resolve them in the declared dependency order and skip questions for values that validate. Ask only the next unresolved field; retain both resolved values and supplied text awaiting revalidation |

Document selection still derives Direction. Message name filtering stays within the
complete Document/Provider-or-unassigned/transformation-mode response; it never
alters the server filters. State this scope before offering choices. A scoped
lookup does not replace final CSV identity and relationship checks.
Delivery filtering applies independently to primary and alternate outbound
selections, preserves applicable skip behavior, and never runs for inbound.
Filtering the provider-unbound delivery response does not prove ownership.
Search text, page cursors and row references are temporary private interaction
state; do not put raw lists, protected values or internal IDs in project logs
or reusable resources. Record only sanitized lookup outcomes and evidence refs.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A Service Providers export or import is requested | Invoke verify_cmksp_b2b_document_setup_enabled automatically for the exact operation host. A feature-state lookup is read-only and needs no user confirmation. Continue only after the result is EnabledFlag: Y; never ask the user whether the feature is enabled. |
| The filtered Features collection has not been validated for this code on the selected pod | Keep the operation blocked; public API documentation supplies the generic read contract but does not prove this code is returned on every pod. Qualify it on the current operation host; another environment's successful read is insufficient |
| The feature response is not a fresh exact-code EnabledFlag: Y from the operation's host | Stop before the first export POST or import upload; recheck after a separate opt-in action |
| Access is insufficient | Request authorized access; do not assign roles or submit an import to test permissions |
| An unchanged completed-export import is requested | Skip business-input dropdown intake and its provider-create validation nodes as not applicable; preserve existing package gates |
| Connection direction is inbound | Skip primary and alternate delivery-method intake, lookup, defaulting and CSV mapping. If delivery-method values are supplied, follow input validation; do not silently change direction |
| Connection direction is outbound and delivery-method values are supplied | Resolve primary and alternate independently using a source-backed read through Core. Use the provider-or-unassigned compatibility evidence from resolve_cmk_connection_delivery_methods; the historical bindProvider=null list is superseded for selection. Do not infer that both methods are mandatory |

## Standalone Delivery Method Lookup Contract

Use the public delivery and outbound connection guides for business rules.
The existing task read adapter must pass its declared route and current
metadata checks independently. A compatible-method comparison does not prove
global name availability; the separate name collision check is FSCR policy.
No REST write route is selected by this guidance.

b2bDeliveryMethodTypes is a documented type-limit resource, not a named
recipient delivery-method creation contract. The public
GET contract lists DeliveryMethodType, DeliveryMethodTypeId and
MaximumMessageSize:
https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/fasrp/op-b2bdeliverymethodtypes-get.html
Use the supplied UI lookup ORA_CMK_DEL_METHOD_TYPE for selection; do not infer
that the type-level limit collection is the UI's eligibility list.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_cmk_delivery_method_type | ensure_delivery_method_setup, create_delivery_method intake/prepared_import or post_import_verify_delivery_method after provider and feature checks | Same-target configured runtime route, supplied UI LookupType ORA_CMK_DEL_METHOD_TYPE, ViewApplicationId 0, current effective date and supplied Type | Through core.fusion-api.apps-common.lookups and core.fusion-api.rest-api-client GET genericLookups/describe then genericLookups with finder=LookupTypeFinder;LookupType=ORA_CMK_DEL_METHOD_TYPE,ViewApplicationId=0; follow only the validated same-target lookupCodes child link under the existing Dynamic REST Execution contract; complete every page | LookupType, ViewApplicationId, LookupCode, Meaning, EnabledFlag, StartDateActive, EndDateActive and pagination | Require one exact lookup context; accept exact code or one case-insensitive exact Meaning among active date-effective codes; no guessed Email code, partial match or fallback lookup | Exact selected LookupCode and Meaning, target, date, request fingerprint and source time | selection_required for missing or ambiguous Type with fresh readable choices; blocked on schema, context, paging or read failure; never use type-limit rows as replacement choices |
| verify_cmk_delivery_method_state | ensure_delivery_method_setup, create_delivery_method business intake or post_import_verify_delivery_method after type selection | Same target, verified selected ProviderId, current type LookupCode, supplied method name, request operation, applicable recipient/attachment/extension/account states and qualified current field evidence | For reference_profile native_fsm_delivery selected at the start of the current validation pass, execute Native FSM Delivery Reuse for ensure_delivery_method_setup, or the existing Native FSM Delivery Preparation and Verification Profile for create/post-import. These native operations consume the invoking shared exporter evidence and do not require discovery, describe or GET of b2bDeliveryMethods. Otherwise preserve the runtime read contract: Through core.fusion-api.rest-api-client GET the bound b2bDeliveryMethods/describe. Require findByProviderOrNullProvider with bindProviderId and readable DeliveryMethodId,DeliveryMethodName,DeliveryMethodType,ProviderId,RecipientEmailId,AttachXmlFlag,EmailAtchUncmpsd. Additionally require and project FileExtension whenever supplied or present in approved intent, and UcmExportDocumentAccount for ORA_UCMFileExport or any requested account comparison. GET the same collection with finder=findByProviderOrNullProvider;bindProviderId=<selected ProviderId>, those exact fields, limit=25, offset=0; preserve scope/projection on every page. An unavailable required optional field blocks this comparison; never retry without it| Native profile: exact current task metadata and the complete twelve-column delivery CSV plus verified parent evidence; compare every represented requested field under Native FSM Delivery Reuse. Otherwise: The seven base attributes plus every conditionally required FileExtension/UcmExportDocumentAccount field, complete pagination and describe metadata| Native profile: apply only the native field/ownership comparisons in Native FSM Delivery Reuse or the strict native creation profile, not the runtime-only account/ID requirements below. Runtime profile only: Require complete pages and distinct method IDs. Match one case-insensitive exact method name in the selected provider-or-actual-null scope. Compare exact type and provider compatibility. Compare supplied email recipient strings without lowercasing mailbox local parts, supplied FileExtension exactly, and requested account exactly; do not infer equivalence from omissions. Compare explicit flags only under source-confirmed response typing. For strict post-import require exact approved provider ownership and every intended mapped field; File Export records the actual account without inferring an undocumented expected constant. Unspecified settings are preserved and never claimed as verified defaults| Native reuse: reconciled with per-field equal/different/preserved evidence or complete absence; no import result or REST ID/account assertion for reuse. Native strict creation keeps its before/after and successful-import requirements. Otherwise: Private identity, per-field matched/different/preserved coverage, complete absence or ambiguity, target/time/fingerprint and operation metadata; the File Export account is an observed output, not a writable CSV value| Ensure/create intake returns reconciled for complete absence or one fully readable match. Strict post-import returns verified only for one matching approved record and complete required comparison coverage. Missing fields/typing, duplicate names/IDs, wrong scope, differences, failed or incomplete reads block the affected comparison; never drop a requested extension/account to claim reuse, POST/PATCH, or infer creation success from describe |

## Connection Retention Unit Qualification

This conditional part of resolve_cmk_connection_status applies to inbound and
outbound new-connection intake and final immutable-row validation, and to an
explicitly supplied unit during requested-state comparison. It does not add a
unit or pair requirement to an existing duration-only comparison. Oracle documents
Retention Duration Unit business meanings; a display label is not a CSV code.
The current public provider child describe must retain the RetentionDurationType
LOV attributeMap from LookupCode and displayAttributes containing Meaning.

| Stage | Read-only contract | Required evidence and result |
|---|---|---|
| Qualify lookup identity | Through core.fusion-api.apps-common.lookups and core.fusion-api.rest-api-client, GET current genericLookups/describe then GET /fscmRestApi/resources/11.13.18.05/genericLookups with finder=LookupTypeFinder;LookupType=ORA_CMK_DURATION_UNIT,ViewApplicationId=0, onlyData=false and REST-Framework-Version 9. This lookup identity was qualified from current generic lookup discovery together with its Retention Duration Unit Meaning, FND application/view context and the provider child LOV attribute mapping; do not derive a field binding from a candidate name alone | Require exactly one row with exact LookupType ORA_CMK_DURATION_UNIT, ViewApplicationId string 0, ApplicationShortName FND, Meaning Retention Duration Unit and a consistent duration-unit description; retain current metadata and identity. Read only its actual same-target lookupCodes child link, including links under @context for framework version 9. Missing or inconsistent identity blocks; never synthesize its opaque key or probe guessed alternatives |
| Resolve current unit | Only after identity qualification, follow its validated returned lookupCodes child link through the existing Dynamic REST Execution contract, preserving the same host/view and exhausting every page | Retain LookupCode, Meaning, EnabledFlag, ViewApplicationId, StartDateActive, EndDateActive and DisplaySequence. Require enabled date-effective rows and exactly one case-insensitive exact business Meaning or case-sensitive exact supplied code. For an English business document only, normalize the explicit singular/plural unit words day/days, week/weeks, month/months and year/years to their singular business labels before exact Meaning matching; this normalizes language, not stored codes. Preserve the original wording and normalization evidence; never fuzzy-match another unit or convert the duration. Retain exact case-preserving LookupCode for CSV RetentionDurationType; never infer D, DAY or Days from prose. Missing identity, attributes, context, dates, schema compatibility or complete pages blocks before preparation |
| Evidence handoff | Keep the explicit business duration/unit, current metadata, qualified lookup identity, selected code/meaning, effective date, request fingerprint and source hashes bound to the same connection and target | Return evidence for the existing native connection mapper. Import remains FSM only. Post-import verification must compare both saved retention cells to the immutable intent; a successful job alone does not verify retention |

Public sources: [Oracle 26D outbound collaboration messages](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/define-outbound-collaboration-messages.html) and [Oracle 26D generic lookups GET](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-fscmrestapi-resources-11.13.18.05-genericlookups-get.html). These document business units and lookup discovery. The exact lookup identity and field correspondence above additionally require current same-target describe and lookup evidence; returned codes are never a stored choice inventory.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.CONNECTION_DOCUMENT | decision | 3 | reference_lookup | verified->CMKSP.CONNECTION_PROVIDER;not_applicable->CMKSP.CONNECTION_PROVIDER;selection_required->CMKSP.CONNECTION_DOCUMENT_REQUIRED;blocked->RETURN_ISSUES | CMKSP.REQUEST_SHAPE | stop | For review_provider_setup, customer_acceptance_prepare, customer_acceptance_execute, customer_acceptance_verify, assisted_delivery_setup, assisted_delivery_verify, assisted_task_setup and assisted_task_verify return not_applicable without GET, runtime-route discovery or dropdown questions; assisted context is confirmed in its own branch. Otherwise: Create/add connection, ensure_connection_setup or post_import_verify_connection: apply Runtime Route Handoff and Recovery before resolve_cmk_connection_document, deriving direction from Document; every other BO and unchanged import skips without GET |
| CMKSP.CONNECTION_PROVIDER | decision | 4 | reference_lookup | verified->CMKSP.CONNECTION_MESSAGE;not_applicable->CMKSP.CONNECTION_MESSAGE;selection_required->CMKSP.CONNECTION_PROVIDER_REQUIRED;blocked->RETURN_ISSUES | CMKSP.CONNECTION_DOCUMENT | stop | For review_provider_setup, customer_acceptance_prepare, customer_acceptance_execute, customer_acceptance_verify, assisted_delivery_setup, assisted_delivery_verify, assisted_task_setup and assisted_task_verify return not_applicable without GET, runtime-route discovery or dropdown questions; assisted context is confirmed in its own branch. Otherwise: Connection intake: execute only resolve_cmk_connection_provider after Document; standalone ensure_delivery_method_setup and create_delivery_method intake/prepared_import also resolve the selected provider without requiring a Document; other BOs and unchanged imports skip |
| CMKSP.CONNECTION_MESSAGE | decision | 5 | reference_lookup | verified->CMKSP.CONNECTION_STATUS;not_applicable->CMKSP.CONNECTION_STATUS;selection_required->CMKSP.CONNECTION_MESSAGE_REQUIRED;blocked->RETURN_ISSUES | CMKSP.CONNECTION_PROVIDER | stop | For review_provider_setup, customer_acceptance_prepare, customer_acceptance_execute, customer_acceptance_verify, assisted_delivery_setup, assisted_delivery_verify, assisted_task_setup and assisted_task_verify return not_applicable without GET, runtime-route discovery or dropdown questions; assisted context is confirmed in its own branch. Otherwise: Connection intake: execute only resolve_cmk_connection_message scoped to the verified Document, Provider-or-unassigned and supplied transformation mode; other BOs and unchanged imports skip |
| CMKSP.CONNECTION_STATUS | decision | 6 | reference_lookup | verified->CMKSP.CONNECTION_DELIVERY;not_applicable->CMKSP.CONNECTION_DELIVERY;selection_required->CMKSP.CONNECTION_STATUS_REQUIRED;blocked->RETURN_ISSUES | CMKSP.CONNECTION_MESSAGE | stop | For review_provider_setup, customer_acceptance_prepare, customer_acceptance_execute, customer_acceptance_verify, assisted_delivery_setup, assisted_delivery_verify, assisted_task_setup and assisted_task_verify return not_applicable without GET, runtime-route discovery or dropdown questions; assisted context is confirmed in its own branch. Otherwise: Connection intake: execute only resolve_cmk_connection_status; other BOs and unchanged imports skip |
| CMKSP.CONNECTION_DELIVERY | decision | 7 | reference_lookup | verified->CMKSP.RESOLVE_PROVIDER_TYPES;not_applicable->CMKSP.RESOLVE_PROVIDER_TYPES;selection_required->CMKSP.CONNECTION_DELIVERY_REQUIRED;blocked->RETURN_ISSUES | CMKSP.CONNECTION_STATUS | stop | For review_provider_setup, customer_acceptance_prepare, customer_acceptance_execute, customer_acceptance_verify, assisted_delivery_setup, assisted_delivery_verify, assisted_task_setup and assisted_task_verify return not_applicable without GET, runtime-route discovery or dropdown questions; assisted context is confirmed in its own branch. Otherwise: Outbound connection intake: execute only resolve_cmk_connection_delivery_methods, including its separately selected predefined_business_event_fsm branch when applicable; inbound skips GET and rejects supplied delivery inputs; other BOs and unchanged imports skip |
| CMKSP.RESOLVE_PROVIDER_TYPES | decision | 8 | reference_lookup | verified->CMKSP.RESOLVE_PROVIDER_ID_TYPES;not_applicable->CMKSP.RESOLVE_PROVIDER_ID_TYPES;selection_required->CMKSP.PROVIDER_TYPE_REQUIRED;blocked->RETURN_ISSUES | CMKSP.CONNECTION_DELIVERY | stop | For review_provider_setup, customer_acceptance_prepare, customer_acceptance_execute, customer_acceptance_verify, assisted_delivery_setup, assisted_delivery_verify, assisted_task_setup and assisted_task_verify return not_applicable without GET, runtime-route discovery or dropdown questions; assisted context is confirmed in its own branch. Otherwise: Provider business-input creation: execute only resolve_cmk_provider_types to resolve supplied or missing Provider Type before input/package qualification; other imports follow not_applicable without GET |
| CMKSP.RESOLVE_PROVIDER_ID_TYPES | decision | 9 | reference_lookup | verified->CMKSP.INPUT_CONTRACT;not_applicable->CMKSP.INPUT_CONTRACT;selection_required->CMKSP.ID_TYPE_REQUIRED;blocked->RETURN_ISSUES | CMKSP.RESOLVE_PROVIDER_TYPES | stop | For review_provider_setup, customer_acceptance_prepare, customer_acceptance_execute, customer_acceptance_verify, assisted_delivery_setup, assisted_delivery_verify, assisted_task_setup and assisted_task_verify return not_applicable without GET, runtime-route discovery or dropdown questions; assisted context is confirmed in its own branch. Otherwise: Provider business-input creation: execute only resolve_cmk_provider_id_types to resolve required ID Type; missing or invalid selections require live choices; unchanged completed-export imports and other BOs follow not_applicable |
| CMKSP.CHECK_PROVIDER_DUPLICATE | decision | 14 | reference_lookup | unique->CMKSP.RESOLVE_PREREQUISITES;not_applicable->CMKSP.RESOLVE_PREREQUISITES;duplicate->RETURN_ISSUES;blocked->RETURN_ISSUES | CMKSP.APPLY_PROVIDER_DEFAULTS | stop | Execute only check_cmk_provider_duplicate after defaults for provider business-input create and final prepared-provider validation; other operations skip without GET |
| CMKSP.RESOLVE_PREREQUISITES | decision | 15 | reference_lookup | verified->CMKSP.CHECK_DELIVERY_DUPLICATE;blocked->RETURN_ISSUES | CMKSP.CHECK_PROVIDER_DUPLICATE | stop | Before task-CSV import approval: execute only verify_cmksp_b2b_document_setup_enabled |
| CMKSP.VERIFY_FEATURE_STATE | decision | 22 | reference_lookup | verified->CMKSP.VERIFY_CONNECTION_STATE;blocked->RETURN_ISSUES | CMKSP.INPUT_CONTRACT | stop | For post_import_verify_connection or ensure_connection_setup: execute verify_cmksp_b2b_document_setup_enabled after the corresponding input checks; no export or import |
| CMKSP.VERIFY_CONNECTION_STATE | decision | 23 | reference_lookup | verified->CMKSP.VERIFICATION_DONE;blocked->RETURN_ISSUES;reconciled->CMKSP.RECONCILE_SETUP | CMKSP.VERIFY_FEATURE_STATE | stop | Execute verify_cmk_connection_state only: strict post_import_verify_connection follows verified or blocked; ensure_connection_setup follows reconciled or blocked under Connection Reconciliation Comparison; no setup mutation or replay |
| CMKSP.DELIVERY_FEATURE | decision | 32 | reference_lookup | verified->CMKSP.DELIVERY_TYPE;blocked->RETURN_ISSUES | CMKSP.INPUT_CONTRACT | stop | Only ensure_delivery_method_setup, create_delivery_method before prepared_import or post_import_verify_delivery_method: execute verify_cmksp_b2b_document_setup_enabled on the selected target; no writes |
| CMKSP.DELIVERY_TYPE | decision | 33 | reference_lookup | verified->CMKSP.DELIVERY_STATE;selection_required->CMKSP.DELIVERY_INPUT_REQUIRED;blocked->RETURN_ISSUES | CMKSP.DELIVERY_FEATURE | stop | Execute only resolve_cmk_delivery_method_type for ensure_delivery_method_setup, create_delivery_method business intake or post_import_verify_delivery_method |
| CMKSP.DELIVERY_STATE | decision | 34 | reference_lookup | reconciled->CMKSP.DELIVERY_RECONCILE;verified->CMKSP.DELIVERY_VERIFIED;blocked->RETURN_ISSUES | CMKSP.DELIVERY_TYPE | stop | Execute only verify_cmk_delivery_method_state using the reference_profile selected before this validation pass; native_fsm_delivery ensure uses Native FSM Delivery Reuse without a b2bDeliveryMethods binding; ensure follows reconciled; strict post-import verification follows verified; no mutation |

## Sources

- [Oracle FSM 26C: migration preparation and setup security](https://docs.oracle.com/en/cloud/saas/applications-common/26c/oafsm/using-functional-setup-manager.pdf), printed pages 41 and 75–79.
- [Oracle 26C security reference](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fammm/Order_Administrator_job_roles.html): provider management and provider web-service access are distinct privileges; one is not proof of the other.
- [Oracle Features collection GET, 26B](https://docs.oracle.com/en/cloud/saas/applications-common/26b/farca/op-fscmrestapi-resources-11.13.18.05-features-get.html): filter by `FeatureCode` and read `EnabledFlag`; the item API recommends querying the collection rather than constructing an item key.
- [Oracle CMK opt-in code reference, 26B](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/cmkapplpartnerssetupvl-3023.html): the view uses `ORA_CMK_B2B_DOCUMENT_SETUP` in its feature-enable test.

## Dynamic REST Execution

The generic provider-type, provider-ID-type and connection-status resolvers
select core.fusion-api.apps-common.lookups with references/generic-lookups.md
and delegate transport to core.fusion-api.rest-api-client under the Shared
Lookup Execution Contract. Sibling pillar examples are not execution adapters.
The selected generic category is established by the declared lookup contract;
do not try other lookup categories or UI endpoints after a failure.

1. Validate the selected Fusion host, privileges and generic lookup identity.
   Inspect the live describe response and use its supported lookup-view context.
   The common reference mentions an older ApplicationCode finder convention;
   do not substitute it for this source-backed contract. Oracle 26D documents
   LookupTypeFinder with LookupType and ViewApplicationId;
   this qualified profile uses application context 0. If the target's
   describe contract differs, stop rather than invent finder parameters.
2. Discover the exact lookup through the documented finder with onlyData=false
   so resource links are returned. Require exactly one matching LookupType and
   ViewApplicationId across the complete discovery result, preserving the finder
   and advancing offset by returned count until hasMore=false. Use the returned
   genericLookups_Id or validated code-child
   link; do not construct an opaque item key by concatenating the lookup type and
   application ID, or reuse a UI rv route.
3. Call the returned code-child route through the Core REST client on the same
   configured HTTPS host. Validate host, resource prefix and lookup identity
   before following a returned URL; reject redirects or links to another host.
   Send REST-Framework-Version: 9. Use onlyData=true, totalResults=true,
   limit=100 and offset=0 for code reads, following hasMore and advancing by the
   returned count until the complete collection is read. Stop on no progress or
   malformed pagination; totalResults is an estimate, not proof of completeness.
4. Offer rows with EnabledFlag Y and inclusive StartDateActive/EndDateActive
   bounds valid on the selected environment's effective date. Reject malformed
   dates, missing identity fields, wrong application context and duplicate codes.
   Sort by DisplaySequence where present, with deterministic label/code ordering
   for ties. Runtime Meaning is the display label; LookupCode is the selection value.
5. When a value is already supplied, validate it against the live collection.
   Exact code matching is case-sensitive. For a Meaning, trim outer whitespace
   and require one case-insensitive exact match. Preserve the returned code;
   never uppercase it, fuzzy-match, select the first row, or ask again for a
   value that has already resolved. If no value is supplied, present the live
   choices and ask the customer to select. ID Type has no inferred default.
6. Record sanitized resolver results, lookup identity, target/effective date,
   read time and evidence references in the selected task run. Captured example
   responses are development evidence only. After final Data Loader approval,
   follow its immutable artifact policy; do not repeat lookups or mutate the
   approved source. Dropdown reads do not authorize an export or import.

Only lookup request identity and REST contracts are fixed. No runtime code/meaning list,
application-specific option whitelist, fallback list or lookup-result cache is
packaged into this skill. All eligible codes in the actual REST response are
available; a reference screenshot is not an option whitelist. If a future
release establishes a further provider-context constraint, author its runtime
predicate and source evidence explicitly rather than copying dropdown results.

## Endpoint Examples

These are requests, not cached dropdown responses. Pass the selected environment
properties and use the shared Core client; no task-local HTTP adapter is required.

```text
python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
  --properties <selected-fusionEnv.properties> --method GET \
  --header "REST-Framework-Version=9" \
  /fscmRestApi/resources/11.13.18.05/genericLookups/describe

python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
  --properties <selected-fusionEnv.properties> --method GET \
  --header "REST-Framework-Version=9" \
  --query "finder=LookupTypeFinder;LookupType=ORA_CMK_PROVIDER_TYPES,ViewApplicationId=0" \
  --query "onlyData=false" --query "totalResults=true" \
  /fscmRestApi/resources/11.13.18.05/genericLookups
```

For ID Type, use the same declared discovery with LookupType
ORA_CMK_EXT_PTNR_ID_TYPE. For code retrieval, use the validated returned
lookupCodes path/link with pagination; never supply a guessed genericLookups_Id.

## Dropdown Sources

- The qualified Provider Type and ID Type read contracts declare lookup
  type names, application context and field names;
  no tenant URL, runtime route ID, credentials, audit values or result inventory
  is retained here.
- Oracle 26D generic lookup discovery and documented finder parameters:
  https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-fscmrestapi-resources-11.13.18.05-genericlookups-get.html
- Oracle 26D generic lookup code resource:
  https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/api-generic-lookups-lookup-codes.html

## Intake Outcome Rules

| Situation | What Happens |
|---|---|
| Provider Type is missing or does not resolve in its own live lookup | Follow selection_required to CMKSP.PROVIDER_TYPE_REQUIRED; show the current Provider Type choices and ask only for that field |
| ID Type is missing or does not resolve in its own live lookup | Follow selection_required to CMKSP.ID_TYPE_REQUIRED; preserve valid Provider Type and other supplied values, and show only the current ID Type choices |
| A value is found only in the other field's lookup | Do not swap fields or treat presence as validation; report the wrong field and ask which intended selection the customer wants |
| A required read fails or the lookup context/response is ambiguous | Follow blocked to RETURN_ISSUES and identify the actual read/metadata failure; do not report intake complete |
| Both applicable dropdown selections have verified resolver evidence | Continue to CMKSP.INPUT_CONTRACT to check remaining required inputs and package-contract readiness; resolved selections remain distinct from import qualification |
| An unchanged completed-export import or another BO is selected | Both provider-dropdown nodes follow not_applicable without reads, then continue to the original input/package gates |

The dropdown nodes are the graph's intake entry points. Their verified outcomes
are prerequisites to validating provider business inputs, not steps hidden behind
the qualified CSV-package gate. Never describe an unverified nonempty string as
validated input. Never tell the customer no more provider details are needed when
a required selection is missing, invalid or unverified.


## Delivery Method Name Collision Contract

Public delivery guidance requires a unique name. The existing complete
name read is FSCR's conservative collision policy, subject to current route,
metadata and privilege checks. It does not assert an undocumented entity key.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| check_cmk_delivery_method_name_duplicate | Only a newly required DM4/DM5 delivery-method create, before preparation and again at prepared_import preapproval; unchanged exported-package imports and other BOs are not applicable | Exact requested DeliveryMethodName, current request/stage, source-confirmed same-target b2bDeliveryMethods route and FSCR unique-name policy | Through core.fusion-api.rest-api-client GET the already bound b2bDeliveryMethods/describe; require readable collection operation and DeliveryMethodId,DeliveryMethodName,ProviderId. Then GET that exact collection with fields=DeliveryMethodId,DeliveryMethodName,ProviderId, limit=25, offset=0 and no provider finder or name filter; follow every page to hasMore=false with the same projection and scope. Stop if that unfiltered read is not supported/authorized; never remove a required security scope or probe another route | Those three attributes plus complete pagination; ProviderId may be explicitly null | Require a complete valid collection and distinct IDs. An exact case-sensitive requested-name match anywhere is a collision, regardless of provider. A differently cased exact normalized-name match returns review rather than asserting server case equivalence. Missing identities, repeated/no-progress pages, or unknown visibility prevent proving absence. A final race is not eliminated by this preflight; preserve any actual import conflict | unique, duplicate or review with sanitized counts, target/time/current request fingerprint and final archive hash at preapproval; raw identities remain private | duplicate, review, unavailable collection privileges/schema/provenance or incomplete reads stop before approval. Never infer global absence from the provider-scoped list, omit a failed page, convert create to update or submit to test uniqueness |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.CHECK_DELIVERY_DUPLICATE | decision | 16 | reference_lookup | unique->CMKSP.VERIFY_DELIVERY_IMPORT_TYPE;not_applicable->CMKSP.VERIFY_DELIVERY_IMPORT_TYPE;duplicate->RETURN_ISSUES;review->RETURN_ISSUES;blocked->RETURN_ISSUES | CMKSP.RESOLVE_PREREQUISITES | stop | At create_delivery_method prepared_import execute only check_cmk_delivery_method_name_duplicate against the exact final row and target. Other BOs and unchanged completed-export imports return not_applicable without a GET |
| CMKSP.VERIFY_DELIVERY_IMPORT_TYPE | decision | 17 | reference_lookup | verified->CMKSP.CHECK_DEPENDENCIES;not_applicable->CMKSP.CHECK_DEPENDENCIES;selection_required->RETURN_ISSUES;blocked->RETURN_ISSUES | CMKSP.CHECK_DELIVERY_DUPLICATE | stop | At create_delivery_method prepared_import execute only resolve_cmk_delivery_method_type and require the final row still matches the current selected type and supported DM4/DM5 preparation profile. Business Event Native Qualification is a restriction, not create eligibility; a new user-defined Business Event row returns blocked. Other BOs and unchanged completed-export imports return not_applicable without a GET |
| CMKSP.DELIVERY_NAME_CHECK | decision | 37 | reference_lookup | unique->CMKSP.DELIVERY_PREPARATION_CHECK;duplicate->CMKSP.DELIVERY_NAME_CONFLICT;review->CMKSP.DELIVERY_NAME_CONFLICT;blocked->RETURN_ISSUES | CMKSP.DELIVERY_TRANSPORT_GATE | stop | Before an absent-method create_needed handoff, execute only check_cmk_delivery_method_name_duplicate; no export, import or mutation |


## Connection Activation Evidence

Business rule source: [Oracle outbound messages](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/define-outbound-collaboration-messages.html)
and [Oracle inbound messages](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/facmm/define-inbound-collaboration-messages.html).
The current read adapter below is an existing FSCR route; the public guide is
not proof of its endpoint, field codes or target availability.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| check_cmk_connection_activation | Before approval of any newly prepared inbound/outbound connection row: first check an existing exact provider/document/message association; only requested Active additionally enters the current active-conflict read. Other BOs and unchanged migration remain not_applicable | Exact target, final ZIP/request fingerprint, selected Document/direction/Provider and complete current status resolver output, including the active label/code correspondence | First consume the selected profile current complete same-target full task export or its already qualified complete connection-state evidence. For a new row, match exact ServiceProviderName/stored flag and MessageName/TransformMode in the intended direction, joined to the selected current public document tuple. An already configured exact association is association_conflict regardless of a different requested connection name or Inactive status; do not import it to discover uniqueness. Missing complete qualified evidence blocks. If no association conflict and the requested status is not Active, return not_applicable for the activation-only step. For Active only, retain the following read: Use only the same qualified b2bConnections collection route already declared by verify_cmk_connection_state, through core.fusion-api.rest-api-client. GET describe and require ConnectionId,ConnectionName,DocumentId,DirectionCode,ProviderId,Status. Read those fields with onlyData=true,limit=25,offset=0 and complete pagination. Do not invent a finder or switch endpoint families | Six attributes and complete pagination | Require distinct IDs and all scope fields. Resolve Active from the current status lookup label/code correspondence, not a hardcoded API code. Within selected Document, direction and Provider, detect another Active connection. Same requested name is a create conflict, not an update. Unknown status typing or incomplete visibility prevents a clear result | clear, conflict or blocked with sanitized coverage and evidence bound to final artifact and target; association_conflict for an already configured exact association, with private matched-state evidence and no write | A conflict requires a separately qualified explicit change plan; never auto-deactivate an existing record. Missing code correspondence, schema, authorization, scope or pages returns blocked. The read performs no import or test transmission An association conflict preserves existing setup and returns reuse/update of that exact supported configuration as the business next choice; it does not authorize rename, silent reuse of strict create, automatic deactivation or another import. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.CHECK_CONNECTION_ACTIVATION | decision | 20 | reference_lookup | clear->CMKSP.IMPORT_GATE;not_applicable->CMKSP.IMPORT_GATE;conflict->RETURN_ISSUES;blocked->RETURN_ISSUES;association_conflict->RETURN_ISSUES | CMKSP.ENFORCE_CHANGES | stop | Before import approval execute check_cmk_connection_activation for any new connection to reject an existing exact provider/document/message association regardless of requested status. Only after that no-conflict result does Active enter its existing current activation check; unchanged imports and other BOs return not_applicable without GET. No deactivation, status substitution or test transmission. |


## Public Stored Provider Reference

[Oracle public provider fields](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bserviceproviders-get.html)
include ServiceProviderId, ServiceProviderName and UserDefined, whose documented
values are Y and N. This read avoids a UI-boolean conversion.

| Situation | What Happens |
|---|---|
| An existing provider has been selected by the owning resolver | Use its selected target and Core client. Require public collection describe support for the three fields. GET /fscmRestApi/resources/11.13.18.05/b2bServiceProviders with a safely escaped exact ServiceProviderName q filter, those fields, onlyData=true and complete pagination. Require one exact-name row, verify its ID agrees with the retained provider identity and require UserDefined Y or N |
| The public tuple matches | Retain exact returned name and stored flag as reference evidence for delivery/connection preparation; do not ask the customer for SPUserDefined or require a second populated export solely for that flag |
| Name/ID differs, several matches exist or the public read fails | Return the actual identity/schema/auth/read failure and preserve the selection. Do not pick Y by default, downgrade a failed read to historical evidence or try a write |


## Message Definition Preparation References

Public sources: [message-definition GET](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bmessagedefinitions-get.html)
and the [26D messaging guide](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/configuring-and-managing-b2b-messaging.pdf).
Generated task exports supply the FSM representation; public REST byte types
are not assumed to be CSV encoding. No runtime Oracle-internal link is used.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_cmk_message_import_references | XSL message-definition create or duplicate at business_intake, source_export or prepared_import | For provider_message_operation_fsm use the source values and stage requirements in Provider Message Operation FSM Reference Lookup; otherwise selected target and exact task, supplied readable Document or retained DocumentId, requested name, external definition and XSL mode, compatible completed same-target populated reference export and separate header-only create template | For reference_profile provider_message_operation_fsm execute Provider Message Operation FSM Reference Lookup below instead of the existing profile; use only its qualified sources and no populated-message operation join. Other profiles retain the following contract. Use core.fusion-api.rest-api-client and same-target qualified describe before each selected collection. First read the existing task-bound b2bDocuments route with fields=DocumentId,DocumentName,DocumentType,Direction and complete paging; resolve one exact ID or unique exact readable name. Then read the task-bound b2bExternalMessageDefinitions route with q=DocumentType=<safely quoted selected type>, projecting ExternalMessageDefinitionId,ExternalMessageDefinitionName,DocumentType and complete paging. Resolve its supplied name uniquely. For the operation join, GET the published /fscmRestApi/resources/11.13.18.05/b2bMessageDefinitions with q=DocumentId=<typed ID> AND TransformMode='ORA_CMK_XSLT';fields=MessageId,MessageName,DocumentId,ExternalMessageTypeName,TransformMode;limit=25;offset=0, complete every page. Also read that public collection unfiltered with the same identity projection to check the requested new name globally; no provider-scoped absence proves name availability. Never change routes after a failure | Document and external-definition identity/context fields, message identity/context and complete pagination; compatible private reference CSV and provenance | For provider_message_operation_fsm apply its complete operation join, match and stage rules below; other profiles retain the following match rule. Resolve current document/direction and exact external name; use that name as ExtMessageTypeName under this explicit profile mapping. Join exact MessageName plus TransformMode from the scoped public rows to unique reference-export message rows. Require matching current DocumentId and one distinct nonblank decimal DocOperationId across the joined rows. Duplicate intent requires the exact selected original. Reject global new-name collisions and case-only ambiguity; never copy an operation ID across environments | ready with target DocOperationId and exact source-qualified ExtMessageTypeName plus source fingerprints; source_export_required if no compatible populated reference exists; choice_required for unresolved business selection; prepared_valid only after the exact final row agrees with refreshed reference evidence | Ambiguous joins, multiple operation values, missing fields or incomplete reads block with precise evidence; never pick the first operation or equate DocumentId and DocOperationId. A reference export request returns to the approved shared export stage, not a direct REST write. If no exportable reference exists, report that execution limitation rather than inventing a target ID |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.MESSAGE_REFERENCES | decision | 11 | reference_lookup | ready->CMKSP.MESSAGE_PREPARATION_READY;prepared_valid->CMKSP.APPLY_PROVIDER_DEFAULTS;source_export_required->CMKSP.MESSAGE_REFERENCE_EXPORT;choice_required->CMKSP.MESSAGE_FIELDS_REQUIRED;blocked->RETURN_ISSUES | CMKSP.INPUT_CONTRACT | stop | For create_external_message_definition with native_fsm_external_definition execute only qualify_cmk_external_definition_references under its native contract. For create_message_definition or duplicate_message_definition for XSL execute only resolve_cmk_message_import_references. Intake readiness hands the selected native definition preparation to the Run Book; source_export_required requests only the owning shared exports. prepared_import follows prepared_valid only with the immutable final row, current reference bindings and complete Native FSM External Definition Inputs or XSL Message Preparation, as applicable |


## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| verify_cmk_message_definition_export_state | Requested native_fsm_export verification after a successfully completed approved FSM message import | Same-target complete before/after exact-task populated exports from the invoking shared export workflow, approved immutable message row and final ZIP/result bindings, current document/external references, field states and private file-text fingerprints | Apply Native FSM Message Verification Inputs. In ORA_CMK_COLLAB_MSG_DEF require exact expected MessageName, DocOperationId, ExtMessageTypeName and TransformMode; zero matching name before and exactly one after. Compare all intended mapped scalar cells and CSV-decoded XsltFile/ValidationPayload text, preserving line endings under the qualified text profile. Require the after message-row multiset to equal the before multiset plus exactly one approved intended row, with no missing, changed or extra rows. Require every unrelated CSV member to have identical headers/types and equal decoded row multisets; expected process/export metadata changes are recorded separately. Evidence retention alone is not an equality result. No reference GET, file enclosure read, export initiation or mutation is performed | verified requested saved state with per-field comparisons, source/final/before/after hashes, processing result and observation time; no numeric REST ID or delivery assertion | Missing/ambiguous name or tuple, field/file differences, incompatible or incomplete exports blocks without replay. Preserve successful processing independently of failed verification |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.MESSAGE_STATE | decision | 12 | reference_lookup | verified->CMKSP.MESSAGE_VERIFIED;blocked->RETURN_ISSUES | CMKSP.INPUT_CONTRACT | stop | Only post_import_verify_message_definition under the existing public saved-state profile with bound completed import and approved intent: execute verify_cmk_message_definition_state. No package preparation or write |


## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_cmksp_runbook_rest_preflight | Only runbook_rest_operation before Run Book payload review and dispatch | Exact selected project/Run Book/task, environment, declared public operation ID, typed business intent and existing reference selections | For create_external_message_definition first execute qualify_cmk_external_definition_references and the Current-Metadata External Definition Inputs; all other operations retain the following contract. Through core.fusion-api.rest-api-client, use only this task's declared reads and the public collection/item selected by its Run Book REST Operations table. Resolve current identity and validated same-host links, then GET the selected operation's describe/metadata. Reuse passing same-operation feature evidence or run the task's declared feature resolver once. For create require current complete name/scope absence; for PATCH require one exact before-snapshot. For message inputs resolve current document/external selections with the owned task reads; no FSM operation-ID join is needed. For provider children verify the selected public provider and its returned child link; do not construct opaque keys. For active-connection changes read current complete scope and retain conflict/dependency evidence. Never call POST/PATCH in this node For File Export creation in the Simplified model, the invoking Run Book selects the existing shared populated exact-task export step before payload review when the public child does not establish complete namespace/readback coverage. Consume its completed private no-criteria before-snapshot, validate exact task/host and CSV shape, and require requested delivery-name absence across the full export. Qualify requested DeliveryMethodName, DeliveryMethodType and optional FileExtension to the exact exported columns plus ServiceProviderName/SPUserDefined. Select the declared File Export Saved-State Evidence step before dispatch; no guessed b2bDeliveryMethods collection is required for this separately selected public operation. An explicitly requested repository account cannot use the export-only verification profile. For create_message_definition with an existing document/external combination, the documented public b2bMessageDefinitions read may qualify that exact combination directly: require describe for MessageId,MessageName,DocumentId,DocumentName,Direction,DocumentType,ExternalMessageTypeId,ExternalMessageTypeName,TransformMode; GET the collection with those fields, onlyData=false, limit=100, offset=0 and every page. Resolve one distinct DocumentId/name/direction/type and one nonblank ExternalMessageTypeId/name association under it. Repeated message rows for the same exact reference tuple are not reference ambiguity; conflicting IDs/types/directions are. Restrict selection to the exact currently represented pair and current verified transform mode; never infer an unused document or external format is supported. Resolve new global name absence from complete current rows. This separately selected public operation does not require the unavailable b2bDocuments route or an FSM DocOperationId. Requests for a new or unrepresented document/external pair retain their own source qualification and stop when missing; no guessed substitute endpoint is permitted. | Exact operation-specific identities, current writable fields/types/nullability and required/default metadata, complete scoped record evidence and intended-field coverage | Require declared method/resource and current target compatibility. Validate all supplied attributes; do not drop a field unsupported by the public/current schema. Server-generated identity must be established by operation metadata; never allocate an application key. A nullable field may clear only when explicit and effective business dependencies remain valid. Preserve active-conflict protection and read-only/uncertain-write boundaries | ready with immutable operation/context/preflight fingerprints and resolved nonsecret field bindings; blocked with precise failure class and evidence | Missing/ambiguous identity, unsupported operation/field, missing secure binding, incomplete pages, privilege/schema/read failure or active conflict blocks before payload approval. A public document is not proof of current privileges or deployed behavior; no alternative write route is a fallback |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.REST_PREFLIGHT | decision | 61 | reference_lookup | ready->CMKSP.REST_GATE;blocked->RETURN_ISSUES | CMKSP.INPUT_CONTRACT | stop | Only the declared runbook_rest_operation: execute verify_cmksp_runbook_rest_preflight. This node performs reads only and cannot approve or dispatch a mutation |


## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_cmksp_runbook_rest_state | Only runbook_rest_verify after the declared dispatch or for safe uncertain-result reconciliation | Exact approved operation/target, private intent and result reference, observed self/child links and before-snapshot; when the declared File Export verification profile applies, the private completed before/after exact-task exports obtained by the invoking shared export workflow | Use core.fusion-api.rest-api-client GET only. Follow the exact validated same-target item link from the current dispatch/selection under the declared public resource, after checking schema. If the result has no item link, use the operation's existing qualified collection read and complete exact-name/scope search; never synthesize opaque keys. For an accepted provider-child create whose returned item GET reports 404, retain that failed GET and reconcile through the same already qualified provider child collection using complete paging. Require one record with the exact returned generated ID, approved name and parent scope, absent from the before-snapshot; compare every intended readable field. A collection match by name alone cannot prove identity or creation. Do not follow another provider, broaden visibility, invent a key, retry the POST or claim the individual-item read succeeded. If the complete same-parent collection is absent, fails or omits required fields, keep verification blocked. Project intended readable fields and identity. For message files follow only the exact same-target XsltFile/PayloadTemplate/MappingFile/MappingFunctionsFile enclosure links or decode returned byte fields according to metadata; never execute XSL or contact the trading partner For an accepted File Export create with no requested repository-account change, consume the declared completed before/after task-export evidence from the invoking Run Book. Validate source host, exact task, completion, no restrictive criteria, safe ZIP, member/metadata integrity and full delivery CSV parse. Compare DeliveryMethodName,DeliveryMethodType,ServiceProviderName,SPUserDefined and supplied FileExtension by exact qualified column names. Require the approved name absent in the complete before namespace and one exact provider/name/flag row after. Verify every requested export-readable field and preserve the failed/incomplete public GET as a separate coverage limitation. This resolver never initiates an export or another mutation. CSV lacks DeliveryMethodId and UcmExportDocumentAccount: do not fabricate identity/account comparisons or treat the accepted response account as saved-state evidence. Requested fields outside this explicit export mapping retain their existing qualified read requirement. | Every intended readable field, explicit nullable values, identity and qualified file comparison; safe result/coverage evidence | Require exactly one identity in the approved scope and compare every supplied set/clear against approved intent. Match file bytes using source-confirmed decoding; do not omit a requested comparison after read failure. Write-only credential values are never fetched or displayed: report accepted secure-binding coverage separately from connectivity. A read alone after an uncertain dispatch proves requested state only, not which write created it The explicit File Export export profile establishes only its named business identity and mapped requested fields; returned REST-ID and repository-account saved values remain unverified. An explicit requested field without a qualified saved read blocks, even if the write was accepted. | verified requested-state coverage, actual action result, target/time and artifact binding; no new mutation or blanket no-changes claim | Absent/ambiguous/different state, missing intended fields, incompatible links or failed/incomplete reads blocks verification without replay. Preserve accepted/partial/uncertain mutation separately; verified configuration does not prove business-document receipt |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.REST_VERIFY | decision | 64 | reference_lookup | verified->CMKSP.REST_VERIFIED;blocked->RETURN_ISSUES | CMKSP.INPUT_CONTRACT | stop | Only runbook_rest_verify: execute verify_cmksp_runbook_rest_state for the exact approved operation. No preparation, approval or dispatch |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_cmk_public_provider_review | review_provider_setup after current test/request input checks, before any reuse claim | Active configured target and Run Book/task binding; optional customer provider name | Through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bServiceProviders/describe, qualify readable ServiceProviderId,ServiceProviderName,UserDefined. Then GET /fscmRestApi/resources/11.13.18.05/b2bServiceProviders with fields=ServiceProviderId,ServiceProviderName,UserDefined;onlyData=true;limit=25;offset=0 and complete all pages. Keep this declared identity projection; never expand delivery children or credential fields. Stop on failed describe/read; no alternate endpoint probe | Three identity/type fields and count,limit,offset,hasMore | Require complete pages, count matching items, correct returned offset, advancing positive limit, distinct exact IDs, nonblank names and stored UserDefined Y or N. Missing name returns selection_required; one exact case-sensitive name returns matched; no exact name with case-only or multiple matches returns selection_required; complete no-match returns not_found. A failed read never means no provider | Private exact provider identity, name and stored type plus target/time/paging coverage; sanitized matched count and result category | not_found is a business no-match, never automatic create. Missing/ambiguous customer name is selection_required. Malformed schema, absent fields, partial pages, auth or transport failure is blocked; no reuse or delivery claim |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.PROVIDER_REVIEW | decision | 90 | reference_lookup | matched->CMKSP.PROVIDER_REVIEWED;not_found->CMKSP.PROVIDER_NOT_FOUND;selection_required->CMKSP.PROVIDER_SELECTION_REQUIRED;blocked->RETURN_ISSUES | CMKSP.INPUT_CONTRACT | stop | Only review_provider_setup: execute resolve_cmk_public_provider_review through the existing Core client. Read identity/type only and stop before any preparation, write, import or reuse assertion |

## Public Provider-or-Unassigned FSM Message Eligibility

The [published message finder](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-b2bmessagedefinitions-get.html)
explicitly distinguishes findByProviderOrNullProvider from hcmSearch. The
former includes unassigned message definitions; an exact-provider search can
legitimately omit them. Select reference_profile
public_provider_or_unassigned_fsm before intake for a new connection using an
existing Service Provider and a current represented document. This reference
profile uses the existing FSM preparation, immutable Data Loader/Task Hook
approval, import and native saved-state verification route. It is not a retry
or a fallback write after a failed mutation. Earlier failed reference attempts
remain separate evidence and do not become successful reads.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmk_provider_or_unassigned_message | Only public_provider_or_unassigned_fsm new connection intake after the existing public document/provider qualifiers | Exact current public DocumentId/name/direction/type, existing provider identity/name/stored flag, explicit supported transformation mode and optional requested message name | Through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bMessageDefinitions/describe. Require the published findByProviderOrNullProvider finder with bindProviderId declared integer, or string with BigInt format. For either representation require the selected provider identity is a positive ASCII decimal integer with no sign, whitespace, exponent or boolean value; serialize its exact validated decimal digits into the finder, never a free-text identifier. Unknown finder typing blocks. Require compatible readable/queryable DocumentId and TransformMode and all projected fields. GET that complete provider-or-unassigned collection with finder=findByProviderOrNullProvider;bindProviderId=<typed current provider ID>;fields=MessageId,MessageName,DocumentId,DocumentName,Direction,DocumentType,TransformMode,ServiceProviderName,AttachmentsFlag;onlyData=false;limit=100;offset=0 and every page | Current message identity/name/document/direction/type/mode/provider-name context and complete pagination | Preserve the exact provider finder on every page and complete that entire provider-or-unassigned scope before selecting by exact DocumentId and TransformMode locally. This avoids relying on an unnecessary combined server filter; keep any earlier filtered zero result as separate evidence. Every returned row must include the projected fields and returned ServiceProviderName must be null/empty for an unassigned definition or exactly the selected provider name. A different nonblank provider is a conflict, not another candidate. Within the complete provider scope select exact DocumentId and TransformMode and require those candidates agree with the already verified DocumentName,Direction,DocumentType tuple. No selection from another document or mode is permitted. Resolve one explicit name/ID, or a delegated non-production fixture from current eligible choices. Record whether the selected definition is provider-associated or unassigned. A duplicate native provider/message association remains blocked by check_cmk_connection_activation before preview, regardless of status/name | One exact eligible current message tuple with finder/target/time/scope fingerprints. Continue with existing current status lookup and, for outbound, the selected delivery resolver: exact provider-owned native delivery-method evidence normally, or the bounded Predefined Business Event Connection References when its delivery_evidence_profile was selected before intake | Missing/ambiguous/inconsistent fields, unsupported finder/query metadata, other-provider rows, incomplete paging or failed reads block before package preparation. Do not remove a filter, infer unassigned status from a missing attribute, create a definition, change provider or switch profiles after a write |

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmk_external_definition_references | create_external_message_definition with native_fsm_external_definition at intake/source_export/prepared_import; historical REST preflight remains inactive under FSM-Only Route Enforcement | Exact configured target, task-declared Native External Definition Resource Qualification below, public document tuple and requested external-format business fields | For native_fsm_external_definition first execute Native External Definition Resource Qualification below; other profiles require their existing selected Core metadata binding. Through core.fusion-api.rest-api-client GET the qualified exact collection with fields=ExternalMessageDefinitionId,ExternalMessageDefinitionName,DocumentType,DocumentTypeDescription,Standard,StandardDescription,Version,MessageType,MessageSubtype,MessageSubtypeIdentificationPath,SenderMessageIdentificationPath,TradingPartnerIdPath,TradingPartnerIdTypePath,ObjectPath,ReferenceObjectKeyPath,POLinePath,UserDefined;onlyData=false;limit=100;offset=0 and every page | Current generated identity/name and complete external-format reference/identification fields, metadata and pagination | Require compatible current attributes, unique positive identities and complete fields/pages. Match the requested neutral document type to the owning current public document tuple and current external records; require a unique consistent type/description. Resolve an explicitly selected existing standard from one exact code/description pair; repeated identical pairs are not ambiguity. Preserve current code strings. Require base/suffixed name absence and no equivalent root/type/standard/version/subtype tuple; apply the existing shared-root discriminator design rule to the complete current scope. For native_fsm_external_definition apply Native FSM External Definition Inputs: bind the one expected _CUST name, explicit custom UserDefined Y and current exact CSV representation; require both name and five-field identification tuple absence across all current flags. Current describe and complete references are read-only evidence; do not require or invoke POST capability. Validate immutable final row against refreshed references at prepared_import. No name/flag/standard default is borrowed from another BO | Qualified current document/standard and immutable field/name/collision evidence with private complete before-snapshot, target/time and schema fingerprint | Unsupported/missing metadata, conflicting references, absent standard/type, existing/ambiguous identity, incomplete pages or failed read stops before body approval. Metadata availability is not server create success; no new standard, guessed endpoint, upsert or alternate route is permitted |


## Native External Definition Resource Qualification

For `native_fsm_external_definition`, the task declares this read-only resource
qualification before any external-format namespace selection. Through
`core.fusion-api.rest-api-client`, GET
`/fscmRestApi/resources/11.13.18.05/b2bExternalMessageDefinitions/describe`
with `REST-Framework-Version=9`, without `metadataMode`. This is an explicit
native FSM reference profile, not a setup write route. The [Oracle 26D metadata
contract](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/Access_Metadata.html)
describes resource-specific metadata access separately from application-wide
catalog access. The specific CMK resource name is qualified against the current
deployment; the general metadata guide does not certify its availability.

Require exactly `Resources.b2bExternalMessageDefinitions`, readable GET support,
and every field projected by `qualify_cmk_external_definition_references`.
Require the generated identity to be an integer or a decimal integer string
with compatible integral metadata; require name and business/path attributes
to be strings. Retain mandatory, nullable and length/precision annotations for
each business attribute mapped by Native FSM External Definition Inputs.
Return those constraints with the exact field-to-native-column correspondence;
the caller must check required business values before preparing the ZIP and
again against the final immutable row. A mandatory MessageSubtype maps to
required DocumentSubtype regardless of whether the XML root is unique. The
shared-root discriminator-path rule is a separate condition and cannot make
this field optional. A metadata-required business value without a qualified
native mapping or conflicting deployed evidence blocks preparation. Do not
apply generated-identity requiredness as a demand for a customer-supplied ID,
derive defaults from existing records or select a subtype on the customer's
behalf without business-choice delegation. Treat optional null business values as null, never as an absent
projected field. Validate the descriptor's collection self link as HTTPS on the
configured origin (default port 443 and explicit 443 are equivalent), no
userinfo/query/fragment, and exact path
`/fscmRestApi/resources/11.13.18.05/b2bExternalMessageDefinitions`.
Only follow that returned validated collection link, retaining its descriptor
fingerprint, environment and qualification time. Complete all pages and the
existing name/identification conflict rules before preparation. The XSL
operation-reference profile may consume this same qualified binding to resolve
its selected external format; it must refresh current reference evidence at
its declared preparation gate.

An application-wide catalog failure or omission is a separate coverage
diagnostic; it does not establish this resource's absence. No cached source
capture, internal reference, local resource binding or customer-supplied
technical URI is a prerequisite. A failed/auth-denied/not-found descriptor,
wrong origin/path, missing resource/GET support, incompatible fields or
incomplete collection stops this profile with the precise failure evidence.
Do not probe other resource names, substitute a UI/REST setup write, or infer
successful creation from readable metadata. The [26D external message definition
guide](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/create-an-external-message-definition.html)
remains the business-field reference; native CSV shape, Task Hook approval,
FSM import and saved-state verification remain mandatory.


## Existing Transformation Export Profile

For export_message_transformation_package the existing
verify_cmksp_runbook_rest_preflight resolves the exact public existing message
self link and current MessageId, DocumentId/DocumentName, Direction,
ExternalMessageTypeId/ExternalMessageTypeName, TransformMode and MessageName.
Require one exact selected tuple, compatible current collection action
exportPackage with MessageId number, lob result, and its validated same-host
/fscmRestApi resource action link. No generated or source-host ID is supplied.
The Run Book owns the one approved action; this lookup never dispatches it.
The existing verify_cmksp_runbook_rest_state for this export operation checks
the returned result against the public byte contract and safe ZIP/member
requirements declared in SKILL.md. Classify absent/malformed/binary-invalid
results as artifact or Fusion failures. Never call messageConversion or send
a PO to test an exported file. Preserve all rejected earlier create evidence.


## Native FSM Delivery Preparation and Verification Profile

Select reference_profile native_fsm_delivery before ensure_delivery_method_setup,
create_delivery_method or post_import_verify_delivery_method. The existing delivery provider/type,
state, duplicate and prepared-import nodes own this profile. Preserve other
GET contracts for their explicitly selected read-only uses; this profile does
not probe another namespace or use a failed read as permission to fall back.

Resolve the exact existing provider through the declared public provider
GET and its exact ServiceProviderName, ServiceProviderId and stored UserDefined
Y/N fields, matching a fresh full provider-task export's ProviderName,
UserDefined and ProviderType. Require the selected provider is user-defined
and is already present in that completed snapshot; this delivery package
never creates its parent. The public provider's current stored Y is direct
field evidence, not a guessed UI boolean conversion. Retain the existing
active date-effective ORA_CMK_DEL_METHOD_TYPE lookup and the selected DM4/DM5 field rules. Business Event Native Qualification below
records the failed DM6 attempt and does not add a create profile.

verify_cmk_delivery_method_state and check_cmk_delivery_method_name_duplicate
consume the completed current full exact-task populated export supplied by
the invoking shared export workflow, with current task/target/completion,
no restrictive criteria, safe ZIP/member and exact schema checks. Match all
names case-insensitively across the complete delivery namespace to prevent
new-name collisions. Require exactly one existing parent name/stored flag;
no first-page or public-child omission proves absence. Inspect the exact
ORA_CMK_COLLAB_MSG_DELV_MTHD row only as inert native data. Empty optional
cells are not evidence of an implicit requested account or endpoint.

Before approval require a qualified exact-task header-only template,
complete business-reference/duplicate evidence and one intended delivery-row
delta; retain every other member unchanged. The existing Core Data Loader
and Task Hook own validation, approval, upload and FSM import.
After actual successful processing, the invoking shared workflow supplies a
fresh complete export. Require zero intended identity rows before and exactly
one after by DeliveryMethodName, ServiceProviderName and SPUserDefined.
Compare every explicitly requested cell and every documented preparation
default; preserve all prior rows as a multiset and the other five objects.
For the bounded File Export negative attachment choice, qualify the existing
AttachXmlFlag string column and its No encoding using the same current
native field correspondence required by DM4. Retain the exact current
template/header/type evidence and, when present, complete same-target
File Export rows as corroboration; do not derive an encoding merely from a
public boolean default or one example. A missing or conflicting current
field correspondence blocks the negative choice. Require the immutable
intended row and fresh saved row to contain exactly No when it was requested;
unspecified stays unspecified and is observed separately. The public delivery
guide places Attach Payload under Email, so report the transport applicability
separately from the saved flag comparison. This does not establish repository
archive contents, uncompressed delivery, business-attachment exclusion or
message processing. No new endpoint, REST write or import executor is selected.
An empty optional cell that represented an unspecified customer choice is not
an explicit request to save a blank. Record the fresh export's value for each
such cell separately, including a value supplied by Fusion during import, and
do not reinterpret that value as customer intent. An explicitly requested
clear or false remains a requested value and must match its qualified native
representation. This verifies the requested native saved settings and strict
creation evidence. CSV does not expose a REST method
ID or repository account; report these as not compared, never fabricate them.
An explicitly requested repository account remains unsupported under DM5 and
blocks before preparation. An unspecified account is not a required input or
acceptance assertion. No saved delivery configuration proves document sending.

### Business Event Native Qualification

The existing type resolver identifies lookup values; it does not establish
whether a delivery type allows user-defined creation. Oracle's public delivery
guide describes the Business Event option and separate OIC setup, but does not
qualify this native create operation. The restriction below comes from the
controlled 26D native FSM test, not from a public statement about every model.
No customer fixture, internal identifier or project artifact is a runtime
prerequisite for applying this task-profile boundary.

Oracle's [26C Gen2 outbound-flow instructions](https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46530.htm)
describe choosing ORA_BusinessEvent while creating a connection, without
creating another delivery method. The latest verified messaging guide is 26D;
this explicit Gen2 selection detail was located in 26C readiness. The source
describes product behavior, not a task-CSV preparation recipe. The following
requirements gate the bounded predefined connection branch below and identify
what remains unqualified outside it. They do not permit a delivery-method
creation retry or replace normal connection import approval.

| Situation | What Happens |
|---|---|
| Recorded DM6 native qualification | Native FSM qualification rejected user-defined Business Event creation with CMK-4215355, CMK_B2B_DELIVERY_DUPE: A delivery method with this type is predefined, so a user-defined one can't be created. The process log completed with errors while the Data Loader dataset still reported in progress. This is failed qualification, not acceptance or proof of rollback. |
| Business Event type interpretation | The test resolved enabled ORA_BusinessEvent with Meaning Business Event through the current lookup. Retain that as scoped observed identity evidence, not a universal hardcoded code or creation permission. For any separately declared current read, keep the resolver's complete active date-effective lookup rules. Do not perform a lookup or experimental import solely to bypass the failed create-profile restriction. |
| Native field correspondence | The shared name/type/parent columns explain how the candidate was represented; their compatibility did not establish that the type accepts a new user-defined method. No supported DM6 creation contract follows from those fields, a unique name, a current header-only template or an enabled lookup row. |
| Create-profile result | New user-defined Business Event creation is blocked under the current FSM profile, before preparation and again at prepared_import. Do not return create_needed, ready_for_preparation, loader_ready or a passed import gate for this request. A different name, provider flag or execution route does not resolve the qualification failure. |
| Failed import and saved-state evidence | Preserve actual processing errors and the original intent. A supported fresh complete before/after comparison is still required to establish saved effects and preservation. Do not infer absence, rollback, a verified new method or unchanged setup from the rejection alone; never automatically replay the import. |
| Existing-method and OIC boundary | This failed create test qualifies neither predefined-method reuse nor connection selection. Those require separately supported identity, ownership and applicability contracts. No OIC subscription, integration runtime state, event processing or receipt was tested. Do not imply that Business Event is unavailable as an Oracle product option. |
| Predefined connection-selection explanation | Recognize Business Event as a predefined connection-delivery choice in the cited Gen2 instructions. Explain that no new user-defined delivery-method row is needed for that product flow. Do not ask for a new delivery-method name, substitute Email or File Export, or equate the product selection label with a qualified DeliveryMethodName CSV value. The create-profile restriction still applies. |
| Native reference and ownership qualification required | Before authoring an executable predefined-method profile, obtain authoritative native FSM import/export mapping or a compatible native reference demonstrating the exact outbound DeliveryMethodName representation and the selected provider relationship. Qualify any shared or unassigned eligibility explicitly; neither a provider-child list nor the absence of a provider-owned delivery row establishes it. Never manufacture a provider, numeric ID, SPUserDefined value or delivery-method row to force a match. Keep lookup type identity distinct from delivery-method reference identity. |
| Native applicability and release qualification required | Bind the source contract to the deployed task, release, Gen2 feature and actual CSV/XML metadata. Establish the supported document, direction, transformation mode and primary or alternate selection scope, plus current reference checks and the existing association-conflict rule. Future-release designs, generic REST CRUD support and another environment's QA outcome do not establish current-target FSM eligibility. An export omission alone does not prove an unpatched environment or global absence. |
| Preparation and acceptance required after qualification | The bounded predefined_business_event_fsm branch below uses the existing assisted connection preparation, shared export and Core Data Loader routes. Prepare only the approved connection row; do not append a Business Event delivery-method row or modify an existing connection. Preserve every other package member and current setup, apply normal approval gates, then compare exact intended saved values and all-object preservation from fresh completed exports. Product documentation, offline tests, UI creation and accepted initiation alone do not establish FSM import acceptance. Outside the bounded branch report the specific capability gap before preparation; OIC setup and delivery remain separate. |


### Predefined Business Event Connection References

This is a branch of resolve_cmk_connection_delivery_methods, not a new resolver,
write route or delivery-method creation profile. A controlled 26D standalone UI
reference exercise and completed exact-task before/after exports established
one Inactive outbound-invoice XSLT connection with DeliveryMethodName
ORA_BusinessEvent, its existing Service Provider name and stored SPUserDefined
Y, while the entire delivery-method object remained unchanged and contained no
matching method row. That verifies native representation and selected-provider
compatibility in this bounded scope. Native FSM import creation remains a
qualification candidate until its own approved import and saved-state test
succeed. No retained customer name, ID or project artifact is a runtime input.

| Situation | What Happens |
|---|---|
| Profile selection and business scope | Select delivery_evidence_profile predefined_business_event_fsm with reference_profile public_provider_or_unassigned_fsm before any lookup. Apply only to a new Inactive outbound Invoice - Outbound connection, explicit XSLT style sheet mode, an existing user-defined Service Provider, the primary predefined Business Event selection and no alternate, retention or attachment-processing changes. The owning current document/provider/message/status resolvers still run. A supplied incompatible scope returns blocked; do not widen it or change profile after a write. Other operations/profiles retain their original contracts. |
| Current evidence and metadata | Consume a current complete same-target provider-task data export from the invoking shared exporter, separately from a completed header-only create template. Qualify exact task, origin, unrestricted scope, safe unique members, CRC, completed EXPORT metadata, native ProcessRelease 11.13.26.10.0, exact outbound eleven-column header/types and existing provider name/stored flag/type. A later release or incompatible model needs renewed qualification. Missing or stale evidence returns blocked or the owning source-export handoff before preparation; this resolver initiates no export or external write. |
| Current provider and reference witness | Retain the unique current public provider identity and matching native ProviderName/UserDefined/ProviderType row from resolve_cmk_connection_provider; require its verified existing Service Provider type and stored Y. In the complete current outbound CSV require an existing reference row with exact same ServiceProviderName/SPUserDefined, DeliveryMethodName ORA_BusinessEvent, TransformMode ORA_CMK_XSLT and Inactive OverrideStatus. Resolve that witness MessageName uniquely in the current complete public message namespace retained by the document resolver. Require its exact DocumentId/DocumentName/Direction/DocumentType/TransformMode tuple agrees with the selected outbound-invoice document/mode. Conflicting or missing reference scopes block. Retain the chosen witness identity/fingerprint privately, without copying its connection name or key into the new row. |
| Requested message eligibility remains independent | The new requested MessageName may differ from the witness only when qualify_cmk_provider_or_unassigned_message independently verifies its current eligibility for the exact same provider/document/direction/mode. Never infer message eligibility from the witness or a broad transformation list. The new name must be absent globally and its exact provider/message/mode association must be unused under check_cmk_connection_activation; an existing association is still a create conflict regardless of a different connection name or Inactive status. |
| Primary method identity and representation | Require the supplied predefined primary choice agrees with the witness native DeliveryMethodName ORA_BusinessEvent. Map that exact value only to outbound DeliveryMethodName. Its reference authority is the current compatible saved connection plus the cited Gen2 predefined-choice contract; no matching provider-owned delivery-method CSV row or numeric DeliveryMethodId is required for this branch. SPUserDefined remains the verified connection-provider flag and never becomes a user-defined-method flag. This proves compatibility only in the witnessed provider/document/mode scope, not global shared eligibility or another provider. Do not run delivery-method create/reconciliation, provider-child or b2bDeliveryMethods probes for this branch. |
| Final preparation and verification binding | At prepared_import revalidate the original selected profile, current witness/reference evidence, exact final request/ZIP fingerprints and all supplied fields. Require one new outbound connection row, DeliveryMethodName ORA_BusinessEvent, retained provider/name/flag, independently eligible MessageName, current Inactive status code and ORA_CMK_XSLT. Keep AlternateDeliveryMethodName, RetentionDuration, RetentionDurationType and AttachmentProcessing empty under this bounded create contract. All other CSVs stay header-only; never append a delivery-method row, copy a source numeric ID, update the witness or relax the association gate. Return verified only for reference qualification; import uses the existing Core Data Loader approval and FSM route. Post-import verification uses post_import_verify_connection_export with all-six-object preservation and reports native import acceptance separately from UI evidence, processing and OIC delivery. |
| Failure and output | Return blocked for wrong target/release/task/type/direction/mode/status/provider, missing witness, unresolved message join, supplied alternate/optional changes or incomplete evidence; preserve business inputs and the specific gap without substituting a method or executor. A passing result supplies exact primary name, provider scope, current public document/message bindings and source/request fingerprints to the existing connection gate. It does not grant import approval, require the implementer to supply internal IDs or imply successful creation. |


## Native FSM Delivery Reuse

This is FSCR verification policy over the existing native export contract.
The [Oracle 26D delivery-method guide](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/define-delivery-methods.html)
defines the provider ownership and transport-specific business fields; the
current exact-task export metadata qualifies their CSV representation.
No public REST creation capability or additional delivery type is inferred.
The following lookup rules belong to verify_cmk_delivery_method_state.

### Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Native profile selected for existing-method reuse | Select native_fsm_delivery before the first reference operation in a new ensure_delivery_method_setup validation pass. Follow the existing feature, provider and active type-code nodes, then the existing DELIVERY_STATE and DELIVERY_RECONCILE nodes. The selection is internal workflow context, not a technical input required from the customer. Do not discover or call b2bDeliveryMethods for this selected native comparison. Preserve the runtime profile for its own explicitly selected uses. A previously failed runtime pass remains failed; record a new pass with its profile selected before reads rather than switching evidence during a failed resolver Enter the existing resolver without a runtime delivery binding. |
| Completed source evidence | Consume the actual populated ZIP supplied by the declared shared export workflow, not a prior matching report or extracted row alone. Validate exact task, configured target, successful completion, complete unrestricted scope, current metadata, safe unique members and CRC, exact twelve-column header/types and source SHA-256. Retain the business request and source fingerprints and export observation time. Reuse an existing completed export only when the owning workflow still qualifies its freshness for this same request and target and no known intervening change invalidates the selected scope. Otherwise stop for a fresh shared export under its existing approval; do not call a substitute endpoint Missing, stale, filtered, wrong-target, incomplete or malformed evidence blocks before reuse. |
| Parent and identity | Use the existing qualified public provider read and matching full native provider row under the Native FSM Delivery Preparation and Verification Profile, retaining exact provider name and stored user-defined flag. Require the existing user-defined-provider scope. Search the complete native delivery namespace for case-insensitive exact requested method names. Require exactly one global candidate and exact ServiceProviderName and SPUserDefined ownership. Do not treat a same-name row under another provider as absence or rely on a numeric method ID unavailable in CSV Duplicate names, wrong parent or flag, and ambiguous parent identity block; zero candidates yields reconciled complete absence for the existing create-needed and global collision gates. |
| Represented requested settings | For the DM4 Email and DM5 standard File Export profiles compare the qualified requested DeliveryMethodName, current DeliveryMethodType code, ServiceProviderName and SPUserDefined. After case-insensitive candidate discovery compare the requested saved name exactly; no silent rename. Business Event Native Qualification does not establish a reuse or create profile; apply its boundary before proposing either. For DM4/DM5 compare a supplied FileExtension exactly. For Email compare supplied RecipientEmailId exactly without lowercasing mailbox local parts; compare explicit XML attachment choice to its qualified Yes or No AttachXmlFlag string. For the bounded DM5 negative choice require the current qualified native No representation and compare AttachXmlFlag exactly to No, retaining its Email-only applicability note separately. File Export positive/clear attachment choices remain unsupported. Preserve omitted settings as unspecified. Every compared value needs its current source-backed field representation; missing headers or unqualified encodings block A complete readable candidate returns reconciled with per-field equality, difference and unspecified coverage; DELIVERY_RECONCILE alone decides reuse or review_required. |
| Unrepresented or unsupported assertions | Keep the selected DM4/DM5 type and unsupported-setting rules. A requested UcmExportDocumentAccount, EmailAtchUncmpsd, credential, unsupported clear or other setting without a qualified native comparison cannot pass through this profile. Retain the exact input and block its comparison. When no account or REST method ID was requested, their absence from the CSV does not block reuse: mark them not compared and do not fabricate a value or claim an observed account. A customer account assertion needs a separately selected qualified read contract before it can be verified Never discard a supplied value, guess a default account, equate blank with false or switch profiles after failure. |
| Reuse result and boundaries | Return reconciled only with the complete native comparison evidence. The existing design rule returns reuse only for one compatible method matching every applicable requested setting and permitted reuse intent. Preserve strict create conflicts, difference review and missing-field blockers. Reuse needs no import, source template, before-absence or import job. Record reused_and_verified only for the represented requested delivery-method scope and its export observation time; no business write, document delivery, repository-account verification, new creation or global preservation proof is implied Existing DELIVERY_REUSED terminal; no new node, approval or mutation. |
| Strict new-creation verification | Keep the existing zero-before and exactly-one-after identity checks, actual successful approved import, every intended mapped value and prior-row multiset preservation. A matching existing method is never proof of creation. This reuse extension does not relax that separate creation path Existing strict post-import requirements unchanged. |


## Public Message Saved-State Verification

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_cmk_message_definition_state | Requested verification after completed approved message import under the existing public saved-state profile | Same target, approved new name, document/external identity, explicit mode, expected scalar values and private source text fingerprints | Use the published b2bMessageDefinitions collection through core.fusion-api.rest-api-client after describe. Use findByMessageName with safely encoded MessageName and complete paging; request MessageId,MessageName,DocumentId,ExternalMessageTypeName,TransformMode and approved readable scalar fields. For supplied file comparison follow only validated same-target enclosure links for XsltFile and PayloadTemplate returned by the exact matched record; never synthesize opaque item keys or fetch external hosts | Current identity, intended scalar/file coverage and same-target enclosure metadata | Require one exact approved name, document, external definition and mode. Compare each intended scalar and file text after source-confirmed transport decoding; preserve expected text without executing XSL. Missing/unreadable file coverage is verification failure, not permission to omit it. Keep processing outcome separately | verified only with complete intended-field comparison, observation time and approved artifact/result binding; no new mutation or reuse claim | Missing/ambiguous identity, differences, unavailable required file links or failed reads block verification. Never repeat import or treat an accepted initiation as completed configuration |


## Provider Message Operation FSM Reference Lookup

The owning resolve_cmk_message_import_references resolver selects this contract
only for provider_message_operation_fsm. Keep its existing outcomes and all
downstream XSL preparation, dependency and immutable-import gates.

| Situation | What Happens |
|---|---|
| Document and global message scope | Through core.fusion-api.rest-api-client qualify the current published b2bMessageDefinitions describe for MessageId,MessageName,DocumentId,DocumentName,Direction,DocumentType,ExternalMessageTypeId,ExternalMessageTypeName,TransformMode and queryability. GET the complete collection with those fields, onlyData=false, limit=100, offset=0 and every page. Resolve the supplied readable document to one consistent current DocumentId/name/direction/type tuple with mode ORA_CMK_XSLT; preserve explicit reference-message selection for duplicate intent. Check the full new-name/mode scope, including case ambiguity. Do not call the unavailable b2bDocuments route or treat this reference read as a write fallback |
| Provider child qualification | Qualify the published b2bServiceProviders collection describe and complete identity collection using fields ServiceProviderId,ServiceProviderName,UserDefined with onlyData=false and complete paging. Resolve the supplied current reference provider exactly, or the already selected provider by retained ID/name/stored flag; do not choose an arbitrary first row. Follow its actual returned same-target messageDefinitions child link, qualify that child's describe and require readable/queryable MessageId,MessageName,DocumentId,Direction,ServiceProviderId,ServiceProviderName,DocumentOperationId,ExternalMessageTypeId. GET its complete collection with those fields and onlyData=false, limit=100, offset=0 and every page. Never construct an opaque key, substitute another parent after failure or follow an external host |
| Exact operation join | Filter the complete child to the selected document ID and direction. Join MessageId,MessageName,DocumentId,Direction,ExternalMessageTypeId to the exact current public ORA_CMK_XSLT tuples. Require the row's ServiceProviderId/name to match its reference parent, positive MessageId/DocumentOperationId and complete match evidence. Resolve the explicit reference message, or require one distinct DocumentOperationId across every eligible joined row for that selected document. Different operation IDs require a meaningful document/version selection; never pick the first. Retain DocumentOperationId as target DocOperationId with reference provider/message fingerprints. This does not make the reference provider the customer's routing provider or assert that its connection was created by the current request |
| Selected external format | Qualify the declared current b2bExternalMessageDefinitions binding and describe, then GET its complete selected-document-type scope with ExternalMessageDefinitionId,ExternalMessageDefinitionName,DocumentType and complete pages. Resolve the exact supplied external name/type, independently of the reference message's existing external format, and retain its exact exported/reference name as ExtMessageTypeName. Missing, conflicting or ambiguous references block; do not create them implicitly |
| Readiness and current-stage result | At intake/business_intake or source_export return ready only with complete qualified business/reference bindings; if the genuine exact-task header-only create template or complete before export is missing, return source_export_required to the invoking shared workflow. At prepared_import require current exact-profile references, complete final native row/provenance, the bound new name/mode/operation/external fields and safe XML-text round-trip, then return prepared_valid. No new numeric ID is allocated. A zero-row custom message export is valid before-state, but does not establish delivered content or insertion success |


## Combined Provider Public Capability Bootstrap

This bounded combined profile specifies FSCR qualification policy, not a claim that every
deployment publishes these resources or supports their metadata identically.
CMKSP.COMBINED_REFERENCES owns these checks through
qualify_cmk_combined_provider_references.

| Situation | What Happens |
|---|---|
| Intake selection | Select operation qualify_combined_provider_setup and Combined Provider Creation Qualification before capability qualification. Bind the exact task, configured HTTPS target, active Run Book, four-row scope, current request and read privileges. This exception belongs only to this operation selected at intake, not every caller of the resolver or other public profiles |
| Bounded public paths | Only the four public resource families in Declared Combined Public Reads below and their qualified returned lookupCodes children are allowed. Use core.fusion-api.rest-api-client with method GET, no body and REST-Framework-Version 9. Resolve the listed paths against the selected configured origin; reject another host/port, version, resource, parent, method, query scope or undeclared endpoint before a call. Do not infer an endpoint from a label or synthesize opaque keys |
| Root catalog omission | Root discovery is not a prerequisite for this profile. An omitted declared resource may proceed to its listed per-resource describe qualification. Omission is not proof of endpoint absence, authorization, schema compatibility or collection completeness. Root discovery diagnostics do not replace describe evidence; a failed describe or collection read cannot be reclassified as catalog omission |
| Describe before collection | Require successful compatible current per-resource describe before the corresponding collection read. Validate the resource-specific readable fields, data types, lengths and required query/finder support, including the lookup child schema as specified below. HTTP success alone is insufficient. A previous filtered features GET does not substitute for describe qualification. No identical provider schema, finder or metadata shape is assumed across resource families |
| General runtime profiles | Retain Runtime Route Handoff and Recovery and their named root-discovery bindings, schema checks and omission stops. This exception does not require or qualify b2bDocuments, b2bProviders, b2bConnections or b2bDeliveryMethods. It cannot be inherited by another operation merely because that operation reuses qualify_cmk_combined_provider_references |
| Remaining gates | Keep feature enabled, exact target/task/Run Book, privileges, all field/type/finder checks, complete pagination, full native before-export and genuine template provenance, collisions, package-local ownership, immutable ZIP/hash, Task Hook and approval gates unchanged. Describes qualify reads only, not creation, export or import permission |
| Failure and review boundary | Stop on failed, unauthorized, ambiguous, malformed or incompatible describe, invalid child link, missing fields, failed reads or incomplete pages. Preserve the actual input validation, catalog mismatch, auth/authz, transport/environment, Fusion API or process timeout classification. No guessed endpoint, broad discovery bypass, scope widening, profile switch after failure, UI fallback, REST write or new retry is permitted. Honor enforced approval restrictions for the current operation; do not replay rejected checks or bypass an enforced rejection. Any live qualification must pass the current workflow's normal automatic approval review |

### Declared Combined Public Reads

All paths below are under /fscmRestApi/resources/11.13.18.05 on the configured
origin. Each collection remains gated by its own successful compatible describe.

| Situation | What Happens |
|---|---|
| b2bServiceProviders | GET /fscmRestApi/resources/11.13.18.05/b2bServiceProviders/describe. Require readable ServiceProviderId,ServiceProviderName,UserDefined with compatible types/lengths. Only then GET /fscmRestApi/resources/11.13.18.05/b2bServiceProviders with fields=ServiceProviderId,ServiceProviderName,UserDefined;onlyData=false;limit=100;offset=0 and every page. Require complete provider identity/name/stored-flag coverage for global collision checks. ProviderType comes from the native export, never an invented public field |
| b2bMessageDefinitions | GET /fscmRestApi/resources/11.13.18.05/b2bMessageDefinitions/describe. Require readable MessageId,MessageName,DocumentId,DocumentName,Direction,DocumentType,TransformMode,ServiceProviderName with compatible types/lengths. Only then GET /fscmRestApi/resources/11.13.18.05/b2bMessageDefinitions with those fields, onlyData=false, limit=100, offset=0 and every page. Preserve the combined resolver's complete scope and existing unassigned outbound PO/inbound invoice XSL eligibility; no b2bDocuments or runtime connection-resource dependency is introduced |
| features | GET /fscmRestApi/resources/11.13.18.05/features/describe. Qualify readable FeatureCode,FeatureType,EnabledFlag and support for the exact FeatureCode q filter and fields projection, not a provider finder or schema. Only then GET /fscmRestApi/resources/11.13.18.05/features with q=FeatureCode='ORA_CMK_B2B_DOCUMENT_SETUP';fields=FeatureCode,FeatureType,EnabledFlag;onlyData=true. Require exactly one matching feature, FeatureType FEATURE and EnabledFlag Y with complete response scope. Missing or incompatible feature describe blocks; neither root omission nor a historical successful filtered GET waives it |
| genericLookups type discovery | GET /fscmRestApi/resources/11.13.18.05/genericLookups/describe. Qualify readable LookupType,ViewApplicationId and current LookupTypeFinder parameters LookupType and ViewApplicationId; record any embedded lookupCodes child metadata separately. This parent describe qualifies type discovery only, not child code reads. Only then GET /fscmRestApi/resources/11.13.18.05/genericLookups separately with finder=LookupTypeFinder;LookupType=<exact declared type>,ViewApplicationId=0;onlyData=false;totalResults=true;limit=100;offset=0 and every page. The only types are ORA_CMK_PROVIDER_TYPES, ORA_CMK_EXT_PTNR_ID_TYPE, ORA_CMK_DEL_METHOD_TYPE and ORA_CMK_EXT_PTNR_MSG_STATUS. Require exactly one matching type/context per complete result. Retain Dynamic REST Execution; do not substitute the older ApplicationCode convention or another lookup view |
| genericLookups returned code child | Follow only the actual lookupCodes child link from the uniquely matched type/context after validating configured HTTPS origin/port, version/resource prefix and exact parent identity. Qualify readable LookupCode,Meaning,EnabledFlag,ViewApplicationId,StartDateActive,EndDateActive and their types from that child's schema in the successful parent describe; if not supplied there, require an actual returned same-parent describe link and its successful compatible response before the code read. Without either qualified schema source, stop; do not append a guessed describe path or construct genericLookups_Id. GET the validated code-child link with onlyData=true;totalResults=true;limit=100;offset=0 and every page. Preserve exact type/application context, effective dates, codes and matching rules; parent finder qualification alone does not qualify child attributes |

### Combined Capability Outcomes

These outcomes describe capability qualification only; continuing a read never
means the package, import or saved configuration has passed validation.

| Situation | What Happens |
|---|---|
| Declared resource omitted; describe compatible | Continue only to the corresponding bounded collection read after all other applicable pre-read gates pass |
| Describe fails | Stop before the collection read; retain the actual failure class and no alternate route |
| Describe unauthorized | Stop before the collection read as auth/authz; do not switch profile or lookup view |
| Describe lacks required fields or finder support | Stop before the collection read with the precise schema or catalog mismatch |
| Undeclared endpoint | Reject before any request; this profile grants no discovery of sibling paths |
| Different operation or scope | Reject the bounded bootstrap exception; retain that operation's own declared capability contract, without profile switching after failure |
| General runtime resource omitted | Stop under the existing general discovery requirements; the bounded exception does not apply |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmk_combined_provider_references | Only explicit qualify_combined_provider_setup before preparation and final immutable Task Hook validation | Current configured host, exact task, four intended rows and fresh full native before-export from shared workflow | For qualify_combined_provider_setup selected at intake, execute Combined Provider Public Capability Bootstrap and Declared Combined Public Reads above before collection reads. Root omission does not block the listed describes; successful compatible per-resource and lookup-child schema qualification remains mandatory. Through core.fusion-api.rest-api-client with REST-Framework-Version 9: features filtered to ORA_CMK_B2B_DOCUMENT_SETUP; published b2bServiceProviders and b2bMessageDefinitions collections plus their describe; genericLookups with LookupTypeFinder for ORA_CMK_PROVIDER_TYPES, ORA_CMK_EXT_PTNR_ID_TYPE, ORA_CMK_DEL_METHOD_TYPE and ORA_CMK_EXT_PTNR_MSG_STATUS then only their actual returned same-target lookupCodes child links. Preserve filters and exhaust all pages. Do not call unavailable b2bDocuments or synthesize opaque keys | FeatureCode,FeatureType,EnabledFlag; provider ServiceProviderId,ServiceProviderName,UserDefined with ProviderType read only from native export; message MessageId,MessageName,DocumentId,DocumentName,Direction,DocumentType,TransformMode,ServiceProviderName; lookup LookupCode,Meaning,EnabledFlag,ViewApplicationId,StartDateActive,EndDateActive and describe field types/lengths | Require exact current feature enabled; absent new provider name in complete public and native scopes, absent new delivery and connection names in complete native scope, exact current Service provider/Generic/File Export/Inactive eligible lookup meanings with current codes; uniquely eligible existing outbound PO and inbound invoice XSL message/document tuples assigned to no provider. Validate schema/lengths and exact case-preserving codes. Match each child to its one package-local intended parent, not a nonexistent live ID | Current exact field/code/document/message bindings, zero collisions, package-local relationship evidence and private source fingerprints | Stop the whole package for missing, ambiguous, mismatched, unreadable or partial evidence. Never substitute a different provider, message, direction, status or write route |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.COMBINED_REFERENCES | decision | 112 | reference_lookup | qualified->CMKSP.COMBINED_PACKAGE;blocked->RETURN_ISSUES | CMKSP.COMBINED_INPUT | stop | For qualify_combined_provider_setup selected at intake execute qualify_cmk_combined_provider_references with Combined Provider Public Capability Bootstrap, Declared Combined Public Reads and Combined Capability Outcomes before collection reads; apply Combined Provider Creation Qualification and all existing applicable field/lookup eligibility checks. Only this bounded operation permits declared public per-resource describes despite root omission; no general runtime-resource prerequisite or profile switch after failure. Package-local provider and delivery are intended references for this bounded profile, never claimed as already saved before import |


## Existing Provider Identifier Update References

Sources: Oracle's [26D CSV modification and import workflow](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/export-and-import-csv-file-packages.html)
and the existing task's Provider CSV Insert and Update Rules. Generic CSV
support does not certify this provider correction before an actual successful
job and saved-state comparison. The invoking Run Book supplies completed
current exact-task data exports and feature evidence from its declared shared
export workflow; this resolver never initiates an export or a business write.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmk_provider_identifier_update | Only update_provider_identifier_fsm with existing_provider_identifier_fsm selected before preparation | Exact configured target/task/active Run Book/current request, literal existing provider name, requested new business identifier, fresh complete provider-task export and current feature evidence | Through core.fusion-api.rest-api-client GET /fscmRestApi/resources/11.13.18.05/b2bServiceProviders/describe then its collection with q=ServiceProviderName='<escaped exact name>';fields=ServiceProviderId,ServiceProviderName,UserDefined;onlyData=true;limit=25;offset=0 and every page. Consume the supplied completed full same-target exact-task native export after safe member/CRC/metadata/header/type checks | One public Service Provider identity/name/stored flag plus the complete native provider CSV row and all-six-object before snapshot | Require one exact public Service Provider and one exact native ProviderName/UserDefined tuple with UserDefined Y and the qualified Service Provider type. Bind public name/flag to the native row; retain the generated ID privately without asking the customer for it. Reject case-only duplicate identities, conflicting types or incomplete scope. ProviderName, UserDefined, ProviderType and PartnerIdType are unchanged. PartnerId is the sole requested nonblank replacement; capture the exact current value and compare the final package against it. No matching row is missing-update-target, never permission to create. Equality returns unchanged rather than a new import. A different requested identifier requires the bounded preparation rules and subsequent actual native import verification | Qualified existing row, exact old/new business identifier, current public identity and lookup/export/request fingerprints, complete before state; ready, unchanged or blocked | Block unavailable metadata, wrong target/task, ambiguous/inactive scope, missing source/feature, unsupported provider type, rename/key/type/flag/extra-field change or incomplete reads. Do not append a provider, guess a new identity, query opaque routes or use REST/UI writes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.IDENTIFIER_UPDATE_REFERENCES | decision | 104 | reference_lookup | ready->CMKSP.IDENTIFIER_UPDATE_PACKAGE;unchanged->CMKSP.IDENTIFIER_UPDATE_UNCHANGED;blocked->RETURN_ISSUES | CMKSP.IDENTIFIER_UPDATE_INPUT | stop | Only update_provider_identifier_fsm executes qualify_cmk_provider_identifier_update. Current identity, before value and all-object scope qualification; no write |

## Provider Task Composition References

This resolver composes existing task-owned read contracts; it introduces no
new REST endpoint, importer algorithm or cross-task orchestration. The invoking
Run Book supplies authoritative local business-input rows/field states and
completed private template/baseline evidence; every saved reference and code
comes from the named existing current-target resolvers below.

Evaluate each existing component contract against its own typed component
projection and stage while retaining the whole composition operation, request
fingerprint and row vector in the authoritative context. Component validation
is not a separate import, a narrower whole-request label, or component approval.

For a Run Book selection to duplicate an Oracle-delivered XSL definition,
qualify the selected public b2bMessageDefinitions describe for XsltFile and
PayloadTemplate attachment attributes and their declared GET action. Through
the same Core client GET the exact selected current message item using its
actual returned canonical/self link, projecting MessageId,MessageName,
DocumentId,DocumentName,Direction,DocumentType,ExternalMessageTypeId,
ExternalMessageTypeName,TransformMode,XsltFile,PayloadTemplate with
onlyData=false. Follow only the selected item's actual same-target enclosure
links for XsltFile and PayloadTemplate, require the metadata-declared attachment
GET and record returned bytes/hashes privately. Do not construct enclosure
paths, invoke transformation-package actions or execute the stylesheet/sample.
Bind the exact existing external parent and document operation independently.
Copy only reviewed nonsecret static transformation/sample content into separate
technical attachments; tenant/customer values must remain private. A missing
link, unreadable content or incompatible XML is a content-preparation blocker,
not permission to export through another adapter or reuse historical test data.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| qualify_cmk_provider_task_composition | Only qualify_provider_task_composition_fsm after COMPOSITION_INPUT | Exact task/target/active Run Book, current business requirement/attachment hashes, nine intended business rows and separate XSL/sample content, full native before and header-only template from shared export | Through the existing Core client execute the feature/provider/type/status/native-scope reads declared by qualify_cmk_combined_provider_references for the provider/delivery/connection components, retaining each requested document and direction rather than its old bounded PO/invoice count. Execute qualify_cmk_external_definition_references under native_fsm_external_definition for the independent external row. Execute resolve_cmk_message_import_references under the originally selected provider_message_operation_fsm or export-join profile for the independent message and its already-saved external parent. Keep all original same-target metadata, actual child-link, projection and complete-page requirements; no b2bDocuments fallback or new endpoint discovery | Existing resolvers' typed current fields/codes, saved document/message/external identities, stored provider flag, private complete native namespace and exact template schema | Apply every component's lookup/default/design condition individually and retain a per-row result. Require exact current Service provider, Generic, File Export and Inactive codes. For four connections resolve one eligible already-saved message/document/direction tuple for each requested scope; do not assume customer scope from supplier scope. Require both new delivery names absent globally and all other create identities/tuples absent in their complete scopes. Verify the exact existing external parent of the new message and reject a match to the package-new external name; reject connections to the package-new message name. Local joins are restricted to intended provider name/flag and same-provider primary/alternate names; duplicate, case-ambiguous or cross-provider names block. Do not reclassify missing saved references as local parents | Nine per-row qualification results, every code/reference/source/request fingerprint and explicit intended provider/delivery joins; source_export_required only for absent current native source evidence | Any failed, incomplete, unsupported, ambiguous or colliding component blocks the complete package before upload. Retain all passing results without claiming creation, do not drop a component or substitute a different document/parent, and do not retry a mutation |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.COMPOSITION_REFERENCES | decision | 401 | reference_lookup | qualified->CMKSP.COMPOSITION_PACKAGE;blocked->CMKSP.COMPOSITION_ISSUES | CMKSP.COMPOSITION_INPUT | stop | Only qualify_provider_task_composition_fsm: execute qualify_cmk_provider_task_composition using all existing typed component sources and the Provider Task Composition dependency firewall. Graph readiness or a template alone is insufficient |
