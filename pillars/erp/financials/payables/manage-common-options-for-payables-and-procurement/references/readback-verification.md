# Post-import verification

The offline adapter compares values and row preservation. A matching file alone
does not establish that Fusion saved the changes. `comparisonStatus: PASS` with
`status: PENDING` means content matches but persistence is unproven.

## Collect the observation

At the routed post-import verification step, retain the exact submitted candidate,
its original baseline, the unmodified Core preflight envelope and the structured
result returned by Core's upload/initiation call. The latter must contain
`RequestId`, `ContentId`, `archiveSha256`, `sourceType`, `uploadStatus` and
`initiationStatus`. Do not reconstruct missing execution evidence from a candidate
or a summary. Missing evidence leaves verification pending.

From this task folder, preview the operation using real project artifact paths:

```sh
python3 scripts/readback_evidence.py \
  --task-code AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT \
  --baseline baseline.zip --candidate submitted.zip \
  --preflight core-preflight.json --initiation core-initiation.json \
  --properties /absolute/path/to/fusionEnv.properties \
  --output-dir /absolute/path/to/project/exports/readback-run
```

Preview and execution reject existing or linked output files and aliases of any
input. Resume permits only the validated regular checkpoint as an existing output.
The preview makes no Fusion calls. Present its environment, task, candidate hash
and export payload, then obtain the existing workflow's approval to start this
data export. Run the same command with `--execute` only after that approval.
Import approval alone does not authorize a new export operation.

The helper delegates status retrieval to Core Data Loader. It requires the exact
request, content ID and task to have succeeded without object errors. It then
starts a new task data export through Shared, checks completion and downloads
`FileContent`. It records UTC times around these operations and hashes the actual
downloaded bytes. Authentication and HTTP remain owned by Core; no import is
submitted by this helper.

The output directory contains `readback-run.json` and, after a successful
download, `readback.zip` and `readback-observation.json`. Each invocation uses a
polling window of at most 60 seconds. On timeout or failure, the run records the
failure class, stage, process identity, last known status and elapsed wait. Terminal export
failures also retain a ProcessLog digest, byte count and sanitized diagnostic
codes when available; free-text log contents are not saved. A pending run does
not prove persistence.

### Resume an existing export

When the user requests another status/download check, run the same command with
the same input files and output directory plus `--resume`. This local preview
checks the saved task, target, import request, input hashes and export process ID.
Continue with `--execute --resume` only at the active workflow's selected
read-only status/download step. It polls and downloads the recorded export; it
does not create another export or repeat the import. Resuming this read-only
step does not require approval for a new export.

If the export remains pending, keep the checkpoint and report its status and
next-check command. Do not poll again automatically after the bounded wait.
Do not edit the checkpoint, substitute files, or overwrite complete or partially
written output artifacts. Resume rejects terminally failed exports, exports
started more than 24 hours ago, and runs without a recorded export process ID.
Preserve these runs for investigation. Starting a new export requires a new
output directory, preview and approval.

## Verify the requested values

Run the existing `reconcile` command with its baseline, candidate, blueprint and
requirements. Set `--export` to the downloaded `readback.zip` and add:

```sh
--readback-evidence /absolute/path/to/readback-observation.json \
--import-request-id CURRENT_REQUEST_ID --target-url https://TARGET_HOST
```

The observation must match the task, target name and URL, current import request,
baseline, submitted candidate and downloaded archive. It must identify a
successful import and completed data export, with export observation after the
import check, no future timestamps and an observation no older than 24 hours.
Candidate/baseline archives cannot serve as read-back proof.

`PASS` and `persistenceVerified: true` require both valid observation binding and
matching business values. Missing evidence is `PENDING`; invalid evidence is
`BLOCKED`; content differences are `FAIL`. These outcomes return a nonzero exit
code except `PASS`. Preparation and its approval gates are unchanged.

The observation is recorded local workflow evidence, not a signed server
attestation. Do not hand-write, rebind or reuse it for another request. Persist the
result and artifact references under the project run using the manifest's
artifact, run and token-usage policies.
