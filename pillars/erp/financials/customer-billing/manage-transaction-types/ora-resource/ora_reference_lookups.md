# Manage Transaction Types Reference Lookups


Only fixed local domains and source-proven FSM import resolvers are recorded. The 26B `transactionTypesLOV` GET is discovery evidence but does not prove a deterministic Name-plus-SetCode preflight, so no executable REST lookup node is generated.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| validate_transaction_class | Type is supplied | ADJ, BR, CB, CM, DEP, DM, GUAR, INV | Trim and normalize a documented label only when its unique code mapping is present; otherwise require an exact code | Type | Reject off-domain or ambiguous values |
| validate_record_status | Status is supplied | A, D, I | Exact code or unique documented label mapping | Status | Reject off-domain or ambiguous values |
| validate_printing_option | DefaultPrintingOption is supplied | N, NOT, PRI | Exact code or unique documented label mapping | DefaultPrintingOption | Reject off-domain or ambiguous values |
| validate_completion_control | ControlCompletion is supplied | ALL, NEGATIVE_LINE_AMT, NONE | Exact code or unique documented label mapping | ControlCompletion | Reject off-domain or ambiguous values |
| validate_boolean_flag | A source-backed Boolean field is supplied | Y, N | Normalize Yes or true to Y and No or false to N; reject every other value | Requested Boolean field | Reject off-domain or ambiguous values |
| verify_creation_sign | CreationSign is supplied | Verified safe subset: `P` / `Positive Sign`; the full SIGN domain is not enumerated | Match exact code `P` or the case-insensitive label `Positive Sign`; normalize to `P` | CreationSign | Return `P`; reject every other value pending direct evidence |
| verify_default_status | DefaultStatus is supplied | Verified safe subset: `OP` / `Open`; the full INVOICE_TRX_STATUS domain is not enumerated | Match exact code `OP` or the case-insensitive label `Open`; normalize to `OP` | DefaultStatus | Return `OP`; reject every other value pending direct evidence |
| verify_usage_category | UsageCategoryCode is supplied | Environment-supported ORA_AR_USAGE_CATEGORY code; not enumerated by current evidence | Require an exact value that has been verified in the selected environment; no label-to-code inference | UsageCategoryCode | Block until environment verification is recorded or omit this optional field |
| verify_transaction_subclass | TrxSubclassCode is supplied | Environment-supported ORA_AR_TRX_SUB_CLASS code; not enumerated by current evidence | Require an exact value that has been verified in the selected environment; no label-to-code inference | TrxSubclassCode | Block until environment verification is recorded or omit this optional field |
| verify_account_combination | Any account-segment field is supplied | Ledger-specific chart and ordered segment combination; not safely enumerable read-only | Require the exact approved ledger/chart context and preserve the ordered segments without normalization | Requested account-segment fields | Block until explicit nonproduction validation is authorized and recorded |

## FSM Import Resolver Contracts

| Requirement ID | Resolver | Source Kind | Inputs | Authoritative Mechanism | Match and Mapping | Failure Boundary | Evidence |
|---|---|---|---|---|---|---|---|
| RES-REFERENCE-SET | resolve_reference_set_code | table_or_view | SetCode | SetIdSetCodeKey | Exact SetCode maps to SetId | Zero or ambiguous match rejects the row | SRC-CODE-AM-IMPL, SRC-CODE-AM-DEF, SRC-CODE-BO-REF-AR-TT |
| RES-LEGAL-ENTITY | resolve_legal_entity_identifier | table_or_view | LegalEntityIdentifier | LegalEntity AltKey | Exact identifier maps to LegalEntityId | Zero or ambiguous match rejects the row | SRC-CODE-AM-IMPL, SRC-CODE-AM-DEF, SRC-CODE-CREATE-VO |
| RES-APPLICATION-RULE-SET | resolve_application_rule_set | table_or_view | RuleSetName | UniqueRuleSetNameAltKey | Exact name maps to RuleSetId | Zero or ambiguous match rejects the row | SRC-CODE-AM-IMPL, SRC-CODE-AM-DEF, SRC-BO-APPRULESET-26C |
| RES-PAYMENT-TERM | resolve_default_payment_term | composite | DefaultTermSetCode, DefaultTermName | SetIdSetCodeKey then PaymentTerm AltKey | Set code maps to SetId; name plus SetId maps to DefaultTermId | Zero or ambiguous match rejects the row | SRC-CODE-AM-IMPL, SRC-CODE-AM-DEF, SRC-SOAP-PAYTERM-26C |
| RES-TRANSACTION-TYPE-REFERENCE | resolve_related_transaction_type | composite | Related SetCode and Name | SetIdSetCodeKey then TransactionType AltKey | Name plus SetId maps to the related transaction type | Zero or ambiguous match rejects the row | SRC-CODE-AM-IMPL, SRC-CODE-PRIMARY-VO, SRC-REST-TRXTYPE-26B |
| RES-BUSINESS-UNIT | resolve_reference_account_business_unit | table_or_view | BuName, EnterpriseId context | BuAltKeyByName | Exact context-qualified name maps to BusinessUnitId | Zero or ambiguous match rejects the row | SRC-CODE-AM-IMPL, SRC-CODE-REF-VO, SRC-CODE-BO-REF-AR-REF |
| RES-LEDGER | resolve_reference_account_ledger | table_or_view | LedgerName | LedgerNameAltKey | Exact name maps to LedgerId and ChartOfAccountsId | Zero or ambiguous match rejects the row | SRC-CODE-AM-IMPL, SRC-CODE-REF-VO |

## Conditional Blocking Gaps

| Gap ID | Applicable Fields | Runtime Result | Evidence | Next Action |
|---|---|---|---|---|
| RESOLVER-CREATION-SIGN | CreationSign | Permit only `P` / `Positive Sign`; reject unverified values because the general SIGN resolver remains Partial | SRC-CODE-CREATE-VO, SRC-BO-TRXTYPE-26C, SRC-E2E-MTT-CREATE-IMPORT-VALUES-20260905, SRC-E2E-MTT-CREATE-RECONCILIATION-20260905 | Gather direct controlled evidence before adding any other SIGN code |
| RESOLVER-DEFAULT-STATUS | DefaultStatus | Permit only `OP` / `Open`; reject unverified values because the general INVOICE_TRX_STATUS resolver remains Partial | SRC-CODE-CREATE-VO, SRC-BO-TRXTYPE-26C, SRC-CODE-PRIMARY-VO, SRC-E2E-MTT-CREATE-IMPORT-VALUES-20260905, SRC-E2E-MTT-CREATE-RECONCILIATION-20260905 | Gather direct controlled evidence before adding any other status code |
| RESOLVER-USAGE-CATEGORY | UsageCategoryCode | Blocked until the environment-supported ORA_AR_USAGE_CATEGORY code is verified | SRC-CODE-CREATE-VO, SRC-BO-TRXTYPE-26C | Verify the requested code in the selected environment or omit the optional field |
| RESOLVER-TRANSACTION-SUBCLASS | TrxSubclassCode | Blocked until the environment-supported ORA_AR_TRX_SUB_CLASS code is verified | SRC-CODE-CREATE-VO, SRC-BO-TRXTYPE-26C | Verify the requested code in the selected environment or omit the optional field |
| RESOLVER-ACCOUNT-COMBINATION | ClearingSegments, DepositOffsetSegments, RevSegments, TaxSegments, UnbilledSegments, UnearnedSegments, DistSetSegments, DrcSegments, FreightSegments, RecSegments, BrUnpaidSegments, BrRemitSegments, BrFactorSegments | Blocked because the authoritative FSM path may create a valid GL combination and is not read-only | SRC-CODE-AM-IMPL, SRC-CODE-GL-BULK, SRC-CODE-ARPT-VALIDATE, SRC-CODE-REF-VO | Exercise only after explicit nonproduction import authorization with exact ledger and chart context |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A fixed domain value is off-domain | Reject it before ZIP generation |
| A customer-configured value is supplied | Preserve the business value and let the source-proven FSM resolver validate it through core.data-loader |
| A Partial resolver field is requested | Stop before candidate handoff unless the exact environment value is verified at the governed task-validation step |
| A public endpoint is unavailable but a Confirmed FSM resolver exists | Record the preflight limitation; do not convert it into permission to guess or into an automatic retry |

<!-- E2E-DISCOVERY:DISC-MTT-VERIFIED-VALUE-SUBSET-20260905 -->
## Verified safe value subset for CreationSign and DefaultStatus

Controlled nonproduction import and fresh-export reconciliation (`SRC-E2E-MTT-CREATE-IMPORT-VALUES-20260905`, `SRC-E2E-MTT-CREATE-RECONCILIATION-20260905`) verify only `P` / `Positive Sign` for `AR_TRANSACTION_TYPE.CreationSign` and `OP` / `Open` for `AR_TRANSACTION_TYPE.DefaultStatus`. Normalize those case-insensitive business labels or exact codes to `P` and `OP`. The general `SIGN` and `INVOICE_TRX_STATUS` resolvers remain Partial; block or clarify every other value and do not infer additional codes. Requests that omit these fields remain eligible to proceed.
