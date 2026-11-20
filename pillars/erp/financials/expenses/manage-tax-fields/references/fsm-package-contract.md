# FSM package contract

Use a fresh same-task export and template through the routed export workflow. Preserve metadata, column order and package membership. This document describes observed structure; it is not a payload generator.

## EXM_CASH_ADV_SETUP_AND_POLICY.csv

```csv
BuName,OptionCode,ValueCode,CreationDate,CreatedBy,LastUpdateLogin,LastUpdateDate,LastUpdatedBy,OtherOrgId
```

## EXM_SETUP_OPTION.csv

```csv
BuName,OptionCode,ValueCode,CreationDate,CreatedBy,LastUpdateLogin,LastUpdateDate,LastUpdatedBy,OtherOrgId
```

## EXM_VAT_FIELD.csv

```csv
BuName,TerritoryCode,EnableMerchantNameCode,EnableMerchantReceiptCode,EnableMerchantTaxRegCode,EnableMerchantReferenceCode,EnableMerchantTaxpayerCode,EnableTaxClassificationCode,EnabledFlag,CreationDate,CreatedBy,LastUpdateDate,LastUpdatedBy,LastUpdateLogin
```

## ASM_SETUP_CSV_METADATA.xml

## Ownership and identity

- EXM_VAT_FIELD is the tax-rule target. The source entity alternate key is OrgId plus TerritoryCode; the FSM service resolves BuName in the current enterprise context before updating primary keys. Do not carry database IDs across environments.
- EXM_SETUP_OPTION contains the business-unit ENABLE_TAX switch. This task changes only ENABLE_TAX for explicitly selected business units. Other option codes are outside this task.
- EXM_CASH_ADV_SETUP_AND_POLICY is an observed alias sharing the setup-option service, XML file and node path. Its bytes matched EXM_SETUP_OPTION.csv in the collected exports (FSM-DUPLICATE-CHECK); recheck both complete aliases for each target. The former single-populated-member strategy is suspended for switch changes after a tester-reported zero-row SetupOption result. DOC-CSV-EMPTY-MEMBER does not resolve shared-alias conversion behavior. Follow [option-alias-qualification.md](option-alias-qualification.md) and the maintained profile: put identical minimal requested ENABLE_TAX rows in both aliases, using each member's exact header order. The normal route covers named-BU create-Y and the separately qualified combined N-to-Y update, each limited to its exact schema/release and operation shape. New Y switches plus new same-BU rules may use the documented switch-only then rule-only staged route, with a fresh reconciled baseline between stages and separate core approvals. This does not qualify a single combined-create import. Other switch operations require explicit nonproduction qualification. Never include unrelated baseline options in the delta, select a winning alias by name, or remove a member. Tax-rule-only candidates leave both aliases header-only.
- Audit columns are exported transport context, not business inputs. Preserve their headers and serialize empty cells for candidate rows under BUILDER-AUDIT-CONTRACT. Never fabricate or copy audit identities/timestamps into candidate rows. Retain original export bytes as baseline evidence. This defines adapter serialization, not proof of target runtime acceptance.
- OtherOrgId has special negative-ID fallback behavior in the shared import hook. Do not use that fallback to turn a business-unit request into global setup. Missing or unresolved BuName is a task issue.

## Field dispositions

| Fields | Meaning | Evidence boundary |
|---|---|---|
| BuName | Business-unit business key | Resolve in target enterprise; name alone across enterprises is insufficient |
| TerritoryCode | Country/territory or OTHER | Territory existence validator exempts literal OTHER; duplicate BU/territory is invalid |
| Six Enable*Code columns | Field behavior | DISABLED, ENABLED, REQUIRED; enabled EXM_FIELD_BEHAVIOUR lookup validates values |
| EnabledFlag | Tax-rule flag | Literal Y/N validation; not a substitute for the ENABLE_TAX setup option |
| OptionCode | Setup option identity | ENABLE_TAX for this task |
| ValueCode | Task switch | Y/N from task UI application-module logic; generic setup entity allows broader values |
| CreationDate, CreatedBy, LastUpdateDate, LastUpdatedBy, LastUpdateLogin | Audit context | Import VO marks these non-updateable; candidate cells are empty under BUILDER-AUDIT-CONTRACT; target audit generation remains subject to live reconciliation |
| OtherOrgId | Shared service transport fallback | Not an implementor tax-field control; retain source context pending verified candidate construction |

Create and update are the supported planning operations under this package contract; selected target executions are recorded in the dated [coverage summary](evidence.md#validation-coverage--2026-10-07), without complete E2E certification. Physical delete, implicit rename, blank-as-clear, and omission-as-default semantics are not established. Preserve supplied values and surface these gaps before preview or execution.
