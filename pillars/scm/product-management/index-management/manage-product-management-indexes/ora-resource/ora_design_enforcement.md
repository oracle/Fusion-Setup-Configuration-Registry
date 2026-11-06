# Design Enforcement

## Rebuild Source Provenance

The developer confirmed during the skill audit follow-up that
`PMESIndexMaintenanceJob` was also discovered through observed application
behavior. The existing rebuild request in the task's
[Index Rebuild ESS Workflow](../SKILL.md#index-rebuild-ess-workflow) is retained
as developer-provided, application-observed guidance. Its payload remains owned
by that workflow.

The observed Fusion release/build and a retained submission capture were not
supplied with this clarification. This provenance statement does not claim a
published Oracle job specification, establish Oracle support status, or report
an independent live verification. The default rebuild decision, including the
empty-delta branch, is this skill's workflow policy; discovery of the job does
not establish an Oracle requirement to rebuild after every operation.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Validate one index and metadata | Complete index, seeded and existing lookups; require available metadata and create contract only for prospective POSTs. |
| 2 | Calculate the delta | Apply the design rules before preparing any Data Loader source. |
| 3 | Validate prepared archive rows | Apply the input contract to prepared archive rows before core preview and approval. |
| 4 | Prepare the rebuild decision | Require successful load and readback, or a confirmed failed load with an explicit proceed choice, for a nonempty delta; retain separate ESS approval or explicit skip. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Every index change or rebuild: Single-index execution boundary | Blocker | resolve_product_management_index_code | Required enforcement is not satisfied: Accept one requested index per invocation; all addition and removal rows inherit its exact canonical IndexName. Reject a multi-index request or mixed Data Loader artifact before any Fusion mutation. | Ask the user to select one index; do not split, queue, or advance other indexes within this skill. | No silent correction |
| Every requested index change or rebuild, including removal-only: Index change-set delta calculation | Blocker | resolve_seeded_indexed_attributes | Required enforcement is not satisfied: Resolve requested additions from complete existing metadata first; retain unique matches as already indexed and validate only unsatisfied requests through available metadata. Build a de-duplicated ordered union of seeded identities and validated requested-addition identities. For an explicit rebuild without additions/removals, use seeded identities as the complete target set. Subtract existing matches before preparing POST: resolved subtype requires exact triplet plus subtype even without user subtype input; only metadata without subtype and seeded requirements use triplets. Missing seeded repair POSTs retain their uniquely resolved subtype. Missing subtype evidence blocks scoped comparison; preserve alternate subtypes. Resolve every explicitly requested removal by all original name/code/subtype/ID constraints to one existing backend record before final delta validation. Preserve resolved removal evidence separately from the original request. Compare all resolved requested additions, including already-indexed matches, against resolved removals before source preparation and again before prepared-archive approval. Equal attribute/group/object code triplets conflict when the resolved addition subtype is blank or equals the removal subtype. Distinct resolved subtype codes do not conflict. Reject overlap with input_validation and request a choice of add or remove; never infer replacement or silently prefer deletion. Conflicting codes must not be ignored even when supplied names match. Validate the initial delta with index_delta_guard.py --stdin without --require-data-loader. If the validated data_loader_required result is false, follow the empty transition to PMINDEX.PREPARE_ESS_REBUILD_EMPTY without source preparation or Core preflight. If true, require --require-data-loader before source preparation and --stdin --require-data-loader --archive and --archive-sha256 with Core's prepared ZIP and preflight digest and the applicable live create contract before approval, including removal-only changes. Every POST carries the exact resolved codes, including nonblank metadata-derived ObjectSubTypeCode; omission or mismatch blocks approval. Follow Core's existing CLI preflight, immutable archive, Task Hook preview, persistence and approved-preflight submission contract. | Stop when an identity is incomplete, a lookup result is unavailable, the calculated delta is missing or mismatched, or a prospective POST identity cannot be resolved to one exact available attribute. | No silent correction |
| When removals are requested: Removal separation | Blocker | resolve_existing_product_management_es_indexed_attribute | Required enforcement is not satisfied: Prepare DELETE rows only for explicitly requested removals after all supplied names, codes, subtype selectors and ID constraints resolve to one exact backend-issued AttributeId. Names-only, code-only and mixed input are equally valid; do not require the user to supply metadata-resolvable names. Reject duplicate DELETE IDs and changes to resolved removal evidence. Do not remove a seeded or existing attribute merely because it is absent from the requested-addition list. | Stop before DELETE preparation when the requested identity has no unique backend record. | No silent correction |
| After addition/removal delta calculation: Rebuild submission | Blocker | resolve_existing_product_management_es_indexed_attributes | Required enforcement is not satisfied: For every requested index operation, prepare the immutable ESS payload. When the calculated change set is nonempty, require successful Data Loader status and readback, or confirmed terminal failure with an explicit same-index rebuild choice. When it is empty, persist the validated delta, record Data Loader as intentionally skipped, prepare the immutable ESS payload and persist ess_approval_pending before review. Empty deltas and normal review do not imply blocked or ESS skip. After fresh approval, apply the ESS approved handoff rule in ora_input_validation.md and delegate its validated approved_submission envelope to core.fusion-api.ess-job-submitter once with submit-only behavior, unless the user explicitly confirms ESS is not required. | Do not submit ESS if the load is pending, uncertain, targets another index, or is failed without an explicit rebuild choice and fresh exact-payload approval. Do not skip ESS without the user's explicit not-required confirmation. | No silent correction |
| After a successful Data Loader status result for a nonempty delta: Successful-load continuation | Blocker | resolve_existing_product_management_es_indexed_attributes | Required enforcement is not satisfied: A terminal successful user-requested Data Loader status result, including an evidence-validated reconciliation of the same accepted request, must record the task checkpoint to data_load_succeeded, read back every requested change for the exact canonical IndexName, prepare the immutable ESS payload, then transition to ess_approval_pending and request fresh approval in the same reply. | Do not end at the status report, omit readback, or submit ESS without the separate approval. | No silent correction |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_product_management_index_code | Before the dependent design rule | One exact canonical IndexName for the selected index | ora_reference_lookups.md |
| resolve_seeded_indexed_attributes | Before the dependent design rule | Seeded AttributeCode#GroupCode#ObjectCode identities | ora_reference_lookups.md |
| resolve_existing_product_management_es_indexed_attributes | Before the dependent design rule | Existing AttributeCode#GroupCode#ObjectCode identities and record details | ora_reference_lookups.md |
| resolve_existing_product_management_es_indexed_attribute | Before the dependent design rule | One backend-issued AttributeId for an explicitly requested removal | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PMINDEX.CALCULATE_ATTRIBUTE_DELTA | decision | 87 | design_enforcement | calculated->PMINDEX.DATA_LOADER_GATE;empty->PMINDEX.PREPARE_ESS_REBUILD_EMPTY;blocked->PMINDEX.HANDLE_ERROR | PMINDEX.RESOLVE_REMOVAL_ATTRIBUTE_IDS | stop | Every requested index change or rebuild; all removal identities are resolved and cross-operation overlap is rejected before final delta validation and prepared-archive approval; nonempty POST or DELETE rows reach the Data Loader gate |
| PMINDEX.PREPARE_ESS_REBUILD | decision | 140 | design_enforcement | prepared->PMINDEX.REQUEST_ESS_APPROVAL;explicit_skip->PMINDEX.DONE_ESS_SKIP_AFTER_LOAD;blocked->PMINDEX.HANDLE_ERROR | PMINDEX.VERIFY_LOADED_ATTRIBUTES | stop | The nonempty Data Loader delta was read back successfully |
| PMINDEX.PREPARE_ESS_REBUILD_EMPTY | decision | 141 | design_enforcement | prepared->PMINDEX.REQUEST_ESS_APPROVAL_EMPTY;explicit_skip->PMINDEX.DONE_ESS_SKIP_EMPTY;blocked->PMINDEX.HANDLE_ERROR | PMINDEX.CALCULATE_ATTRIBUTE_DELTA | stop | The validated POST and DELETE delta is empty; persist it, skip Data Loader, prepare the exact canonical-index ESS payload and persist ess_approval_pending before fresh approval |
| PMINDEX.PREPARE_ESS_REBUILD_FAILED | decision | 142 | design_enforcement | prepared->PMINDEX.REQUEST_ESS_APPROVAL_FAILED;blocked->PMINDEX.HANDLE_ERROR | PMINDEX.DECIDE_FAILED_LOAD_REBUILD | stop | Confirmed terminal failed load and explicit proceed choice for the same Request ID and canonical index; retain terminal failure checkpoint markers and current in-memory status evidence or an authorized report, without requiring a saved core failure file, and prepare the immutable payload without declaring load success |
