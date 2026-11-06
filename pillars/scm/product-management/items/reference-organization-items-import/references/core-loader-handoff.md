# Select the installed Core Data Loader contract

Read this before source preparation or Fusion calls. Read the checked-out
`core/data-loader/SKILL.md`, its referenced import/Task Hook contracts, and run
`python3 -B core/data-loader/scripts/upload_and_initiate.py --help` locally.
Select the workflow explicitly documented **and** exposed by that checkout.
An environment label, branch name, or a previous run is not capability evidence.

| Core contract | Required evidence | Handoff |
|---|---|---|
| In-memory session | Core documents the session protocol; CLI exposes --interactive-session | Session workflow below |
| Retained preflight | Core documents preflight and Task Hook approval; CLI exposes --task-routed, --preflight-envelope-output, --approved-preflight-envelope and --confirm-upload | Preflight workflow below |
| Unknown or inconsistent | Neither complete contract, or documentation disagrees with CLI | Stop with catalog_or_metadata_mismatch before source preparation or Fusion calls; report missing capability |

When CLI help exposes retired compatibility flags as well, the active workflow
documented by the installed Core wins; legacy flags alone do not select a route.
Select once before validation. Never switch workflows after a failed or uncertain
upload/initiation, copy Core modules from another branch, or implement a loader
adapter in this pillar. The preparation helper has no Core imports and does not
select or execute either workflow. Core's own policy is authoritative for its
artifact retention, approval, submission and reporting mechanics.

## Common task gates

Both workflows require the same active project/Run Book/task context, available
Item Index result, current explicit or retrieved template/control contract,
validated Batch ID and requested scope, and exact Reference Organization Items
BO selected through Core's normal native-FBDI routing. Core owns filename/account/adapter validation and executes the BO's configured Import Mode. Do not add a pillar LoadAdapterConfig/link/SQL check. Read all planned task rules.
Omitted mode defaults to ORA_REF_ORG_ASSGN_BOM_COMMON; unsupported live overrides
remain blocked. No structure rows are invented for an assignment request.

Prepare one source ZIP in the controlled transient location, or retain a
validated supplied native ZIP. Validate the bytes Core binds for upload:
captured nativeSources for a session, or Core's final immutable artifact for a
preflight. Never return to the original source after Core fixes the artifact.
Keep validation evidence in the ordered ruleResults, including the Batch ID and
resolved Import Mode as informational issues. Do not add ESS parameters.

## In-memory session workflow

Use Core's existing entry point, from the repository root:

```bash
python3 -B core/data-loader/scripts/upload_and_initiate.py \
  --interactive-session <source.zip> \
  --business-object "Reference Organization Items" \
  --task-context <task-context.json> \
  --task-name "Reference Organization Items Import" --sequence <sequence> \
  --run-config <selected-run.properties>
```

Retain the actual process handle. At awaiting_task_rules, evaluate the captured
nativeSources and the common gates. Send the ordered rules, then preview.
Display Core's approval Markdown verbatim. Only after contextual user approval
send approve with that session's previewId. Use Core's rules/preview/approve/
cancel protocol unchanged. No source reread, repackaging, disk approval envelope
or custom session factory is permitted in this contract. A lost handle, expired
session or changed source/target requires fresh validation and approval.

## Retained preflight workflow

Use this only when the installed Core declares it; a session-only Core explicitly
retires these commands. Read the installed `core/data-loader/task-hook/SKILL.md`
and `core/data-loader/references/task-rule-registry-execution.md` first.

1. Run Core's preapproval validation with the source ZIP, exact BO and
   `--task-routed --run-config <selected-run.properties>
   --preflight-envelope-output <private-transient-dir>/preflight.json`.
   Do not pass upload/confirmation flags. Keep internal paths and output out of
   chat. Core's documented approval-required exit may be nonzero; distinguish
   that expected pause from a failed validation. Require Core's valid retained
   preflight, taskRouted true, mappingComplete true, and its matching final
   artifact before continuing. Do not create, repair or reconstruct a preflight.
2. Invoke Task Hook's `data-load` with the exact task context/name/sequence.
   Read its executionGuide and ordered resources. Evaluate every applicable
   task node against the retained artifact and common gates; no direct Task
   Validator invocation and no invented successful rule results.
3. Through Task Hook's `build-data-load-preview --input-stdin`, provide the
   documented taskContextPath, taskName, sequence, finalData and ordered
   ruleResults. Use the exact archive integrity metadata supplied by Core;
   retain only the artifact metadata needed by the contract, without raw rows.
   Render the installed Core's final approval report unchanged after all task
   gates pass. A blocker is not an approval request.
4. Wait for a later contextual user approval for that exact artifact, target,
   scope and task. Then use Task Hook's `approve-data-load-preview`, followed by
   `verify-approved-data-load-archive --archive <Core-final-artifact>`.
   Pass its returned taskValidationEnvelope unchanged through the declared
   `--task-validation-envelope` file. Never fabricate approval JSON or waive a
   task gate to make the workflow proceed.
5. Submit through the installed Core's retained-artifact entry point:

   ```bash
   python3 -B core/data-loader/scripts/upload_and_initiate.py \
     --approved-preflight-envelope <Core-preflight.json> \
     --task-validation-envelope <Core-task-envelope.json> \
     --confirm-upload --run-config <selected-run.properties>
   ```

   Preserve any explicitly selected OAuth properties. Do not supply a source,
   mapping, routing, task-routed or review override on retained submission.
   Core verifies its retained bytes, target and Run Book context. A missing,
   changed or mismatched artifact/envelope requires fresh validation and approval.

Only this Core contract may retain its required artifacts/envelopes. Use an
explicit owner-only transient directory outside the repository/project for
loader control files, with private files; do not persist raw intake JSON or
standalone CSVs. Follow Core's prescribed lifecycle and Task Hook project
evidence requirements. Core-required integrity metadata and sanitized Task Hook
validation evidence may be retained in the prescribed project record; the pillar
does not create independent preview/approval snapshots. Exclude customer rows,
credentials and payload copies from project records. If a mandatory Core persistence requirement cannot
meet repository data-handling policy, stop and record the conflict instead of
changing its output or inventing another route. Do not apply session-only
memory rules to a preflight Core or preflight rules to a session-only Core.

## Completion

For either contract, return Core's accepted-initiation report verbatim and stop.
No automatic status polling, upload/initiation replay, purge or alternate ESS
submission. A later requested status uses Core's status workflow and permitted
logs. Acceptance and ESS success do not independently verify assignments;
business completion requires approved result evidence.
