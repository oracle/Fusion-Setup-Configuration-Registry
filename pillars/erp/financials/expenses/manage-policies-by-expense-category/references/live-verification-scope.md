# Live verification scope

The selected five-category creation case passed native import and independently
captured fresh-export reconciliation on cptcwxaqy, release 11.13.27.04.0. All
110 requirements passed with zero mismatches. Baseline business-row preservation
passed across all 19 entities. The FSM process log reported 18 successful objects,
zero failed objects and zero warnings; those object counts are not physical-row
counts. Exactly five policies and five rates were created and retained with
explicit approval, separately from four historical retained rows.

| Category | Configuration verified in this case |
| --- | --- |
| Airfare | No determinants; CATCH_ALL rate; COACH flight class |
| Car Rental | SINGLE USD currency; fixed daily limit; USD100 daily rate |
| Mileage | SINGLE USD currency; MILE unit; base MILEAGE rate0.65; no deductions, passenger or company add-ons |
| Miscellaneous | SINGLE USD currency; LIMIT mode; single-instance limit100; VIOLATION enforcement; warning enabled with tolerance10; display and prevention disabled |
| Per Diem | SINGLE formula; RATE calculation; DAYS multiplier; meals and accommodations included; no deductions or conversion; ANCHOR BaseRate100 |

All rates start2026-10-31 with no EndDate. Parents and ordinary rates are DRAFT;
the Per Diem ANCHOR rate is source-derived VALID. No activation, determinant,
update or delete was part of this creation case.

## Evidence identity

- Submitted candidate SHA256: `ded563cfc46c116aff4bd79a08ca648435b5b876b991faac8f77c344634b6009`.
- Fresh verification export SHA256: `c0f8d1bae7ba9be8a62ba7c98a2406e592cab897f50a7f6ddbf346746f266352`.
- Reconciliation report SHA256: `57b046ff11e1407f3ebd34738d6136a7298843336305e92c0e9a177c9bc2f7db`.

Raw exports, approvals, ProcessLog, requirement matrix and retained-state records
remain in the originating private project workspace. They are not shipped with
the skill and are not runtime prerequisites or reusable execution authority.
Export-local metadata ordering differences were explicitly reconciled under the
source-reviewed ordering contract; metadata was not claimed byte-identical.

## Interpretation and remaining limits

The environment and release above describe observations, not runtime allowlists.
User-provided names, amounts, dates and admitted choices remain supported subject
to normal validation; they need not equal the test values. This case does not
establish every supported combination, other target/provider/build parity,
nonblank EndDate behavior, all-or-nothing failure behavior, automatic cleanup or
rollback. Passenger/company Mileage, other Miscellaneous modes and expanded Per
Diem formulas/effects were not live qualified by this case. Rate Determinants
remain excluded. Existing-update exact-field uncertainty gates are unchanged.

Frozen source/evidence JSON files retain their capture-time qualification labels,
including `live_pending` and source-only assessments. Read them as the scope of
that evidence, not as a denial of this later independent live result. Do not
rewrite source-bound contracts or promote all runtime profiles to live-qualified
because one selected case passed. Each new candidate still requires fresh target
evidence, native validation/approval and its own post-import reconciliation.
