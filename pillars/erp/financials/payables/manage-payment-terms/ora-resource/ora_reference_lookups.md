# Reference Lookups

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| validate_payables_calendar | AP_TERM_LINE.Calendar is supplied | Calendar | /fscmRestApi/resources/11.13.18.05/payablesCalendarTypes?onlyData=true&fields=calendarName,calendarType&q=calendarName='{Calendar}' and calendarType='PAYMENT TERMS' | calendarName, calendarType | One or more rows corroborate the supplied value only; do not select a row or claim uniqueness. | Submitted Calendar; returned values are corroborating evidence only. | Zero rows are `not_found` and block ZIP/import. Malformed or unexpected responses are `resolver_failure` and block. HTTP 400 is advisory; 401/403/network/timeout/5xx are unavailable/skipped. |
| validate_set_code | AP_TERM_SUBSCRIPTION.SetCode key is supplied | SetCode from the subscription alternate key | /fscmRestApi/resources/11.13.18.05/setIdSetsLOV?onlyData=true&fields=SetCode,SetName,Description&q=SetCode='{SetCode}' | SetCode, SetName, Description | One or more rows corroborate the supplied value only; do not select a row or claim uniqueness. | Submitted SetCode; returned values are corroborating evidence only. | Zero rows are `not_found` and block ZIP/import. Malformed or unexpected responses are `resolver_failure` and block. HTTP 400 is advisory; 401/403/network/timeout/5xx are unavailable/skipped. |
| resolve_set_reference | A Set Name or unspecified set is supplied | The supplied set value and whether the user called it a code, a name, or just a set | Same setIdSetsLOV endpoint; query SetName for names, and both SetCode and SetName for unspecified input, as described below | SetCode, SetName, Description | Read all pages and require exactly one distinct SetCode across the applicable searches. | Set Code for the assignment CSV, and lookup details for the preview | No matches, multiple distinct codes, malformed responses, or any unfinished search stop processing. Ask for a code or a user selection; never skip a lookup that must derive the code. |

## Set Code and Set Name Input

The CSV always needs `AP_TERM_SUBSCRIPTION.SetCode`. A Set Name is not a CSV field.
Use these rules when turning the user's request into a design:

| What the user supplies | Search | What happens next |
|---|---|---|
| Explicit Set Code | `SetCode='{value}'` | Keep the supplied code unchanged. One or more readable rows allow processing; no rows stop it. |
| Explicit Set Name | `SetName='{value}'` | Read all pages. One distinct SetCode is used; more than one asks the user to choose; no rows stop it. |
| "Set" without saying code or name | Search `SetCode` and `SetName` separately | Read all pages from both searches. Combine results by exact SetCode. One distinct code is used; more than one asks the user to choose; no rows stop it. |

All searches use `/fscmRestApi/resources/11.13.18.05/setIdSetsLOV`,
`onlyData=true`, and `fields=SetCode,SetName,Description`. Follow `hasMore`
before deciding that a name or unspecified set has only one match. Keep code
case and spacing as returned; codes that differ in case are separate candidates.
Escape single quotes inside query values. Do not use partial or fuzzy matches.

For example:

- “Assign `<payment term>` to Set Code `<set code>`”: check that exact code.
- “Assign `<payment term>` to the set named `<set name>`”: search by Set Name
  and use the matching Set Code.
- “Assign `<payment term>` to set `<set value>`”: search both Set Code and
  Set Name because the user has not said which one they supplied.

Keep the user's supplied value unchanged during the lookup. Do not decide
whether it is a code or name from its spelling, capitalization, or spaces.
Use the resolved Set Code in the assignment CSV. Show the supplied value,
matching Set Name, Set Code, and lookup status in the preview. If the user
supplies both a code and a name, they must identify the same set; otherwise
ask the user which set to use.

If the API is unavailable, an explicit code stays unchanged with a visible
`validation_skipped` warning. A name or unspecified set must stop and ask for a
Set Code. If either search fails, do not choose a result from the other search.
A readable zero-result response always stops processing. The import and its
approval rules are unchanged.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| validate_payables_calendar returns no matching item | Stop as `not_found` before ZIP/import; preserve the supplied Calendar in failure evidence. |
| validate_payables_calendar returns HTTP 400 | Preserve the Calendar and record `validation_skipped` plus a `resolver_contract_issue` finding. Do not call the Calendar invalid or the endpoint unavailable. FSM import remains separately approved and authoritative; review the finding during implementation review. |
| validate_payables_calendar returns HTTP 401/403 or another availability error | Record `validation_skipped` with the error, endpoint, supplied Calendar, and time; continue to package generation and, if approved, the governed FSM import through `core.data-loader`. Do not substitute a proxy, UI value, or write operation. |
| validate_set_code returns no matching item | Stop as `not_found` before ZIP/import; preserve the supplied SetCode in failure evidence. |
| A response has no `items` array, a non-object item, or omits requested fields | Stop as `resolver_failure`; do not generate or import a candidate. |
| Any supporting read-only GET is unavailable | Record `validation_skipped` with the error, endpoint, supplied value, and time; continue to package generation and, if approved, the governed FSM import through `core.data-loader`. Do not use this rule when the GET derives a required package value, resolves a required key, or selects an update target. |

## Uploaded ZIPs

A SetCode in an uploaded assignment CSV is an explicit code. Check every
SetCode using the same lookup and failure rules as a code in a user request.
Do not interpret a CSV code as a Set Name or replace it.

Also check every nonblank `AP_TERM_LINE.Calendar`, including Calendars on
existing installment updates. Query by `calendarName` and
`calendarType='PAYMENT TERMS'`, joined with `and`, using the same lookup rules
as a Calendar supplied in a request. Keep the supplied Calendar unchanged.

When the routed workflow reaches reference validation, run
`scripts/resolve_reference_prerequisites.py --package <uploaded.zip> --output <lookup-results.json>`
with the workflow's approved authentication arguments. Save the results under
the current project. Then pass `--reference-evidence <lookup-results.json>` to
`scripts/fsm_task_adapter.py validate-upload`, along with its baseline and package.
Use the results from the target environment; show the environment and any skipped
checks in the review before import approval.

The validator stays offline. It checks that the lookup results belong to the
exact ZIP and cover each distinct SetCode and installment Calendar once. Missing or incomplete results,
no matches, and malformed lookup responses stop validation. If the API is
unavailable, the results must record `validation_skipped`, the error, endpoint,
supplied value, and time; validation can continue with a visible warning. HTTP 400 also
records a `resolver_contract_issue`. Changing the ZIP requires new results.
ZIPs without set assignments or installment Calendars need no reference results.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| LOOKUP.CALENDAR | step | 30 | reference_lookup | success->LOOKUP.SET;unavailable->LOOKUP.SET | DEP.CHECK | stop | Calendar is supplied, including an installment Calendar in an uploaded ZIP |
| LOOKUP.SET | step | 40 | reference_lookup | success->DEFAULT.APPLY;unavailable->DEFAULT.APPLY | LOOKUP.CALENDAR | stop | A set code, set name, or unspecified set is supplied, including SetCode in an uploaded ZIP |


## Authentication profile and selected Fusion identity

The OAuth properties `environment` identifies the login/trust profile; it may
include an authentication-method label and need not equal Fusion's `ProcessEnv`.
For reference preflight, provide the independently selected Fusion identity as
`referenceContext: {"environment": "<Fusion ProcessEnv>", "baseUrl": "https://<Fusion host>"}`
in the design, or pass a JSON file with those two fields via `--reference-context`.
For Payment Terms uploaded-package lookups, use `--reference-context`.
The selected origin must match the configured authenticated origin, and the
selected environment must still match the baseline/package `ProcessEnv` exactly.
Conflicting CLI/design contexts are rejected before any reference call. The same
selected context must be used for offline receipt and uploaded-package validation.
Without an explicit context, the existing profile-name fallback remains; a
mismatch blocks rather than guessing from a suffix, hostname, ZIP, or receipt.
Timestamp freshness, source hashes, release compatibility and origin checks remain
in force. This does not rename profiles, edit trust enrollment, or change OAuth.
