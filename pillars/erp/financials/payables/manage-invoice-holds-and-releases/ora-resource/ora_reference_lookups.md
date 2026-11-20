# Manage Invoice Holds and Releases — Reference Lookups

This file owns task-record identity
and lookup behavior. The embedded import dependencies below do not authorize
standalone database access, lookup mutation or an alternative public API.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AP_HOLD.LOOKUPS | step | 20 | reference_lookup | success->AP_HOLD.DEPENDENCIES;failure->AP_HOLD.ERRORS | AP_HOLD.INPUT | stop | Establish exact task-key identity through a fresh task export and apply the embedded lookup contracts below. |

## Record Identity

Preserve the exact HoldLookupCode and its case. Create requires no exact key
match in a fresh same-task export and no duplicate requested keys. Update
requires exactly one nonblank baseline key. Reject absent or duplicate update
targets and existing create keys instead of allowing implicit task-row upsert.
Do not substitute an alternate or surrogate key. A task export establishes
only task-row identity, not independently stored supporting lookup absence.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_hold_code_identity | Declared read-only workflow reaches identity preflight | Exact HoldLookupCode; q filter with escaped code; limit and offset | GET /fscmRestApi/resources/11.13.18.05/payablesInvoiceHoldsLOV | HoldLookupCode, HoldType, Name, Description; items and hasMore pagination | Compare exact HoldLookupCode over every page and corroborate with the fresh same-task export. The single-match requirement is a client guard, not asserted server uniqueness. | Returned HoldLookupCode unchanged to AP_HOLD_CODE.HoldLookupCode; Name/Description are display values. | Zero is no visible LOV match, not absence or create permission. Multiple matches are ambiguous. Auth/transport/API failures remain failures, not zero matches. |

## Type Labels

Resolve supplied labels only when the canonical code is unambiguous. An input
of quick release needs clarification because the first two types below differ.
These mappings and existing export codes are not an exhaustive create allowlist.
Scalar requiredness and precision belong to [Input Validation](ora_input_validation.md).

| Label | Canonical HoldType |
|---|---|
| Invoice line hold reason | LINE HOLD REASON |
| Hold quick release reason | HOLD QUICK RELEASE REASON |
| Invoice quick release reason | INV QUICK RELEASE REASON |
| Invoice release reason | INVOICE RELEASE REASON |
| Matching release reason | MATCHING RELEASE REASON |
| Variance release reason | VARIANCE RELEASE REASON |

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_hold_type | Fusion validates supplied HoldType during import. This is not a client lookup or a pre-import dependency; do not query the environment or require a membership receipt. | HoldType; HOLD TYPE; application 200; effective-date conditions | Embedded Fusion import validation; no standalone endpoint. | LookupCode, DisplayedField, Description; projected fields are not a closed accepted-value list. | Canonical LookupCode within HOLD TYPE; sysdate >= nvl(start_date_active,sysdate) and sysdate < nvl(end_date_active,sysdate+1). Do not add a separate SET_ID or EnabledFlag filter. | LookupCode to AP_HOLD_CODE.HoldType; never substitute a display label or uppercase an ambiguous label. | Zero membership raises FND_CMN_INVALID_ATTRB_API_SERV during import. Do not invent an endpoint, label mapping or identity-style duplicate selection. |
| resolve_hold_description | Supporting lookup maintenance during create/update import. Description input and update eligibility are owned by Input Validation and Design Enforcement. | HoldLookupCode; DspDescription; HOLD CODE; set_id 0; view_application_id 200 | Embedded supporting lookup maintenance; no standalone mutation. | Explicit description; create meaning=HoldLookupCode; update existing displayed meaning; same-context exported description for reconciliation. An export confirms its description, not hidden metadata or every language version. | Exact HOLD CODE/set0/app200/key context and nonnull description guard. | DspDescription to lookup-backed description, never an AP_HOLD_CODES column, ExternalDescription or HoldInstruction. | Create deletes a preexisting exact-context supporting lookup before inserting the requested name/description. Update creates the supporting lookup when absent or updates it even when the description is unchanged. This is normal import behavior: do not reject create because its supporting lookup exists, or require independent lookup absence, extra lookup fields, acknowledgment or language/tag/deployment/persistence proof before import. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Identity preflight passes | An exact-code read identifies a visible definition; it does not establish import capability or authorize a write. |
| A required identity or execution contract is incomplete | Stop only the affected live operation and retain its exact gap. Do not invent an endpoint or direct database/manual shortcut. |
| Read-only preflight is unavailable | Preserve the actual failure; do not treat it as absence or invent a current value. Offline preparation may proceed while the affected live action remains blocked. |

The supported update fields add no external reference resolver. Field domains
and clear rules belong to Input Validation; update restrictions and import
effects belong to [Design Enforcement](ora_design_enforcement.md).
