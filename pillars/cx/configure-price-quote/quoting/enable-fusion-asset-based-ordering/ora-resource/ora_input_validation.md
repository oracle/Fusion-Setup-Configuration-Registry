# Input Validation

Initial Full Publish additionally requires the known catalog blocker, ordered
nine-object scope, separate two-hour one-use preparation permission, distinct
initialization receipt and independent Core approval from
[ora_initial_full_publish.md](ora_initial_full_publish.md). Selective-pair
inputs below remain mandatory for the later normal Partial Publish.

| Input | Required When | Validation |
|---|---|---|
| Target context | Every run | Exact selected Fusion/CPQ target; do not repoint submitted checkpoints. |
| Process | Before preflight | Exact supplied variable or explicit default choice; verify Standard Process. |
| CPQ/ABO features | First feature stage | Exactly two expected COMBO records, one per code, boolean StatusFlag. |
| Subscription/Coverage features | After CPQ/ABO pass | Exactly two expected COMBO records, one per code, boolean StatusFlag. |
| Opt-in choice | Shared update | Shared workflow resolves exact choiceShortName; no inferred fallback. |
| Task context | Core preflight setup | Original project/Run Book; exactly one Enable Fusion Asset-Based Ordering task with a positive integer sequence (not boolean). |
| CPQ preparation approval | Before workbook generation/Core startup | Later contextual affirmative for the full ABO proposal; exact project/workflow, target, fixed normal/function-only plan, original process selection and semantic preflight digest. Two-hour expiry; one-use permission. Fresh readback must match before preparation and again before load approval. |
| Load approval | Each load | Independent contextual approval of the exact current saved Core preview and immutable validated archive after ordered task checks. |
| Adaptive Search preparation approval | Before companion workbook/preflight preparation | Exact current business proposal: project/workflow, target, selected process, verified CPQ receipt and fixed ConsolidatedAsset/SerializedAsset selective pair. Two-hour one-use permission; recheck CPQ/Fusion readiness before handover. Never forward this permission as Core approval. |
| Workflow ID | Continuation | Non-executable project/target/business provenance; not load approval. |
| Status request | Data Loader check | Explicit current user request; exact submitted IDs and target. |
| Publish monitoring choice | Before repeated publish checks | Explicit current continuous/manual choice bound to this workflow/project/target/opaque operation; verified loader success required. Continuous uses 15-second intervals. |
| Publish status request | Later job check | One exact-operation job check; prior monitoring consent does not restart a loop. |
| Companion result | Before ESS | Same opaque operation and fixed pair; terminal success and final enabled evidence. |
| ESS approval | Before ESS POST | Exact current payload digest, target and separate explicit approval. |

Reject raw URLs, bodies, caller-selected sources/ESS parameters, legacy saved
approvals and mismatched identities. Never silently replace a lost prepared load.
The preparation proposal digest is business provenance, not a Core source hash
or load approval. Decline/resume cannot upload; an already consumed permission
cannot start another prepared load. No Excel review gate is introduced.
