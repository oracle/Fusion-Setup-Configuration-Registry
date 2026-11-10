# Nullable conversion policy values

The frontend has no blanket requirement for populated tolerance percentages.
WarningTolerance and ErrorTolerance are optional on both parent and currency
rows. A single percentage is permitted; compare ErrorTolerance > WarningTolerance
only when both merged values are populated. The numeric preparation policy
still rejects nonfinite, nonnumeric and negative supplied values.

On updates, blank workbook cells retain the exact baseline value, including a
blank baseline value. Carried sibling rows may retain blank tolerances too.
On creates, omitted optional values serialize as empty cells; no zero or other
default is invented. Parent Display Warning to User is nullable; a supplied
flag must be Y/N. Default Conversion Rate remains required for both entities;
child Display Warning to User remains required. Required identities and the
parent conversion type remain required. A new currency identity with all four
settings blank is still a no-override request and is omitted.

This is not an instruction to clear an existing setting. Clearing Warning in
the UI clears/disables Display Warning; do not silently change an imported
flag or use this UI event handler as proof of import-side behavior. Preserve
existing values and resolve contradictory requested flags through normal
task review. All candidates still require normal references, preflight,
Task Hook and exact-artifact approval before import.

## Source evidence

CodeSearch MCP, maintainer-reviewed source snapshot, reviewed 2026-10-21:

- `fusionapps/fin/components/payables/exm/policy/exchangeRate/ui/public_html/oracle/apps/financials/expenses/policy/exchangeRate/ui/page/ManageExchangeRate.jsff`:
  parent percentage required attributes inherit hints at 286/313, child at
  454/486. Child Currency is explicitly required at 415. Checkboxes at
  275/299 and 441/470 do not establish percentage requiredness. Warning
  change handlers are bound at 289/459.
- `fusionapps/fin/components/payables/exm/policy/shared/model/src/oracle/apps/financials/expenses/policy/shared/model/entity/ExchangeRateOptionEO.xml`:
  Default flag is IsNotNull at 140; Error/Warning attributes at 183/220 have
  no IsNotNull requirement. Comparisons run only for nonnull pairs at
  204/211 and 241/248. Parent Display flag at 257 is nullable.
- Sibling `ExchangeRateToleranceEO.xml`: Default and Display flags are
  IsNotNull at 120/237; Error/Warning attributes at 163/200 are nullable.
  Comparisons are conditional on nonnull pairs at 184/191 and 221/228.
- UI ExchRateOptionVO Error/Warning attributes at 103–112 and child
  ExchRateToleranceVO at 150–165 do not override percentage nullability.

Existing controlled evidence in remaining-contracts.md independently records
successful raw blank tolerances and parent display clearing. No new live
import or create-with-null result is claimed by this source review.
