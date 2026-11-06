# Contribution Guidelines

## Purpose

These guidelines describe the workflow for authorized project contributors.
Public feedback and external contribution policies are defined in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

These guidelines define how FSCR contributors add, review, and merge reusable
Oracle Fusion implementation skills, catalogs, schemas, governance, and project
workspace templates. Contributions should preserve the repository layer
boundaries described in `AGENTS.md` and keep reusable implementation knowledge
separate from customer or project-specific outputs.

## Contributor Roles

| Role | Primary Responsibilities |
| --- | --- |
| FSCR repository owners | A-Team members and Pillar Development Leads jointly protect repository quality, access, review discipline, and merge readiness. |
| A-Team / core owners | Own the FSCR framework, `core/`, `shared/`, `router/`, `governance/`, `schemas/`, `knowledge/`, and reusable `project/` patterns. They add Pillar Leads to repository access, collaborate on framework contributions, review merge requests, and approve framework changes. |
| Pillar Development Leads | Own pillar quality under `pillars/`, participate in governance/schema/knowledge changes that affect pillar delivery, add pillar developers, and review merge requests from their pillar teams. |
| Pillar Developers | Create and enrich pillar skills under `pillars/`, use `pillar-skill-gen`, attach domain guidance through `fusionapps-resource-authoring`, and make skills functionally complete for the target offering, functional area, or setup task. |
| FSCR QA team | Validate functional behavior, golden scenarios, sample outputs, skill completeness, and QA gates before merge or release. |

## Placement Rules

1. Add Oracle offering and functional-area implementation intelligence under
   `pillars/{common,cx,erp,hcm,scm}/{offering}/{functional-area}`.
2. Add cross-pillar implementation methodology under repository-level `shared`.
3. Add technical execution primitives under `core`.
4. Add entry-point orchestration and routing skills under `router`.
5. Add reusable catalogs, dependency graphs, rules, generated hierarchy data,
   and templates under `knowledge`.
6. Add project workspace templates and sample artifact contracts under `project`
   only when they are safe for the reusable base repository.
7. Add schema changes under `schemas` only after architecture review.
8. Add contribution, naming, review, release, and design standards under
   `governance`.

## Skill Requirements

Each skill should provide:

1. A manifest aligned to `schemas/skill-manifest.schema.json`.
2. A manifest file named `SKILL.md`; do not add lowercase `skill.md` files.
3. Clear inputs and outputs.
4. Declared dependencies on other skills, catalogs, schemas, or core services.
5. Execution mode: `advisory`, `assisted`, `automated`, or `hybrid`.
6. Owner team and reviewer group.
7. Applicability by pillar, offering, functional area, country, industry, or
   Fusion release when relevant.
8. Side effects, required privileges, and execution boundaries for automated
   or hybrid behavior.
9. Test data, examples, fixtures, or golden scenarios when the skill performs
   validation, transformation, import, export, generation, or verification.
10. Workspace output metadata when the skill produces durable project artifacts:
    `persists_project_state`, `state_updates`, and `workspace_outputs`.
11. Error-handling expectations for automated, hybrid, validation, import,
    export, and generation skills. Use `governance/error-handling-guidelines.md`.
12. Pillar `ora-resource/ora_*.md` guidance files when a generated pillar skill
    needs source-aligned best practices, validation rules, dependency readiness,
    REST execution, design advisory, or error-handling guidance.

## Pillar Contributions

Pillar engineers should:

1. Use `core/fusion-dev/pillar-skill-gen/scripts/pillar_skill_gen.py` for
   catalog-backed functional-area and nested setup-task skill creation.
2. Use `core.fusion-dev.fusionapps-resource-authoring` to attach source-aligned
   Oracle FusionApps guidance under the generated skill's `ora-resource/`
   folder.
3. Enrich pillar skills with workflows, setup sequencing, dependency readiness,
   validation, reference lookups, defaulting behavior, CSV support behavior,
   REST execution guidance, diagnostics, manual fallback steps, and golden
   scenarios.
4. Follow the catalog hierarchy instead of flattening unrelated setup tasks into
   one large skill.
5. Reuse `core/`, `shared/`, and `router/` capabilities rather than duplicating
   primitives in a pillar folder.
6. Preserve generated metadata and only add authored guidance in supported
   extension locations.

When a pillar contribution depends on shared objects such as enterprise
structures, legal entities, business units, reference data, security,
integrations, reporting, or environment setup:

1. Reference the shared/common skill instead of copying logic.
2. Add missing shared requirements as a shared/common issue or pull request.
3. Identify the consuming pillar and setup object in the request.
4. Ask A-Team/core to resolve ownership if two pillars require different
   behavior for the same shared object.

## Framework Contributions

Contributions outside pillar-owned areas should be coordinated with the A-Team
or FSCR framework owners before implementation when they affect shared behavior,
automation primitives, routing, schemas, generated catalogs, project workspace
contracts, or governance.

Framework contributions should:

1. Use the same short-lived branch and merge request process as pillar work.
2. Keep changes scoped to the target repository layer.
3. Update related schemas, governance, templates, tests, or examples when the
   contribution changes a contract.
4. Include mandatory review from at least two FSCR owner-team reviewers.
5. Pass required QA gates before merge to `main`.

## Branching Model

All contributors should use short-lived feature branches and merge through a
reviewed merge request. Do not commit directly to protected branches.

Protected branches:

- `main`
- optional `integration`
- `release/<version>`

Feature branches should follow:

```text
<pillar-or-area>/<type>/<short-description>
```

Examples:

```text
scm/skill/item-master-setup
hcm/skill/worker-onboarding
erp/validation/legal-entity-readiness
shared/schema/artifact-index-v2
core/auth/fusion-session-helper
governance/docs/review-checklist-refresh
```

Recommended daily Git flow:

```bash
git fetch origin
git switch -c <feature-branch-name> origin/main
git status -s
git add <file-name>
git commit -m "feat(<area>): describe the contribution"
git fetch origin main
git rebase origin/main
git push -u origin <feature-branch-name> --force-with-lease
```

Use a normal push when branch history was not rewritten:

```bash
git push origin <branch-name>
```

## Merge Request Expectations

Every merge request should include:

1. Summary of the change and affected repository layers.
2. Jira story, task, or work item reference where applicable.
3. Skill IDs, generated paths, task codes, or setup objects affected.
4. Evidence that generated outputs are intentional and scoped.
5. Validation commands run and checks skipped with reasons.
6. Error-handling, retry, timeout, and diagnostic behavior when execution or
   automation is affected.
7. Security and data-safety statement for examples, screenshots, payloads, and
   project artifacts.
8. Required reviewers: Pillar Lead/SME, A-Team/core, QA, security, or
   publication reviewers as applicable.
9. When the MR adds, changes, moves, or removes one or more FSCR skills, a
   consolidated MR-scope report generated by `core.fusion-dev.fscr-merge-auditor`
   for the committed source branch and current target SHA.

## Skill Self-Audit Gate

Before merging a branch into its target branch, the developer must self-audit the branch
when it affects one or more FSCR skills under `router/`, `core/`, `shared/`, or
`pillars/`.

1. Commit the source-branch changes, check out that branch, fetch the target
   branch, and run `core.fusion-dev.fscr-merge-auditor` in MR scope with its
   number or link.
2. Inventory every MR commit and audit every affected skill in the complete
   merge-base-to-source diff; do not substitute a single-skill or single-commit
   report for the consolidated MR report.
3. Save the Markdown and JSON reports under `governance/audit-reports/`. The
   repository `.gitignore` excludes report contents; do not force-add them.
4. Attach the completed Markdown report to the merge request before reviewer
   approval and attach the JSON report when the merge-request system permits it.
5. Record both audited source and target SHAs in the report. Rerun the audit
   after either changes; a report with an older SHA must not authorize merge.
6. Resolve every blocker and major finding before requesting approval. Record
   any skipped check and its reason.
7. Require the reviewer or approver to confirm the report covers every MR
   commit and affected skill, matches the current source and target SHAs, and
   supports the stated verdict before approving merge to the target branch.

An MR audit compares the merge base of the recorded target and checked-out
source `HEAD`, inventories all commits in the MR range, and covers every skill
affected by the consolidated diff. It does not create temporary Git
repositories or archived worktrees.

## Review and Approval Expectations

1. Pillar skill contributions require at least two reviews: the responsible
   Pillar Development Lead or SME and an FSCR A-Team/core reviewer.
2. Framework, core, shared, router, schema, governance, knowledge, and project
   template changes require at least two FSCR owner-team reviews.
3. Peer review and cross-pillar peer review are recommended when a change
   affects common setup objects, shared methodology, or cross-pillar behavior.
4. Automated and hybrid skills require review of privileges, side effects,
   approval gates, retry behavior, timeout behavior, diagnostics, and redaction.
5. QA review is required when functional behavior, golden scenarios, public
   readiness, or release readiness is affected.

## Project Workspace Rules

1. Do not depend on chat history as the source of truth for project continuity.
2. Persist objectives, requirements, scope, task sequences, design decisions,
   configuration blueprints, exports, baselines, validation results, and reports
   under the local `project` folder.
3. Store generated artifacts under `project/{project_id}/artifacts` by mirroring
   the skill structure.
4. Store raw setup/configuration exports under `project/{project_id}/exports`.
5. Store curated setup/configuration baselines under
   `project/{project_id}/baselines`.
6. Create a new artifact version for major regenerated changes.
7. Update an existing artifact for minor regenerated changes only after user
   confirmation.
8. Never store credentials, secrets, tokens, private keys, tenant secrets, real
   customer data, or production-only sensitive values in the project workspace.

## Security and Data Rules

1. Do not commit credentials, keys, tokens, wallet files, private certificates,
   or tenant secrets.
2. Do not commit real customer data or identifiable customer configuration.
3. Do not include screenshots that reveal customer, employee, tenant, or
   environment details.
4. Do not document private or unsupported APIs as externally consumable patterns
   without approval.
5. Do not imply that FSCR performs unattended production configuration.
6. Store customer/project-specific outputs outside the reusable base repository.
7. Use synthetic data for examples, payloads, screenshots, validation artifacts,
   and golden scenarios.
8. Do not print or persist access tokens, token cache contents, client secrets,
   or full sensitive payloads in reports or logs.
