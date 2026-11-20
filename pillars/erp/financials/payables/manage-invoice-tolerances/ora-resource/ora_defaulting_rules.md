# Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| ToleranceType | No default; require an explicit type on create | A create candidate omits ToleranceType or supplies it blank | Block before ZIP creation and require an explicit QUANTITY BASED or AMOUNT BASED code | |
| Tolerance limit fields | No source-backed task-wide default | A create or update candidate omits a limit | Preserve blank or existing value as appropriate; do not synthesize zero | |

## Dependent-clear normalization

For an explicit update to `ToleranceType=AMOUNT BASED`, include blank `PriceTolerance`, `ShipAmtTolerance`, `QtyConsumedTolerance` and `MaxQtyConTolerance` values during normalization, and disclose each derived clear with its prior value in the preview. Reject conflicting explicit nonblank inputs. Validate, serialize and reconcile the same effective values; a prepared ZIP must contain the agreed blanks and is never rewritten during validation. Preserve all unrelated fields and all omitted fields on unrelated updates. This is a source-backed type-switch consequence, not a create default or an import-side automatic clear.
