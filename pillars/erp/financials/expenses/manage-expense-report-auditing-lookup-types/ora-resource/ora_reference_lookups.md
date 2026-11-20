# Auditing lookup preflight

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_auditing_lookup_references | Before deriving operations and before packaging | Destination snapshot from the declared core GETs and source-backed set context | Exact task/environment; age at most one hour; all pages; one type and set; Expenses module verified; full type/view/set/code identity; resulting meanings unique | Derived create/update, view ID, SetCode, retained values | Block invalid/ambiguous evidence; zero code matches means create only after complete lookup population and full context are verified |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_expenses_application_module | No EXM/APPLICATION module mapping in approved exact-task export | Fixed task parameters EXM / APPLICATION and selected environment | Core BOSS GET /api/boss/data/objects/ora/commonAppsInfra/objects/v1/taxonomyNodes; $filter=moduleType = 'APPLICATION'; $sortBy=moduleId; $limit/$offset | moduleId, moduleKey, moduleType, complete items/hasMore | Complete stable pagination, exactly one exact EXM/APPLICATION node; documented nonblank moduleId only | Verified Expenses module scope and captured-response provenance | Zero/multiple matches, unsupported identity, missing boss_scope, incomplete pagination or auth/transport failure blocks; never substitute IDs |
| find_auditing_lookup_type | Active workflow selects reference gathering | Exact LookupType and selected environment | GET /fscmRestApi/resources/11.13.18.05/genericLookups with q=LookupType='<escaped type>'; limit and offset | LookupType, ViewApplicationId, ModuleId, CustomizationLevel, Meaning, Description, links | Exact unique type in verified Expenses APPLICATION module; complete pagination | Target type/view/module context | Zero type matches is missing setup; multiple view matches require scope clarification |
| find_auditing_lookup_codes | Type resolved | Exact returned same-origin lookupCodes child link | GET returned /genericLookups/{id}/child/lookupCodes; limit and offset | LookupCode, ViewApplicationId, Meaning, Description, EnabledFlag, dates, DisplaySequence, Tag | All pages; bind full set context separately because generic code responses omit SetId | Complete selected type code population, including seeded values | Multiple identity matches block; absent codes are new only with proven complete set context |
| find_auditing_reference_set | SetCode supplied | Exact code, not display name | GET /fscmRestApi/resources/11.13.18.05/setIdSets with finder=SetCodeFinder;SetCode=<escaped code> | SetCode, SetId, SetName | Exact unique code; paginate completely | Verified set identity and display name | Zero is missing setup; multiple matches block |

## Lookup Execution Rules

### Customer reference refresh (read-only)

After exact-task exports and local intake validation, refresh the selected
customer environment using core.fusion-api.rest-api-client. Never use the
bundled starter list as destination evidence. Resolve Expenses module IDs from
the fresh exact-task export's ModuleKey/ModuleType mappings. If no mapping exists,
including a header-only modified export, select find_expenses_application_module
through Core's BOSS route with boss_scope. Read all APPLICATION nodes in stable
moduleId order and require exactly one EXM key with its documented moduleId.
Explicit terminal hasMore=false is required; reject missing continuation metadata,
repeated pages, empty continuing pages and conflicting export mappings. No
environment ID or host is embedded in this task. Fetch every genericLookups page for each
verified module and every setIdSets page. Retain fresh type names, descriptions,
configuration levels and view IDs for the implementor's dropdowns.

For each selected type, follow its returned lookupCodes child link and every
page. Follow each code's returned lookupsDFF child link, or explicitly expand
lookupsDFF and verify complete child pagination. Read LookupType, LookupCode,
ViewApplicationId and SetId from that child; require exact parent-key equality,
one unambiguous set identity and a matching target setIdSets row. Never derive a
hash key, decode an opaque URL, assign SetId zero, or infer COMMON. A missing or
ambiguous DFF identity is an explicit evidence blocker, not a missing code.
Read-only identity collection does not authorize DFF edits.

Authority: Oracle 26D Generic Lookups item GET documents lookupCodes.lookupsDFF
and its full identity fields:
https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-fscmrestapi-resources-11.13.18.05-genericlookups-genericlookups_id-get.html
The same-origin child links are the runtime navigation authority. Use these
GETs and the taxonomy GET above only; no dependency query, write method, or alternate transport is allowed.
Taxonomy authority: Oracle 26D (latest Common documentation index checked 2026-11-17),
https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-api-boss-data-objects-ora-commonappsinfra-objects-v1-taxonomynodes-get.html
documents moduleId, moduleKey, moduleType and $limit/$offset/$sortBy. This new
route has synthetic qualification; target availability and privileges still need
live qualification. Do not infer moduleGUID equivalence on a different schema.

| Situation | What Happens |
|---|---|
| Client and origin | core.fusion-api.rest-api-client owns standard OAuth GETs (scope) and the declared taxonomy BOSS GET (boss_scope). --properties selects the trusted private profile without copying it; pin environment, HTTPS origin and profile digest across both services. No direct SQL or custom REST transport |
| Missing set identity | Generic code rows omit SetId. Read each returned lookupsDFF child and require its full matching type/code/view/set identity; verify the set against setIdSets. If not verified, stop with an evidence gap; never assume COMMON from a missing field |
| Customer-modified export | Does not enumerate seeded values. Combine read-only references with schema/preservation evidence; never classify missing export rows as new |
| Import resolver | AM-SERVICE importData resolves SetCode through SetIdLookupVO and writes SetId; missing set removes that row with a migration warning. Preserve partial warnings and inspect row outcomes |
| Unavailable preflight | Separate auth/transport/contract unavailability from a successful zero or multiple match. A source-proven FSM fallback may be offered with explicit uncertainty acceptance through normal Data Loader approval; the offline helper remains blocked and must not claim verified references |

Sources: REST-TYPES, REST-SETS, AM-SERVICE, VO-SET and observed read-only results;
see references/evidence.md and references/destination-reference-contract.md.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUDLK_LOOKUP | step | 3 | reference_lookup | success->AUDLK_DEFAULT | AUDLK_DEP | stop | Always |

## Type-text preparation checks

Lookup Types rows require exact existing type/view/module and current text/level.
Require the language and translation-preservation evidence in references/ui-parity.md.
This extension declares no new live endpoint. If the existing workflow cannot provide
complete language/preservation evidence, record the missing readback contract and stop
preparation; never substitute SQL or an exploratory client. Code-only work retains its
full type/view/set/code checks. No permission is derived from editable reference lists.
