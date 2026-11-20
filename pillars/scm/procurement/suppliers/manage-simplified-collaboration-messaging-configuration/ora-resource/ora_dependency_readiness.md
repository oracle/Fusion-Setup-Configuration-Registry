# Partner Properties Dependencies

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Partner kind | Resolve the user's supplier/customer intent before reading partner choices |
| 2 | Partner and child scope | Resolve customer then optional account, or supplier then site and derived BU |
| 3 | Provider | Revalidate supplied provider or resolve an existing provider; do not create another one |
| 4 | Optional customer BU | Resolve only when selected or supplied; preserve explicit omission |
| 5 | Preparation evidence | Check the stage-specific schema and mapping requirements in input validation before package editing |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| customer | Existing customer | Conditional | Customer partner-property creation | Lookup | Same-target live customer resolver evidence | resolve_cmksc_customer | Identifies customer scope | Choose a customer by name or number | Customer identity and number |
| customer_account | Account belonging to customer | Conditional | Specific-account customer scope | Lookup | Selected-customer account resolver evidence | resolve_cmksc_customer_account | Prevents cross-customer assignments | Choose an account under the selected customer | Account identity, number and parent context |
| supplier | Existing supplier | Conditional | Supplier partner-property creation | Lookup | Same-target live supplier resolver evidence | resolve_cmksc_supplier | Identifies supplier scope | Choose a supplier by name or number | Supplier identity and number |
| supplier_site | Site belonging to supplier | Conditional | Supplier partner-property creation | Lookup | Selected-supplier site resolver evidence | resolve_cmksc_supplier_site | Resolves site and its Procurement BU | Choose a site; Business Unit comes from that site | Site and derived Procurement BU |
| provider | Existing provider | Yes | Partner-property creation | Lookup | Same-target live provider resolver evidence; retained Run Book selection revalidated | resolve_cmksc_provider | Associates properties with the intended provider | Keep the connection's provider when supplied, or choose an existing provider | Provider identity, exact name, type and flag |
| customer_bu | Financial Business Unit | Conditional | Customer BU selected or supplied | Lookup | Same-target live BU resolver evidence | resolve_cmksc_customer_business_unit | Keeps optional customer BU distinct from supplier Procurement BU | Select or omit; an unmapped supplied value cannot be discarded | Selected customer BU identity and name |
| simplified_feature | Simplified-model feature evidence | Yes | Before this task's export or import | Verify | Existing same-target feature resolver result | resolve_simplified_feature_state | Records the existing feature gate without duplicating its mechanics | Stop on a failed or missing result; do not enable the feature in this task | Current operation-host feature evidence |
| partner_identifier_type | Qualified partner identifier type | Conditional | Partner-property preparation when identifier type is represented | Verify | Current standard-lookup result from the named resolver, backed by Partner Properties Public Sources, the qualified field contract and Partner Properties Public Sources | verify_cmksc_partner_id_type | Prevents an observed request value from becoming an inferred default | Use the declared identifier-type read; do not ask for provider-creation fields | Qualified code and applicability evidence |
| partner_property_collision | Existing-property collision evidence | Yes | Partner-property create preparation and final preapproval validation | Verify | Current complete evidence from the source-backed named resolver | check_cmksc_partner_property_duplicate | Supplier/customer LOV selection does not prove absence of existing properties | Stop before preparation on missing/incomplete collision evidence; preserve create intent | Scope-bound collision outcome |
| partner_property_verification | Qualified target-state verification | Yes | After completed partner-property import, before reporting verified properties | Verify | Current complete evidence from the source-backed named resolver | verify_cmksc_partner_property_state | Import status does not establish the intended target properties | Require the declared complete before/after comparison before reporting verified properties | Verified property comparison outcome |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Every applicable reference resolved with consistent parent and target scope | Proceed to design checks; no mutation from this node |
| Lookup | A choice is missing or stale | Return to the declared intake resolver; never repeat an uncertain write |
| Blocked | Scope conflicts, incomplete read or missing route evidence | No dependent action; preserve selections and explain the missing fact |

CMKSC.VERIFY_PARTNER_DEPENDENCIES checks the results of the prior intake nodes;
it does not issue a duplicate GET when that evidence is still current. A child
selection cannot survive a changed parent or environment without revalidation.
Unchanged completed-package operations and other BOs return not_applicable.
The invoking Run Book owns any continuation from connection creation; this
task graph never starts or modifies another task.

The additional rows expose contracts already required by the reviewed evidence
map and existing preparation/verification rules. Lookup mechanics and live
authority are owned solely by ora_reference_lookups.md. A Verify row does not
authorize an unresolved request. Source: ora_input_validation.md, Partner Properties Public Sources. Existing intake and export stage boundaries remain. Authoring readiness does not establish passing runtime lookup, approval or verification results.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSC.VERIFY_PARTNER_DEPENDENCIES | decision | 30 | resolve_dependency | satisfied->CMKSC.ENFORCE_DESIGN;not_applicable->CMKSC.ENFORCE_DESIGN;blocked->CMKSC.RETURN_ISSUES | CMKSC.CHECK_PROPERTY_COLLISION | stop | Partner creation checks applicable resolver evidence and parent/target consistency; other operations skip |
