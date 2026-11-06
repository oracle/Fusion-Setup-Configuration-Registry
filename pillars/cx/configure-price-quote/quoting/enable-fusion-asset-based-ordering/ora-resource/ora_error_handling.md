# Error Handling

For Entities' exact HTTP 400 `Could not find active meta model`, null response,
null `items` or empty `items`, retain the safe error and CPQ completion and
offer [initial Full Publish](ora_initial_full_publish.md), not another selective
approval. Other errors stop without Full Publish fallback. Failed jobs, unknown
correlation and possibly-sent intents require exact status/reconciliation,
never automatic retry or ESS.

| Failure | Required response |
|---|---|
| Invalid input, task sequence, target or rule evidence | Stop before approval; correct and validate a fresh preflight. |
| CPQ preparation missing/declined, mismatched, expired or consumed | Do not generate a workbook or start Core. Resume the same unconsumed proposal, or cancel it and prepare a fresh proposal with fresh approval. Never use this permission as load approval. |
| CPQ state/prerequisites changed after preparation proposal | Mark preparation failed; show no actionable approval. Re-preflight and approve a fresh proposal; cancel any unsubmitted Core preflight rather than reusing its preview. |
| False/malformed CPQ/ABO feature evidence | Stop before Subscription/Coverage; use the existing one-feature shared approval/readback workflow. |
| False/malformed Subscription/Coverage evidence | Stop before CPQ; resolve through the existing shared route and rerun preflight. |
| Metadata 401/403 | Report the exact approved stage and safe classification; do not guess privileges or bypass Core. |
| Prepared artifact missing, cancelled or expired before approval | Fresh preparation and fresh approval; never reuse an expired or changed preview. |
| Upload/initiation possibly started | Persist intent/confirmed correlations; reconcile only on request. No automatic retry. |
| CPQ load pending | Pause with "Check the CPQ load status and continue." |
| Adaptive Search preparation missing/declined, expired, mismatched or consumed | Stop before companion workbook/preflight preparation. Retain CPQ completion and show no actionable load approval. Resume the same pending proposal; explicitly refresh a stopped proposal only when no submission intent/receipt exists, then obtain fresh preparation and Core approvals. |
| CPQ/Fusion readiness no longer verified before companion preparation | Stop and retain historical CPQ completion; do not reload CPQ or submit publish/ESS. Diagnose readiness through the declared read-only routes before a fresh attempt. |
| CPQ failed/unknown or readbacks invalid | Block companion; exact status/read-only reconciliation only. |
| Companion load pending | Pause with "Check the Adaptive Search load status and continue." |
| Companion failed/unknown, correlation missing | Stop before ESS; never republish automatically. |
| Verified-load Adaptive Search job pending | Show actual status and full template; offer 15-second monitoring or check later. Loop only on current choice; later status checks once, no repeated Data Loader reads. |
| Publish monitoring timeout/interruption | Monitoring stopped, not still running. Preserve exact operation/job and last status; later check once or obtain fresh keep-checking choice. Never republish or submit ESS. |
| Nominal publish success without exact readiness | Stop before ESS. |
| ESS uncertain/timeout | Preserve request and use existing exact-request monitoring/reconciliation; no new POST. |
| Checkpoint persistence failure after approval | Treat outcome as uncertain; do not recreate or retry. |

Classify input validation, catalog mismatch, auth/authz, transport/environment,
Fusion API, process timeout/failed, artifact persistence and approval blockers.
Never persist secrets, raw errors or sensitive diagnostics.
