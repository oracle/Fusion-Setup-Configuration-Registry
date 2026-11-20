# ASL Status Design Enforcement

Submitted values and caller context are the local authority, as specified in the
approved plan. Policy checks below are FSCR safeguards, while flag meanings come
from Oracle's [26D REST contract](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingapprovedsupplierliststatuses-statusid-patch.html).
No node inspects existing Fusion records or infers business policy from names such
as Review, Approved, or New.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Use validated input | Rely on [input validation](ora_input_validation.md) and [preservation rules](ora_defaulting_rules.md); do not repeat their checks |
| 2 | Apply business policy | Check clearing authorization and scope against the current request |
| 3 | Explain effects | Return applicable business recommendations; do not invent blockers based on unknown server state |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Blank InactiveDate on update | Error | | Explicit clearing intent does not cover the current rows and batch | Ask once whether the affected rows should keep or clear their dates; explicit prior instructions for those rows in this batch count. A blank alone is not authorization. Keep instructions follow source preparation rules. | No |
| Any date-clearing instruction | Error | | Target rows or scope are unclear, or consent has been carried from another row/batch | Clarify the targets before preparation. Apply an entire-batch instruction only when explicitly stated; retain the instruction and row references outside business data. | No |
| AslDefaultFlag supplied true | Recommendation | | None; this is not a server-state assertion or an extra approval gate | Review whether this status is appropriate for newly created ASL entries because the flag makes it their default. Do not automatically unset another status or claim uniqueness. | No |
| Approval or sourcing flags supplied | Recommendation | | None | Review each flag independently: true permits its named activity, false prevents it. Do not infer either flag from the status name or force both to match. | No |
| InactiveDate supplied | Recommendation | | None | Review the intended retirement date because it controls status inactivation; clearing removes that planned inactivation. Confirm that the requested effect fits the intended use of the status. | No |

Clearing consent does not establish a supported wire representation. Apply
[error handling and handoff gates](ora_error_handling.md#representation-and-handoff-gates)
after these policies, including when a nullable business value is valid.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASL.CHECK_DESIGN | decision | 30 | design_enforcement | valid->ASL.HANDOFF;blocked->ASL.HANDLE_ISSUES | ASL.PRESERVE_VALUES | stop | Enforce local policies and return applicable recommendations without live lookups or new approval gates |
