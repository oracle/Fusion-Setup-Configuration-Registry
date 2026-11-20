# Manage Corporate Card Programs Defaulting Rules

> Execution scope: apply these task rules through the service handoffs in
> [live setup workflow](../references/live-setup-workflow.md). The rule registry
> performs validation only; core Data Loader owns import approval and submission.


Source-backed draft for EXM_MANAGE_CORPORATE_CARD_PROGRAMS. Public documentation is 26D; maintainer provenance is SOURCE-SNAPSHOT-147cfa7f931f. Source revision references do not establish compatibility with a deployed environment. The bounded CREATE preparation contract is defined in references/create-contract.md; unsupported requested features stop before preparation. Internal ADF calls do not establish callable preflight APIs.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| FileFormatCode | AmericanExpress -> FILE_FMT_AMEX_GL1025; Diners -> FILE_FMT_DINERS; MasterCard -> FILE_FMT_MSTRCARD_CDF3; Visa -> FILE_FMT_VISA (UPLOAD-FORMAT-BRAND) | CREATE a new program with upload rules in scope and blank/unspecified file format; use the resolved exact CardBrandLookupCode | No; preserve an explicit format and validate it against the brand-filtered enabled lookup |  |

## Server Observations — No Client Default

These are implementation observations, not payload default rules. The only
client default currently qualified above is the brand-derived file format.
Require an explicit type choice. Do not synthesize token, party-module, site-name
or identifying-address values from these observations. Their missing/blank FSM
contracts still require qualification before generating an affected candidate.

| Observed Field | Observed Server Behavior |
|---|---|
| CardTypeLookupCode | TRAVEL is the EO initializer (PROGRAM-TYPE-EO-DEFAULT) |
| EnableCcTokenFlag | Server retains existing Y/M; an existing other/blank XML element becomes M for exact MasterCard and Y otherwise (PROGRAM-TOKEN) |
| Internal CreatedByModule attributes | AP_SUPPLIERS_API fallback in specific new-party/usage/location/site branches (PARTY-INTERNAL-FALLBACKS) |
| Internal new-site name | EXM_PARTY_SITE_ plus party name when that creation branch has a blank site name (PARTY-INTERNAL-FALLBACKS) |
| Internal identifying-address flag | Y in the reviewed new-site branch (PARTY-INTERNAL-FALLBACKS) |

## Brand-derived File Format

For a new program, derive a blank or unspecified `FileFormatCode` from the exact
resolved `CardBrandLookupCode` using the Standard Defaults table. Do not ask the
customer to provide a file format when this mapping supplies the default. Record
that the value was derived from card brand and show it in the import preview.
An explicit customer format takes precedence and must be validated; never replace
an invalid explicit value silently. For an unknown or unresolved brand, stop
format derivation and resolve the brand rather than guessing a format.

These assignments reproduce setup UI behavior. `refreshFileFomatCodeLOV()` calls
`execRefreshFileFormat()`, which both assigns the default and filters the file
format LOV by the corresponding code prefix. This is not proof that the FSM
importer calls that UI method. Once the import path is qualified, explicitly
serialize the derived value in `EXM_CARD_UPLOAD_RULE.FileFormatCode`; do not rely
on an omitted or blank CSV value to trigger server defaulting. Validate that the
code is enabled in the target's `EXM_CC_FILE_FORMAT` lookup before execution.
Do not apply this CREATE default to updates or overwrite an existing program's
format. This rule does not clear the task's other execution-readiness blockers.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CCP.CHECK_DEFAULTS | step | 40 | apply_default | qualified->CCP.ENFORCE_DESIGN;blocked->CCP.HANDLE_ERROR | CCP.CHECK_DEPENDENCIES | stop | Apply only source-qualified field defaults; unresolved conditions prevent planning and payload defaulting. |

## Source Evidence

| Fact ID | Reviewed Source and Locator | Evidence Boundary |
|---|---|---|
| PROGRAM-TYPE-EO-DEFAULT | SRC-CODE-CARD-EO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/publicModel/entity/CardProgramEO.xml:111`); lines 111-111 | EO declaration only, not proof of FSM absent/blank serialization or default applicability. Do not silently populate TRAVEL. |
| PROGRAM-TOKEN | SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:623`); lines 623-635 | AM normalization occurs only when the element exists. Missing-element behavior and CSV blank-to-XML behavior are not proved. Record server observation; default applicability remains TBD and no payload default is synthesized. |
| PARTY-INTERNAL-FALLBACKS | SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:347`); lines 347-381; SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:425`); lines 425-430; SRC-CODE-CARD-AMIMPL (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/applicationModule/CorporateCardProgramServiceAMImpl.java:453`); lines 453-477 | Internal implementation defaults for specific creation branches only. Do not synthesize CSV values or apply these defaults to pre-existing parties/sites. |

| UPLOAD-FORMAT-BRAND | ManageCardProgramAMImpl.java (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/setup/model/src/oracle/apps/financials/expenses/creditCard/setup/uiModel/applicationModule/ManageCardProgramAMImpl.java:1053`); lines 765-787 and 1053-1083 | Source-confirmed UI assignments and brand-prefix LOV filtering. CREATE-only client default policy preserves explicit input; target enabled values and FSM execution remain subject to qualification. |
