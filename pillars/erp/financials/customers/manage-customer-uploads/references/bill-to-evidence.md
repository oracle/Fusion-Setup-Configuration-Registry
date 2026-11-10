# Bill-to link evidence


`scripts/customer_bill_to_review.py:analyze` compares the supplied after-state
link for nonblank BILL_TO_CUST_SITE_REF on SHIP_TO rows. It revalidates the
candidate's identity and ownership bundle. This is a local evidence review,
not a Fusion client, a pre-import lookup replacement or a loader-path assertion.

Pass ZIP bytes, operation intent, environment, identity evidence, after-phase
ownership evidence and `ar-customer-bill-to-evidence-v1`. The evidence includes
candidate_sha256, environment_url, operation_intent, ownership_evidence_sha256,
timezone-qualified captured_at, evidence_reference, reference_queries,
link_queries and target_queries. Capture must follow ownership evidence.

Reference queries contain orig_system, owner_table_name, reference, complete and
records, scoped to exact candidate bill-to references and resolved source codes.
The owner is HZ_CUST_SITE_USES_ALL. Each record retains
orig_system_reference_id, orig_system, owner_table_name, reference,
owner_table_id, status, start_date_active and end_date_active. Export all status
and history rows without deduplication. The comparison uses exactly one A-status
reference, matching the reviewed fallback predicate; dates remain visible and
validated, but do not silently add a date filter the loader does not use.

Link queries use site_use_id, complete and records. Each record has site_use_id
and nullable bill_to_site_use_id. The source ID must be present in the bound
ownership evidence. Target queries have site_use_id, complete and records;
their IDs must be observed in the reference or persisted-link evidence. Target
records contain site_use_id, cust_acct_site_id, cust_account_id, set_id,
account_site_set_id, site_use_code and status. Follow actual parent IDs in the
query and preserve nulls/duplicates. IDs are decimal strings; set ID 0 is valid.

The actual link must equal the unambiguous expected reference owner. The target
must have BILL_TO purpose and complete parent data with a consistent parent set.
Target status and cross-account/set differences are reported as observations.
They do not establish business eligibility. Do not impose an unsupported
same-account rule or describe an inactive target as eligible merely because
the selected link matches.

`SELECTED_BILL_TO_LINKS_MATCH` is limited to these after-state links. All full
reconciliation, approval, business-eligibility, resolution-path and Journey flags
stay false. Same-batch resolution versus existing-reference fallback requires
attempt-specific interface evidence. Blank input is not a clear request and
needs before/after effect review. Missing/ambiguous evidence never authorizes
creation, replay or resubmission. Diagnostics do not echo input references.

See [downstream source findings](downstream-party-and-bill-to.md). Final helper
and test placement remains provisional pending the separate ownership contract.
