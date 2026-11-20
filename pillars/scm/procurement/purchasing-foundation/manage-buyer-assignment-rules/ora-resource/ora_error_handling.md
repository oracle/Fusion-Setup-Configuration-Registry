# Buyer Assignment Rule Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| A required input is absent | Identify the row and missing display field or accepted qualifier group; stop before submission. |
| A type, length, format, or choice check fails | Identify the row, field, expected type or limit, and observed type or length; request corrected input without rewriting it. |
| A Rule Sequence default lookup cannot return a usable highest sequence | Identify the read-only lookup failure or empty/non-numeric response; stop and request a supplied RuleSequenceNumber. |
| A later execution workflow reports a failure | Preserve the sanitized result and stop before retry; this resource does not authorize a retry. The declared sequence lookup is the only REST call in this resource. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| MISSING | Required display input is absent | Supply the identified display value |
| INVALID | Local row shape, type, length, numeric format, or choice check fails | Correct the supplied input and revalidate |
| FAILED | A downstream execution result is returned | Preserve diagnostics and use the declared workflow; do not retry automatically |
| SEQUENCE_DEFAULT_UNAVAILABLE | The highest RuleSequenceNumber cannot be read and incremented | Supply RuleSequenceNumber or resolve the read-only lookup failure |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Client validation | Row and field or group, expected constraint, observed type or length, and corrective action; avoid exposing sensitive input values. |
| Local defaulting | Disclose when an omitted or blank RuleSet was set to Default or when RuleSequenceNumber was derived from the highest returned sequence plus 1; supplied nonblank values remain unchanged. |
| Validation completion | Distinguish local input conformance from Data Loader source validation. A source is ready only after the registered business object accepts the display-value mappings and its derivations. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Reference value is unknown | Do not perform an undeclared live lookup or REST call, infer an ID, or claim reference eligibility. |
| Rule sequence or condition comparison needs existing rules | Do not claim uniqueness, duplicate detection, or specificity. |
| Input fails validation | Do not truncate, coerce, default, clear, copy, or silently correct any value. |
| Data Loader source validation fails | Do not construct or retain an upload ZIP. Correct the reported display value or mapping, then start a fresh validation session. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BAR.READY | terminal | 40 | terminal | none | BAR.APPLY_DEFAULTS | stop | All applicable local input checks pass and the conditional RuleSet default has been evaluated |
| BAR.INPUT_INVALID | terminal | 50 | terminal | none | none | stop | Input validation fails |
| BAR.SEQUENCE_DEFAULT_UNAVAILABLE | terminal | 60 | terminal | none | none | stop | A missing RuleSequenceNumber could not be derived from the declared live lookup. |
