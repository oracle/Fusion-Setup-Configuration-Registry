# Lookup-type choices for this task

Reviewed 2026-10-31 for **EXM_MANAGE_AUDIT_LOOKUP_TYPES** only. No other FSM task,
lookup-type creation or configuration-level change is introduced by this workbook.

## Predefined auditing starter choices

These definitions were read from Oracle's shipped
`StandardLookupTypeSD.xml`
on the selected source branch. They were corroborated by read-only target
inventory; they are not derived by matching a code prefix.

| Lookup Type | Meaning | Configuration level |
|---|---|---|
| EXM_AUDIT_REASON | Expense Report Audit Reason | Extension |
| EXM_AUDIT_ISSUE | Audit Issue | System |
| EXM_AUDIT_ACTION_REASON | Audit Action Reason | System |
| EXM_AUDIT_LIST_AUTO_REASON | Automatic Addition to Audit List Reason Codes | Extension |
| EXM_AUDIT_LIST_MANUAL_REASON | Manual Addition to Audit List Reason Codes | Extension |
| EXM_AUD_END_DATE_ADJSTMT_RSN | Manual End Dating to Audit List Reason Codes | Extension |

All six seed definitions use ViewApplicationId 0. These are historical seed examples, not shipped dropdown choices. Customer
dropdowns are populated from the selected environment.
System versus Extension affects allowed edits: the observed System audit type
disabled Create and several code fields in the UI. Do not infer that a listed
type permits every workbook operation, or that UI restrictions prove identical
FSM service behavior. Retain destination checks and application validation.

## Why the full page is broader

- `SetupTaskSD.xml, lines 10211–10247`
  launches ManageGenericLookupTF with mode=search, moduleType=APPLICATION and
  moduleKey=EXM. It does not pass a literal auditing lookup-type list.
- `ManageGenericLookupTF.xml`
  passes module parameters into GenericSearchFlow, whose initializer is
  initGenericLookupModuleKey.
- `UI application module, lines 48–94`
  restricts types to the selected taxonomy module **and its descendants**.
  A direct ModuleId inventory covers that module, not necessarily all descendants.
- `SearchGenericLookups.jsff`
  binds the lookup-type search and conditional code-maintenance controls, including
  the reference-data-set choice and Enabled checkbox.
- The FSM export VO's customer-modified filter is not a complete list of seeded
  lookup types. An export-only dropdown would omit valid seeded choices.

Authoring evidence included an IntelliJ FUSION_READ_ONLY SELECT on the selected
nonproduction connection, a complete core-client REST inventory, and a read-only
clickthrough of this exact setup page. The direct-module REST inventory and SQL
aggregate each returned 261 type/set rows on that environment. They include
environment additions and non-auditing types, so those values are kept in the
ignored project workspace, not embedded in the shipped template.

## Public documentation and release qualification

Latest public Financials documentation located was 26D; no accessible 27A
equivalent was found. Oracle's [26D Expense Assistant setup](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/set-up-expense-assistant.html)
uses this same FSM page for merchant-name maintenance, and [26D mileage-location setup](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/use-oracle-maps-for-trip-distance-calculation.html)
uses it for preferred locations. These substantiate the shared page's broader
use; they do not replace the selected task scope or environment checks.
The internal export's 11.13.27.04.0 version is distinct from public release 26D.

Dropdowns improve entry; they are not preflight evidence. Current exact type,
module/descendant scope, view, reference set and full code population still need
verification. A reference-set dropdown alone does not resolve the missing SetId
in generic lookup-code REST responses.
