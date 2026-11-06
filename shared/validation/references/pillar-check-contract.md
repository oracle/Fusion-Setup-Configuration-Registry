# Framework intake contract for pillar checks

This reference defines what the framework accepts; it does not create or edit pillar content.

Normalize a reviewed offering check into `schemas/implementation-validation-check.schema.json`. Keep the original Markdown or SKILL.md as `source_ref`. Validate the normalized definition before offering execution. A schema-valid definition is still not proof that its API/client is supported: resolve and read the declared workflow, confirm ownership/current product references and pass its prerequisites.

| Required area | Intake requirement |
| --- | --- |
| Identity | Exact check ID/version, offering/pillar, source, owner, reviewer and applicability. |
| SVF | `source_kind: svf` only for a reviewed Starter Validation Flow; identify its source/version and supported route. Otherwise use `pillar-check`. |
| Intent | Purpose, explicit lifecycle boundary/exclusions, requirement/task references and required/blocking policy. Task references do not make this a setup task or prove requirement coverage outside the selected check. |
| Inputs | Minimum fields, operation-specific required-value constraints, source strategy and existing prerequisites. Declare supported reference checks where needed; do not guess ambiguous values or imply that metadata alone proves referenced records exist. |
| Execution | API workflow/client and operation, or explicit manual/artifact procedure; timeout and poll bounds where relevant. Setup checks must be read-only. |
| Assertions | Stable assertion IDs, approved expected outcome/value/relationship, supported verification procedure and evidence requirements. Keep task status, load/job state, row/object outcomes and actual-value assertions distinct. HTTP status alone is insufficient. |
| Limits | Maximum one primary transaction; actual-payload enforcement, bounded intrinsic children, synthetic marker and duplicate strategy. |
| Effects | Notifications/workflows and lifecycle boundary; no additional independent prerequisite creation. |
| Cleanup | Evidence before cleanup, supported route, instructions, exact-record targeting, separate authorization, retention policy and owner. Preserve cleanup outcome independently of the business-check result. |

The reporting helper's `--check-definition` validates the normalized schema locally. It does not grant permission, inspect a live request or register an execution adapter.

Manual alternatives are separately declared procedures, not a fallback inferred by the framework. They use the same one-check/one-transaction rules. Document the performer, actual effects, evidence and cleanup. A user may skip; preserve the decision and unverified scope.

Results must include observed assertions, evidence provenance and observation time, owner and next action for incomplete coverage. Missing or conflicting evidence does not become PASS. If a needed prerequisite failed in an earlier review, supply current correction/read-back evidence before execution; do not erase the earlier report or treat an unrelated passing task as resolution.

The framework may include the result in a local executive index of explicitly selected historical reports. This does not authorize a batch of tests or aggregate their assertions into wider business coverage. Pillars retain ownership of scenarios, business correctness, supported routes and cleanup; core services retain ownership of metadata, task hooks, status and execution controls. Never require report consumers to retain Data Loader payloads, hashes, previews or approval envelopes.

When missing, return specific fields the pillar must supply and owner/next action. Do not edit pillar skills during framework implementation. No generic product scenario, catalog task code, API path or privilege may be invented to fill a gap.
