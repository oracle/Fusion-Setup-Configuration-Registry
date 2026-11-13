# Focused candidate regression cases

Use when authoring or correcting amount-total validation, timestamp handling, or optional invoice fields. Instantiate the cases with the selected processor, currency scale, source contract and provider profile. Record the evidence for applicability; not-applicable is not a pass. These cases do not change a provider contract or mandate new behavior in unrelated engines.

| Area | Positive cases | Negative or conditional cases |
|---|---|---|
| Supplied monetary totals | Matching integer/decimal values; binary-sensitive fractions; multiple groups; aggregates above the per-payment maximum | Missing/duplicate/blank supplied values; nonnumeric/exponent syntax where disallowed; unsupported sign/scale; extra-precision mismatch that would disappear after rounding; a valid-scale one-minor-unit mismatch. Exercise both header and group totals where supplied. |
| Timestamps | Preserve existing accepted timestamps; preserve permitted positive/negative and boundary timezone offsets byte-for-byte | Invalid calendar/time values; malformed offsets; out-of-range offsets; offset boundary with nonzero minutes. Test excluded fractions or absent timezone according to the documented contract, not a global rule. No implicit timezone conversion. |
| Optional invoice fields | Net-only input only when source/provider optionality is evidenced; present gross/discount still reconciles | Missing required fields still fail. Present inconsistent gross/discount/net still fail. Do not substitute zero or a copied paid amount for missing gross/discount. Keep credit-note behavior separate. |

For a correction, freeze the previous candidate and test inputs, create a new version, and record the permitted behavior changes before execution. Rerun previous positive and negative cases and compare serialized output (or documented canonical equivalence when serialization changes are intentional). Existing accepted outputs, identifiers, grouping, amounts and optional-field suppression should remain unchanged unless the approved correction explicitly affects them. Add only affected-path tests; do not infer universal correctness from a passing synthetic fixture.

Keep customer/provider documents, synthetic run samples and candidate-specific results in the project/test workspace, not in shipped reusable references. Report actual executed checks separately from case specifications and bank/runtime acceptance.
