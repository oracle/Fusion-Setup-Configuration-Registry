# Adaptive Search Preparation

The initial Full Publish exception is defined in
[ora_initial_full_publish.md](ora_initial_full_publish.md). On the allowlisted
missing/null/empty catalog condition, show its blocker and initialization
proposal, not another selective approval. The following applies to normal
Partial Publish after catalog initialization.

## adaptive-search-preparation

Prepare the fixed ConsolidatedAsset, SerializedAsset selective workbook only
after the exact CPQ Data Loader request succeeded on an explicit user status
check and fresh process, enablement and function readbacks passed, and the
separate ABO preparation proposal was approved. First show the complete ABO
template with CPQ verified, the fixed selective pair and ESS waiting. No
workbook generation or Core preflight starts until that preparation-only permission is validated,
CPQ/Fusion readiness is rechecked and the permission is consumed once.
The parent remains cpq_completed; separate adaptive_preparation metadata tracks
pending, consumed, cancelled, expired or failed preparation. Resume displays
the existing proposal or stopped state without starting Core. Explicit refresh
requires no submission intent/receipt and fresh preparation approval.
The companion validates target/entities/concurrency, constructs its canonical
values input and returns a versioned `core.data-loader` workbook handoff. Return
Core's confirmed workbook through `accept-adaptive-workbook`, then follow the
Core persisted-preflight and Task Hook handoff. Core freezes the immutable
archive and builds the bound preview after ordered rule evaluation. Return the
structured result through `build-load-preview`; the companion verifies the
source, archive, task context and preview. Preparation is not approval.
The second, independent Core preview binds the saved immutable archive; the first preparation affirmative never authorizes submission.
At successful Core approval readiness, display the companion's separate
`workbook_access` Markdown link once before the unchanged preview. Viewing is
optional and adds no gate; file edits do not alter the validated immutable archive.

After approval, follow the Core submit handoff and return its correlated receipt
through `complete-data-load`; never replay an uncertain reserved submission.
After submission, pause for an explicit load-status request. Follow Core's exact
status handoff and return its bound result. After exact load
success, pin the new publish job and check it once. If still nonterminal, show
the complete ABO template with the actual status and ask:
"Would you like me to keep checking every 15 seconds, or would you prefer to check the status later?"
The current keep-checking choice enables the bounded exact-job GET loop;
check-later saves the checkpoint and stops. A later status request checks once.
Both paths require final success and both entities enabled, then display the
same separate exact-payload ESS approval template. No Excel review step is added.
