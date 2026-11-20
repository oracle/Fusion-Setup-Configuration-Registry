# Buyer Assignment Rule Reference Lookups

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_highest_buyer_assignment_rule_sequence | RuleSequenceNumber is omitted, null, empty text, or whitespace-only text after local input validation | No input value; current buyer-assignment rules in the target environment | /fscmRestApi/resources/latest/purchasingBuyerAssignmentRules?fields=RuleSequenceNumber&limit=1&onlyData=true&orderBy=RuleSequenceNumber:desc | RuleSequenceNumber | Read the sole returned row. Its RuleSequenceNumber must be a finite decimal number; add 1 to it. | RuleSequenceNumber | No returned row, missing or nonnumeric RuleSequenceNumber, more than one returned row, or a REST failure: stop and report that the sequence cannot be defaulted. |

The lookup is read-only. It uses the exact request path supplied for this task.
Do not run it when a nonblank RuleSequenceNumber is supplied.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BAR.LOOKUP_NEXT_SEQUENCE | decision | 20 | reference_lookup | resolved->BAR.APPLY_DEFAULTS;not_applicable->BAR.APPLY_DEFAULTS;unavailable->BAR.SEQUENCE_DEFAULT_UNAVAILABLE | BAR.VALIDATE_INPUT | stop | RuleSequenceNumber is missing; otherwise return not_applicable without a REST request. |
