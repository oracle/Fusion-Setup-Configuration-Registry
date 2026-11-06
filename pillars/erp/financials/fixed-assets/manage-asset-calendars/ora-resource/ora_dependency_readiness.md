# Manage Asset Calendars: Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Fiscal Year | Reuse a valid user-selected fiscal year unchanged. When no fiscal year is supplied, show every qualifying equivalent, including a sole candidate, and require the customer's exact selection or another exact Fiscal Year Name. If no equivalent exists, complete `FA_MANAGE_FISCAL_YEAR` creation or extension and confirm availability before calendar work. Its complete date rows establish the available Calendar coverage. |
| 2 | Technical import metadata | A current same-task FSM export must establish package members, fields, codes, and defaults. |
| 3 | Existing calendar state | The target calendar and its periods must be compared before creating setup data, using complete BOSS paging or the validated full FSM snapshot path in [Reference Lookups](ora_reference_lookups.md#complete-lookup-source-selection). |

## Calendar Export Contract

When a Calendar package is required, request **one current, unfiltered data**
`FA_MANAGE_CALENDAR` setup-data export after Fiscal Year validation and before
package generation. Do not request a template/spec export first and then a
second data export because a template has header-only contents. A successful
data export may legitimately contain zero Calendar parent and period rows;
validate it under Reference Lookups and accept it as empty Calendar setup.

Treat this export as an authorized prerequisite lookup, not as a separate
customer approval gate. When the active workflow has authorized the target
export, perform it without asking the customer to approve it again. Keep
endpoint names, HTTP methods, task payloads, CSV headers, and other technical
export mechanics internal.

This export rule does not replace the shared preview gates: retain the Input
Preview, Reference Validation Preview, Design Preview, Final ZIP Preview, and
the separate approval for submission of the exact immutable ZIP.

After Fiscal Year and complete existing-calendar validation, render the full
`Reference Validation Preview` in the active Manage Asset Calendars chat before
advancing to `CAL.APPLY_DEFAULTS` or requesting design approval. Then render
the full `Design Preview`, including every proposed calendar-period row and
date, in that chat before requesting approval to create the ZIP. Audit files,
file links, and summary tables do not satisfy either chat gate. If a preview
was omitted or shortened, render the missing complete preview before asking
for approval or preparing a package.

When BOSS returns 403 or `hasMore: true` on the initial collection page, use
a fresh Calendar data export as the complete
existing-state snapshot under [Complete Lookup Source
Selection](ora_reference_lookups.md#complete-lookup-source-selection). This
bulk-read use requires the Calendar parent and period members and does not
replace a separately required Fiscal Year export.
For a validated empty snapshot, mark the existing-calendar dependency satisfied
and retain the export process ID, target, archive SHA-256, successful status,
unfiltered data-export scope, validated headers, and parent/period row counts
(both zero). No override or seeded Calendar rows are required. Retain every
existing preview, ZIP creation, import approval, and post-import verification gate.

## Fiscal Year Creation Handoff

When the Fiscal Year lookup proves that no reusable exact equivalent exists,
the Manage Asset Calendars workflow invokes
`FA_MANAGE_FISCAL_YEAR` for the same target. The Calendar workflow must not
create or extend a Fiscal Year through its own package or import route.

Pass only the supplied Fiscal Year inputs and the Calendar coverage requirement
to the Fiscal Years workflow. Before the handoff, request any Fiscal Year name,
ledger or user-defined cycle, coverage, or Start Fiscal Year that is required
but absent; do not invent or default those business values. Several equivalent
Fiscal Years remain a Calendar selection decision and do not trigger creation.

The Fiscal Years workflow owns its validation, previews, approvals, immutable
package, submission handoff, and parent verification. Resume Calendar work only
after it returns the exact verified Fiscal Year Name and complete selected date
rows needed for the Calendar Start and End Basis. An accepted-but-unverified
Fiscal Year import, an incomplete lookup, a failed import, or a timed-out
process blocks Calendar ZIP preparation and import.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| fiscal_year | Fiscal year and Start Fiscal Year | Yes | Before calendar creation | Lookup | [Verified BOSS Request Contract](ora_reference_lookups.md#verified-boss-request-contract) | resolve_calendar_date_basis_from_fiscal_year | Reuse a valid user-selected fiscal year unchanged. Without a user selection, show every qualifying equivalent, including a sole candidate, and require the customer to select one exact Fiscal Year Name or provide another. The selected Start Fiscal Year must be an exact available row. If no fiscal year exists, create or extend it through `FA_MANAGE_FISCAL_YEAR`. | Validate and retain user selections. Present every qualifying equivalent with coverage and stop for the selection. Block an unavailable Start Fiscal Year row and request a valid row or fiscal-year extension. | Fiscal Year Name, Start Fiscal Year, selection source, equivalence result, exists/not-exists result, Calendar Start Basis, Calendar End Basis, and complete selected date rows |
| ledger_equivalent_fiscal_year | Equivalent ledger fiscal years | Conditional | Ledger-derived setup without a selected fiscal year | Lookup | Complete regular GL fiscal-year ranges and complete Fixed Assets fiscal-year rows | resolve_equivalent_fiscal_years_for_ledger | Establish every equivalent before customer selection. | Show all qualifying names with coverage; require customer selection even for one candidate. | Equivalent fiscal-year names and date rows |
| import_metadata | FSM import metadata | Yes | Before package generation | Lookup | One current unfiltered Manage Asset Calendars setup-data export, including a validated header-only data result | resolve_asset_calendar_export_metadata | Technical defaults must be proven before the first import attempt | Use the active workflow's authorized current setup-data export; do not request a template export or a separate customer approval | CSV members, columns, internal codes, date format, reserved fields |
| existing_calendar | Existing calendar and periods | Yes | Before design approval and create | Lookup | Complete BOSS result, or validated current unfiltered FA_MANAGE_CALENDAR data export when BOSS returns 403 or first reports hasMore=true | resolve_existing_asset_calendar | Prevent an unnecessary duplicate using complete existing-state evidence | A validated export with zero parent and period rows satisfies this check as empty Calendar setup. Otherwise compare exact-name and equivalent calendars and obtain any reuse-or-create decision. | Selected source, export process ID, target, SHA-256, status/scope, validated headers, parent/period row counts, exact-name and equivalence results, and any reuse-or-create decision |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Ready | All required evidence is current and unambiguous | Lookup yes; create only after approval |
| Technical lookup gap | A field, code, endpoint, or metadata value is not proven | Lookup yes; create no |
| Business decision | An existing exact-name calendar differs, or one or more configuration-equivalent calendars exist | Lookup yes; create no |
| Start-year confirmation | An existing fiscal year lacks the requested Start Fiscal Year row but has one or more nearest candidates | Lookup yes; create no until the user confirms one exact candidate |

## Ledger-Derived Customer Decision Gate

After the [ledger lookup gate](ora_reference_lookups.md#no-match-retry-and-multi-ledger-gate)
passes, use the single [Ledger-Derived Decision Prompt](ora_input_validation.md#ledger-derived-decision-prompt)
to present evidence and collect missing values. This gate owns readiness, not
another prompt: do not prepare a calendar package while any included ledger's
selected fiscal year or required name is unresolved. The selected fiscal year
determines the linked calendar coverage and first calendar-period start.

## Multi-Ledger Setup and Review Prerequisites

Prepare asset calendars only after every linked fiscal year is confirmed in the
target with the required date rows. Treat every ledger as an independent track;
a differing existing calendar is a business decision only for that track.

Before building a combined calendar ZIP, require all included tracks to have
the same target environment and current Manage Asset Calendars export contract.
The ZIP must not include fiscal-year objects.

Render the following calendar and period tables in the active Manage Asset
Calendars chat as the [Final ZIP Preview](../../SKILL.md#shared-fixed-assets-preview-and-approval-gates)
for every calendar in scope. This fulfills the parent's shared review gate; it
is not an additional preview or approval request, and it must not be collapsed
into a parent-only reference:

### Create Calendar — `<calendar name>`

| Field | Value |
|---|---|
| *Name | `<calendar name>` |
| Description | `<resolved description>` |
| *Fiscal Year Name | `<exact fiscal-year name>` |
| *Periods per Year | `<regular-period count>` |
| *Period Suffix | `<None, Calendar, or Fiscal>` |

| Period Name | Period Number | Start Date | End Date |
|---|---|---|---|
| `<period name>` | `<number>` | `<start>` | `<end>` |

Show the first 10 period rows and total row count when the table is longer.
State the ledger mapped to each calendar and archive totals for parent and
period rows. The review must match the immutable archive. Follow the parent's
shared gates for design approval before ZIP creation. For submission, use the
single approval under [Data Loader](../../../../../../core/data-loader/SKILL.md#execute-a-data-loading-request)
for that exact artifact and target; it satisfies the parent's execution gate,
and Task Hook records the same approval rather than asking again.

## Bulk Packaging and Review

Apply [Multi-Ledger Setup and Review Prerequisites](#multi-ledger-setup-and-review-prerequisites)
to each batch. Begin batching only after the matching fiscal-year batch has a
confirmed target-state result. Select the batch size from proven import payload
limits; do not invent a fixed limit such as 100 or 1,000.

Persist a batch manifest that maps each input row to its calendar key,
fiscal-year dependency, archive, and validation/existing-state outcome. Add one
summary row per calendar to the shared ZIP review. For large batches, retain
the full parent and period-row review as a durable tabular artifact, link it
from the summary, and use the preview row limit above. Apply the submission
approval separately to each immutable archive; approval for one batch does not
approve another.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CAL.RESOLVE_DEPENDENCIES | decision | 20 | resolve_dependency | ready->CAL.LOOKUP_EXISTING;blocked->CAL.HANDLE_DEPENDENCY | CAL.VALIDATE_INPUT | stop | Valid input |
