# Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Single-index request | One environment; one scalar index name or code; additions/removals or explicit rebuild | Stop before lookup | Ask for one index; attribute rows inherit it | Always | index_work_item_guard |
| Registered business object | productManagementESIndexedAttributes | Stop before preparation | Verify exact registration | Always | verify_product_management_es_indexed_attributes_business_object |
| Addition selector | Attribute name or code; optional group and object names or codes; generic selectors and explicit snake_case or PascalCase fields may be mixed | Stop only if attribute selector absent or malformed | Resolve missing names/codes from metadata; confirm unique scope if group/object omitted | Every addition | resolve_indexed_attribute_scope |
| Removal selector | Attribute name or code; optional group, object and subtype names or codes; optional backend AttributeId; generic selectors and explicit snake_case or PascalCase fields may be mixed | Stop if attribute selector absent or malformed; a missing name is not a blocker when a code is supplied | Resolve missing names/codes and backend ID from the existing indexed record; confirm unique scope if group/object omitted | Every removal | resolve_existing_product_management_es_indexed_attribute |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Canonical index | Accept lookup code or display meaning and retain the exact returned code | Every operation | resolve_product_management_index_code |
| Name-or-code input | Accept generic attribute/group/object selectors or explicit snake_case/PascalCase name and code fields. If both are supplied, both must match the same metadata record. No fuzzy matching or invented codes. | Additions and removals |  |
| Incomplete scope | A unique match with omitted group/object requires confirmation; multiple matches require clarification using names or codes | Additions and removals with partial scope |  |
| Create-required fields | POST must contain IndexName, AttributeCode, GroupCode and ObjectCode copied from the resolved record. Names cannot replace codes. Enforce additional live create requirements without applying a blanket mandatory-field rule to DELETE or other business objects. | Every POST including seeded repairs | resolve_indexed_attribute_create_contract |
| Resolved object subtype | User subtype selectors are optional. Preserve every nonblank ObjectSubTypeCode from the uniquely resolved metadata record in the resolved identity, delta, and POST, including seeded repairs. Both supplied fields must agree. Block missing resolved codes, captured-row omission or mismatch, and fields not writable in the live create contract. Only resolved metadata without a subtype uses triplet comparison. A resolved subtype must match existing data and post-load readback exactly; a different subtype cannot satisfy the request. Missing subtype evidence on a matching existing triplet blocks scoped comparison. | Additions and removals |  |
| Generated ID | AttributeId must be blank or omitted on POST; require the exact resolved backend ID on DELETE and agreement of every supplied ID alias | POST or DELETE |  |
| Prepared archive contract | Run index_delta_guard.py --stdin --archive <Core prepared ZIP> --archive-sha256 <Core archiveSha256> using the original request, resolved addition/removal evidence, delta and applicable create contract. Verify one immutable ZIP snapshot against Core's returned digest; use its parsed rows, never the workbook or caller-created records. Require exact names, index, order and operations, mandatory POST codes and backend DELETE ID; validate every nonblank optional DELETE code/subtype value; never repair captured rows in place | Before core preview and approval |  |
| ESS approved handoff | Validate the envelope against schemas/ess-delegation-contract.schema.json version 1.0, including approved_submission conditional requirements. Require explicit_submission_approval=true and a matching approved payload SHA-256. Require exact task identity, matching job_contract and request_payload job/application, the approved canonical index, target environment, and unchanged execution options. Missing approval or any mismatch blocks delegation; correct and obtain fresh approval for changed submission details. | After fresh ESS approval, immediately before delegation to core.fusion-api.ess-job-submitter |  |
| Immutable source | Follow core.data-loader’s existing CLI preflight, immutable artifact, Task Hook preview, approval and source-correction contract | Data Loader |  |
| Checkpoint bindings | Require a nonblank verified environment and lowercase 64-character request SHA-256 before an initial checkpoint. Continuations inherit immutable original bindings; reject missing legacy bindings rather than backfilling them. Require the original approved payload SHA-256 before ess_submitting. | Every local checkpoint write |  |
| Reconciliation envelope | Require confirmed boolean true, outcome matching the requested checkpoint, immutable environment/request SHA-256/index bindings and permitted pillar or authorized evidence refs. Load reconciliation without a report reference requires user_requested_status_check=true from the fresh user-requested core status result; ESS reconciliation still requires an authorized artifact reference. Load outcomes require the same accepted Request ID; readback requires load_succeeded=true. ESS acceptance requires the original approved payload SHA-256 and confirmed accepted ESS Request ID. Missing legacy bindings or mismatches block. The host supplies normalized declared core results in memory; this envelope is evidence validation, never execution approval. | Recovery from blocked checkpoint |  |

## Failed-Load Rebuild Validation

Require a core-confirmed terminal failed status, accepted Request ID, exact canonical
index, environment, current confirmed status evidence and explicit proceed choice before preparing
a failed-load rebuild. Keep terminal failure provenance in the permitted pillar checkpoint through ESS states. A saved failure report is optional; without one, validate fresh user-requested in-memory status evidence through --reconcile-stdin with user_requested_status_check=true. Do not save core diagnostics or counts unless a specific file is requested. A pending
or uncertain load cannot use this branch. The proceed choice does not replace
fresh approval of the exact ESS payload or the validated delegation envelope.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PMINDEX.VALIDATE_BUSINESS_OBJECT | step | 10 | validate_input | valid->PMINDEX.VALIDATE_SCOPE_INPUT;invalid->PMINDEX.HANDLE_ERROR | none | stop | Always |
| PMINDEX.VALIDATE_SCOPE_INPUT | decision | 20 | validate_input | scope_ready->PMINDEX.VERIFY_BUSINESS_OBJECT;scope_partial->PMINDEX.VERIFY_BUSINESS_OBJECT;scope_missing->PMINDEX.REQUEST_SCOPE_INPUT;invalid->PMINDEX.HANDLE_ERROR | PMINDEX.VALIDATE_BUSINESS_OBJECT | stop | When adding, removing, or explicitly rebuilding one index; multiple index inputs are invalid |
