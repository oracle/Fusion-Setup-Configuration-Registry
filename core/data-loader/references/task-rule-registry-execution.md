# Task Rule Registry Execution

Use this guide after Task Hook's `data-load` route, or `resolve-task-rules`, selects a task. The registry controls
flow; its `ora_*.md` source contains the rule details. Do not infer an order
from Markdown headings or execute all nodes merely by sequence.

1. Read the returned `registryPath`, select the exact task, confirm its
   `readiness.status` is `ready`, and begin at `start_node`. A registry with
   missing Task Node references or other readiness blockers must not resolve
   into a rule plan.
2. Before executing a node, confirm each `prerequisite` passed and evaluate
   `applies_when`. Use only a declared outcome; never invent a transition.
3. Read the node's `source.file` and anchor, then execute its `action_type`:
   - `validate_input`: validate task data and the prepared load.
   - `resolve_dependency`: confirm the required dependency.
   - `reference_lookup`: perform only its declared read-only lookup, apply its
     match rule, save mapped values, and fail on no or ambiguous match.
   - `apply_default`: set only an unset value according to the rule.
   - `design_enforcement`: evaluate the stated policy against task state.
   - `error_handler`, `execution_gate`, or `evaluate_result`: apply the
     source-defined condition and result.
   - `terminal`: stop and return its outcome.
4. Record the node ID, evidence, change or output, and declared outcome. Follow
   exactly `transitions[outcome]`; a failure route or stop condition blocks the
   load unless the user explicitly waives that evaluated validation. For a user
   waiver, retain the failure evidence and record the affected rule resource as
   `status: "overridden"`, with an issue that identifies the user's waiver and
   reason. This may be used for any task-rule validation, including input,
   lookup, design-enforcement, and payload-contract rules. It does not alter the
   registry transition graph, erase the finding, or replace the separate
   approval required for a state-changing operation.
5. Aggregate evidence into one ordered `ruleResults` item per planned resource,
   with `source`, `status`, `issues`, and `changes`, before
   `build-task-preview`.

## Fusion GET Routing

Task Validation may perform a declared read-only Fusion `GET` when its selected
rule node requires it. Separately, when the user requests a read or query for
the selected task, the LLM may perform any declared read-only Fusion `GET` from
that task's `ora-resource` rules. This includes `reference_lookup` nodes and
declared GET operations in task REST-execution rules. In either case, route the
request through `core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`.
Use only the request path, query values, requested fields, and match behavior
documented by the selected task rule. If those declared lookups do not answer a
user-requested read query, the LLM may perform an additional read-only Fusion
`GET` through the same client. It must use a documented or otherwise confirmed
Fusion API contract; do not guess an unsupported endpoint, parameter, field, or
request method. Never bypass the shared client with a direct Fusion call.

For requests to `dataLoaderBusinessObjects`, `dataLoaderDataSets`, or
`dataSetErrors`, pass `--header REST-Framework-Version=9` on every delegated
client invocation. This includes their Describe, finder, child-resource, action,
and pagination requests, for both `latest` and versioned resource URLs, and
every retry permitted by the existing policy. This header requirement does not
authorize additional operations or retries.

`resolve-task-rules` is the gate. A user may explicitly waive any task-validation
failure, including missing or incomplete registry readiness, by using
`--allow-readiness-override`. The resulting preview must include an overridden
resource with the original failure evidence and the user's waiver reason; do not
silently parse around the error or omit it from the approval artifact.
