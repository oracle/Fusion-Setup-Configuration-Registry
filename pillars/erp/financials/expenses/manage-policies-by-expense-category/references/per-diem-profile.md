# Per Diem existing-row preparation


Per Diem policy and rate updates use their own service, line and value contracts.
Complete the existing workbook, bind fresh target currency and lookup evidence,
and review exact business-field uncertainty before native preview. This route
does not establish import acceptance or authorize a save/import.

Daily (`SINGLE`) uses the existing `ANCHOR` amount. `SUMUP` checks the selected
meal component amounts, accommodation night rate and Other amount independently;
zero is a value and TYPE/NUMBER meals need at least one amount, not all three.
The active no-determinant time formulas use RATE range rows. The captured UI's
calculation-choice filters require ADFDi for time percentage/spreadsheet choices;
they are not active choices in this no-determinant profile. Do not globally ban
their seeded codes or overwrite retained inactive settings.
The SINGLE formula also always displays its Meals Calculation Method selector;
its non-ADFDi/no-first-last-day choice is RATE even when Meals is not included.
Percentage, spreadsheet, invalid or missing active SINGLE method values must be
corrected explicitly before final validation. Dormant method fields in another
formula are preserved rather than rewritten.

Retain the full existing 17-coordinate line key and six-coordinate value key.
An omitted line subtype is taken only from a single exact existing match; it
does not default to `ANCHOR` or `STANDARD`. All input rows must keep their
existing dates, status, association, currency, keys and range coordinates.
An existing draft's empty business amount can be completed; business completeness
is checked on the merged resulting state rather than demanded before edits.

Percentage meal and accommodation deductions require value rows in addition
to ANCHOR columns. The reviewed FSM service imports lines and values separately
and does not call UI synchronization. When matching value rows already exist,
preparation explicitly includes their changed `LineValue` in the candidate and
exact-field acceptance plan. The review and blueprint disclose each such update.
All keys, audits and other values are preserved. A missing or ambiguous value
row, changed required value-row inventory, new association, new ID or clearing
effect cannot be replaced with an assumed generated import side effect.

The resulting-state checks include source EO eligibility-time ordering even
when its checkbox is inactive; selected component/deduction applicability;
source-synchronized lower/upper time ranges; complete identity uniqueness; and
exact active percentage value relationships. Retained inactive child rows are
preserved without making them writable targets or deleting them.

Changed deduction controls and rate amounts are checked against the final
merged parent, including rate-only requests. A deduction amount must match its
enabled DAILY/TYPE/NUMBER branch; a component or time amount must belong to its
actual ANCHOR/STANDARD/SAME/OTHER_STANDARD subtype and included component.
Parent and rate rows can be supplied together in either order. These checks do
not clear or rewrite unchanged dormant amounts or controls.

Active time duration inputs use the captured 0–24 hour and 0–60 minute ranges.
When enabled, this task requires at least one explicit hours/minutes value;
zero counts and no missing coordinate is generated. TIME_SUMUP accommodation
has the reviewed UI save predicate. Time meals uses the UI-required input
indication as an explicit task input policy: the captured commonCode refers to
different component bindings, so backend or UI-save enforcement of that pair
is not established. SUMUP's meals and accommodation duration inputs are both
commented out in the captured fragment; no new duration bound or pair rule is
imposed on those dormant values. Unchanged disabled duration values remain
preserved. See the evidence qualifications in the own source inventory.

Create, formula/currency/status/key/date/range-coordinate transitions, value-row
creation/deletion, and explicit-empty/default transformation need separate
qualification. Existing non-key business writes remain evidence-unresolved and
use the normal exact-field uncertainty and candidate-specific native approval
gates. Fresh export reconciliation must prove the requested values and preserve
all untouched state after any authorized import.

See [the own source inventory](per-diem-source-contract.json) and
[exact-field uncertainty](field-uncertainty-validation.md).
