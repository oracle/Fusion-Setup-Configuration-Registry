# Manage Bank Charges Dependency Readiness

## Dependency readiness policy

This step determines whether every dependency that applies to the requested
create operation is ready enough to continue. It runs after reference lookup
assessment and before defaulting. It does not perform lookups, create related
setup, build an import package or mutate Oracle Fusion.

An omitted field with an executable standard default is `default pending` and
may continue to the defaulting step. An explicitly supplied reference must use
its declared resolver. A supplied value alone does not prove identity,
eligibility or readiness. The exact resolver contracts are maintained in
[ora_reference_lookups.md](ora_reference_lookups.md).

A bound UNVERIFIED_API_UNAVAILABLE warning under that reference policy permits
continuation for additional REST checks without marking the dependency
satisfied. This exception takes precedence over their resolved-result or
approved-exception requirements below. Required CSV inputs and local choices
still apply; completed invalid or ambiguous results still stop. Carry warnings
into Data Loader validation and preview.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| BKC.DEPENDENCIES | step | 30 | resolve_dependency | pass->BKC.DEFAULTS;fail->BKC.ERROR | BKC.LOOKUPS | stop | true |

## Dependency Rules

Evaluate transferring and receiving bank and branch dependencies separately.
Parent-qualified line references inherit the resulting header values.

| Dependency ID | Dependency | Applies When | Ready Result | Value Source | Resolver | Values to Fill |
|---|---|---|---|---|---|---|
| BKC.DEP.LEGAL_ENTITY | Legal entity identity | LegalEntityName or LegalEntityIdentifier is supplied, or both are omitted on create | Both omitted: default pending. All with blank identifier: satisfied local choice. Named entity: satisfied only after the identifier contract resolves. Unavailable additional REST check: continue with a bound UNVERIFIED_API_UNAVAILABLE warning; required CSV inputs remain mandatory. | Standard default or explicit customer value | resolve_legal_entity | LegalEntityName and LegalEntityIdentifier |
| BKC.DEP.CURRENCY | Currency identity | CurrencyCode is supplied or omitted on create | Omitted: default pending. Supplied: satisfied only after currency resolution succeeds. Unavailable additional REST check: continue with a bound UNVERIFIED_API_UNAVAILABLE warning; required CSV inputs remain mandatory. | Standard default or explicit customer value | resolve_currency | CurrencyCode |
| BKC.DEP.SETTLEMENT | Settlement priority choice | SettlementPriorityDisplay is supplied or omitted on create | Omitted: default pending. Supplied Express or Normal: satisfied local choice. | Standard default or explicit customer choice | resolve_settlement_priority | SettlementPriorityDisplay |
| BKC.DEP.BANK_OPTION | Bank option choice | A transferring or receiving bank option is supplied or omitted on create | Option and name omitted: default pending. Valid supplied All or Specific choice: satisfied. | Standard default or explicit customer choice | resolve_bank_option | Corresponding BankOption |
| BKC.DEP.BRANCH_OPTION | Branch option choice | A transferring or receiving branch option is supplied or omitted on create | Option and name omitted: default pending. Valid supplied All or Specific choice: satisfied. | Standard default or explicit customer choice | resolve_branch_option | Corresponding BranchOption |
| BKC.DEP.BANK | Bank identity | The corresponding bank option is Specific bank | Satisfied only by the declared resolver result or a recorded approved verification exception; otherwise blocked. Unavailable additional REST check: continue with a bound UNVERIFIED_API_UNAVAILABLE warning; required CSV inputs remain mandatory. | Explicit bank context | resolve_bank | Corresponding BankName, BankNumber and BankCountry context |
| BKC.DEP.COUNTRY | Bank country context | A bank country is supplied for the corresponding side, including All banks or All branches | Satisfied only when the applicable resolver contract accepts the context or a recorded approved verification exception covers it; otherwise blocked. Unavailable additional REST check: continue with a bound UNVERIFIED_API_UNAVAILABLE warning; required CSV inputs remain mandatory. | Explicit country context | resolve_bank_country | Corresponding BankCountry |
| BKC.DEP.BRANCH | Bank branch identity | The corresponding branch option is Specific branch | Satisfied only by the declared resolver result or a recorded approved verification exception; otherwise blocked. Unavailable additional REST check: continue with a bound UNVERIFIED_API_UNAVAILABLE warning; required CSV inputs remain mandatory. | Explicit bank and branch context | resolve_bank_branch | Corresponding BranchName and BranchNumber context |
| BKC.DEP.HEADER_DFF | Header descriptive flexfields | A header flexfield value is supplied | Satisfied by the native type check in BKC.INPUT; no separate dependency lookup is performed. Fusion may apply additional validation at import. | Optional customer value |  | Preserve the supplied value |
| BKC.DEP.LINE_DFF | Line descriptive flexfields | A line flexfield value is supplied | Satisfied by the native type check in BKC.INPUT; no separate dependency lookup is performed. Fusion may apply additional validation at import. | Optional customer value |  | Preserve the supplied value |

## Dependency Classification

| Result Category | Meaning | Next Step |
|---|---|---|
| Default pending | The field is omitted and an executable standard default applies | Continue to BKC.DEFAULTS. |
| Satisfied | The local choice or applicable resolver result is complete | Continue when every other applicable dependency is also ready. |
| Verify | The resolver contract exists but its required result has not been obtained | Run only the declared read-only verification route. |
| Not applicable | The effective option means this dependency is unnecessary | Continue and retain the applicability decision. |
| Blocked: evidence_unresolved | The applicable contract, identity, eligibility or result is incomplete | Stop and report the missing dependency. |
| Invalid supplied value | Verification proves that the supplied value fails its contract | Stop and request corrected input. |

## Evidence Boundary

When an effective bank or branch option is All, its corresponding specific
identity dependencies are not applicable and its name must be blank. This file
does not authorize creation of legal entities, currencies, banks, branches or
flexfields; package generation, import approval, reconciliation and recovery
remain separate workflow gates.
