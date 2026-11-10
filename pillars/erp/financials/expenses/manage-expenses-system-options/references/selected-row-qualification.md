# Selected-row audit-preservation qualification

This is a task-owned maintainer branch for an explicit developer investigation
on a user-selected nonproduction environment. It is not ordinary customer
qualification or an alternative to core Data Loader. A current project and
active Run Book, current environment binding and the normal task preconditions
are required. Retain the user's explicit readiness run/skip decision for the
same scope; do not waive Data Loader validation.

The initial controlled create/update qualified the selected-row serialization
for the bounded cases in [preservation evidence](selected-row-preservation.md).
The ordinary builder now uses that serialization. This separate command and
workflow remain for explicit nonproduction qualification of further changes;
their results do not automatically broaden live coverage or approve an import.

## Candidate contract

The existing `validate` command must first return ready_for_import with no input
or mapping blockers, binding the unchanged workbook, fresh completed export,
metadata/process/archive and current BU evidence. `build-qualification` reruns
all builder identity, digest, mapping, paired-alias and duplicate checks.

It emits only complete selected rows from each updated CSV, keyed by canonical
BuName plus SettingCode or OptionCode. Omitted rows are a test of preservation,
not a deletion request. Existing selected rows retain every non-input cell;
new rows use the normal sparse-create field contract. Both option aliases
remain present and identical on selected rows. Unselected entities retain
ordered headers with no rows. All four members remain and the exact fresh
descriptor bytes are unchanged. Never copy a different BU's internal keys or
audit fields, choose a winning alias, rewrite NodeSequence or manufacture XML.

```text
node scripts/expense_system_options_intake.mjs build-qualification \
  --validation /absolute/project/artifacts/intake-validation.json \
  --baseline-dir /absolute/project/exports/extracted-current-export \
  --baseline-process-id PROCESS_ID \
  --baseline-archive /absolute/project/exports/unchanged-export.zip \
  --environment TARGET_ENV --nonproduction-environment TARGET_ENV \
  --reference-evidence /absolute/project/artifacts/current-bu-evidence.json \
  --output /absolute/project/artifacts/qualification-candidate.zip \
  --manifest-output /absolute/project/artifacts/qualification-manifest.json
```

The manifest records selected_rows_qualification, qualification_only=true,
live_qualified=false, submitted/omitted row counts and a preservation warning.
The nonproduction argument must match the selected environment; it records the
explicit choice, not independent environment certification. Require the actual
user-selected nonproduction identity before using this branch. No credential,
lookup or live operation is performed by the builder.

## Native execution and approval

1. Review the exact requested values and per-key create/update operations
   against the fresh baseline. Use run-owned retained fixtures only with their
   documented lifecycle. New keys require absence proof and separate retention
   or supported cleanup consent. No broad create or restore is implied.
2. Independently inspect the final ZIP: members, descriptor bytes, ordered
   headers, complete selected rows, aliases, omitted unrelated rows and digest.
   Persist the selected-key intent and expected before/after values privately
   in the project. Reject unexpected keys, changes or removed members.
3. Run the ordinary task planner and shared setup/reference validation, then
   `core.data-loader` preflight on those exact bytes. Use the current three
   task-local nodes to evaluate validated intake, baseline and native handoff.
   For this branch they establish qualification-candidate conformance only;
   retain a warning that omitted-row and unrelated-audit preservation is not
   yet live-qualified. Do not fabricate a passing preservation result or use
   an override to bypass a failed prerequisite.
4. Present the target, fixture lifecycle, exact key/value changes, qualification
   scope, warning and immutable artifact for core's normal explicit approval.
   Submit once through the approved Data Loader envelope. Do not directly call
   an FSM import API, replace its adapter, or modify the approved artifact.
5. Monitor the accepted request and retrieve ProcessLog through the declared
   workflow. A failed/ambiguous job requires reconciliation before any retry.
   Obtain a separately approved fresh verification export.

## Reconciliation and promotion

Compare selected values and multiplicity, complete unrelated-row multisets,
business values, creation history and last-update audits separately. Preserve
ordered headers, all task identities, both aliases and metadata/ownership
checks. An import success with unrelated audit changes is a failed strict test.
Keep process and artifact IDs, baseline/verification hashes, actual failures and
retained fixture disposition in the project.

Qualify create and update separately; an update does not prove create. A
successful limited test qualifies only its recorded operation, row families,
scope, target/release and serialization. Record a reviewed promotion decision
before making selected rows an ordinary builder behavior. Do not convert a
local test or simulation into live evidence. If a contract step, alias result
or preservation check is unresolved, keep ordinary promotion blocked.

No automatic reverse import, cleanup, audit repair or deletion is provided.
Any later restore requires a fresh baseline/intervening-change check, supported
operation, exact-artifact approval and fresh reconciliation.
