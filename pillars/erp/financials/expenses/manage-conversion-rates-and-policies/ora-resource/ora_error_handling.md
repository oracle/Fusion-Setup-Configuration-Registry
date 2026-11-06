# Manage Conversion Rates and Policies Error Handling

Controlled existing-row blank imports established required-attribute failures for parent default, child default and child display flags (SRC-FSM-EXM-BLANK-20261014). Off-domain flags, numeric violations, reference failures, new-row omissions and universal atomicity remain unproved. `core.data-loader` owns immutable preview, approval and submission. Return immediately on accepted initiation. Later explicitly selected status and ProcessLog workflows use the original request identity; no automatic polling or resubmission.

## Error Situations

| Situation | What Should Happen | Evidence |
|---|---|---|
| Package member or header mismatch | Stop before candidate generation and obtain a fresh same-task template | Same-task template inventory |
| Business unit or conversion type has zero or multiple read-only matches | Report the affected input and match count; correct the value before a new preview | SRC-CODE-EXM-AMIMPL, SRC-CODE-BU-PVO, SRC-CODE-GL-PVO |
| Currency code is missing, inactive or disabled in read-only preflight | Report the exact code and destination check; do not claim the FSM import would return the same error | SRC-CODE-EXM-CURRENCY-LOV, SRC-ORACLE-26C-REST-CURRENCY |
| Flag is outside Y or N | Reject locally before package build; report input_validation without inventing a Fusion error | SRC-CODE-EXM-UI-PAGE, SRC-CODE-EXM-UI-ROW |
| Fusion import fails after separately approved submission | Persist the process identity, status and redacted ProcessLog; classify the observed error and stop before another submission | core.data-loader status/ProcessLog contract; SRC-FSM-EXM-BLANK-20261014 |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Task identity, package shape, required business input or fixed flag domain fails | Correct the input and rebuild the immutable preview |
| Catalog mismatch | Task code, business object or package member conflicts with effective catalog or live metadata | Stop and reconcile exact task identity |
| Auth or environment | Read-only path or authorized loader cannot reach the selected environment | Preserve the context and resolve access before retry |
| Fusion API or process failed | A governed import returns a task-bound failure | Retrieve ProcessLog; do not infer success or automatically resubmit |
| Approval blocker | Candidate-specific preview and approval are absent or changed | Return for the exact approval required by core.data-loader |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Static readiness | Exact task, target environment, source IDs, incomplete rules and unproved operation contracts |
| Loader handoff | Exact immutable archive, intended operation and business effect, environment, validation result and candidate-bound approval status |
| Failed process | TaskCode, ProcessId or request ID, last status, elapsed wait, redacted ProcessLog and one safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Clearing, unknown defaults, rekeying, deletion or unsupported fields are requested | Stop with the exact unsupported contract; never waive it or use a different execution route |
| A write is uncertain or failed | Do not retry POST, import or ESS work without reconciliation and a new approval when required |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| EXMCR.EXECUTION_GATE | decision | 7 | execution_gate | ready->EXMCR.STATIC_HANDOFF;blocked->EXMCR.BLOCKED | EXMCR.CHECK_DESIGN | stop | Supported create/update candidate with source-required fields and nullable percentages, verified references, preservation and core preflight; return validation only before core approval |
| EXMCR.BLOCKED | terminal | 8 | terminal | none | none | stop | Return unresolved source-backed blockers without Fusion mutation |
| EXMCR.STATIC_HANDOFF | terminal | 9 | terminal | none | EXMCR.EXECUTION_GATE | stop | Return a task-local static handoff only after all declared gates are complete |

<!-- E2E-DISCOVERY:DISC-EXM-CONTRACTS-20261014 -->
## Observed required-attribute failure boundary

For the single-field existing-row blank probes, FND_CMN_REQ_ATTRIB_API_SERV was captured in actual FSM ProcessLogs when parent DfltExchangeRateFlag, child DfltExchangeRateFlag or child DispWarningToUser was blank. Fresh exports showed no business/audit changes for those attempts. The child-field failures were reported in ExchangeRateOption parent detail and the parent CSV; preserve actual attribution. This does not establish universal import atomicity or other error messages.
