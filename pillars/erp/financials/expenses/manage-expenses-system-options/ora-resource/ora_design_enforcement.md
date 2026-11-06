# Manage Expenses System Options Design Enforcement

The confirmed FSM option create/update package contract verifies an exact data
transformation, not the business outcome of enabling an option. The selected
option is still subject to its Oracle setup guidance and to the owning
dependency tasks. This file is documentation-only: it contributes no runtime
Task Node and does not require an undeclared Fusion lookup.

## Sources

- [Enable Splitting Expenses](https://docs.oracle.com/en/cloud/saas/financials/25c/faiex/enable-splitting-expenses.html)
- [Enable reimbursement currency selection](https://docs.oracle.com/en/cloud/saas/financials/25d/faiex/how-can-i-enable-users-to-select-reimbursement-currencies-for.html)
- [Enable payment-method selection](https://docs.oracle.com/en/cloud/saas/financials/25c/faiex/how-can-i-enable-users-to-select-payment-methods-in-expense.html)

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| A supported option value is edited | Informational | | The value is outside the confirmed package contract | Use a task-supported confirmed option edit or obtain source evidence before preparing an import | No |
| Enable Split Allocations is enabled | Informational | | Users lack privileges or valid account or project targets when using the feature | Complete the applicable security and master-data setup before expecting users to split expenses | No |
| Allow Reimbursement Currency Selection is enabled | Informational | | The requested allowed-currency list is not supported by the confirmed create/update contract | Configure the option through this contract only; obtain a separate supported path for the currency list | No |
