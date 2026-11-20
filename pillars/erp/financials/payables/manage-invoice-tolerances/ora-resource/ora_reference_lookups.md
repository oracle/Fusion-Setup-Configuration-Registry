# Reference Lookups

## Tolerance Type

No lookup GET call or separate resolver is required for this task. Validate locally against the two fixed values from the same-task CSV contract:

| UI label | `ToleranceType` CSV code |
|---|---|
| Quantity based | `QUANTITY BASED` |
| Amount based | `AMOUNT BASED` |

The generic adapter normalizes either label or exact code to the CSV code. Reject any other value before preview; do not choose a type from the UI’s initial selection. Fusion validates the submitted code during import, so preserve any actual loader error and verify the post-import value.

## Selected Fusion target and authentication profile

Before preparing exports or task data, retain the independently confirmed Fusion
environment name and credential-free HTTPS origin in the project target context.
Retain the selected OAuth `environment` value separately as the authentication
profile. The names may be unrelated (for example, profile `DEV` and Fusion
environment `example-fusion`). Reuse a previously confirmed target; ask for its
actual identity only when it is missing or ambiguous. Never derive it by removing
a profile suffix or guessing from a hostname, ZIP or reference receipt.

Pass the actual selected Fusion name to task manifest/target-validation inputs,
and require it to match export `ProcessEnv`. Require the selected origin to match
the authenticated configured origin. Compare the login profile only with the
profile bound to the Data Loader preflight; do not compare it with `ProcessEnv`.
Keep task, release/schema, Run Book, archive-integrity and approval checks intact.
If a workflow accepts `referenceContext`, supply the separately selected target
there; do not invent that CLI option for adapters that do not declare it. This
identity handling grants no additional execution or import capability.
