# Account-profile class and requested reference-set evidence


Use `scripts/customer_profile_set_review.py:analyze` after the identity and
ownership checks. Pass candidate ZIP bytes, declared operation, environment,
identity evidence, after-phase ownership evidence and profile/set evidence.
The helper recomputes ownership; supplied result labels cannot bypass it.

## Evidence structure

Version `ar-customer-profile-set-evidence-v1` requires `candidate_sha256`,
`environment_url`, `operation_intent`, `ownership_evidence_sha256`, `as_of_date`,
timezone-qualified `captured_at`, `evidence_reference`, and these query arrays:

| Array / exact key | Record fields |
|---|---|
| `set_queries` / `set_code` | `set_code`, `set_id` |
| `class_queries` / `name` | `name`, `profile_class_id`, `status` |
| `profile_queries` / `cust_account_id` | `cust_account_profile_id`, `cust_account_id`, `site_use_id`, `profile_class_id`, `status`, `effective_start_date`, `effective_end_date` |

Each query also has boolean `complete` and a `records` array. IDs are strings;
set/profile-class ID `0` is valid. Site-use ID must be explicit null for an
account-level profile. Preserve all account-level profile rows and their raw
Oracle DATE seconds, including historical and inactive rows. Do not substitute
an empty query when execution failed or the export was truncated. Verify complete
pagination/row counts before declaring complete. A zero-row result is an empty
array; a Publisher left-join placeholder is not a real profile record.

The environment, intent, candidate and ownership fingerprints must match.
`as_of_date` is the database-exported date already bound to the ownership evidence.
Capture must follow ownership capture. Query keys must be the candidate's exact
requested set/class names or the bound ownership account IDs. No extra account
or guessed identifier is accepted.

## Comparison semantics and evidence limits

Requested set code is resolved to the set ID and compared against both actual
account-site and site-use IDs. Their mutual agreement alone is insufficient.
Repeated set metadata rows resolving to the same ID remain preserved and counted;
the reviewed 26D site-use staging query uses SELECT DISTINCT. Distinct IDs for
the same code are ambiguous. This is an after-state value comparison, not a claim
that every upstream reference-set validation accepts repeated metadata rows.

The requested profile-class name must resolve to exactly one active class row.
Duplicate class rows are ambiguous even when identical. Blank Customers
CUSTOMER_PROFILE_CLASS produces a DEFAULT expectation from the reviewed 26D
interface mapping, explicitly marked `REVIEWED_INTERFACE_DEFAULT`; it is not
written into the user's CSV or represented as an explicit business value.

Profile existence and effective-value comparison remain separate. The helper
reports the number of all supplied profile rows and completeness without assuming
that an inactive/historical row is absent. It compares the class only when exactly
one active profile covers the exported database date at midnight, retaining full
DATE seconds and inclusive bounds. This is an explicit snapshot comparison
policy, not a claim about the downstream loader's effective-date generation.
Missing dates/status, duplicate profile periods or overlapping active profiles
require review. Profile creation versus update/reuse and all defaulted profile
attributes remain unresolved by this comparison alone.

Source evidence: reviewed Customer Interface package lines 13680–13714
(set-code staging) and 14571–14629 (DEFAULT expectation and all-row existence).
The latter I/U predicate does not filter profile status/effective dates and uses
the source-reference dates without an OSR status predicate. This helper does not
claim that branch executed. Source fingerprints are recorded in the existing
reconciliation matrix; target FSCM probes verified relevant schema and class/set
ID-zero examples. No live import has yet validated these effects.

## Handoff

`PROFILE_SET_VALUES_MATCH` covers only these two comparisons. Combine it with
the selected-value findings for CUSTOMER_PROFILE_CLASS and ACCT_ADDRESS_SET_CODE;
do not suppress other `FIELD_NOT_COVERED` findings or treat the selected-value helper
as expanded to all 87 fields. Keep mismatches and incomplete results distinct.
Full persisted reconciliation, authorization and Journey completion stay false.
Credit-hold/default attributes, receipt assignments, DFFs, before/after effects
and process correlation still need their own evidence.

This module has no Fusion client and does not add a pre-import requirement for
post-import evidence. Task Hook uses the central handoff contract and still
requires actual candidate evidence. Placement/test-discovery contracts remain provisional.
