# Oracle Fusion Run Book Command Contract

Use `scripts/runbook_rest.py` for every Oracle Fusion REST operation performed by the Run Book skill. Do not construct or invoke Run Book endpoints directly. The client reads `restBaseUrl` and OAuth configuration from `core/auth/fusionEnv.properties`, delegates authentication and default token-cache selection to `core.auth.fusion-oauth-authentication`, and preserves active journey ID resolution, requested field lists, pagination, and timeout.
Send `REST-Framework-Version: 9` on every Oracle Fusion REST request.
After a cached-token 401 or 403, invoke the shared core-auth refresh and retry once only for read-only operations. Never automatically refresh or retry a request that can create or modify data. Never refresh an explicitly supplied access token.

## Read commands

- `list-runbooks`: POST the self-journey search with subject type `RBK`. Send an empty `StatusCategoryMeaning` terms array by default. Send exact canonical terms only for explicit `Open`, `Completed`, or `Overdue` filters. Retain selection IDs in the structured result and format the resulting list page as Markdown.
- `get-journey`: retrieve journey metadata, including the exact `JourneyTitle`.
- `list-tasks`: retrieve bounded `allStepTasks` pages in sequence.
- `get-task`: retrieve the selected task's raw detail fields.
- `get-documents`: retrieve an `ORA_CHK_DOC` task's raw documents within the collection limits.
- `summary`: retrieve all tasks and return deterministic `counts` and `summary` values.
- `dashboard`: retrieve tasks first and optional journey metadata second, build a field-allowlisted model, and return the dashboard as Markdown. Journey failure is nonfatal; task failure is fatal.
- `task-detail`: retrieve task details and accessible attachments for every task type, retrieve documents only when `Type` is `ORA_CHK_DOC`, retrieve Data Load Status only when `Type` is `ORA_CHK_DATA_LOADER`, and return the compact detail view as Markdown.

`dashboard --include-task-index <zero-based-index>` may be repeated to show a selected subset; indexes refer to the original `list-tasks` input. Counts and the summary use only the selected tasks. The title always remains the exact retrieved `JourneyTitle`.

For `dashboard` and `task-detail`, return the complete user-friendly report in the JSON result's `markdown` field.

For `list-runbooks`, use `/hcmRestApi/redwood/11.13.18.05/workerJourneySearches` and send the prescribed finder, status filters, display-field allowlist, and offset. For `--query-stdin`, also send the exact non-empty stdin value as `query` and send `searchFields: ["JourneyDisplayName"]`; omit both fields when no name search was requested. A name search may be combined with status filters. The response page may be larger than the configured chat page. Return `nextOffset` whenever undisplayed items or another page remain. Retain `WorkerJourneyId` in the machine-readable selection index. A `load more` follow-up must use the prior `nextOffset`, original query when active, and resolved status terms.

When `dashboard` or `summary` has neither an explicit journey selection nor a configured active Run Book, fail before authentication. User-facing output must be exactly `No Run Book is available to show. Create or select a Run Book, then try again.` Keep Data Loader configuration and CLI flags out of the response.

## Collection fetch limits

Tasks, comments, documents and attachments share bounded pagination. Each collection retrieval defaults to:

```yaml
total_record_fetch_limit: 2500
pagination_record_limit: 500
pagination_limit: 50
```

Remote commands accept `--total-record-fetch-limit`, `--pagination-record-limit`, and `--pagination-limit` as positive integers. These are also keyword settings on `RunbookClient` and `build_authenticated_client`. The total limit bounds cumulative records across the initial read and its explicit follow-ups from offset zero; the page record limit bounds requested records per page; the pagination limit bounds page fetches per collection. Authentication refresh/retry for the same page does not consume another pagination slot. `pagination_record_limit` is the sole per-page record ceiling for tasks, comments, documents and attachments. Their commands and client methods do not accept `--page-size` / `page_size`; `list-runbooks` retains its separate display-only `--page-size`. No replacement create or write retries are introduced.

For example, `dashboard --total-record-fetch-limit 500 --pagination-record-limit 200 --pagination-limit 3` requests up to 200, 200, then 100 tasks, stopping earlier if Fusion reports no more records. A server returning fewer than requested does not increase the page allowance. A server returning more than requested causes `ApiError` before its items are appended.

When a limit stops retrieval while Fusion reports more, return `hasMore: true`, `complete: false`, `nextOffset`, and `stopReasons`. Do not automatically continue with another invocation to bypass the limit. The returned `count` counts fetched records, not all available records. Dashboard and summary counts cover fetched tasks only. Preserve the existing summary and task-detail Markdown without automatic pagination notices; retain completeness and continuation information in internal pagination metadata. Run Book search remains a separate, single-search-page operation. These record limits do not bound response bytes.

Explicit collection continuation uses `--offset` on `dashboard`, `summary`, `list-tasks`, and `get-documents`. Task detail has independent `--attachments-offset`, `--comments-offset`, and `--documents-offset`. These offsets must be nonnegative. Responses retain `paginationSettings` and `nextOffset`; dashboard/task-detail CLI output retains the service's `pagination` metadata. On "show more", reuse the selected collection's next offset and all previous runtime limits, using `pagination_record_limit` for the per-page ceiling. Do not reset limits to defaults or fetch all remaining records. Each explicit follow-up gets a fresh page-call allowance, but only the remaining cumulative record allowance (`total_record_fetch_limit - offset`). Thus total 5, per-page record limit 2, and one page per invocation yield 2, 2, then 1 record. At the total cap, `nextOffset` is null and `continuationAllowed` is false even if `hasMore` is true. Internal results include `fetchedSoFar` and `remainingRecordAllowance`; reaching the cap does not add a display notice. A direct offset at or beyond the total cap raises `ApiError` before any collection request. Do not infer that no more records exist from cap exhaustion. Do not reset or increase limits for "show more"; a changed total or restart requires an explicit user request. A complete result sets `nextOffset` to null. Keep availability and continuation metadata internal; do not add availability, partial-count or page-only notices to the existing display format.

## Create contract

`create-runbook --project-root <absolute-project-workspace>` reads the canonical persisted plan from `artifacts/shared/runbook/current/runbook-plan.json` inside that workspace. It does not accept `--input-stdin`. The persisted plan has this shape:

```json
{
  "tasks": []
}
```

- POST exactly once, without retry, to `/hcmRestApi/resources/11.13.18.05/journeySubjects/RBK/child/assignedJourneys/action/assignRunbook`.
- For project-backed creation, use each plan task's `task_description` as its Notes entry. Missing or null descriptions become empty strings; reject a non-text description before the POST.
- Require a non-empty `tasks` array. The Notes array must contain exactly one entry per source task.
- Ignore `sequence_status` completely, including during Notes generation. Sort valid tasks by ascending positive integer `sequence`, preserving source order for equal sequences.
- Accept each `taskNotes` entry as supplied when it is text, including an empty string. Do not inspect or transform its content.
- Skip task objects with an invalid name, sequence, or non-text `taskNotes` entry. Return their source indexes and reasons in `skippedTasks`; reject the request without POSTing when no valid tasks remain.
- Build `journeyDetails.name` from `project_id`, passing non-string values unchanged and trimming string values. When it is absent or a blank string, use the plan-level `<offering> - <functional_area>` only when both are non-empty text; otherwise, use `Implementation Run Book`. Task-level `offering` and `functional_area` are optional and control task grouping only. Always send `journeyDetails.completionCriteria` as `ORA_CHK_ALLTASKS_COMPLETE`, `archiveOffset` as `12`, and `purgeOffset` as `12`. Do not send `journeyDetails.initiator`.
- Require a non-empty string `task_id` on every accepted source task, pass it unchanged as `taskActionCode`, and use `taskType: ORA_CHK_DATA_LOADER` for every accepted task. Validate, trim, and de-duplicate each task's `business_objects` array, then pass it to the Oracle task detail as comma-separated `embeddedApplicationTaskCode`. Never send `business_objects` or `businessObjectId` during creation, and preserve Notes unchanged.
- Send `AllowMultipleCommentsFlag: "Y"` for every generated task detail.
- Treat `depends_on` as an array of source-task `task_id` values. Resolve each value to every matching valid task name in source order, preserve the supplied dependency order, join the names with `|`, and send that string as `dependentOn`. Send `null` when `depends_on` is missing, empty, or malformed. Skip a task whose non-empty dependency array contains an unknown task ID and report the reason in `skippedTasks`.
- Require the journey ID from the response `result`, atomically stamp it into Data Loader's case-sensitive `runID`, and use it to retrieve and format the existing dashboard. Return it in machine-readable output for follow-up context.
- Exit 3 with `created: true` when HTTP success is known but the ID, Data Loader config write, or dashboard retrieval failed.
- After the dashboard model is available, return the complete report in `markdown` with the successful creation outcome and any skipped-task warnings. Do not repeat the POST.
- Exit 3 with `created: "unknown"` when the POST was dispatched but its outcome cannot be determined. Never repeat the POST after either exit-3 result.

## Merge contract

`merge-runbook [--journey-id <WorkerJourneyId>] --input-stdin` accepts the original standard-input envelope containing `plan` and `taskNotes`. It does not accept a raw plan. Resolve an omitted journey ID from the active Run Book; use an explicitly selected Run Book ID when the user searched for a target.

- Build the payload through the same validation and task ordering as `create-runbook`, then send exactly `{ "taskDetails": <generated-task-details> }`. Never send `journeyDetails`.
- POST exactly once, without retry, to `/hcmRestApi/resources/11.13.18.05/journeySubjects/RBK/child/assignedJourneys/<WorkerJourneyId>/action/mergeJourney` with `Content-Type: application/vnd.oracle.action+json` and `REST-Framework-Version: 9`.
- Do not locally detect, reject, remove, or modify duplicate task names; Fusion owns merge conflict handling.
- Treat an empty, non-JSON, or unreadable confirmed 2xx response as a successful merge. After the POST, retrieve the target dashboard and atomically stamp the target as active only after dashboard retrieval succeeds.
- Return `merged: true` with the standard dashboard Markdown after success. If the POST is known to have succeeded but dashboard retrieval or active-ID persistence fails, return exit code 3 with `merged: true`; when dispatch is indeterminate, return exit code 3 with `merged: "unknown"`. Never repeat the POST.
- The standard dashboard reads Fusion's `StageName` and renders each returned stage as a separate heading and a three-column task table: Sequence, Task, Status. This also applies to dashboards returned after creation, import, or merge; individual task details retain five columns. When Fusion returns no stage name, retain the ungrouped `Tasks` section; do not invent a stage.

## Add-task contract

`add-task --journey-id <WorkerJourneyId> --input-stdin` creates exactly one manual Run Book task. It accepts this input object:

| Field | Required | Validation and default |
| --- | --- | --- |
| `name` | Yes | Non-empty text. |
| `sequence` | No | Positive integer. When omitted, use `"10"` for an empty Run Book or the highest existing Sequence plus 10. |
| `required` | No | Boolean; defaults to `false`. |
| `notes` | No | Text; preserve exactly and omit `Notes` when absent. |
| `allow_comments` | No | Boolean; defaults to `true`. |
| `allow_attachments` | No | Boolean; defaults to `true`. |
| `performer_type` | No | Non-empty text; defaults to `ORA_INITIATOR`. |

Reject unknown or invalid fields before POSTing. The task type is always `ORA_CHK_MANUAL`.

- POST exactly once to `/hcmRestApi/resources/11.13.18.05:9/journeySubjects/RBK/child/assignedJourneys/` with the shared OAuth authorization, `Content-Type: application/json`, and `Upsert-Mode: true`.
- Send only:

  ```json
  {
    "WorkerJourneyId": "<journey-id>",
    "tasks": [
      {
        "Name": "<derived-name>",
        "Type": "ORA_CHK_MANUAL",
        "PerformerType": "<performer_type>",
        "RequiredFlag": false,
        "Sequence": "<supplied-or-derived-sequence>",
        "AllowCommentFlag": true,
        "AllowAttachmentFlag": true
      }
    ]
  }
  ```

  Include exact `Notes` in the task only when supplied.
- After HTTP success, require the response to contain exactly one `tasks.items` object with a positive `WorkerJourneyTaskId`. Use that ID and the input `WorkerJourneyId` to retrieve and format the task-detail view. Do not refresh the task list or match by name and sequence.
- Return `added: true` and the complete report in `markdown` after task retrieval. Exit 3 with `added: true` after known creation followed by an unusable response or task-detail retrieval failure. Exit 3 with `added: "unknown"` when dispatch is indeterminate. Never repeat the POST after either exit-3 result.

## Task attachment contract

`attach-task-files --parent-worker-journey-id <ParentWorkerJourneyId> --worker-journey-task-id <WorkerJourneyTaskId> --input-stdin` accepts one object with a non-empty `files` array. Each file accepts only `path`, `approved_sha256`, `title`, `description`, and `content_type`.

- Require an absolute path to an existing, non-empty regular file and a matching lowercase SHA-256 digest. Validate every file before authentication and recheck its digest immediately before upload.
- Use the selected path's filename, which must contain 1 through 2048 characters. Default `title` to that filename and infer `content_type`, falling back to `application/octet-stream`; preserve supplied metadata exactly. When present, `description` must be text no longer than 255 characters.
- Retrieve the selected task before writing. Use its name when available; otherwise, use `Run Book task` in user-facing output.
- For each file, POST exactly once through the Run Book client's task-attachment operation with `Content-Type: application/json`, `REST-Framework-Version: 9`, and no `Upsert-Mode` header. Send only `DatatypeCode: FILE`, `FileName`, `Title`, `UploadedFileContentType`, Base64 `FileContents`, and optional `Description`.
- Require a positive `AttachedDocumentId` in each successful response, but never expose it. Upload multiple files sequentially and stop after the first failure or unverifiable outcome. Never retry a POST, including after authentication, transport, or response-validation failure.
- Return only task name, filenames, approved digests, per-file statuses, overall status, an optional sanitized error, and Markdown. Never return local paths or Base64 content. Use `attached`, `failed`, `unknown`, `attached-unverified`, and `not-attempted` file statuses. Set overall `attached` to `true` when every upload is confirmed, `false` when the first attempted upload fails before any attachment is confirmed, `partial` when an earlier upload was confirmed but the batch did not finish, and `unknown` when the current POST may have succeeded. A first known upload failure exits 2 with the attempted file marked `failed` and every remaining file marked `not-attempted`. Exit 3 when an earlier upload succeeded or the current POST succeeded or may have succeeded but the batch cannot finish safely.

## Force-complete contract

- `force-complete-runbook --journey-id <WorkerJourneyId>` POSTs exactly once to `/hcmRestApi/resources/11.13.18.05:9/journeySubjects/RBK/child/assignedJourneys/<WorkerJourneyId>/action/forceComplete`.
- Validate the selected ID before authentication and dispatch. Do not expose it in Markdown.
- Require explicit authorization for this write and never retry it automatically, including after authentication, transport, or response-validation failures.
- Return `completed: true` and the success Markdown only after a confirmed usable success response.

## Status contract

| Oracle Fusion status | Display | Summary bucket | Complete |
| --- | --- | --- | --- |
| `INI` | Not Started | open | no |
| `INP` | In Progress | in progress | no |
| `RFR` | Ready for Review | not summarized | no |
| `DEP` | Dependent | not summarized | no |
| `COM` | Completed | completed | yes |
| `CWE` | Completed with Exceptions | completed | yes |
| `TOH` | Error | not summarized | no |
| `REJ` | Not Applicable | completed | yes |

Unknown or missing statuses are reported separately.

## Task-detail contract

- Require `--journey-id <WorkerJourneyId>` in addition to the selected task's parent and task IDs. Use the exact ID returned by `create-runbook` or supplied to `dashboard`; `ParentWorkerJourneyId` is not the Data Load Status run ID.
- Render the task's Sequence, Task, Status, % Completed, and Required values in a five-column task-detail table. Dashboard tables use only Sequence, Task, and Status. Show the remaining allowlisted details below that table.
- Preserve `Notes` exactly as returned by Oracle Fusion without encoding or decoding, and derive visible Markdown text with the formatter's basic sanitizer.
- Retrieve Object Notes from `/hcmRestApi/resources/11.13.18.05/objectNotesV2/ORA_CHK_ALLOC_TASK/child/notes` with `expand=NoteText,attachments`, the documented allowlisted fields, `onlyData=true`, `orderBy=LastUpdateDate:desc`, and `q=ObjectId=<WorkerJourneyTaskId> and ContextType='TASK_COMMENTS'`. Retrieve pages in returned order within the configured collection limits. On any comment-read failure, omit Comments and continue task-detail rendering.
- Render each returned comment immediately below Notes as `**{author}** — {UTC timestamp}` followed by supported `NoteText` HTML converted to Markdown. If conversion or timestamp formatting cannot be completed, show the original `NoteText` and `Unknown date` rather than omitting the comment. Use `AuthorName`, then `AuthorKnownAs`, then `CreatedBy`, then `Unknown author`; do not expose note IDs, task IDs, attachment metadata, or other non-allowlisted fields.
- Retrieve accessible task attachment pages within the configured collection limits for every task type. Allowlist only attachment type, file name, title, preview URL, file URL, and web URL. Render Attachments after Comments, using file name, title, then `Attachment` as the label and preview URL, file URL, then web URL as the link. Show a plain-text label when no link is available. If retrieval or validation fails, omit Attachments and continue rendering task detail.
- Only for `Type: ORA_CHK_DATA_LOADER`, request `ApplicationTaskName` in the task detail and POST once to `/hcmRestApi/resources/11.13.18.05:9/dataLoaderDataSets/action/generateRunbookSummary` with `Content-Type: application/vnd.oracle.action+json` and `{"runId": <WorkerJourneyId>, "fsmTaskCode": <ApplicationTaskName>}`. This is a read-semantic action: retry only once after refreshing a cached token rejected with 401 or 403. Treat any request, transport, HTTP, body-read, or response-validation failure as an empty status result and continue formatting the task without a Data Load Status section.
- The action response must be an object whose optional `result` is JSON text. Treat a missing, null, blank, `"null"`, or `"[]"` result as no rows. A nonempty malformed result is an error. Decode the string once into an ordered array of objects, preserve duplicates and zero counts, and ignore unknown row fields.
- Allowlist `DataSetName`, `BusinessObjectName`, `DataSetStatus`, `LoadedCount`, `ErrorCount`, and `SkippedCount`. Show Data Load Status after Comments only for Data Loader tasks with one or more result rows; keep the section hidden when no rows are returned. Render Data Set Name, Business Object, Status, Loaded, Errors, and Skipped, in that order.
- Do not preview or load video `ActionURL` values.
- Format attachment, external, and document URLs as returned, without a scheme restriction.
- For documents, use `FileName` as the link text for `DocumentPreviewURL`.
- Never include `WorkerJourneyId`, `ApplicationTaskName`, `EmbeddedApplicationTaskTypeId`, `UcmContentId`, `TotalCount`, parent/task IDs, owner/contact details, action/access codes, attachment IDs or raw metadata, or unset dates in the Markdown model.
- Markdown includes task status, percentage when present, required indicator, dependency, visible Notes text, Object Notes comment history when available, accessible attachments, non-empty Data Load Status, external action, and documents. It excludes video URLs and every suppressed field.

## Run ID contract

- `create-runbook` stamps the newly returned `WorkerJourneyId`; `dashboard --journey-id <WorkerJourneyId>` stamps the directly opened ID after successful retrieval. Read commands prefer an explicit journey ID, otherwise use the non-empty case-sensitive `runID`; if neither is available, they fail before authentication. Reject an invalid or duplicated configured `runID` before authentication. Both write operations preserve every other property and file mode, add `runID` when absent, and reject duplicate entries. A failed atomic replacement leaves the original file unchanged.
- Never display the Data Loader config contents. Tests must use temporary config files and must not change the real Data Loader config.

## Update contract

`update-task --input-stdin` accepts one object with optional `taskName`, `description`, `status`, `sequence`, `taskPercentage`, `notes`, `comments`, and `reopen` fields. Map taskName, description, status, and sequence to `Name`, `Description`, `Status`, and `Sequence`.

- `notes` is an object with optional text `replace` and `append` fields. `comments` is text and creates one new Object Notes record; it does not replace, append to, update, or delete any existing comment. Preserve `NoteText` exactly, including HTML.
- `status` maps `open`, `in-progress`, `ready-for-review`, `completed`, and `not-applicable` to `INI`, `INP`, `RFR`, `COM`, and `REJ`. `taskPercentage` is an integer from 0 through 100 and maps to `TaskPercentageComplete`.
- `reopen` initializes `Status` to `INI` and `TaskPercentageComplete` to null; it preserves Object Notes comment history. Explicitly supplied update fields then apply.
- PATCH non-comment fields once, then POST one comment when supplied to `/hcmRestApi/resources/11.13.18.05/objectNotesV2/ORA_CHK_ALLOC_TASK/child/notes` with `{ "ObjectId": "<WorkerJourneyTaskId>", "ObjectType": "ORA_CHK_ALLOC_TASK", "NoteVisibilityCode": "ALL", "ContextType": "TASK_COMMENTS", "NoteText": "<supplied text>" }`. Never retry either write. Retrieve the refreshed task detail after success; report partial success when one write is known or may have succeeded but later work is unavailable.
