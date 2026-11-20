# Corporate Card Program FSM Structure

Supported structural inventory: see `package-headers.json`. This is structural evidence, not a reusable customer-data package or proof of operation semantics. For every load, bind the selected environment’s actual template, preserve its XML metadata and ordered headers, and validate task identity before generating rows. The template has six CSV members and 174 physical columns (165 entity fields plus nine repeated parent-link columns).

## Seed mappings

| CSV object | XML file | XML row path |
|---|---|---|
| EXM_CARD_DOWNLOAD_PARAM | EXM_CARD_PROGRAMS.xml | `/CardProgramVO/CardProgramVORow/CardDownloadParameter/CardDownloadParameterVORow` |
| EXM_CARD_PROGRAM | EXM_CARD_PROGRAMS.xml | `/CardProgramVO/CardProgramVORow` |
| EXM_CARD_UPLOAD_RULE | EXM_CARD_PROGRAMS.xml | `/CardProgramVO/CardProgramVORow/CardUploadRule/CardUploadRuleVORow` |
| EXM_CC_COMPANY_ACCOUNT | EXM_CARD_PROGRAMS.xml | `/CardProgramVO/CardProgramVORow/CardCompanyAccount/CardCompanyAccountVORow` |
| EXM_CORPORATE_CARD_ISSUER | EXM_SETUP_PARTY_REFERENCE.xml | `/SetupPartyReferenceVO/SetupPartyReferenceVORow` |
| ORA_EXM_SETUP_PARTY_REFERENCE | EXM_SETUP_PARTY_REFERENCE.xml | `/SetupPartyReferenceVO/SetupPartyReferenceVORow` |

The task seed directly enables program, upload rule, download parameter, company account and ORA_EXM_SETUP_PARTY_REFERENCE. The observed template additionally includes EXM_CORPORATE_CARD_ISSUER. Both party objects map to the same XML row path; this does not authorize duplicating party rows across the two CSV members. Preserve all template members and leave party creation out of scope until ownership and intended mutations are qualified.

Company-account and upload/download parent references use FSMCardProgramName and reference EXM_CARD_PROGRAM.CARD_PROGRAM_NAME. Seed alternate-key flags and CSV parent-prefix columns are not substitutes for the importer VO/EO key definitions.

Sources: task membership (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/fun/db/data/FinFunShared/SetupTaskBusinessObjectSD.xml:2434`), company-account mapping (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/fun/db/data/FinFunShared/SetupBusinessObjectSD.xml:13883`), reference binding (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/fun/db/data/FinFunShared/SetupBOReferenceAttributeSD.xml:3306`), issuer mapping (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/fun/db/data/FinFunShared/SetupBusinessObjectSD.xml:13995`), shared party mapping (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/fun/db/data/FinFunShared/SetupBusinessObjectSD.xml:37241`).

## Ordered template headers

### EXM_CARD_PROGRAM.csv

```text
CardProgramName,CardTypeLookupCode,CardBrandLookupCode,Description,InactiveDate,EnableCcTokenFlag,AttributeCategory,Attribute1,Attribute2,Attribute3,Attribute4,Attribute5,Attribute6,Attribute7,Attribute8,Attribute9,Attribute10,Attribute11,Attribute12,Attribute13,Attribute14,Attribute15,CreationDate,CreatedBy,LastUpdateDate,LastUpdatedBy,LastUpdateLogin
```

### EXM_CARD_DOWNLOAD_PARAM.csv

```text
EXM_CARD_PROGRAM.CardProgramName,EXM_CARD_PROGRAM.CardTypeLookupCode,EXM_CARD_PROGRAM.CardBrandLookupCode,DownloadProfileName,Username,EncryptedPassword,RemoteFilename,Server,SecureDirectory,CreationDate,CreatedBy,LastUpdateDate,LastUpdatedBy,LastUpdateLogin,PgpEncryptionAlias,PgpSignatureAlias
```

### EXM_CARD_UPLOAD_RULE.csv

```text
EXM_CARD_PROGRAM.CardProgramName,EXM_CARD_PROGRAM.CardTypeLookupCode,EXM_CARD_PROGRAM.CardBrandLookupCode,FileFormatCode,CcExpTypSumSourceCol,MapTypeCode,DetailWaitingDuration,CardEmpMatchingRule,CcExpTypDtlSourceCol,MatchEmployeeAcrossBu,CreationDate,CreatedBy,LastUpdateDate,LastUpdatedBy,LastUpdateLogin,MapTypeCode1
```

### EXM_CC_COMPANY_ACCOUNT.csv

```text
EXM_CARD_PROGRAM.CardProgramName,EXM_CARD_PROGRAM.CardTypeLookupCode,EXM_CARD_PROGRAM.CardBrandLookupCode,CompanyAccountName,PaymentTermName,PayablesBUName,CardIssuerName,CardIssuerSiteName,MarketCode,CompanyNumber,BillingCntlAcctNumber,CardAdminName,CardIssuerNumber,CreatedBy,CreationDate,InactiveDate,InclPersonalExpenseFlag,InterbankCardassocNumber,LastUpdateDate,LastUpdateLogin,LastUpdatedBy,OverlayBalancingSegFlag,PaymentCurrencyCode,PaymentDueFromCode,SysDate,BuName,Address1,Address2,Address3,Address4,City,Country,State,Province,PostalCode,Name,PartyNumber,ExpenseCcidSegments,PersonNumber,PayGroupCode,BookNumber,LoadNumber,CardDisguiseCtrlAcctNum,TerritoryCode,MultiCurrencyEnabled
```

### EXM_CORPORATE_CARD_ISSUER.csv

```text
PartyName,PartyNumber,PartySiteName,PartySiteNumber,PartyType,PartyUniqueName,Status,EffectiveEndDate,EffectiveStartDate,PartyUsageCode,StatusFlag,Address1,Address2,Address3,Address4,Country,County,City,Building,Province,PostalCode,State,StatusFlag1,ValidatedFlag,PartyUsageCode1,CreatedByModule,CreatedByModule1,CreatedByModule2,CreatedByModule3,ProfileOptionValue,LevelName,LevelValue,ProfileOptionValue1,LevelName1,LevelValue1
```

### ORA_EXM_SETUP_PARTY_REFERENCE.csv

```text
PartyName,PartyNumber,PartySiteName,PartySiteNumber,PartyType,PartyUniqueName,Status,EffectiveEndDate,EffectiveStartDate,PartyUsageCode,StatusFlag,Address1,Address2,Address3,Address4,Country,County,City,Building,Province,PostalCode,State,StatusFlag1,ValidatedFlag,PartyUsageCode1,CreatedByModule,CreatedByModule1,CreatedByModule2,CreatedByModule3,ProfileOptionValue,LevelName,LevelValue,ProfileOptionValue1,LevelName1,LevelValue1
```


## Company-account identity and site selection

The FSM service CardCompanyAccountVO.xml ViewKey AltKey (lines 585-595)
references CardCompanyAccountAltKey. CardCompanyAccountEO.xml lines 866-898
resolve that to CardProgramId, CompanyAccountName, CardIssuerNumber,
InterbankCardassocNumber, BillingCntlAcctNumber and MarketCode. CompanyNumber
is required business data, not a member of this key. Do not collapse company
identity to company name or substitute the three parent-reference CSV columns
for this entity key. The helper's treatment of missing key values still needs
qualification before claiming an executable create/update contract.

PartySiteVVO.xml selects HZ_PARTY_SITES joined to HZ_LOCATIONS; the applied
PartySiteVC_PartyID criterion filters only PartyId (lines 624-661). It has no
site-name, address or active-status predicate. Combined with service AMImpl
lines 719-783, a company-account import with an existing issuer can choose the
first site for that party. An export containing one active site does not prove
there are no inactive/other sites in this resolver's result. Before executing,
require qualified complete party-site cardinality evidence or a corrected
supported importer contract. Do not claim CardIssuerSiteName ensures selection.

Sources: company service VO (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/view/CardCompanyAccountVO.xml:585`),
party-site resolver (`SOURCE-SNAPSHOT-a832b44f25f2/fusionapps/fin/components/payables/exm/creditCard/shared/publicModel/src/oracle/apps/financials/expenses/creditCard/shared/corporateCardProgramService/view/PartySiteVVO.xml:624`).

## Existing issuer and site: package disposition

For program CREATE using an existing issuer and site, retain both
`EXM_CORPORATE_CARD_ISSUER.csv` and `ORA_EXM_SETUP_PARTY_REFERENCE.csv` with
exact template headers and no data rows. Do not copy issuer-export rows into
these members. Company PartyNumber and address references are resolved by the
company importer independently; apply the qualified single-site preflight.
Keep an unused download-parameter CSV header-only as well. Never delete a member.

This follows [Oracle 26D FSM instructions](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/export-and-import-csv-file-packages.html)
and the task importer lines 693-783. It resolves unused-member disposition only.
It does not qualify empty cells inside populated rows or new issuer/site setup.
