# Defaulting rules


## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| TotalPercentDistribution | Application default: 100. Allowed explicit values: 0 or 100. | Create: explicitly include 0 or 100 in the FSM import file. Child-line percentages must add up to that value. Do not leave the field out: whether FSM applies the default when omitted has not been verified. | No |  |
| DistributionSetLineNumber | Application default: 1; supply explicit line numbers | Create: require explicit unique line numbers until FSM omission behavior is qualified | No |  |
| SOBName | No fixed default; derive the ledger from the owning header | Create or null internal ledger; retain BU primary-ledger coherence | No |  |

Preserve omitted update fields; do not zero-fill or default from exported frequency.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DS.DEFAULT | step | 20 | apply_default | complete->DS.LOOKUPS;invalid->DS.ISSUES | DS.INPUT | stop | After input validation |


Omission of an update field preserves the baseline value. An explicitly requested empty optional InactiveDate is a clear, and is serialized and verified as such. A missing create header total or line number is still a required input; this runtime does not infer either from generic test defaults.
