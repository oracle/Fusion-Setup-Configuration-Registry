# Reference Organization Items Import Mode Defaulting

Apply the user-requested default before source validation. Import Mode is a lookup code, not a numeric value, a CSV column or the loader fileAction.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Import Mode | ORA_REF_ORG_ASSGN_BOM_COMMON | Neither mode nor import_mode supplied | No | |

Resolve an explicit supported code or alias without replacing it. Non-default
modes remain offline-validation only until a supported per-run ESS binding
exists. Explicit null, blank, unsupported or conflicting inputs stop with
input_validation; never replace them with the default.

Supported codes are ORA_REF_ORG_ASSGN_BOM_COMMON (both), ORA_REF_ORG_ASSIGN_ONLY (assign), and ORA_REF_ORG_BOM_COMMON_ONLY (structures). Codes and aliases are accepted case-insensitively. Lookup type: ORA_EGO_UPG_REF_ORG_ASSIGN. Values were verified in local Fusion seed StandardLookupTypeSD.xml; the combined code was also supplied by the user from the UI.

Include the resolved code as an informational issue in the defaulting rule result returned to Core. Task Hook compares this source intent with the requested operation and captured CSV scope; it does not inspect the BO configuration or claim the deployed mode is verified. Defaults do not invent structure selectors or organization scope. Combined mode permits item/organization rows without a structure member; structure-only mode requires structure rows.

Core's selected preview binds the validated ordered rule results to approval.
There is no operation-intent extension or automatic outbound mode mapping.
The current live route supports only ORA_REF_ORG_ASSGN_BOM_COMMON; local source
preparation and native handoff checks reject other modes. Offline dry-run may
validate them without authorizing execution. Core executes with the registered BO's configured mode. No pillar configuration
read or LoadAdapterConfig enclosure is required. A defaulted source intent is
not an outbound override or independent verification of the effective mode;
never silently replace an override or add guessed action/ESS arguments.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| REF_ORG_ITEMS.DEFAULT_MODE | step | 2 | apply_default | valid->REF_ORG_ITEMS.VALIDATE_FBDI;invalid->REF_ORG_ITEMS.FAILED | REF_ORG_ITEMS.CHECK_ITEM_INDEX | stop | Resolve explicit Import Mode or apply ORA_REF_ORG_ASSGN_BOM_COMMON when omitted; return the validated code in the Core rule result; Core owns deployed BO configuration; RESOLVE_CONTEXT evaluates its returned preflight evidence. |
