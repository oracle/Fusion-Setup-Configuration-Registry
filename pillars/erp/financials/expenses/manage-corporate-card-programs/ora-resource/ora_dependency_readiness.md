# Manage Corporate Card Programs Dependency Readiness

> Execution scope: apply these task rules through the service handoffs in
> [live setup workflow](../references/live-setup-workflow.md). The rule registry
> performs validation only; core Data Loader owns import approval and submission.


Source-backed draft for EXM_MANAGE_CORPORATE_CARD_PROGRAMS. Public documentation is 26D; maintainer provenance is SOURCE-SNAPSHOT-147cfa7f931f. Source revision references do not establish compatibility with a deployed environment. The bounded CREATE preparation contract is defined in references/create-contract.md; unsupported requested features stop before preparation. Internal ADF calls do not establish callable preflight APIs.


## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Task and requested entity scope | Confirm the exact task and requested business effects; no cross-task ordering is assigned here. |
| 2 | References | Complete applicable named resolver contracts before treating any reference as satisfied. |
| 3 | Parent/child ownership | Use CREATE-only parent/child rows and existing issuer/site references from references/create-contract.md. Retain unused members header-only. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| CCP.BU | Business unit | Yes | Company account is requested | Verify | Selected target finBusinessUnitsLOV through resolve_business_unit | resolve_business_unit | Company-account validator requires the business unit | Select an active exact business unit; do not infer import privilege from visibility | Exact BuName, BusinessUnitId and PrimaryLedgerId as validation evidence |
| CCP.TERMS | Payment terms | Conditional | Company account is non-PROCUREMENT or PaymentTermName supplied | Verify | Selected target payablesPaymentTerms through resolve_payment_terms | resolve_payment_terms | Company validator requires terms for non-PROCUREMENT | Use a unique enabled in-date exact payment-term name; do not ask for internal IDs | Validated PaymentTermName; termsId only as evidence |
| CCP.ISSUER | Existing issuer party | Yes | Company account is requested | Verify | Approved same-target EXM_CORPORATE_CARD_ISSUER.csv through resolve_card_issuer | resolve_card_issuer | Company-account validator requires an issuer | Use an existing active exact issuer; new issuer creation is a separate request | CardIssuerName and PartyNumber; site qualification remains separate |
| CCP.SITE | Existing issuer site | Yes | Company account is requested | Verify | Complete Hub Organizations Address collection and approved issuer export through resolve_issuer_site | resolve_issuer_site | Importer selects a site by party; name alone cannot disambiguate | Use the exact existing selected site only when its party has one address; multiple sites require a different qualified importer contract | Validated existing party/site numbers and exported address; numeric ID only as evidence |
| CCP.LEDGER | Ledger and chart of accounts | Conditional | Company-account ledger or clearing account is requested | Verify | Selected target ledgersLOV through resolve_ledger | resolve_ledger | Clearing segments must be evaluated in the BU ledger chart of accounts | Resolve the primary ledger and reject a conflicting explicit ledger | Returned Name to company-account Name; ChartOfAccountsId for validation |
| CCP.CLEARING | Existing expense clearing combination | Conditional | Parent type is not PROCUREMENT and PaymentDueFromCode is COMPANY or BOTH, or a clearing account is explicitly supplied | Verify | Selected target accountCombinationsLOV through resolve_expense_clearing_account | resolve_expense_clearing_account | Non-Procurement Company and Both Pay require an expense clearing account | Customer selects the business account; verify it in the BU ledger COA; never auto-create | Validated ExpenseCcidSegments; combination ID only in validation evidence |
| CCP.ADMIN | Corporate-card administrator | Conditional | Nonempty administrator input is supplied | Blocked | Unsupported requested feature in bounded CREATE path | resolve_card_administrator | No qualified administrator adapter is included | Do not ask for an absent optional administrator; reject a supplied one before packaging | None; no person identifier synthesized |
| CCP.TERRITORY | Remittance territory | Conditional | Nonempty remittance input is supplied | Blocked | Unsupported requested feature in bounded CREATE path | resolve_territory | No qualified remittance adapter is included | Do not ask for an absent optional territory; reject supplied remittance before packaging | None; no territory identifier synthesized |
| CCP.SUMMARY_MAP | Existing transaction mapping | Conditional | MapTypeCode is supplied | Verify | Approved target mapping-task export through resolve_summary_mapping_rule | resolve_summary_mapping_rule | Importer resolves a unique MapTypeCode alternate key | Preserve the requested rule and validate its source column; no internal ID required | Exact MapTypeCode and matching source-column code |
| CCP.DETAIL_MAP | Existing transaction mapping | Conditional | MapTypeCode1 is supplied | Verify | Approved target mapping-task export through resolve_detail_mapping_rule | resolve_detail_mapping_rule | Importer resolves a unique MapTypeCode alternate key | Preserve the requested rule and validate its source column; no internal ID required | Exact MapTypeCode1 and matching source-column code |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Blocked | Required contract, source authority, scope or requested reference is unresolved | No; close the applicable contract before execution |
| Verify | A complete declared resolver exists and the active workflow selects it | Only the declared read; this resource grants no create permission |
| Satisfied | Qualified same-target evidence proves the exact applicable dependency | No additional write is implied |

## Domain and Relationship Evidence

| Context | Source-backed Relationship | Boundary |
|---|---|---|
| Corporate-card program | Issuer agreement with one or more company accounts; issuer and terms belong to the business setup (DOC-PROGRAM, DOC-ISSUER) | Does not establish every CSV field as mandatory |
| ADF task hierarchy | CardProgram has download-parameter, upload-rule and company-account child views (AM-HIERARCHY) | Child keys, update and cascade behavior remain unresolved |
| Mappings and runtime cards | Feed-to-card-expense-type mapping and BU expense-template mapping support transaction processing; runtime card creation is distinct (DOC-MAPPING, DOC-EMPLOYEE-MATCH) | Do not add runtime cards as another setup CSV |
| BOSS relationships | Program/account/upload/mapping relationships support domain navigation (BOSS-PROGRAM-RELATIONS, BOSS-UPLOAD-RELATIONS, BOSS-ACCOUNT-RELATIONS) | Filtered or outer/inner joined read results do not prove a persisted object is absent |
| Privileges | Manage Corporate Card Program privilege and authorized-BU data policy appear in the 26D security source (DOC-PRIVILEGE) | Actual target principal privileges must be verified by the routed workflow |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CCP.CHECK_DEPENDENCIES | step | 30 | resolve_dependency | satisfied->CCP.CHECK_DEFAULTS;blocked->CCP.HANDLE_ERROR | CCP.RESOLVE_REFERENCES | stop | Evaluate task-local dependency evidence after the required resolver contracts succeed. |

## Source Evidence

| Fact ID | Reviewed Source and Locator | Evidence Boundary |
|---|---|---|
| AM-HIERARCHY | SRC-CODE-CARD-AM (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAM.xml:29`); lines 29-39; SRC-CODE-CARD-AM (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAM.xml:90`); lines 90-106 | Task-wired hierarchy is confirmed; CSV child lifecycle and cascade/delete policy are not inferred. |
| BOSS-PROGRAM-RELATIONS | SRC-ALM-BOSS-CARD-PROGRAM: ALM MCP get_repository_blob: project=SOURCE-SNAPSHOT-1e7ea97e94a4; repository=erp_core_expenses.git; revision=main; path=ora_erp_core_expensesSetup/sources/model/self/modules/oraErpCoreExpensesSetup/businessObjects/CorporateCardProgram/bo.json5#197; lines 197-235 | Helpful domain relationships. Does not add runtime CorporateCard as a seventh setup CSV or qualify cascade behavior. |
| BOSS-UPLOAD-RELATIONS | SRC-ALM-BOSS-CARD-UPLOAD-RULE: ALM MCP get_repository_blob: project=SOURCE-SNAPSHOT-1e7ea97e94a4; repository=erp_core_expenses.git; revision=main; path=ora_erp_core_expensesSetup/sources/model/self/modules/oraErpCoreExpensesSetup/businessObjects/CorporateCardTransactionUploadRule/bo.json5#271; lines 271-320 | Join-filtered results cannot prove absence of a persisted upload rule. Detail mapping field and import MapTypeCode1 behavior use separate AM evidence. |
| BOSS-ACCOUNT-RELATIONS | SRC-ALM-BOSS-CARD-COMPANY-ACCOUNT: ALM MCP get_repository_blob: project=SOURCE-SNAPSHOT-1e7ea97e94a4; repository=erp_core_expenses.git; revision=main; path=ora_erp_core_expensesSetup/sources/model/self/modules/oraErpCoreExpensesSetup/businessObjects/CorporateCardCompanyAccount/bo.json5#582; lines 582-632 | Read-model joins, not task resolver filters or validation. Do not infer missing joined object means account missing. |
| DOC-PROGRAM | [SRC-CARD-26D-HELP-PROGRAM](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/what-s-a-corporate-card-program.html) | Domain semantics only, not CSV keys or child requiredness. |
| DOC-ISSUER | [SRC-CARD-26D-HELP-ISSUER](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/how-can-i-configure-corporate-card-issuers.html) | UI/business prerequisites. Does not map either party-reference CSV or prove target authorization. |
| DOC-MAPPING | [SRC-CARD-26D-HELP-MAPPING](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/mapping-rules.html) | Business dependency context. Do not equate every mapping UI label with import code or runtime REST lookup. |
| DOC-EMPLOYEE-MATCH | [SRC-CARD-26D-HELP-CARD-CREATION](https://docs.oracle.com/en/cloud/saas/financials/26d/faiex/options-for-creating-corporate-cards.html) | Explain CardEmpMatchingRule purpose; do not treat feed/card processing as part of setup import. |
| DOC-PRIVILEGE | [SRC-CARD-26D-SECURITY-FIN-ADMIN](https://docs.oracle.com/en/cloud/saas/financials/26d/oaahm/Financial_Application_Administrator_job_roles.html) | Documented prerequisite, not proof of actual target user privileges or authorization. |
