# Associate a Customers attempt with core status evidence


## Selected task-owned REST collection

After an approved attempt has a retained candidate, environment, preflight,
registration/argument hashes and actual initiation receipt, select
`scripts/customer_attempt_collect.py` for read-only post-import evidence.
Read core REST client instructions first. Use `--repo`, `--properties`,
`--token-cache`, `--environment`, `--candidate`, `--operation`, `--binding`
and a new `--output` directory. The binding must come from retained evidence,
not invented identifiers or substitute approvals. Use the authorized read
principal; read authorization does not establish import authorization.

The fixed GET routes are `/hcmRestApi/resources/latest/dataLoaderDataSets`
filtered by the exact retained `DataSetRequestId`, then the sole matching
data set's `child/processes`, `child/fbdiBusinessObjects`, and the Customers
object's `child/fbdiErrorMessages`. Follow bounded pagination and reject
ambiguous data sets, foreign parents, duplicate process IDs and partial pages.
No submission action, arbitrary endpoint, SQL or task-owned HTTP/auth code is
selected. Core owns transport and token refresh. Failure preserves partial
captures and grants no retry authority.

The collector writes raw responses with hashes, the original binding and
`ar-customer-task-status-evidence-v1` with `task_status`. This is explicitly
task-composed evidence, not native core output. The reviewer also accepts the
historical core-evidence schema for retained artifacts. Both use identical
matching requirements below. Missing server Run Book linkage is reported as
`DATASET_CONTEXT_MISMATCH`; do not populate it from local expectations.
The evidence timestamp/hash binds the exact supplied observation. Association
alone never establishes staging lineage, loaded row counts or business outcome.

Current runtime availability is governed by [governed read routes](governed-read-routes.md).
Exact Customer Upload attempt evidence can be collected through
`scripts/customer_attempt_collect.py` using the unchanged core REST GET client.
Its task-owned evidence schema is distinct from historical core `fbdiDiagnostics`
output. Missing or ambiguous evidence still blocks association; basic logs alone
never establish row lineage or persisted business outcomes.


`scripts/customer_attempt_review.py:analyze` checks a supplied immutable candidate,
retained execution binding and core `get_data_load_info` result. It is an offline
evidence reviewer. It does not submit an import, authenticate evidence, query
Fusion, mark a Journey complete or authorize retry.

## Retained binding

Version `ar-customer-runtime-binding-v1` contains candidate_sha256,
environment_url, operation_intent, registration_sha256, arguments_sha256,
preflight_sha256, initiation_request_id, content_id, run_id, task_code,
initiated_at and initiation_evidence_reference. Obtain these from the actual
approved preflight and initiation response; never create a synthetic production
binding merely to pass this check. Context hashes are lowercase SHA-256 hex;
request/run IDs are positive decimal strings, content_id has the UCMFA numeric
shape and task_code is ORA_AR_MANAGE_CUSTOMER_UPLOADS.

Version `ar-customer-core-status-evidence-v1` contains binding_sha256,
environment_url, captured_at, evidence_reference and core_status. Its timestamp
cannot precede initiation. A changed candidate/context invalidates the binding.
Retain the full original result as an access-controlled runtime artifact.

## Association rules

The core lookup must match the initiation request or content ID. Require exactly
one consistent data set with the matching SourceType, DataSetRequestId,
UcmContentId, RunId and RunTaskCode, and matching queried/diagnostic data-set IDs.
Missing or multiple data sets remain unresolved; no first-match selection.

Require complete FBDI diagnostics and a single customers business-object record.
All process IDs must be valid and unique; each process must belong to the same
data set. Match exactly one process for each reviewed definition:

- `JobDefinition://oracle/apps/ess/hcm/common/dataLoader/HRC_DL_MAIN`
- `JobDefinition://oracle/apps/ess/financials/commonModules/shared/common/interfaceLoader/InterfaceLoaderController`
- `JobDefinition://oracle/apps/ess/financials/receivables/customerSetup/customerProfileClasses/UploadCustomerEss`

The first process ID must equal the retained initiation RequestId. The product
definition comes from the reviewed Customers application/interface process
contract; the core/process representation is corroborated by 26D REST metadata
and a read-only GL comparison. Verify the mapping against the actual Customers
attempt in the selected environment; an example execution does not establish
association for a new candidate.

Do not infer roles from numerical ordering, display labels, success status,
ParentRequestId or AbsParentId. The observed GL processes were independent ESS
roots with ParentRequestId=0. Failed product status can still identify an attempt;
it cannot establish successful business persistence. Multiple product matches
require explicit scope review, never selection of the latest successful one.

Only a full match returns `stage_request_ids`. `staging_attempt` then creates the
existing `ar-customer-request-attempt-v1` input, with the interface process as
LOAD_REQUEST_ID scope and product process as expected UPLOAD_REQUEST_ID. The
separate staging reviewer must compare the actual product stamps; association
alone cannot prove those IDs were passed as arguments or stamped on rows.

## Interface failure before a product process is observed

`INTERFACE_FAILURE_NO_PRODUCT_OBSERVED` describes the narrower case where all
candidate/data-set/diagnostic context checks pass, the complete collection has
exactly the initiation and interface definitions, both report Error, and the
Customers record reports import ERROR and load UNPROCESSED. The separate
`interface_failure_observation` retains those two IDs. It does not invent a
product request, infer request roles from status, or certify absent targets.

The full three-stage association remains false and `stage_request_ids` remains
null; `staging_attempt` cannot manufacture a product-stage input for this case.
Pending, missing, conflicting, duplicate or incompletely collected process data
does not qualify for the narrower failure observation. Preserve the original
findings as well as the specific failure status.

Retrieve [the existing interface ESS diagnostics](ess-interface-diagnostics.md)
and verify persisted effects separately. Zero loader counters or an empty error
collection do not prove that no rows were staged or no targets changed. Do not
resubmit merely to obtain a product request or a clearer diagnostic.

The result keeps candidate_staging_lineage_verified,
persisted_reconciliation_complete, execution_authorized, retry_authorized and
journey_complete false. This helper narrows request-correlation uncertainty; it
does not resolve the remaining runtime readback or campaign readiness gates.
