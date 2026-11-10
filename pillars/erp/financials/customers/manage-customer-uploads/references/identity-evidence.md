# Source-key evidence review


The task's `scripts/customer_identity_review.py` reviews supplied read-only evidence offline. It is not a live resolver, an authentication mechanism or full persisted reconciliation. It always reports live execution blocked. Use only evidence exported through a reviewed, declared route; record exact candidate hash, environment, operation, capture timestamp and query date. Completeness declarations are assertions to verify, not proof of authority or freshness.

The reviewed 26D `ar_customer_interface_pkg.pkb` source changes the matching design:

The input is a **display name**, not the distinct 30-character source code.
Reviewed target 26D schema exposes AR_UPD_CUSTOMERS.ORIG_SOURCE_SYSTEM_NAME and
HZ_ORIG_SYSTEMS_TL.ORIG_SYSTEM_NAME as VARCHAR2(80 CHAR); both source-code
columns are VARCHAR2(30 CHAR). The template comment's 30-character recommendation
for a new source must not reject a longer registered name. Preserve exact names;
the code-resolution and unknown-source rules below still apply. This staging
character limit does not certify every SQL*Loader byte/character-set boundary.

- Lines 13209–13215 resolve an exact display name through `HZ_ORIG_SYSTEMS_VL` and use its registered code when found. Do not assume a punctuation-stripped name is that code. Multiple matching records are ambiguous. With no matching name, the supplied ADE control derives the code using Oracle `SUBSTR(REGEXP_REPLACE(name,'[^[:alnum:]]'),1,30)`; database character semantics must be retained. The offline helper does not approximate that expression with Python character classes.
- Lines 13300–13328 and 13589–13714 propagate distinct source references for party, account, party site, location, account site and site use. Match owner table together with source code and reference. Equal reference text across different entity types is not a duplicate by itself.
- Lines 14618–14629 check an account-level profile using the account's source reference, owner table and active dates; this particular query does not filter `HZ_ORIG_SYS_REFERENCES.STATUS`. Therefore an inactive but date-current account reference still needs the profile-effect check. Do not turn a generic active-only lookup into a prediction that no profile update can occur.

The developer supplied an ADE `ArUpdCustomers.ctl` in response to the target-release source request. Its SHA-256 is `c85f853f709c7adaec364476049c74f21f00ac5fc5bfdf97b6e2a96c89a548e4`; the exact ADE label was not supplied. All 87 input fields match the template contract. The helper now derives lookup keys from these expressions without changing candidate bytes:

| Entity | Supplied reference | Loader behavior when blank |
|---|---|---|
| Party | PARTY_ORIG_SYSTEM_REFERENCE | PARTY_NUMBER |
| Account | CUST_ORIG_SYSTEM_REFERENCE | ACCOUNT_NUMBER |
| Account site | CUST_SITE_ORIG_SYS_REF | PARTY_SITE_NUMBER |
| Location | LOCATION_ORIG_SYSTEM_REFERENCE | No fallback in this control |
| Account site use | CUST_SITEUSE_ORIG_SYS_REF | No fallback in this control |
| Party site use | CUST_SITEUSE_ORIG_SYS_REF | No fallback; separate owner HZ_PARTY_SITE_USES, never the account-site-use ID |
| Party site | Generated SITE_ORIG_SYSTEM_REFERENCE | PARTY_NUMBER concatenated with `-partysite-` and LOCATION_ORIG_SYSTEM_REFERENCE; this uses the display number, not the party source reference |

An explicit nonblank reference takes precedence over its number fallback. Edge whitespace requires loader lexical review; the helper does not silently trim it. An absent reference is not proof that no entity exists through another matching path. A single reference does not verify its parent relationships or field mutability. Source-file compatibility is not proof of live execution or exact deployed patch identity.

Evidence schema `ar-customer-identity-evidence-v3` contains `candidate_sha256`, `environment_url`, `operation_intent`, `as_of_date` (database date from `TRUNC(SYSDATE)`), `captured_at` (timezone-qualified timestamp), `evidence_reference`, `source_system_queries` and `reference_queries`. Version 3 adds party-site-use identity to the previous six entities. Old v2 evidence must be recollected with the seventh owner; changing its version string alone does not supply the missing evidence. Version 2 had replaced an unused date-only v1 draft.

The party-site-use mapping is explicit in Customer Interface lines 13634–13658
and HZ_CIMP_ADDRESS_PKG lines 3398–3428. That package inserts the source reference
with OWNER_TABLE_NAME HZ_PARTY_SITE_USES and the resolved PARTY_SITE_USE_ID.
Sharing the spreadsheet reference with an account-site use does not equate IDs.

Each source query contains `source_name`, Boolean `complete`, and `records` of exact `orig_system_name` / `orig_system`. Each reference query contains `orig_system`, `owner_table_name`, `reference`, Boolean `complete`, and records containing string `owner_table_id`, `status`, `start_date_active` and nullable `end_date_active`. Preserve every matching row and explicit empty results; omitted or incomplete queries mean unknown. Export Oracle DATE bounds with `YYYY-MM-DD"T"HH24:MI:SS` in database-local time, without timezone conversion or truncation. A same-day start after midnight does not satisfy the reviewed profile query's `TRUNC(SYSDATE)` comparison. `dated_records` describes this source-specific comparison, not generic current-time activity across all HZ consumers. Do not collapse duplicate records or select the first match.

```text
python <task-folder>/scripts/customer_identity_review.py --zip candidate.zip --operation create --environment-url https://<approved-host> --evidence reviewed-identity-evidence.json
```

The output contains row/entity finding codes and counts, without customer identity values. Exit code 2 reflects incomplete live readiness even when supplied reference evidence is coherent. Account-profile existence, actual ownership, receipt-method assignments, all requested persisted values and DFFs still need separate authoritative readback. The helper neither fills customer values nor enables an import.
