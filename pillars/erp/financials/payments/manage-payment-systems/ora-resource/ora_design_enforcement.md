# MPS design enforcement



<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_PAYMENT_SYSTEM::Name, IBY_PAYMENT_SYSTEM::Baseurl, IBY_PAYMENT_SYSTEM::Suffix, IBY_PAYMENT_SYSTEM::BepType, IBY_PAYMENT_SYSTEM::OutboundInvalidChars, IBY_PAYMENT_SYSTEM::OutboundReplaceChars, IBY_PAYMENT_SYSTEM::NlsLanguage, IBY_PAYMENT_SYSTEM::StartDate, IBY_PAYMENT_SYSTEM::EndDate, IBY_PAYMENT_SYSTEM::B2BTradingPartnerName, IBY_PAYMENT_SYSTEM::CreditCardFlag, IBY_PAYMENT_SYSTEM::DebitCardFlag, IBY_PAYMENT_SYSTEM::FCBankTransferFlag, IBY_PAYMENT_SYSTEM::FDBankTransferFlag, IBY_PAYMENT_SYSTEM::BankName, IBY_PAYMENT_SYSTEM::HomeCountry, ORA_IBY_PAYMENT_SYSTEM_SCHEME::Pmtschemename, ORA_IBY_PAYMENT_SYSTEM_TRAN::TransmitProtocolCode, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::AccountOptionCode, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::AccountOptionValue, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::BuName, ORA_IBY_PAYMENT_SYSTEM_FORMAT::PaymentFormatCode, ORA_IBY_PAYMENT_SYSTEM_FORMAT::StartDate, ORA_IBY_PAYMENT_SYSTEM_FORMAT::EndDate, ORA_IBY_PAYMENT_SYSTEM_KEY::Ownertype, ORA_IBY_PAYMENT_SYSTEM_KEY::Key1, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::AccountOptionCode, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::AccountOptionDatatype, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::SecuredFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::UniquePerBatchFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::DisplayOrder, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::TokenProfileFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::AccountOptionName, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::AccountOptionCode, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::Language, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::SourceLang, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::AccountOptionName, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_FORMAT::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_KEY::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_SCHEME::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_TRAN::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::ORA_IBY_PAYMENT_SYSTEM_KEY.Key1, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::IBY_PAYMENT_SYSTEM.Suffix, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::ORA_IBY_PAYMENT_SYSTEM_ACC_NAME.AccountOptionCode -->
<!-- fscr-update-fields: IBY_PAYMENT_SYSTEM::Name, IBY_PAYMENT_SYSTEM::Baseurl, IBY_PAYMENT_SYSTEM::BepType, IBY_PAYMENT_SYSTEM::OutboundInvalidChars, IBY_PAYMENT_SYSTEM::OutboundReplaceChars, IBY_PAYMENT_SYSTEM::NlsLanguage, IBY_PAYMENT_SYSTEM::StartDate, IBY_PAYMENT_SYSTEM::EndDate, IBY_PAYMENT_SYSTEM::B2BTradingPartnerName, IBY_PAYMENT_SYSTEM::CreditCardFlag, IBY_PAYMENT_SYSTEM::DebitCardFlag, IBY_PAYMENT_SYSTEM::FCBankTransferFlag, IBY_PAYMENT_SYSTEM::FDBankTransferFlag, IBY_PAYMENT_SYSTEM::BankName, IBY_PAYMENT_SYSTEM::HomeCountry, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::AccountOptionValue, ORA_IBY_PAYMENT_SYSTEM_ACC_VAL::BuName, ORA_IBY_PAYMENT_SYSTEM_FORMAT::StartDate, ORA_IBY_PAYMENT_SYSTEM_FORMAT::EndDate, ORA_IBY_PAYMENT_SYSTEM_KEY::Ownertype, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::SecuredFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::UniquePerBatchFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::DisplayOrder, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::TokenProfileFlag, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME::AccountOptionName, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::SourceLang, ORA_IBY_PAYMENT_SYSTEM_ACC_NAME_TRANSLATION::AccountOptionName -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Classify sensitive data | Apply versioned sensitive-policy.json before logs, previews or package construction |
| 2 | Apply field boundaries | Validate independent create/update disposition and same-row preservation |
| 3 | Respect lifecycle | No implicit removal, key renaming or unrelated row replay |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Sensitive or unknown account option | Block |  | SecuredFlag Y, known sensitive semantics, topology-managed option, or unclassified value | Omit the whole value row; record manual UI completion. Never replace with blank, mask or changeit. | No automatic fix |
| Root dependency serialization | Block |  | Any nonempty or uncertain Bepusername, Beppassword, Psusername or Pspassword | Exclude the entire affected serialized root subtree and complete its change in UI. Never copy or blank credentials. | No |
| Existing row update | Block |  | Unchanged serialized fields cannot be safely preserved from a matching sanitized baseline | Preserve reviewed ordinary values only; absence of a field is not evidence of a blank. Stop the affected operation if preservation is uncertain. | No |
| Unresolved field mutation | Block |  | Requested field disposition is unresolved without the exact governed update override | Preserve the evidence gap. Resolve the contract or use the current Builder/Data Loader application-validation override with exact field and operation binding, explicit implementor approval and single-submission controls. Concrete unsupported, sensitive and lifecycle restrictions cannot be overridden. Create remains source-backed only. | Governed update only |
| DFF changes | Block |  | Unverified context or segment contract without an eligible governed update override | Prefer target DFF definition qualification. Eligible evidence-unresolved updates retain the exact governed application-validation controls; never relabel unresolved fields as supported. | Governed update only |
| Instrument flags and schemes | Block |  | Contradictory independent edits or unintended scheme removal | Reconcile Y create/keep and N removal behavior; null has no action. Require explicit intended effect. | No |
| Citi character substitution | Block |  | OutboundInvalidChars/OutboundReplaceChars requested outside Citi-Payables or positional pairing inconsistent | Confirm applicability and aligned substitution lists. | No |
| Encryption interpretation | Block |  | SecuredFlag alone or masked/blank value used as encryption/preservation proof | A positive VAL_SEC_SEGMENT_ID identifies segment-backed storage; null can mean plaintext. Neither permits secret replay. | No |
| Unsupported lifecycle | Block |  | Physical deletion, account key renaming, MAX_BATCH_SIZE automation or DATE option conversion without exact format | Explain the boundary and use manual supported UI completion. | No |
| Policy revision | Block |  | Policy version/hash changed after preparation | Discard candidate approval and revalidate through the active Data Loader session. | No |


Source: SRC-MPS-POLICY; SRC-MPS-ADE-001/005/007/008/009/011; SRC-MPS-FW-CSV/READER; SRC-MPS-EDM-IBY-BEPINFO. Complete child-row omission is the preservation design; target runtime qualification remains required. Do not claim a blank password clears successfully: mandatory validation may reject before DML.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPS.POLICY | step | 10 | design_enforcement | pass->MPS.INPUT;fail->MPS.RETURN_ISSUES | none | stop | always |
