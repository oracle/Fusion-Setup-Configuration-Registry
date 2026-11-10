# Meals input validation

Use [ordinary Meals execution](../references/ordinary-meals-execution.md) for
the supported workbook and governed workflow.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Identity | Exact Policy Name and full rate key including unchanged existing Start Date/End Date | Stop | Supply exact portable identity; no case alias, duplicate key or rename | Selected rows | |
| Create group | One parent and at least one rate per new policy, Currency Code, explicit limit/enforcement/control choices, enabled amounts and effective periods | Stop | Supply complete create inputs for every new policy; multiple policies/rates allowed | New policies | resolve_policy_currency |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Workbook | Reject unknown sheets/columns, formulas, duplicate identities, removed inputs and conflicting associations with cell diagnostics; allow multiple policy/rate rows | Parse | |
| Encoding | Five input Booleans use explicit Yes/No to Y/N; enforcement labels map to UPPER/VIOLATION; rate date uses YYYY/MM/DD | Supplied fields | |
| Values | Finite decimals, name80/description240 character bounds, exact field domains; validate all resulting sibling rates, full/NoStart key uniqueness and nonoverlapping inclusive periods after preserving omissions | Create/update | |
| Package | Exact task,19entities/634ordered columns, safe archive paths and row widths; non-target entities header-only in candidate | Baseline/candidate | |

Business compatibility belongs to design enforcement. The fixed input schema is
[intake-fields.json](../references/intake-fields.json); encoding/identity evidence is
in [source notes](../references/source-notes.md).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| POLICY.VALIDATE | step | 10 | validate_input | passed->POLICY.REFERENCES;failed->POLICY.RETURN_ISSUES | none | stop | This task is requested |
