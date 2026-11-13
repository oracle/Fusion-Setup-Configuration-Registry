# Sales Play Knowledge Management REST API Instructions

Use this instruction file for the task's only Knowledge Management operation:

```text
POST /api/knowledge-management/v2/contentIntelligence
```

Invoke these endpoints with the single scope token containing
`knowledge-management` from the regular OAuth `scope` property in
`core/auth/fusionEnv.properties`. Use the task-local wrapper instead of the
BOSS client so the exact method, relative path, and fixed search contract are
validated before authentication.

## Script

Run from the repository root:

```bash
python3 pillars/cx/sales/sales-orchestration/sales-plays-and-content/scripts/knowledge_rest_client.py \
  '/api/knowledge-management/v2/contentIntelligence' \
  --method POST \
  --header 'Content-Type=application/json' \
  --body '<serialized-request-body>'
```

## OAuth Scope and Cache

The script reads the regular `scope` from:

```text
core/auth/fusionEnv.properties
```

It splits that value on whitespace and uses the single scope token containing
`knowledge-management` to acquire the OAuth token. If no matching scope token
or more than one matching scope token exists, stop before requesting a token and
fix the `scope` property.

The default `--token-cache auto` delegates storage to the shared OAuth service
at `~/.fusionaim/<profile-fingerprint>_token.json`, outside the repository. The
fingerprint binds the approved issuer/endpoints, client, target, and selected
scope, keeping the Knowledge Management profile separate from other scopes.
Use the same narrowed scope for token acquisition and every request, including
the single retry. Repository-local cache paths are rejected; never copy tokens
into the checkout or project workspace. For the declared CONTENT_SEARCH read,
the wrapper refreshes the managed cache and retries once after HTTP 401 or 403.

If the interactive authorization callback returns `unauthorized_client`, stop
without retrying. The configured OAuth client or regular scope is not accepted
by the target identity domain, and no Knowledge Management endpoint request was
sent. Require an approved OAuth client registration and regular scope that can
obtain a token for the selected `knowledge-management` scope token; do not fall
back to a separate Knowledge Management scope property or a pasted bearer token.

## Endpoint Rules

- The wrapper accepts only POST to the exact relative
  `/api/knowledge-management/v2/contentIntelligence` path. Absolute URLs,
  suffixes, query overrides, other methods and service overrides are rejected.
- The validated path is joined to `restBaseUrl` through the shared host guard.
- Use JSON request bodies through `--body` or `--body-file`.
- Follow `sales-plays-content-intelligence-read.md`: only the question and
  exact Sales Play ID may vary. The connector, published-content filters,
  equality operators and nested userInput settings are validated before OAuth.
- Use `--token-cache auto`; explicit access tokens and custom cache paths are
  rejected. Only application/json Accept and Content-Type headers are allowed.
- The Content Intelligence POST has semantic-read behavior. The wrapper does
  not grant approval for another POST or any mutation.

## Error Output

Fixed validation messages identify the rejected contract. HTTP failures report
only the status and fixed relative endpoint; raw response bodies and URLs are
suppressed. Other failures report their exception type without details. The
CLI exits with code 1 on failure. Only the validated semantic read may receive
the single cache-managed authentication refresh and retry.
