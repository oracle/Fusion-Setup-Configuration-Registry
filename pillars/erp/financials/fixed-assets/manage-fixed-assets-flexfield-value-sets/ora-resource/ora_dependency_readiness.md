# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---:|---|---|
| 1 | REST lookup | Retrieve the requested value sets and values through `core.fusion-api.apps-common.value-sets`; verify filters, pagination, and visibility before comparison. |
| 2 | REST definition metadata | Resolve one exact case-sensitive `ValueSetCode`, returned child links, and material definition/protection fields; use returned links unchanged and do not construct resource keys or paths. |
| 3 | Security and table metadata | Verify required settings from REST metadata and target import schema; unknown required properties block mutation. |
| 4 | Batch comparison | Compare all requested values locally with complete REST data. |
| 5 | Data Loader import path | Submit only the validated ZIP through core.data-loader after approval. |

## Package Readiness

Group package work by distinct ValueSetCode and requested values, not input
record. Use bounded, paginated retrieval for only the requested scope; do not
retrieve every value-set definition or start all-set exports for verification.

| Prerequisite | Required condition | Blocks Progress When |
|---|---|---|
| Package source | For a first-time definition, a current same-environment, same-release export containing `FND_APP_FLEX_VALUE_SET.csv`, `ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv`, and `ASM_SETUP_CSV_METADATA.xml` with the required members, headers, and metadata; zero data rows are valid. For an existing-definition amendment, use a populated export or a validated template/spec package with the complete reference-parent evidence in `ora_reference_lookups.md`. | The contract lacks a required member, header, or metadata item; or an existing-definition amendment lacks an authoritative parent-field source. A template alone is insufficient. |
| Package inventory | Record package members, row counts, ValueSetCode inventory, values per set, dependent-parent context, and one same-package FND_APP_FLEX_VALUE_SET.csv parent row for every value-row ValueSetCode. For bootstrap, record the template process identity and parent-row field-source evidence. | Approved scope has not been compared with the observed package or a value row lacks its definition parent row. |
| CSV package shape | Altered CSV members retain exact export headers, row widths, and valid quoting. | Any altered member is malformed. |
| Import readiness | Identify required members/columns, derived values and evidence, unresolved gaps, preview fingerprint, target environment, and approval state. | Any readiness item is unresolved. |

| Package member | Readiness requirement |
|---|---|
| `FND_APP_FLEX_VALUE_SET.csv` | Add or change only approved definition rows in export-supported form. Every value-row ValueSetCode must have exactly one matching definition row in this same package, even when its definition already exists in the target. A bootstrap parent row requires field-by-field authoritative evidence; no blanks, defaults, or REST-name guesses may replace an unresolved required or material existing field. |
| `ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv` | Add value rows only when approved scope includes Manage Values, the same immutable package contains exactly one matching FND_APP_FLEX_VALUE_SET.csv definition row, and dependent values also have their verified enabled parent value. |
| Relationship and validation-object/table members | Use the target-supported member contracts and apply the parent Fixed Assets Import Scope rule. |
| `ASM_SETUP_CSV_METADATA.xml` | Preserve its package shape. |

For a first-time definition, the current export and metadata establish only
the package contract. Construct each new definition/value field from validated
input, an explicit default in `ora_defaulting_rules.md`, or an intentional
blank. Do not treat a populated export row as a source for new-definition
values.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| VSET-EXISTING | Existing value set | Yes | After grouped REST retrieval, before package generation | Verify | Complete filtered REST definitions | find_value_set | Resolve identity and material fields before changes | Reuse compatible definitions; classify absent only with proven coverage; stop on ambiguous/differing definitions | returned definition, code, identifier, flags and existence outcome |
| VSET-SECURITY | Data security evidence | Conditional | SecurityEnabledFlag is Y | Verify | Nonblank DataSecurityObjectName and same-task export-supported security fields | resolve_value_set_metadata | A secured value set requires an explicit security object and target-supported package fields | Provide DataSecurityObjectName and target-supported security evidence, or disable value-set security | DataSecurityObjectName and supported security-field evidence |
| VSET-REFERENCE | REST lookup | Yes | Every reference batch and after successful import | Lookup | Current REST definitions and values with per-query coverage | resolve_value_set_metadata | REST is the existence and validation source | Batch needed codes and values; query the exact case-sensitive `ValueSetCode`, then follow returned child links and all pages; do not construct resource keys or paths; verify visibility before absence | definitions, values, supported fields and coverage |
| VSET-PARENT | Independent definition and parent value | Yes | Dependent validation | Verify | Verified REST parent definitions and values; or the same approved package for confirmed-missing parents | resolve_parent_value | A dependent value requires a matching parent | Supply the exact IndependentValueSetCode. Reuse a verified parent, or create the independent and dependent sets together only when the same approved package adds the exact independent definition and every enabled parent value referenced by the dependent rows. If no parent code is supplied, ask for it and stop. | IndependentValueSetCode, typed parent value, same-package parent evidence when used |
| VSET-TABLE | Validation-table definition | Conditional | ValidationType is Table | Verify | REST validationTable metadata and target import CSV schema | verify_table_validated_value_set_metadata | Table validation requires resolvable source and target-schema-required column metadata | Provide FromClause and ValueColumnName plus only the target-required optional fields; do not invent an ID, type, length, enabled, date, filter, or order-by field | FromClause, ValueColumnName, and target-required table attributes |
| VSET-DATA-LOADER | Data Loader authorization | Yes | Before any live import | Ready | Approved validated FSM ZIP and core.data-loader task-validation result |  | The FSM ZIP is package evidence only; it must not be submitted through a direct FSM import endpoint | Approve the exact package fingerprint and target environment | approved source path, checksum, preview, and Data Loader handoff |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Reuse | Compatible verified REST definition | Check requested values; additions still require supporting definition context |
| Create readiness | Complete effectively filtered REST retrieval with verified visibility proves no matching definition exists | Continue through package-readiness and approval gates |
| Create parent and dependent values together | A dependent set names an independent code confirmed absent by complete REST checks and the same immutable package adds the exact independent definition and every referenced enabled parent value | Continue with the package-readiness, and approval gates; verify both definitions and all parent-child values after import |
| Update decision | A matching code has a differing definition | Lookup only; require an update-or-new decision before package generation |
| Ambiguous | More than one candidate match or target state cannot establish a unique compatible definition | Lookup only; stop and resolve the ambiguity |

## Ownership Boundary

This file owns dependency order, package readiness, and the Data Loader handoff
gate. `ora_reference_lookups.md` owns grouped REST retrieval, returned-link
traversal, target-state comparison, and reference-parent package evidence.
`ora_input_validation.md` owns submitted definition/value shape and supported
FSM choices; `ora_defaulting_rules.md` owns first-time-definition defaults and
blank serialization; `ora_design_enforcement.md` owns package-design blockers;
and `ora_error_handling.md` owns failure classification, disclosure, recovery,
and post-import verification requirements.

`core.fusion-api.apps-common.value-sets` is this task's implementation client;
`shared.setup-export.task-level-export` supplies package-contract evidence; and
`core.data-loader` owns approval-gated import submission. Consuming setup tasks
delegate value-set verification to this task rather than invoking those
dependencies as alternate routes.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| VSET.RESOLVE_DEPENDENCIES | decision | 20 | resolve_dependency | ready->VSET.LOOKUP_EXISTING;blocked->VSET.HANDLE_DEPENDENCY | VSET.VALIDATE_INPUT | stop | Valid input |
| VSET.SELECT_PACKAGE_SOURCE | decision | 45 | resolve_dependency | export_contract->VSET.ENFORCE_DESIGN;reference_parent_bootstrap->VSET.ENFORCE_DESIGN;blocked->VSET.HANDLE_DEPENDENCY | VSET.APPLY_DEFAULTS | stop | A package is required. Use the current export contract, including valid header-only evidence, for a first-time definition. Select bootstrap only for values added to an existing resolved definition when its populated export is unusable and every bootstrap precondition is met. |
