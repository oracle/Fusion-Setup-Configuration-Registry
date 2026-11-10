# Manage Transaction Types Input Validation


<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AR_REF_ACCT_TRX_TYPE::AR_TRANSACTION_TYPE.Name, AR_REF_ACCT_TRX_TYPE::AR_TRANSACTION_TYPE.SetCode, AR_REF_ACCT_TRX_TYPE::BrFactorSegments, AR_REF_ACCT_TRX_TYPE::BrRemitSegments, AR_REF_ACCT_TRX_TYPE::BrUnpaidSegments, AR_REF_ACCT_TRX_TYPE::BuName, AR_REF_ACCT_TRX_TYPE::ClearingSegments, AR_REF_ACCT_TRX_TYPE::DepositOffsetSegments, AR_REF_ACCT_TRX_TYPE::DistSetSegments, AR_REF_ACCT_TRX_TYPE::DrcSegments, AR_REF_ACCT_TRX_TYPE::FreightSegments, AR_REF_ACCT_TRX_TYPE::LedgerName, AR_REF_ACCT_TRX_TYPE::Name, AR_REF_ACCT_TRX_TYPE::RecSegments, AR_REF_ACCT_TRX_TYPE::RevSegments, AR_REF_ACCT_TRX_TYPE::SourceRefTable, AR_REF_ACCT_TRX_TYPE::TaxSegments, AR_REF_ACCT_TRX_TYPE::UnbilledSegments, AR_REF_ACCT_TRX_TYPE::UnearnedSegments, AR_TRANSACTION_TYPE::AccountingAffectFlag, AR_TRANSACTION_TYPE::AdjPostToGlFlag, AR_TRANSACTION_TYPE::AllocateTaxFreight, AR_TRANSACTION_TYPE::AllowFreightFlag, AR_TRANSACTION_TYPE::AllowFutureAcctDateFlag, AR_TRANSACTION_TYPE::AllowOverapplicationFlag, AR_TRANSACTION_TYPE::Attribute1, AR_TRANSACTION_TYPE::Attribute10, AR_TRANSACTION_TYPE::Attribute11, AR_TRANSACTION_TYPE::Attribute12, AR_TRANSACTION_TYPE::Attribute13, AR_TRANSACTION_TYPE::Attribute14, AR_TRANSACTION_TYPE::Attribute15, AR_TRANSACTION_TYPE::Attribute2, AR_TRANSACTION_TYPE::Attribute3, AR_TRANSACTION_TYPE::Attribute4, AR_TRANSACTION_TYPE::Attribute5, AR_TRANSACTION_TYPE::Attribute6, AR_TRANSACTION_TYPE::Attribute7, AR_TRANSACTION_TYPE::Attribute8, AR_TRANSACTION_TYPE::Attribute9, AR_TRANSACTION_TYPE::AttributeCategory, AR_TRANSACTION_TYPE::ControlCompletion, AR_TRANSACTION_TYPE::CreationSign, AR_TRANSACTION_TYPE::CreditMemoTypeName, AR_TRANSACTION_TYPE::CreditMemoTypeSetCode, AR_TRANSACTION_TYPE::DefaultPrintingOption, AR_TRANSACTION_TYPE::DefaultStatus, AR_TRANSACTION_TYPE::DefaultTermName, AR_TRANSACTION_TYPE::DefaultTermSetCode, AR_TRANSACTION_TYPE::Description, AR_TRANSACTION_TYPE::DraweeIssuedFlag, AR_TRANSACTION_TYPE::EndDate, AR_TRANSACTION_TYPE::ExcludeFromLateCharges, AR_TRANSACTION_TYPE::GlobalAttribute1, AR_TRANSACTION_TYPE::GlobalAttribute10, AR_TRANSACTION_TYPE::GlobalAttribute11, AR_TRANSACTION_TYPE::GlobalAttribute12, AR_TRANSACTION_TYPE::GlobalAttribute13, AR_TRANSACTION_TYPE::GlobalAttribute14, AR_TRANSACTION_TYPE::GlobalAttribute15, AR_TRANSACTION_TYPE::GlobalAttribute16, AR_TRANSACTION_TYPE::GlobalAttribute17, AR_TRANSACTION_TYPE::GlobalAttribute18, AR_TRANSACTION_TYPE::GlobalAttribute19, AR_TRANSACTION_TYPE::GlobalAttribute2, AR_TRANSACTION_TYPE::GlobalAttribute20, AR_TRANSACTION_TYPE::GlobalAttribute3, AR_TRANSACTION_TYPE::GlobalAttribute4, AR_TRANSACTION_TYPE::GlobalAttribute5, AR_TRANSACTION_TYPE::GlobalAttribute6, AR_TRANSACTION_TYPE::GlobalAttribute7, AR_TRANSACTION_TYPE::GlobalAttribute8, AR_TRANSACTION_TYPE::GlobalAttribute9, AR_TRANSACTION_TYPE::GlobalAttributeCategory, AR_TRANSACTION_TYPE::GlobalAttributeDate1, AR_TRANSACTION_TYPE::GlobalAttributeDate2, AR_TRANSACTION_TYPE::GlobalAttributeDate3, AR_TRANSACTION_TYPE::GlobalAttributeDate4, AR_TRANSACTION_TYPE::GlobalAttributeDate5, AR_TRANSACTION_TYPE::GlobalAttributeNumber1, AR_TRANSACTION_TYPE::GlobalAttributeNumber2, AR_TRANSACTION_TYPE::GlobalAttributeNumber3, AR_TRANSACTION_TYPE::GlobalAttributeNumber4, AR_TRANSACTION_TYPE::GlobalAttributeNumber5, AR_TRANSACTION_TYPE::LegalEntityIdentifier, AR_TRANSACTION_TYPE::Name, AR_TRANSACTION_TYPE::NaturalApplicationOnlyFlag, AR_TRANSACTION_TYPE::PostToGl, AR_TRANSACTION_TYPE::RuleSetName, AR_TRANSACTION_TYPE::SetCode, AR_TRANSACTION_TYPE::SignedFlag, AR_TRANSACTION_TYPE::StartDate, AR_TRANSACTION_TYPE::Status, AR_TRANSACTION_TYPE::SubsequentTrxTypeName, AR_TRANSACTION_TYPE::SubsequentTrxTypeSetCode, AR_TRANSACTION_TYPE::TaxCalculationFlag, AR_TRANSACTION_TYPE::TrxSubclassCode, AR_TRANSACTION_TYPE::Type, AR_TRANSACTION_TYPE::UsageCategoryCode -->
<!-- fscr-update-fields: AR_TRANSACTION_TYPE::Description, AR_TRANSACTION_TYPE::EndDate, AR_TRANSACTION_TYPE::Status -->

Validate normalized business intent and exact FSM package structure before any candidate is handed to `core.data-loader`. The template package owns header order; these tables do not replace it.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver | Evidence |
|---|---|---|---|---|---|---|
| Parent business identity | SetCode and Name | Block preparation | Require both exact values; Name alone is not unique across sets | Every parent create |  | SRC-CODE-BO-META, SRC-CODE-PRIMARY-VO, SRC-EDM-RA-CUST-26B |
| Parent create contract | SetCode, Name, PostToGl, AccountingAffectFlag, Status, Type, DefaultPrintingOption, DefaultStatus, AllowFreightFlag, AllowOverapplicationFlag, CreationSign, StartDate, TaxCalculationFlag, NaturalApplicationOnlyFlag | Block preparation | Ask only for the missing business values; do not invent defaults | Parent create |  | SRC-FSM-PACKAGE, SRC-CODE-CREATE-VO, SRC-CODE-PRIMARY-EO, SRC-BO-TRXTYPE-26C |
| Child parent linkage | AR_TRANSACTION_TYPE.SetCode and AR_TRANSACTION_TYPE.Name | Block child row | Copy the exact parent identity into the child header fields | Every reference-account child row |  | SRC-FSM-PACKAGE, SRC-CODE-AM-DEF, SRC-CODE-REF-VO |
| Child accounting context | BuName and LedgerName | Block child row | Require exact environment business-unit and ledger names | Every reference-account child row |  | SRC-CODE-AM-IMPL, SRC-CODE-REF-VO, SRC-EDM-AR-REF-26A |
| Lifecycle operation | create or update | Block unsupported operation or unsupported update field | For update, require one exact existing SetCode-plus-Name target and permit only Description, Status, or EndDate; preserve every other field and unrelated row. Physical delete is unsupported, and Status/EndDate retirement remains an update. | Every normalized design |  | SRC-HELP-TRXTYPE-26C, SRC-CODE-CREATE-VO, SRC-CODE-AM-IMPL, SRC-CODE-PRIMARY-VO, SRC-CODE-PRIMARY-EO, SRC-E2E-MTT-DESCRIPTION-UPDATE-20260905, SRC-E2E-MTT-DESCRIPTION-ROLLBACK-20260905 |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver | Evidence |
|---|---|---|---|---|
| A related payment term is supplied | DefaultTermName and DefaultTermSetCode must be supplied together | Resolve the set and term through the documented FSM import contract |  | SRC-CODE-AM-IMPL, SRC-CODE-CREATE-VO, SRC-SOAP-PAYTERM-26C |
| A subsequent or credit-memo transaction type is supplied | Supply the related Name and companion SetCode together | Resolve within the exact set; zero or ambiguous matches block |  | SRC-CODE-AM-IMPL, SRC-CODE-CREATE-VO, SRC-REST-TRXTYPE-26B |
| Any account-segment role is supplied | BuName and LedgerName are mandatory and the ordered segments must match that ledger's chart | Keep the candidate blocked until authorized environment validation |  | SRC-CODE-AM-IMPL, SRC-CODE-GL-BULK, SRC-CODE-ARPT-VALIDATE |
| A descriptive-flexfield segment is supplied | Its matching AttributeCategory or GlobalAttributeCategory and source-backed datatype must be present | Reject contextless or cross-context values |  | SRC-CODE-PRIMARY-EO, SRC-CODE-PRIMARY-VO, SRC-EDM-RA-CUST-26B |

## Field Validation

| Check | What Happens | Applies When | Resolver | Evidence |
|---|---|---|---|---|
| Fixed transaction class | Accept only ADJ, BR, CB, CM, DEP, DM, GUAR, or INV | Type is supplied |  | SRC-BO-TRXTYPE-26C, SRC-CODE-CREATE-VO |
| Fixed record status | Accept only A, D, or I | Status is supplied |  | SRC-BO-TRXTYPE-26C, SRC-EDM-RA-CUST-26B |
| Fixed printing option | Accept only N, NOT, or PRI | DefaultPrintingOption is supplied |  | SRC-BO-TRXTYPE-26C, SRC-CODE-CREATE-VO |
| Fixed completion control | Accept only ALL, NEGATIVE_LINE_AMT, or NONE | ControlCompletion is supplied |  | SRC-BO-TRXTYPE-26C, SRC-CODE-CREATE-VO |
| Boolean option fields | Accept only Y or N | Any source-backed Boolean flag is supplied |  | SRC-BO-TRXTYPE-26C, SRC-CODE-PRIMARY-EO |
| Application flags | Reject when NaturalApplicationOnlyFlag and AllowOverapplicationFlag are both Y | Both fields are supplied |  | SRC-BO-TRXTYPE-26C, SRC-CODE-PRIMARY-EO |
| Effective dates | Require valid ISO date syntax and reject EndDate earlier than StartDate | StartDate or EndDate is supplied |  | SRC-BO-TRXTYPE-26C, SRC-CODE-PRIMARY-EO, SRC-EDM-RA-CUST-26B |
| Audit fields | Reject caller values and omit LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, and LastUpdateLogin from generated rows | Parent or child candidate generation |  | SRC-CODE-AM-IMPL, SRC-CODE-PRIMARY-EO, SRC-CODE-REF-VO |
| CSV row width | Require exactly 87 fields for AR_TRANSACTION_TYPE and 24 fields for AR_REF_ACCT_TRX_TYPE, including explicit trailing blanks | Every source or generated CSV row |  | SRC-FSM-PACKAGE |
| Guarded feature fields | Reject inferred MagneticFormatCode or DocumentType values | Either field is supplied without source-backed exact evidence |  | SRC-CODE-PRIMARY-EO, SRC-CODE-PRIMARY-VO, SRC-EDM-RA-CUST-26B |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTT.VALIDATE_INPUT | decision | 10 | validate_input | valid->MTT.CHECK_DEPENDENCIES;invalid->RETURN_ISSUES | none | stop | A Manage Transaction Types design or FSM package is prepared |

<!-- E2E-DISCOVERY:DISC-MTT-FIELD-LENGTH-20260909 -->
## Source-backed text length limits

Before producing an immutable preview or candidate, require `AR_TRANSACTION_TYPE.Name` to contain no more than 20 characters and an explicitly supplied `AR_TRANSACTION_TYPE.Description` to contain no more than 80 characters. Report the record, field, actual length, maximum length, and unit in business language. Do not silently truncate, abbreviate, or rewrite the implementor's text; ask for or preview a revised value. Evidence: `SRC-EDM-RA-CUST-26B`, `SRC-E2E-MTT-FIELD-LENGTH-20260909`.
