# Manage Expenses System Options Defaulting Rules

This resource documents the existing workbook and package-builder behavior.
It adds no runtime Task Node or new external execution route.

## Sources

- Task-local `scripts/expense_system_options_intake.mjs`
- [Confirmed create/update contract](../references/create-update-contract.md)

## Defaults

| Input | Behavior | Basis |
|---|---|---|
| Blank workbook setting | Preserve existing configuration; leave absent overrides unset | Confirmed create/update contract |
| Missing named-BU option in both paired files | Create only the explicitly requested option; leave transport IDs and audit cells blank | Confirmed sparse-create contract |
| Missing explicitly selected global option | Use blank BuName and OtherOrgId=-1; never infer global scope from an EBS Site assignment | Confirmed global identity contract |
| Source value or scope not mapped | Ask for semantics/scope; do not supply Yes, No, a BU or an effective value | EBS intake contract |
| Existing requested value equals baseline | Record no change; no package when every requested setting is unchanged | Task-local package comparison |

EBS profile scope is mapped by an explicit migration decision. The target
baseline determines record existence; it does not establish EBS hierarchy
precedence or authorize a global setting. No defaults are copied from another BU.
