# Customers Defaulting


## Default Rules

| Field | Default | Applies When | Override Behavior | Resolver |
|---|---|---|---|---|
| All emitted fields | No local business default; missing/null becomes an empty positional field | Offline normalization | Explicit supplied values are preserved |  |
| CUSTOMER_PROFILE_CLASS | Product source maps null to DEFAULT when populating profile interface rows; do not inject this in the CSV | Applicable 26D product-stage path | Preserve explicit class; reconcile actual assignment |  |
| PAYMENT_METHOD_PRIMARY_FLAG | Product source maps null to N for an emitted receipt-method interface row; do not inject this in the CSV | PAYMENT_METHOD_NAME is supplied | Preserve explicit Y/N; no requirement to supply a method for every row |  |
| Derived references and source-system code | Owned by the product; retain explicit references and do not synthesize a guessed source-code transformation | Product matching/defaulting | Inspect existing-target contract before treating blank and explicit references as equivalent |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ARCU.DEFAULTS | step | 20 | apply_default | preserved->ARCU.DEPENDENCIES;invalid->ARCU.ERROR | ARCU.INPUT | stop | After input validation |
