# Customer ownership evidence


`scripts/customer_ownership_review.py` checks supplied evidence for the seven entities resolved by the identity helper. Matching a source reference alone does not establish that its target belongs to the intended customer hierarchy. This check compares the account's party, the party site's party/location, the account site's account/party site, the account-site use's account site/set/purpose, and the party-site use's party site/purpose.

It accepts an `ar-customer-ownership-evidence-v1` object with these exact top-level fields:

| Field | Contract |
|---|---|
| schema_version | ar-customer-ownership-evidence-v1 |
| candidate_sha256, environment_url, operation_intent | Match the candidate and identity evidence exactly |
| identity_evidence_sha256 | Canonical JSON fingerprint of the complete identity evidence, using the package helper |
| phase | before or after; use fresh identity and ownership evidence after execution |
| as_of_date | Same database date as the bound identity evidence |
| captured_at | Timezone-qualified capture timestamp, not earlier than the identity capture |
| evidence_reference | Provenance of the reviewed export; a declaration alone does not authenticate it |
| queries | All scoped query results, including empty results and duplicates |

Each query contains `entity`, string `owner_table_id`, Boolean `complete`, and `records`. IDs must be positive decimal strings, and the queried ID must occur in the bound identity evidence for that entity. Records contain exactly the fields below; the first is the primary key and must equal the queried ID. Parent IDs and purpose can be null, which cannot pass a relationship comparison.

| Entity | Record fields |
|---|---|
| party | party_id |
| location | location_id |
| account | cust_account_id, party_id |
| party_site | party_site_id, party_id, location_id |
| account_site | cust_acct_site_id, cust_account_id, party_site_id, set_id |
| account_site_use | site_use_id, cust_acct_site_id, set_id, site_use_code |
| party_site_use | party_site_use_id, party_site_id, site_use_type |

Use only an unambiguous active source reference with one preserved reference row for automated comparison. Historical, ambiguous and inactive reference sets remain visible for review. Do not select an arbitrary row, collapse duplicates, or interpret a missing query as an empty result. Query physical rows by the reviewed ID without joining to an expected parent: such a join could hide an incorrect relationship. Missing physical records, incomplete queries, null relationships and absent identities remain incomplete, not creation authority.

```text
python <task-folder>/scripts/customer_ownership_review.py --zip candidate.zip --operation create --environment-url https://<approved-host> --identity-evidence identity.json --evidence ownership.json
```

The report exposes row/check/status diagnostics without customer IDs or source values. `SUPPLIED_OWNERSHIP_CONSISTENT` means these supplied relationships agree. It does not establish all persisted field values, update mutability, profile effects, receipt assignments, BILL_TO links, tax, DFFs, authentication or snapshot consistency. The helper always retains incomplete live readiness and returns exit code 2. A before/after label does not replace capture provenance or comparison of the two states.

This is an offline evidence evaluator. It adds no external operation or fallback to the compiled task graph. Runtime data acquisition must be declared and reviewed separately; campaign evidence collection is not a substitute for a completed reusable runtime route.
