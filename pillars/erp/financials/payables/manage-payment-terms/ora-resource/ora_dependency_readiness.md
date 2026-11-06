# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Payables calendar | Run the conditional read-only validation for a supplied Calendar before submission when the endpoint is available |
| 2 | Reference data set | Check an explicit Set Code, or resolve a Set Name/unspecified set to one code, before building the package |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| DEP-CALENDAR | Payables calendar | Conditional | AP_TERM_LINE.Calendar is supplied | Conditional blocker | Payables Calendar Types REST collection; query uses the supplied Calendar and `PAYMENT TERMS` predicate | validate_payables_calendar | The documented endpoint corroborates an already supplied value | One or more rows corroborate only. Zero rows block as `not_found`; malformed/unexpected responses block as `resolver_failure`. HTTP 400 is advisory; 401/403/network/timeout/5xx are `validation_skipped`. | Calendar |
| DEP-SET-CODE | Payables Payment Terms reference data set | Conditional | AP_TERM_SUBSCRIPTION.SetCode is supplied | Conditional blocker | Set ID Sets LOV REST collection | validate_set_code | A code is checked; a name or unspecified set must be turned into one code | Follow ora_reference_lookups.md. No matches or unclear results stop processing. Only explicit codes may continue after an unavailable check. | SetCode |
| DEP-SET-REFERENCE | Payables Payment Terms reference data set | Conditional | A set name or unspecified set is supplied | Conditional blocker | Set ID Sets LOV REST collection | resolve_set_reference | A code is checked; a name or unspecified set must be turned into one code | Follow ora_reference_lookups.md. No matches or unclear results stop processing. Only explicit codes may continue after an unavailable check. | SetCode |

## What These Statuses Mean

| Status | Plain Meaning | What Happens Next |
|---|---|---|
| Conditional blocker | Run the declared check when its value is supplied. No matches or malformed results stop processing. Only a check of an already supplied Set Code or Calendar may be skipped when unavailable. A Set Name or unspecified set must resolve completely to one distinct SetCode; it cannot use this exception. | Correct a blocking value or response issue before candidate generation. For an advisory/unavailable result, preserve the value and evidence; Fusion remains authoritative during approved import. |

## Set Name Needs a Code

A name or unspecified set needs a complete lookup before we can build a ZIP.
Read [Reference Lookups](ora_reference_lookups.md). One distinct returned code
is required; missing, multiple, or unavailable results stop processing. Only
an already supplied Set Code can use the skipped-check rule when access fails.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DEP.CHECK | step | 20 | resolve_dependency | success->LOOKUP.CALENDAR;advisory-unavailable->LOOKUP.CALENDAR | INPUT.VALIDATE | stop | Always |

## Installment for a New Payment Term

A new payment-term header requires at least one explicitly requested installment
for that header in the same ZIP. Check this locally before preview or package
generation. A set assignment or translation cannot replace it, and disabling
the new term does not remove the requirement. Stop with `AP_AT_LEAST_ONE_CHILD`
and ask for installment details; do not create a placeholder line.

For an existing payment term, preserve its baseline installments. A header
update or child create/update does not require an additional installment.
