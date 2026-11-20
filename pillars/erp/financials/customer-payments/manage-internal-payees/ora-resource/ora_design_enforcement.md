# Design enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: ORA_IBY_FC_DEFAULT_ROUTE::Instrtype, ORA_IBY_FC_DEFAULT_ROUTE::PaymentChannelCode, ORA_IBY_FC_DEFAULT_ROUTE::FndcptUserProfileCode, ORA_IBY_FC_DEFAULT_ROUTE::FndcptUserProfileName, ORA_IBY_FC_DEFAULT_ROUTE::Key1, ORA_IBY_FC_DEFAULT_ROUTE::Suffix, ORA_IBY_FC_INT_PAYEE_MAP::OrgType, ORA_IBY_FC_INT_PAYEE_MAP::BuName, ORA_IBY_FC_ROUTING_CONDITION::ParameterCode, ORA_IBY_FC_ROUTING_CONDITION::OperationCode, ORA_IBY_FC_ROUTING_CONDITION::Value, ORA_IBY_FC_ROUTING_CONDITION::EntrySequence, ORA_IBY_FC_ROUTING_CONDITION::PayerBankRoutingNumDisp, IBY_INTERNAL_PAYEE::Payeeid, IBY_INTERNAL_PAYEE::Name, IBY_INTERNAL_PAYEE::Ecappid, IBY_INTERNAL_PAYEE::Username, IBY_INTERNAL_PAYEE::Password, IBY_INTERNAL_PAYEE::Activestatus, IBY_INTERNAL_PAYEE::Supportedop, IBY_INTERNAL_PAYEE::Logo, IBY_INTERNAL_PAYEE::Threshold, IBY_INTERNAL_PAYEE::RiskEnabled, IBY_INTERNAL_PAYEE::MccCode, IBY_INTERNAL_PAYEE::DbaName, IBY_INTERNAL_PAYEE::DbaCity, IBY_INTERNAL_PAYEE::DbaStateProvince, IBY_INTERNAL_PAYEE::DbaCountry, IBY_INTERNAL_PAYEE::InactiveDate, IBY_INTERNAL_PAYEE::StartDate, IBY_INTERNAL_PAYEE::EndDate, IBY_INTERNAL_PAYEE::PayerNotifSendFrom, IBY_INTERNAL_PAYEE::PayerNotifEmailSubject, IBY_INTERNAL_PAYEE::EndDateDsp, ORA_IBY_FC_ACCNT_PAYMENT::Ecappid, ORA_IBY_FC_ACCNT_PAYMENT::Payeeid, ORA_IBY_FC_ACCNT_PAYMENT::Status, ORA_IBY_FC_ACCNT_PAYMENT::Accttype, ORA_IBY_FC_ACCNT_PAYMENT::Instrtype, IBY_FC_ROUTING_RULE::Payeeid, IBY_FC_ROUTING_RULE::Configured, IBY_FC_ROUTING_RULE::Priority, IBY_FC_ROUTING_RULE::Paymentmethodname, IBY_FC_ROUTING_RULE::InstrType, IBY_FC_ROUTING_RULE::InstrSubType, IBY_FC_ROUTING_RULE::Bepkey, IBY_FC_ROUTING_RULE::InactiveDate, IBY_FC_ROUTING_RULE::FndcptUserProfileCode, IBY_FC_ROUTING_RULE::FndcptUserProfileName, IBY_FC_ROUTING_RULE::PaymentChannelCode, IBY_FC_ROUTING_RULE::StartDate, IBY_FC_ROUTING_RULE::EndDate, IBY_FC_ROUTING_RULE::Suffix, IBY_FC_ROUTING_RULE::Key1, IBY_FC_ROUTING_RULE::EndDateDsp, IBY_FC_ROUTING_RULE::TokenizationRoutingFlag, IBY_FC_ROUTING_RULE::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_ACCNT_PAYMENT::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_DEFAULT_ROUTE::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_INT_PAYEE_MAP::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_ROUTING_CONDITION::IBY_INTERNAL_PAYEE.Payeeid, ORA_IBY_FC_ROUTING_CONDITION::IBY_FC_ROUTING_RULE.Paymentmethodname -->
<!-- fscr-update-fields: ORA_IBY_FC_DEFAULT_ROUTE::Instrtype, ORA_IBY_FC_DEFAULT_ROUTE::FndcptUserProfileCode, ORA_IBY_FC_DEFAULT_ROUTE::FndcptUserProfileName, ORA_IBY_FC_DEFAULT_ROUTE::Key1, ORA_IBY_FC_DEFAULT_ROUTE::Suffix, ORA_IBY_FC_ROUTING_CONDITION::ParameterCode, ORA_IBY_FC_ROUTING_CONDITION::OperationCode, ORA_IBY_FC_ROUTING_CONDITION::Value, ORA_IBY_FC_ROUTING_CONDITION::PayerBankRoutingNumDisp, IBY_INTERNAL_PAYEE::Name, IBY_INTERNAL_PAYEE::Ecappid, IBY_INTERNAL_PAYEE::Username, IBY_INTERNAL_PAYEE::Password, IBY_INTERNAL_PAYEE::Activestatus, IBY_INTERNAL_PAYEE::Supportedop, IBY_INTERNAL_PAYEE::Logo, IBY_INTERNAL_PAYEE::Threshold, IBY_INTERNAL_PAYEE::RiskEnabled, IBY_INTERNAL_PAYEE::MccCode, IBY_INTERNAL_PAYEE::DbaName, IBY_INTERNAL_PAYEE::DbaCity, IBY_INTERNAL_PAYEE::DbaStateProvince, IBY_INTERNAL_PAYEE::DbaCountry, IBY_INTERNAL_PAYEE::InactiveDate, IBY_INTERNAL_PAYEE::StartDate, IBY_INTERNAL_PAYEE::EndDate, IBY_INTERNAL_PAYEE::PayerNotifSendFrom, IBY_INTERNAL_PAYEE::PayerNotifEmailSubject, IBY_INTERNAL_PAYEE::EndDateDsp, ORA_IBY_FC_ACCNT_PAYMENT::Ecappid, ORA_IBY_FC_ACCNT_PAYMENT::Status, IBY_FC_ROUTING_RULE::Configured, IBY_FC_ROUTING_RULE::Priority, IBY_FC_ROUTING_RULE::InstrType, IBY_FC_ROUTING_RULE::InstrSubType, IBY_FC_ROUTING_RULE::Bepkey, IBY_FC_ROUTING_RULE::InactiveDate, IBY_FC_ROUTING_RULE::FndcptUserProfileCode, IBY_FC_ROUTING_RULE::FndcptUserProfileName, IBY_FC_ROUTING_RULE::PaymentChannelCode, IBY_FC_ROUTING_RULE::StartDate, IBY_FC_ROUTING_RULE::EndDate, IBY_FC_ROUTING_RULE::Suffix, IBY_FC_ROUTING_RULE::Key1, IBY_FC_ROUTING_RULE::EndDateDsp, IBY_FC_ROUTING_RULE::TokenizationRoutingFlag -->

Apply these task operating policies to the affected request only. Partial evidence never removes independently supported create/update behavior.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Identity and preservation | Confirm precise operation and scope |
| 2 | Business rules | Apply only relevant policy and known validations |
| 3 | Handoff | Return reviewable results to Run Book/Data Loader; they own preview, approval and writes |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Update existing payee or child | Block |  | Sparse payload or changed immutable identity | Overlay explicit changes on the complete fresh baseline; preserve unrelated records and values | Only with reviewed business intent |
| Payee effective end date | Block |  | Conflicting EndDate/EndDateDsp or treating null alias as unchanged | Keep the canonical end date and its display alias consistent with the approved date; a null alias resets the open-ended sentinel | Only with reviewed date intent |
| Date-based UI inactivation | Verify |  | Treating Activestatus=N as proof of UI Inactive | Use approved effective dates and verify the calculated UI result against database-date semantics; retain stored-flag evidence separately | No inferred effective date |
| Condition with omitted display input | Verify |  | Requiring blank PayerBankRoutingNumDisp although the display output returns current Value | Reconcile the derived display fallback against current Value, including AMOUNT; preserve explicit display input and ABA write semantics | No independent display default or business choice |
| Payment account is unowned | Block |  | Related ownership effect absent from preview | Include import assignment of Ownerid/Ownertype and its verification in preview and reconciliation | No silent side effect |
| Routing rule with PROCESSOR | Block |  | Missing required funds-capture process profile | Supply eligible profile; the PROCESSOR requirement differs from GATEWAY | User correction |
| Routing rule | Block |  | No condition or duplicate rule name within payee | Provide at least one valid condition; preserve matching identity | User correction |
| Unknown conditional reference contract | Block affected reference only |  | Attempt to invent a raw identifier or infer membership from display text | Resolve exact reference using a qualified contract; preserve unchanged baseline references | No invented identity |
| Accepted payment method disabled | Verify |  | Assuming generic FSM status change runs UI cleanup | Disabling through the UI can remove a default route; FSM status import does not imply that cleanup. Preview intended related records explicitly | No assumed cascade |
| Credential unchanged | Block |  | Masked or normalized text replaces opaque baseline | Preserve exact opaque value under governed handling; reviewed direct assignment is not an encryption or authentication claim | No silent substitution |
| Physical delete requested | Unresolved |  | No established deletion mechanism | Keep operation evidence unresolved; do not equate end-date/inactivation with delete | No unsupported delete claim |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IP.DESIGN | step | 50 | design_enforcement | pass->IP.GATE;fail->IP.ERROR | IP.DEFAULTS | stop | Selected Manage Internal Payees request; evaluate only applicable source rows |


## Business-unit ownership across payees

A business unit can be assigned to only one payee for the same OrgType. Resolve exact BuName to OrgId, inspect the fresh complete same-environment mapping population across all payees, and reject creation when that pair belongs to another payee. A different parent payee does not permit reuse of the same assignment. Preserve existing mappings; no implicit reassignment or delete.
