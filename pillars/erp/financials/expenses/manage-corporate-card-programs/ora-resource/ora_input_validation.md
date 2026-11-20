# Manage Corporate Card Programs Input Validation

> Execution scope: apply these task rules through the service handoffs in
> [live setup workflow](../references/live-setup-workflow.md). The rule registry
> performs validation only; core Data Loader owns import approval and submission.


Source-backed draft for EXM_MANAGE_CORPORATE_CARD_PROGRAMS. Public documentation is 26D; maintainer provenance is SOURCE-SNAPSHOT-147cfa7f931f. Source revision references do not establish compatibility with a deployed environment. The bounded CREATE preparation contract is defined in references/create-contract.md; unsupported requested features stop before preparation. Internal ADF calls do not establish callable preflight APIs.


## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Program identity | CardProgramName | Block the requested program validation | Use the exact intended program name; EO requires a non-null value and has precision 80 (PROGRAM-NAME) | Program root is requested | find_program_name_conflict |
| Program type | CardTypeLookupCode | Block classification until the user choice or proven import-default contract is available | Resolve enabled EXM_CARD_TYPE; the EO TRAVEL initializer does not prove CSV omission behavior (PROGRAM-TYPE) | Program root is requested | resolve_enabled_card_type |
| Card brand | CardBrandLookupCode | Block brand validation | Resolve enabled EXM_CARD_BRAND; message literals do not replace target lookup evidence (PROGRAM-BRAND) | Program root is requested | resolve_enabled_card_brand |
| Entity and operation contract | Requested create/update operation, selected entities and requested fields | Retain the requested business intent and report unresolved field contracts | Apply the bounded CREATE contract and executable field allowlist in references/create-contract.md; reject unsupported requested operations/fields before packaging | Any package authoring |  |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| A source package is supplied | Only exact task and release-qualified structural evidence is usable | Compare the selected target template with the reviewed structure in references/fsm-structure.md; bind its bytes and task identity, then separately qualify current baseline and requested entity ownership |  |
| A business reference is supplied | Its importer call site is evidence of translation, not a usable preflight route | Invoke only the applicable named resolver from ora_reference_lookups.md; skip absent optional references and reject explicitly unsupported ones |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Company account create inputs | Require company account name (maximum 80 characters), company number (maximum 30 characters), resolved issuer/site and business unit. For non-PROCUREMENT require payment terms, payment currency and payment option; for non-PROCUREMENT, COMPANY or BOTH additionally require an expense clearing account (COMPANY-REQUIRED). | Company account is requested |  |
| Name shape | Require CardProgramName non-null and within EO precision 80; duplicate-name validator reports EXM_CC_CARD_PRGRM_EXISTS (PROGRAM-NAME). Reject blank or whitespace-only names before serialization; never rely on importer blank handling for a required name. | Program root is requested | find_program_name_conflict |
| Type code | EO requires a non-null CardTypeLookupCode with precision 25 and validates enabled EXM_CARD_TYPE. Message lists TRAVEL and PROCUREMENT; target enabled values require lookup (PROGRAM-TYPE). | Type is supplied | resolve_enabled_card_type |
| Brand code | EO requires a non-null CardBrandLookupCode with precision 25 and validates enabled EXM_CARD_BRAND. Message lists AmericanExpress, Diners, MasterCard and Visa; target availability is not inferred (PROGRAM-BRAND). | Brand is supplied | resolve_enabled_card_brand |
| Description length | EO precision is 240; do not infer omission, clearing or update semantics from the length constraint (PROGRAM-DESCRIPTION). | Description is supplied |  |
| Inactive date | Nonempty InactiveDate is unsupported in the bounded CREATE path and must be rejected. Empty optional date is not supplied; no timezone or serialization is guessed (PROGRAM-INACTIVE). | InactiveDate is supplied |  |
| Token code | EO validates enabled ORA_EXM_CC_TOKEN_CODE; message values are Y and M. Server normalization is owned by the defaulting resource (PROGRAM-TOKEN-VALIDATION). | EnableCcTokenFlag is supplied | resolve_enabled_token_code |
| Observed package shape | The supported blank-template structure has six CSV entities, 174 physical columns and 165 entity fields. Use exact ordered headers from the selected target template and preserve metadata; references/fsm-structure.md records the reviewed structure (PACKAGE-SCOPE). | Any FSM candidate is proposed |  |

## Observed Entity Inventory

| Entity | Observed Columns | Evidence Scope |
|---|---|---|
| EXM_CARD_PROGRAM | 27 | Blank-template headers confirmed; field operations independently qualified |
| EXM_CARD_DOWNLOAD_PARAM | 16 | Blank-template headers confirmed; field operations independently qualified |
| EXM_CARD_UPLOAD_RULE | 16 | Blank-template headers confirmed; field operations independently qualified |
| EXM_CC_COMPANY_ACCOUNT | 45 | Blank-template headers confirmed; field operations independently qualified |
| EXM_CORPORATE_CARD_ISSUER | 35 | Blank-template headers confirmed; field operations independently qualified |
| ORA_EXM_SETUP_PARTY_REFERENCE | 35 | Blank-template headers confirmed; field operations independently qualified |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CCP.VALIDATE_INPUT | step | 10 | validate_input | valid->CCP.RESOLVE_REFERENCES;invalid->CCP.HANDLE_ERROR | none | stop | Validate requested task inputs before a runnable rule plan or package preview. |

## Source Evidence

| Fact ID | Reviewed Source and Locator | Evidence Boundary |
|---|---|---|
| TASK-IDENTITY | SRC-CATALOG-TASKS: knowledge/setup-task-catalog/effective/setupTasksAll.json; taskShortName EXM_MANAGE_CORPORATE_CARD_PROGRAMS; SRC-CATALOG-HIERARCHY: knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json; Financials/Expenses and Procurement/Self Service Procurement placements | Catalog eligibility and identity do not qualify a live target or per-field operations. |
| PACKAGE-SCOPE | SRC-FSM-PACKAGE: reviewed same-task current-export metadata and blank-template header inventory; ordered headers documented in references/fsm-structure.md; no customer rows distributed | Blank-template package identity and ordered headers confirmed; no import success, field lifecycle semantics or source-to-target deployment equivalence inferred. |
| PROGRAM-NAME | SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:88`); lines 88-107; SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:447`); lines 447-455; SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:536`); lines 536-546; SRC-CODE-CARD-VO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/view/CardProgramVO.xml:241`); lines 241-246 | Source-backed root name validation. Do not infer rename support or a three-field composite key from child CSV prefix columns. |
| PROGRAM-TYPE | SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:29`); lines 29-43; SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:111`); lines 111-150 | Lookup validation and message values are source observations; target enabled codes and FSM absent/blank semantics remain unqualified. EO default is separately owned by PROGRAM-TYPE-EO-DEFAULT. |
| PROGRAM-BRAND | SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:13`); lines 13-27; SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:154`); lines 154-191 | Verify enabled lookup codes for the qualified target before executing; a message literal is not a current target LOV snapshot. |
| PROGRAM-DESCRIPTION | SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:195`); lines 195-205 | EO length constraint only; no FSM create/update/blank disposition inferred. |
| PROGRAM-INACTIVE | SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:207`); lines 207-228 | Use source operator, not inferred wording from the message identifier; timezone/date serialization and null semantics remain unqualified. |
| PROGRAM-TOKEN-VALIDATION | SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:44`); lines 44-63; SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:547`); lines 547-564 | EO lookup validation and message literal only; current target enabled lookup values and CSV blank/omitted behavior remain unqualified. Import normalization is separately owned by PROGRAM-TOKEN. |

| COMPANY-REQUIRED | CardCompanyAccountEO.xml (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardCompanyAccountEO.xml:97`); CardCompanyAccountEOImpl.java (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardCompanyAccountEOImpl.java:1298`), lines 1298-1380 | EO precision, mandatory fields and conditional validators. Internal identifier validation does not supply portable import keys. Payment-option selection is a business choice; do not infer it from the card brand. |

## Empty customer cells (CREATE)

Treat null, empty-string and whitespace-only cells as not supplied. For fields
that are optional in the selected program/company/upload context, skip their
value validation and reference lookup, and do not ask the customer to fill them.
Record skipped field names without inventing a value. Do not turn blank into
zero, N, a default choice or an instruction to clear an existing value. Preserve
explicit values, including text `0`, `N` and leading zeros, and validate them.

Check mandatory and conditional requirements first: an empty required cell still
blocks preparation. For Travel company accounts, Both Pay or Company Pay requires
the clearing account. Fields with a qualified derivation retain that rule: blank
file format derives from the resolved brand when upload rules are requested.
Unknown fields and invalid types remain errors, even when apparently empty.

Skip the business input, not the physical FSM column. Keep exact headers, row
widths, trailing empty cells and all CSV members. Never construct a row from only
nonempty cells. Populated rows still require the task's supported serialization
contract; this customer-input policy does not prove that Fusion ignores empty
CSV cells or authorize deleting XML nodes, changing metadata or clearing values.
The current request is CREATE; this policy does not qualify update semantics.
