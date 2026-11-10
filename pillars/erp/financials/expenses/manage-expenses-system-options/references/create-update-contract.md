# Sparse create and update contract

Business-unit existence and option configuration are separate questions.
Resolve a specific BU by one exact active BusinessUnitName/BusinessUnitId match
from `/fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV`, through the shared
REST client, core OAuth and REST-Framework-Version: 9. Retrieve all pages of
the exact-name filtered result, using core's escaped query handling. Never
infer a missing BU from its absence in an Expenses setup export.

Both validate and build-import accept `--reference-evidence FILE`. Its JSON
contains environment, baseline_process_id, captured_at (offset-aware, within
24 hours), path (the collection path above), http_status=200, complete=true,
and items. Only set complete after hasMore=false. Retain actual request/response
provenance privately in the project. Fail on zero or multiple exact active BU
matches, failed HTTP, incomplete pages, stale evidence or mismatched targets.
All Business Units is the source-defined global identity and needs no BU LOV.

Environment labels compare case-insensitively across the requested target,
metadata, archive prefix, validation result and reference evidence. Preserve
the original archive name and metadata bytes. Task names, process IDs, archive
suffixes and content hashes still require exact matches; do not trim or coerce
environment evidence to make it match.

Resolve workbook Create/Edit from a fresh completed EXPORT. For each supplied
setting, independently resolve `(BuName, OptionCode)` or `(BuName, SettingCode)`:

- One existing row: update its requested value, preserving other columns.
- No existing row: append a sparse row using the fresh export's ordered header.
  Do not copy another BU's IDs, audits, values or global settings.
- Multiple rows: stop for ambiguity.

The paired EXM_SETUP_OPTION and EXM_CASH_ADV_SETUP_AND_POLICY files must have
identical headers and selected rows. Both absent permits sparse insertion into
both. One absent and one present, divergent values, malformed CSV records or
duplicate identities blocks preparation. A new global row has blank BuName
and OtherOrgId=-1; a specific BU row has exact BuName, with OtherOrgId blank.

Confirmed scalar EXM_ORG_SETTING text, email and nonnegative-integer fields
use exact SettingCode and SettingValue, with SettingValueDecoded equal to the
plain scalar value. Preserve zero as a value. New rows leave audit cells blank.
Dynamic references and candidate/unmapped fields still need their own proven
resolver/mapping; create support never fabricates those contracts. Removing an
override to restore inheritance still requires a supported removal operation.

Blank workbook fields do not request an override or clearing. A BU can have
an Edit row while its selected option is newly created. A completed populated
data export with no configuration rows is a valid empty baseline; a template
export is not a data baseline. Metadata/process/archive checks still apply.

Build review-only packages, obtain core Data Loader/Task Hook validation and
exact-candidate approval, then submit once. Fresh-export reconciliation must
verify new overrides, values, and preservation separately from job acceptance.

## Selected-row submission and audit preservation

Both builder commands retain all four members, the exact fresh descriptor and
ordered headers. They submit only complete selected rows by BuName/code; CSVs
with no requested keys are header-only. Existing selected rows keep all non-input
cells. New rows follow the sparse-create contract. Both option aliases remain
identical; unrelated baseline rows are never replayed. The manifest records
selected/omitted counts and the candidate digest.

The prior full-baseline create/update regression retained business values but
changed last-update audits on an unrelated DFLT_CC_EXP_TEMPLATE_ID row. Those
strict failures remain historical evidence. The selected-row repair passed
48/48 create and 57/57 update checks, including every unrelated full row and
audit cell. See [bounded preservation evidence](selected-row-preservation.md).

`build-import` is the ordinary confirmed-mapping route using this profile.
`build-qualification` is the explicit nonproduction maintainer route and labels
its result qualification-only. Neither local result is a live success claim:
Task Hook, immutable approval and fresh-export reconciliation remain required.
The controlled evidence does not certify every field combination or global
setting. Do not remove aliases, manufacture metadata, clear unrelated audits,
bypass Task Hook or silently downgrade a preservation failure.

## Source evidence

CodeSearch series maintainer-reviewed source snapshot, reviewed 2026-10-21:

- `fusionapps/fin/components/payables/exm/setup/shared/model/src/oracle/apps/financials/expenses/setup/shared/expenseSetupOptionService/applicationModule/ExpenseSetupOptionServiceAMImpl.java`:
  BuName-to-BusinessUnitPVO mapping at 143–153, global OtherOrgId sentinel
  handling at 161–167, alternate-key update at 174, and MigratorHelper.readXML
  at 177 with create/update enabled.
- Sibling `expenseSetupOptionService/view/SetupOptionVO.xml` includes BuName;
  `setup/shared/model/entity/SetupOptionEO.xml` alternate key includes OrgId
  and OptionCode (409–414).
- Sibling `expenseOrgSettingService/applicationModule/ExpenseOrgSettingServiceAMImpl.java`:
  blank BU maps to OrgId=-1 at 177–179; template/account decoding is specific
  to those dynamic fields at 192 and 203; alternate-key processing/readXML
  at 215–219 enables create/update. The service AM declares OrgSettingVO and
  BusinessUnitPVO; its VO includes SettingValueDecoded at 148.
- Fresh 26.10 test exports corroborate both option headers, OtherOrgId and
  the OrgSetting header. This establishes source/package support, not a claim
  of successful live import or universal product acceptance.
- [Financials BU LOV](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-finbusinessunitslov-get.html).

Keep development-source evidence distinct from release-matched live results.
