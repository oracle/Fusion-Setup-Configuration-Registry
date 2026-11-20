# Buyer Assignment Rule Defaulting Rules

Apply the requested RuleSet default and the conditional RuleSequenceNumber
default after input validation passes. The configurator supplies all other
intended display values.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| RuleSet | Default | RuleSet is omitted, null, empty text, or whitespace-only text | No; preserve every supplied nonblank value exactly | |
| RuleSequenceNumber | Highest returned RuleSequenceNumber plus 1 | RuleSequenceNumber is omitted, null, empty text, or whitespace-only text | No; preserve every supplied nonblank value exactly | find_highest_buyer_assignment_rule_sequence |

## Defaulting Boundaries

| Situation | What Happens |
|---|---|
| Rule-set input omitted or blank | Set the display attribute RuleSet to the literal text Default. The Data Loader business object derives RuleSetCode during its validation. |
| Nonblank rule-set input supplied | Preserve it exactly after type and length validation; do not trim, replace, or normalize it. |
| Rule-set input has an invalid type or exceeds its length limit | Fail input validation; do not replace an invalid supplied value with Default. |
| Rule Sequence input omitted or blank | Run `find_highest_buyer_assignment_rule_sequence`. Set RuleSequenceNumber to the returned RuleSequenceNumber plus 1. |
| Rule Sequence input supplied | Preserve it exactly after numeric validation; do not run the sequence lookup. |
| Sequence lookup has no usable result | Stop without assigning RuleSequenceNumber; disclose the lookup outcome and request a supplied sequence. |
| Other optional input omitted or blank | Preserve its state; no other default applies. |
| Duplicate action | Do not copy source values or clear RuleSequenceNumber. Apply only the RuleSet default when its own condition matches. |
| Requisitioning BU changed or cleared | Do not clear or derive any other attribute. |
| A value needs a reference lookup or transport mapping | Use the declared sequence lookup for RuleSequenceNumber. The registered Data Loader business object derives supported foreign-key and foreign-user-key values from supplied display attributes. |
| Packaging for upload | Keep the validated source workbook as the input to the Data Loader session. The session creates the upload ZIP in memory only after its final preview is approved. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BAR.APPLY_DEFAULTS | step | 30 | apply_default | applied->BAR.READY | BAR.LOOKUP_NEXT_SEQUENCE | stop | Apply RuleSet when omitted or blank and, only when RuleSequenceNumber was missing, assign the lookup result plus 1; otherwise preserve supplied values. |
