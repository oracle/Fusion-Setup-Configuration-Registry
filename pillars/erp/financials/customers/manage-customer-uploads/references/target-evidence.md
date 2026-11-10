# Before-state target intent


For the supported existing-target API route, use the raw collection/replay and
`customer_api_target_review` contract in [assisted evidence](assisted-evidence.md).
Its explicit plan binds the collection hash and contains one intent per row/entity.
Both routes preserve the same identity, ambiguity and parent-consistency rules.
The following detailed identity/ownership schema is the alternative supplied
developer-evidence route, not a SQL prerequisite for a business user.

`scripts/customer_target_review.py:analyze` combines raw before-state identity
and ownership evidence with explicit create/update/reuse intent for every row
and each of the seven entities. The campaign reviewer accepts these under
`before_identity`, `before_ownership` and `target_plan`.

The exact plan schema `ar-customer-target-plan-v1` contains candidate_sha256,
environment_url, operation_intent, identity_evidence_sha256,
ownership_evidence_sha256, timezone-qualified captured_at, review_reference,
expectations and number_queries. Every expectation has row (one-based), entity
and intent. The overall operation does not force every supporting entity to be
created; reused parents and new children are supported. Shared targets must have
consistent intent, including when different source references resolve to the
same physical ID.

Each number query contains field, value, complete and records of
`{owner_table_id: "<positive decimal ID>"}`. Query each supplied PARTY_NUMBER,
ACCOUNT_NUMBER and PARTY_SITE_NUMBER against its full table, preserving duplicate
results and returning actual IDs. Do not filter by expected party/parent, source
system, status or anticipated ID. An empty complete result is distinct from a
missing query. A nonempty result for a proposed new target is a collision. An
existing reference and number must identify the same target; differences need
review rather than a silently inferred renumbering operation.

Existing targets require unambiguous source references, observed target rows,
parent/set relationships and site-use purposes. Historical/inactive ambiguity
does not become a first-match selection. A new reference proposal cannot
silently reparent an existing child. Absent references/numbers are point-in-time
observations; they do not prove global absence, reserve an identity, establish
physical creation or authorize an import.

`TARGET_INTENT_OBSERVATIONS_CONSISTENT` means this supplied target evidence agrees
with the declared intent. It does not verify field mutability, before-state value
differences, defaults, privilege, readback provenance/freshness, execution
readiness or approval. Those remain separate gates. Complete raw results and
query scope must be reviewed through the declared campaign evidence route.

For the accepted Publisher-backed campaign, capture scoped read-only FSCM
results outside the reusable task tree. The local checker performs no Fusion
call and does not establish an automatic REST resolver. Any eventual use as an
assisted Task Hook input needs an explicit local-evidence contract and semantic
review; do not relabel the current incomplete fusion-rest node as ready.
