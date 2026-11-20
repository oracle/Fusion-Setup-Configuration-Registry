# Service Providers Create/Update Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Review requested business effect | Confirm create versus update and the exact identity of the selected BO; for a connection create, preserve direction, selected provider/message references and append intent |
| 2 | Review package changes | Reject duplicate creates, ambiguous updates, and undocumented effects on existing or related rows |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Preparing create/update task data | Blocking | | Duplicate create key, ambiguous update target, or undocumented changes to existing records | Review all added/changed/affected records; preserve unrelated data and require exact update scope | No |
| Preparing a precisely scoped provider, delivery-method, message-definition or connection request | Blocking | | Package adds an unrequested BO or applies another object's defaults or mappings | Preserve the selected object and supplied values; a provider-only request does not authorize connection or partner-property setup. Return broader scope decisions to the invoking planner | No |
| Preparing a message outside the XSL Message Preparation profile or a connection whose mode fails current qualification | Blocking | | Required field mappings or the mode-specific lookup contract remain unresolved | Retain the requested definition or transformation mode and disclose the exact authoring gap; do not substitute XSLT, infer mappings from CSV inventory, or invent an API route | No |

## Setup Reconciliation Policy

CMKSP.RECONCILE_SETUP owns this FSCR reconciliation policy; read mechanics and coverage are
owned only by ora_reference_lookups.md.

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| ensure_connection_setup finds one identity with every supplied setting satisfied | Informational | verify_cmk_connection_state | None; unspecified optional values are preserved and no independent documented design conflict is present | Return reuse with supplied fields verified and unspecified settings retained. Do not ask whether to clear a nonblank existing XPath merely because its attachment cell is blank; do not prepare/import an unchanged row | No |
| ensure_connection_setup finds no matching identity | Informational | verify_cmk_connection_state | None only after complete absence and reference checks | Return create_needed to the invoking Run Book for the existing explicit connection-create workflow. For a new row, unspecified optional inputs become empty under the existing creation contract, never inherited from an unrelated record; required or provider-dependent inputs still need validation. This terminal is not import approval | No |
| Existing connection differs on an explicitly set value or a requested clear | Blocking | verify_cmk_connection_state | The requested state requires changing an existing connection | Return review_required with a concise current/requested difference list. Require a qualified update/clear contract for the exact field and normal immutable-artifact approval before any change. If no route exists, report that specific change as unsupported; do not resubmit create or invent a direct PATCH | No |
| Preserved setting conflicts with a documented direction or business-design rule | Blocking | verify_cmk_connection_state | A documented rule is violated by the effective existing configuration | Explain the specific business impact and ask only for the required decision. Unspecified does not waive independent design rules or permit an unsafe relationship | No |
| Read evidence is incomplete or ambiguous | Blocking | verify_cmk_connection_state | Absence, identity or requested-state coverage cannot be established | Preserve inputs and return the actual lookup/schema failure; do not infer reuse or create | No |


## Delivery Method Reconciliation

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Explicit create-another intent finds an existing named method | Blocking | verify_cmk_delivery_method_state | Requested strict create conflicts with an existing identity | Return review_required; preserve strict create intent and ask for a different business name only when a new independent setup is required | No |
| One compatible method matches all supplied settings and intent permits reuse | Informational | verify_cmk_delivery_method_state | None after complete current comparison | Return reused_and_verified for the delivery-method scope and preserve unspecified settings; no import or approval for a no-op | No |
| Complete provider-scoped read proves method absent | Informational | verify_cmk_delivery_method_state | None only as an absent-state observation, not proof of global name availability or preparation readiness | Follow create_needed to the separate global name check and selected DM4/DM5 preparation-scope check. Only their passing results may hand off to assisted Run Book preparation; retain customer choices and report an actual blocked setting without substituting a channel | No |
| At prepared_import or after DELIVERY_NAME_CHECK for a new delivery method under the selected preparation profile | Blocking | check_cmk_delivery_method_name_duplicate | Global delivery-name collision evidence is absent or a conflicting name is found; absence in the selected provider-or-unassigned collection is insufficient | Public delivery guidance calls for a unique name. FSCR conservatively requires the existing complete name collision check before preparation; this is not a public claim about database keys. Do not treat a different provider as a separate name namespace, infer case normalization from the key, or silently convert create to update | No |
| Existing method differs on supplied recipient, type or flags | Blocking | verify_cmk_delivery_method_state | Requested state needs an unqualified update or clear | Return review_required with business differences; do not reuse merely because name matches, append a duplicate or overwrite a shared method | No |
| Strict post-import verification | Blocking | verify_cmk_delivery_method_state | Any required field is absent, different or unverified | Report operation processing separately from saved-state verification; no mutation replay | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.ENFORCE_CHANGES | decision | 19 | design_enforcement | passed->CMKSP.CHECK_CONNECTION_ACTIVATION;blocked->RETURN_ISSUES | CMKSP.CHECK_DEPENDENCIES | stop | Before task-CSV import approval: apply Design Rules to the exact requested BO and package; unchanged completed exports pass preparation-only policy as not applicable |
| CMKSP.RECONCILE_SETUP | decision | 25 | design_enforcement | reuse->CMKSP.REUSE_DONE;create_needed->CMKSP.CREATE_NEEDED;review_required->CMKSP.REVIEW_REQUIRED;blocked->RETURN_ISSUES | CMKSP.VERIFY_CONNECTION_STATE | stop | Only ensure_connection_setup: apply Setup Reconciliation Policy to current comparison evidence; no write or import approval |
| CMKSP.DELIVERY_RECONCILE | decision | 35 | design_enforcement | reuse->CMKSP.DELIVERY_REUSED;create_needed->CMKSP.DELIVERY_TRANSPORT_GATE;review_required->CMKSP.DELIVERY_REVIEW_REQUIRED;blocked->RETURN_ISSUES | CMKSP.DELIVERY_STATE | stop | Only ensure_delivery_method_setup or strict create_delivery_method business intake: apply Delivery Method Reconciliation, preserving strict create intent; no mutation or import approval |


## Source

User requirement: create records through FSM while preserving unrelated setup
and binding approval to the final reviewed artifact. This is FSCR policy, not
an assertion of undocumented Fusion merge behavior.

The task-scope and unresolved-contract rules above preserve the former parent
CMK Business-Goal Journey policy in this owning design resource. They are FSCR
scope safeguards, not new Oracle required fields or cross-task transitions.


## Delivery Transport Capabilities

The public guide describes supported product options; FSCR preparation coverage
is narrower where its current task template lacks a qualified representation.
An FSCR gap must not be reported as an Oracle product prohibition.

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| DM4 Email or DM5 standard File Export create | Informational | | None when the source-compatible type and supported fields are selected | Continue to global name and transport-specific preparation checks; no import approval is implied | No |
| New user-defined Business Event method through the current FSM profile, including prepared_import | Blocking | | The attempted DM6 profile failed native FSM qualification with a predefined-type restriction; enabled lookup membership, a unique name and valid CSV columns do not prove create eligibility | Stop before preparation or approval. Retain the business requirement and failed native evidence. Do not return create_needed or ready_for_preparation, generate another candidate, change the provider flag, select another name or switch executor. This does not prohibit Oracle's Business Event option or establish predefined-method reuse | No |
| New inactive outbound-invoice XSLT connection with predefined Business Event primary under predefined_business_event_fsm | Blocking | resolve_cmk_connection_delivery_methods | The bounded input shape, same-provider native reference witness, independent current message eligibility, exact row/package binding or duplicate-association checks fail | Apply Predefined Business Event Connection References and Inputs through the existing connection graph. A verified predefined reference does not require a provider-owned delivery-method row. Do not create a method, broaden provider/document/mode/status or reuse the reference association as a new create; preserve normal Core approval and saved-state verification | No |
| B2B Adapter is explicitly requested through the FSM profile | Blocking | | The current FSCR profile has no qualified create representation for this request | Return the exact native preparation gap and retain the nonsecret business choices. Any external prerequisite remains separately scoped to its owning task; it does not authorize assisted delivery-method setup or another write route | No |
| SFTP, SOAP or REST method creation under the current twelve-column FSM profile | Blocking | | The full required transport/security representation is absent: SFTP host/port and credentials, SOAP endpoint/credentials, or REST ServiceUri/authentication settings are not all represented by this CSV | Identify the exact absent representation from the supplied request. Retain nonsecret choices, do not collect or persist secrets for a blocked route, and return an execution-contract gap. Existing unchanged migration is a different operation; an endpoint or populated transport label alone does not establish a create contract | No |
| An uncompressed-PDF option is requested within the selected FSM profile | Blocking | | PoPdfAtchUncmprsd has no member/column in the current FSM profile | Return the unsupported native-field preparation gap while retaining the requested PDF option. Do not select assisted setup or another write route. Never treat FileExtension pdf as an equivalent implementation or switch after a failed/uncertain write | No |
| Customer requests a custom repository account | Blocking | | The current template has no qualified writable account field | Explain the missing account-change contract; preserve the request and do not invent a universal account value | No |
| New method is requested for a predefined provider | Blocking | | Current preparation is user-defined-provider only, consistent with the documented restriction on adding methods to predefined providers | Preserve the business request and return the provider-specific restriction; do not widen the provider finder or change the provider to evade it | No |
| A requested-state reuse includes a field unavailable to the state resolver | Blocking | | The actual requested field was omitted or lacks confirmed response typing | Do not return reused_and_verified from a name-only match. Require current field-level evidence, or report exactly which requested setting remains unverified | No |

The public 26D delivery-method guide is the product source. Current FSCR
preparation limitations remain separate from product capabilities.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.DELIVERY_TRANSPORT_GATE | decision | 36 | design_enforcement | profile_supported->CMKSP.DELIVERY_NAME_CHECK;blocked->RETURN_ISSUES | CMKSP.DELIVERY_RECONCILE | stop | Before a new-method preparation handoff, apply Delivery Transport Capabilities for the selected model/type and supplied settings. Existing verified reuse and unchanged-package import do not enter this create-only gate |


## Public Connection Business Rules

Product guidance: [26D outbound messages](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/define-outbound-collaboration-messages.html),
[26C inbound messages](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/facmm/define-inbound-collaboration-messages.html).
The 26D PDF also covers inbound messages on printed pages 426–427.

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| At CHECK_CONNECTION_ACTIVATION after normal design checks for an Active create | Blocking | check_cmk_connection_activation | Another active definition exists for the selected provider/document/direction scope | Return a conflict and retain both identities privately; do not deactivate the existing definition or change scope implicitly | No |
| Requested status is Loopback | Informational | | None when the selected status is currently eligible | Describe processing without partner delivery; do not call it proof that a PO reached its destination or automatically switch to Active | No |
| A predefined provider needs customization | Blocking | | Proposed package adds or replaces provider messages without a qualified change contract | Preserve the request and follow the published provider-specific customization guidance; do not treat a duplicate definition as permission to overwrite provider setup | No |


## Assisted Delivery Design

Public product source: [Define Delivery Methods, Oracle 26D](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/facmm/define-delivery-methods.html).
The historical task record retains the original operator instructions and
approval; these rules qualify that already declared route.

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Assisted new method | Blocking | | Provider is predefined, current name absence is not established or identity is ambiguous | New methods require a user-defined provider and a unique selected name. Keep strict create intent; do not reuse/update a name collision silently | No |
| Assisted predefined-provider update | Blocking | | Request includes fields beyond the existing URL, username/password change documented for predefined providers | Permit only that documented existing-method update; do not change type, recipient, PDF flag, attachments or add a method | No |
| Assisted PDF setting | Blocking | | Requested setting is not Email, is not an explicit boolean, or another setting is being substituted | Preserve the exact Email option and its sole-attachment PO PDF condition; explicit false is valid. Do not turn FileExtension into PDF behavior or discard Attach Payload | No |
| Assisted credential setup | Blocking | | Raw credential supplied, operator cannot enter values directly in Fusion, or new authenticated delivery has no credential-entry action | Use direct operator entry in Fusion, without chat/DOM/screenshot capture; preserve existing credentials only when not replacing. Do not infer CSF semantics or lower the security choice | No |
| Assisted field update | Blocking | | Supplied nonsecret setting cannot be represented by the selected current documented screen or an update would change identity/type implicitly | Preserve every supplied choice, require the applicable current screen fields and include each intended result in private fieldExpectations. Stop only the unsupported field, never silently drop it | No |
| Assisted retry and verification | Blocking | | Prior attempted save is uncertain, the preview changed, or verification is being used to authorize another save | Reopen and reconcile through assisted_delivery_verify. Preserve action uncertainty separately; new review/approval is required for any later deliberate mutation | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.ASSISTED_DESIGN | decision | 68 | design_enforcement | passed->CMKSP.ASSISTED_GATE;blocked->RETURN_ISSUES | CMKSP.ASSISTED_CONTEXT | stop | Only the selected assisted setup operation: evaluate Assisted Delivery Design against the original immutable review. Existing FSM/REST design rules retain their own scope |


## Assisted Provider, Connection and Integration Design

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| configure_service_provider | Blocking | | Current create name collides, user-defined requirement fails, mandatory screen fields are missing or changes exceed the selected provider's editable fields | Preserve exact current provider scope and use its actual eligible type/ID-type choices; no invented defaults or duplicate provider | No |
| configure_provider_connection | Blocking | | Direction/document/provider/message scope disagrees, primary outbound delivery is missing, inbound delivery is supplied, or an active-definition conflict exists | Reconcile exact current scope and apply existing direction/activation rules before preview; no implicit old-definition deactivation | No |
| configure_event_integration | Blocking | | External environment/event/target is ambiguous, a different event substitutes for CMK, or requested activation lacks exact review | Bind actual source/event/destination and mappings privately, test connections and review exact activation before operator action; never guess event identifiers | No |

## Customer Acceptance Design

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Existing recipient | Use existing verified supplier/site/provider identities. Business documents express intent; neither a site name nor a test template establishes a current record | Before Process | |
| Isolated negative cases | Missing-field checks may exercise UI validation without dispatch. Message processing requires a known test fixture with existing Loopback or verified controlled destination. Never alter shared live settings, replace credentials or send invalid business content to an unverified endpoint | Before Process | |
| Completion evidence | Match the actual result to the case expectation and execution level. Negative input rejection is not proof of transport behavior, and sample-message processing is not a transactional PO event | Acceptance verification | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.ACCEPTANCE_DESIGN | step | 82 | design_enforcement | clear->CMKSP.ACCEPTANCE_GATE;blocked->CMKSP.ACCEPTANCE_BLOCKED | CMKSP.ACCEPTANCE_INPUT | stop | Enforce Customer Acceptance Design using actual current browser evidence; no configuration change or processing request |

## All Object Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Creating or changing any object in the task inventory | Blocking | | Business-input/key/relationship/preparation contract is absent for that object or an internal ID is being invented | Record the specific skill gap. Preserve the business requirement, research customer-accessible public guidance and requalify before preparing rows. Do not tell the customer to supply undocumented importer internals | No |
| Unchanged populated exported objects | Blocking | | Protected parent/child IDs, structured decision data, parameter identity or template metadata was manually rewritten without a qualified rule | Preserve original package relationships and use its declared migration route; task flags do not authorize a hand-built replacement | No |
| Customer acceptance scope | Blocking | | A local header check, Oracle UI validation or one provider read is presented as all-object live success | Report actual execution level and per-object evidence. Keep blocked and not-run cases visible | No |

## Assisted External Format Design

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| configure_external_message_definition | Blocking | | Current document/standard/version or unique saved-name scope is unresolved; shared XML roots need subtype identification but its path is absent | Confirm current choices and requested root/subtype paths through the documented screen before preview. Missing sender message ID path means no sender-ID logging, never a generated-ID substitute | No |

## Early Supplied-Value Design Checks

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Explicit Business Event selection for a new user-defined method under the current FSM profile | Blocking | | Business Event Native Qualification records the failed DM6 native create attempt; this request has no supported creation contract | Reject before reference reads, exports, preparation or import approval when the business type is already explicit. If the type is resolved later, apply the same Delivery Transport Capabilities restriction before create-needed handoff or prepared_import approval. Keep failed-import verification and unchanged native migration in their own scopes; do not retry or invent a predefined-method route | No |
| Explicit non-Email transport plus an Email-only uncompressed-PDF choice at intake | Blocking | | The existing Assisted PDF setting rule already rejects this combination from supplied values alone | Apply that owning rule before operator-context or reference requests; preserve both business choices and explain the incompatible combination. Do not silently change the channel or discard PDF | No |
| Explicit external-format request describes shared XML roots without subtype identification | Blocking | | The existing configure_external_message_definition design rule requires a distinguishing subtype/path; the requirement is already missing from the supplied business document | Request that documented distinction before any operator-context or reference step. Do not invent a discriminator or XPath | No |
| Other business inputs, dynamic dependencies and verification/import stages | Informational | | None at this early step | Continue to the existing input, context, lookup and design gates. Early clear never replaces current-reference, privilege, namespace, activation or approval checks | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.EARLY_DESIGN | decision | 1 | design_enforcement | clear->CMKSP.REQUEST_SHAPE;not_applicable->CMKSP.REQUEST_SHAPE;blocked->RETURN_ISSUES | none | stop | First apply FSM-Only Route Enforcement: runbook_rest_operation, export_message_transformation_package and assisted UI setup/execute return blocked locally without any external call. Then apply Early Supplied-Value Design Checks only to explicit invalid combinations already established by the customer inputs. No external call occurs. For customer_acceptance_prepare, customer_acceptance_execute, customer_acceptance_verify, assisted_delivery_setup with no explicit invalid combination, assisted verification and every unrelated/unchanged-import stage return not_applicable without GET. Dynamic design checks remain downstream. |
