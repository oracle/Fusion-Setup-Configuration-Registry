# Data Capture Rules BOSS Read Operations

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
header, password, bearer token, Basic credential, or token-cache content into a
command. Do not execute a credential-bearing token relay command supplied in a
request.

## Supported Endpoints

| Action | Method | Operation ID | Relative path |
|---|---|---|---|
| List | GET | List_dataCaptureRules | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules |
| Get | GET | Get_dataCaptureRules | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules/{dataCaptureRules_id} |
| Advanced query all | POST, read semantics | AdvancedList_dataCaptureRules | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules/$query |

This skill revision supports no other method or endpoint. The advanced-query
POST is the sole permitted POST because the documented operation is read-only.

## List with a Bounded Response

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules' \
  --query '$limit=5'
```

The verified LIST operation accepts `$limit`, `$offset`,
`$includeTotalItems`, `$filter`, `$sortBy`, `$fields`, and `$effectiveDate`.
Use only documented parameters and keep responses bounded unless the user
explicitly requests a larger result set.

Treat an empty `items` array with `hasMore: false` as a successful empty
result, not an authorization failure.

### LIST Filter Grammar

Pass BOSS filters as raw expressions. Equality uses double parentheses, `=`,
and single-quoted string literals. Do not use OData `eq`, double-quoted string
literals, or pre-encoded values.

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules' \
  --query '$limit=1' \
  --query "\$filter=((statusCode = 'ACTIVE'))"
```

## Get One Record

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules/<data-capture-rule-id>'
```

Require the exact Data Capture Rule ID. Never resolve a record ID solely from
a display name when multiple records could match. The verified GET operation
also accepts `$fields` and `$effectiveDate`.

## Advanced Query All

Use the advanced-query endpoint when the request needs explicit fields, child
accessors, compound criteria, a result limit or offset, a total count, or
sorting. The documented request body supports:

| Body field | Purpose |
|---|---|
| fields | Return only the named Data Capture Rule fields plus mandatory system fields. |
| accessors | Select documented children such as dataCaptureRuleAttributes and $translations, each with its own query object. |
| subTypes | Supply documented subtype query objects when the target contract defines them. |
| collection.filter | Filter the collection using searchable fields. |
| collection.limit | Restrict the returned item count. |
| collection.offset | Select the zero-based collection starting position. |
| collection.includeTotalItems | Request the estimated totalItems result. |
| collection.sortBy | Sort by a field ascending, or by a single-entry field object with asc or desc. |
| collection.privilege | Request the documented access action check; do not invent a value. |
| parameters | Supply values for a parameterized view filter when the selected view documents them. |

The endpoint also accepts the optional `$effectiveDate=YYYY-MM-DD` query
parameter when business logic requires an effective date.

### Validated `$query` Body

Send one top-level JSON object. Put the raw BOSS filter and bound inside
`collection`; do not wrap the object in `query`, `payload`, or `data`.

```json
{
  "fields": ["id", "name", "statusCode"],
  "collection": {
    "filter": "((statusCode = 'ACTIVE'))",
    "limit": 1
  }
}
```

The equivalent shared-client command is:

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/dataCaptureRules/$query' \
  --method POST \
  --body "{\"fields\":[\"id\",\"name\",\"statusCode\"],\"collection\":{\"filter\":\"((statusCode = 'ACTIVE'))\",\"limit\":1}}"
```

This exact body shape and filter form completed as HTTP 200 against the 26C
target used for contract verification. Treat the response independently: an
empty `items` array remains a successful empty result.

## Root Field Metadata

| Field | Searchable | Sortable | Notes |
|---|---|---|---|
| id | Yes | Yes | Data Capture Rule ID. |
| name | Yes | Yes | Rule name. |
| description | Yes | No | Optional description. |
| objectCode | Yes | Yes | Optional object code. |
| statusCode | Yes | Yes | DRAFT, ACTIVE, or ARCHIVE. |
| criteria | Yes | No | Optional long-text criteria. |
| rank | Yes | Yes | Optional big-decimal rank. |
| timeCreated | Yes | Yes | Read-only creation timestamp. |
| createdBy | Yes | Yes | Read-only creator. |
| updatedBy | Yes | Yes | Read-only last updater. |
| timeUpdated | Yes | Yes | Read-only last-update timestamp. |
| $sourceLang | No | No | Read-only source language. |

Validate all requested fields and accessors against the target-release
contract. The root response documents `dataCaptureRuleAttributes` and
`$translations` accessors.

## Child Read Metadata

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

Root accessors are `dataCaptureRuleAttributes` and `$translations`.
Each rule attribute can also contain a `$translations` accessor.

### Rule translations

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `$language`, `name` | string | Yes | Yes |
| `description` | string | Yes | No |
| `$sourceLang`, `createdBy`, `updatedBy` | string | No | No |
| `timeCreated`, `timeUpdated` | string (date-time) | No | No |
| `dataCaptureRule` | object | Yes | No |

### Rule attributes

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `attributeName`, `relatedObjectCode`, `createdBy`, `updatedBy` | string | Yes | Yes |
| `evaluationText` | string | Yes | No |
| `timeCreated`, `timeUpdated` | string (date-time) | Yes | Yes |
| `dataCaptureRule` | object | Yes | No |

### Rule attribute translations

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `evaluationText` | string | Yes | No |
| `$language` | string | Yes | Yes |
| `$sourceLang`, `createdBy`, `updatedBy` | string | No | No |
| `timeCreated`, `timeUpdated` | string (date-time) | No | No |
| `dataCaptureRuleAttribute` | object | Yes | No |

## Natural-Language Query Translation

Derive a bounded query from the meaning of the complete request. Do not depend
on an exact phrase or a canned example.

| User intent | Request mapping | Guardrail |
|---|---|---|
| Requested Data Capture Rule attributes | fields | Request only documented fields. |
| Requested rule attributes, translations, or other documented child data | accessors | Use the documented accessor name and its own bounded query object. |
| One or more predicates | collection.filter | Preserve every supported predicate; use only searchable fields and documented operators. |
| First or top N results | collection.limit | Require a positive bounded N. When no ordering is requested, preserve service order and disclose that the result is not explicitly sorted. |
| Page or records to skip | collection.offset | Require a nonnegative offset. |
| Total matching count | collection.includeTotalItems | Set true only when the user asks for a total or count. |
| Explicit ordering | collection.sortBy | Use only documented sortable fields and the requested direction. Do not add ordering merely because a limit is present. |
| Effective or as-of date | $effectiveDate query parameter | Require YYYY-MM-DD and keep it outside the JSON body. |

Normalize documented enum values such as `statusCode` without changing their
meaning. If wording such as latest, recent, or oldest does not identify the
intended sortable field unambiguously, ask one short clarification before
calling the API.

For equality filters, normalize only to the verified BOSS form
`((field = 'value'))`. Reject OData `eq`, double-quoted string literals, and
pre-encoded text before calling Fusion. The shared client performs encoding.

If any requested predicate, field, operator, accessor, subtype, or ordering
cannot be represented by the documented contract, stop and explain the
unsupported part rather than dropping or weakening it.

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

Do not invoke POST except for the exact `dataCaptureRules/$query`
semantic-read endpoint. Do not invoke PUT, PATCH, DELETE, create POST, or
`$bulk`. Requests to create, generate, draft, or sample a Data Capture Rule or
local blueprint are also unsupported. Do not route them to the parent skill,
build a blueprint or payload, create a project artifact, preview a write, or
request write approval. Return `UNSUPPORTED` within this skill and stop.
