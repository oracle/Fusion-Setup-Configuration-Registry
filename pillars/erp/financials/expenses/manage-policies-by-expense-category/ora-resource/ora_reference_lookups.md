# Expense policy reference lookups


Use [ordinary Meals execution](../references/ordinary-meals-execution.md) for
the supported workbook and governed workflow.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_policy_currency | Selected parent create/update, including retained currency for rate-only update | Exact code, target origin, validation date and operation-bound evidence | GET /fscmRestApi/resources/11.13.18.05/currenciesLOV through declared core REST client | CurrencyCode, CurrencyFlag, EnabledFlag, StartDateActive, EndDateActive | Complete pages; unique exact code; monetary/enabled Y and active at date | No generated input; hash-bound eligibility evidence only | Stop on absent, duplicate, inactive or incomplete evidence; auth/transport failure is unavailable evidence |
| resolve_expanded_policy_lookup | Expanded-category field mapped to an Expenses standard lookup in intake-fields.json is supplied or retained by the selected operation | Exact entity, field, lookup type, code, target origin, workbook/baseline/contract hashes and selected operation | GET /fscmRestApi/resources/11.13.18.05/standardLookups with LookupTypeFinder; follow returned lookupCodes and selected code's lookupsDFF child links through the declared core REST client | LookupType, ModuleId, LookupCode, EnabledFlag, ViewApplicationId, SetId, links, count, offset, hasMore | Unique exact type/code; Expenses module 47110F64AC0608E2E040449823C60DB6; enabled Y; application 0 or 10016 and set 0; complete responses; exclude FIRST for EXM_TICKET_CLASS; verify operation-bound hashes and request paths | Recomputed eligibility evidence only; no default substitution or FSM write-acceptance inference | Stop on absent, duplicate, disabled, wrong-context, changed, incomplete or unavailable evidence; do not infer eligibility from dropdown membership |
| resolve_mileage_country | Mileage CountryCode supplied or retained by the selected operation | Exact territory code, target origin and operation binding | GET /fscmRestApi/resources/11.13.18.05/territoriesLOV with TerritoryCodeAllRowsFinder;TerritoryCode=the exact code | TerritoryCode, TerritoryShortName, EnabledFlag, count, offset, hasMore | Complete response; unique exact code and EnabledFlag Y. A matching TerritoryCodeFinder result alone is not eligibility. No unsupported ObsoleteFlag restriction | Verified territory code only; never replace with display name | Stop on missing, duplicate, disabled or unavailable evidence |
| resolve_mileage_company_rates | The selected resulting Mileage parent enables company rates and its retained or selected ADDITIONAL rows consume codes | Exact resulting AdditionalRatesListCode and every consumed existing AdditionalRateCode; workbook/baseline/runtime/target/date binding | GET standardLookups with exact LookupTypeFinder; follow returned lookupCodes and each consumed code's lookupsDFF child link through the declared core REST client | LookupType, CustomizationLevel, ModuleId, LookupCode, EnabledFlag, ViewApplicationId, SetId, links and complete collection metadata | Exact U/E type in the Expenses module; every code enabled Y with unique application 0 or 10016 context and explicit integer SetId. No source-backed fixed SetId or active-date filter is imposed. Recompute the complete consuming sibling set | One operation-bound parent receipt covering all consumed codes; no arbitrary type, default or omitted-sibling waiver | Stop on missing, ambiguous, unsafe, changed or incomplete context; target capture is still required for the exact operation |

## Operation-bound evidence input

Expanded-category lookup evidence is supplied to offline preparation using
`--lookup-receipts` on `build_fsm_from_workbook.py` and
`check_candidate_rules.py`, or the optional `policyPreparation.lookup_receipts`
file path on the public adapter. The JSON index maps exact entity, policy name,
operation (`create` or `update`), and CSV field to an absolute receipt path.
The adapter binds both the index and each receipt to the reviewed design.
Every used receipt must independently match the workbook, baseline, runtime
contract, catalog, target, date, field and resulting value. An index does not
waive missing operation contracts or enable an unqualified category.

`capture_policy_lookup.py` writes a plan by default. Select `--execute` only
at the routed reference-lookup step after its input, target and provenance checks.
The command captures supplied and retained references through the cache-only
core HTTP API. The Mileage company resolver derives its type and complete
consuming code set from the resulting parent and existing rates; see the
[company lookup contract](../references/mileage-company-lookup-contract.json).
Offline resolver tests do not constitute a fresh target receipt or import qualification.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_policy_enforcement | Supplied label | Fixed intake display mapping | Reimburse upper limit when expense exceeds defined rate to UPPER; Generate policy violation when expense exceeds defined rate to VIOLATION | Exact parsed code | Reject unknown values; no inferred choice |
| resolve_entertainment_field_behavior | Entertainment field behavior supplied | Reviewed EXM_FIELD_BEHAVIOUR seed and intake mapping | Hidden to DISABLED; Optional to ENABLED; Required to REQUIRED | Exact parsed code | Reject unknown choice |
| resolve_entertainment_period_month | Yearly reset month supplied | Reviewed MONTH binding and same-task export codes in intake mapping | January through December to 01 through 12; never UI selection index | Exact parsed code | Reject unknown month |
| validate_expanded_period_month | Active yearly reset on an expanded-category resulting parent | Existing or supplied month/day | Validate local calendar month and day, preserving the exact existing month representation. MONTH target-code eligibility is not claimed by this local check | Local validation evidence with target_eligibility_verified=false | Stop on invalid active calendar values; preserve unchanged inactive reset values |

Entertainment uses resolve_policy_currency for both CurrencyCode and
NumOfAttendeesCurrCode, when applicable, including retained references. Bind
each exact code to its parent operation; a receipt does not qualify CSV writes.

For the previously qualified categories, only currency eligibility is externally resolved. Role, geography, season,
gender and multi-currency inputs are unsupported. No captured result grants
import approval. See [currency contract](../references/currency-reference.md).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| POLICY.REFERENCES | step | 20 | reference_lookup | passed->POLICY.DEPENDENCIES;failed->POLICY.RETURN_ISSUES | POLICY.VALIDATE | stop | This task is requested |

Accommodations follows the same task workflow with category-specific parent/rate
identities and currency evidence. Daily Limit? must remain Yes on every populated
Accommodations policy row; it is a grey workbook-only indicator, never a CSV
flag. Each resulting rate requires DailyLimit. Role, location, seasonal rate and
gender determinants are excluded; reject incompatible retained settings. Use
[Accommodations evidence](../references/accommodations-profile.json) for the
local authoring extension and its mandatory live reconciliation boundary.
