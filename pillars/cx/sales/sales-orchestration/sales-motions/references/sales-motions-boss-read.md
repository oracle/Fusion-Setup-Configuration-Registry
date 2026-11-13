# Sales Motions BOSS Read Operations

## Verified Source

The endpoint summary below reflects the 26C BOSS API contract used when this
reference was authored.

Reverify the target release before execution when it is later than 26C.

## Shared Client

Run commands from the repository root through:

`core/fusion-api/rest-api-client/scripts/boss-rest_client.py`

The client obtains `boss_scope` from `core/auth/fusionEnv.properties` and uses
`--token-cache auto`, the shared managed external profile cache at
`~/.fusionaim/<profile-fingerprint>_token.json`. The profile binds the approved
issuer/endpoints, client, target, and selected scope. Repository-local cache
paths are rejected; never copy tokens into the checkout or project workspace. Never paste an Authorization
header, password, bearer token, or token-cache content into a command.

## Supported Endpoints

| Action | Method | Relative path |
|---|---|---|
| List | GET | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions |
| Get | GET | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions/{salesMotions_id} |
| Advanced query all | POST, read semantics | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions/$query |

This skill revision supports no other method or endpoint. The advanced-query
POST is the sole permitted POST because the documented operation is read-only.

## List with a Bounded Response

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions' \
  --query '$limit=5'
```

LIST accepts `$limit`, `$offset`, `$includeTotalItems`, `$filter`, `$sortBy`,
`$fields`, and `$effectiveDate`. `$sortBy` is a comma-separated list of field
names, each optionally followed by `:asc` or `:desc`; the default is ascending.
Keep previews bounded unless the user explicitly requests a larger result set.

Treat an empty `items` array with `hasMore: false` as a successful empty
result, not an authorization failure.

## Get One Record

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesMotions/<sales-motions-id>'
```

Require the exact Sales Motion ID. Never resolve a record ID solely from a
display name when multiple records could match. GET also accepts `$fields`
and `$effectiveDate`.

## Advanced Query All

Use the advanced-query endpoint when the request needs a filter, explicit
fields, child accessors, a result limit or offset, a total count, or sorting.
The documented request body supports:

| Body field | Purpose |
|---|---|
| fields | Return only the named Sales Motion fields plus mandatory system fields. |
| accessors | Select salesMotionObjectives or $translations at the root; nest salesMotionObjectiveHvas inside salesMotionObjectives.accessors. |
| collection.filter | Filter the collection using searchable fields. |
| collection.limit | Restrict the returned item count. |
| collection.offset | Select the zero-based collection starting position. |
| collection.includeTotalItems | Request the estimated totalItems result. |
| collection.sortBy | Sort by a field ascending, or by a single-entry field object with asc or desc. |
| collection.privilege | Request the documented access action check; do not invent a value. |
| parameters | Supply values for a parameterized view filter when the selected view documents them. |

The endpoint also accepts the optional `$effectiveDate=YYYY-MM-DD` query
parameter when business logic requires an effective date.

### Natural-Language Query Translation

Derive a bounded query from the meaning of the complete request. Do not depend
on an exact phrase or a canned example.

| User intent | Request mapping | Guardrail |
|---|---|---|
| Requested Sales Motion attributes | fields | Request only documented fields. |
| Requested objective, high-value-activity, or other documented child data | accessors | Use the documented accessor name and its own bounded query object. |
| One or more predicates | collection.filter | Preserve every supported predicate; use only searchable fields and documented operators. |
| First or top N results | collection.limit | Require a positive bounded N. When no ordering is requested, preserve service order and disclose that the result is not explicitly sorted. |
| Page or records to skip | collection.offset | Require a nonnegative offset. |
| Total matching count | collection.includeTotalItems | Set true only when the user asks for a total or count. |
| Explicit ordering | collection.sortBy | Use only documented sortable fields and the requested direction. Do not add ordering merely because a limit is present. |
| Effective or as-of date | $effectiveDate query parameter | Require YYYY-MM-DD and keep it outside the JSON body. |

Normalize documented enum values such as `statusCode` without changing their
meaning. Valid `statusCode` values in the verified 26C contract are `DRAFT`,
`ACTIVE`, and `ARCHIVE`. Validate requested fields against the target-release
contract; fields used in `filter` must be searchable and fields used in
`sortBy` must be sortable.

If wording such as latest, recent, or oldest does not identify the intended
sortable field unambiguously, ask one short clarification before calling the
API. If any requested predicate, field, operator, accessor, or ordering cannot
be represented by the documented contract, stop and explain the unsupported
part rather than dropping or weakening it.

## Local Read Metadata

The field tables below preserve the 26C metadata for the supported reads.
`No` means the source contract does not declare that capability; do not filter
or sort by that field. Validate fields within their own object scope, rather
than inheriting search or sort permissions from a parent object. Parent-reference
fields are objects; do not invent nested reference fields or filter syntax.

Use a separate query object for each accessor under `accessors`, with a bounded
`collection.limit` for each requested child collection. `fields` is an array
of field names; `collection.sortBy` is an array such as `["name"]` or
`[{"name":"desc"}]`. Select only fields and accessors documented locally.
Omit `collection.privilege`, `parameters`, or subtype-specific criteria unless
an approved contract supplies their exact supported values.

### Sales Motion root fields

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `name`, `objectCode`, `statusCode`, `createdBy`, `updatedBy` | string | Yes | Yes |
| `description` | string | Yes | No |
| `deletedFlag` | boolean | Yes | Yes |
| `timeCreated`, `timeUpdated` | string (date-time) | Yes | Yes |
| `$sourceLang` | string | No | No |

Root accessors are `salesMotionObjectives` and `$translations`.
Objective accessors are `salesMotionObjectiveHvas` and `$translations`.
The 26C HVA response defines no further child accessor; do not place the HVA
accessor at the Sales Motion root.

### Sales Motion translations

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `$language`, `name` | string | Yes | Yes |
| `description` | string | Yes | No |
| `$sourceLang`, `createdBy`, `updatedBy` | string | No | No |
| `timeCreated`, `timeUpdated` | string (date-time) | No | No |
| `salesMotion` | object | Yes | No |

### Objectives

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `name` | string | Yes | Yes |
| `description` | string | Yes | No |
| `evaluationText`, `createdBy`, `updatedBy` | string | No | No |
| `displaySequence` | string (big-decimal) | No | Yes |
| `deletedFlag` | boolean | Yes | Yes |
| `timeCreated`, `timeUpdated` | string (date-time) | Yes | Yes |
| `salesMotion` | object | Yes | No |

### Objective translations

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `$language`, `name` | string | Yes | Yes |
| `description` | string | Yes | No |
| `evaluationText`, `$sourceLang`, `createdBy`, `updatedBy` | string | No | No |
| `timeCreated`, `timeUpdated` | string (date-time) | No | No |

### High-value activities

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `name` | string | Yes | Yes |
| `description`, `evaluationText` | string | Yes | No |
| `displaySequence` | string (big-decimal) | No | Yes |
| `timeCreated`, `timeUpdated` | string (date-time) | Yes | Yes |
| `deletedFlag` | boolean | Yes | Yes |
| `createdBy`, `updatedBy` | string | No | No |
| `salesMotionObjective` | object | Yes | No |

## Effective Read Access

- A successful LIST, GET, or QUERY proves effective read access for that call only.
- HTTP 401 is an authentication result.
- For LIST or GET, the shared client refreshes and retries once on a
  cache-managed HTTP 401 or 403. A second 403 is an authorization or privilege
  failure.
- For QUERY, the shared client does not automatically refresh or retry the
  POST after HTTP 401 or 403. Stop and report the sanitized authentication or
  authorization failure; do not infer a missing role from that response alone.
- HTTP 404 on an exact GET is a not-found result, not proof of missing read
  permission.
- Do not infer role membership, permission-group membership, setup-screen
  privilege, or write access from a successful read.

## Explicit Read-Only Boundary

Do not invoke POST except for the exact `salesMotions/$query` semantic-read
endpoint. Do not invoke PUT, PATCH, DELETE, create POST, or `$bulk`. Do not
build a write preview or request write approval. Return `UNSUPPORTED` and stop
when the request is a mutation.
