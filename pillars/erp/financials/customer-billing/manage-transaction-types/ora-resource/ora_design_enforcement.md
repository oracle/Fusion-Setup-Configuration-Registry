# Manage Transaction Types Design Enforcement


<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AR_REF_ACCT_TRX_TYPE::AR_TRANSACTION_TYPE.Name, AR_REF_ACCT_TRX_TYPE::AR_TRANSACTION_TYPE.SetCode, AR_REF_ACCT_TRX_TYPE::BrFactorSegments, AR_REF_ACCT_TRX_TYPE::BrRemitSegments, AR_REF_ACCT_TRX_TYPE::BrUnpaidSegments, AR_REF_ACCT_TRX_TYPE::BuName, AR_REF_ACCT_TRX_TYPE::ClearingSegments, AR_REF_ACCT_TRX_TYPE::DepositOffsetSegments, AR_REF_ACCT_TRX_TYPE::DistSetSegments, AR_REF_ACCT_TRX_TYPE::DrcSegments, AR_REF_ACCT_TRX_TYPE::FreightSegments, AR_REF_ACCT_TRX_TYPE::LedgerName, AR_REF_ACCT_TRX_TYPE::Name, AR_REF_ACCT_TRX_TYPE::RecSegments, AR_REF_ACCT_TRX_TYPE::RevSegments, AR_REF_ACCT_TRX_TYPE::SourceRefTable, AR_REF_ACCT_TRX_TYPE::TaxSegments, AR_REF_ACCT_TRX_TYPE::UnbilledSegments, AR_REF_ACCT_TRX_TYPE::UnearnedSegments, AR_TRANSACTION_TYPE::AccountingAffectFlag, AR_TRANSACTION_TYPE::AdjPostToGlFlag, AR_TRANSACTION_TYPE::AllocateTaxFreight, AR_TRANSACTION_TYPE::AllowFreightFlag, AR_TRANSACTION_TYPE::AllowFutureAcctDateFlag, AR_TRANSACTION_TYPE::AllowOverapplicationFlag, AR_TRANSACTION_TYPE::Attribute1, AR_TRANSACTION_TYPE::Attribute10, AR_TRANSACTION_TYPE::Attribute11, AR_TRANSACTION_TYPE::Attribute12, AR_TRANSACTION_TYPE::Attribute13, AR_TRANSACTION_TYPE::Attribute14, AR_TRANSACTION_TYPE::Attribute15, AR_TRANSACTION_TYPE::Attribute2, AR_TRANSACTION_TYPE::Attribute3, AR_TRANSACTION_TYPE::Attribute4, AR_TRANSACTION_TYPE::Attribute5, AR_TRANSACTION_TYPE::Attribute6, AR_TRANSACTION_TYPE::Attribute7, AR_TRANSACTION_TYPE::Attribute8, AR_TRANSACTION_TYPE::Attribute9, AR_TRANSACTION_TYPE::AttributeCategory, AR_TRANSACTION_TYPE::ControlCompletion, AR_TRANSACTION_TYPE::CreationSign, AR_TRANSACTION_TYPE::CreditMemoTypeName, AR_TRANSACTION_TYPE::CreditMemoTypeSetCode, AR_TRANSACTION_TYPE::DefaultPrintingOption, AR_TRANSACTION_TYPE::DefaultStatus, AR_TRANSACTION_TYPE::DefaultTermName, AR_TRANSACTION_TYPE::DefaultTermSetCode, AR_TRANSACTION_TYPE::Description, AR_TRANSACTION_TYPE::DraweeIssuedFlag, AR_TRANSACTION_TYPE::EndDate, AR_TRANSACTION_TYPE::ExcludeFromLateCharges, AR_TRANSACTION_TYPE::GlobalAttribute1, AR_TRANSACTION_TYPE::GlobalAttribute10, AR_TRANSACTION_TYPE::GlobalAttribute11, AR_TRANSACTION_TYPE::GlobalAttribute12, AR_TRANSACTION_TYPE::GlobalAttribute13, AR_TRANSACTION_TYPE::GlobalAttribute14, AR_TRANSACTION_TYPE::GlobalAttribute15, AR_TRANSACTION_TYPE::GlobalAttribute16, AR_TRANSACTION_TYPE::GlobalAttribute17, AR_TRANSACTION_TYPE::GlobalAttribute18, AR_TRANSACTION_TYPE::GlobalAttribute19, AR_TRANSACTION_TYPE::GlobalAttribute2, AR_TRANSACTION_TYPE::GlobalAttribute20, AR_TRANSACTION_TYPE::GlobalAttribute3, AR_TRANSACTION_TYPE::GlobalAttribute4, AR_TRANSACTION_TYPE::GlobalAttribute5, AR_TRANSACTION_TYPE::GlobalAttribute6, AR_TRANSACTION_TYPE::GlobalAttribute7, AR_TRANSACTION_TYPE::GlobalAttribute8, AR_TRANSACTION_TYPE::GlobalAttribute9, AR_TRANSACTION_TYPE::GlobalAttributeCategory, AR_TRANSACTION_TYPE::GlobalAttributeDate1, AR_TRANSACTION_TYPE::GlobalAttributeDate2, AR_TRANSACTION_TYPE::GlobalAttributeDate3, AR_TRANSACTION_TYPE::GlobalAttributeDate4, AR_TRANSACTION_TYPE::GlobalAttributeDate5, AR_TRANSACTION_TYPE::GlobalAttributeNumber1, AR_TRANSACTION_TYPE::GlobalAttributeNumber2, AR_TRANSACTION_TYPE::GlobalAttributeNumber3, AR_TRANSACTION_TYPE::GlobalAttributeNumber4, AR_TRANSACTION_TYPE::GlobalAttributeNumber5, AR_TRANSACTION_TYPE::LegalEntityIdentifier, AR_TRANSACTION_TYPE::Name, AR_TRANSACTION_TYPE::NaturalApplicationOnlyFlag, AR_TRANSACTION_TYPE::PostToGl, AR_TRANSACTION_TYPE::RuleSetName, AR_TRANSACTION_TYPE::SetCode, AR_TRANSACTION_TYPE::SignedFlag, AR_TRANSACTION_TYPE::StartDate, AR_TRANSACTION_TYPE::Status, AR_TRANSACTION_TYPE::SubsequentTrxTypeName, AR_TRANSACTION_TYPE::SubsequentTrxTypeSetCode, AR_TRANSACTION_TYPE::TaxCalculationFlag, AR_TRANSACTION_TYPE::TrxSubclassCode, AR_TRANSACTION_TYPE::Type, AR_TRANSACTION_TYPE::UsageCategoryCode -->
<!-- fscr-update-fields: AR_TRANSACTION_TYPE::Description, AR_TRANSACTION_TYPE::EndDate, AR_TRANSACTION_TYPE::Status -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Identity and operation | Require an exact SetCode-plus-Name target and source-evidenced create or update intent |
| 2 | Field-domain safety | Validate fixed domains, Boolean constraints, dates, and DFF context |
| 3 | Relationship safety | Bind each child to one parent and exact business-unit/ledger context |
| 4 | Resolver boundary | Block Partial environment choices and programmatic account combinations |
| 5 | Governed handoff | Send only the immutable validated FSM ZIP to core.data-loader |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? | Evidence |
|---|---|---|---|---|---|---|
| Every requested parent create or update | Error |  | SetCode or Name is blank; create targets an existing identity; or update does not resolve exactly one existing identity | Use a unique identity for create or the exact existing SetCode-plus-Name identity for update | Yes before preview | SRC-CODE-BO-META, SRC-HELP-TRXTYPE-26C, SRC-CODE-AM-IMPL, SRC-CODE-PRIMARY-VO, SRC-CODE-PRIMARY-EO |
| NaturalApplicationOnlyFlag and AllowOverapplicationFlag are both Y | Error |  | Both flags are enabled | Correct at least one flag before package generation | Yes before preview | SRC-BO-TRXTYPE-26C, SRC-CODE-PRIMARY-EO |
| EndDate is present | Error |  | EndDate is earlier than StartDate or either date is malformed | Correct the ISO date values | Yes before preview | SRC-BO-TRXTYPE-26C, SRC-CODE-PRIMARY-EO |
| A DFF segment is supplied | Error |  | Matching context is absent or datatype does not match the task metadata | Supply the exact supported context and datatype or omit the segment | Yes before preview | SRC-CODE-PRIMARY-VO, SRC-CODE-PRIMARY-EO, SRC-EDM-RA-CUST-26B |
| A reference-account child row is emitted | Error |  | Parent SetCode and Name, BuName, LedgerName, or SourceRefTable constant is absent or inconsistent | Rebuild the child from the exact parent and accounting context | Yes before preview | SRC-FSM-PACKAGE, SRC-CODE-AM-DEF, SRC-CODE-REF-VO |
| CreationSign is requested with a value other than `P` / `Positive Sign` | Error | verify_creation_sign | Only `P` / `Positive Sign` is verified safe; the full SIGN domain remains Partial | Use `P` or `Positive Sign`, omit the optional field, or provide direct evidence for another value | No automatic inference | SRC-CODE-CREATE-VO, SRC-BO-TRXTYPE-26C, SRC-E2E-MTT-CREATE-IMPORT-VALUES-20260905, SRC-E2E-MTT-CREATE-RECONCILIATION-20260905 |
| DefaultStatus is requested with a value other than `OP` / `Open` | Error | verify_default_status | Only `OP` / `Open` is verified safe; the full INVOICE_TRX_STATUS domain remains Partial | Use `OP` or `Open`, omit the optional field, or provide direct evidence for another value | No automatic inference | SRC-CODE-CREATE-VO, SRC-BO-TRXTYPE-26C, SRC-E2E-MTT-CREATE-IMPORT-VALUES-20260905, SRC-E2E-MTT-CREATE-RECONCILIATION-20260905 |
| UsageCategoryCode is requested | Error | verify_usage_category | Exact current-environment ORA_AR_USAGE_CATEGORY code is not verified | Verify the exact code at the governed task-validation step or omit this optional field | No automatic fix | SRC-CODE-CREATE-VO, SRC-BO-TRXTYPE-26C |
| TrxSubclassCode is requested | Error | verify_transaction_subclass | Exact current-environment ORA_AR_TRX_SUB_CLASS code is not verified | Verify the exact code at the governed task-validation step or omit this optional field | No automatic fix | SRC-CODE-CREATE-VO, SRC-BO-TRXTYPE-26C |
| Any account-segment field is requested | Error | verify_account_combination | Exact ledger chart structure and ordered segment value are not approved for nonproduction validation | Stop before candidate handoff; never invent or normalize segments | No automatic fix | SRC-CODE-AM-IMPL, SRC-CODE-GL-BULK, SRC-CODE-ARPT-VALIDATE |
| An update requests a field other than Description, Status, or EndDate | Error |  | The field has no operation-specific supported update contract | Keep the field blocked as evidence-unresolved; do not infer updateability from CSV presence or task-level update support | No | SRC-CODE-AM-IMPL, SRC-CODE-PRIMARY-VO, SRC-CODE-PRIMARY-EO, SRC-E2E-MTT-DESCRIPTION-UPDATE-20260905, SRC-E2E-MTT-DESCRIPTION-ROLLBACK-20260905 |
| Any operation other than create or update is requested | Error |  | Physical delete or another unsupported operation is requested | Keep the request blocked; explicit Description, Status, or EndDate changes are updates, and Status/EndDate retirement is not physical delete | No | SRC-HELP-TRXTYPE-26C, SRC-CODE-CREATE-VO, SRC-CODE-AM-IMPL, SRC-CODE-PRIMARY-VO, SRC-CODE-PRIMARY-EO |
| A Fusion mutation is requested | Error |  | Required core.data-loader/Task Hook validation or approval is absent | Complete the governing Data Loader validation and approval workflow; any changed candidate invalidates approval | No | Current repository contracts |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| verify_creation_sign | CreationSign is requested | `P` / `Positive Sign`; direct evidence is required before any other SIGN value is allowed | ora_reference_lookups.md |
| verify_default_status | DefaultStatus is requested | `OP` / `Open`; direct evidence is required before any other INVOICE_TRX_STATUS value is allowed | ora_reference_lookups.md |
| verify_usage_category | UsageCategoryCode is requested | Exact environment-supported ORA_AR_USAGE_CATEGORY code | ora_reference_lookups.md |
| verify_transaction_subclass | TrxSubclassCode is requested | Exact environment-supported ORA_AR_TRX_SUB_CLASS code | ora_reference_lookups.md |
| verify_account_combination | Any account-segment field is requested | Exact ledger, chart, and ordered segment combination | ora_reference_lookups.md |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTT.ENFORCE_DESIGN | decision | 40 | design_enforcement | compliant->MTT.GATE_DATALOADER;blocked->RETURN_ISSUES | MTT.APPLY_DEFAULTS | stop | Source-backed defaults are applied or not needed |

<!-- E2E-DISCOVERY:DISC-MTT-TYPED-DATE-CANON-20260909 -->
## Metadata-declared calendar-date persisted-format canonicalization

For every package field whose exact `ASM_SETUP_CSV_METADATA.xml` type is `date`, reconciliation may accept strict requested/candidate `YYYY-MM-DD` and strict persisted `YYYY/MM/DD` only when both parse to the identical Gregorian calendar date. Controlled Fusion 11.13.26.10.0 evidence confirms this behavior for `AR_TRANSACTION_TYPE.StartDate` (`SRC-E2E-MTT-STARTDATE-CANON-20260905`) and `AR_TRANSACTION_TYPE.EndDate` (`SRC-E2E-MTT-ENDDATE-CANON-20260909`). The report must retain requested, candidate, and persisted raw values, canonical ISO date, declared type, generic rule ID, and metadata-contract evidence. This is type-driven, not a field-name heuristic: date-time/timestamp fields, strings whose names merely contain `Date`, blanks, malformed or locale-ambiguous values, unequal dates, and candidate drift remain mismatches.

<!-- E2E-DISCOVERY:DISC-MTT-VERIFIED-VALUE-SUBSET-20260905 -->
## Field-scoped verified-value boundary

For `AR_TRANSACTION_TYPE.CreationSign`, permit only exact code `P` or business label `Positive Sign`, normalized to `P`. For `AR_TRANSACTION_TYPE.DefaultStatus`, permit only exact code `OP` or business label `Open`, normalized to `OP`. Block or clarify all other values because the full resolver domains remain Partial. Do not globally block operations that omit these fields. Evidence: `SRC-E2E-MTT-CREATE-IMPORT-VALUES-20260905`, `SRC-E2E-MTT-CREATE-RECONCILIATION-20260905`.

<!-- E2E-DISCOVERY:DISC-MTT-FIELD-LENGTH-20260909 -->
## Text length design boundary

Treat the 20-character transaction-type Name maximum and 80-character Description maximum as deterministic design constraints for create and for any supported update of Description. A boundary value is valid; a boundary-plus-one value blocks candidate generation. Never resolve an overlength request by silent truncation because that can change identity, uniqueness, or business meaning. Evidence: `SRC-EDM-RA-CUST-26B`, `SRC-E2E-MTT-FIELD-LENGTH-20260909`.
