# Return Routing Rules Error Handling and Handoff Gate

This task guidance stops handoff when its Business Object contract or rule identity is unresolved.

## Error Situations

| Situation | What Should Happen |
|---|---|
| REST import BO `returnRoutingRules` is not registered, the supplied `ReturnRoutingRules` spelling resolves ambiguously, or its live attributes and keys cannot be read | Classify as catalog mismatch or auth/authz as appropriate; stop and report the selected environment and failed metadata stage |
| A supplied field, status value, or existing-rule key is not confirmed by live Business Object metadata | Stop rule preparation; show the unresolved mapping without guessing |
| A reference value has no exact match or multiple matches in validated project data | Stop resolution and request a unique valid value |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before Data Loader import handoff | Exact target environment, operation, confirmed Business Object, immutable import artifact, validated fields and keys, preview result, and `core.data-loader` approval status |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Business Object registration, fields, keys, source validation, preview, or required approval are unresolved | Do not submit or retry an import |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RRR.EXECUTION_GATE | decision | 4 | execution_gate | ready->RRR.RETURN_PREPARED;blocked->RRR.RETURN_REFUSAL | RRR.RESOLVE_DEPENDENCIES | stop | After input and applicable lookup checks and before Data Loader handoff |
| RRR.RETURN_PREPARED | terminal | 5 | terminal | none | RRR.EXECUTION_GATE | continue | Validation and handoff checks passed; no import has occurred |
| RRR.RETURN_REFUSAL | terminal | 6 | terminal | none | none | continue | Required Business Object contract, reference value, or approval is missing |
