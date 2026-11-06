# Currency reference contract

This contract covers the supplied or retained parent CurrencyCode for the one
Meals policy/rate pair, including rate-only updates. Omitted workbook cells
request no default or clearing; the retained parent's currency still needs checking.
Do not derive currency from a parent: reviewed rate EO getters suppress their
interactive parent-currency fallback during migration.

## Source and applicability

The read-only collection and response fields are documented in Oracle's
[26c currency LOV API](https://docs.oracle.com/en/cloud/saas/applications-common/26c/farca/op-http-servername-fscmrestapi-resources-11.13.18.05-currencieslov-get.html).
The corresponding 26d endpoint page was unavailable at authoring time. No
target-release equivalence is inferred from that documentation version.

Reviewed CurrencyPVO source declares an exact currency-code criterion, enabled
and monetary filters, and inclusive active-date bounds with null alternatives.
The pinned file SHA256 is
abf87851b59d7fda0433a91f0a7b67a2618b48644d79c467b8e1e18269833a5f;
source path ends in currencies/manageRate/publicView/CurrencyPVO.xml,
FPH label261013.0000.S. These are reference facts, not CSV field acceptance,
minimum-input, write/defaulting or target-release qualification.

## Declared lookup

Use only the repository's core.fusion-api.rest-api-client after the active task
workflow selects reference_lookup. scripts/currency_reference.py creates a
request plan and classifies captured responses; it performs no network call.

- Method/path: GET /fscmRestApi/resources/11.13.18.05/currenciesLOV.
- Inputs: exact supplied CurrencyCode and explicit operational validation date,
  YYYY-MM-DD. Do not default a business currency or policy/rate date.
- Query: q=CurrencyCode='<exact code>'; fields=CurrencyCode,CurrencyFlag,
  EnabledFlag,StartDateActive,EndDateActive; onlyData=true; limit=100; offset=0.
- Header: REST-Framework-Version=9. No body.
- Continue only this declared collection for pages: offset advances by the
  actual count, with unchanged filter/fields. A failed page invalidates the
  result. Do not follow arbitrary response links or switch endpoints.

The request helper serializes only letters, digits, underscore, period and
hyphen inside its quoted query literal. It refuses other characters without
claiming the currency is invalid; no unescaped user text enters the expression.
The documented code length is15. This is not an invented ISO-only code list or
permission to normalize case, trim values or substitute a currency.

## Match and failure behavior

Require complete, consistent pages and exactly one exact case-sensitive code.
The match must have EnabledFlag=Y, CurrencyFlag=Y and active date bounds
containing the explicit validation date; null bounds are unbounded. Dates must
be canonical date-only strings. Preserve exact input code on successful mapping
to the requesting CurrencyCode field; never map a display name or inferred ID.

Complete zero-match, multiple-match and ineligible results are distinct data
findings and stop resolution. Missing fields, malformed dates/flags, incomplete
or inconsistent pages are unavailable evidence, never proof of an invalid code.
Authentication, transport and server failures retain their core error class;
no alternative lookup or automatic retry is selected here. Any later governed
application-validation choice belongs to its owning workflow and is not created
by this contract.

Bind actual target, code, explicit validation date, request and response hashes
to the consuming operation. A captured response or pure helper result alone
must not set a permanent runtime-contract reference_verified flag. Do not reuse
a developer observation as a current runtime result or import approval.

## Integration boundary

The ordinary supported Meals route accepts an operation-bound currency receipt, while
retaining the independent native-plan, entity, field and package gates. Static
reference_verified flags and a pure classifier result remain insufficient.

scripts/capture_currency_reference.py plans the declared GET by default and
executes only with --execute after the active authoring/reference_lookup step
has selected it. It verifies the core profile's exact environment/origin, uses
only the core REST client, captures complete response pages and records each
request/response hash. Its consuming operation list must match the workbook's
supplied currency references. It never builds a candidate or submits an import.

scripts/currency_receipt.py rechecks eligibility from those pages, not a saved
success flag. The builder binds the receipt to exact workbook, baseline and
runtime-contract hashes, environment, HTTPS origin, explicit operational date,
entity, policy association, operation and currency. Baseline provenance must
verify and have the same target origin. Altered requests, pages, adapter version,
incomplete pagination or a mismatched operation stop preparation. Evidence
files are immediate nonsymlinked receipt-directory members. Retained currency
also requires evidence when its reviewed operation declares that validation.
The capture launcher resolves supplied or retained parent currency from the
bound workbook/baseline; it never invents a code or skips the retained requirement.

Use candidate options --currency-receipt, --target-origin and --validation-date
only with this complete evidence. Refresh after any bound input/contract changes
or when the current workflow needs a new operational validation date. Receipts
are host-recorded local audit evidence, not signed authentication, an indefinite
freshness guarantee, product write acceptance or import authority.

This currency route does not bypass the native planner or approval, qualify any
role/geography field, or certify every possible currency import outcome.
