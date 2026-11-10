# Defaults and preservation

One controlled27A absent-BU create persisted blank PaymentsApprovalFlag as N while all other requested business values and all pre-existing cells matched. Clarify the intended persisted value before proposing blank as an exact outcome. Never silently coerce blank to N, weaken reconciliation or apply this observation to existing-row updates/other contexts. Source: SRC-E2E-CREATE-C01-164773.
Keep requested input and observed output distinct. No universal scalar default or blank-update behavior is proved.


Create preparation requires explicit values for every business field, including
intentional optional blanks. No existing row supplies defaults. Blank audit and
derived usage serialization is a disclosed service-assignment proposal requiring
qualification, not a business default. Preserve all pre-existing cells in a
create batch. AutomaticPprReportSubmit is not declared non-null in the reviewed
EO/import VO; do not replace its explicit blank with N. PaymentsApprovalFlag's
different VO/EO hints remain an exact-create qualification uncertainty.

Scope: IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS.

Source: SRC-GOLD-EO-SNIPPETS, SRC-GOLD-VO-SNIPPETS, SRC-USER-ROUNDTRIP-153565. No task-owned scalar create default is established. Existing exported settings are baseline facts, never universal defaults. Blank PaymentsApprovalFlag must remain blank when unrequested.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| All task fields | No task-owned default; obtain explicit evidence-backed create inputs | Create | No |  |
| Unrequested existing values | Preserve exact baseline including blanks and service-owned metadata | Update | No | match_baseline_identity |

## Observed update evidence and its limits

Observed values are update facts, never create defaults. Enterprise AutoPPR was restored N -> Y; enterprise subject was restored to Automatic Separate Remittance Advice and the two observed named-BU subjects to their original blanks. Preserve every unrequested value and unrelated row. Blank subject restoration does not imply blank-to-value normalization, and blank PaymentsApprovalFlag remains preserved when unrequested. Sources: SRC-E2E-OBSERVED-AUTOPPR-164493-164510, SRC-E2E-OBSERVED-SUBJECT-164559-164580.

## Observed create and reviewed lookup source boundaries

Only the two recorded retained explicit-N creates are observed: terminal request164877 succeeded, while its original fresh-export comparison failed for hidden expected identities. Later export300104797771464 after separate user-completed prerequisite setup matched both creates and all1219cells of the previous53rows without reimport. c01 blank PaymentsApprovalFlag -> N remains an original FAIL with accepted retention, not a blank-create PASS or universal default. Explicit N was supplied for the two observed retained creates. It is not an inferred default. Keep requested input, observed output, original failure and later business retention distinct. Source seed code/label pairs establish neither field defaults nor automatic label serialization; preserve unrequested existing blanks. Sources: SRC-E2E-RETAINED-CREATE-55ROW-164877, SRC-DEV-LOOKUP-SEEDS-20260924, SRC-DEV-INTERNAL-PAYER-EO-LOOKUPS, SRC-DEV-INTERNAL-PAYER-EOIMPL-PPR.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DSO_PRESERVATION | decision | 40 | apply_default | preserved->DSO_DESIGN;missing->DSO_RETURN_MISSING;invalid->DSO_RETURN_FAILED | DSO_VALUE_EVIDENCE | stop | true |
