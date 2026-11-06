# Repository Agent Directives
## Scope
- Applies to the full FSCR Fusion Implementation Skills Repository unless a nested `AGENTS.md` overrides it.
- Preserve layer boundaries: `router` orchestration, `core` technical services, `shared` cross-pillar methodology, `pillars` domain/setup guidance, `knowledge` catalogs/reference data, `schemas` contracts, `governance` standards, and `project` workspace templates/artifacts.

## Repository Entry Point
- For FSCR onboarding, a general overview or introduction, public OAuth client (Mobile Application) setup, `core/auth/fusionEnv.properties` guidance, and any login or authentication questions or issues, begin with `core/getting-started/onboarding/SKILL.md`.
- Use onboarding's `references/iam-client-application-setup.md` for a guided journey with steps and diagrams to create the public client and populate the properties file. Use its `references/pkce-login-flow.md` for the Fusion environment enrollment overview, private trust policy, PKCE login, token acquisition, and troubleshooting.
- Keep explanatory and troubleshooting guidance in onboarding. When the user requests actual enrollment, login, or token renewal, hand execution to `core/auth/fusion-oauth-authentication/SKILL.md` under the active workflow and its checks; onboarding guidance is not authorization for external operations.
- For any implementation user request to start, begin, or work on an Oracle Fusion implementation in FSCR, begin with `router/implementation-router/SKILL.md`.
- Treat `router/implementation-router/SKILL.md` as the canonical implementation-workflow entry point. It classifies the objective and routes work to the appropriate `shared`, `core`, and `pillars` skills.

## Validation Questions and Guidance
- For questions about FSCR validation, prevalidation/environment readiness, implementation review, transactional tests/SVF, validation reports, evidence, ownership, prompts, skipping or reruns, begin with `knowledge/validation-rules/README.md` and the relevant sections of `knowledge/validation-rules/fscr-validation-faq.md`.
- Use the FAQ as explanatory guidance and cite the relevant section. Verify claims about current capabilities against the referenced skill manifests, contracts and scripts; distinguish implemented behavior, proposed work, limitations and illustrative examples. If they differ, explain the discrepancy rather than treating the FAQ as proof of executable support.
- A question about validation does not authorize a validation run, project creation or external calls. For an actual execution request, use the canonical implementation router and the selected skill's prerequisites and approval gates. Authentication-specific diagnosis still begins with onboarding.

## Product and Best-Practice Guidance
- For best-practice or product-guidance questions about specific Oracle Fusion pillars or offerings, consult the relevant content under `knowledge/product-guidance/` as the first reference source.
- After reviewing that guidance, use official Oracle Fusion documentation to research specifics, fill gaps, and verify release-dependent details. For every Oracle Fusion documentation lookup, verify and use the latest available Fusion release documentation for the relevant product and topic; do not assume a repository link, search result, or previously used release is current. If the topic is unavailable in the latest release documentation, explicitly identify the older release used and the gap. Distinguish repository guidance, Oracle-documented behavior, and implementation recommendations in the response.

## Skill Authoring
- Skill manifests are named `SKILL.md`; folders use lowercase kebab-case and skill IDs use dot-separated names.
- Align manifests with `schemas/skill-manifest.schema.json` and follow `governance/skill-design-standards.md`, `governance/contribution-guidelines.md`, and `governance/naming-conventions.md`.
- Declare inputs, outputs, dependencies, owner/reviewer metadata, execution mode, applicability, side effects, and workspace persistence when relevant.
- Use `advisory`, `assisted`, `automated`, or `hybrid` execution modes.
- Follow the latest-release documentation requirement above for all Oracle Fusion documentation references, including skill authoring, even if repository references point to older documentation versions.

## Project and Change Discipline
- Treat `project/{project_id}` as the durable workspace; persist outputs under `artifacts`, `exports`, `baselines`, `decisions`, or `blueprints`, and record durable runs under `project/{project_id}/state/runs`.
- For project workspace impacting work, if no implementation project exists, create one from `project/_template` named `draft_impl_project_<date>`, inform the user, and offer to rename it based on the implementation objective.
- For any project workspace impacting activity, track and report token usage in the prescribed token-usage log inside that project workspace.
- Never store credentials, secrets, tokens, or private keys in repository files or in a project workspace, even if gitignored. Never store customer data or production-only sensitive values in tracked repository files.
- Exports produced using FSCR skills, including FSM export ZIPs, must be stored under the current project's `project/{project_id}/exports/` directory. These exports may contain customer setup data or production-only configuration values required by the authorized workflow. Do not use `/tmp` or another location outside the current project as their durable destination. `project/.gitignore` excludes all project folders except `_template` from version control; keep project exports untracked and never force-add them or place them in `_template`.
- FSCR may retain an OAuth access-token cache only in the authentication service's approved local storage outside the repository, solely to reuse the token until it expires. Token files must remain outside the repository, including all project workspaces; a gitignored repository file is not an allowed cache location. Do not add the cache to version control, include it in diagnostics or artifacts, expose its contents in output, or use it for any other secret type.
- Keep edits scoped, preserve unrelated user changes, reuse `core` services, and update source scripts/catalogs when generated `knowledge` artifacts change.

## Project Workflow Enforcement
- **Do not deviate from the routed project workflow.** For an implementation request, begin with the required router, select the applicable project, core, shared, and pillar skills, and use the route, execution mode, and approval gates those skills declare.
- A reference lookup, REST path, OAuth configuration, token cache, browser capability, or available CLI is not an execution route. Do not call it directly unless the active workflow explicitly selects it and its prerequisites have passed.
- Do not bypass a missing, disabled, ambiguous, or incomplete workflow step by substituting a browser, direct REST call, loader, import/export utility, OAuth login, or another external integration. Record the gap under the project workspace and stop with the prescribed blocker and next action.
- External calls are permitted only when the active project workflow reaches its declared external-operation step. Before the call, complete the workflow's input, identity, privilege, catalog, payload, artifact, and approval checks; use its declared client or adapter; and persist the prescribed audit/diagnostic record.
- For a mutating external action routed through any skill other than `core/data-loader` or `core.runbook`, obtain explicit approval immediately before the declared execution step after presenting the exact target environment, operation, and payload or immutable import artifact. Do not treat approval for a plan, lookup, workspace artifact, or a different execution route as approval to bypass the workflow. Skip this additional approval gate for actions routed through `core/data-loader` or `core.runbook`, because their own approval workflows are authoritative and users must not be asked to approve the same task action twice.
- Browser navigation, OAuth login, token refresh, and read-only external requests must also be selected by the active workflow. They are not permissible as exploratory shortcuts or as a fallback when the workflow does not declare a live execution path.
## Error Handling Discipline
- For Fusion-touching, automated, hybrid, validation, import/export, generator, and durable-artifact workflows, classify failures as input validation, catalog mismatch, auth/authz, transport/environment, Fusion API, process timeout, process failed, artifact persistence, or approval blocker.
- Preflight inputs, environment identity, privileges, catalog flags, payload/ZIP shape, source paths, destination workspace paths, and approval requirements before side effects.
- Use preview, dry-run, or plan-first behavior when supported; explicitly gate live execution with side effects.
- Retry only known recoverable failures: refresh cached-token 401/403 once, and do not retry live POST/PATCH/DELETE, import, loader, or ESS operations without idempotency or explicit approval.
- On polling timeout, stop and report environment, operation, TaskCode or job, ProcessId/requestId, last status, elapsed wait, and next-check or retry path.
- For failed Fusion jobs, retrieve and persist ProcessLog/status payload when available; preserve partial successes with an errors array and nonzero status.
- Persist diagnostics under `project/{project_id}` with status, stage, failure class, message, recommended action, environment, artifact refs, and external IDs; redact secrets, tokens, private keys, and sensitive payloads.
- Fail closed on ambiguous catalog matches, destructive actions, overwrite conflicts, unsupported CSV flags, missing source guidance, or unsafe paths.

## Validation
- Run `git diff --check` before handoff.
- For skill-file refactors, verify manifest names/references are updated.
- For generator changes, validate with `--help` and a `--dry-run` where practical.
