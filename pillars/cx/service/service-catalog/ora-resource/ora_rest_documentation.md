# Product Groups REST creation

Status: **enabled through the Product Groups-specific Service command**.
This exact-task capability lives in `scripts/product_group_rest.py` and
implements its own domain preflight/approval/verification steps. It delegates
all HTTP, OAuth, trusted-origin checks and transport behavior to
`core.fusion-api.rest-api-client`; it does not implement a generic REST, auth,
loader or multi-task execution framework. Core Task Hook does not implement
these REST commands and is not part of this selected create route.

## Scope and source

Only `QSC_MANAGE_PRODUCT_GROUPS` / `Manage Product Groups`, offering `Service`,
functional area `Service Catalog`, operation `create-product-group` is accepted.
The [Oracle product-group create reference](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-setupsalescatalogs-post.html)
is the retained endpoint source. Live collection Describe must confirm the
field types, lengths, mandatory names and collection create action. Retained
Fusion evidence returns integral lengths and IDs as numeric strings; the
command validates and normalizes them with bounds. No value is inferred.

Catalog export/import flags remain N/N. This route enables no CSV/FSM import,
upsert, update, delete, publish, parent link or Usage assignment. Product Group
Usage retains its independent read/FSM workflow.

## Selected workflow

Run from the repository root:

`python3 pillars/cx/service/service-catalog/scripts/product_group_rest.py <command> --input-stdin`

1. Require the generated selected project's
   `artifacts/shared/runbook/current/task-context.json` and active environment-bound
   Run Book. Preserve task identity and sequence. Resolve missing context through
   the active router/Run Book workflow, never by rewriting a source task.
2. Obtain assisted `core.diagnostics.role-access-check` evidence for the current
   principal: `status: passed`, `skillId: core.diagnostics.role-access-check`,
   exact environment origin, `taskCode: QSC_MANAGE_PRODUCT_GROUPS`,
   `operation: create-product-group`, `canRead: true`, `canCreate: true`, and UTC
   `checkedAt` within 15 minutes. Store it inside that initialized project.
   Do not infer privileges from Describe or fabricate an IAM check.
3. `validate-fscr-task-rest-payload` accepts `taskContextPath`, exact `taskName`,
   positive `sequence`, `operation`, `payload` and project `privilegeEvidence`
   path. It validates names/optional flags, GETs collection Describe and checks
   exact InternalName OR ProdGroupName duplicates. Quotes are escaped; require
   empty items and hasMore=false. Any mismatch blocks; no POST occurs.
4. Present the returned exact environment, POST path, payload and immutable
   preview digest to the user. Obtain explicit approval immediately before
   execution. Planning, login or repository-edit approval is not write approval.
5. `verify-fscr-task-rest-preview` accepts only the returned `previewPath`,
   unchanged `previewSha256`, and literal `approved: true` after user approval.
   It rechecks 15-minute expiry, context, Run Book binding, source contract,
   task guidance and reviewed privilege hashes. Never edit/reconstruct previews.
6. `fscr-task-rest` consumes the same approved input, claims an exclusive attempt
   journal, repeats Describe/duplicate checks, rechecks approval/binding and
   submits exactly one POST through core. Numeric-string or integer positive
   ProdGroupId and approved values must match the response and a fresh GET.
   No retry, upsert or automatic cleanup is supported. An attempted preview
   cannot be reused after success, failure or uncertainty.
7. Persisted preview/transport/attempt/result/failure evidence stays under
   `project/{project_id}/artifacts/pillars/cx/service/service-catalog/product-group-rest/`.
   Evidence creation accepts only new absolute paths in that fixed Product Groups namespace; traversal, symlinks, existing files and other tasks/projects are rejected. The active core Run Book binding and initialized project are rechecked before persistence. Use existing project registry/state/token services to register results and
   record the lifecycle. On failure preserve stage/class, environment and any
   known record ID; redact secrets and reconcile before considering a new request.

The command delegates HTTP through the core REST CLI with
REST-Framework-Version=9, a 60-second request timeout and a 90-second subprocess
limit. Only core owns token reuse/recovery. No write is retried. Export, polling,
Run Book creation, cross-task routing and unrelated setup sequencing are outside
this focused capability.

## Failure diagnostics

REST creation remains enabled with one attempt and no write replay. The task
adapter retains an allow-listed diagnostic artifact for a failed core-client
invocation, including its recognized failure class, safe summary, available HTTP
status, request ID/ECID, return code, method and evidence references. The create
failure record links that artifact and preserves its class across preflight,
creation and verification. A subprocess timeout is `process_timeout`; HTTP
401/403 is `auth_authz`. A recognized structured core class is otherwise retained;
unclassified HTTP failures are `fusion_api_error` and failures without usable
status/class evidence remain `transport_environment`.

Raw stdout/stderr, exception text, URLs, authorization headers and response-body
messages are not copied into summaries. Missing or conflicting diagnostic IDs
are omitted rather than guessed. Inspect retained project evidence to reconcile
a failed or uncertain operation. Never replay an attempted preview or retry POST.

## Exact operation contract

```json
{
  "schemaVersion": "1.0",
  "taskCode": "QSC_MANAGE_PRODUCT_GROUPS",
  "taskName": "Manage Product Groups",
  "operations": [
    {
      "id": "create-product-group",
      "enabled": true,
      "method": "POST",
      "path": "/crmRestApi/resources/11.13.18.05/setupSalesCatalogs",
      "describePath": "/crmRestApi/resources/11.13.18.05/setupSalesCatalogs/describe",
      "duplicateFields": ["InternalName", "ProdGroupName"],
      "verification": {
        "identityField": "ProdGroupId",
        "identityType": "positive_integer",
        "matchFields": ["InternalName", "ProdGroupName"]
      },
      "fields": {
        "InternalName": {"type": "string", "required": true, "maxLength": 150},
        "ProdGroupName": {"type": "string", "required": true, "maxLength": 250},
        "ActiveFlag": {"type": "string", "maxLength": 1, "enum": ["Y", "N"]},
        "AllowDuplicateContentFlag": {"type": "string", "maxLength": 1, "enum": ["Y", "N"]},
        "UsageRootFlag": {"type": "string", "maxLength": 1, "enum": ["Y", "N"]}
      }
    }
  ]
}
```
