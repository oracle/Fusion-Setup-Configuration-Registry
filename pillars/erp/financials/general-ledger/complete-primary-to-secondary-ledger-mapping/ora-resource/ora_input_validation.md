# Complete Primary to Secondary Ledger Mapping Input Validation

## Lifecycle Position

| Topic | Contract |
|---|---|
| Purpose | Complete structural, rate, journal-conversion, and explicitly selected balancing-segment transfer policy for one existing primary-to-secondary relationship |
| Starts after | Primary and secondary ledger identities exist in the same scoped accounting configuration |
| Ends before | Review and Submit, confirmation, activation, conversion enablement, and period opening |
| Supported baseline | Validate and preview the smallest supported CSV delta; do not treat mapping completion as lifecycle approval |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Source primary ledger | Raw primary ledger name and exact accounting-configuration scope | Stop this task and identify the missing primary ledger | Ask for the exact primary ledger in the target configuration | Always | resolve_primary_secondary_relationship |
| Target secondary ledger | Raw secondary ledger name | Stop this task and identify the missing secondary ledger | Ask for the exact secondary ledger related to the selected primary | Always | resolve_primary_secondary_relationship |
| Directional chart-of-accounts mapping | Exact mapping name for the source COA to target COA direction | Block the different-COA path | Ask the user to select an existing exact directional mapping; never reverse or guess one | Source and target structure instances differ | resolve_directional_coa_mapping |
| Default conversion rate type | Exact conversion rate type display value | Block the different-currency path with the compared currencies | Ask the user to choose an exact eligible rate type; Corporate is not a default | Source and target currencies differ | find_conversion_rate_type_exact |
| Balancing segment conversion rows | Exact source balancing values and meanings for each requested row | Block only the requested balancing-segment conversion path | Ask for exact source values after resolving the source balancing value set | User explicitly selects controlled BSV conversion or replication | find_balancing_segment_value_exact |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Primary and secondary names resolve to one existing relationship in the selected scope | Satisfied | Continue with relationship-state validation | resolve_primary_secondary_relationship |
| Source and target use the same structure instance | COA mapping is intentionally blank | Record the GL-781805 warning decision before preview and do not fabricate Name4 | resolve_primary_secondary_relationship |
| Source and target use different structure instances | Directional mapping is required | Resolve exactly one source-to-target mapping from the scoped Financial Reporting Structures export | resolve_directional_coa_mapping |
| Source and target currencies differ | Rate type is required | Resolve exactly one eligible rate type before preview | find_conversion_rate_type_exact |
| Controlled BSV conversion is selected | Value-set and value evidence is required | Resolve the actual balancing ValueSetCode, then each exact effective source value | derive_balancing_value_set |
| Custom journal source or category policy is requested | Direct baseline is unsupported | Preserve existing rules and hand off custom include or exclude configuration to the UI; re-export before Review readiness | resolve_existing_conversion_rules |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Raw and normalized free text | Preserve raw input; whitespace-only is missing; do not trim internal whitespace, collapse characters, case-fold, or fuzzy-match ledger, mapping, rate-type, source, category, or segment display values | Every free-text input |  |
| Exact relationship identity | Require one relationship with the selected primary as source and selected secondary as target; validate ledger category, conversion level, currency, and the exact ten-column relationship parent tuple | Always | resolve_primary_secondary_relationship |
| Mapping direction | Require an exact From source COA to To target COA mapping; a reverse-direction or unrelated mapping is invalid | COAs differ | resolve_directional_coa_mapping |
| Same-COA warning | Keep Name4 blank only after an accountable GL-781805 decision acknowledges that this flow cannot later assign a mapping after confirmation | COAs are the same |  |
| Currency rate rule | Require one exact rate type when currencies differ; surface GL-781342 when absent | Currencies differ | find_conversion_rate_type_exact |
| Journal rule coherence | Preserve key and name pairs for source and category, UserUpdatableFlag, IncludeFlag, the relationship conversion flags, and the exact parent OrgIdTrans | Existing rules or controlled catch-all row | resolve_existing_conversion_rules |
| Controlled catch-all scope | Other source, Other category, UserUpdatableFlag Y, IncludeFlag Y is permitted only for the proven matching controlled Journal-secondary path; disclose it in preview and never synthesize it for arbitrary Subledger design | Controlled Journal-secondary relationship lacks a required role row |  |
| Balancing value validation | SourceSegmentValue and Meaning are mandatory per authored conversion row; require exact value-set membership, enabled status, effectivity for the requested date, and non-duplicate semantic key | BSV conversion row is requested | find_balancing_segment_value_exact |
| Relationship key preservation | Preserve the exported OrgIdTrans, whether -99 or -1, and every child-rule parent reference; assigning Name4 does not authorize a key rewrite or a RelationshipTypeCode change | Every existing relationship, including its first mapping assignment | resolve_existing_relationship |
| Initialization inputs | Initialization period and historical conversion type must be exact and present together where required | Historical initialization is explicitly selected |  |
| CSV aliases and serialization | Both 133-column ledger aliases remain unchanged and symmetric; preserve quoted multiline account segments, actual headers, header order, parent keys, header-only members, and the ASM manifest | Every package |  |
| Unknown fields | Reject fields not present in the current exported headers or a reviewed same-role contract; classify optional tree, replication, DFF, or segment-type fields as exact-evidence/UI-handoff boundaries rather than new open contracts | User supplies unsupported fields |  |

## Intake and Population Classification

| Class | Mapping Examples | Policy |
|---|---|---|
| Required user input | Primary ledger; secondary ledger | Never guess or replace with the first match |
| Conditional user input | Directional COA mapping; conversion rate type; BSV values; initialization policy | Ask only after the triggering difference or explicit feature selection |
| Optional user input | Custom journal policy; replication; DFF values | Never ask in baseline; require exact supported contract or UI handoff |
| Resolver-derived | Ledger IDs/categories; structure instances; currencies; rate type code; balancing ValueSetCode/value metadata | Populate only from exact eligible resolver receipts |
| Export-derived | Existing relationship tuple; existing rules; current OrgIdTrans; current conversion flags | Preserve unless the task owns a proven delta |
| Controlled role default | Matching-role relationship flags and controlled catch-all | Apply only to a same-release, exact-role new transition and disclose in preview |
| Intentional blank | Name4 when COAs match; optional initialization, tree, DFF, and conversion fields when not selected | Preserve blank; never fill for completeness |
| Service-owned | TargetLedgerId, target ShortName, audit, process, request, status, and metadata identities | Do not author; verify after re-export |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| GLMAP.VALIDATE | decision | 10 | validate_input | valid->GLMAP.DEPENDENCIES;invalid->GLMAP.RETURN_ISSUES | none | stop | Always |
