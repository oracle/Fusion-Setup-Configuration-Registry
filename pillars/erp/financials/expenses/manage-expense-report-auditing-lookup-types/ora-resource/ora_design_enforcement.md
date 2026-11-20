# Auditing lookup design gates

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Intake | All source-format and value issues resolved |
| 2 | Lookup preflight | Type, view, module, set, code population and retained-value checks verified |
| 3 | Candidate | Exact task metadata, four members, header order and row width; selected type/code rows only |
| 4 | Core handoff | Active Run Book and current Data Loader contract; immutable preview then its separate approval |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Every row | Error | resolve_auditing_lookup_references | Missing, stale, ambiguous or incomplete references | Refresh exact target evidence and correct scope | Local correction only |
| Existing code absent from export | Error | | No schema-complete preservation baseline | Obtain verified selected-row evidence; do not fabricate DFF or audit values | No guessed values |
| Translated meaning/description | Error | | Existing translations without resolved source language | Use a separately verified language-aware preparation flow | No silent translation rewrite |
| Candidate import | Error | | Task mismatch, bad headers/width, source conflict, inactive Run Book, missing core preview/approval | Correct preparation or core prerequisites | No direct POST fallback |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_auditing_lookup_references | Every candidate | Exact fresh type/view/module/set/code context and complete population | ora_reference_lookups.md |

Candidates do not replay unrelated codes or types. Selected existing type Meaning/Description
updates use full retained parent rows; type translations stay header-only to avoid stale
text replay. Verify session/export/import language and complete translation preservation
evidence. Type-only work does not require unrelated code/set collections. Preserve selected-code
non-input values from complete evidence; unresolved text-language changes stay blocked.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUDLK_DESIGN | step | 5 | design_enforcement | success->AUDLK_HANDOFF | AUDLK_DEFAULT | stop | Always |
