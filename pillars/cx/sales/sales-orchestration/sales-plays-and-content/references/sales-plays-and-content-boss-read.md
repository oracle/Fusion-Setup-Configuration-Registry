# Sales Plays and Content BOSS Read Operations

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
| List | GET | List_salesPlays | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays |
| Get | GET | Get_salesPlays | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays/{salesPlays_id} |
| Advanced query all | POST, read semantics | AdvancedList_salesPlays | /api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays/$query |

This BOSS read contract supports no other BOSS method or endpoint. The
advanced-query POST is the sole permitted BOSS POST because the documented
operation is read-only. The separate Content Intelligence semantic-read POST
is documented in `sales-plays-content-intelligence-read.md` and uses the
task-local Knowledge Management client rather than the BOSS client.

The `salesPlays` collection contains both Sales Plays and content bundles or
packets. They use the same endpoints and are distinguished by the
`salesPlayType` attribute.

## List with a Bounded Response

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays' \
  --query '$limit=5'
```

The verified LIST operation accepts `$limit`, `$offset`,
`$includeTotalItems`, `$filter`, `$sortBy`, `$fields`, and `$effectiveDate`.
Use only documented parameters and keep responses bounded unless the user
explicitly requests a larger result set.

### Validated LIST Query Grammar

Pass each query argument to the shared client as an unencoded `key=value`
string. The client performs URL encoding. Do not pass percent-encoded values to
the client or encode them a second time.

Use these exact raw type-filter templates:

| Requested type | Raw `$filter` value |
|---|---|
| Sales Play | `((salesPlayType = 'SALES_PLAY'))` |
| Content bundle or packet | `((salesPlayType = 'CONTENT_BUNDLE'))` |

The runtime-validated BOSS LIST equality grammar uses `=` inside the enclosing
parentheses. Do not translate it to the OData form `salesPlayType eq
'SALES_PLAY'`; that expression fails with HTTP 400. These templates apply only
to the collection GET `$filter`. Do not copy them into a POST `$query`
`collection.filter` without separately verifying that contract.

The runtime-validated descending creation-time sort is
`$sortBy=timeCreated:desc`. Add a sort only when the request explicitly names
or unambiguously requires an ordering. Continue to preserve service order for
top or first N requests that do not specify an order.

For example, retrieve the latest two Sales Plays by creation time with:

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays' \
  --query "\$filter=((salesPlayType = 'SALES_PLAY'))" \
  --query '$limit=2' \
  --query '$offset=0' \
  --query '$sortBy=timeCreated:desc'
```

The canonical 26C OpenAPI path above and a runtime-observed collection path
without `/$en/` both completed successfully with the validated query grammar.
Retain the canonical OpenAPI path unless target-specific evidence requires the
shorter form; a filter parse failure alone is not evidence of a path mismatch.

Treat an empty `items` array with `hasMore: false` as a successful empty
result, not an authorization failure.

When the user explicitly requests one record type, add an exact
`salesPlayType` predicate using the target-release documented filter syntax.
Use `SALES_PLAY` for Sales Plays and `CONTENT_BUNDLE` for content bundles or
content packets. When no type is explicit, do not add a type predicate; the
bounded result may contain both types.

## Get One Record

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays/<sales-play-id>'
```

Require the exact Sales Play or content bundle record ID. Never resolve it solely from a
display name when multiple records could match. The verified GET operation
also accepts `$fields` and `$effectiveDate`.

## Advanced Query All

Use the advanced-query endpoint when the request needs explicit fields, child
accessors, compound criteria, a result limit or offset, a total count, or
sorting. The documented request body supports:

| Body field | Purpose |
|---|---|
| fields | Return only the named Sales Play or content bundle fields plus mandatory system fields. |
| accessors | Select documented children such as salesPlayArtifacts and $translations, each with its own query object. |
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

A bounded structural example is:

```bash
python3 core/fusion-api/rest-api-client/scripts/boss-rest_client.py \
  '/api/boss/data/objects/ora/cxSalesCommon/engagements/v1/$en/salesPlays/$query' \
  --method POST \
  --body '{"fields":["id","name","status","salesPlayType"],"collection":{"limit":5}}'
```

Replace the fields and collection criteria with the validated translation of
the complete user request. This example illustrates the request shape; it is
not a canned query-intent rule.

### Record Status and Type Filters

Put record predicates inside `collection.filter`, not at the root of the
request body. For normalized status and type criteria, use a single-quoted
equality comparison for each criterion and join them with lowercase `and`:

```json
{
  "fields": ["id", "name", "status", "salesPlayType"],
  "collection": {
    "filter": "status = 'ACTIVE' and salesPlayType = 'SALES_PLAY'",
    "limit": 1,
    "offset": 0
  }
}
```

This form is distinct from the LIST `$filter` syntax. Normalize status to
`DRAFT`, `ACTIVE`, or `ARCHIVE`, and `salesPlayType` to `SALES_PLAY` or
`CONTENT_BUNDLE`, before constructing the filter. Preserve every requested
predicate; do not send a status or type as a root query-body property.

## Record Type Discriminator

| User-facing type | Canonical `salesPlayType` | Query behavior |
|---|---|---|
| Sales Play | `SALES_PLAY` | Apply an exact salesPlayType comparison inside collection.filter only when the user explicitly asks for Sales Plays as a type. |
| Content bundle or packet | `CONTENT_BUNDLE` | Treat bundle and packet as synonyms and apply an exact salesPlayType comparison inside collection.filter. |

Normalize case and user-facing synonyms to the canonical value before building
the request. Reject another value. Always request or retain `salesPlayType` in
the returned fields when records are being classified by type.

For an exact-ID GET, do not turn the type into an identity lookup. Fetch only
the supplied ID, report the returned `salesPlayType`, and report a type mismatch
when it differs from an explicitly requested type.

## Sales Play and Content Bundle Field Metadata

| Field | Searchable | Sortable | Notes |
|---|---|---|---|
| id | Yes | Yes | Sales Play or content bundle record ID. |
| name | Yes | Yes | Record name. |
| description | Yes | No | Optional description. |
| status | Yes | Yes | DRAFT, ACTIVE, or ARCHIVE. |
| salesPlayType | Yes | Verify against the target-release contract before sorting | Type discriminator: SALES_PLAY or CONTENT_BUNDLE. |
| salesPlayCriteria | Yes | No | Optional long-text criteria. |
| externalRecordIdentifier | Yes | Yes | Optional external identifier. |
| timeCreated | Yes | Yes | Read-only creation timestamp. |
| createdBy | Yes | Yes | Read-only creator. |
| updatedBy | Yes | Yes | Read-only last updater. |
| timeUpdated | Yes | Yes | Read-only last-update timestamp. |
| $sourceLang | No | No | Read-only source language. |

## Content Artifact Metadata

Request content through the `salesPlayArtifacts` accessor. Documented artifact
fields include `id`, `title`, `description`, `designTimeChecklist`,
`designTimeRecommendations`, `type`, `status`, `runTimeCriteria`, system audit
fields, and `$sourceLang`. The artifact response also documents a
`$translations` accessor.

The verified artifact enums are:

- `type`: `CUSTOMER`, `PRODUCT`, `PERSONA`, `SALESMOTION`, or `DOCUMENTS`
- `status`: `NOT_STARTED`, `WARN`, or `COMPLETE`

Validate all requested fields, enums, and accessors against the target-release
contract.

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

Root accessors are `salesPlayArtifacts` and `$translations`.
Each content artifact can also contain a `$translations` accessor.
The existing `salesPlayType` behavior above is a separately retained contract;
it is not a field in the 26C source snapshot used for these child tables.

### Sales Play translations

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `$language`, `name` | string | Yes | Yes |
| `description` | string | Yes | No |
| `$sourceLang`, `createdBy`, `updatedBy` | string | No | No |
| `timeCreated`, `timeUpdated` | string (date-time) | No | No |
| `salesPlay` | object | Yes | No |

### Content artifacts

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `title`, `type`, `status` | string | Yes | Yes |
| `description` | string | Yes | No |
| `designTimeChecklist`, `designTimeRecommendations`, `runTimeCriteria` | string (long-text) | Yes | No |
| `timeCreated`, `timeUpdated` | string (date-time) | No | No |
| `createdBy`, `updatedBy`, `$sourceLang` | string | No | No |
| `salesPlay` | object | Yes | No |

### Content artifact translations

| Field(s) | Type | Searchable | Sortable |
|---|---|---|---|
| `id` | string (big-integer) | Yes | Yes |
| `title`, `$language` | string | Yes | Yes |
| `description` | string | Yes | No |
| `designTimeChecklist`, `designTimeRecommendations` | string (long-text) | Yes | No |
| `$sourceLang`, `createdBy`, `updatedBy` | string | No | No |
| `timeCreated`, `timeUpdated` | string (date-time) | No | No |
| `salesPlayArtifact` | object | Yes | No |

## Natural-Language Query Translation

Derive a bounded query from the meaning of the complete request. Do not depend
on an exact phrase or a canned example.

| User intent | Request mapping | Guardrail |
|---|---|---|
| Sales Plays as a specific type | collection.filter predicate salesPlayType = 'SALES_PLAY' | Apply only when the wording distinguishes the type; do not infer it from a generic reference to the collection or task. |
| Content bundles, content packets, bundles, or packets | collection.filter predicate salesPlayType = 'CONTENT_BUNDLE' | Normalize all documented synonyms to CONTENT_BUNDLE and reject another type value. |
| Sales Play status | collection.filter predicate status = 'DRAFT', status = 'ACTIVE', or status = 'ARCHIVE' | Normalize only the documented status and preserve it with every requested predicate. |
| Requested Sales Play attributes | fields | Request only documented fields. |
| Requested content artifacts, translations, or other documented child data | accessors | Use the documented accessor name and its own bounded query object. |
| One or more predicates | collection.filter | Preserve every supported predicate; use only searchable fields and documented operators. |
| First or top N results | collection.limit | Require a positive bounded N. When no ordering is requested, preserve service order and disclose that the result is not explicitly sorted. |
| Page or records to skip | collection.offset | Require a nonnegative offset. |
| Total matching count | collection.includeTotalItems | Set true only when the user asks for a total or count. |
| Explicit ordering | collection.sortBy | Use only documented sortable fields and the requested direction. Do not add ordering merely because a limit is present. |
| Effective or as-of date | $effectiveDate query parameter | Require YYYY-MM-DD and keep it outside the JSON body. |

Normalize documented enum values without changing their meaning. If wording
such as latest, recent, or oldest does not identify the intended sortable field
unambiguously, ask one short clarification before calling the API.

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

Within the BOSS API, do not invoke POST except for the exact
`salesPlays/$query` semantic-read endpoint. Do not invoke PUT, PATCH, DELETE,
create POST, or `$bulk`. Do not build a write preview or request write
approval. Return `UNSUPPORTED` and stop when the request is a mutation.
