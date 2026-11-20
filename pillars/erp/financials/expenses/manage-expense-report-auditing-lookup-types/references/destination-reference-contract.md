# Destination reference contract

A parsed workbook is never destination-ready by itself. Under the active task
workflow use core.fusion-api.rest-api-client for the GETs in ora_reference_lookups.md.
Gather fresh exact-task template/current exports through the shared exporter.
Credential handling, single-origin enforcement and one cached-token auth refresh
belong to core. Follow all pages until hasMore is false; reject repeated pages,
contract mismatches and partial collections. Use exact quoted/escaped query values,
not string interpolation that could broaden an ADF query. Follow only returned child
links on the approved origin.

Normalize the reviewed evidence into one JSON snapshot under the current project:

| Field | Contract |
|---|---|
| task_code | EXM_MANAGE_AUDIT_LOOKUP_TYPES |
| environment | Exact selected environment name |
| captured_at | UTC ISO timestamp; preflight accepts at most one hour old, at most one minute in the future |
| complete, codes_complete, sets_complete | true only after every requested result page is verified |
| expenses_module_ids | Module IDs proven by fresh task export rows with ModuleKey EXM and ModuleType APPLICATION, or the unique live taxonomy node with moduleKey EXM and moduleType APPLICATION when no mapping is exported; no hardcoded environment ID |
| scope_kind, module_source_ref | Export- or taxonomy-confirmed application-module scope and its baseline/captured-response reference; descendants are not inferred |
| types | Exact genericLookups rows including LookupType, ViewApplicationId, ModuleId, CustomizationLevel, Meaning, Description |
| sets | Exact setIdSets rows including SetCode, SetId, SetName |
| codes | Complete code rows with LookupType, LookupCode, ViewApplicationId, SetId, Meaning, EnabledFlag and normalized dates/retained values |
| code_scopes | One entry per requested type/view/set: LookupType, ViewApplicationId, SetId, complete=true, source_ref pointing to the exact readback and context evidence |
| template_sha256, baseline_sha256 | Hashes of the exact packages used by the local preparer; not a Data Loader approval envelope |

Generic lookup-code GET results omit SetId. Request expand=lookupsDFF on the
paginated lookupCodes collection and use each originating row's embedded identity.
Require hasMore=false, offset=0, count matching the item count and exactly one
matching identity row. Reject missing/truncated expansions rather than following
code-only child URLs: those URLs collide when a code exists in multiple sets.
Verify LookupType, LookupCode, ViewApplicationId and SetId against the parent and
complete set inventory. Never decode an opaque key or substitute COMMON/zero.
The unfiltered selected-type child is read across all sets; after complete
pagination, qualify every set from the complete destination set inventory.
SetIdLookupVO resolves SetCode independently of existing code usage. Thus a new
code may use a customer set that has no existing codes for this type, and an empty
type is not blocked merely because it has no observed set.
If this context is not established, leave an evidence gap and stop. Successful
zero type/set matches are missing setup; multiple matches are ambiguity. Only a
complete exact type/view/set code collection can establish that a code is new.

The customer-modified FSM export is not complete reference data. In particular,
EXM_AUDIT_REASON was found by read-only REST/UI while absent from that export during
authoring. CodeSearch proves resolvers, not configured environment values. Never use
EXM/ORA_EXM prefixes or the largest exported string as an authority for scope/length.

If a read-only service is unavailable, classify that independently from zero matches.
The source-proven SetCode import resolver may support a governed application-validation
choice with explicit uncertainty acceptance and normal Data Loader approval. The local
helper deliberately stays blocked until its complete-reference contract is met and
must not report a successful lookup. No readiness choice bypasses keys, unsafe package
shape, known-invalid values, target identity or core execution approval.

## Offline package boundary

build_import_candidate.py reruns preflight, validates exact template/current hashes,
metadata environment/release, member set, header order and every logical CSV row width.
It emits selected changed code rows and their existing translation rows, plus selected
existing type rows when their Meaning or Description changes. Type-translation members
remain header-only to avoid replaying stale TL text. Parents must already exist.
The four package CSV names and ordered headers are in package-contract.json, extracted
from a real template, not retyped from assumptions. ZIP entries use deterministic names,
timestamps and ordering; trailing empty fields remain explicit. No unchanged unrelated
code is replayed. Missing optional new-code values stay empty, except enabled Y.

For an update, a complete original code row is required to preserve fields outside
intake. A seeded code absent from the customer-modified export stays an update and
blocks this packager until complete preservation evidence is available. If selected
translations exist, Meaning/Description edits require source-language resolution and
are blocked by this preparer. These are tool limitations, not claims that Oracle does
not support those operations. No-op edits do not produce an import package.

The helper performs no import and does not claim live acceptance. Confirm source/session
language and release-specific create defaults at core handoff. In an active memory-only
Data Loader session, follow the core retention rules: do not persist captured payloads,
hashes, previews or approval objects. Previously authorized baseline exports and local
authoring evidence remain separate artifacts; never reconstruct a session from them.

## Type metadata edits

For type-only work, complete type evidence is required, but code/set collections
are not. Add text_context and complete type_translation_scopes as specified in
ui-parity.md. The type snapshot includes current Meaning, Description and
CustomizationLevel. An export-omitted parent requires reviewed schema-complete
preservation_rows; source seed data is never a target preservation baseline.
Runtime language/readback qualification remains outstanding.

## Customer workbook refresh

refresh_customer_references.py consumes validated selected types/codes and the
exact approved template/current exports. Its core GET adapter verifies configured
environment identity, returned-link origin, pagination offsets and repeated pages.
The resulting catalog includes current meanings, descriptions, levels and sets;
existing-input.json prepopulates selected existing rows. Unchanged populated cells
produce no updates. Editing a dropdown reference sheet never changes Fusion setup.
Customer catalogs and workbooks belong only in the ignored project workspace.
The shipped workbook contains portable starter guidance and blank input rows.

### Selected profile preservation

The reference reader accepts --properties for the trusted enrolled private profile;
the compatible default remains core/auth/fusionEnv.properties. It retains the selected
configuration in memory and uses the public Core REST/authentication providers for
its declared GET requests. It does not reread a default profile in a subprocess or
save a credential-bearing configuration copy. It checks the original profile digest
before authentication and each request, after responses, and before completing
reference evidence. Any profile change stops the run; restart through the selected
workflow. Both services use the selected environment and HTTPS restBaseUrl origin.
Standard lookup GETs use scope; taxonomy uses boss_scope with a separately acquired,
scope-bound token and the Core auto cache outside the repository. Core authentication
may refresh a rejected cached token once for a GET using the same retained service
configuration. Cross-origin links remain rejected.

### Empty modified-only exports

No exported module mapping means reference discovery is still required, not that
the seeded lookup is absent. The declared Core BOSS GET reads taxonomyNodes with
moduleType = 'APPLICATION', stable moduleId ordering and complete $limit/$offset
pagination. Require explicit hasMore=false, reject repeated or empty continuing
pages, then require exactly one exact moduleKey EXM node with a nonblank documented
moduleId. Do not substitute alternativeId, moduleGUID or an opaque key. Missing
boss_scope, unavailable services and unsupported schemas are blockers, not zero
matches. Then use that moduleId in the existing genericLookups inventory, followed
by the same type/view/set/code/DFF checks. Preserve the captured taxonomy response
under project exports and identify its provenance in the snapshot. Conflicting
export mappings stop rather than selecting an alternate source. Dry-run reports
the planned route and references_verified=false without authentication or GETs.

### Reference output containment

Before reading inputs or loading authentication providers, validate the supplied
project/output paths without resolving away symlinks. The selected project,
exports/artifacts roots and destination ancestors must be real directories;
reject symlinks, junctions, traversal, other-project destinations and existing
outputs. Recheck the capture path at profile/authentication/request boundaries
and before each raw response write. Revalidate the artifact destination after
collection and use exclusive creation for generated JSON files. A linked or
changed path blocks the capture rather than redefining the approved project root.
