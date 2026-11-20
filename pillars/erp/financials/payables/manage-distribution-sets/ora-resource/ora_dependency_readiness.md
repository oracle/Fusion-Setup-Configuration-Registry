# Dependency readiness


## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Owning enterprise and BU | Resolve exact header identity without guessing |
| 2 | BU primary ledger and COA | Establish coherence before account selection |
| 3 | Account and optional tax code | Preserve source-backed import mechanism and its effects |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| bu_composite | BU and enterprise | Yes | Create or update selection | Verify | Exact active BU preflight plus deterministic EnterpriseId; preserve uniquely matched export context on update | resolve_business_unit_context | Source import resolves BuName + EnterpriseId to OrgId; helper internal duplicates are not inferred | Use explicit row EnterpriseId, then current-run default, then one distinct nonblank fresh-export value; block ambiguity or conflicting defaults | BuName, EnterpriseId; OrgId remains internal |
| primary_ledger | BU primary ledger and COA | Yes | Every child | Verify | Owning BU/primary-ledger relationship and optional exact GET preflight | find_ledger_by_exact_name | Supplied SOBName cannot relocate the line | Require target evidence matching owning BU primary ledger and COA | SOBName retained; internal ledger/COA identifiers derived |
| account_transform | Distribution combination | Yes | Account or ledger context changes; new line | Verify | Exact ledger and ordered-segment validation receipt, or authoritative missing-account evidence and exact creation consent | validate_distribution_account | Source FSM transform resolves an existing combination or may create one during approved import | Invalid or indeterminate results block. For confirmed absence ask about creation, disclose it in the normal preview and require candidate approval before one FSM submission | DistCcidSegments retained; internal CCID verified as evidence, never a new CSV column |
| income_tax | Optional income-tax code | Conditional | Newly supplied or effectively changed nonblank Type1099 | Verify | Seed repository first, standard REST for unknown values; final income-tax validation in Fusion | find_active_income_tax_type | Description must resolve to one code; seed mapping is not live validation | Follow Income tax resolution policy. Unavailable REST permits an explicit code with disclosed warning; confirmed invalid/inactive or ambiguous values require correction. Blank/clear/omitted and unchanged existing values need no lookup | Exact Type1099 code and provenance; no automatic reference creation |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Required candidate-specific evidence established | Only documented read-only lookups or validation-only SOAP; any creation requires the separate approved FSM import |
| Blocked | Missing identity, ambiguous match, or incomplete required contract | No mutation; preserve exact gap |
| Verify | Candidate-specific checks required by the dependency rows, plus any requested additional preflight | Documented read-only GET or validation-only SOAP; no automatic create |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DS.DEPENDENCIES | decision | 40 | resolve_dependency | satisfied->DS.DESIGN;blocked->DS.ISSUES | DS.LOOKUPS | stop | Before candidate readiness |
