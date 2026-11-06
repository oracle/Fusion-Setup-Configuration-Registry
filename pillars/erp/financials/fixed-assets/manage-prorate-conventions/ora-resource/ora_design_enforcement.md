# Manage Prorate Conventions: Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Fiscal-year sequence | Before accepting any generated or archive-matched dates |
| 2 | Coverage and selected-variant integrity | Every basis; also apply the Half-year check when selected |
| 3 | Actual package row order | Proposed CSV rows before ZIP approval and actual immutable CSV rows before submission |
| 4 | Audit and package fidelity | Create/update readiness and parent-directed package validation |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Fiscal-year setup preservation | Error | | Preparation creates or changes fiscal-year setup instead of consuming the resolved intervals. | Return generation_failed. | No automatic repair |
| Fiscal-year sequence | Error | resolve_prorate_fiscal_year_range | The normalized intervals do not form one continuous non-overlapping sequence: each start must be no later than its end, and each next start exactly one day after the preceding end. Never invent absent years or trim boundaries. | Return generation_failed. | No automatic repair |
| Requested-scope coverage | Error | resolve_prorate_fiscal_year_range | Dates differ from supplied starting dates or requested row count, have gaps, overlaps or duplicate ranges, or exceed verified fiscal-year coverage. With no supplied scope, use the documented full-coverage defaults. | Report conflicts without changing supplied values. If verified coverage remains after the requested schedule, show the remaining months and ask whether to retain or extend it; never extend automatically. | No automatic repair |
| Half-year integrity | Error | resolve_prorate_fiscal_year_range | The returned or fallback midpoint is outside its own inclusive fiscal-year interval. Row count and exact tuples must also pass Requested-scope coverage. | Return generation_failed. | No automatic repair |
| Actual package row order | Error | | Dates do not use the business date-format default, parents are interleaved or differ from parent-file order, or a parent's rows are not strictly ascending by date-only StartDate with each next start equal to prior end plus one day. Check the actual serialized sequence, never a sorted copy; a correct tuple multiset alone is insufficient. | Return generation_failed. | No automatic repair |
| Audit integrity | Error | resolve_existing_prorate_parent | A proposed row fails [Audit-Field Defaults](ora_defaulting_rules.md#audit-field-defaults), or an audit mapping conflict is unresolved. This is a technical gap, not missing business input. | Return package_gap. | No automatic repair |
| Header and cell fidelity | Error | resolve_prorate_export_metadata | The package fails the parent's [CSV Encoding Fidelity](../../SKILL.md#csv-encoding-fidelity), changes header bytes/column order, drops or adds omitted audit columns, moves audit cells, or gives a data row a different field count than the header. | Return package_gap. | No automatic repair |
| Prepared package fidelity | Error | resolve_prorate_export_metadata | The prepared ZIP differs from template structure or the verified requested values/count, its date/flag formats do not follow Standard Defaults, or a detail row does not match exactly one same-package parent by convention and set. Check the actual package, not only its preview. | Return package_gap before submission approval. | No automatic repair |
| Immutable artifact | Error | | A supplied ZIP is repaired, deduplicated, reordered, replaced, or rebuilt. Corrections to a prepared package must return through existing parent review/approval gates. | Return package_gap. | No automatic repair |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_prorate_fiscal_year_range | Date integrity | Complete normalized exact-name fiscal-year intervals | ora_reference_lookups.md |
| resolve_prorate_export_metadata | Audit and package fidelity | Fresh export contract | ora_reference_lookups.md |
| resolve_existing_prorate_parent | Explicit-update audit integrity | Exact same-parent/detail evidence | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PRC.ENFORCE_DESIGN | decision | 25 | design_enforcement | checked->PRC.RESOLVE_PACKAGE;generation_failed->PRC.HANDLE_DESIGN | PRC.GENERATE_DATES | stop | Apply applicable Design Rules before readiness. A date-integrity failure selects generation_failed. Pass an audit or package_gap to PRC.RESOLVE_PACKAGE for its blocked outcome. Parent-directed actual-package validation reuses these checks before Final ZIP Preview and import approval. |
