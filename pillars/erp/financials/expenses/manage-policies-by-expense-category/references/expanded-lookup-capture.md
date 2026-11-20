# Expanded-category lookup capture


At the task's routed reference-lookup step, `scripts/capture_policy_lookup.py`
prepares one exact supplied or retained-parent field selection, or a batch of
selections for the workbook. Its default mode validates the
workbook, task package, baseline provenance, explicit environment/origin and
project artifact destination, then writes a plan with zero network calls.
`--execute` selects the read-only capture after those checks; it does not select
authentication, candidate construction or an import.

The selection JSON contains exactly `entity`, `policy_name`, `operation`,
`field`, `lookup_type` and `code`. The selected field/type and supplied value
must match the current task catalog and workbook. For an omitted parent field,
an `update` selection may use the exact nonempty value from the verified baseline
only when that policy or one of its rates is selected in the workbook. Missing,
duplicate or case-only parent matches are rejected. A supplied workbook value
always takes precedence; it cannot be replaced by a retained-value selection.
Create/update is independently
rechecked when candidate preparation derives the actual baseline operation.
The successful command writes `lookup-receipts.json` for the public adapter or
the preparation/validation `--lookup-receipts` option. Existing output folders
are refused, and changed preparation inputs invalidate capture.

The `code` is resolved to the value that ordinary import serialization will
write, not compared to the target as workbook display text. The normal command
accepts either an exact serialized code or a declared workbook label and uses
the same intake normalization and runtime `field_value` encoder as candidate
construction. For example, boolean No becomes N and Yes becomes Y through that
field's proven mapping; an already encoded N remains N. Other dropdown labels
use their own declared mappings. There is no global text replacement, inferred
default, business-identifier case conversion or waiver of target eligibility.

Plans record `selection_encodings` when a supplied label changes. Original
selection-file bytes and hashes stay unchanged. GET selection, receipt identity,
aggregate index and final resulting-state checks all use the serialized code.
A choice that encodes differently from the workbook's actual value still fails
before transport. Missing/invalid encoding contracts also stop capture. Batch
callers should use the exported `encoded_selection` helper when they need a
canonical selection for local review; do not invent an alternate conversion in
an ad-hoc batch-generation script.

## Workbook batches

Missing reference evidence is the next normal preparation step, not a reason to
stop just because a workbook has many lookup values. At the selected reference
step, put the exact selection objects into a JSON array and pass that file with
the existing `--selection` option. `--dry-run` validates the complete array and
the initialized project destination without files or network requests; it cannot
be combined with `--execute`. Plan the whole array first; use a new output
directory for the subsequent `--execute` invocation. Validate every selection
against the workbook/baseline before constructing a transport. No separate
approval or user-supplied evidence is required for each field by this task;
the active workflow's rules still govern the read-only execution step.

Each selection retains its entity, policy, operation, field, type and exact code.
Include resulting retained references and source-owned derived references where
the owning profile requires them, not only visible nonblank workbook cells.
For example, a new Mileage policy with commute deduction explicitly disabled
also consumes its source-owned inactive commute encoding. Its existing capture
validator checks that derivation; never invent a default or omit that lookup.
Candidate construction remains the independent check of operation and resulting
state, and refuses missing or ineligible evidence.

Within one batch, byte-identical GET requests share fresh response bytes. This
avoids fetching the same lookup type, code list or code context for each policy
field. Every consuming field still receives a separate receipt, and its full
eligibility/context validation runs independently. Responses are not cached
across invocations, targets, changed inputs or failed requests. A multi-code
field uses the existing literal code-to-receipt map; no wildcard is introduced.

The aggregate receipt index is published only after every capture succeeds and
input hashes still match. Failure leaves diagnostic/partial capture files but
no aggregate index, candidate or import authority. Stop without automatic retry;
do not turn partial reference success into a completed preparation result.

## Transport failures and execution context

The capture command records a redacted `transport_reason` and specific recovery
guidance for DNS resolution, certificate trust, timeout and network-permission
failures, including causes wrapped by the core client. It never prints the raw
exception URL, query, headers or credentials. Unknown causes remain explicitly
unclassified rather than being diagnosed as a rejected policy value.

Repeating a request in an unchanged sandbox cannot repair unavailable DNS. For
a DNS failure, compare target name resolution in the permitted execution
contexts without sending a Fusion request. If the target resolves only outside
the sandbox, obtain the execution tool's required authorization and invoke the
same selected capture command there with a new output directory. Do not use a
different REST client, endpoint, credentials, disabled TLS or fabricated lookup
evidence. The task never elevates itself or retries automatically. A new
explicitly authorized attempt preserves the original failed diagnostics and
remains a read-only reference operation, not policy/import approval.

The task adapter reuses the selected repository's core REST client API:
`rest_client_common.build_url` and `request_bytes`, with the existing
`fusion_auth` trust validation, cache reader and `BoundAccessToken` context.
The standard CLI is deliberately not invoked: its normal GET authentication
recovery is not selected by this reference-lookup step. Only an existing
authorized, unexpired private cache is read. A missing/expired cache or HTTP
401/403 returns an auth blocker; no enrollment, OAuth flow or retry is attempted.
The bearer token stays in memory and never enters command arguments, local
evidence or diagnostics. Core source/profile hashes are checked before and
after requests; only the declared lookup/country resources and returned child links are allowed.

The selected REST framework version is 9. Item child links can be returned
inside `@context.links`; legacy top-level item links remain supported. Exactly
one matching returned child link is required across both representations, with
the same origin/path restrictions. No endpoint is inferred from a key or self
link. Framework 9 can serialize high-precision numeric attributes as strings:
only canonical `0`/`10016` application IDs and `0` set ID are accepted in either
integer or string form. Booleans, floats, alternate numeric spellings and other
IDs remain invalid. This changes wire representation support, not eligibility.
See [Oracle REST framework versions](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/Setting_the_REST_Framework_Version.html).

The command captures supplied standard-lookup and country fields and retained
references. Mileage's dynamic company resolver recomputes the resulting parent
type and complete set of consumed ADDITIONAL codes. Its parent receipt binds
every retained or selected child reference, including siblings omitted from the
workbook. The source requires U/E customization, the Expenses module, enabled
codes and application 0 or 10016; it does not impose the standard resolver's
fixed SetId 0 restriction or an active-date filter. SetId remains an explicit,
unambiguous integer identity. See the
[own company lookup contract](mileage-company-lookup-contract.json).

The dynamic resolver is source-matched and offline tested. A new operation still
requires fresh target capture satisfying those predicates; public 26D response
documentation does not establish parity with a later target release. A
dropdown, research snapshot or successful capture does not qualify a field's
FSM operation contract.
