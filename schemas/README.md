# Schemas

This folder contains shared JSON schemas for FSCR skill manifests and implementation artifacts.

Schemas should be treated as contracts. Changes should be reviewed by the platform architecture team and affected pillar teams.

## Knowledge Schemas

| Schema | Purpose |
| --- | --- |
| `product-guidance-reference-entry.schema.json` | Metadata contract for one URL reference entry rendered in a product-guidance Markdown file. |

## Project Workspace Schemas

The project workspace lifecycle is governed by these schemas:

| Schema | Purpose |
| --- | --- |
| `project-state.schema.json` | Durable current state for a local implementation project. |
| `project-artifact.schema.json` | Metadata for generated skill outputs and persisted artifacts. |
| `artifact-index.schema.json` | Project-level registry of generated artifacts. |
| `skill-run.schema.json` | Audit record for each skill execution. |
| `design-decision.schema.json` | Captures design decisions, alternatives, and consequences. |
| `configuration-baseline.schema.json` | Captures named setup/configuration baselines from exports. |

## Token Usage Contract

Skill manifests for `router`, `shared`, and `pillar` layers must declare a
`token_usage_tracking` policy. The policy records where token usage estimates
are persisted, the estimation method, and the fields required for each usage
entry.

Every activity performed by a router, shared, or pillar skill must include a
`token_usage` object in its skill-run record when a run record is written. If
the activity writes project artifacts, the same activity must also append or
update a token usage entry at the manifest's
`token_usage_tracking.default_location`.

Token usage entries must record `activity_start_time`, not only a date. Use an
ISO 8601 timestamp for the start of the activity, including a timezone offset or
`Z` when available.

Token usage estimates are operational estimates unless exact tokenizer or API
accounting data is available. The default repository method is `chars/4`.

## Implementation Validation Contracts

| Schema | Purpose |
| --- | --- |
| `implementation-validation-check.schema.json` | Normalized offering-owned setup or transactional check/SVF intake; no execution authorization. |
| `implementation-validation-run.schema.json` | Sanitized stage-specific evidence, requirement traceability, task outcomes, assertions, diagnostics and cleanup. |

These additive versioned contracts do not change the existing
`validation-result.schema.json`. The local reporting helper adds semantic
checks and derived readiness; see `core/validation/reporting/SKILL.md`.
