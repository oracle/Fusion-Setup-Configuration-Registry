# Meals reference lookups

Use [ordinary Meals execution](../references/ordinary-meals-execution.md) for
the supported workbook and governed workflow.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_policy_currency | Selected parent create/update, including retained currency for rate-only update | Exact code, target origin, validation date and operation-bound evidence | GET /fscmRestApi/resources/11.13.18.05/currenciesLOV through declared core REST client | CurrencyCode, CurrencyFlag, EnabledFlag, StartDateActive, EndDateActive | Complete pages; unique exact code; monetary/enabled Y and active at date | No generated input; hash-bound eligibility evidence only | Stop on absent, duplicate, inactive or incomplete evidence; auth/transport failure is unavailable evidence |

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_policy_enforcement | Supplied label | Fixed intake display mapping | Reimburse upper limit when expense exceeds defined rate to UPPER; Generate policy violation when expense exceeds defined rate to VIOLATION | Exact parsed code | Reject unknown values; no inferred choice |

Only currency eligibility is externally resolved. Role, geography, season,
gender and multi-currency inputs are unsupported. No captured result grants
import approval. See [currency contract](../references/currency-reference.md).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| POLICY.REFERENCES | step | 20 | reference_lookup | passed->POLICY.DEPENDENCIES;failed->POLICY.RETURN_ISSUES | POLICY.VALIDATE | stop | This task is requested |
