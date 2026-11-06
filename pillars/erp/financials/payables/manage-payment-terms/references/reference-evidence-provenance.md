# Reference evidence provenance

Use this contract when preparing or validating setup artifacts that rely on
read-only reference lookups. Existing routed workflow and external-operation
prerequisites continue to apply.

## Select the target independently

Read `environment` and the HTTPS base URL from the selected workflow target,
not from the receipt being validated. Save that selection as JSON:

```json
{"environment": "selected-environment", "baseUrl": "https://selected-host.example"}
```

For a normalized design, store this object in `referenceContext`. The lookup
helper checks any supplied context against its actual selected configuration;
it records `referenceContext` when producing a resolved design. Normalization
preserves the selection in the approved blueprint and subsequent build report.
Reference-dependent build and validation check the baseline export's ProcessEnv
against that selection.

For `validate-upload`, supply the independently selected JSON file with
`--reference-context <selected-target.json>` as well as the existing evidence
argument. Never obtain this selection by copying a target from submitted
evidence. An absent selection blocks reuse of lookup evidence.

## Evidence and time rules

Invoice/Payment Options prerequisites and business-unit scope entries carry a
`provenance` object containing `environment`, `baseUrl`, and `checkedAt`.
Payment Terms uploaded evidence carries environment/baseUrl on its envelope and
a checkedAt timestamp on each reference check. Set-name resolution records in
Payment Terms designs also carry provenance. Helpers populate these values
from their actual selected configuration and observation time.

Origins must be HTTPS and contain only a DNS host and optional port. Credentials,
paths, queries, fragments, malformed ports, and whitespace are rejected. Host
case, an optional trailing slash, and explicit default port 443 are normalized
for comparison. The environment name must match the selected target and baseline.

`checkedAt` must be an RFC 3339 date/time with seconds and a timezone (`Z` or
`+/-HH:MM`). It must be no later than validation time and at most 24 hours old;
the exact 24-hour boundary is allowed. This is a local freshness policy, not an
Oracle package-status definition. The same target/time checks apply to successful
and unavailable/advisory results. Unavailable lookups retain their existing
warning policy only after their provenance passes.

Keep existing task, ZIP hash, baseline hash, reference coverage, operation/value,
and endpoint checks. Provenance supplements those checks. A hash identifies an
artifact; it does not establish where or when a lookup happened. These checks
validate recorded claims and are not a cryptographic attestation of live access.

## Regenerate old or rejected evidence

Existing evidence without the required target/time fields cannot be reused.
Rerun the relevant read-only helper through the routed workflow; do not fill in
missing timestamps manually or copy a prior receipt to a new target. Rebuild
reference-dependent candidates after refreshing their design receipts. Local
validation alone makes no Fusion call and does not import anything.
