# Registration and argument binding


`scripts/customer_registration_review.py` compares supplied registration evidence
with the reviewed [registration recipe](../assets/customer-registration-contract.json)
and the actual central preflight envelope. It has no Fusion client, query,
submission, retry or approval capability. Registration IDs remain run evidence;
they are not defaults in the portable recipe.

Supply `ar-customer-registration-evidence-v1` with environment_url, a timezone-aware
captured_at, evidence_reference, boolean complete and records. The records are the
complete, unfiltered exact Customers discriminator readback. Each record preserves
BUSINESS_OBJECT_ID, UI_BUSINESS_OBJECT_ID, BUS_OBJ_FILE_DISCRIMINATOR,
BUS_OBJ_TOP_DISCRIMINATOR, OBJECT_TYPE, PRODUCT_AREA, PRODUCT_FAMILY, MODULE_ID,
APPLICATION_ID, LOAD_ADAPTER_INTERFACE_ID, LOAD_ADAPTER_REF,
BUSINESS_OBJECT_VO_FQ_NAME and full LOAD_ADAPTER_CONFIG. IDs must be strings;
LOAD_ADAPTER_CONFIG is raw JSON text. Missing, truncated or multiple rows fail.
Retain capture provenance and review its freshness; relabeling an old readback
with the current time does not refresh it.

Call `analyze(candidate, operation, environment, core_envelope, evidence,
runbook_control)`. It recomputes the central envelope fingerprint, verifies exact
archive/environment/FBDI/Customers/member/account/interface routing, requires
Run Book task-code support and the active matching project binding, and compares
all configuration content with the reviewed recipe. Different validation SQL,
scope resolver, arguments, metadata, disabled status or unknown properties require
an explicit authoring review. JSON formatting alone is immaterial; duplicate keys
and nonfinite values are invalid. Comparisons distinguish booleans from numbers.

The result provides `final_data` for inclusion in the actual Task Hook preview,
once every planned rule has been evaluated. `customerFbdiBinding` retains hashes
of the candidate, full normalized registration, argument recipe, preflight,
registration evidence, reviewed contract and project Run Book binding. Do not
manufacture passed rule results or replace the central envelope with this result.

After Task Hook creates a preview, call `preview_context` with the same raw inputs
and that actual preview. It recomputes the evidence checks and requires the same
binding in `finalData`, correct task/route and ordered capture time. The resulting
context is consumed by the existing loader-validation acceptance helper.
`preview_id` is the SHA-256 of the entire retained Task Hook preview, not a server
identifier. Include any eligible gap acceptance in the normal candidate decision.

`arguments_sha256` binds `applicationArguments` **and** the scope-resolver query
and binds. For this recipe, Fusion derives the batch name and import-process
argument from the eventual interface request; document and batch IDs are null,
and mode is ESSCREATE. These future values must not be fabricated before preview.
After submission, compare actual scope/process/staging evidence with that recipe.
The recipe hash does not prove the actual five values were passed successfully.

This check does not establish freshness/authenticity by itself, prevent a server
registration edit after capture, prove UCM privileges, classify field effects,
grant approval or establish live readiness. Retain these limits in the campaign.
Core still owns immutable upload, permission enforcement, initiation and status;
the task adds no post-approval metadata request or alternate import path.
