# Core Skills

Core skills provide foundational Fusion Cloud automation capabilities used across all pillars.

Pillar teams should consume core skills instead of duplicating authentication, API, ESS, FBDI, HDL, file transfer, project workspace, or diagnostic logic.

## Core Areas

| Area | Purpose |
| --- | --- |
| `auth` | Authentication profiles, credential validation, and token handling. |
| `getting-started` | Initial implementation setup capabilities, including first implementation users and startup gates. |
| `fusion-ai` | Fusion AI Studio workflow agent invocation and tracking primitives. |
| `fusion-api` | REST, FSM REST, ESS, and API error handling primitives. |
| `data-loaders` | FBDI, HDL, spreadsheet loader, and file-transfer primitives. |
| `diagnostics` | Environment health, role access, and instance capability checks. |
| `fusion-dev` | Fusion development utilities, repository onboarding, catalog and hierarchy-browser management (`fusion-dev/catalog-management/`), and skill generation helpers. |
| `project-mgmt` | Local project state, artifact registry, artifact versioning, and configuration baseline management. |

## Local Validation Reporting

[Validation Reporting](validation/reporting/SKILL.md) validates sanitized
implementation evidence and publishes HTML/JSON with project audit metadata.
It does not contact Fusion or supply a live test runner.
