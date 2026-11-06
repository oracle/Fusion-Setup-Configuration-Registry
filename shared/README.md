# Shared Skills

Shared skills contain cross-pillar implementation methodology and shared advisory capabilities.

Use this area for logic that applies to more than one pillar, such as intake, planning, validation, baseline analysis, reporting strategy, integration design, extensibility guidance, data conversion, localization, and instance strategy.

## Shared Areas

| Area | Purpose |
| --- | --- |
| `project-intake` | Shared intake patterns for requirements, scope, localization, enterprise structure, and integrations. |
| `implementation-planning` | Offering task maps, dependency resolution, setup roadmaps, waves, and readiness checklists. |
| `baseline-assessment` | Baseline extraction, fit-gap analysis, drift analysis, and environment comparison. |
| `setup-export` | Cross-pillar FSM CSV and setup-data export capabilities. |
| `setup-import` | Cross-pillar FSM CSV import, REST configuration import, and import monitoring. |
| `validation` | Shared setup, reference data, dependency, and completeness validation. |
| `best-practices` | Oracle-aligned process, risk, security, approval, and localization guidance. |
| `integrations` | Integration strategy and design guidance. |
| `extensibility` | Extensibility strategy and supported customization guidance. |
| `data-conversion` | Data profiling, mapping, cleansing, transformation, loading, and reconciliation guidance. |
| `reporting` | Reporting strategy, OTBI, BI Publisher, KPI, and operational report guidance. |
| `instance-strategy` | Instance, pod, refresh, migration, and release readiness guidance. |

Shared skills that gather objectives, requirements, scope, implementation plans,
or baselines must persist their outputs into the local `project` workspace using
the core project workspace skills. Downstream pillar skills should consume those
project artifacts instead of asking the user to repeat prior intake.

## Pillar Metadata Context

When a shared skill operates on offering, functional-area, or setup-task data,
it must resolve the matching pillar skill metadata before deciding output paths
or pillar-specific behavior. Use `pillars/*/<offering>/SKILL.md`,
`pillars/*/<offering>/<functional-area>/SKILL.md`, and setup-task metadata
files such as `pillars/*/<offering>/<functional-area>/<task>.md`. These
frontmatter fields provide `offering`, `functional_area`,
`functional_area_code`, `task_code`, and `task_name`.

Shared setup workflows should use those metadata values for project persistence
paths and future pillar-specific directives. Export paths should use kebab-case
metadata names, for example:

```text
project/{project_id}/exports/product-management/item-organizations/manage-item-organizations/
```

## Token Usage Tracking

Every shared skill activity must track token usage according to the skill
manifest's `token_usage_tracking` policy. When a shared skill writes project
artifacts or a skill-run record, include a `token_usage` estimate in the run
record and append or update the project token usage log at:

```text
project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md
```

Use exact tokenizer/API accounting when available; otherwise use the repository
default `chars/4` estimate and note any exclusions.

## Implementation Validation

- [Prevalidation](validation/prevalidation/SKILL.md):
  environment readiness and the run-or-skip gate before Run Book creation.
- [Implementation Review](validation/configuration-completeness-validator/SKILL.md):
  approved requirements, task evidence, actual setup and manual verification gaps.
- [Transactional Validation Coordinator](validation/transactional-validation-coordinator/SKILL.md):
  one explicitly selected pillar check/SVF, declared execution route and cleanup.
- [Implementation Summary and Evidence](validation/implementation-summary-and-evidence/SKILL.md):
  traceable HTML/JSON reports and scoped readiness.

Prevalidation is hybrid; the other validation workflows are assisted. Product
checks remain pillar-owned; missing live routes are blocked.
[Validation Reporting](../core/validation/reporting/SKILL.md)
provides local schema checks, assessment and report publication.
