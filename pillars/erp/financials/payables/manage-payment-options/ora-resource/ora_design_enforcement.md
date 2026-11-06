# Design Enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_SYSTEM_PARAMETER::BuName, AP_SYSTEM_PARAMETER::EnterpriseId, AP_SYSTEM_PARAMETER::BankChargeBearer, AP_SYSTEM_PARAMETER::BankChargeDeductionTypeDes, AP_SYSTEM_PARAMETER::TermName -->
<!-- fscr-update-fields: AP_SYSTEM_PARAMETER::WhenToAccountPmt, AP_SYSTEM_PARAMETER::PostDatedPaymentsFlag, AP_SYSTEM_PARAMETER::AllowSupplierBankOverride, AP_SYSTEM_PARAMETER::PayDocCategoryOverride, AP_SYSTEM_PARAMETER::AllowPymtThirdPartyOvrd, AP_SYSTEM_PARAMETER::BankChargeBearer, AP_SYSTEM_PARAMETER::BankChargeDeductionTypeDes -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm source scope | Match the request to the exact task package and target business unit |
| 2 | Confirm field contract | Validate each supplied Payment Options field against its documented value rule. For updates, preserve omitted fields from the fresh exact-task baseline and require a field-specific governed override where updateability is unproven. For creates, reuse only the Invoice Options documented shared defaults and resolved reference values; do not invent other defaults. Require those defaults in the actual generated or uploaded CSV. |
| 3 | Govern execution | Use core.data-loader for immutable preview, separate approval, and any Fusion import |

## Design Rules

A blank Required Lookup leaves the local package, field-contract, baseline,
and approval checks in the rule fully enforced; no reference lookup is required.

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Always | Blocker | | Candidate package does not match AP_MANAGE_PAYMENT_OPTIONS and AP_SYSTEM_PARAMETER | Rebuild from the exact task template | Yes |
| Every supported Payment operation | Blocker | | The sibling adapter is unavailable, its package structure differs, or its validation rejects the resulting complete shared row | Stop before preview; correct the shared-row dependency or evidence drift | Yes |
| Any optional Payment field is edited | Blocker | | The supplied value fails its field contract, the target baseline is not verified, or the field has evidence-unresolved updateability without an exact governed application-validation override | Stop before preview; validate the requested field and bind any required override exactly to that field. Do not infer support or exclusion from a different field's evidence. | Yes |
| A Payment Options checkbox is edited | Blocker | | The submitted value is not Y or N, or the baseline row is unavailable for preservation | Correct the value and rebuild from a fresh exact-task baseline | Yes |
| Bank Charge Deduction Type or Escheatment days is edited | Blocker | | Bank Charge Deduction Type is not Standard, Negotiated, or None; or the days value is not a nonnegative integer | Serialize Bank Charge Deduction Type as `Standard`, `Negotiated`, or `None` in the CSV, rather than the database codes `S`, `N`, or `X`. | Yes |
| Any Fusion import is requested | Blocker | | Preview, approval, and execution are not routed through core.data-loader | Follow the central Data Loader workflow; task guidance never authorizes direct writes | Yes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PAYOPT.ENFORCE_DESIGN | step | 30 | design_enforcement | pass->PAYOPT.EXECUTION_GATE;blocked->PAYOPT.DESIGN_BLOCKED | PAYOPT.APPLY_DEFAULTS | stop | Always |

The task-node flow is **Input → Lookups → Dependencies → Defaults → Design → Execution gate**.
`PAYOPT.CHECK_DEPENDENCIES` leads to `PAYOPT.APPLY_DEFAULTS` before design checks.
Apply documented shared defaults only to generated creates; verify the required
values in uploaded create ZIPs without editing them, and preserve update values
without inferred defaults. Each node is defined once in its owning resource file;
the generated registry connects them.
