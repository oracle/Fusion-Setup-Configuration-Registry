# Design Enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_TOLERANCE_TEMPLATE::Description, AP_TOLERANCE_TEMPLATE::MaxQtyConTolerance, AP_TOLERANCE_TEMPLATE::MaxQtyOrdTolerance, AP_TOLERANCE_TEMPLATE::MaxQtyRecTolerance, AP_TOLERANCE_TEMPLATE::PriceTolerance, AP_TOLERANCE_TEMPLATE::QtyConsumedTolerance, AP_TOLERANCE_TEMPLATE::QtyReceivedTolerance, AP_TOLERANCE_TEMPLATE::QuantityTolerance, AP_TOLERANCE_TEMPLATE::RateAmtTolerance, AP_TOLERANCE_TEMPLATE::ShipAmtTolerance, AP_TOLERANCE_TEMPLATE::ToleranceName, AP_TOLERANCE_TEMPLATE::ToleranceType, AP_TOLERANCE_TEMPLATE::TotalAmtTolerance -->
<!-- fscr-update-fields: AP_TOLERANCE_TEMPLATE::Description, AP_TOLERANCE_TEMPLATE::MaxQtyConTolerance, AP_TOLERANCE_TEMPLATE::MaxQtyOrdTolerance, AP_TOLERANCE_TEMPLATE::MaxQtyRecTolerance, AP_TOLERANCE_TEMPLATE::PriceTolerance, AP_TOLERANCE_TEMPLATE::QtyConsumedTolerance, AP_TOLERANCE_TEMPLATE::QtyReceivedTolerance, AP_TOLERANCE_TEMPLATE::QuantityTolerance, AP_TOLERANCE_TEMPLATE::RateAmtTolerance, AP_TOLERANCE_TEMPLATE::ShipAmtTolerance, AP_TOLERANCE_TEMPLATE::ToleranceType, AP_TOLERANCE_TEMPLATE::TotalAmtTolerance -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 10 | Task and package identity | Confirm exact same-task CSV, metadata, ordered headers, and row widths |
| 20 | Business and field contract | Confirm create-only name uniqueness, type, amount-based conflict, and field-level allowlists |
| 30 | Environment readiness | Use either exact supported FSM import code; retain governed preview and actual import-result verification |
| 40 | Governed execution | Use core.runbook and core.data-loader immutable preview and candidate-bound approval before any Fusion import |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Always | Error | | Package identity, header order, row width, or metadata node differs from exact export | Restore same-task package fidelity | Yes, with a corrected package |
| Create | Error | | Candidate ToleranceName is in the set of existing names in a fresh full same-task export or repeats among newly requested create names | Choose a different name before preview; do not assume a zero exact match proves case/space variants are accepted | Yes, with corrected candidate |
| Create; update when type supplied | Error | | Create omits ToleranceType or supplies it blank, or a supplied type is neither QUANTITY BASED nor AMOUNT BASED | Supply one of the two exact task package codes on create; validate a supplied update code. Fusion rejected a blank create type as required (JBO-27014) | Yes, with corrected candidate |
| Any applicable tolerance limit is supplied | Error | | The value is nonnumeric in either tolerance type | Supply a decimal value for that field; do not infer precision or range from the UI example | Yes, with corrected candidate |
| ToleranceType is AMOUNT BASED | Error | | PriceTolerance, ShipAmtTolerance, QtyConsumedTolerance, or MaxQtyConTolerance is nonblank in the proposed candidate | For a requested type change, show each existing quantity-only value becoming blank and include that blank explicitly in the candidate. Block if the requester insists on keeping a conflicting value; do not rely on import to clear it automatically | Yes, with an explicit corrected candidate |
| Update | Error | | ToleranceName is renamed or unrelated fields/rows would change | Preserve the existing name and unrelated state; do not apply create-name uniqueness validation to updates | Yes, with corrected candidate |
| Any requester-authored field | Error | | Field is outside the documented create/update allowlist or is system-managed audit data | Remove unsupported changes and retain source-backed boundaries | Yes, with corrected candidate |
| Physical deletion or retirement | Error | | No task-specific import deletion/end-date contract is established | Stop and seek task-specific evidence | Only after new evidence and approval |
| Live import | Error | | Supported type validation, immutable preview, candidate-bound approval, or core.data-loader route is absent | Complete the governed central workflow; submit once and verify persisted state | Yes, through central workflow |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| TOLERANCE.ENFORCE_DESIGN | decision | 20 | design_enforcement | ready->TOLERANCE.EXECUTION_GATE;blocked->TOLERANCE.DESIGN_BLOCKED | TOLERANCE.VALIDATE_INPUT | stop | Always |

## Dependent-clear normalization

For an explicit update to `ToleranceType=AMOUNT BASED`, include blank `PriceTolerance`, `ShipAmtTolerance`, `QtyConsumedTolerance` and `MaxQtyConTolerance` values during normalization, and disclose each derived clear with its prior value in the preview. Reject conflicting explicit nonblank inputs. Validate, serialize and reconcile the same effective values; a prepared ZIP must contain the agreed blanks and is never rewritten during validation. Preserve all unrelated fields and all omitted fields on unrelated updates. This is a source-backed type-switch consequence, not a create default or an import-side automatic clear.
