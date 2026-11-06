# Manage Expenses System Options Reference Lookups

The active workflow selects the read-only finBusinessUnitsLOV GET through
the shared REST client for every specific BU. Follow the exact fields,
pagination, freshness and evidence binding in
[create-update-contract.md](../references/create-update-contract.md).
The export supplies package schema and existing settings, not the BU domain.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_expenses_option_edit_baseline | A confirmed FSM option create/update package is prepared | The validated intake result and the exact four-member completed FSM export named by its target environment, export job ProcessId, and CSV digests | Match task code EXM_MANAGE_EXPENSES_SYSTEM_OPTIONS, target environment, and each normalized BuName plus OptionCode exactly; require at most one row in each paired option CSV; both absent permits a create, divergent presence blocks. Match metadata ProcessId to the export job ID, or bind the observed `-999` placeholder through the unchanged exporter ZIP filename and member bytes | Baseline identity, source workbook digest, archive and CSV digests, selected rows, original ValueCode, and requested ValueCode | Stop package preparation and re-export or correct the workbook; never select a first or similarly named row |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| The task is a confirmed FSM option edit | Resolve the baseline from the locally persisted validation result and fresh exported package; specific BUs require the declared read-only finBusinessUnitsLOV resolution |
| The request needs a dynamic reference, inheritance representation, or an unconfirmed code | Return unsupported_by_confirmed_fsm_contract with the exact field and missing evidence; do not generate a package |
