# FSCR — Oracle Fusion Setup and Configuration Skills Registry

**FSCR helps customers, system integrators, and AI assistants turn Oracle Fusion
implementation questions into guided, reviewable work.**

Its shared foundation of reusable AI skills and guided workflows supports planning,
setup, configuration, and validation across Oracle Fusion Cloud Applications,
including ERP, HCM, SCM, and CX.

FSCR is separately released sample and reference material for planning and
configuring Oracle Fusion Cloud implementations. It is not an Oracle Fusion
Cloud product feature and is not covered by Fusion Cloud product support.

Use FSCR only with an Oracle Fusion Cloud environment that you are authorized
to access. You must configure your own environment connection, supply your own
authorized credentials, and have the permissions required for each operation.
FSCR does not include a Fusion environment or credentials. Review generated
plans, requests, and changes before running them in your environment.

## License

FSCR is released under the Universal Permissive License (UPL), Version 1.0.
See [LICENSE.txt](LICENSE.txt) for the full text.

## Binary Distributions

Developers choosing to distribute a binary implementation of this project are responsible for obtaining and providing all required licenses and copyright notices for the third-party code used in order to ensure compliance with their respective open source licenses.

The repository is organized to support:

1. End-to-end implementation orchestration.
2. Reusable core Fusion automation services.
3. Shared cross-pillar implementation methodology.
4. Independent ERP, HCM, SCM, and CX pillar contributions.
5. A local implementation project workspace that persists state and artifacts across sessions.
6. Standardized schemas, governance, and skill metadata.

## Getting Started

**Start with a question or an implementation goal.**

With this repository open in your AI assistant, describe what you want to
understand or accomplish.

### First-time users

Try questions such as:

- “Introduce me to FSCR and explain what I can do with it.”
- “Help me define the scope and requirements for an Oracle Fusion implementation.”
- “What information should I gather before starting configuration?”
- “Help me connect FSCR to my Fusion environment.”

### Returning users

Continue work in your saved project workspace with requests such as:

- “Resume my implementation project and summarize where we left off.”
- “What should I work on next, and are there any dependencies or blockers?”
- “Help me continue configuring [offering or functional area].”
- “Our requirements have changed. Help me assess the impact on the implementation plan.”

For guided setup and authentication help, see
[FSCR Onboarding](core/getting-started/onboarding/SKILL.md). Onboarding provides
guidance; environment enrollment and login execution follow the
[Fusion OAuth Authentication](core/auth/fusion-oauth-authentication/SKILL.md)
workflow and its checks.

## Software Requirements

FSCR skills require Oracle Fusion Applications Release 26D with the
06 November 2026 Weekly Maintenance Pack for Fusion Applications Update 26D,
or a higher release or maintenance pack.

## Prerequisites

Customers should use Python 3.11 or newer when running repository-provided
automation scripts.

Minimum compatible Python version:

```text
Python 3.10+
```

Recommended customer baseline:

```text
Python 3.11 or 3.12
```

Several scripts use modern Python type syntax such as `str | None` and
`list[dict[str, Any]]`, so Python 3.9 or older is not supported.

## AI Model Considerations

FSCR has been tested with the GPT 5.6 Terra Medium model. Performance varies
by model; select a model whose reasoning capability is appropriate for the
activity being pursued in FSCR.

## Repository Layers

| Layer | Purpose |
| --- | --- |
| `router` | Entry-point skills that classify implementation objectives, determine next actions, and orchestrate other skills. |
| `core` | Foundational technical services such as authentication, REST clients, ESS job handling, setup export/import, FBDI, HDL, and diagnostics. |
| `shared` | Cross-pillar methodology skills for intake, planning, baseline assessment, validation, best practices, integration, extensibility, conversion, reporting, and instance strategy. |
| `pillars` | Domain-specific ERP, HCM, SCM, and CX skills owned by pillar teams. |
| `knowledge` | Shared catalogs, rules, reference models, dependency graphs, prompts, and templates. |
| `schemas` | Machine-readable contracts for skill manifests and implementation artifacts. |
| `governance` | Contribution standards, review checklists, naming conventions, and release management guidance. |
| `project` | Local implementation project workspace for state, skill outputs, exports, baselines, decisions, and blueprints. |

For the full repository taxonomy and logical skill architecture, see
[SKILLS_TAXONOMY.md](SKILLS_TAXONOMY.md).

## Project Workspace Lifecycle

When users clone this repository for an implementation, the `project` folder is
their local workspace. Guided skills should not depend on chat history for
continuity. They should persist their outputs as project artifacts and update
`project/{project_id}/state/project-state.json` so the implementation can resume across
sessions.

Generated artifacts are organized under `project/{project_id}/artifacts` by mirroring the
skill structure:

```text
project/{project_id}/artifacts/{router|core|shared|pillars}/...
```

Examples:

```text
project/{project_id}/artifacts/router/project-objective-classifier/
project/{project_id}/artifacts/shared/project-intake/scope-definition/
project/{project_id}/artifacts/shared/implementation-planning/offering-task-map-builder/
project/{project_id}/artifacts/pillars/scm/product-management/
project/{project_id}/artifacts/pillars/scm/product-management/item-organizations/
```

Configuration exports are stored under `project/{project_id}/exports`, curated baselines
under `project/{project_id}/baselines`, design decisions under `project/{project_id}/decisions`, and
configuration blueprints under `project/{project_id}/blueprints`.

When a skill is revisited, major changes create a new artifact version. Minor
changes update the current artifact only after user confirmation.

## Contribution Model

Oracle-contributed canonical skills under `router/`, `core/`, `shared/`, and
`pillars/`, and content under `governance/`, `schemas/`, and `knowledge/`, are
read-only by default. Changes require explicit maintainer approval and repository
review. Keep implementation-specific artifacts and customizations in
`project/{project_id}`; a user request alone is not maintainer approval.

Pillar teams should contribute under their owning pillar folder. Reusable cross-pillar behavior should be proposed under `shared`. Technical execution primitives should be proposed under `core`.

Each skill should include a manifest that declares its inputs, outputs, dependencies, execution mode, owner, and applicability.
Skills that produce project artifacts should also declare `persists_project_state`,
`state_updates`, and `workspace_outputs` metadata.

## Recommended Skill Execution Modes

| Mode | Description |
| --- | --- |
| `advisory` | Produces guidance for implementors to execute offline. |
| `assisted` | Generates artifacts or recommendations that require human review. |
| `automated` | Performs approved actions directly through APIs, loaders, or jobs. |
| `hybrid` | Combines automated discovery or preparation with human approval. |

## Repository Status

This repository contains sample skills, scripts, reference material, and
workspace templates. Coverage and implementation depth vary by skill. Review
each workflow and its prerequisites before using it with your authorized Fusion
environment.
