# Field Service Technicians Error Handling and Handoff Gate

Current capability gate: the task SKILL.md permits metadata/sample and explicitly requested status only. Complete business/reference reads and create/update/delete preparation are unsupported. Return blocked (invalid at input validation) before external activity or source preparation; the remaining domain contracts do not enable those operations.

The task selects only `core.data-loader` for Fusion-facing operations on `technicianSubinventories`. Data Loader owns technical diagnostics. Complete assignment and reference reads use a future reviewed core Data Loader reader selected by the task Reference Read Workflow; task export and registration publication remain unsupported capability gates; no substitute route is authorized. Readiness requires the reviewed operation-specific input contract, live identity checks, and immutable Data Loader artifact. Create rejects duplicates; an EnabledFlag-only update, default usable repair or one selected assignment deletion requires exactly one existing assignment and its server-returned surrogate. This gate prepares a preview; it does not approve submission.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Task source fields or existing-record identity are unresolved | Stop before preview or import; obtain a reviewed task-specific contract |
| Exact Data Loader registration is missing | Stop source preparation with catalog mismatch; ask the environment owner to confirm registration and metadata visibility, then retrieve and validate its live template before resuming |
| Requested condition differs from the selected stock location | Stop the create request; Condition is read-only on the assignment, so never update the stock location or an existing assignment to force the requested condition |
| Data Loader reports a missing default usable subinventory | Treat RCL_NO_DEF_USABLE_SUBINV as a business prerequisite failure. Confirm load outcome and current records through Data Loader; block the same nondefault create before upload. Obtain an explicit default-assignment decision, prepare a materially corrected immutable artifact, rerun Task Hook and obtain fresh approval before retrying. Do not attribute this diagnostic to Boolean serialization or alter unapproved assignments |
| Complete Data Loader reader or reference evidence is unavailable | Stop with catalog mismatch before preview or approval; resolve the owning Data Loader reader failure and obtain fresh complete evidence. No request, sample enrichment or alternate executor is permitted |
| Task export or registration publication is requested | Stop with unsupported capability; environment-owner registration repair is outside this skill and requires independent governance |
| Operation privileges are missing or unverified | Stop before submission; owning core preflight must establish authorization for the exact operation and target; metadata read access is insufficient |
| Create handoff is not ready | Stop until live registration/template validation, create-only source, unique identities, matching condition, duplicate rejection, and immutable archive preparation pass; hand off through Task Hook and core.data-loader only |
| EnabledFlag update handoff is not ready | Stop until the exact existing assignment, registered surrogate, PATCH operation, three-column source and approved flag change are validated; do not create a replacement assignment or include unrelated writable fields |
| Default usable repair handoff is not ready | Stop until explicit target selection, one existing usable row, no competing default usable row, exact surrogate, four-column source and immutable preview are validated. Require Data Loader approval and verified repair completion before preparing a dependent nondefault create; preserve the defective default and all unrelated assignments |
| Assignment delete handoff is not ready | Stop until one selected existing assignment, its server-returned surrogate, live DELETE action, two-column delete source and immutable artifact are validated; missing or ambiguous selection blocks before approval and deletion |
| Submission or outcome is uncertain | Retain the approved artifact and envelopes; reconcile through the owning core.data-loader status workflow before any new submission |
| Boolean fields have String loader metadata after HTTP 400 | Inspect the complete source, payload exclusions, live Data Loader field contract and available generated-request diagnostics; do not attribute the failure to serialization without the generated request. A fresh attempt requires a reviewed material correction, new immutable artifact and approval; never invent a registration override, substitute another executor, or claim that source validation proves backend success |
| Successful load but readback is missing, ambiguous or mismatched | Do not claim a verified create or update. Use a fresh complete Data Loader read, show the actual observed values when available, preserve diagnostics and stop dependent writes. Never replay the mutation automatically |
| Export, validation, or import fails | Stop and use the owning core.data-loader diagnostics; do not invent a retry or substitute another executor |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Before import handoff | Target environment, exact task, supported operation, validated source and keys, preview outcome, and approval state |
| Status or saved-record display explicitly requested in the active request | Use core status only for the explicit request. After confirmed completion, obtain fresh complete root assignment evidence through a future reviewed core reader; disclose read/verification failures separately from load status. Accepted initiation and load counters alone never prove saved record values |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Source contract, record identity, validation, preview, or approval is unresolved | Do not submit an import or select another executor |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FST.EXECUTION_GATE | decision | 3 | execution_gate | ready->FST.RETURN_PREPARED;blocked->FST.RETURN_REFUSAL | FST.RESOLVE_IDENTITIES | stop | After input validation and reference resolution; require complete Data Loader reference evidence, verified operation privileges and validated immutable Data Loader artifact before preview |
| FST.RETURN_PREPARED | terminal | 4 | terminal | none | FST.EXECUTION_GATE | continue | All checks for the selected create, EnabledFlag-only update, default usable repair or one assignment deletion pass; return prepared preview for separate Data Loader approval; no import has occurred |
| FST.RETURN_REFUSAL | terminal | 5 | terminal | none | none | continue | A required task contract or validation gate is unresolved |
