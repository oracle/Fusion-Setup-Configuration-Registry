# Input Validation

A blank Resolver means the check runs locally against the documented task
contract, candidate package, or fresh baseline; it requires no reference lookup.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_TERM_HEADER::Name, AP_TERM_HEADER::EnabledFlag, AP_TERM_HEADER::DueCutoffDay, AP_TERM_HEADER::Type, AP_TERM_HEADER::StartDateActive, AP_TERM_HEADER::EndDateActive, AP_TERM_HEADER::Rank, AP_TERM_HEADER::AttributeCategory, AP_TERM_HEADER::Attribute1, AP_TERM_HEADER::Attribute2, AP_TERM_HEADER::Attribute3, AP_TERM_HEADER::Attribute4, AP_TERM_HEADER::Attribute5, AP_TERM_HEADER::Attribute6, AP_TERM_HEADER::Attribute7, AP_TERM_HEADER::Attribute8, AP_TERM_HEADER::Attribute9, AP_TERM_HEADER::Attribute10, AP_TERM_HEADER::Attribute11, AP_TERM_HEADER::Attribute12, AP_TERM_HEADER::Attribute13, AP_TERM_HEADER::Attribute14, AP_TERM_HEADER::Attribute15, AP_TERM_HEADER::Description, AP_TERM_HEADER::GlobalAttributeCategory, AP_TERM_HEADER::GlobalAttribute1, AP_TERM_HEADER::GlobalAttribute2, AP_TERM_HEADER::GlobalAttribute3, AP_TERM_HEADER::GlobalAttribute4, AP_TERM_HEADER::GlobalAttribute5, AP_TERM_HEADER::GlobalAttribute6, AP_TERM_HEADER::GlobalAttribute7, AP_TERM_HEADER::GlobalAttribute8, AP_TERM_HEADER::GlobalAttribute9, AP_TERM_HEADER::GlobalAttribute10, AP_TERM_HEADER::GlobalAttribute11, AP_TERM_HEADER::GlobalAttribute12, AP_TERM_HEADER::GlobalAttribute13, AP_TERM_HEADER::GlobalAttribute14, AP_TERM_HEADER::GlobalAttribute15, AP_TERM_HEADER::GlobalAttribute16, AP_TERM_HEADER::GlobalAttribute17, AP_TERM_HEADER::GlobalAttribute18, AP_TERM_HEADER::GlobalAttribute19, AP_TERM_HEADER::GlobalAttribute20, AP_TERM_HEADER::GlobalAttributeDate1, AP_TERM_HEADER::GlobalAttributeDate2, AP_TERM_HEADER::GlobalAttributeDate3, AP_TERM_HEADER::GlobalAttributeDate4, AP_TERM_HEADER::GlobalAttributeDate5, AP_TERM_HEADER::GlobalAttributeNumber1, AP_TERM_HEADER::GlobalAttributeNumber2, AP_TERM_HEADER::GlobalAttributeNumber3, AP_TERM_HEADER::GlobalAttributeNumber4, AP_TERM_HEADER::GlobalAttributeNumber5, AP_TERM_LINE::AP_TERM_HEADER.Name, AP_TERM_LINE::SequenceNum, AP_TERM_LINE::DuePercent, AP_TERM_LINE::DueAmount, AP_TERM_LINE::DueDays, AP_TERM_LINE::DueDayOfMonth, AP_TERM_LINE::DueMonthsForward, AP_TERM_LINE::DiscountPercent, AP_TERM_LINE::DiscountDays, AP_TERM_LINE::DiscountDayOfMonth, AP_TERM_LINE::DiscountMonthsForward, AP_TERM_LINE::DiscountPercent2, AP_TERM_LINE::DiscountDays2, AP_TERM_LINE::DiscountDayOfMonth2, AP_TERM_LINE::DiscountMonthsForward2, AP_TERM_LINE::DiscountPercent3, AP_TERM_LINE::DiscountDays3, AP_TERM_LINE::DiscountDayOfMonth3, AP_TERM_LINE::DiscountMonthsForward3, AP_TERM_LINE::AttributeCategory, AP_TERM_LINE::Attribute1, AP_TERM_LINE::Attribute2, AP_TERM_LINE::Attribute3, AP_TERM_LINE::Attribute4, AP_TERM_LINE::Attribute5, AP_TERM_LINE::Attribute6, AP_TERM_LINE::Attribute7, AP_TERM_LINE::Attribute8, AP_TERM_LINE::Attribute9, AP_TERM_LINE::Attribute10, AP_TERM_LINE::Attribute11, AP_TERM_LINE::Attribute12, AP_TERM_LINE::Attribute13, AP_TERM_LINE::Attribute14, AP_TERM_LINE::Attribute15, AP_TERM_LINE::FixedDate, AP_TERM_LINE::Calendar, AP_TERM_SUBSCRIPTION::AP_TERM_HEADER.Name, AP_TERM_SUBSCRIPTION::SetCode, AP_TERM_HEADER_TRANSLATION::AP_TERM_HEADER.Name, AP_TERM_HEADER_TRANSLATION::Name, AP_TERM_HEADER_TRANSLATION::Description, AP_TERM_HEADER_TRANSLATION::Language, AP_TERM_HEADER_TRANSLATION::SourceLang -->
<!-- fscr-update-fields: AP_TERM_HEADER::EnabledFlag, AP_TERM_HEADER::DueCutoffDay, AP_TERM_HEADER::Type, AP_TERM_HEADER::StartDateActive, AP_TERM_HEADER::EndDateActive, AP_TERM_HEADER::Rank, AP_TERM_HEADER::AttributeCategory, AP_TERM_HEADER::Attribute1, AP_TERM_HEADER::Attribute2, AP_TERM_HEADER::Attribute3, AP_TERM_HEADER::Attribute4, AP_TERM_HEADER::Attribute5, AP_TERM_HEADER::Attribute6, AP_TERM_HEADER::Attribute7, AP_TERM_HEADER::Attribute8, AP_TERM_HEADER::Attribute9, AP_TERM_HEADER::Attribute10, AP_TERM_HEADER::Attribute11, AP_TERM_HEADER::Attribute12, AP_TERM_HEADER::Attribute13, AP_TERM_HEADER::Attribute14, AP_TERM_HEADER::Attribute15, AP_TERM_HEADER::Description, AP_TERM_HEADER::GlobalAttributeCategory, AP_TERM_HEADER::GlobalAttribute1, AP_TERM_HEADER::GlobalAttribute2, AP_TERM_HEADER::GlobalAttribute3, AP_TERM_HEADER::GlobalAttribute4, AP_TERM_HEADER::GlobalAttribute5, AP_TERM_HEADER::GlobalAttribute6, AP_TERM_HEADER::GlobalAttribute7, AP_TERM_HEADER::GlobalAttribute8, AP_TERM_HEADER::GlobalAttribute9, AP_TERM_HEADER::GlobalAttribute10, AP_TERM_HEADER::GlobalAttribute11, AP_TERM_HEADER::GlobalAttribute12, AP_TERM_HEADER::GlobalAttribute13, AP_TERM_HEADER::GlobalAttribute14, AP_TERM_HEADER::GlobalAttribute15, AP_TERM_HEADER::GlobalAttribute16, AP_TERM_HEADER::GlobalAttribute17, AP_TERM_HEADER::GlobalAttribute18, AP_TERM_HEADER::GlobalAttribute19, AP_TERM_HEADER::GlobalAttribute20, AP_TERM_HEADER::GlobalAttributeDate1, AP_TERM_HEADER::GlobalAttributeDate2, AP_TERM_HEADER::GlobalAttributeDate3, AP_TERM_HEADER::GlobalAttributeDate4, AP_TERM_HEADER::GlobalAttributeDate5, AP_TERM_HEADER::GlobalAttributeNumber1, AP_TERM_HEADER::GlobalAttributeNumber2, AP_TERM_HEADER::GlobalAttributeNumber3, AP_TERM_HEADER::GlobalAttributeNumber4, AP_TERM_HEADER::GlobalAttributeNumber5, AP_TERM_LINE::DuePercent, AP_TERM_LINE::DueAmount, AP_TERM_LINE::DueDays, AP_TERM_LINE::DueDayOfMonth, AP_TERM_LINE::DueMonthsForward, AP_TERM_LINE::DiscountPercent, AP_TERM_LINE::DiscountDays, AP_TERM_LINE::DiscountDayOfMonth, AP_TERM_LINE::DiscountMonthsForward, AP_TERM_LINE::DiscountPercent2, AP_TERM_LINE::DiscountDays2, AP_TERM_LINE::DiscountDayOfMonth2, AP_TERM_LINE::DiscountMonthsForward2, AP_TERM_LINE::DiscountPercent3, AP_TERM_LINE::DiscountDays3, AP_TERM_LINE::DiscountDayOfMonth3, AP_TERM_LINE::DiscountMonthsForward3, AP_TERM_LINE::AttributeCategory, AP_TERM_LINE::Attribute1, AP_TERM_LINE::Attribute2, AP_TERM_LINE::Attribute3, AP_TERM_LINE::Attribute4, AP_TERM_LINE::Attribute5, AP_TERM_LINE::Attribute6, AP_TERM_LINE::Attribute7, AP_TERM_LINE::Attribute8, AP_TERM_LINE::Attribute9, AP_TERM_LINE::Attribute10, AP_TERM_LINE::Attribute11, AP_TERM_LINE::Attribute12, AP_TERM_LINE::Attribute13, AP_TERM_LINE::Attribute14, AP_TERM_LINE::Attribute15, AP_TERM_LINE::FixedDate, AP_TERM_LINE::Calendar, AP_TERM_HEADER_TRANSLATION::Name, AP_TERM_HEADER_TRANSLATION::Description, AP_TERM_HEADER_TRANSLATION::SourceLang -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Payment-term identity | Header name and source package identity | Block preview | Provide the exact FSM package fields | Always | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Package structure | Preserve the four evidenced CSV entities and metadata hierarchy | Always | |
| CSV header fidelity | Use each exact header from the same-task CSV Template Report; reject duplicate, renamed, reordered, added, or omitted columns | Always | |
| CSV row width | Every nonempty data row must contain exactly the number of fields in its entity header; serialize unset trailing values as explicit empty CSV cells | Always | |
| Child parent support | For every `AP_TERM_LINE`, `AP_TERM_SUBSCRIPTION`, or `AP_TERM_HEADER_TRANSLATION` create or update, include its matching `AP_TERM_HEADER` row in the same archive. Unless an explicit header operation supplies it, copy the parent unchanged from the fresh baseline with all audit fields blank, once per parent. Reject a missing parent, changed supporting business values, or populated audit fields. Block generation when neither the explicit operations nor the baseline supplies the parent. | Child create or update | |
| Payment-term type | Require `AP_TERM_HEADER.Type=STD` whenever Type is supplied; for a new header, default an omitted or blank Type to `STD`. Reject every other explicit value before ZIP generation. | AP_TERM_HEADER create or update | |
| New payment-term installment | Every new header requires at least one explicitly requested `AP_TERM_LINE` create for the same header in the package, even when `EnabledFlag=N`. Subscriptions and translations do not count. Reject with `AP_AT_LEAST_ONE_CHILD` before preview/ZIP generation and ask for installment details. Do not invent a line or require an extra line for an existing-header update or child change. | AP_TERM_HEADER create | |
| Required payment-term header values | For a new AP_TERM_HEADER, serialize `EnabledFlag=Y`, `Type=STD`, and `StartDateActive=<package-builder system date in YYYY/MM/DD>` when the request omits or leaves the corresponding value blank; never serialize these defaulted fields as blank | Create | |
| Active dates | Require supported Gregorian calendar dates. When both dates are effective, `EndDateActive` must be on or after `StartDateActive`. | AP_TERM_HEADER create or update | |
| Rank | When supplied, require a whole numeric value with at most 18 digits. Compare its numeric value globally across all Payment Terms in the fresh export plus the requested changes and reject duplicates. Negative values are not rejected merely for being negative; no documented positive/minimum constraint is declared. | AP_TERM_HEADER create or update | |
| Due basis | Require exactly one of `DuePercent` or `DueAmount` on every effective line. Reject negative amounts and percentages outside 0 through 100. | AP_TERM_LINE create or update | |
| Due-date method | Require exactly one complete method: nonnegative `DueDays`; `DueDayOfMonth` from 1 through 31 together with nonnegative `DueMonthsForward`; `FixedDate`; or `Calendar`. Reject either day/month component without the other and reject mixed methods. | AP_TERM_LINE create or update | |
| Cross-line due basis | Do not mix percentage-based and amount-based rows for one payment term. Percentage lines must total exactly 100. Amount lines must include at least one explicit `DueAmount=0` line. | AP_TERM_LINE create or update | |
| Discount completeness and ranges | For each discount tier, require `DiscountPercent` and exactly one complete discount date method. Percentage must be greater than 0 and at most 100; days and months-forward must be nonnegative; day-of-month must be 1 through 31 and paired with months-forward. | AP_TERM_LINE create or update | |
| Discount ordering | A second tier requires the first and a third requires the first two. Later discount dates must be later and later discount percentages must be lower. | AP_TERM_LINE create or update | |

## Set Input

Accept a code, a name, or an unspecified set using `setReference` as described
in [Reference Lookups](ora_reference_lookups.md). Before package generation,
require one resolved `SetCode` for names and unspecified sets. Stop if the
lookup has no match, is unclear, cannot finish, or conflicts with a supplied
code. Never serialize a Set Name or `setReference` as a CSV column. Keep the
original wording and resolved code visible in the preview.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INPUT.VALIDATE | step | 10 | validate_input | success->DEP.CHECK | none | stop | Always |

## Clearing Optional Values in Uploaded ZIPs

For an existing record, compare each business field with the fresh baseline,
including blank cells. A populated description changed to blank is a requested
clear and must pass the same checks as a description cleared through NLP input.
Keep required-field checks in place. Blank optional cells on new records do not
count as supplied values, and an unchanged parent header remains supporting data.

## Update preservation

For updates, `preserveOtherValues` must be `true` or omitted (defaults to `true`). Explicit `false` and nonboolean values are rejected before candidate preparation or validation. Omitted fields retain their baseline values.
