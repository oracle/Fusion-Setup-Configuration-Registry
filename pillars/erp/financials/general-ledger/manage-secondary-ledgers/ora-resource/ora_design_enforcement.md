# Manage Secondary Ledgers Design Enforcement

The design gate keeps the task within a reusable structural baseline. The outcome is an in-process secondary and disabled relationship, not completed options, mapping, activation, conversion enablement, or period opening.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm business intent | State why a secondary representation is needed and choose the conversion level intentionally. |
| 2 | Validate compatibility | Enforce source-primary ownership and conversion-level-specific COA, calendar, period, and currency rules, plus the conversion-level accounting-method policy. |
| 3 | Gate on primary options | Allow package preparation to overlap, but require successful, verified primary creation and primary Specify Ledger Options before secondary preview approval or live import. |
| 4 | Build smallest delta | Add only the role-supported secondary, relationship, and conditional controlled rule rows. |
| 5 | Preserve closure | Keep all unrelated rows, headers, aliases, header-only files, and manifest content unchanged. |
| 6 | Preview effects | Show exact member changes, row adds, field source class, intentional blanks, service-owned fields, open boundaries, and later handoffs. |
| 7 | Gate execution | Require explicit approval bound to the exact preview and verify by an identical-scope re-export. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Always | Error | resolve_source_primary_ledger | Source is not exactly one PRIMARY ledger or export aliases disagree | Re-resolve and acquire a fresh scoped export | No |
| Source primary was newly created through FSCR | Error before preview approval and import | verify_source_primary_options_complete | Primary creation or primary-context Specify Ledger Options is not terminal-success and verified, retained earnings or method language remains incomplete, aliases diverge, or evidence is stale/cross-environment | Complete and re-export the primary options, then regenerate and re-preview the secondary package; preparation before readiness does not authorize import | No live import until satisfied |
| Always | Error | check_ledger_name_availability | Secondary name exists in the ledger or reporting-currency relationship namespace, or availability evidence is incomplete | Choose a unique business name and rerun preview | Yes, by user input |
| DataConversionLevel is Adjustment Only | Error | read_source_primary_export | Any COA, calendar, period set, accounted period type, or currency differs from the primary | Align every required attribute to the primary | Yes, by user design |
| New secondary at any conversion level | Error | resolve_accounting_method_evidence | Either alias violates the conversion-level method policy or differs from the resolved user choice | Correct both aliases: blank code/type for BALANCE/JOURNAL; user method or omitted-input STANDARD_ACCRUAL/S default for SUBLEDGER/ADJUST; blank structural-create language | Yes, before approval |
| Secondary COA differs from primary | Error before Review and Submit | read_source_primary_export | No approved primary-to-secondary COA mapping is scheduled or available | Complete the dedicated mapping task after structural create | No in this task |
| Secondary currency differs from primary | Error before Review and Submit | read_source_primary_export | No explicit later default conversion-rate policy is scheduled | Select the rate type in the dedicated mapping task; do not default Corporate | No in this task |
| Secondary calendar differs from primary | Error | read_source_primary_export | Operational compatibility is unreviewed or an undocumented calendar mapping is proposed | Obtain reviewed design evidence; do not invent a mapping field | No |
| Both ledger aliases are changed | Error | read_source_primary_export | GL_PRIMARY_LEDGER.csv and GL_SECONDARY_LEDGER.csv do not contain the same complete SECONDARY row | Regenerate the symmetric row delta | Yes, before approval |
| Relationship row is created | Error | read_source_primary_export | Name, Name2, or Name3 is not the exact primary; Name1 is not the target secondary; any key is blank/unresolved; RelationshipEnabledFlag is not N, OrgIdTrans is not -99, or activation state is authored | Restore the documented disabled relationship shell and resolvable ledger keys for every conversion level | Yes, before approval |
| New Balance, Journal, or Subledger secondary baseline | Error | inspect_task_package | The new relationship's baseline rule is absent, duplicated, violates ora_defaulting_rules.md, or has inconsistent parent keys | Apply the documented conversion-specific baseline; no existing same-conversion secondary is required under the source primary | Yes, before approval |
| Existing or custom journal conversion rules | Error | inspect_task_package | New-create defaults overwrite existing rules, donor customizations are copied, or seeded rules are duplicated | Preserve existing rows; use the documented baseline for the new relationship and the mapping/UI handoff for requested custom rules | Yes, before approval |
| Optional BSV assignment is absent | Error | resolve_coa_structure_roles | Assignment rows are invented while BalSegValueOptionCode is A | Keep the assignment member unchanged or header-only | Yes, before approval |
| Package is prepared | Error | inspect_task_package | Member set, headers, aliases, row order, manifest, dependency closure, or unrelated rows drift | Rebase the smallest delta on a validated export | Yes, before approval |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_source_primary_ledger | Always | Exact PRIMARY identity and scope | ora_reference_lookups.md |
| check_ledger_name_availability | Always | Zero-match broader namespace evidence | ora_reference_lookups.md |
| read_source_primary_export | Always | Source policy, compatibility values, aliases, and relationship parent keys | ora_reference_lookups.md |
| verify_source_primary_options_complete | Newly FSCR-created source primary, before preview approval and import | Successful primary create/options receipts, retained earnings, Standard Accrual and English language readiness, triggered mandatory options, and alias parity | ora_reference_lookups.md |
| resolve_secondary_first_ledger_period | Always | Explicit or independently authoritative physical FirstLedgerPeriodName validated against PeriodNameId and PeriodType, plus complete eligible-period evidence | ora_reference_lookups.md |
| resolve_coa_structure_roles | Always | Exact COA task-export receipt, GL structure instance, and balancing/management segment-role metadata | ora_reference_lookups.md |
| resolve_accounting_method_evidence | Every new secondary | Conversion-level method tuple and exact evidence for an applicable user-selected method | ora_reference_lookups.md |
| inspect_task_package | Always | Current member, schema, alias, manifest, and scope evidence | ora_reference_lookups.md |

## Preview and Verification Contract

| Gate | Required Evidence |
|---|---|
| Preview identity | Environment, release, task code and name, source primary, exact raw secondary name, and conversion level. |
| Package diff | Member checksums for comparison only, exact row adds, zero unintended updates or deletes, and preserved dependency closure. Do not embed environment-specific checksum values in reusable guidance. |
| Field provenance | Every changed field labeled required user, conditional user, resolver derived, export derived or inherited, controlled role default, intentional blank, or service owned. |
| Approval | Explicit accountable approval bound to the exact preview fingerprint; any material edit invalidates approval. |
| Import | Submit once through the authorized task CSV executor; this rule graph alone does not authorize a write. |
| Monitoring | Track external process or object identity, last status, elapsed time, sanitized errors, and safe resume stage. |
| Re-export | Export the identical task scope and compare semantic identities, both physical aliases, conversion-level method tuple, inherited flags, Name/Name1/Name2/Name3, disabled relationship state, controlled rule-parent keys, generated IDs, defaults, and status. Manifest-only change is not success. |
| Verification export isolation | If Fusion cannot source-filter the populated identical-task export, stage it only in transient untracked storage, exact-filter the new secondary plus its exact primary-parent and relationship rows, persist only the filtered comparison, and discard the unfiltered package and every unrelated row. Fail closed on identity, parent linkage, cardinality, or alias ambiguity; never reuse verification rows as design input, defaults, or a carrier. |

## UI and Lifecycle Handoffs

| Boundary | Required Handoff |
|---|---|
| Source-primary ledger options | Secondary package preparation may overlap, but complete and verify the source primary Specify Ledger Options context before secondary preview approval or import. |
| Secondary ledger options | Complete the separate secondary Specify Ledger Options context after structural create; do not collect optional families here. |
| Different COA or currency | Complete Primary to Secondary Ledger Mapping with exact mapping and rate policy. |
| Custom source or category rules | Use the mapping UI when requested unless a separately reviewed exact rule contract is available. |
| Optional assignments or unsupported role variants | Import the supported baseline only, configure the requested feature in the Oracle UI, re-export, and revalidate before Review and Submit. |
| Activation and submission | Stop before Review and Submit, activation, relationship enablement, conversion enablement, or period opening. |

## Boundary Register

| Boundary ID | Status | Effect in This Task |
|---|---|---|
| GL-01 | Create policy defined; explicit method mapping must be evidenced | BALANCE/JOURNAL keep method fields blank. SUBLEDGER/ADJUST use the resolved user method or STANDARD_ACCRUAL/S when omitted; an unresolved explicit choice blocks rather than creating with another method. |
| TBD-GL-07 | Open | No writable Review and Submit contract exists; this task never activates or submits the accounting configuration. |
| GL-03 | Closed | Reporting-currency role shapes are documented; they are not secondary-ledger create defaults. |
| GL-09 | Closed | Optional ledger-option families use opt-in, preserve-or-disabled-baseline, and UI-handoff policy. |
| GL-12 | Closed | Posting cutoff remains disabled in baseline and is configured by UI when explicitly requested. |
| GL-13 | Closed | Only the proven controlled journal-rule scope is directly authored; custom rules use UI handoff. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MSL-050-ENFORCE-DESIGN | decision | 50 | design_enforcement | ready->MSL-060-EXECUTION-GATE;blocked->MSL-070-HANDLE-ERROR | MSL-040-APPLY-DEFAULTS | stop | Always |
