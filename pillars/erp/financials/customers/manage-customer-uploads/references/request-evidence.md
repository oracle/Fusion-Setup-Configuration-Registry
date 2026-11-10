# Request-scope evidence


`scripts/customer_request_review.py:analyze` compares candidate ZIP bytes,
operation, environment, a supplied attempt record and staging evidence offline.
It performs no status call, upload, retry or Journey transition. It does not
invent a mapping from a Data Loader response to interface/product ESS IDs.

## Distinct identifiers

Retain core's initiation RequestId and UCM ContentId. Obtain the interface request
and upload request IDs from separately retained, reviewed runtime evidence;
never copy the initiation ID into another namespace as a fallback. Numeric
equality alone does not establish or disprove a link between these namespaces.

The reviewed Customers registration scopes AR_UPD_CUSTOMERS by LOAD_REQUEST_ID
bound to interfaceRequestId. The captured 26D Customer Interface source's
SCU_postprocessing (lines 13018–13064) separately stamps BATCH_ID and
UPLOAD_REQUEST_ID for that load scope. Receipt assignment REQUEST_ID is
negative BATCH_ID (lines 10127–10210), not an ESS request ID. FILE_RECORD_NUM can
represent a party group, so repeated values are retained and never interpreted
as candidate CSV row positions. Source/control hashes are recorded in
`assets/customer-reconciliation-matrix.json`.

## Supplied schemas

Attempt version `ar-customer-request-attempt-v1` requires:

- candidate_sha256, environment_url and operation_intent;
- initiation_request_id, content_id, interface_request_id and upload_request_id;
- timezone-qualified initiated_at, initiation_evidence_reference and
  scope_evidence_reference.

The three request IDs are positive decimal strings; upload_request_id may be
null while unknown. ContentId is an opaque nonblank string. These fields are
review inputs, not an approved execution envelope or authenticated evidence.

Evidence version `ar-customer-request-evidence-v1` requires attempt_sha256,
captured_at, evidence_reference, requested_load_request_id, complete and records.
The query key must equal the supplied interface_request_id, capture cannot
precede initiation, and complete must describe the entire queried scope.
Each row contains exactly cust_upload_id, load_request_id, upload_request_id,
batch_id, file_record_num and upload_status. IDs are decimal strings; product
stamps and file_record_num may be null. Status is string or null. Preserve all
rows and statuses; never query only expected IDs, successful rows or a guessed
batch. Do not deduplicate CUST_UPLOAD_ID or truncate without marking incomplete.

The review suppresses counts for incomplete, duplicated or out-of-scope results.
Otherwise it preserves SUCCESS counts, the registration's three error statuses
(FAILED, FAILED_NOT_CORRECTABLE, BLOCKED), and pending counts for every other
status including null and unknown future statuses. It reports missing stamps,
mixed batches/uploads, an unexpected upload request and row-count differences.
Matching counts do not prove candidate-to-staging lineage. No-staging-rows does
not mean rollback, safe retry or a successful empty import.

`SUPPLIED_STAGING_SCOPE_AGREES` is only an observation. The result always keeps
initiation_to_product_link_verified, candidate_staging_lineage_verified,
persisted_reconciliation_complete, execution_authorized, retry_authorized and
journey_complete false. Keep all core datasets, scopes, diagnostics and detailed
errors separately; this helper does not replace core status collection.

Live field extraction, candidate-to-staging lineage and a runnable campaign
adapter remain separate dependencies. File layout/test discovery remain
provisional under the parallel ownership agreement.

## Core association bridge

[Attempt association](attempt-association.md) now checks retained core data-set and process evidence and can prepare this helper's attempt record. It requires exact candidate/context, Run Book/task/content and process-definition matches. Actual Customers stage mapping and candidate-to-staging lineage still require live campaign evidence. The staging reviewer independently compares the supplied expected IDs with the persisted stamps.
