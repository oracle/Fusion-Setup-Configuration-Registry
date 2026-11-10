# Financials / Customers placement


This revision moves the previous Receivables-owned task and its owned noship
bundle into the existing catalog-backed Financials / Customers functional area.
The task code ORA_AR_MANAGE_CUSTOMER_UPLOADS, FBDI business object customers,
Fusion UCM account, SOAP namespaces and ESS definitions are unchanged.

- Old skill ID: `erp.financials.receivables.manage-customer-uploads`.
- New skill ID: `erp.financials.customers.manage-customer-uploads`.
- New task path: `pillars/erp/financials/customers/manage-customer-uploads`.
- New test path: `pillars/erp/financials/customers/noship/tests/manage-customer-uploads`.
- Parent: `erp.financials.customers`, catalog functional area `ORA_EGP_CUSTOMER`.

Use the new parent path for planner invocations. Resolve new task contexts through
normal planning; do not edit approved historical contexts or retrofit old previews.
New execution requires current validation and exact-candidate approval. Preserve
historical reports, source paths, hashes and Run Book evidence as recorded. Offline
historical evidence interpretation does not authorize resubmission or establish
qualification of a new candidate. Do not install an alias, central catalog entry
or planner override to keep the old source path executable.

The generated Customers parent links to this task. Existing Receivables and other
product skills remain unchanged. No customer import behavior changes merely from
this placement correction.
