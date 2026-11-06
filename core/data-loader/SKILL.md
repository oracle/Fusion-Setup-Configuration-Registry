---
skill_id: "core.data-loader"
name: "Data Loader"
description: "Prepare, validate, execute, monitor, and troubleshoot Oracle Fusion HCM, SCM, and ERP data loads, and generate live-metadata-grounded sample XLSX workbooks or explicitly requested DAT files for one or more registered business objects. Present every result as a complete user-friendly Markdown report. Use when Codex needs to validate or prepare ZIP, DAT, TXT, CSV, or XLSX loader files, generate sample XLSX or explicitly requested DAT files, upload content to UCM, initiate import or load operations, inspect status by request ID or UCM Content ID through dataLoaderDataSets, retrieve errors through dataSetErrors, or diagnose failed data-loading requests."
layer: "core"
pillar: "Core"
type: "import"
execution_mode: "hybrid"
owner_team: "Central platform team"
version: "0.1.0"
inputs:
  - "fusion_environment_context"
  - "data_load_source_or_registered_business_object"
  - "requested_operation"
  - "task_context"
  - "run_configuration"
  - "execution_approval"
outputs:
  - "sample_loader_file"
  - "validation_result"
  - "data_load_execution_result"
  - "data_load_status"
  - "diagnostics"
  - "inline_dashboard"
depends_on:
  - "core.auth.fusion-oauth-authentication"
uses_core:
  - "core.auth.fusion-oauth-authentication"
persists_project_state: false
workspace_outputs: []
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Updates business-object attributes through the advertised findBusinessObjectsForFSCR finder during sample/attribute retrieval and load validation; this GET operation is never automatically retried."
  - "Reads local loader files and Oracle Fusion Data Loader metadata to generate samples, validate sources, inspect status, and diagnose failures."
  - "Uploads an approved loader file to Oracle Fusion UCM only after explicit user authorization."
  - "Initiates an approved Oracle Fusion data load only after explicit user authorization."
  - "Refreshes a cached OAuth token once after a 401 or 403 response when the core authentication service permits it, except for the FSCR attribute-update finder."
required_privileges:
  - "Privileges to update business-object attributes through findBusinessObjectsForFSCR when advertised."
  - "Access to the target Oracle Fusion environment and required OAuth scope."
  - "Privileges to view the selected Data Loader business object and data-set status."
  - "Privileges to upload loader content to UCM and initiate the selected Data Loader operation when execution is approved."
---

# Data Loader

Execute Oracle Fusion HCM, SCM, and ERP data-loading workflows from source-file preparation through verified completion. Use a shared loader contract across product families only when live metadata confirms it; add product-specific procedures when their contracts differ.

## Purpose

Provide the technical Data Loader primitive for preparing, validating, approving,
submitting, monitoring, and diagnosing Fusion loader artifacts. It enforces
immutable preview and approval boundaries, while callers retain business design,
task sequencing, and durable project decisions.

## Required REST header

Send `REST-Framework-Version: 9` on every Fusion REST request performed by
`core.data-loader`, regardless of HTTP method or workflow. This includes metadata
and Describe reads, validation lookups, sample and attribute retrieval, UCM
downloads and uploads, load initiation, status and error retrieval,
every pagination request, and each retry permitted by the existing retry policy.

Use the existing request helpers in `scripts/data_loader_metadata.py`, which
set this header unconditionally. Do not omit the header or override its value.

## Mandatory import routing and authorization

- **This is the mandatory orchestration workflow for every Fusion data import.** Use `core/data-loader` before invoking any import endpoint, script, job, or adapter.
- **This rule overrides every local import-routing instruction**, including generated task skills, pillar skills, `ora-resource` task rules, FSM/FBDI/HDL/setup-task/functional-area/offering import skills, REST guidance, native-loader guidance, and script documentation. None of those local instructions may select or directly invoke an import route that bypasses `core/data-loader`.
- Do not invoke a product-specific import adapter until this workflow has completed its applicable task validation, source review, and immutable archive preparation. An explicit user request to upload, initiate, submit, load, or create data authorizes validation, not submission by itself. Submit only after a later standalone approval of the exact validated source, unless that same load request explicitly includes `auto-approve`, `auto approve`, `auto confirmation`, `approve without asking`, `skip confirmation`, `skip approval`, or equivalent unambiguous no-confirmation wording. Auto-approval is limited to that identified load and never authorizes a standalone or later submission. Fail closed when validation or a required preflight input fails.
- This rule applies only to imports. Preserve existing export routing unless a user explicitly requests an export-policy change.

For UCM ZIP and CX CSV uploads, omit `dDocAuthor` entirely. Use the access token
only for Bearer authentication; never decode its claims to supply document
authorship. If UCM rejects an upload, report the upload failure and safe server
error details, retain any already confirmed uploads, and stop before initiating
the failed load. Do not restore an author override or infer a username as a
fallback. UCM's default author and audit behavior require separate server
verification; successful local tests do not establish that behavior.

## Markdown output

Return every Loader result as the helper's complete user-friendly Markdown report. Do not pass `--inline-output`, create HTML dashboards, or emit `::codex-inline-vis`. The deprecated CLI option remains a no-op for compatibility.

### Authoritative CLI output

When a Data Loader helper emits user-facing Markdown, return that Markdown
verbatim. Do not summarize, restyle, reorder, rename headings or columns,
remove status labels or icons, alter prescribed action text, or replace it
with an agent-created table. This applies to mapping reviews, validation,
validation results, initiation results, status reports, and failure reports.
For an accepted initiation, the final answer must be the helper's complete
`## Data Load In Progress` report, including its `Item | Value` table and any
Run Book progress table. Do not add a bullet summary, file citation, prose
restatement, or any other agent-authored content before or after it.
Commentary may appear only before the helper report when needed and must not
substitute for or modify the helper's Markdown.

When a result creates or returns a local deliverable, include direct Markdown links to every requested or generated file: sample XLSX or DAT files, attribute-details workbooks, validated ZIP archives, downloaded FSM ProcessLogs, and generated non-FSM Data Loader error logs. Keep working commentary to the shortest update required by the host or to continue safely.

## Use the default environment

1. Read `../../core/auth/fusionEnv.properties` through the core `fusion-oauth-authentication` service before a live operation. Treat `environment` and `restBaseUrl` as required configuration, let the core service validate the remaining OAuth properties when it obtains a token, and use `restBaseUrl` as the Fusion host.
2. Send OAuth access tokens only as `Authorization: Bearer <token>`. Reuse the core token cache, refresh once after an HTTP 401 or 403, and fail after a second authentication response. Never persist a token inside this skill or expose a token, authorization code, or client secret in output.
3. Read the optional `runID` from `config/env.properties`. When nonblank, pass it to `initiateDataLoad`; for a task-routed load, also pass the Task Hook-approved `taskCode` as `runBookTaskCode` only when the exact live `initiateDataLoad` action declares it, including Fusion's `parameters` entry whose exact case-sensitive `name` is `runBookTaskCode`. For an FBDI route, require a positive integer and send it as a JSON number. Authentication values in that file are unsupported.
4. Use `--properties <path>` for an explicit OAuth-properties override; `--config` remains a compatibility alias with the same OAuth meaning. Use `--run-config <path>` only for an explicit initiation run-ID override.
5. Include the exact case-sensitive `runID` value in an `initiateDataLoad` request only when its configured value is nonblank. If the live action supports `runBookTaskCode`, include the exact validated Task Hook task code only for that task-routed load. If Fusion returns HTTP 400 with action error `27503`, retry once without either optional Run Book field using the same uploaded content.
6. Keep `core/auth/fusionEnv.properties` and this skill's run-ID-only `config/env.properties` updated when the user supplies replacement values. Do not print authentication material in routine output.

## Execute a data-loading request

1. Send the exact HTTP header `REST-Framework-Version: 9` with every Fusion REST request, regardless of endpoint, product family, or HTTP method. This includes metadata, describe, collection, document download, upload, initiation, monitoring, and error-detail requests. Never omit the header or substitute a different framework version.
2. Establish whether the request targets HCM, SCM, or ERP, plus the exact environment, operation, and source artifact. Infer the product family from an explicit user statement, the registered business object, or live metadata; ask only when it remains materially ambiguous. Preserve user-provided names, paths, identifiers, and payload values literally. Interpret an unqualified request to create, configure, or set up a registered business object (for example, “I need to create an inventory organization”) as a request for a create-oriented sample XLSX workbook. Interpret an explicit request for a sample XLSX or DAT file to delete records as a delete-oriented sample, not as authorization to delete Fusion data. Generate a DAT file only when the user explicitly asks for a DAT file. Do not upload or initiate a data load for either sample request. Perform a live state change only when the user explicitly asks to upload, initiate, submit, or load a file, or explicitly asks to create the object in Fusion. For a confirmed CX Import, pass internal `--cx-import-high-volume-load` only when the prompt explicitly describes that load or import as `high volume`, `high-volume`, `bulk`, `large volume`, `large-volume`, or `mass`; never infer high-volume mode from the source size, row count, or filename, and never let this option classify a source as CX.
3. Inspect the applicable file format and API contract before acting. Prefer live metadata, describe responses, supplied Postman/OpenAPI artifacts, or product documentation. Do not reuse an endpoint, payload, archive layout, or operation sequence from another Fusion loader without evidence that the contract matches.
4. Prepare the source data in the required Data Loader file format. Keep the prepared file immutable through the remaining validation gates; any source, mapping, or formatting change restarts the gates.
5. For a task-routed load, complete the normal Data Loader conversion, source review, Business Object/API validation, and final immutable upload artifact preparation first. Immediately then invoke Task Hook and complete its planned read-only task validation for that exact artifact before rendering any approval feedback or taking a UCM action. Build and retain the Task Hook preview internally only after every task rule passes or is explicitly waived. A task-validation failure is a blocker, not an approval prompt. Any subsequent change restarts Task Hook validation and approval.
6. Validate the same approved loader file against the confirmed Business Object and Data Loader API contract. Check required headers, encoding, delimiters, filenames, archive structure, record relationships, live schema, and payload shape only when those rules are established for the selected loader.
7. First complete every read-only validation, including the applicable Task Hook validation, prepare and persist the immutable upload artifact, and persist its internal preflight envelope and task preview. The read-only FBDI business-object metadata lookup runs during this validation. For an explicit load request with same-prompt `auto-approve`, `auto approve`, `auto confirmation`, `approve without asking`, `skip confirmation`, `skip approval`, or equivalent unambiguous wording, approve and verify the retained Task Hook preview when applicable, then upload the same already-validated artifact object without a confirmation question. Otherwise, make no state-changing POST and render the approval-required report only after all applicable task validation has passed; wait for a later clear contextual affirmative, such as `yes`, `go ahead`, or `submit it`. Do not require a fixed keyword. For that later submission, verify only the persisted artifact's approval-bound integrity, environment and Run Book context, plus the approved Task Hook envelope when applicable, then upload those exact bytes. Do not reopen the original source, rebuild or reconvert the artifact, refresh live metadata, repeat duplicate or reference checks, or rerun Task Hook rules. Changes to the original source do not affect an intact approved artifact; a missing or changed approved artifact or a context/envelope mismatch requires fresh validation and approval. Auto-approval is never standalone or session-wide authorization. Required source, mapping, CX object-code, task-validation, schema, authentication, and destructive-operation safeguards still block the preapproval validation.
8. Require explicit confirmation before an unrequested destructive delete, cancel, overwrite, or replacement operation.
9. Verify each state-changing response before continuing. Carry forward returned UCM content IDs, document IDs, dataset IDs, request IDs, and other server-issued identifiers rather than inventing them.
10. Report every operation as a user-friendly Markdown report using compact tables or another scannable reporting structure. Include the operation performed, HTTP or tool result, request ID when one exists, current status, and actionable errors when relevant. Every status-only request that resolves to a data set includes the data-set status plus total, loaded, and failed counts, even when the load succeeds. Label the first column `Data Set` and populate it with the exact returned `DataSetName`; fall back to `UIName`, `BusinessObject`, then `Unknown data set` only when Fusion omits it. When `dataSetErrors` returns any items, append every actionable business diagnostic and a concrete next action. Extract nested `o:errorDetails[].detail` values into separate rows, deduplicate repeated diagnostics within each returned error, and omit raw JSON, wrapper fields, technical codes, `{MESSAGE}` placeholders, and the generic HCM Data Loader Error Analysis Report guidance. For non-FSM log records, use `MessageText` only when it contains no unresolved `{...}` placeholder; otherwise use a nonblank resolved `Message`, retaining the original `MessageText` only when no usable `Message` exists. Use a compact two-column `Not available yet` table only while no data set exists. Do not create a file for a response body, diagnostic, summary, or other information unless that file is an explicitly required deliverable. A successful data-load initiation is terminal for that request: return immediately after the accepted initiation response, without polling or querying `dataLoaderDataSets` or `dataSetErrors`. For every accepted load, begin with `## Data Load In Progress`, name the friendly load type in the success sentence, and show Data Set Name plus one `Content ID(Request ID)` row with Fusion's returned values. Use `Data Loader - CX Import`, `Data Loader - FBDI`, `Data Loader - FSM`, or `Data Loader` as the friendly load type. For CX Import and FBDI only, also show Business Object Name and UCM Account. Render Run Book task display names, never task action codes. Do not show archive details, SHA-256, initiation options, credentials, configured run IDs, raw responses, or `DataSetId`.

## Task Hook routing

For a request with an already selected task code/name, retain the selected task
context until normal Data Loader validation has produced its final immutable
artifact. Then invoke the single Task Hook before any approval feedback. Its
approved envelope is the sole authoritative source for `runBookTaskCode` when
the live initiation action supports that optional parameter.

```text
python3 task-hook/scripts/task_hook.py data-load --task-context <task-context.json> --task-name <exact-task-name> --sequence <positive-sequence>
```

For a task-routed Data Loader request, invoke the `data-load` route only after normal Data Loader processing has produced the exact final immutable upload artifact, but before displaying approval feedback. It internally invokes the reusable Task Validator script and its rule-execution guide; evaluate every returned read-only rule and build the Task Hook preview for the final artifact before requesting approval. If any task rule blocks, return its user-friendly validation finding and do not display an approval request. If all rules pass, retain the preview internally and show the normal approval-required report. Do not invoke Task Validator commands directly from the Data Loader workflow.

- **Preflight gate:** Before invoking `data-load`, require Data Loader to produce
  and verify the persisted preflight for the final immutable artifact.
- **Task-routed auto-approval:** For same-prompt `auto-approve`, `auto approve`,
  `auto confirmation`, `approve without asking`, `skip confirmation`,
  `skip approval`, or equivalent unambiguous no-confirmation wording, run
  preflight and Task Hook without pausing, then submit through
  `--approved-preflight-envelope` with `--task-validation-envelope` and
  `--approve-upload`.

Use the Task Hook's `build-data-load-preview` immediately after successful rule
evaluation. Only on auto-approval or a later contextual approval use
`approve-data-load-preview`, then `verify-approved-data-load-archive`. The last
command returns the envelope object that must be written unchanged and provided
to `upload_and_initiate.py` through `--task-validation-envelope`.
Never manually create, reconstruct, or modify this envelope, or substitute a
directly generated Task Validator envelope. If it is missing or invalid, stop
submission and return through the required Task Hook workflow.

- **Missing guidance or registry:** Record `status: "not_applicable"` with the
  unavailable-guidance reason and continue without requesting a user override.
- **Blocked validation:** Stop and request correction or an explicit user
  override.
- **User override:** Record the failed resource as `status: "overridden"`, retain
  the failure evidence and user's reason, and require literal
  `allowReadinessOverride: true`. A waiver never replaces approval for the
  state-changing upload or initiation. Any changed source or prepared archive
  requires a new Task Hook validation cycle.

## Prepare reviewed source files without guesswork

1. Before uploading a user-provided DAT, TXT, CSV, or XLSX file, resolve the exact registered business object and validate its live UCM template, component attributes, mandatory flags, and key flags. Treat mandatory flags as operation guidance, not as a blanket source-column requirement.
2. For ordinary non-FSM, non-CX, non-FBDI CSV and XLSX sources, complete Mapping stage before Task Hook validation, archive approval, UCM upload, or initiation. Resolve headers in this order: exact live attribute, unique normalized technical name or live display label, reviewed glossary alias, then semantic candidates at 68% confidence with an 8-point lead. Show every non-exact mapping and automatically verify deterministic mappings; exact matches remain implicit. Unmapped, ambiguous, duplicate-target, or less-than-100%-confidence mappings block the load until resolved through `--mapping-edit SECTION/SOURCE=ATTRIBUTE|exclude` or the existing fuzzy-mapping control. Mapping resolution is required validation, not a second data-load approval. FSM, CX, and FBDI sources bypass Mapping stage and retain their native workflows. DAT, TXT, and ordinary ZIP sources retain exact validation.
3. Validate the exact source before upload. Any source, mapping, schema, or payload change requires a new explicit data-load request.

For known sections of `ADF_VO` objects, accept the exact HDL parameters `ReplaceFirstEffectiveStartDate` and `ReplaceLastEffectiveEndDate` even when absent from the UCM template and attribute metadata. Preserve supplied headers, values, and column order through XLSX/CSV conversion and generated DAT validation. These parameters remain in DAT output. Their header exemption does not establish that the Fusion component supports the effective-date change; other object types retain ordinary template validation.

4. In validation output, show `Mapped columns` for every retained automatic, user-defined, and approved-fuzzy mapping. Use the columns `Source Header`, `Mapped Attribute`, and `Match Rule`; do not show a section column.

## XLSX SET commands

An input workbook may include a visible `Set Commands` or `SetCommands` sheet
at any tab position. Match the title case-insensitively after trimming and
collapsing whitespace. Read first-row headers `Parameter` or `Parameters` and
`Value` or `Values` in either order, ignoring case and surrounding whitespace.
Trim each parameter and value; ignore incomplete pairs, empty control sheets,
and control sheets without both required headers. Hidden and very-hidden control
sheets contribute no commands. Keep ordinary workbook structure and size checks.

For example, these rows on `Set Commands`:

| Parameter | Value |
|---|---|
| PURGE_FUTURE_CHANGES | Y |

prefix the workbook's generated DAT with `SET PURGE_FUTURE_CHANGES Y` before its
first `METADATA` line. Preserve parameter spelling and literal values; do not
add a parameter allowlist. Across recognized sheets in workbook order, the last
complete value wins for each case-sensitive parameter name, while its first
occurrence determines output order. A later incomplete row does not erase a
complete value.

Control sheets are excluded from business-object discovery, `Data Loader Map`
coverage, attribute mapping, and ADF REST business-data date formatting. The
first visible business-data worksheet still identifies the root, and normal
business-data sheets and rows remain required. Each workbook contributes only
its own SET commands, including in an existing multi-XLSX submission. Conversion
occurs during preflight, before Task Hook evaluation and approval, so the retained
archive and its existing integrity digest cover the commands. Generated samples
remain unchanged; this support does not add XLSX conversion inside supplied ZIPs.

## Present every result clearly

1. Read [references/user-friendly-output.md](references/user-friendly-output.md) before returning the result of any sample generation, validation, upload, initiation, status, information, monitoring, or troubleshooting action.
2. Return the complete user-friendly Markdown report defined in [references/user-friendly-output.md](references/user-friendly-output.md), including for status-only checks. Never emit only an outcome sentence or raw helper output.
3. Treat attribute-detail, sample, initiation, status, validation, and failure requests as complete Markdown result envelopes. Keep helper progress internal unless a compact working update is required for a long-running operation; never repeat progress in the final result.
4. Do not create or update an implementation project, token-usage log, run record, diagnostic report, audit Markdown, manifest, auxiliary summary, HTML dashboard, or other unrequested attachment.
5. Keep all information required to understand or act on the result in the chat response. Do not make a generated file or link the sole source of required result details.
6. Never paste raw API responses, structured helper dictionaries, credentials, Base64 content, or long null-filled field lists into the chat unless the user explicitly requests raw output. If raw output is explicitly requested, keep the friendly report first and redact every identifier other than the request ID.
7. Show only fields that help the user understand the action, current state, failure, or next step. Every resolved status-only request shows the data-set name and status with total, loaded, and failed counts, including for successful loads. If errors are returned, follow the counts with every user-friendly business diagnostic and a concrete next action regardless of the overall status or counters. Normalize status diagnostics according to [references/user-friendly-output.md](references/user-friendly-output.md); do not display raw JSON, generic diagnostic-report guidance, placeholders, or technical error codes. If no data set exists yet, use only the compact `Not available yet` status table. Omit identifiers, attachments, and generated report artifacts from status-only output. For a successful initiation, show only the required success table. Use the one-load two-column shape for a single source or homogeneous archive and the three-column multi-load shape only when FSM ZIPs were split from a homogeneous DAT/XLSX group. For all other results, preserve the exact request ID when available, plus filenames, HTTP statuses, and every relevant server error message; hide other identifiers, including data-set IDs, UCM content IDs, document IDs, business-object IDs, and configured run IDs. Retain hidden identifiers internally only as needed to complete API calls. For object-detail requests, do not mention SourceRef handling or state that no data was uploaded or changed unless the user asks. End failed or active results with a concrete next action; do not add generic advice after completed success.
   For a direct UCM upload HTTP 403 whose response identifies `csUserInsufficientAccess` or error code `-18`, render only: `The authenticated Fusion user does not have permission to upload files to the UCM account <account>. No data load was initiated.` Direct the user to obtain access from a Fusion security administrator. Do not refresh OAuth, retry the UCM upload, or call `initiateDataLoad` after this response. Do not display the raw `errorMessage`, username, error key, or JSON response unless the user explicitly asks for the raw response.
8. The helper CLIs emit Markdown. Their Python functions may retain structured dictionaries internally, but JSON is not an external output format.
9. Provide newly generated, adapted, or requested sample data as an `.xlsx` workbook by default. When the user explicitly asks for a DAT file, create, attach, link, and present the `.dat` sample instead. DAT content is otherwise an internal representation for live validation and ZIP upload processing.

## Prepare, upload, and initiate a registered Fusion data load

1. Use an explicitly named `.zip`, `.dat`, `.txt`, `.csv`, or `.xlsx` path when supplied. Otherwise, consider only supported files actively opened, selected, attached, or shared through the IDE context. Ignore every ZIP member beneath a case-insensitive `_MACOSX` or `__MACOSX` directory during classification and validation. When two or more shared files are all `.dat` files or all `.xlsx` files, use all of them. For CX Import, `--cx-import` also accepts one or more supplied `.csv` files as one direct CSV group; preserve data-file order, detect one optional mapping by content, and package the exact ordered members once into an internal deterministic staging ZIP for approval-bound reuse. When one or more supplied ZIPs are FSM archives, where each contains a member whose basename is exactly `ASM_SETUP_CSV_METADATA.xml`, treat every FSM ZIP as its own load and submit it separately from one homogeneous `.dat` or `.xlsx` group. Classify exactly one ZIP as CX Import when the prompt identifies it as CX Import (pass `--cx-import`) or one CSV contains the complete CX mapping signature described below. Mapping filenames have no special meaning. Reject CX selections that mix direct CSVs with other source types and any archive that combines the FSM marker with a CX marker or explicit CX selection. Reject every other mixed multi-file selection and do not scan unrelated local directories.
2. Read [references/fusion-zip-rest.md](references/fusion-zip-rest.md) before using this workflow for HCM, SCM, or ERP. The `/hcmRestApi/` namespace identifies the shared Data Loader service and does not restrict registered business objects to the HCM product family. Identify an FBDI ZIP from internal CSV basenames through the advertised filename action, or legacy expanded metadata only when that action is absent, as specified in **FBDI filename routing** below. Count each CSV once per Business Object and choose the object with the highest match count. For a tie, list candidates and require an exact `--business-object` selection on a fresh preflight run. Validate one UCM account and one consistent nonblank `loadAdapterInterfaceId` for the selected object.
3. For an explicit upload/initiation request without auto-approval wording, first run `python3 scripts/upload_and_initiate.py <source-path> --preflight-envelope-output <internal-envelope-path>` without `--approve-upload`, adding `--cx-import` when the prompt explicitly identifies CX Import. Return its approval-required report and wait for a later clear contextual affirmative, such as `yes`, `go ahead`, or `submit it`; do not require a fixed keyword. After approval, run `python3 scripts/upload_and_initiate.py --approved-preflight-envelope <internal-envelope-path> --approve-upload`, adding only the same explicit `--properties`, `--run-config`, and approved `--task-validation-envelope` context when applicable. Do not pass source files, mappings, skips, Business Object selections, or CX routing inputs on that approved invocation. It verifies the persisted artifact and approval context and uploads the exact saved bytes without source conversion or live validation. Direct CSV groups use repeated `--ide-file <path>` with `--cx-import` during preapproval validation and are staged once into a deterministic internal ZIP. Auto-approval applies only to that explicit load request; it does not waive required mapping/input, task-validation, schema, authentication, or destructive-operation gates. Do not require a review-copy directory. Treat `--approved-sha256` as deprecated; the structured preflight envelope is authoritative. When a CX ZIP or CSV group has no mapping CSV, ask exactly `What is the CX Business Object code for this file?` and stop; this is required request input, not a second approval. A mapping CSV derives the code exclusively from `IMPORT OBJECT` and rejects a caller-supplied code. The helper validates the exact source, persists one immutable upload artifact with its internal envelope, and uploads only those approved bytes. A single supported file retains the existing flow; two or more homogeneous `.dat` or `.xlsx` files are combined. When FSM ZIPs accompany that group, submit the combined DAT/XLSX load first, then each FSM ZIP independently in supplied order. Use `--properties <path>` only for an explicit OAuth environment override and `--run-config <path>` only for an explicit run-ID override. For one non-CX CSV whose filename does not match its registered object, one XLSX whose 30-character root worksheet prefix matches multiple longer discriminators, or a tied FBDI ZIP, add `--business-object <exact-name>` during preapproval validation.
   A routed FBDI ZIP must be the only supplied ZIP. The initiation report shows the resolved SCM business object route, matched CSV members, and mapped UCM account after acceptance.
4. Let the script prepare the deterministic loader file or archive before the validation gates. Pass a supplied valid ZIP through unchanged and upload it with its exact original basename; this applies to ordinary, FSM, FBDI, and CX ZIP inputs. Package a single DAT file as-is; treat TXT files as preformatted HDL DAT content and rename the archive member to `.dat`; convert CSV headers and rows to `METADATA` and `MERGE` DAT records using the validated CSV filename stem, or its explicitly supplied `--business-object` discriminator. For XLSX input, use a valid legacy `Data Loader Map` as authoritative when present; otherwise resolve the first visible business-data worksheet by a case-sensitive exact registered discriminator first. Only when no exact match exists and the worksheet name is exactly 30 characters may it match the first 30 characters of a discriminator longer than 30 characters. Reject every shorter partial name, every non-exact name longer than 30 characters, and every ambiguous 30-character prefix; for an ambiguous prefix, list the candidates and require `--business-object <exact-top-level-discriminator>` on a single-XLSX retry. Resolve child and DFF sheets against that root schema by exact name or unique prefix. New workbooks never generate a map. Convert the workbook to `<validated-top-level-business-object>.dat`. Reject malformed legacy maps and any ambiguous map-free prefix. For multiple DAT or XLSX files, create one in-memory archive with members in supplied order. Multi-DAT members retain their source basenames; multi-XLSX members use their validated top-level discriminator and must be unique. Name only generated ZIP uploads `<source-stem>_YYYY-MM-DD_HH-MM-SS.zip` using local preparation time; use `combined-data-load` as the source stem for a multi-file archive. Persist the exact upload name in preflight so a later approved upload reuses it unchanged. The helper uploads only the final ZIP bytes. Keep the prepared file or archive immutable through the remaining validation gates; any source, mapping, formatting, or packaging change restarts all applicable gates.
5. Before upload, run all read-only source and metadata checks. A nonblank `runID` does not restrict eligible sources or validate the requested task. For a multi-DAT or multi-XLSX submission, validate every source independently: resolve the case-sensitive top-level discriminator through the unfiltered `findDataLoaderBos` finder, refresh the matched object through the advertised FSCR finder (falling back to the business-object detail GET only when absent or empty) and fetch its UCM DAT template, query component attributes, and validate every supplied `METADATA` section and attribute against the live schema.
6. After all source, metadata, Business Object, and Data Loader API validation has passed and the final immutable upload artifact is prepared, invoke Task Hook `data-load` for every task-routed load before presenting approval. Task Hook performs **Ora Resource Task Validation** against its exact upload bytes. Persist the resulting approved Task Hook envelope with the preflight state. Do not run a later conversion or validation step that changes the upload artifact; any approved-artifact change requires fresh validation and approval.
For two or more XLSX sources, write flushed per-workbook checkpoints to `stderr` for business-object resolution, template, sheet, and header matching, parent-child and key-metadata validation, and in-memory DAT conversion. Keep these checkpoints internal unless the operation runs long enough to require a progress update; then consolidate them into one short, nontechnical commentary update. They must never appear in the final dashboard or Markdown result. If one or more resolved business objects fail source or schema validation, report all failed and eligible objects, make no POST, and require the user to explicitly confirm skipping every failed discriminator. On the fresh retry, pass each exact discriminator as `--skip-business-object <discriminator>`, revalidate all sources, and submit only eligible objects in original order when the skip list exactly matches the current failures. Do not offer skipping for unresolved or unsafe source files, duplicate targets, environment or authentication failures, archive failures, upload failures, or initiation failures; those remain fail-closed. Do not require every attribute marked mandatory by live metadata, because required fields depend on the selected DAT operation and section and Fusion enforces operation-specific required values during import or load. Template-only DFF sections receive the same schema validation. Do not send `ProductAreaCode`. A configured nonblank `runID` is sent to `initiateDataLoad` so Fusion's backend can associate the load with its Run Book; it does not replace Ora Resource Task Validation or restrict the business objects that can be loaded. For an explicit ZIP containing a member whose basename is exactly `ASM_SETUP_CSV_METADATA.xml`, case-sensitive, classify it as FSM, preserve it unchanged, skip Business Object validation, and add `sourceType: "FSM"` only to its initiation payload. For an otherwise unclassified ZIP with CSV members, GET all pages of `dataLoaderBusinessObjects` with `q=ObjectType='FBDI'`, `expand=fbdiMetadata`, and `onlyData=true`. Match each CSV stem case insensitively against `DataFileNamePrefix` and count it once per Business Object. Choose the highest positive match count. Keep unmatched CSVs in the original ZIP. If no CSV matches, stop before upload. For a tie, list the tied objects and counts and require exact `--business-object` selection on a fresh preflight run; reject any other selection. Validate unique case-insensitive basenames, safe paths, nonempty matched files, one normalized UCM account, and one consistent nonblank scalar `loadAdapterInterfaceId` for the selected object. Persist that route before approval. For CX Import, bypass `dataLoaderBusinessObjects`, UCM DAT-template, component, attribute, and registered business-object validation except for one required read-only `objectMetadata/<ObjectCode>?fields=UcmAccount&onlyData=true` lookup during preapproval validation. Require only nonempty path-safe CSV members with unique case-insensitive basenames, zero or one content-identified mapping CSV, and at least one data CSV. Identify the mapping CSV only when its first nonblank row is `MAP NAME,MAP DESCRIPTION,IMPORT OBJECT,OBJECT DISPLAY NAME` and a later row is `COLUMN HEADER,TARGET ATTRIBUTE CODE,TARGET ATTRIBUTE DISPLAY NAME,SOURCE ATTRIBUTE CODE`, comparing trimmed cells case-insensitively in exact column order. Every nonblank metadata row before the column header must have the same nonblank `IMPORT OBJECT` value; this authoritative trimmed value is sent as `cxImportObjectName`. Without a mapping CSV, require the caller's trimmed `--cx-import-object-code` value. Require the metadata response's nonblank `UcmAccount`, convert `crm/accessGroups/import/` to `crm$/accessGroups$/import$`, show it in the approval preview, persist it in the preflight envelope, and use it for the mapping and data CSV uploads; no account fallback is allowed. Reject partial, reversed, reordered, blank, conflicting, or duplicate mapping headers. Preserve exact bytes and original data-member order. For every other explicit ZIP, inspect every DAT member, require exactly one registered root per member with no duplicate roots, validate each member against its live schema, and preserve the valid archive bytes unchanged.
7. Immediately before the first POST after a later approval, read only the persisted preflight envelope and immutable upload artifact. Verify the artifact integrity, selected environment, exact Run Book context, and approved Task Hook envelope when applicable. Do not read the original source, rebuild or extract a replacement artifact, query live schema or routing metadata, repeat duplicate/reference checks, or rerun Ora Resource Task Validation. A missing or modified artifact, malformed envelope, environment or Run Book change, or Task Hook digest mismatch blocks before upload and requires fresh validation and approval. Retain the artifact and envelopes after partial or uncertain failure for reconciliation; remove the internal preflight state after accepted initiation.
8. When configured, use the nonblank `runID` as an initiation payload property so Fusion can associate the data load with its Run Book and update task status in the backend. For a task-routed load, obtain the authoritative task code only from its approved Task Hook envelope and send it as `runBookTaskCode` only when the preapproval metadata check found that exact case-sensitive name in the exact `initiateDataLoad` action's parameter descriptors or request properties. When that preapproval metadata was unavailable, malformed, or lacked the parameter, continue with `runID` only; do not refresh it after approval. When `runID` is missing, empty, or whitespace-only, omit both Run Book fields. For FBDI, also send the approval-bound metadata value as `loadAdapterInterfaceId`; an older FBDI preflight without that value requires fresh validation and approval. For an explicitly requested high-volume CX Import, persist `cxImportHighVolumeLoad: true` during preflight and send `"cxImportHighVolumeLoad": "YES"`; omit the property for every other load and never send `"NO"`. A later approval uses only the persisted values and cannot add or change them. Sample generation and status-only operations do not use these initiation options. If the first initiation returns HTTP 400 with action error `27503`, retry exactly once without `runID` or `runBookTaskCode`, retaining `sourceType`, `loadAdapterInterfaceId`, every CX-specific field, and the returned `ContentId`; do not upload the file again.
9. Treat upload and initiation as two separate state changes. Upload the ZIP only after all applicable validation gates succeed, verify `Status=SUCCESS`, and carry the returned `ContentId` unchanged into initiation. For CX Import, upload the mapping CSV first and each data CSV in original ZIP order as ordinary CRM UCM documents without supplying `dDocName`. Retain each raw returned `dDocName` for upload reporting, but prefix the mapping ID with `M_` only when building the semicolon-joined `initiateDataLoad.contentId`; leave data IDs unchanged. Stop before initiation if any CX upload fails or omits its required content ID; report already-created documents, and do not retry, delete, or initiate a partial load.
10. Fusion's backend updates associated Run Book task status after initiation. Codex does not retrieve assigned Journey tasks or call `updateProgress`.
11. For every successful initiation, report `## Data Load In Progress`, then `The data load for <friendly load type> Load Type was initiated successfully.`, followed by a Markdown table showing the exact Data Set Name and one `Content ID(Request ID)` row containing the returned Content ID and `RequestId`. Use `Data Loader - CX Import`, `Data Loader - FBDI`, `Data Loader - FSM`, or `Data Loader` as the friendly load type in the sentence, not in the table. For CX Import and FBDI only, insert Business Object Name and UCM Account. For multiple accepted loads, use one titled table per load and identify its friendly load type in the heading. Do not write any local report, log, run record, or user-facing auxiliary file. Remove internal preflight and Task Hook envelope files after accepted initiation; retain approved artifacts and envelopes after partial or uncertain failures for reconciliation. Do not poll or call `dataLoaderDataSets` or `dataSetErrors` after initiation; those endpoints may be called only when the user explicitly asks for status, progress, results, counts, or errors.

## Validate a source file before upload

1. For an explicit pre-upload validation request, run `python3 scripts/validate_data_load_file.py <source-path>` from this skill folder. The helper checks the local source, resolves non-ZIP business objects and templates through live GET metadata, validates attributes, and prepares the deterministic upload archive entirely in memory. It does not upload content or initiate a load.
2. Return the validation Markdown report with the source file, business object, local workbook structure, live schema validation, prepared archive name, and sections. Do not expose credentials, server-issued IDs, raw REST responses, or configured run IDs.
3. Save a prepared validation archive beside its source by default; for multi-source validation, use the first source. `--output-zip <path>.zip` may select any writable destination. When that destination is not writable, require `--project-root project/<project_id>` and save under `artifacts/core/data-loader/current/mapping-reviews/` in that initialized project. Use a meaningful deterministic ZIP name based on the validated top-level discriminator, first-record user-key values, and row count; keep the full filename including `.zip` to 49 characters or fewer. Confirm every saved ZIP is non-empty and ZIP-valid, and include its direct link in the Markdown report. The ZIP is a validation deliverable only; it does not authorize UCM upload or data-load initiation.
4. Any change to the source, mapping, schema, or output archive requires another validation before upload approval.

### FBDI filename routing

Classify FSM and CX archives first. For other CSV ZIPs, inspect
`/hcmRestApi/resources/11.13.18.05/dataLoaderBusinessObjects/describe` for the
`findFbdiObjectsByFileName` custom action in `actions`. When advertised, POST to
that resource's `/action/findFbdiObjectsByFileName` using the ADF action media
type and `{"pFileName":"ATPRules,InvPickConfirmInterface123"}`: comma-separated
CSV basenames from the ZIP without `.csv`, preserving filename suffixes and
member order. Reject blank stems or embedded commas. Unwrap the action response's
`result` field when present and JSON-decode it once when it is text. Accept a
bare array for compatibility. Require the decoded value to be an array; a
`result` of `"[]"` means no matches. Missing, null, malformed, or non-array
results block without retry or fallback. Parse the array using
`BusObjFileDiscriminator` as business-object identity,
`DataFileNamePrefixes` as matching prefixes, and the same row's `UcmAccount` and
`LoadAdapterInterfaceId`. Require a nonblank identity and a nonempty array of
nonblank text prefixes. Do not use `BusinessObject` or the singular
`DataFileNamePrefix` in this action response. The action uses the shared
120-second transport timeout without retries. Describe failures, malformed
responses, and action failures block; an empty action array means no matches.

Only when the action is absent, use the existing `q=ObjectType='FBDI'` GET with
expanded `fbdiMetadata`, reading all parent and nested pages. In this fallback,
identify the business object from the parent's nonblank `BusObjTopDiscriminator`;
retain it across nested pages. Read `DataFileNamePrefix`, `UcmAccount`, and
adapter IDs from child rows. Do not substitute child `BusinessObject`, child
`BusObjFileDiscriminator`, parent `BusinessObject`, or `UIName` for this identity.

## Generate a sample XLSX workbook or explicitly requested DAT file

Workbook generation prefers the bundled `@oai/artifact-tool` writer, including
the existing `DATA_LOADER_ARTIFACT_NODE` and `DATA_LOADER_ARTIFACT_NODE_MODULES`
overrides. If Node, its module directory, or the package is missing, the helper
automatically uses a Python standard-library XLSX writer. Both writers preserve
the same files, including the attribute-details workbook for DAT samples; no
`openpyxl` installation is required. A broken installed runtime, serialization
failure, permission error, or output-validation failure remains an error and
does not trigger fallback. Use the helper in Codex, Cursor, or Claude Code;
missing spreadsheet tooling does not require manually authoring sample files.

Sample and attribute requests resolve candidates through the paginated
`dataLoaderBusinessObjects?q=BusObjTopDiscriminator LIKE '<requested-name>%' OR UIName LIKE '<requested-name>%'`
query, without a finder, TemplateFileName condition, or ProductAreaCode filter.
Keep exact discriminator selection first, then the existing normalized alias
selection, and reject missing or ambiguous matches. Before retrieving the
schema, GET `/hcmRestApi/resources/11.13.18.05/dataLoaderBusinessObjects/describe`
and check the resource's finder definitions for exact `findBusinessObjectsForFSCR`.
If advertised, GET the same versioned collection with
`finder=findBusinessObjectsForFSCR;BusObjTopDiscriminator="<resolved-discriminator>"`.
Wait synchronously for its completed response before any template, component,
or attribute request. If an object is returned, replace the lookup record
entirely with it. Require exactly one record with the resolved discriminator
and `hasMore: false`; an empty completed result retains the lookup record.
Reject ambiguous, mismatched, or malformed results.
Use the chosen record directly, including its UcmContentId and BusinessObjectId;
do not GET `dataLoaderBusinessObjects/<BusinessObjectId>` in these flows.
The finder has a 120-second transport timeout and no automatic retry. A valid
describe without that finder continues using the original record. Describe or
finder failures, timeouts, and malformed response envelopes block the request.
Existing downstream template and attribute checks remain. This sequence also applies to
attribute-details-only, mandatory-attribute, and key-attribute helpers; it does
not change Excel worksheet resolution.

Load validation preserves its existing object-identification rules, then runs
the same advertised FSCR finder for standalone sources and DAT ZIP members.
The finder updates business-object attributes despite using GET. Wait for its
completion before schema/template requests and use the returned record directly.
An absent finder or empty completed result preserves the existing object-detail
GET. Failures block validation without retries, including authentication retries.
Attribute refresh does not authorize upload or initiation; existing approval
gates still apply.

1. Treat an unqualified create/configure/set-up request as this safe sample-generation workflow. Read [references/fusion-zip-rest.md](references/fusion-zip-rest.md), then run `python3 scripts/generate_sample_dat.py <business-object> --output-dir <directory>`. Samples default to the current directory, and `--output-dir` may name any writable directory. Every XLSX sample, including one populated with supplied business values, creates `<top-discriminator>.xlsx`, `<top-discriminator>_attribute-details.xlsx`, and `<top-discriminator>_key-fields.xlsx`. The editable workbook contains the full columns, mapped values, and blank unspecified cells; the key-fields workbook retains its key-only template values. Use `--populate-json <values.json>` internally and require user mapping review for fuzzy, ambiguous, or unknown fields. Generated XLSX workbooks omit Attribute Type, `SourceRef*`, and the standard who columns `CreatedBy`, `CreationDate`, `LastUpdatedBy`, and `LastUpdateDate`. Generated XLSX sheets are plain, CSV-safe rows and columns: every populated cell is stored as text, including dates, booleans, and numeric values; blank values remain blank; and no colors, formulas, filters, panes, custom sizing, or other worksheet formatting is applied. Only when the user explicitly asks for a DAT file, add `--format dat`; its output filename is `<top-discriminator>.dat`. Use `--operation update` for an update sample, `--operation delete` for a deletion sample (`RestAction=DELETE` for non-ADF_VO objects and `DataLoaderAction=DELETE` in ADF_VO XLSX sheets), or omit it for create. For an attribute-details request, add `--attribute-details-only`; this creates only `<top-discriminator>_attribute-details.xlsx` and rejects `--format dat` or a non-create operation. Use `--properties <path>` only for an explicit OAuth environment override. The advertised FSCR finder may update business-object attributes as declared above. Do not upload content or initiate a data load while generating a sample.
2. Let the helper resolve an exact discriminator or a unique normalized UI name or template filename. Stop and list candidates after an ambiguous match.
3. Let the helper download the live UCM DAT template and preserve every parent, child, and DFF section in both XLSX files. Generated XLSX and explicit DAT samples omit `SourceRefTableName` and `SourceRef001` through `SourceRef010`; generated XLSX also omits the standard who columns `CreatedBy`, `CreationDate`, `LastUpdatedBy`, and `LastUpdateDate`, while explicit DAT keeps its existing selection. Generated fields are ordered by surrogate ID, mandatory field, user key, foreign key, then original template order. A child or DFF sheet without usable live data remains visible with headers only and produces no DAT `MERGE` record; explicit DAT samples retain their compact mandatory/key, `RestAction`, and child-linkage field selection with a row for every section. If the UCM file has no `METADATA`, sample generation alone may synthesize sections from live component and attribute metadata in parent-before-child order. This fallback never relaxes DAT, TXT, or CSV upload validation.
4. Let the helper read parent resource names only from the REST attribute `BusObjTopDiscriminator` and component resource names only from `BusObjFileDiscriminator`, with `ParentBusObjFileDiscriminator` defining the hierarchy. It probes the parent through `/fscmRestApi/resources/11.13.18.05/<parent>` and each registered child through `/<parent>/<parent-key>/child/<child>`, recursively carrying the first record's `@context.key`. Database column names such as `BUS_OBJ_TOP_DISCRIMINATOR` and `BUS_OBJ_FILE_DISCRIMINATOR` are not REST aliases. Template-only sections without registered component metadata use placeholders. Always use `restBaseUrl` from the selected OAuth properties; never substitute or hardcode an example hostname.
5. For `ADF_VO` business objects only, render generated attributes whose live metadata `DataType` is `Date` in `YYYY/MM/DD` format. Normalize safe REST-derived ISO date values to this format and use the same format for date placeholders. For `ADF_REST` business objects, treat date attributes as strings: preserve safe REST text without date parsing or normalization and use generic text placeholders. In ADF_REST XLSX sources, preserve text cells and decode native Excel date cells to their displayed date or time text for supported Excel formats; use ISO `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS` text when a format is unsupported or locale dependent. Honor the workbook's 1900 or 1904 date system and do not add a timezone. CSV and DAT date values remain text. Do not apply the `ADF_VO` date-only format to timestamp or datetime attributes.
6. For XLSX output, create one sheet per parent, child, and DFF discriminator in hierarchy order. Sheet columns preserve the exact attribute labels. Use the exact discriminator when it is legal and 30 characters or fewer; otherwise use its first 30 characters. Preserve existing names for non-colliding sections. Detect shortened-name collisions case-insensitively; assign colliding sections readable truncated aliases with `_1`, `_2`, and subsequent numeric suffixes in parent-before-child hierarchy order, keeping names at most 30 characters and skipping suffix candidates already occupied by unchanged names or prior aliases. Only when a collision exists, append a visible `Data Loader Map` to the editable and key-fields workbooks. Its exact headers are `Sheet Name`, `Discriminator`, `Parent Discriminator`, and `Business Object Name`; map every data sheet exactly once in hierarchy order using full discriminators and registered parent discriminators, with the root discriminator in `Business Object Name` only on the root row and a blank root parent. Attribute-details workbooks use the same aliases but remain map-free reference material. Illegal or reserved names (including `Data Loader Map`) and duplicate full discriminators still fail generation. A populated child-only workbook retains an empty root sheet but omits that root section from its DAT conversion. For ADF_VO objects, append workbook-only `DataLoaderAction` to every editable and key-fields sheet. During XLSX-to-DAT conversion, trimmed `DELETE` emits a `DELETE` directive; `MERGE`, blank, or a missing column emits `MERGE`; reject other values with the sheet and row. Remove that column and its cells from DAT output. Non-ADF_VO objects continue to use an exact `DELETE` in `RestAction` or the BOSS `$operation` column for the `DELETE` directive. Explicit ADF_VO DAT delete samples emit `DELETE` directly without `DataLoaderAction`. The helper performs GET requests only and never uploads or initiates a load.
7. For every successful XLSX sample, begin with `This is the generated sample files:` followed by links to the editable, attribute-details, and key-fields workbooks. Then provide a `Sections:` list and one compact `Preview — <top-discriminator>` hierarchy. For an explicitly requested DAT sample, begin with `This is the generated sample file:` followed by its file and attribute-details-workbook links. For a business-object details request, use `--attribute-details-only` and return the compact schema summary, section names, each section's attribute count, and its single attribute-details workbook link. Render the hierarchy as a narrow two-column Markdown table with `Section` and `Details` columns: show the top section first and every child or DFF section beneath it. In `Details`, summarize the first generated row with two to four identifying or configurable business-friendly `Label: value` pairs; use line breaks when supported, otherwise concise semicolon-separated pairs. Prefer user-facing labels and meaningful values over raw loader attribute names, technical IDs, `RestAction`, and `ParentIdentifier`. Do not render a separate raw Markdown table for every XLSX sheet or DAT section unless the user explicitly asks for the raw preview. Do not show operation, schema source, REST host, upload status, enrichment, fallback reasons, server IDs, or generic review text.
8. For a request naming two or more registered business objects, pass every name as an ordered positional argument to `generate_sample_dat.py`. Apply one operation to the full batch. Stage and validate every artifact before publishing any final file, and restore pre-existing targets if publication fails. Keep `--attribute-details-only` limited to exactly one business object. Return the ordered multi-object Markdown report defined in the user-friendly output contract.

## Inspect mandatory and foreign-key attributes

1. When asked for a business object's mandatory attributes, run `python3 scripts/get_mandatory_attributes.py <business-object>` from this skill folder. The helper reads live metadata only and performs no upload or local sample generation.
2. Return its Markdown title, section, and mandatory-attribute rows. Do not show a summary, success state, file section, or file links.
3. When asked for both mandatory and foreign-key attributes, run `python3 scripts/get_key_attributes.py <business-object>` from this skill folder. The helper reads live metadata only and performs no upload or local sample generation.
4. Return its Markdown title, section list, and rows labeled `Mandatory` or `Foreign key`. Do not show a summary, success state, file section, or file links.

## Inspect data-load status or information

1. Read the monitoring contract in [references/fusion-zip-rest.md](references/fusion-zip-rest.md) only when the user explicitly asks for status, progress, results, counts, errors, or other information about a data load. Never use it as an automatic follow-up to initiation.
2. Always use both `dataLoaderDataSets` and `dataSetErrors`; for each resolved non-FSM data set, additionally query `failedLines` and `dataSetAllObjects`. For `SourceType: FBDI`, also retrieve the complete ESS hierarchy with the `reviewProcessHierarchy` ADF custom action and download every available process-log attachment; treat those logs as authoritative job-level diagnostics while retaining the row/object endpoints as supplementary evidence. Do not answer from the initiation response, request ID alone, prior output, or an incomplete endpoint set.
3. For an initiation request ID or UCM Content ID, run `python3 scripts/get_data_load_info.py <request-id-or-ucm-content-id>` from this skill folder. Use `--properties <path>` only for an explicit OAuth environment override.
4. Let the helper query `dataLoaderDataSets` with `q=DataSetRequestId=<positive-integer>` for a request ID. For a UCM Content ID, require the exact form `UCMFA` followed by digits and query with the single-quoted Fusion string literal `q=UcmContentId='<exact-id>'`. Never send an unquoted UCM string filter or interpolate arbitrary text into `q`; URL encoding must preserve the quotes. Carry each returned `DataSetId` unchanged into `dataSetErrors` with `q=DataSetId=<data-set-id>`, and follow pagination. For non-FSM data sets, then query `child/failedLines` with `fields=UIName,FileLine,Message,MessageText,MessageUserDetails`, `finder=findByBusinessObject`, and `q=MessageText!='-1'`; also query `child/dataSetAllObjects` with `fields=BusObjFileDiscriminator,UIUserKey,Message,MessageText,MessageUserDetails`, `finder=findErrorMessageDetails`, and `q=OriginatingProcess in ('LOAD','VALIDATION','ORA_ROLLBACK') and MessageText != '-1'`. Follow pagination on both child resources and never retrieve or log `MessageText = '-1'` rows. In non-FSM error logs only, prefer a meaningful `MessageText`; use `Message` when it is blank, unavailable, `-1`, or the generic `{MESSAGE}` placeholder.
5. Query `dataSetErrors` even when `dataLoaderDataSets` reports success or zero error counts. If no data-set record exists yet, report that the request is not yet available for error lookup; do not invent an error query key or expose the unresolved `DataSetId`.
6. When the user asks only for status and a data set exists, run the helper with `--status-only` and always render its Markdown `Data Set` status table with total, loaded, and failed object counts, even when the load succeeds and no errors are returned. Populate `Data Set` with the exact `DataSetName`, then fall back to `UIName`, `BusinessObject`, or `Unknown data set` only when needed. For `dataSetErrors`, render a row only when `MsgText` is nonblank, preserving it exactly as returned; never use `GroupByExprVal`, nested details, or fallback text. Omit the Diagnostics section when no rows remain. For FBDI, render `ORA_FBDI_IMPORT` as `FBDI Import` and `ORA_FBDI_LOAD` as `FBDI Load`; append only actionable ESS error summaries after MsgText rows, aggregate repeats, omit operational noise and server identifiers, and continue on partial log failures. Save and link applicable FSM ProcessLogs and non-FSM error logs under the per-request Codex diagnostics directory, or an explicit `--diagnostic-log-output-dir`; FBDI ESS process logs are also applicable linked status logs. If no data set exists yet, render only a compact two-column `Not available yet` status table.

## Handle failures

- Preserve the exact HTTP status, server message, error code, request ID, and failed stage. Show only the request ID in user-facing failure output; keep all other identifiers internal.
- Distinguish authentication, authorization, file-validation, business-object-validation, UCM-upload, dataset-creation, import, load, and downstream processing failures.
- Re-inspect the live contract after a schema or payload error. Do not substitute cached metadata after a failed live lookup unless the user explicitly chooses a supplied local artifact as the source of truth.
- Render every failure as a Markdown error report. Do not persist diagnostics, logs, run records, summaries, HTML dashboards, or other failure artifacts unless the user explicitly requests a specific file.
- Do not claim success until the requested server-side action is accepted and its returned status is verified.

## Extend the skill

Add product-specific references and deterministic scripts only when concrete workflows, endpoints, file examples, and expected results are available. Keep the core workflow generic and route each future product procedure explicitly.
