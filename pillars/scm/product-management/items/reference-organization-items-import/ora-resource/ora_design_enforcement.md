# Reference Organization Items Import Design Enforcement

Scope authority: [Oracle template guidance](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/faipr/organize-your-data-in-the-fbdi-spreadsheet-import-template.html). Compare requested scope with verified associations from the readiness resolver.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Organization scope | Determine and confirm resulting reference-organization scope. |
| 2 | Structure scope | Apply documented selector combinations for structure modes. |
| 3 | Handoff | Return scope results to the selected Core plan before approval. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Organization selectors | Blocker | verify_reference_org_readiness | Current template scope guidance unavailable or supplied business evidence conflicts with resulting scope | Apply template metadata: export supplied references only; otherwise export the definition organization for its associated references. Retain a definition supplied with references as context. Do not ask to reconfirm scope already determined by the request. | No inferred organizations |
| Structure mode with item number and structure name | Blocker | verify_reference_org_readiness | Source item/structure unverified or selected references differ from intended scope | Make the selected structure common to the selected references | No inferred structure |
| Structure mode with structure name only | Blocker | verify_reference_org_readiness | Item sheet missing or source structures unverified | Apply the named structure to items in the item sheet and selected references | No inferred item list |
| Structure mode with item number only | Blocker | verify_reference_org_readiness | All-structure scope unverified or different from intended scope | Oracle documents all structures for items in the item sheet; confirm this broader scope against current template and existing structures | No silent broadening |
| Assignment-only mode with populated structures | Blocker | | Structure data would be silently ignored or treated as combined mode | Clarify the mode and correct source/mode with fresh validation | No silent discard or mode change |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| verify_reference_org_readiness | Organization/structure scope comparison | Verified associations and conditional source structures | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| REF_ORG_ITEMS.VALIDATE_SCOPE | step | 6 | design_enforcement | valid->REF_ORG_ITEMS.HANDOFF_GATE;invalid->REF_ORG_ITEMS.FAILED | REF_ORG_ITEMS.CONFIRM_DEPENDENCIES | stop | Confirm effective organization/structure scope matches resolved mode and intended request. |
