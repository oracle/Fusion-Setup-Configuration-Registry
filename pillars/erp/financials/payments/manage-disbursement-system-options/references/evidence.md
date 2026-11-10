# Evidence and claim boundaries

## Controlled create observation

SRC-E2E-CREATE-C01-164773: one native FSM absent-BU create on release11.13.27.01.0 completed53rows with zero failures/warnings. Fresh exact-task export proved12requested business values, explicit context and every pre-existing cell matched; requested blank PaymentsApprovalFlag persisted as N. Original exact reconciliation remains FAIL. New audit/derived cells were service-assigned.

Candidate SHA256:281495f4146686648aae1cefece48746c03c6106048cf9c963a8e8b0125ae852; fresh-export SHA256:7a8218bae0296a27ead86a3d2859d782b57c3d568312ecb1f6e8b74fa5a9571d. These immutable developer evidence bindings are not runtime dependencies. This case establishes neither a universal default nor blank-update behavior, exact ModuleId mapping or other-BU qualification. The exact defaulting layer remains unlocated. Do not turn fixture identities, historical service values or later business acceptance into defaults.


## Create preparation source review

SRC-GOLD-CREATE-REVIEW: full InternalPayerEO.xml (711 lines), service import
InternalPayerVO.xml (315 lines) and BusinessUnitValueVO.xml (223 lines) were
reviewed on GOLD. The Source IDs below identify these files; full internal locations remain in the external developer source register.
AutomaticPprReportSubmit has no IsNotNull declaration in either EO or import
VO. Seven other business fields have corroborated entity non-null declarations.
PaymentsApprovalFlag has a VO non-null hint but none in the EO; blank create
behavior is still unresolved. The BU selection query excludes existing
OPERATING_UNIT payer rows. Actual current-task UI selection can corroborate a
specific absent BU; it does not establish FSM serialization or import defaults.
The primary key is excluded from CSV and remains service-owned. No historical
audit value or derived BU usage value is a business-owned create input.

Controlled create preparation uses explicit business/context values and current
references, leaving service-owned columns blank for qualification. Its candidate
and exact application-validation decisions require independent human gates.
No create import success or deletion/absence restoration is claimed here.

Source review used the explicitly authorized GOLD series. The sources below support only their reviewed claims; they do not imply revision equivalence or current target lookup contents.

## Identity and persistence

The approved local repair adds offline deterministic serialization and independent
candidate checks. Metadata bytes/member order and all unrequested logical CSV
values are preserved; ZIP container timestamps/compression are normalized locally.
Synthetic regressions establish helper behavior only. Reverse preparation rejects
forged original before-values and fresh post-forward drift; restoration remains a
new separately confirmed and approved import.

An actual read-only Core capture on CPTCXCSQY-PKCE resolved the dedicated one-task
Run Book, exact task code, two native members and six resources. The connection
remained available for status and was cancelled without an approval command.
This qualifies that observed capture/cancellation boundary only; changed-value
persistence, submission and cleanup were not tested by that read-only repair.
The later controlled update/restoration observations below are separate evidence.

Task registration maps Internal Payer / IBY_INTERNAL_PAYER to the task import root. InternalPayerVO AltKey maps InternalPayerEO AltOrgKey containing OrgId. Import resolves BuName through Name + current EnterpriseId, then owns OrgId translation. Explicit enterprise scope preserves blank BuName.

## Controlled product evidence

A user-executed unchanged 27A import processed 53 rows with zero failures/warnings, including one blank enterprise row. A later read-only exact-task export had byte-identical CSV SHA-256 b15fa5aa1f211c8756af0bda7defb8a0714ad221f147d23f877624f423efdeba. This establishes unchanged acceptance/preservation only. No changed-field qualification, create default or deletion mechanism follows from it.

## Sources

| Source ID | Exact source | Reviewed claim boundary |
|---|---|---|
| SRC-DOC-INDEX | https://docs.oracle.com/en/cloud/saas/financials/26d/books.html | Newest accessible public Financials documentation index; not evidence of target environment release. |
| SRC-DOC-PAYMENT-METHODS | https://docs.oracle.com/en/cloud/saas/financials/26c/faipp/payment-methods.html | Supplier-specific payment-method defaults are enabled through this task. Does not establish CSV input codes or import defaults. |
| SRC-DOC-EDM | https://docs.oracle.com/en/cloud/saas/financials/26b/oedmf/ibyinternalpayersall-31649.html | Persistence corroboration only: system-generated IntPayerId, OrgId scope, audit columns and documented lookup families. Not authority for FSM keys, create defaults or target environment values. |
| SRC-INTERNAL-INDEX | Reviewed internal task guidance; full source location retained in the external developer source register | Navigation to task page; no import-semantic detail. |
| SRC-INTERNAL-TASK | Reviewed internal task guidance; full source location retained in the external developer source register | Identifies IBY_INTERNAL_PAYERS_ALL and screenshots; no import operation contract. |
| SRC-UI-VO | Reviewed source `DisbursementBusinessUnitWiseOptionVO.xml`; full location and source revision retained in the external developer source register | UI-side VO reviewed in existing browser tab. Business-unit filtering, field nullability/update metadata and LOV wiring only; does not establish FSM import behavior. |
| SRC-LIVE-UI | {target_fusion_base_url}/fscmUI/ | Corroborates visible enterprise settings, business-unit overrides, field labels and choices. No changes saved; no claim of FSM import behavior. |
| SRC-GOLD-AM-SNIPPETS | Reviewed source `FundsDisbursementPayerServiceAMImpl.java`; full location and source revision retained in the external developer source register | Full381 lines read. Export excludes IntPayerId,OrgId,BusinessUnitId,ObjectVersionNumber,EnterpriseId189-190. Import resolves BuName using BuAltKeyByName with current tenant/FND_ENTERPRISE_ID250-281; sets OrgId on non-null match. updatePrimaryKeysInXML uses root AltKey289-291; readXML294-295; commits root transaction298-299. Exceptions surface localized processing error302-304. |
| SRC-GOLD-UI-FULL | Reviewed source `ManageFDSystemOption.jsff`; full location and source revision retained in the external developer source register | Full 240-line source accessible in existing user tab. Enterprise settings and separate DisbursementBusinessUnitWiseOption collection; BU Name LOV required=true (148). SRA lengths/mandatory rules use binding hints (33-37,164-170); report Format uses binding hints (110). UI add/remove (141) is not proof of FSM lifecycle support. |
| SRC-GOLD-VO-SNIPPETS | Reviewed source `InternalPayerVO.xml`; full location and source revision retained in the external developer source register | Full315 lines read. Outer joins root to BU and usage, selecting enterprise null OrgId or resolved BU with PAYABLES_PAYMENT_BF46-49. Audit fields nonupdateable163-200. BU metadata BusinessUnitId1,ModuleId,ModuleKey nonupdateable/SDOHidden261-285. PK IntPayerId305-307; ViewKey AltKey maps EntityKey AltOrgKey308-313. |
| SRC-GOLD-AMDEF-SNIPPETS | Reviewed source `FundsDisbursementPayerServiceAM.xml`; full location and source revision retained in the external developer source register | MCP excerpts: InternalPayer ViewUsage11; root ViewObjectName12 has truncated suffix. BusinessUnit ViewUsage32 and exact oracle.apps.financials.commonModules.businessUnits.publicView.BusinessUnitPVO33. ServiceViewUsage49 declares CanCreate,CanUpdate,CanDelete true. Export/Import Control/Data/Return VO declarations15-30. |
| SRC-GOLD-EO-SNIPPETS | Reviewed source `InternalPayerEO.xml`; full location and source revision retained in the external developer source register | Full711 lines read. AltOrgKey is OrgId only657-668; unique-key validation690-703. Lookup list validators: payment basis200-213, document233-246, payment266-279, charge bearer498-511. OrgId validates BusinessUnitValueVA454-467. PPR format validates FormatVA530-543 constrained to IBY_FD_PPR_STATUS145-159. SRA fields length1024563-598. Audit HistoryColumn annotations357-441. |
| SRC-HELP-IBY-PAYMENTS-IMPLEMENT-26D | https://docs.oracle.com/en/cloud/saas/financials/26d/facsf/how-you-implement-payables-and-payments.html | Exact task section confirms enterprise and business-unit processing options and preconfigured setups. Application Implementation Consultant is the implementing role. Does not define CSV import fields. |
| SRC-HELP-IBY-INVOICE-TO-PAY-26D | https://docs.oracle.com/en/cloud/saas/financials/26d/faipp/implementing-payables-invoice-to-pay.pdf | Task-related sections: supplier-default option p206, default-basis alternatives p209, payment approval configuration p211-212. Business context only; not an FSM import contract. |
| SRC-HELP-APPROVAL-26D | https://docs.oracle.com/en/cloud/saas/financials/26d/faipp/how-you-set-up-payment-approval.html | Business setup links payment approval enablement with a selected PPR status report format and automatic submission. Approval policy and BPM rules are separate configuration. No scalar import defaults or validations inferred. |
| SRC-GOLD-EOIMPL | Reviewed source `InternalPayerEOImpl.java`; full location and source revision retained in the external developer source register | Reviewed method inventory and custom validation565-575, lock580-586 and doDML590-596. AutomaticPprReportSubmit=Y requires non-null/nonblank trimmed PprReportFormat. doDML delegates to superclass. No create override found in method inventory. |
| SRC-GOLD-BU-PVO | Reviewed source `BusinessUnitPVO.xml`; full location and source revision retained in the external developer source register | Reviewed resolver query FUN_ALL_BUSINESS_UNITS_V, BusinessUnitId/Name/EnterpriseId mappings and ViewKey BuAltKeyByName994-999. Uses matching entity key; alternate key is distinct from user-search STARTSWITH criteria. |
| SRC-GOLD-BU-PEO | Reviewed source `BusinessUnitPEO.xml`; full location and source revision retained in the external developer source register | Reviewed277-287: BuAltKeyByName unique metadata key consists of Name then EnterpriseId. Read-only FUN_ALL_BUSINESS_UNITS_V entity. BusinessUnitId is underlying PK. |
| SRC-GOLD-BU-VALUE | Reviewed source `BusinessUnitValueVO.xml`; full location and source revision retained in the external developer source register | Full223 lines read. SQL23 selects BU rows excluding ORG_ID already in IBY_INTERNAL_PAYERS_ALL with ORG_TYPE=OPERATING_UNIT. Used by OrgId list validation in task EO. FindByNameAndId criteria combines ID equality and name STARTSWITH. |
| SRC-GOLD-SETUP-SEED | Reviewed source `SetupBusinessObjectSD.xml`; full location and source revision retained in the external developer source register | Reviewed22871-22925: IBY_INTERNAL_PAYER service registration, IBY_PAYER.xml and /InternalPayerVO/InternalPayerVORow. BUSINESS_UNIT_NAME maps BuName, AlternateKeyFlag=Y, UpdateEnabledFlag=N. MandatoryFlag/default sources null. |
| SRC-REST-FIN-BU-26C | https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-finbusinessunitslov-get.html | GET /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV; q supports BusinessUnitName and BusinessUnitId. Returned fields include BusinessUnitName,BusinessUnitId,ActiveFlag; paginate using hasMore,limit,offset. ModuleIdFinder is documented but its exact mapping to this task's eligibility is not qualified. |

## Remaining questions

Full current lookup populations, label-to-code normalization/extensibility, changed-field behavior, creation requirements/defaults, new-BU eligibility, OrgType mutability, exact import-helper zero/many-match details and CSV lifecycle/delete support remain source-bounded gaps. They are neither proven invalid values nor unsupported product behavior. Automatic PPR report submission requires a valid nonblank format; an unrequested blank payment-approval flag is preserved. No public write API is inferred from VO/service metadata.

## SRC-E2E-M01-EXPORT-VISIBILITY-164877

The controlled native mixed import completed successfully but omitted its two expected named identities from a fresh task export. Source InternalPayerVO lines46–49 requires the named BU and PAYABLES_PAYMENT_BF usage joins. Read-only UI observations corroborated missing payment-function assignments. Developer-only diagnostics found both intended underlying rows with matching values and no usage matches; these diagnostics explain the discovery but do not qualify customer runtime reconciliation.

The product-semantic rule is filter-aware interpretation: missing export rows may exist, and no automatic create retry is justified. Payment usage is required for this named-row export visibility, not established as necessary for physical insertion. Preserve original failed comparisons, protected usage fields and separately authorized prerequisite setup. Database access is not an implementor dependency; no alternate SQL runtime verification is introduced.

## SRC-E2E-OBSERVED-AUTOPPR-164493-164510

Observed only: enterprise AutomaticPprReportSubmit Y -> N -> Y with PprReportFormat=PPR_STATUS_REPORT preserved, terminal success and fresh all-cell reconciliation (164493/164510; corroborated 164559/164580), release11.13.27.01.0. Other scopes, values and report formats remain unresolved. No create default, lookup-domain or new mutation authority follows. All four controlled processes reported53 processed,0 failed and0 warnings. Original and restored business values and all unrelated rows reconciled; permitted requested-row last-update audit deltas were disclosed. The recorded enterprise report format was preserved rather than invented. Sources: outputs/FINIBY-1910/merge-readiness-next/import-a01-terminal-result.json, outputs/FINIBY-1910/merge-readiness-next/import-a01-fresh-export-reconciliation.json, outputs/FINIBY-1910/merge-readiness-next/restoration-r01-fresh-export-reconciliation.json, outputs/FINIBY-1910/merge-readiness-next/live-enterprise-flag-evidence.json, outputs/FINIBY-1910/merge-readiness-next/bulk-b01-terminal-result.json, outputs/FINIBY-1910/merge-readiness-next/bulk-b01-fresh-export-reconciliation.json, outputs/FINIBY-1910/merge-readiness-next/bulk-restoration-br01-terminal-result.json, outputs/FINIBY-1910/merge-readiness-next/bulk-restoration-br01-fresh-export-reconciliation.json.

## SRC-E2E-OBSERVED-SUBJECT-164559-164580

Observed only: SraEmailSubject enterprise Automatic Separate Remittance Advice -> FSCR FINIBY-1910 validation -> original, and FGST-Auto Ltd / FGST-Service Ltd blank -> same requested subject -> blank, terminal success and fresh all-cell reconciliation (164559/164580), release11.13.27.01.0. Other subjects/scopes remain unresolved. Blank restoration is not a create default. Requests164559/164580 each completed53 rows with0 failures and0 warnings, followed by fresh exact-task exports300104798768016/300104798767189 and complete requested/preserved/unrelated comparisons. Sources: outputs/FINIBY-1910/merge-readiness-next/bulk-b01-terminal-result.json, outputs/FINIBY-1910/merge-readiness-next/bulk-b01-fresh-export-reconciliation.json, outputs/FINIBY-1910/merge-readiness-next/bulk-restoration-br01-terminal-result.json, outputs/FINIBY-1910/merge-readiness-next/bulk-restoration-br01-fresh-export-reconciliation.json, outputs/FINIBY-1910/merge-readiness-next/bulk-update-requests.json, outputs/FINIBY-1910/merge-readiness-next/bulk-restore-requests.json.

These are historical controlled results in the recorded target/release, not proof of every field value or current environment state. Other update contexts, lookups, create defaults, deletion and product maximum remain unresolved. Later exports do not erase the original create/mixed missing-identity FAIL or qualify unrelated operations. Every new reverse operation retains fresh evidence, confirmation and candidate approval.

## SRC-E2E-RETAINED-CREATE-55ROW-164877

Only the two recorded retained explicit-N creates are observed: terminal request164877 succeeded, while its original fresh-export comparison failed for hidden expected identities. Later export300104797771464 after separate user-completed prerequisite setup matched both creates and all1219cells of the previous53rows without reimport. c01 blank PaymentsApprovalFlag -> N remains an original FAIL with accepted retention, not a blank-create PASS or universal default. Supported final export SHA2562a1c0db649c3e25174b2c3d93cd3de2b37448dd1420bcc59b3f51f04719ac1bb, release11.13.27.01.0. No reimport was used for this later verification. Sources: outputs/FINIBY-1910/merge-readiness-next/anz-apac-m01-terminal-result.json, outputs/FINIBY-1910/merge-readiness-next/anz-apac-m01-fresh-export-reconciliation.json, outputs/FINIBY-1910/merge-readiness-next/after-payables-payment-enabled-fresh-export-verification.json, outputs/FINIBY-1910/merge-readiness-next/create-c01-outcome.md, outputs/FINIBY-1910/merge-readiness-next/create-c01-fresh-export-reconciliation.json.

## SRC-DEV-LOOKUP-SEEDS-20260924 / SRC-DEV-INTERNAL-PAYER-EO-LOOKUPS / SRC-DEV-INTERNAL-PAYER-EOIMPL-PPR

Read-only browser CodeSearch reviewed DEV StandardLookupTypeSD.xml, InternalPayerEO.xml and EOImpl.java, source /st_fusionapps_pt-v2mibfphdev/63 dated2026/09/24. Exact URLs, lines, seed labels/codes and filter predicates are retained in outputs/FINIBY-1910/merge-readiness-next/browser-lookup-source-findings.md. These are DEV source facts, not exact deployed revision or current lookup membership. BankChargeBearer is extensible; its IsActive filter is commented. No automatic normalization/closed-domain validator or endpoint has been added. Format codes, OrgType mutability and helper zero/multiple-match details remain gaps. DEV attributes not in the exact exported23-column schema remain excluded.
