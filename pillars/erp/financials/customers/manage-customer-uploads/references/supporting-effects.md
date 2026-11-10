# Supporting profile and sibling-site effects


`scripts/customer_supporting_effect_review.py:analyze` compares complete,
supplied before/after inventories for every party in the bound ownership
evidence. The two inventory kinds are organization_profiles and party_site_uses.
It performs no query, mutation, approval or Journey update.

The 26D HZ_CIMP_ADDRESS_PKG post-processing source, lines 3700–3860, counts
primary party-site uses across a party and site-use type, clears competing
primary flags and can select a default primary. Consequently, reading only
sites explicitly present in the candidate can miss affected sibling sites.
Capture all party-site uses for each scoped party, including inactive and
historical rows, without filtering to expected values or candidate site IDs.

Account-site uses have a separate effect boundary. Reviewed 26D
HZ_CIMP_ACCTSITEUSE_PKG.ASU_PROCESS_PRIMARY, lines 1066–1094 and 1143–1158,
selects active site uses across affected accounts and updates account-site
BILL_TO_FLAG, SHIP_TO_FLAG and MARKET_FLAG, plus technical audit/batch stamps.
Adding a Ship-to site can therefore touch an existing Bill-to account site even
when its selected business values and primary purpose remain unchanged. Capture
the scoped account-site-use inventory, these denormalized flags and technical
stamps before and after when reviewing such effects. Do not infer an unrequested
business change solely from an updated timestamp, or assume no physical write
from unchanged selected values. Conversely, do not discard business-flag changes
as technical noise.

The helper below covers party-site uses and organization profiles only. It does
not cover account-site-use inventories or these denormalized flags. Retain that
separate review explicitly; after-only flag observations cannot prove before/after
equality, and database test evidence does not qualify functional runtime collection.

Each evidence document has schema_version ar-customer-supporting-evidence-v1,
candidate_sha256, environment_url, operation_intent,
ownership_evidence_sha256, phase, captured_at, database_as_of,
evidence_reference and queries. captured_at is timezone-qualified; database_as_of
is the query's Oracle database DATE rendered with full ISO seconds. Keep the
database instant distinct from an inferred loader execution instant.

Queries contain kind, party_id, complete and records. Exact record projections:

| Kind | Fields |
|---|---|
| organization_profiles | party_id, organization_profile_id, effective_start_date, effective_end_date, effective_sequence, effective_latest_change, duns_number_c, jgzz_fiscal_code, gsa_indicator_flag |
| party_site_uses | party_id, party_site_id, party_site_use_id, site_use_type, primary_per_type, status, begin_date, end_date |

Preserve string values and explicit nulls. IDs are decimal strings; profile
sequence permits zero. Dates use full YYYY-MM-DDTHH:MM:SS. Export all profile
versions; their key is profile ID, effective start and sequence. Party-site uses
are keyed by party-site-use ID. Duplicate keys, incomplete queries or missing
before inventories suppress change counts. Never fabricate an empty before
inventory for a newly observed party or infer creation from its source reference.

For complete, ownership-consistent inventories, results show added, removed,
changed and unchanged row counts plus changed column names. A change requires
effect review; it is not implicitly authorized or attributed to the import.
The helper also corroborates nonblank DUNS, taxpayer ID and GSA values against
exactly one latest organization profile covering database_as_of. Missing dates
and overlapping profiles remain explicit findings. This does not certify other
profile defaults, fields or physical creation. The supplied inventory must
contain every party-site use in the bound ownership evidence with the same
parent and purpose; missing or conflicting entries suppress effect counts.

All completion, effect-acceptance, causality and execution flags remain false.
The separate v3 identity/ownership check resolves the party-site use's own source
reference: simplified Upload Customers maps CUST_SITEUSE_ORIG_SYS_REF to
HZ_IMP_PARTYSITEUSES_T.SITEUSE_ORIG_SYSTEM_REF as well as to the account-site-use
interface. Never equate the two persisted use IDs merely because input references
are equal. Final helper/test placement remains subject to the separate contract.
