# IDR Reference Lookups

These are local value resolvers. They do not read or write Fusion lookup data.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_idr_override_business_unit | Override Default Business Unit is explicitly supplied | Named choices: Email Routing Attribute=RA; Sender's Email Address=SE; Recipient Email Address=RE. No selection=N. | Trimmed case-insensitive exact named label or code; an explicitly supplied empty value maps to N. Omission leaves the field unchanged. | BuDerivationBasisCode canonical code | Reject an unknown or ambiguous label or code; ask for a supported choice. |
| validate_idr_extension_option_code | An extension row is requested | User-confirmed fixed code AP_PRORATE_FREIGHT_MISC | Exact OptionCode AP_PRORATE_FREIGHT_MISC only | Existing extension row selector OptionCode | Reject any other code, including ORA_AP_IMAGES and ORA_POLICY_DETAILS. A missing existing row blocks update; do not create it. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| The requester names Override Default Business Unit | Resolve its named selection or code with resolve_idr_override_business_unit. A request to leave the field empty maps to N; omission preserves its current value. |
| The requester supplies an extension code | Validate exact AP_PRORATE_FREIGHT_MISC with validate_idr_extension_option_code. Reject operations targeting another extension code. Leave untargeted rows out of the update ZIP and verify their non-audit values remain unchanged in target state; do not add rows from another source environment. |

## Selected Fusion target and authentication profile

Before preparing exports or task data, retain the independently confirmed Fusion
environment name and credential-free HTTPS origin in the project target context.
Retain the selected OAuth `environment` value separately as the authentication
profile. The names may be unrelated (for example, profile `DEV` and Fusion
environment `example-fusion`). Reuse a previously confirmed target; ask for its
actual identity only when it is missing or ambiguous. Never derive it by removing
a profile suffix or guessing from a hostname, ZIP or reference receipt.

Pass the actual selected Fusion name to task manifest/target-validation inputs,
and require it to match export `ProcessEnv`. Require the selected origin to match
the authenticated configured origin. Compare the login profile only with the
profile bound to the Data Loader preflight; do not compare it with `ProcessEnv`.
Keep task, release/schema, Run Book, archive-integrity and approval checks intact.
If a workflow accepts `referenceContext`, supply the separately selected target
there; do not invent that CLI option for adapters that do not declare it. This
identity handling grants no additional execution or import capability.

## Email to Business Unit Mapping boundary

`Mappings` contains the mapping-dialog XML: a `<mappings>` root with `<item email="..." buid="..."/>` rows. Supply business-unit names in the FSM `buid` attribute. An empty `<mappings/>` root clears the collection. Submit the complete intended collection and retain every unrequested assignment. Preserve the separate `BuEmailMapping` wrapper and `MappingUpdated` cells; they are not mapping inputs. The adapter can serialize structured email/businessUnit rows and validates the supported XML representation. Fusion validates BU existence against the selected target during the approved import; do not claim local BU lookup evidence. Follow the governed mapping-validation path in SKILL.md. Do not invent business-unit IDs, reference APIs or duplicate-resolution rules.