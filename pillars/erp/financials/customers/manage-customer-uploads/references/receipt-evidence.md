# Receipt-assignment evidence


`scripts/customer_receipt_review.py:analyze` compares supplied after-state receipt
values for a candidate bound to identity/ownership evidence. It does not submit
an import or decide that an assignment was created by this attempt. The reviewed
26D source inserts RA_CUST_RECEIPT_METHODS; a matching existing assignment is
not proof that replay or in-place update is supported.

## Evidence

Version `ar-customer-receipt-evidence-v1` requires candidate_sha256,
environment_url, operation_intent, ownership_evidence_sha256, captured_at,
evidence_reference and the arrays below. Capture is timezone-qualified and follows
the bound after-phase ownership evidence. Queries have their exact key, boolean
`complete` and `records`; preserve duplicates, historical and unrelated rows.

| Array / exact query key | Record fields |
|---|---|
| `method_queries` / `name` | `name`, `receipt_method_id`, `start_date`, `end_date` |
| `site_use_queries` / `cust_acct_site_id` | `site_use_id`, `cust_acct_site_id`, `set_id`, `site_use_code`, `status` |
| `assignment_queries` / `customer_id` | `cust_receipt_method_id`, `customer_id`, `receipt_method_id`, `site_use_id`, `primary_flag`, `start_date`, `end_date`, `request_id` |

IDs are strings; site-use ID may be null for account-level assignments. Dates are
full Oracle DATE seconds or explicit null. REQUEST_ID is preserved as a signed
numeric string or null. In this loader it can be negative BATCH_ID, not the ESS
request ID. This helper does not certify batch/request correlation.

Return all assignments for the exact account, without filtering to the expected
method/site/date. Return all site uses for the exact account site, not just the
expected purpose or active rows. Completeness requires verified export counts or
pagination; an absent/failed query is not an empty successful result. Query scope
must derive from candidate-bound ownership IDs and exact requested method names.

## Interpretation

The method name must resolve to one row. Resolve exactly one active BILL_TO use
through the actual account site and verify its set ID. A SHIP_TO candidate can
therefore refer to a separate active BILL_TO use on the same account site; do not
blanket-reject SHIP_TO based on the worksheet purpose alone. Duplicate active
BILL_TO results require review. Account-level-only reconciliation remains a
separate unimplemented scope, not a prohibition on the skill's business inputs.

For a single scoped assignment compare method/site, primary flag and start date.
Blank primary flag has the reviewed interface expectation N. Start date derives
from ACCOUNT_ESTABLISHED_DATE, including the reviewed control's 1900/01/01 blank
default; compare midnight after the source's truncation. Never inject those
defaults into the CSV. A nonnull persisted end date needs an effect review.
Method/receipt-class business validity is separate from this value comparison.

Preserve all unrelated assignment counts. Multiple periods or assignment IDs
for the same method/site require history review, not first-match selection.
No receipt input produces `NO_RECEIPT_INPUT_EFFECTS_UNVERIFIED`, not a claim that
there are no assignments or no unintended changes. Before/after snapshots and
attempt correlation remain necessary to prove actual effects.

Every result keeps assignment_delta_verified, request_correlation_verified,
persisted_reconciliation_complete, execution_authorized and journey_complete
false. Source backing: Customer Interface package 486–757, 10127–10210 and
14646–14684; reviewed control fingerprint and source capture are in the existing
reconciliation matrix. This is offline behavior-tested comparison, not a live
import result. Final file placement/test discovery remains provisional.
