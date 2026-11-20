# Manage Budgetary Control Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Technical import value | Exact value evidenced by the current same-task metadata or a supported read-only source | A required template field is not a business decision and the evidence identifies one value | No | resolve_fsm_template_contract |
| Entity scope | Scope evidenced as enterprise, ledger, or business-unit scoped by template metadata or release documentation | An option or entity label alone is ambiguous | No | resolve_fsm_template_contract |
| Create versus update | No create artifact for an exact existing match; update only for an approved, FSM-supported difference | Existing-object comparison completes | No | resolve_existing_budgetary_control_setup |
| ORA_XCC_ENABLED_JOURNAL_SOURCE.AllCategoryFlag | Y, representing all journal categories | A Journal Source is requested and the user supplies no specific journal categories | Yes; specific requested journal categories set AllCategoryFlag to N and require corresponding ORA_XCC_ENABLED_JOURNAL_CATEGORY rows | resolve_journal_category_scope |
| ORA_XCC_ENABLED_BUSINESS_FUNCTION.ReserveOnSubmitFlag | N, representing Approval | Budgetary Control is enabled for REQUISITIONING_BF or PROCUREMENT_BF and no Reservation Point is supplied or retained from the exact existing enabled row | No; preserve an explicit Approval / N or Submission / Y choice | resolve_business_function_bc_enablement_sequence |

## Default Evidence Rules

| Situation | What Happens |
|---|---|
| Evidence is incomplete, conflicting, or absent | Leave the value unresolved and stop before preview. |
| A UI label differs from a technical field | Serialize a label only when the current template or metadata proves it is accepted; otherwise resolve the technical value. |
| A business configuration choice is absent | Do not default it; classify it as a business decision. |
| Budget Segment is Use a specified value when not provided in budget data and the prompt omits Segment Value | Retain Segment Value only from the exact existing segment row when it is nonblank. If no nonblank existing value is available, leave it unresolved and stop before preview. |
| A Journal Source is supplied without specific journal categories | Set AllCategoryFlag to Y and do not generate ORA_XCC_ENABLED_JOURNAL_CATEGORY rows for that source. |
| One or more specific journal categories are supplied for a Journal Source | Set AllCategoryFlag to N and generate only the validated requested ORA_XCC_ENABLED_JOURNAL_CATEGORY rows after the parent source. |
| REQUISITIONING_BF Budgetary Control changes from N to Y | Set BcEnabledFlag Y for REQUISITIONING_BF, PROCUREMENT_BF, EXPENSE_MANAGEMENT_BF, RECEIVING_BF, and PAYABLES_INVOICING_BF for the same ledger and business unit. For enabled Requisitioning and Procurement, preserve an explicit Approval / N or Submission / Y choice; retain the value of an existing enabled row when unspecified, otherwise default to Approval / N. |
| PROCUREMENT_BF Budgetary Control changes from N to Y | Set BcEnabledFlag Y for PROCUREMENT_BF, RECEIVING_BF, and PAYABLES_INVOICING_BF for the same ledger and business unit, regardless of the Requisitioning state. For Expense Management, use an explicit user request to enable or disable it first; otherwise retain the current same-business-unit BcEnabledFlag Y or N from the fresh export. Default EXPENSE_MANAGEMENT_BF to Y only when neither an explicit user choice nor an existing Y or N value is available. Never overwrite an explicit choice or existing value with the Procurement default. Preserve an explicit Approval / N or Submission / Y choice for Procurement; retain the value of an existing enabled row when unspecified, otherwise default to Approval / N. |
| Reservation Point is requested for a disabled or unsupported business function | Do not apply a Reservation Point default or infer Budgetary Control enablement. Return the Reservation Point validation error. An unchanged template/export placeholder is not a requested Reservation Point setting. |
| Business-function Encumbrance Accounting prerequisite is unmet | Do not default or cascade EaEnabledFlag on the parent business unit or Requisitioning. Return the prerequisite validation error; coordinated prerequisite changes must be explicitly requested. |
| EXPENSE_MANAGEMENT_BF, RECEIVING_BF, PAYABLES_INVOICING_BF, or PROJECT_ACCOUNTING_BF changes | Apply only the explicitly requested independent enablement or disablement unless that row is also required by a Requisitioning or Procurement enablement cascade. |
| Any input, metadata, target, or default changes | Invalidate the preview and import approval; derive again from current evidence. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MBC.DEFAULT | step | 4 | apply_default | ready->MBC.DESIGN;blocked->MBC.RETURN_ISSUES | MBC.LOOKUP | stop | After required technical values resolve |
