# Design Enforcement

## Source

- Oracle readiness: Streamline the Import and Export of Messaging Setup Data, 26C, https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46531.htm
- Oracle readiness: Redwood: Simplify Configuration and Processing for B2B Messaging, 25C, https://docs.oracle.com/en/cloud/saas/readiness/scm/25c/sccv25c/25C-sccv-wn-f39141.htm

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm simplified feature state | Do not proceed unless the feature is enabled on the selected host |
| 2 | Confirm migration scope | Include the service-provider task when migrating all Collaboration Messaging configuration objects |
| 3 | Confirm supported simplified setup | Do not use unsupported documents, predefined providers, or override message definitions where the enabled release documents those limitations |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Migrating all Collaboration Messaging configuration data through a configuration package | Blocking | | Manage Collaboration Messaging Service Providers is not included with this task | Add both documented tasks to the implementation project | Yes |
| Simplified B2B Messaging is enabled | Blocking | resolve_simplified_feature_state | The required feature-state prerequisite has no passing result | Consume the existing same-operation prerequisite evidence; do not repeat its GET or enable the feature from this design gate | Yes |
| Simplified partner-property setup or migration | Blocking | resolve_simplified_feature_state | Live Gen2 feature evidence is absent/disabled, the template/schema conflicts with the declared source profile, or requested provider scope is outside the current user-defined create resolver | Require same-target Gen2 feature evidence and compatible profile. Keep Gen1 Redwood separate; preserve seeded provider flags for unchanged imports. Document and override-message eligibility belongs to its owning document/connection workflow; never infer it from this task or apply 25C restrictions to all later releases | Conditional |
| Preparing create/update task data | Blocking | | Duplicate create key, ambiguous update target, or undocumented changes to existing records | Review all added/changed/affected records; preserve unrelated data and require exact update scope | No |
| Add provider to customer/supplier properties | Blocking | | Request is silently converted into provider creation, connection assignment or document enablement | Limit the change to the requested partner property; use the existing provider | No |
| Connection followed by partner-property setup | Blocking | | Partner or account/site scope is unspecified, or a completed connection is treated as authorization to select a partner automatically | Ask only for missing partner scope and reuse known provider input; orchestration belongs to the invoking Run Book | Yes |
| Partner create intent with existing matching properties | Blocking | check_cmksc_partner_property_duplicate | A new-row request would overwrite an existing property or append an ambiguous duplicate, or the current complete collision result is missing | Show the existing-match outcome; require explicit update scope and a qualified update contract before any update. Do not relabel create as update | No |
| Partner create import matching | Blocking | | Preparation is blocked only because Fusion's internal FSM match key or insert/update algorithm is undocumented | Validate one unambiguous requested business scope and exactly one prepared partner-property row, then let the supported FSM import job perform record matching; retain the import result and verify terminal target state | No |
| Partner optional settings | Blocking | | Customer-supplied BU, Domain Value Map or Application Partner Code is dropped, or a value is invented to fill a mapping gap | Preserve the requested setting and qualify its representation before editing; explicit omission needs no invented default | No |
| Direct-provider derivation used for partner properties | Blocking | | A Partner ID is invented from the provider name, numeric ProviderId or provider's own partner identity | Preserve a supplied Partner ID exactly; leave the optional field blank when omitted. Use Partner ID Type only as a selected qualified code | No |
| Partner artifact isolation | Blocking | | Preparing partner properties changes another CSV, metadata or existing row | Keep the single new-row intent and validate the exact delta before review | No |
| Selected provider has ProviderType ORA_CMK_DIRECT, the declared provider-dependent design contract | Blocking | | Either PartnerId or PartnerIdTypeCode is blank at the final design gate | Preserve optional intake; before execution request the missing identifier pair for this selected provider or return a precise invalid-design result. Never derive identifiers from provider identity | No |
| Customer property with a non-direct provider, sources the qualified field contract | Blocking | | Both the complete PartnerId/PartnerIdTypeCode pair and a nonblank DvmGroup are absent | Require the identifier pair or a DVM group; DVM-only customer input remains valid under this predicate | No |
| Supplier property with a non-direct provider, the declared provider-dependent design contract | Blocking | | No complete identifier pair, DvmGroup or ApplPartnerCode is supplied | Preserve all explicit choices and require one source-supported identification/mapping alternative | No |
| Supplier ApplPartnerCode is supplied, the declared provider-dependent design contract | Blocking | | PartnerId, PartnerIdTypeCode or supplier site is missing | Require the complete identifier pair and selected site for this setting; do not treat APC as bypassing its separate validator | No |
| Preparing partner properties from a broad messaging request | Blocking | | Partner kind, selected supplier/site or customer/account scope is unresolved, or package includes unrequested BOs | Preserve known provider and business inputs; resolve only missing partner scope through this task's intake. A successful connection does not select a partner or complete its properties | No |
| Preparing another BO found in this task's CSV inventory | Blocking | | Inventory is treated as proof of a qualified business-input creation contract | Require that BO's source-backed input, mapping and preparation contract; return the exact authoring gap without borrowing another task's CSV members or execution route | No |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_simplified_feature_state | Before simplified configuration is accessed | Feature enabled state | ora_reference_lookups.md |
| check_cmksc_partner_property_duplicate | Partner-property create preparation and final preapproval validation | Scope-bound complete existing-property collision result from the declared live read | ora_reference_lookups.md |

The feature-state request is owned by CMKSC.RESOLVE_FEATURE_STATE in
ora_reference_lookups.md; ora_dependency_readiness.md owns prerequisite
readiness. This design gate consumes that result rather than introducing a
second verification operation. Collision and eligibility policy is owned by
this file; its resolver mechanics and missing authority are owned exclusively
by ora_reference_lookups.md. Input representation remains owned by
ora_input_validation.md and failure disclosure by ora_error_handling.md.

## Setup Reconciliation Policy

CMKSC.RECONCILE_SETUP owns these FSCR reconciliation decisions. It evaluates the applicable
provider-dependent Design Rules above against effective values, not blank
attachment cells. Lookup mechanics remain in ora_reference_lookups.md.

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| ensure_partner_setup finds one matching scope and all supplied settings satisfied | Informational | check_cmksc_partner_property_duplicate | None when effective current values pass applicable provider/source-profile design checks | Return reuse with requested-state verification and preserved unspecified settings. No export, import or optional-field question is required for a no-op | No |
| ensure_partner_setup finds no existing property | Informational | check_cmksc_partner_property_duplicate | None only when the explicit/unspecified create inputs meet applicable provider-dependent design requirements and collision checks | Return create_needed to the invoking Run Book's existing create workflow; unspecified optional fields remain empty for a new row. Revalidate current absence and all package/approval checks before any import; this result is not create approval | No |
| Existing property requires an explicitly supplied change or clear | Blocking | check_cmksc_partner_property_duplicate | Desired state differs from the current property | Return review_required with current/requested business differences. Require exact update scope, a qualified field-specific update/clear contract and the normal immutable-artifact approval. Do not convert reuse or explicit create into an update, infer clearing support or submit a new duplicate row | No |
| Effective values fail provider-dependent rules or required scope is unresolved | Blocking | verify_cmksc_partner_id_type | The effective identifier/mapping alternatives or current code eligibility do not satisfy the applicable Design Rules | Group missing business decisions once with their concrete business effect. Preserving unspecified settings does not waive provider validators or reuse an invalid existing property; do not ask for irrelevant optional values | No |
| Explicit create sees an existing property | Blocking | check_cmksc_partner_property_duplicate | Existing matching scope or alternate-key collision | Retain the existing strict create rule; only ordinary ensure_partner_setup may classify a verified no-op as reuse | No |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.ENFORCE_DESIGN | decision | 40 | design_enforcement | passed->CMKSC.GATE_EXECUTION;blocked->CMKSC.RETURN_ISSUES | CMKSC.VERIFY_PARTNER_DEPENDENCIES | stop | Apply design rules for current operation and stage; package-delta checks apply only once a package is prepared |
| CMKSC.RECONCILE_SETUP | decision | 36 | design_enforcement | reuse->CMKSC.REUSE_DONE;create_needed->CMKSC.CREATE_NEEDED;review_required->CMKSC.REVIEW_REQUIRED;blocked->CMKSC.RETURN_ISSUES | CMKSC.CHECK_PROPERTY_COLLISION | stop | Only ensure_partner_setup: apply Setup Reconciliation Policy and the applicable effective-value provider design rules; no mutation or artifact approval |

The task-scope and CSV-inventory rules above preserve the former parent CMK
Business-Goal Journey policy in this owning design resource. Cross-task planning
remains with the invoking roadmap and Run Book, outside this task graph.


## Assisted Configuration Design

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Any declared assisted configuration setup | Blocking | | Current configured context, feature/model availability, privileges or exact object/scope cannot be established | Retain supplied inputs and obtain current operator-confirmed page/scope; no opaque URL is a customer prerequisite | No |
| Assisted partner update/create | Blocking | | Create collides, selected site/account belongs to another partner, provider/BU scope conflicts or effective provider-dependent property rules fail | Apply the existing partner key and optional-field business rules to current screen selections before review; do not transfer supplier/customer key roles | No |
| Assisted document assignment | Blocking | | Direction is inbound, connection/document/direction disagree, connection is not eligible/active or assignment widens beyond approved partner/default scope | Preserve exact document and assignment scope, correct the explicit requested mismatch before Save; no hidden activation or default changes | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.ASSISTED_DESIGN | decision | 15 | design_enforcement | passed->CMKSC.ASSISTED_GATE;blocked->CMKSC.RETURN_ISSUES | CMKSC.ASSISTED_CONTEXT | stop | Only selected assisted setup: apply Assisted Configuration Design and current effective business rules |

## All Object Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Creating or changing any object in the task inventory | Blocking | | Business-input/key/relationship/preparation contract is absent for that object or an internal ID is being invented | Record the specific skill gap. Preserve the business requirement, research customer-accessible public guidance and requalify before preparing rows. Do not tell the customer to supply undocumented importer internals | No |
| Unchanged populated exported objects | Blocking | | Protected parent/child IDs, structured decision data, parameter identity or template metadata was manually rewritten without a qualified rule | Preserve original package relationships and use its declared migration route; task flags do not authorize a hand-built replacement | No |
| Customer acceptance scope | Blocking | | A local header check, Oracle UI validation or one provider read is presented as all-object live success | Report actual execution level and per-object evidence. Keep blocked and not-run cases visible | No |

## Additional Assisted Object Design

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Account or ship-to setup | Blocking | | Supplier/site/BU or account/location relationship is unresolved, cross-scope, duplicated or already assigned under a strict-create request | Resolve current business identities and requested create/update intent before review; never silently widen ship-to assignment scope | No |
| Processing or delivery-size setting | Blocking | | Field/unit/range is unconfirmed, unrelated setting is changed, or request is being translated into an invented parameter/type primary key | Use current documented setting semantics and preserve every unrequested value; verify exact fields rather than a broad saved-success statement | No |

## Public Account and Location Design

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Public account/ship-to creation | Blocking | verify_cmksc_runbook_rest_preflight | Account exists in the same scope, supplier/site/BU or location relationship is unresolved, nested schema cannot represent requested assignments, or derived IDs are being allocated | Resolve exact current business scope and absence before review; block unsupported assignment representation rather than creating an incomplete account | No |
| Public location creation | Blocking | verify_cmksc_runbook_rest_preflight | Code/scope is duplicated or ambiguous, customer/site relationship is unverified, or payload includes derived address/flag/ID fields | Resolve current existing customer/site; submit only qualified business references and preserve the full current scope | No |

## Native Initial Settings Design

These rules own the effective-state and initial-settings change decision.
Input shapes and native representation belong to Native FSM Initial Settings
Inputs; lookup mechanics belong to qualify_cmksc_fsm_initial_settings.

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Initial settings request | Blocking | qualify_cmksc_fsm_initial_settings | An existing target parameter/type/property row is replaced by a fabricated new identity, its semantic parent is unknown, or a requested field is dropped | Preserve requested business settings and target row identities. Return the precise missing contract; greenfield initial settings can change existing configuration rows | No |
| Large-PO settings | Blocking | qualify_cmksc_fsm_initial_settings | Effective delivery attempt interval is not less than delivery duration, either is nonpositive, or a selected count lacks its qualified range | Compare requested and current unspecified values together. Keep minute/count units separate; report the conflicting settings before preparation | No |
| Selected reprocessing or storage settings | Blocking | qualify_cmksc_fsm_initial_settings | Effective automatic reprocessing is enabled while effective outbound-source storage is disabled, or an effective reprocessing window/interval is not positive | Preserve the documented storage dependency and evaluate effective state. Never silently change an unspecified flag or drop the requested setting. Saved parameters alone do not establish scheduler activation or successful reprocessing | No |
| Document-property setting | Blocking | qualify_cmksc_fsm_initial_settings | Property is read-only, current document/property is ambiguous, value targets another document or MaxNumericValue/semantic identity metadata would change | Resolve the current mutable property under the intended document; preserve bounds and parent. An ID without a current business-label join is insufficient | No |
| Every selected initial setting already matches | Informational | qualify_cmksc_fsm_initial_settings | None after current complete native/API comparison and effective-state checks | Return already_satisfied with every supplied field verified and unspecified settings preserved. No import is needed; this is neither newly changed configuration nor a changed-value FSM test pass | No |
| At least one selected setting differs | Informational | qualify_cmksc_fsm_initial_settings | None only after every selected field and effective dependency qualifies | Return changed_required for preparation and immutable Core Data Loader approval. This decision does not approve or submit an import | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.FSM_SETTINGS_DESIGN | decision | 162 | design_enforcement | changed_required->CMKSC.FSM_SETTINGS_PACKAGE;already_satisfied->CMKSC.FSM_SETTINGS_ALREADY_SATISFIED;blocked->CMKSC.FSM_SETTINGS_ISSUES | CMKSC.FSM_SETTINGS_REFERENCES | stop | Only configure_initial_settings_fsm: apply Native Initial Settings Design using qualified current rows, field states and effective values. Changed preparation and verified no-op have separate terminals; no external call, mutation or approval |
