# Reference Lookups

Initialization uses the companion's `prepare_initialization_load` and
`initialization_status`, not direct API shortcuts. Require exact private load
and pinned Full job correlation, then a fresh catalog proving ABO pair presence.
See [ora_initial_full_publish.md](ora_initial_full_publish.md). Presence only
permits proposing Partial Publish; ESS requires its later enabled-entity proof.

| Resolver | When | Evidence | Rule |
|---|---|---|---|
| `read_cpq_commerce_settings` | CPQ preflight and verification | Commerce Settings state and selected process | Require one readable settings object. |
| `read_abo_delta_action_library_function` | CPQ preflight and verification | Exact fixed function value | Require `_s_getAttributesForABODeltaActionCalculation` after CPQ write. |
| `verify_fusion_abo_standard_process` | CPQ preflight | Exact process and `processType = 0` | Stop on missing or non-Standard process. |
| `validate_cpq_preparation_proposal` | Before workbook/Core startup and immediately before Core load approval | Exact approved business proposal and fresh semantic preflight | Preserve original explicit/default process choice; reject changed scope. Preparation digest never replaces Core's persisted preview digest or approval. |
| `read_cpq_abo_optin_states` | First Fusion preflight stage | Exactly two `COMBO` feature-state records: Asset-Based Ordering and Unified Oracle CPQ in Fusion | If either is false, return its one-feature shared-workflow approval handoff; do not read Subscription/Coverage states yet. |
| `read_subscription_coverage_optin_states` | Second Fusion preflight stage | Exactly two `COMBO` feature-state records: Subscription integration and Coverage integration | Run only after CPQ/ABO stage passes. If either is false, return its one-feature shared-workflow approval handoff. |
| `resolve_fusion_abo_subscription_optin_codes` | Metadata reconciliation only | `ORA_FOM_OSS_INTEGRATION_SUBSCRIPTIONS` and `ORA_FOM_OSS_INTEGRATION_COVERAGES` resolved from their exact Feature Names | Use `/features` exact-name GET evidence; do not infer codes from UI labels. |
| `read_adaptive_search_publish_status` | After an explicit user check verifies exact loader success | Child status for the same opaque operation and pinned job | One check unless the user currently chooses bounded 15-second job-only monitoring; check-later saves/stops; no repeated Data Loader checks. |
| `verify_adaptive_search_entities_enabled` | After child status is `SUCCEEDED` | Final child-skill entity evidence | Require both fixed entities enabled before ESS. |
| `resolve_ess_sync_submission_route` | Before ESS | Core submitter, fixed contract, successful child evidence, and separate exact-payload ESS approval | Submit only once after successful child evidence. |

The Adaptive Search skill remains under Sales Foundation. Fusion ABO calls only
the companion's declared persisted-preflight and status operations;
this cross-skill handoff does not change the companion's ownership.

Data Loader status inspection is permitted only on an explicit user request,
for the exact submitted CPQ or companion request. Pending returns a next-check
prompt and stops; final Adaptive Search readiness still gates separate ESS approval.
