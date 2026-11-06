# Reference Lookups

`Manage Payment Options` creates the same `AP_SYSTEM_PARAMETER` row as its sibling `Manage Invoice Options`. Before live normalization, run `scripts/resolve_lookup_prerequisites.py`; it delegates only the shared-row prerequisite checks to the sibling's task-local read-only preflight contract. For a shared-row create, the wrapper keeps the supplied `TermName` for the Invoice Options-owned resolver and retains its receipt for normalization. Invoice-owned term changes on updates and the optional PrepaymentTermName/EmployeeTermName fields remain outside Payment Options ownership. The Payment Options adapter remains offline, and neither component calls CRM, BICC, or SQL.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_bank_charge_deduction_type | Bank Charge Deduction Type is supplied | BankChargeDeductionTypeDes and the task-local e2e-adapter.json field contract | Accept only Standard, Negotiated, or None; the CSV uses names rather than database codes S, N, or X | Validated submitted BankChargeDeductionTypeDes | Block every other value; do not confuse this control with Bank Charge Bearer |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_business_unit_by_name_and_enterprise | A create targets BuName | Requested BuName, explicit EnterpriseId or the fresh FSM baseline, and the delegated Invoice Options preflight contract | scripts/resolve_lookup_prerequisites.py delegates GET /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV to the sibling Invoice Options helper | BusinessUnitId, ActiveFlag, PrimaryLedgerId | Require one active exact BU; obtain EnterpriseId from the explicit row or one distinct nonblank baseline value | Resolved BU identity and EnterpriseId | Block a missing, inactive, or ambiguous BU or EnterpriseId; never create a BU |
| resolve_business_unit_primary_ledger | A new AP_SYSTEM_PARAMETER row is created | Exact BU and its PrimaryLedgerId from the delegated Invoice Options preflight receipts | scripts/resolve_lookup_prerequisites.py delegates GET /fscmRestApi/resources/11.13.18.05/ledgersLOV/{PrimaryLedgerId} to the sibling Invoice Options helper | LedgerId, Name, CurrencyCode | Require the returned ledger to match the exact BU primary-ledger receipt | Derived SOBName and BaseCurrencyCode | Block missing, malformed, or conflicting receipts; do not infer a ledger or currency |
| resolve_payment_term_from_name | A new AP_SYSTEM_PARAMETER row supplies required TermName | Requester-supplied term name | scripts/resolve_lookup_prerequisites.py delegates GET /fscmRestApi/resources/11.13.18.05/payablesPaymentTerms to the owning Invoice Options helper | name, termsId | Follow all returned pages. One valid term ID with a consistent nonblank name validates without a duplicate warning; retain different IDs or incomplete/inconsistent identity as advisory | Submitted TermName unchanged and its owning lookup receipt; never write a numeric term ID | Block a readable zero-result. Disclose ambiguity or unavailable access as advisory; Fusion validates the name in import context |

Payment Options and Invoice Options use the same `AP_SYSTEM_PARAMETER` row and CSV package contract. Validate the resulting shared row through the sibling Invoice Options contract before preview; do not bypass that dependency with a payment-only package.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A supporting lookup returns one or more readable records | Keep the submitted CSV value. Do not choose a returned ID or replace the value. Fusion performs the final check during the approved import. The required BU/ledger checks for a new row follow the stricter rules below. |
| The API responds successfully but finds no matching record | Stop preparation before preview, ZIP generation, or import. Identify the field and supplied value, and ask the user to correct it. Do not treat this as an unavailable API or continue with only a warning. |
| A supporting lookup cannot be checked because access is denied (HTTP 401/403), the network fails, the request times out, or the server returns HTTP 5xx | Keep the submitted value, record `validation_skipped` with the reason, and tell the user it could not be checked. Preparation may continue; Fusion checks the value during the separately approved import. This does not apply when a new row still needs required BU/ledger values from the API. |
| A new row needs required BU/ledger values, but the API cannot provide them | Stop before preview, ZIP generation, or import if the required values remain unresolved. Ask for correction or restored API access; do not guess the values. |
| A supported read-only lookup is later evidenced | Add one task-scoped resolver with source values, request path, match rule, output mapping, and no-match/many-match behavior before it is used |
| A delegated supporting GET returns HTTP 400 | Keep the submitted value and record both `validation_skipped` and `resolver_contract_issue`. Report that the lookup request could not be used; do not say the value was not found. Preparation may continue unless required BU/ledger values for a new row remain unresolved. Fusion performs the final check during the separately approved import. |

## Uploaded Create ZIPs

Keep the JSON build report alongside the generated ZIP. It contains the
business-unit/primary-ledger and shared reference lookup results already used
for that build, tied to the exact ZIP and baseline hashes.

Run `scripts/fsm_task_adapter.py validate-upload --baseline <baseline.zip>
--package <uploaded.zip> --validation-context <build-report.json>`.
Use the saved report from the target environment and the same fresh baseline.
If the ZIP or baseline changes, obtain new lookup results through the routed
preparation workflow and save a new build report; do not edit the hashes to
reuse old results. For another uploaded ZIP, its preparation must supply the
same exact-file lookup context before its create rows can pass validation.

For a create, `SOBName` and `BaseCurrencyCode` are physical CSV context fields.
Check both against the exact business unit's primary-ledger lookup results.
Do not treat them as user-requested changes, silently replace them, or remove
these columns from the ZIP. Missing or conflicting values stop validation.
The shared Invoice Options checks still require all mandatory values and
applicable lookup receipts. Existing Payment-only updates that need no lookup
context can continue without a build report. Validation performs no live calls
and never changes or imports the uploaded ZIP.

For uploaded creates, also compare every shared create-default cell with the
Invoice Options documented default. Blank or conflicting cells block import.
Validation must not approve a default that exists only in its normalized copy
of the request; the exact uploaded CSV must contain it.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PAYOPT.LOOKUP_PREFLIGHT | step | 15 | reference_lookup | ready->PAYOPT.CHECK_DEPENDENCIES;blocked->PAYOPT.DEPENDENCY_BLOCKED | PAYOPT.VALIDATE_INPUT | stop | Always; run applicable local checks and the delegated read-only preflight, preserve its receipts, and do not call a live service for a local check or an update needing no lookup |


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
