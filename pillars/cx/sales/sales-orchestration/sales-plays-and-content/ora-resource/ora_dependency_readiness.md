# Sales Plays and Content Read Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Target environment | Confirm that the configured Fusion environment is the user's intended read target. |
| 2 | Operation-specific OAuth | Prepare the shared BOSS OAuth client for LIST, GET, or QUERY, or the task-local Knowledge Management wrapper that selects the `knowledge-management` token from the regular `scope` property for CONTENT_SEARCH, without exposing credentials. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| SPC.DEP.ENVIRONMENT | Target Fusion environment | Yes | LIST, GET, QUERY, or CONTENT_SEARCH | Satisfied | fusion_environment_context and core/auth/fusionEnv.properties |  | Read and search results must come from the intended environment. | Confirm the environment before the call. | Target environment identity |
| SPC.DEP.BOSS_OAUTH | BOSS OAuth configuration | Yes | LIST, GET, or QUERY | Satisfied | core.auth.fusion-oauth-authentication and core.fusion-api.rest-api-client |  | BOSS reads require boss_scope and the shared managed external profile cache (--token-cache auto), isolated by issuer/endpoints, client, target, and selected scope; no tokens belong in the checkout or project workspace. | Use the shared OAuth flow; never paste, execute, or persist a credential-bearing token command. | Authenticated BOSS client readiness |
| SPC.DEP.KM_OAUTH | Knowledge Management OAuth configuration | Yes | CONTENT_SEARCH | Satisfied | sales-plays-and-content/scripts/knowledge_rest_client.py with shared low-level OAuth and REST helpers |  | Content Intelligence reads the regular `scope`, selects the single token containing `knowledge-management`, and uses the shared managed external profile cache (`--token-cache auto`) for `/api/knowledge-management`, bound to the selected scope; no tokens belong in the checkout or project workspace. | Use the task-local Knowledge Management wrapper; never supply, echo, or persist a bearer token or Authorization header. | Authenticated Knowledge Management client readiness |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Target environment and the operation-specific BOSS or Knowledge Management OAuth configuration are ready. | Lookup only |
| Blocked | Environment is ambiguous or the applicable authentication configuration is incomplete. | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SPC.ACCESS | step | 2 | resolve_dependency | ready->SPC.SELECT_READ;blocked->SPC.ERROR | SPC.VALIDATE | stop | LIST, GET, QUERY, or CONTENT_SEARCH input validation passed. |
