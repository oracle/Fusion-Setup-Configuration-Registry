# Conversion policy contract matrix

Updated 2026-10-14 from reconciled controlled nonproduction results. Human semantic disposition and ordinary runtime readiness remain separate gates. See [the evidence index](observed-import-contracts.md) for Source IDs and exact result pointers.

## Implemented intake contract

- Match one parent by exact business-unit name and one child by exact business-unit name plus currency code. Reject duplicate or ambiguous identities.
- Blank Excel **value** cells on existing rows preserve fresh-export values by explicit merge. Identity cells must be supplied. Empty child intake carries existing children; it never requests deletion.
- Require source-required fields on new rows. Percentages and parent Display flag may be blank under [nullable-value-contract.md](nullable-value-contract.md); no numeric or flag defaults are invented.
- Preserve exact template headers, including audit columns, and serialize empty audit cells. Clearing, audit overrides, rekeying and deletion have no workbook syntax.
- Use the persisted review-only ZIP for maintenance Data Loader preflight and Task Hook under [the handoff contract](data-loader-handoff.md). `build_in_memory` uses the same merge for local serialization checks; it supplies no interactive core session route. Neither form closes readiness gaps or grants import approval.
- Freshness uses export ProcessDate, never file modification time; timestamps without offsets require the routed exporter's UTC convention.

## Parent and child contracts

| Contract | Observed evidence | Remaining boundary |
| --- | --- | --- |
| Parent match | Updates selected the existing policy without adding another parent. Source maps BuName to OrgId; EO alternate key is OrgId. SRC-FSM-EXM-PARENT-20261014 | Rekey, general duplicate-resolution behavior and shared helper implementation unproved |
| Parent create | Fully supplied Corporate / Y / warning 5 / display Y / error 10 accepted and persisted. SRC-FSM-EXM-PARENT-20261014 | New-row omission/defaults and other create combinations untested |
| Parent updates | All five fields writable in observed cycles: warning 5↔6, error 10↔11, default Y↔N, display Y↔N, Corporate↔Spot. Parent error cycle also preserved both children. SRC-FSM-EXM-PARENT-20261014 | Tested values are examples, not an exhaustive allowed-value list or numeric range |
| Child match | Existing row updated with unchanged cardinality, parent and sibling business values. Source key is CurrencyCode plus parent ExchangeRateId. SRC-FSM-EXM-CHILD-20261014 | Currency/BU rekey and duplicate resolution untested |
| Child create | CAD and then INR accepted with supplied business values; second create preserved sibling and parent. SRC-FSM-EXM-CHILD-20261014 | New-row omissions/defaults and other combinations untested |
| Child updates | All four fields writable in CAD cycles: warning 2↔3, error 5↔6, default Y↔N, display Y↔N. INR warning 10↔11 also verified through Excel. SRC-FSM-EXM-CHILD-20261014; SRC-FSM-EXM-WORKBOOK-20261014 | Numeric domain, invalid-value errors and arbitrary combinations untested |
| Workbook partial updates | Actual Excel parent and child warning forward/reversal imports preserved every blank-input field; child-only intake carried the parent. SRC-FSM-EXM-WORKBOOK-20261014 | Explicit merge, not raw FSM patch semantics |
| Child rows omitted | A present header-only child CSV preserved both children as full rows including audits during parent warning update/reversal. SRC-FSM-EXM-OMISSION-20261014 | Absent member/XML node and partially omitted siblings untested; builder continues carrying all children |
| Audits | Empty audit inputs accepted on observed parent/child creates and updates; Fusion populated or maintained audits. SRC-FSM-EXM-PARENT-20261014; SRC-FSM-EXM-CHILD-20261014 | Explicit audit overrides and omitted audit columns untested |
| Removal | Individual CAD and INR UI deletions persisted, preserving parent and unrelated rows. SRC-FSM-EXM-UI-20261014 | No FSM/workbook deletion, parent deletion or automatic recovery route proved |
| Import errors | Parent default, child default and child display blank probes returned FND_CMN_REQ_ATTRIB_API_SERV with unchanged exports. SRC-FSM-EXM-BLANK-20261014 | Child probes surfaced parent ExchangeRateOption detail; other errors and universal atomicity untested |

## Existing-row raw FSM blank cells

Full headers were retained. These observations do not authorize clearing through the workbook.

| Field | Parent blank outcome | Child blank outcome |
| --- | --- | --- |
| UserConversionType | Existing Corporate and audits preserved in tested case | Not a child field |
| DfltExchangeRateFlag | Required-attribute rejection; unchanged | Required-attribute rejection; unchanged |
| DispWarningToUser | Cleared; recovery verified | Required-attribute rejection; unchanged |
| WarningTolerance | Cleared; display Y retained; recovery verified | Cleared; display N retained; recovery verified |
| ErrorTolerance | Cleared; recovery verified | Cleared; recovery verified |

Source: SRC-FSM-EXM-BLANK-20261014. The parent warning/display outcome differs from the UI handler's checkbox clearing. Keep the UI rule distinct from import behavior.

## Open evidence and readiness

Unresolved: new-row default/omission behavior, omitted columns or absent members, multi-field null combinations, numeric ranges and exact numeric/off-domain/reference errors, universal failure atomicity, rekeying, FSM/parent deletion, and the indexed shared MigratorHelper implementation. Positive destination lookups do not prove negative FSM resolver errors.

The authored route supports creates with source-required fields and explicit-merge updates preserving nullable percentages. Validate populated tolerances as finite/nonnegative and compare error > warning only when both are populated. Required flags remain Y/N; parent Display is nullable. Exact identities, blank audit cells and child carry-forward remain enforced. Unknown defaults, clearing, rekeying and deletion remain outside that route. Exact Oracle rejection wording and a universal numeric domain are not asserted and are not prerequisites to rejecting invalid input locally. Require fresh destination exports, complete reference evidence, Task Hook validation and core approval for every candidate. Campaign approvals never approve future imports.
