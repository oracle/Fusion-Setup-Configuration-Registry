# SVF / Validation Framework: Implementation and Remaining Tasks

Status: framework authoring and local report tooling implemented; live pillar integration and release review pending. No pillar skill or Fusion environment was changed.

## Implemented framework work

| Task | Owner | Deliverable | Requirement served |
| --- | --- | --- | --- |
| FW-01: Route validation requests | Framework | Updated implementation router and next-action planner | Distinguish implementation review, one transactional check, and reporting-only requests. |
| FW-02: Implement the assisted setup-review workflow | Framework, pillar semantic review | Updated `shared.validation.configuration-completeness-validator` | Trace requirements to tasks, expected setup, actual observations and manual gaps. |
| FW-03: Implement assisted single-check coordination | Framework | New `shared.validation.transactional-validation-coordinator` | Discovery, SVF applicability, one-check limit, declared routes, approval, skip and cleanup workflow. |
| FW-04: Consolidate evidence and explain results | Framework | New `shared.validation.implementation-summary-and-evidence` | Both stage reports, decisions, provenance, exclusions and owned follow-up actions. |
| FW-05: Add local assessment/report publication | Framework | New `core.validation.reporting`, standard-library CLI | Validate consistency, derive readiness, generate HTML/JSON, register artifacts and log reporting tokens. |
| FW-06: Define additive check/run contracts | Framework architecture | Two new versioned JSON schemas and common references | Product-owned check intake, requirement traceability, manual outcomes and cleanup; legacy result schema unchanged. |
| FW-07: Verify local behavior | Framework QA | Synthetic tests and fixtures | Missing coverage, false PASS, one-check limits, uncertain outcomes, cleanup, safe HTML and publication rollback. |

These skills are assisted workflows. The reporting CLI is executable local tooling. No generic live executor, automatic evidence collector, product API route, SVF adapter or transactional test has been added.

## Remaining delivery tasks

| Task | Accountable owner | Required outcome before closure |
| --- | --- | --- |
| FW-08: Review shared contracts and readiness policy | Framework architecture owner + affected pillar leads | Confirm schema semantics, required/blocking policy, manual/skip extension and report content. |
| FW-09: Assign named pilot owners | Framework lead + HCM lead | Select project, environment, HCM scenario and evidence sources; replace role assignments with names and dates. |
| FW-10: Integrate existing evidence services in the pilot | Framework developer + Run Book/Data Loader owners | Demonstrate routed status reads and safe normalized input without changing their approval/persistence policies. |
| FW-11: Accept pillar definitions | Pillar lead; framework intake review | Supply product correctness rules, one transaction/SVF, supported route, payload enforcement, assertions and cleanup. Framework does not author these pillar deliverables. |
| FW-12: Exercise the live pilot through approved routes | Pillar developer + implementer + QA | Prove setup mismatch detection, one bounded transaction, read-back, timeout/duplicate handling and cleanup. |
| FW-13: Review and release | Framework repository owners + QA | Complete required MR-scope skill audit on the committed branch and target SHA, owner reviews and Jira acceptance assessment. |
| FW-14: Validate reuse in a second offering | Framework lead + second pillar lead | Reuse common contracts/reporting without copying framework code. |

No Jira issues, assignments, due dates, commits or merge requests were created by these local changes. The tasks above are a reviewable delivery checklist, not externally assigned work.

## How to exercise the local tooling

From the repository root, using Python 3.10+:

```bash
python3 -m unittest discover -s core/validation/reporting/tests -v
python3 core/validation/reporting/scripts/validation_report.py --help
python3 core/validation/reporting/scripts/validation_report.py --check-definition core/validation/reporting/references/example-check-definition.json
python3 core/validation/reporting/scripts/validation_report.py --input core/validation/reporting/references/example-implementation-review.json --dry-run
python3 core/validation/reporting/scripts/validation_report.py --input core/validation/reporting/references/example-transactional-validation.json --dry-run
```

Fixtures are synthetic; a green fixture assessment is not implementation evidence. Real publication requires a selected, initialized local project and a sanitized run envelope. Use a fresh run ID:

```bash
python3 core/validation/reporting/scripts/validation_report.py --input /path/to/sanitized-run.json --publish
```

This writes local reports only. It cannot run a transaction. HTML shows evidence references as inert text; upstream reports and source artifacts remain independently owned.

## Skill index

- [Implementation Router](../router/implementation-router/SKILL.md)
- [Next Action Planner](../router/next-action-planner/SKILL.md)
- [Implementation Review](../shared/validation/configuration-completeness-validator/SKILL.md)
- [Transactional Validation Coordinator](../shared/validation/transactional-validation-coordinator/SKILL.md)
- [Implementation Summary and Evidence](../shared/validation/implementation-summary-and-evidence/SKILL.md)
- [Validation Reporting](../core/validation/reporting/SKILL.md)
- [Delivery guide and ownership flow](svf-validation-delivery-guide.md)
