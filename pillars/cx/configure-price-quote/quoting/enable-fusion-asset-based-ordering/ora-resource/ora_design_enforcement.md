# Design Enforcement

The allowlisted missing-metamodel/null/empty catalog inserts
[ora_initial_full_publish.md](ora_initial_full_publish.md) before selective
submission. Keep CPQ verified; require separate Full preparation and Core
approvals, exact successful load/job/catalog proof, then fresh selective
preparation and Core approvals. Initialization evidence cannot authorize ESS.

## Required Sequence

1. Fresh routed CPQ/Fusion preflight; show the full ABO template and exact normal
   or function-only CPQ plan. Stop for preparation-only approval before generating
   a workbook or starting Core. Bind the permission to the current business
   proposal and its two-hour validity; recheck scope and consume it once before
   preparation. Decline cancels only this unconsumed proposal. Resume shows the
   same proposal; changed/expired proposals require fresh preflight and approval.
2. Retain one Core persisted preflight, evaluate ordered task rules against
   validated source records, show Core's Markdown verbatim and obtain a second contextual
   approval. Preparation consent never authorizes or substitutes for this load.
3. Reserve intent, then have Core verify and submit the exact persisted artifact after independent load approval; return Core's receipt
   and pause: "Check the CPQ load status and continue."
4. On that explicit request, verify exact load success and all three CPQ values.
   Show the full ABO template and fixed selective proposal; stop for separate
   preparation-only approval before generating a companion workbook or starting
   Core. Preserve cpq_completed and use separate preparation metadata. Recheck
   CPQ/Fusion readiness, validate the two-hour permission and consume it once.
   Only then invoke the existing companion and obtain its independent Core load
   approval. Resume never starts preparation; decline/expiry retains CPQ history.
5. After separate publish approval, return its submission and pause:
   "Check the Adaptive Search load status and continue."
6. On that explicit check, require exact loader success. Then perform existing
   job discovery and one pinned-job check, without further Data Loader queries.
   If still pending, show the full template and offer keep checking every 15
   seconds or check later. Current keep-checking consent enables bounded
   job-only monitoring; check-later saves the checkpoint and stops. Later status
   requests check once. Require exact final two-entity readiness on either path.
7. Show the fixed ESS payload and obtain separate exact-payload approval.
   Preserve the single submission reservation and bounded ESS monitoring.
   Relay the full ESS approval and final completion templates, not summaries.

## Prohibitions

- No Core edits, direct publish POST, substituted execution route or global retry.
- Keep the Core preflight, archive digest, task preview and approval envelope bound to the exact load. Do not reconstruct the validated archive from an edited workbook.
- No detached runner/listener or artificial keepalive.
- No automatic Data Loader polling, republish on uncertainty, or ESS before readiness.
- Preserve historical evidence; saved approvals never authorize new mutations.
  The saved ABO business proposal permits preparation only; it contains no
  pending Core preview/source data. Do not restart already-running/submitted
  legacy checkpoints to insert the new preparation gate.
  Refresh only a stopped, unsubmitted preparation with no companion intent or
  receipt. Never use the earlier preparation affirmative as Core load approval.
