# Fusion file-to-ZIP REST workflow

Use this contract for HCM, SCM, and ERP business objects registered with Fusion Data Loader when the target environment's live `dataLoaderDataSets/describe` metadata exposes `initiateDataLoad` and its Fusion Documents endpoint accepts uploads at `/documents/files/data`. The `/hcmRestApi/` namespace identifies the shared Data Loader service; it does not mean the registered business object must belong to HCM.

## Required REST framework header

- Send `REST-Framework-Version: 9` with every Fusion REST request in this workflow, including GET and POST requests.
- Apply it to business-object metadata, UCM document downloads, FSCM describe and collection probes, uploads, initiation, status monitoring, and error queries.
- Do not invoke a Fusion REST endpoint without this header and do not substitute another version.
- Read OAuth properties from `core/auth/fusionEnv.properties`, use `restBaseUrl` as the host, and obtain a Bearer token through `core/auth/fusion-oauth-authentication`. Refresh and retry exactly once after HTTP 401 or 403, except for the FSCR attribute-update finder; do not retry other failures.

## Sample and attribute metadata lookup

For samples and attribute queries, page through the latest business-object
collection using `q=BusObjTopDiscriminator LIKE '<name>%' OR UIName LIKE '<name>%'`
without a finder. Escape literal wildcard and quote characters and URL-encode
the query. Preserve exact/alias resolution. Describe
`/hcmRestApi/resources/11.13.18.05/dataLoaderBusinessObjects/describe`; when it
advertises `findBusinessObjectsForFSCR`, call the versioned collection with
`finder=findBusinessObjectsForFSCR;BusObjTopDiscriminator="<discriminator>"`.
Wait for completion before schema requests. Require one matching discriminator
and `hasMore: false`, or an empty completed result. Replace the lookup record
with the returned record; an empty result or absent finder retains the lookup.
Use that record's `BusinessObjectId` and `UcmContentId` directly, omitting the
object-detail GET. Malformed responses and request failures block. The finder
has a 120-second timeout and no automatic retries, including authentication.
XLSX root searches use only the discriminator prefix without a finder.

Load validation preserves its existing object-identification rules, then uses
the same advertised FSCR finder for standalone sources and DAT ZIP members.
This finder updates business-object attributes despite using GET. Wait for it
before checking `UcmContentId` or requesting the template, and use its returned
record directly without an object-detail GET. An absent finder or empty result
preserves validation's existing object-detail GET. Finder failures stop
validation and must not be retried, including after an authentication failure.
Attribute refresh does not authorize upload or initiation; existing approval
gates still apply.

## Source selection

- Prefer an explicit `.zip`, `.dat`, `.txt`, `.csv`, or `.xlsx` path.
- Otherwise use only files shared through IDE context, such as opened, selected, or attached files.
- Accept one supported candidate as-is. When two or more IDE candidates are all `.dat` files or all `.xlsx` files, validate and combine them into one archive. When one or more FSM ZIPs accompany one homogeneous DAT or XLSX group, initiate the combined group first and each FSM ZIP as a separate load in supplied order. Reject every other mixed multi-file selection and homogeneous groups of other formats.
- Reject unsupported, missing, empty, duplicate-basename, ambiguous, or malformed inputs before making a request.

## Registered business-object validation

- Before preparing DAT, TXT, CSV, or XLSX input, call `GET /hcmRestApi/resources/latest/dataLoaderBusinessObjects?finder=findDataLoaderBos&onlyData=true&limit=500&offset=<n>` with the configured authentication. For a combined submission, perform this validation independently for every source before creating the ZIP or making any POST request.
- Do not filter by `ProductAreaCode`. Follow pagination until `hasMore` is false so registered HCM, SCM, and ERP objects are all eligible.
- Require the case-sensitive source filename stem to match exactly one `BusObjTopDiscriminator`. For one CSV or XLSX input only, `--business-object <discriminator>` may provide an exact top-level discriminator; for XLSX it must also match the root worksheet exactly or match its 30-character prefix when the selected discriminator is longer than 30 characters. Reject this override for every other format or a multi-file submission. Read registered parent names only from this REST attribute; `BUS_OBJ_TOP_DISCRIMINATOR` is a database column name, not a REST alias.
- After identification, perform the advertised FSCR finder refresh described above. Use its returned record directly, or fetch `GET /hcmRestApi/resources/latest/dataLoaderBusinessObjects/<BusinessObjectId>` when the finder is absent or empty. Require the selected record's `UcmContentId`, then download `GET /documents/files/<UcmContentId>/data`.
- Parse every live-template `METADATA` section as a case-sensitive discriminator and attribute schema. Normalize only `SourceRefTableName=<value>` and `SourceRef001` through `SourceRef010=<value>` to their base attribute names.
- Fetch paginated `childBusinessObjects`, then fetch paginated `child/attributes` with the documented field list for every mapped template section.
- Validate every DAT or TXT `METADATA` section and the CSV header section. Reject unknown sections and unknown or duplicate attributes. Do not reject omitted attributes solely because live metadata marks them mandatory: whether a field is required depends on the selected DAT operation and section, and Fusion validates that contract during import/load.
- Validate DFF and other template-only sections against the same UCM schema rules. Keep mandatory metadata available for generation and guidance, but do not turn it into a blanket pre-upload requirement.
- For two or more XLSX sources, emit flushed `stderr` progress in supplied order: workbook start, exact business-object resolution, live template/sheet/header match, parent/child and key-metadata validation, and in-memory DAT conversion. Continue through all sources before any POST. When resolved source/schema failures occur, report failed and eligible business objects and make no POST. A fresh retry may omit only every currently failed discriminator by passing each exact `--skip-business-object <discriminator>` after the user explicitly confirms; revalidate all sources and require that skip list to exactly match the current failures. Unresolved, unsafe, duplicate, authorization, archive, upload, and initiation failures remain fail-closed. Single XLSX, DAT, ZIP, and FSM flows remain quiet.
- Fail at `business-object-validation` before DAT generation, archive creation, UCM upload, or initiation when any metadata request, template parse, or validation fails.

## Run Book association

- A nonblank `runID` is sent to `initiateDataLoad`; it never validates, filters, or excludes a source before upload.
- For a task-routed load, use only the exact `taskCode` from the approved Task Hook envelope as `runBookTaskCode`, and only if the exact preapproval live `initiateDataLoad` action declares it through a parameter descriptor whose exact case-sensitive `name` is `runBookTaskCode` or through an equivalent request-property key. Persist that capability in the preflight envelope and do not refresh it after approval. Do not add a CLI or run-configuration override for the task code.
- If metadata is unavailable, malformed, or does not declare `runBookTaskCode`, initiate with `runID` only. Fusion's backend updates task status after initiation; Codex does not retrieve assigned Journey tasks or call `updateProgress`.

## Sample XLSX and explicit DAT generation

Workbook generation prefers the bundled `@oai/artifact-tool` writer, including
the existing `DATA_LOADER_ARTIFACT_NODE` and `DATA_LOADER_ARTIFACT_NODE_MODULES`
overrides. If Node, its module directory, or the package is missing, the helper
automatically uses a Python standard-library XLSX writer. Both writers preserve
the same files, including the attribute-details workbook for DAT samples; no
`openpyxl` installation is required. A broken installed runtime, serialization
failure, permission error, or output-validation failure remains an error and
does not trigger fallback. Use the helper in Codex, Cursor, or Claude Code;
missing spreadsheet tooling does not require manually authoring sample files.

- Generate an `.xlsx` workbook by default. Emit a `.dat` file only when the user explicitly asks for one.
- Run `python3 scripts/generate_sample_dat.py <business-object> [<business-object> ...] [--output-dir <directory>] [--operation update]`. Generated files default to the current directory, and `--output-dir` may name any writable directory. The default filename is `<top-discriminator>.xlsx`; use `--format dat` for the explicitly requested `<top-discriminator>.dat`. Omitted operation means create (`POST`).
- For multiple registered business objects, pass every discriminator, UI name, or template filename as an ordered positional argument. Preserve requested business-object order, reject duplicate resolved roots, and validate the complete staged batch before atomically publishing it; a failure preserves existing targets and publishes no partial batch. `--populate-json` and `--mapping-edit` are limited to one business object.
- For an attribute-details request, run `python3 scripts/generate_sample_dat.py <business-object> --attribute-details-only`. Retrieve the same live schema and product metadata, create only `<top-discriminator>_attribute-details.xlsx`, and do not probe sample collection rows or create the editable or key-fields workbooks. It accepts exactly one business object and rejects `--populate-json`, `--format dat`, and a non-create operation.
- Resolve an exact discriminator first. If none matches, accept only a unique normalized `UIName` or `TemplateFileName` stem; return candidates for ambiguity.
- Preserve all live-template sections and their order. Generated XLSX and explicit DAT samples omit `SourceRefTableName` and `SourceRef001` through `SourceRef010`, while retaining all other template attributes. Generated fields are ordered by surrogate ID, mandatory field, user key, foreign key, then original template order. XLSX samples retain visible header-only child/DFF sheets when no usable live child data exists; explicit DAT samples use mandatory fields, key fields, `RestAction`, and child `ParentIdentifier` for mapped components, and every non-SourceRef template field for template-only sections.
- Read component resource names only from the REST attribute `BusObjFileDiscriminator` and their hierarchy only from `ParentBusObjFileDiscriminator`. The uppercase underscore forms are database column names and are not REST aliases. If the downloaded UCM file contains no `METADATA`, sample generation may synthesize sections from paginated `childBusinessObjects` and attribute metadata. Order the top component first and every child after its parent. Empty attributes, duplicate discriminators, missing parents, and hierarchy cycles remain failures. Upload validation does not use this fallback.
- Probe the registered parent through `GET <configured-host>/fscmRestApi/resources/11.13.18.05/<BusObjTopDiscriminator>/describe` and its matching collection. Build every registered child path from the actual first parent record as `/<parent-collection>/<@context.key>/child/<BusObjFileDiscriminator>`, then repeat the same rule recursively for deeper children. Percent-encode discriminators and keys. Keep every probe within that single record lineage; never retry a child as a top-level resource.
- Require an exact resource name in each describe response, intersect its attributes with the selected DAT fields, then request only that intersection with `?fields=<fields>&limit=1&onlyData=true`. If a parent record, `@context.key`, or child collection is unavailable, use section-level fallback and mark all dependent descendants as unavailable. Template-only DFF or other sections without a registered `BusObjFileDiscriminator` use UCM-schema placeholders without a REST probe.
- Always derive the host and Bearer token from the selected OAuth properties. The `11.13.18.05` path and discriminator convention are reusable; example pod hostnames are not.
- Render every generated attribute whose live metadata `DataType` is `Date` as `YYYY/MM/DD`. Normalize both safe REST-derived dates and deterministic date placeholders to this format; keep timestamp and datetime formats unchanged.
- Use safe non-null strings, numbers, booleans, dates, and timestamps from only the first returned record. Reject complex, empty, delimiter-bearing, line-breaking, or over-`DataLength` values and keep the deterministic placeholder for those fields.
- Treat authentication or authorization errors, 404s, unmatched resources, empty collections, malformed responses, missing fields, null values, and unavailable parent item routes as section-level fallback conditions, not sample-generation failures.
- Every XLSX sample creates editable, attribute-details, and key-fields workbooks. A populated XLSX applies prompt-supplied values only to the editable `<top-discriminator>.xlsx`; its key-fields workbook retains key-only template values. Unspecified editable cells remain blank and fuzzy, ambiguous, or unknown fields require mapping review. Store each section in its own sheet with exact attribute labels as headers; use the first 30 characters only when the discriminator is longer. Preserve all non-colliding names. Detect collisions case-insensitively and assign readable truncated aliases with `_1`, `_2`, and subsequent numeric suffixes in parent-before-child hierarchy order, keeping aliases at most 30 characters and skipping names occupied by unchanged sheets or prior aliases. Only for collisions, append a visible `Data Loader Map` to editable and key-fields workbooks with exact headers `Sheet Name`, `Discriminator`, `Parent Discriminator`, and `Business Object Name`. Map every data sheet exactly once in hierarchy order to its full discriminator and registered parent discriminator; set `Business Object Name` to the root discriminator only on the root row, whose parent is blank. Attribute-details workbooks use the same aliases but remain map-free reference material. Continue rejecting illegal or reserved names (including `Data Loader Map`) and duplicate full discriminators. During child-only populated XLSX conversion, retain the empty root worksheet but omit its DAT `METADATA` and data records. For explicit DAT output, write ordered `METADATA` and `MERGE` records for each populated section.
- When converting an XLSX workbook to DAT, an exact `DELETE` in `RestAction` or a BOSS `$operation` column emits a `DELETE` record directive. All other values retain the `MERGE` directive.
- Sample generation performs GET requests only and never uploads or initiates a load. Return only the prescribed sample or attribute-details report; keep the schema source, configured REST host, enrichment counts, fallback reasons, and raw REST records internal.

### Mocked forward-test guidance

- Record every request and assert every URL starts with `restBaseUrl` supplied in the test OAuth properties; reject any hardcoded pod hostname.
- Return an exact parent describe resource and `@context.key`, then assert direct and deeper children use nested collection paths. Cover independent 401, 403, 404, empty, malformed, missing-key, null, complex, delimiter-bearing, and oversized cases.
- Assert only intersecting fields are requested with `limit=1&onlyData=true`, only the first record is considered, enriched sections use `PATCH`, and fallback-only sections use `POST`.
- Exercise a comment-only UCM file with out-of-order components and assert synthesized sections are parent-before-child. Run the same file through upload validation and assert no POST is made.
- Fail the test if sample generation invokes any non-GET operation or emits raw REST record values in its Markdown report.

## XLSX SET commands

An input workbook can supply control rows on visible sheets named `Set Commands`
or `SetCommands`, matched case-insensitively with surrounding/inter-word
whitespace normalized. Read `Parameter`/`Parameters` and `Value`/`Values` headers
from the first row in either order, ignoring case and trimming whitespace.
Trim names and values; ignore incomplete pairs, empty control sheets, missing
required header columns, and hidden or very-hidden control sheets. Ordinary
workbook structure, coordinate, header-width, and output-size checks still apply.

For example, a `Parameters` / `Value` row containing `PURGE_FUTURE_CHANGES` / `Y`
produces `SET PURGE_FUTURE_CHANGES Y` before the first `METADATA` line. Preserve
parameter spelling and literal values without a parameter allowlist. Across
recognized sheets in workbook order, use the last complete value for each
case-sensitive parameter name, retaining first-occurrence order. Incomplete
later rows do not overwrite complete values.

Exclude these control sheets from business-object discovery, legacy-map coverage,
attribute mapping, and ADF REST business-data date formatting. Required data
sheets and rows remain required; the first visible business-data sheet identifies
the root. Each workbook's commands prefix only its own generated DAT, including
in existing multi-XLSX groups. Perform this conversion during preflight before
Task Hook validation and approval; the saved artifact's existing digest binds
the resulting bytes. Keep generated samples and submission interfaces unchanged.
This does not add XLSX conversion inside supplied ZIPs.

## Archive preparation

For ordinary CSV and XLSX sources, complete Mapping stage before archive preparation. FSM, CX, and FBDI classification occurs first and bypasses Mapping stage. DAT, TXT, and ordinary ZIP inputs are schema-validated without header mapping. Mapping decisions are stored beside the source when possible, with a protected repository-local fallback; source or live-schema changes invalidate them.

- Ignore every member beneath a case-insensitive `_MACOSX` or `__MACOSX` directory for normal, FSM, CX, and FBDI archive classification and validation. Do not let AppleDouble sidecars or copied marker filenames in those folders create duplicate mappings, opaque-member failures, or false source-type markers. Preserve the original archive bytes where normal, FSM, or FBDI pass-through requires them; CX uploads only the meaningful CSV member bytes.
- Preserve supplied valid ZIP bytes and their exact original basename unchanged for UCM upload. This mandatory rule applies to ordinary, FSM, FBDI, and CX ZIP inputs. Persist that basename in preflight and reuse it unchanged after approval. A ZIP with a member whose basename is exactly `ASM_SETUP_CSV_METADATA.xml` is an FSM archive; do not transform or inspect its CSV/XML members as DAT content.
- A prompt-declared `--cx-import` ZIP, or one containing a content-identified mapping CSV, is CX Import; filenames have no mapping semantics. Identify a mapping only when its first nonblank row contains `MAP NAME,MAP DESCRIPTION,IMPORT OBJECT,OBJECT DISPLAY NAME` and a later row contains `COLUMN HEADER,TARGET ATTRIBUTE CODE,TARGET ATTRIBUTE DISPLAY NAME,SOURCE ATTRIBUTE CODE`. Decode with optional UTF-8 BOM, trim header cells, compare case-insensitively, and require exact column order. Reject partial, reversed, reordered, or duplicate mapping headers. Reject an FSM marker combined with either CX signal. Require one ZIP containing only nonempty, path-safe CSV members with unique case-insensitive basenames, zero or one mapping CSV, and at least one non-mapping CSV. Nested safe paths are allowed. When no mapping CSV exists, ask `What is the CX Business Object code for this file?` and require the user-provided code; never infer it from filenames or context. Preserve every CSV byte and the original data-member order. CX Import bypasses every `dataLoaderBusinessObjects`, DAT-template, component, attribute, and business-object validation request.
- Classify an otherwise unclassified ZIP with CSV members using the [FBDI filename routing contract](../SKILL.md#fbdi-filename-routing). Describe the versioned resource first; use advertised `findFbdiObjectsByFileName` with CSV basenames and parse `BusObjFileDiscriminator` plus `DataFileNamePrefixes`, unwrapping `result` when present. Only when the action is absent, use paginated `GET dataLoaderBusinessObjects` with `q=ObjectType='FBDI'`, `expand=fbdiMetadata`, and `onlyData=true`; use the parent `BusObjTopDiscriminator` as identity and child `DataFileNamePrefix` for matching. Describe/action failures or malformed results block without fallback or retry. Match CSV stems case insensitively, counting each CSV once per Business Object. The object with the highest positive count supplies the route; preserve all original ZIP members, including unmatched CSVs. If no CSV matches, stop before upload. If several objects tie for the highest count, present their names and counts and require an exact `--business-object` selection on a fresh preflight run. Validate the selected object has one normalized UCM account and a consistent nonblank scalar `loadAdapterInterfaceId`; reject malformed or incomplete metadata, unsafe paths, duplicate case-insensitive basenames, and empty matched files. Persist the selected route and original ZIP bytes before approval, and reuse them unchanged after approval.
- Package a DAT file unchanged inside `<stem>.zip` using its original DAT basename.
- Treat a TXT file as preformatted UTF-8 Data Loader DAT content and package it inside `<stem>.zip` as `<stem>.dat`.
- After live validation, parse a UTF-8 CSV using its first row as attributes and its filename stem exactly as the business-object discriminator, unless a single-CSV `--business-object` override supplies the validated discriminator. Emit `METADATA|<discriminator>|<attributes>` followed by one `MERGE|<discriminator>|<values>` record per nonempty row, then package `<discriminator>.dat` inside `<source-stem>.zip`.
- For XLSX input, accept a valid `Data Loader Map` sheet as authoritative for mapped sections and the root business object; reject duplicate, stale, malformed, incomplete, or conflicting map entries. Without a map, resolve the first visible business-data worksheet against the live top-object finder by case-sensitive exact discriminator first. Only when there is no exact match and the worksheet name is exactly 30 characters may it match discriminators longer than 30 characters by their first 30 characters. Reject shorter partial names and non-exact names longer than 30 characters. When that 30-character prefix matches multiple long discriminators, list the candidates and require `--business-object <exact-discriminator>` for a single-XLSX retry. Resolve remaining child/DFF sheets against the selected root schema by exact discriminator or unique prefix. Reject zero or multiple root matches, unknown or ambiguous sheet prefixes, a non-root first business-data worksheet, or a root worksheet without a data row unless child/DFF data exists. Convert validated headers and nonempty rows to in-memory DAT records, retaining `METADATA` without `MERGE` for a header-only child/DFF sheet; package that DAT as `<validated-top-level-business-object>.dat`, and retain the source filename stem for the ZIP name.
- Parse XLSX worksheets sparsely: skip empty row gaps while retaining physical Excel row numbers in diagnostics. Reject coordinates beyond row 1,048,576 or column 16,384 (XFD), duplicate cell coordinates, and populated cells beyond the header width. Empty or styled-only cells must not enlarge the output. Preserve a missing first-row header as an error; never promote a later row into the header. Bound each worksheet to 1,000,000 materialized output cells, including header cells. These checks run during existing preflight conversion before Task Hook validation and approval.
- Accept internal XLSX relationship targets expressed relative to their source part or from the package root with a leading `/`. Normalize package-root targets to ZIP member paths while continuing to reject external relationships, parent traversal through `..`, empty targets, and targets that resolve outside the package.
- Reject CSV files with no header, empty header names, no data rows, excess row values, malformed quoting, or fields containing DAT delimiters or line breaks.
- Create generated archives once. For same-request auto-approval, retain the exact ZIP object in memory through upload. For later approval, atomically persist the immutable artifact and a restrictive internal preflight envelope that binds its integrity, filename, ordered sources, source type, environment, Run Book context, mappings, routing, and business objects. Base64-encode the complete ZIP bytes, not the original DAT, TXT, or CSV bytes. Do not expose or link internal artifact or envelope paths in user-facing reports.
- Use the final UCM ZIP name as both `fileName` and `dataSetName`: the exact original basename for a supplied ZIP, or the timestamped name for a generated ZIP.
- For two or more IDE DAT files, create the ZIP in memory with each supplied DAT under its original basename and in supplied order; upload it as `combined-data-load_YYYY-MM-DD_HH-MM-SS.zip`.
- For two or more IDE XLSX files, independently resolve and validate each workbook, convert it to `<validated-top-level-business-object>.dat`, reject duplicate resulting member names, and create the ZIP in memory with the DAT members in supplied order; upload it as `combined-data-load_YYYY-MM-DD_HH-MM-SS.zip`.
- Do not write combined DAT members or the generated ZIP to disk.

## Upload to UCM

For an explicit upload or initiation request without same-prompt auto-approval wording, first invoke the CLI without `--approve-upload` and with `--preflight-envelope-output <internal-envelope-path>`. It validates the exact source, creates and persists the immutable upload artifact, and records its approval-bound preflight envelope. When a task is selected, immediately invoke the Data Loader Task Hook, evaluate its read-only rules, and build its preview for that exact artifact before returning any approval-required report. A task-validation failure returns its blocker and must not display an approval request. On success, retain the preview internally and return the approval-required report without a POST, hash, or internal-path display. After a later clear contextual affirmative, approve and verify the retained Task Hook preview when applicable, then invoke the CLI with `--approved-preflight-envelope <internal-envelope-path> --approve-upload` and the approved task envelope. The approved invocation verifies artifact integrity plus environment and Run Book context, then uploads the persisted bytes without reopening source files, reconverting, rebuilding, refreshing live metadata, repeating duplicate/reference checks, or rerunning Task Hook rules. Source changes after approval do not affect the persisted artifact. Missing or modified approved artifacts and envelope/context mismatches block before the first POST and require fresh validation and approval. With same-prompt `auto-approve`, `auto approve`, `auto confirmation`, `approve without asking`, `skip confirmation`, `skip approval`, or equivalent unambiguous no-confirmation wording, complete validation and construction once, then upload that same in-memory object; this applies only to that exact load and never authorizes a standalone or later submission. Validation remains exact and case-sensitive: reject unmapped, unknown, or duplicate attributes rather than inferring a mapping or adding fields. Required mapping, CX object-code, task-validation, schema, authentication, and destructive-operation gates still block preapproval validation. Do not reject an omitted attribute solely from its live mandatory flag; Fusion enforces the operation-specific required-value contract. `--approved-sha256` is deprecated; the structured preflight envelope is authoritative.

Send `POST /documents/files/data` with OAuth Bearer authentication and:

```http
Content-Type: multipart/form-data; boundary=<generated boundary>
Accept: application/json
REST-Framework-Version: 9
```

The multipart form must contain exactly these parts:

- `metadataValues`: UTF-8 JSON with `dDocTitle` set to the ZIP basename, `dSecurityGroup` set to
  `FAFusionImportExport`, and `dDocType` set to `Document`. Set `dDocAccount`
  to `setup$/functionalSetupManager$/import$` for an FSM archive (one with an
  `ASM_SETUP_CSV_METADATA.xml` member), to the exact mapped `ucmAccount` for an
  FBDI archive, and otherwise to `hcm$/dataloader$/import$`.
- `primaryFile`: the exact approved ZIP bytes with the ZIP basename as its
  multipart filename and `application/zip` content type.

Do not base64 encode the ZIP. Continue only when the JSON response contains a
nonblank top-level `dDocName`; use that value as the Data Loader `contentId`.

Omit `dDocAuthor` from all upload metadata. Treat the access token as an opaque
Bearer credential and never decode its claims for document authorship. If UCM
rejects the upload, return the structured `ucm-upload` failure with redacted
server error details; do not retry by adding an author or initiate the failed
load. Preserve any previously confirmed uploads. Server-assigned author and
audit identity must be verified separately in the target environment.

For CX Import, accept either one CX ZIP or one direct group of CSV files. Resolve the object-specific `dDocAccount` before approval with `GET /crmRestApi/resources/11.13.18.05/objectMetadata/<url-encoded-ObjectCode>?fields=UcmAccount&onlyData=true`. Require a nonblank `UcmAccount` string and convert it to UCM account syntax; for example, `crm/accessGroups/import/` becomes `crm$/accessGroups$/import$`. Upload one multipart request per CSV. Upload the optional mapping CSV first, then data CSVs in ZIP-member or direct-source order, all to that recorded account. Direct groups require unique case-insensitive CSV basenames, at least one data CSV, and deterministic one-time packaging into an internal staging ZIP that preserves exact member bytes, roles, and order. After approval, extract those recorded members from the verified staging artifact without reading the original CSVs or resolving metadata again. Every upload uses the CSV basename as `dDocTitle`, `CRM` as `dSecurityGroup`, `Document` as `dDocType`, and the exact CSV bytes as `primaryFile` with `text/csv`. Do not send `dDocAuthor` or `dDocName` for either mapping or data CSVs; require every response to return a nonblank generated `dDocName`. Retain those raw IDs when reporting created UCM documents. If an upload fails or omits its expected ID, stop without initiation, retry, or cleanup and report all documents already created. Retain the approved artifact and envelopes for reconciliation after partial or uncertain failures.

## Initiate import and load

Read the optional `runID` only from the selected Data Loader run configuration, defaulting to `core/data-loader/config/env.properties`, and trim surrounding whitespace. Send `POST /hcmRestApi/resources/latest/dataLoaderDataSets/action/initiateDataLoad` with the same OAuth authentication and headers, preserving the existing import-and-load options:

```json
{
  "contentId": "<returned dDocName>",
  "fileAction": "IMPORT_AND_LOAD",
  "dataSetName": "<zip basename>",
  "importConcurrentThreads": 8,
  "loadConcurrentThreads": 8,
  "importMaxErrorPercentage": 100,
  "loadMaxErrorPercentage": 100,
  "fileEncryption": "NONE",
  "verificationKey": null,
  "startDate": null,
  "deleteSourceFileFlag": "Y",
  "generateMappingFileFlag": "N",
  "uiInvoke": "Y"
}
```

When `runID` is present and nonblank, add it to the payload. For a task-routed load whose approved Task Hook envelope supplies `taskCode`, add that exact value as `runBookTaskCode` only when the persisted preapproval action-capability result says the action declares the parameter. For FBDI, require a positive integer before UCM upload and serialize `runID` as a JSON number; for other routes, preserve the exact configured string. Omit both Run Book fields when `runID` is missing, empty, or whitespace-only. If the preapproval metadata was unavailable or did not declare the task-code parameter, retain `runID` only; do not inspect action metadata again after approval. If the server returns HTTP 400 with `o:errorCode` `27503` and a detail stating that the request does not represent an action, retry this action exactly once without `runID` or `runBookTaskCode`; retain the already returned `ContentId` and do not upload again.

For an FSM archive, add `"sourceType": "FSM"`; for a routed FBDI archive, add `"sourceType": "FBDI"` and the exact approval-bound `"loadAdapterInterfaceId": <metadata-value>`. Do not add either FBDI property to ordinary registered Data Loader, FSM, or CX loads. Persist the FBDI adapter ID before approval and reuse it without refreshing metadata afterward. A missing or malformed value, conflicting matched-row values, or an older FBDI preflight without the field blocks before UCM upload and requires fresh validation and approval. FSM and FBDI archives do not resolve registered DAT business objects; on the one-time `27503` retry, retain `sourceType` and `loadAdapterInterfaceId` while omitting both optional Run Book fields.

For CX Import, use the original ZIP basename as `dataSetName` and add `"sourceType": "ORA_CX_IMPORT"`. Build `contentId` in mapping-first upload order: prefix only the mapping CSV's returned `dDocName` with `M_`, leave every data CSV ID unchanged, and join the resulting values with semicolons and no spaces. For example, a mapping ID `UCMFA495444` and data ID `UCMFA125006` become `M_UCMFA495444;UCMFA125006`. Always add `"cxImportObjectName"` using the trimmed `IMPORT OBJECT` value from the mapping CSV; every nonblank metadata row before `COLUMN HEADER` must provide the same nonblank value. Without a mapping CSV, require the caller to supply `--cx-import-object-code <ObjectCode>` and use its trimmed value. A mapping CSV rejects this option, and no object-name fallback is allowed. When the originating prompt explicitly describes the confirmed CX load or import as high volume, high-volume, bulk, large volume, large-volume, or mass, pass internal `--cx-import-high-volume-load`, persist `cxImportHighVolumeLoad: true` in the preflight envelope, and add `"cxImportHighVolumeLoad": "YES"` to initiation. Never infer this setting from file size, row count, or filename; omit the payload property otherwise and never send `"NO"`. The high-volume option does not classify a source as CX and cannot be added to an approved preflight submission because its persisted value is authoritative. Older approved envelopes without the field behave as `false`, while a non-boolean value blocks before upload. Preserve all standard `IMPORT_AND_LOAD` options and optional Run Book fields. On action error `27503`, retry initiation once after removing `runID` and `runBookTaskCode`, retaining every CX field and the already-uploaded documents; never re-upload CSVs.

Accept initiation only when `result.Status` is `SUCCESS` and `result.RequestId` is nonempty. Do not return or report the configured run ID. This response confirms asynchronous submission, not completion. Begin the report with `## Data Load In Progress`, then show the exact data-set name, Load Type, UCM content ID, and returned `RequestId` labeled `Request ID`. Use `Data Loader - CX Import`, `Data Loader - FBDI`, `Data Loader - FSM`, or `Data Loader` as the friendly load type. For CX Import and FBDI only, also show business object name and UCM account. Render Run Book task display names rather than task action codes. Do not show archive details, SHA-256, initiation options, raw responses, or `DataSetId`, and do not poll or query either status endpoint unless the user explicitly asks for status, progress, results, counts, or errors.

When `runID` is nonblank, include it in `initiateDataLoad` so Fusion can associate the accepted archive with its Run Book. Fusion's backend updates task status; Codex does not retrieve assigned Journey tasks or call `updateProgress` after initiation.

## Monitor status and errors

Only for an explicit user request for status, progress, results, counts, errors, or other data-load information, query both endpoints in this order. Do not run this workflow automatically after initiation:

1. Resolve the data set using one of these filters:
   - Request ID: `GET /hcmRestApi/resources/latest/dataLoaderDataSets?q=DataSetRequestId=<positive-integer>&onlyData=true&limit=500&offset=<n>`.
   - UCM Content ID: first require the exact form `UCMFA` followed by digits, then use `GET /hcmRestApi/resources/latest/dataLoaderDataSets?q=UcmContentId='<exact-id>'&onlyData=true&limit=500&offset=<n>`. `UcmContentId` is a string field, so the value must be enclosed in single quotes. Never send the value unquoted or interpolate arbitrary input; retain the quotes when URL-encoding the query.
2. Follow pagination and preserve each returned `DataSetId`.
3. For every returned data-set ID, query `GET /hcmRestApi/resources/latest/dataSetErrors?q=DataSetId=<data-set-id>&onlyData=true&limit=500&offset=<n>`.
4. Follow error pagination even when the data-set status or counters indicate success or zero errors.

For every resolved non-FSM data set, query both child diagnostic resources after `dataSetErrors`, following pagination independently:

1. `GET /hcmRestApi/resources/latest/dataLoaderDataSets/<DataSetId>/child/failedLines?fields=UIName,FileLine,Message,MessageText,MessageUserDetails&finder=findByBusinessObject&q=MessageText!='-1'&onlyData=true&limit=500&offset=<n>`.
2. `GET /hcmRestApi/resources/latest/dataLoaderDataSets/<DataSetId>/child/dataSetAllObjects?fields=BusObjFileDiscriminator,UIUserKey,Message,MessageText,MessageUserDetails&finder=findErrorMessageDetails&q=OriginatingProcess in ('LOAD','VALIDATION','ORA_ROLLBACK') and MessageText != '-1'&onlyData=true&limit=500&offset=<n>`.

Do not retrieve or write rows whose `MessageText` equals `-1`. For every non-FSM data set, write one atomic `0600` `<safe-data-set-name>-errors-<sequence>.log` with a count summary and separate numbered Failed Line Errors and Data Set Object Errors sections. Label the returned values with business-friendly names, using `MessageText` for the logged problem only when it has no unresolved `{...}` placeholder; otherwise use a nonblank resolved `Message`, retaining the original `MessageText` only when no usable `Message` exists. Omit blank Additional Details, and preserve complete `FileLine` values in a final delimiter-preserving Technical Details section correlated to the failed-line error number. Use friendly empty-section text instead of an empty table. If one child fails, retain the resolved status, continue with the other child, write a partial log with an `Unavailable` section, and expose a Markdown warning. File-write failures also retain status and produce a warning. Save logs under the per-request Codex diagnostics directory by default; `--diagnostic-log-output-dir` and `--fsm-process-log-output-dir` may select any writable destination. Link every saved log in the Markdown report and keep its row-level details out of the report.

For a resolved data set whose `SourceType` is exactly `ORA_CX_IMPORT`, retain the `dataSetErrors` lookup but do not query `failedLines` or `dataSetAllObjects`. Instead retrieve the paginated `GET /hcmRestApi/resources/latest/dataLoaderDataSets/<DataSetId>/child/cxImportBusinessObjects?expand=all` collection. For each business object with errors, collect embedded `cxImportErrors`; if that child reports more pages, follow its same-host `self` link and paginate it. Write one atomic `0600` CX error log only when one or more errors are collected or a CX diagnostic retrieval fails. Include the business object and file context with each record's file-record number, error code, error type, and error message. Preserve resolved status on partial retrieval or write failure, include a readable `Unavailable` section in a qualifying log, link it in the Markdown report, and keep raw identifiers and REST responses out of chat output.

For every resolved data set whose `SourceType` is exactly `FSM`, keep that `dataSetErrors` lookup and also download `GET /fscmRestApi/resources/latest/setupTaskCSVImports/<FsmTaskCode>/child/SetupTaskCSVImportProcess/<FsmMigRequestId>/child/SetupTaskCSVImportProcessResult/<FsmMigRequestId>/enclosure/ProcessLog`. Require a safe nonempty task code and positive migration request ID before constructing the URL. Preserve the response bytes unchanged in one `.log` file per FSM data set. Parse failed business-object blocks, detail-object context, row counts, and failure totals into structured FSM Import diagnostics after any MsgText rows; summarize raw Java exception classes in friendly language and retain their exact text only in the download. If the ProcessLog request or file write fails, retain the resolved data-set status and report the download failure.

For every resolved data set whose `SourceType` is exactly `FBDI`, keep `dataSetErrors`, `failedLines`, and `dataSetAllObjects` as supplementary diagnostics and treat ESS logs as the authoritative job-level source. POST `{}` to `/hcmRestApi/resources/latest/dataLoaderDataSets/<DataSetId>/action/reviewProcessHierarchy` with `REST-Framework-Version: 9`, `Accept: application/json`, and `Content-Type: application/vnd.oracle.adf.action+json`. Parse the JSON array encoded in `result`, deduplicate positive `processId` values in source order, and GET every process at `dataLoaderDataSets/<DataSetId>/child/processes/<processId>`. When `AttachmentDocumentId` is present, download `child/processLogs/<AttachmentDocumentId>/enclosure/FileContents`. Save each available log atomically as owner-only readable text. Render `ORA_FBDI_IMPORT` as `FBDI Import` and `ORA_FBDI_LOAD` as `FBDI Load`, including in saved filenames. Summarize only actionable messages from explicit product error sections or explicit error records, group repeated messages with an occurrence count, and exclude informational notes, status polling, checkpoints, request/scope identifiers, interface-limit tables, and stack traces. Retain the complete log content in the linked file. Keep data-set, process, and attachment identifiers internal. A malformed hierarchy entry, failed process request, failed download, or file-write error is fail-soft: continue other diagnostics, retain the data-set status, and show a readable warning. A missing attachment means that process has no downloadable log and is not itself an error.

For CSV and XLSX validation, map a non-exact source header only when it uniquely resolves to a live section attribute by normalized technical name, live `AttributeLabel`, or the reviewed column-alias glossary. Exact headers take precedence; other duplicate targets fail closed. Ignore unmappable columns in the in-memory DAT only and list both mappings and ignored columns in the validation output. DAT and explicit ZIP metadata remain exact-only.

Do not call `GET dataLoaderDataSets/{RequestId}`. The resource primary key is `DataSetId`; the initiation response returns `DataSetRequestId`. Use either the validated `DataSetRequestId` or quoted `UcmContentId` query to resolve the load to its server-issued `DataSetId`.

Run `python3 scripts/get_data_load_info.py <request-id-or-ucm-content-id>` for this two-endpoint lookup, adding `--status-only` when the user asks only for status. Whenever a matching data set exists, a status-only response always reports its data-set status with total, loaded, and failed counts, including when the load succeeds. Label the first column `Data Set` and populate it with the exact `DataSetName`, falling back to `UIName`, `BusinessObject`, or `Unknown data set` only when Fusion omits it. For `dataSetErrors`, render only each nonblank `MsgText` exactly as returned; do not use `GroupByExprVal`, nested details, or fallback text, and omit Diagnostics when no rows remain. Apply error reporting regardless of the overall status or reported error counters. If no matching data set exists yet, return only a compact two-column `Not available yet` status table. Keep data-set status, transfer/import/load stages, line counts, timestamps, and server identifiers internal unless the user explicitly asks for them.

Treat the helper's internal dictionary as implementation evidence. The CLI itself emits the complete Markdown report defined by [user-friendly-output.md](user-friendly-output.md). Do not paste raw API responses into chat unless explicitly requested.

Status lookup is read-only except for applicable FSM ProcessLog downloads, FBDI ESS log downloads, and qualifying non-FSM Data Loader error logs, which are written only to the selected output directory; it creates no run records, summaries, or other diagnostic reports.

If `dataLoaderDataSets` returns no item, report that the request has not resolved to a data set. A `dataSetErrors` query requires the server-issued `DataSetId`; do not substitute the request ID.

## Failure rules

- Preserve the failed stage, HTTP status, response body, and any server-issued identifiers without printing credentials or base64 file content.
- Do not make an upload or initiation request after source-selection, file-validation, business-object-validation, or archive-preparation failure.
- Do not call `initiateDataLoad` after an upload failure or incomplete upload response.
- On initiation failure, report the already-created UCM content ID with the error.
