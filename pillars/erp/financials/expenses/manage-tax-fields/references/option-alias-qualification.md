# ENABLE_TAX alias qualification

Strategy `enable-tax-identical-minimal-aliases-v1` has the narrowly qualified
boundary below. Do not use the former single-populated alias as the routine
switch route or treat related Auto Submission evidence as Tax qualification.
Normal tax-rule-only imports keep both option aliases header-only. Operations
outside the maintained profile require an explicitly selected nonproduction Tax
test through the existing router, active Run Book and core Data Loader workflow.
No alternate authentication, export, import or browser route is introduced.

## Live-qualified boundary — 2026-10-29

A controlled switch-only named-BU insertion of `ENABLE_TAX=Y` passed on observed process
release `11.13.27.04.0`. The terminal ProcessLog recorded one SetupOption row
processed with zero failures. A fresh same-target task export confirmed the new
value in both aliases and exact preservation of 306 unrequested option facts and
44 existing tax rules. The human explicitly requested retaining the inserted
row, so teardown was skipped with that decision recorded in the project.

The same corrected create-Y strategy also passed a controlled cross-environment
test on process release `11.13.26.10.0`: one SetupOption row processed, zero
failures, the new Y value present in both fresh-export aliases, all 64 protected
option facts unchanged, and all 3 existing tax rules unchanged. Retention was
explicitly requested. Its CSV headers and XML mappings match the first test;
its exact release/schema fingerprint is listed separately in the profile.

The retained earlier failed package had the same setup-option row and the same
`11.13.26.10.0` process release, but its companion alias was header-only. The new
package duplicates that row into the companion and omits the already-imported
tax-rule delta. These observations support a packaging correction across both
tested deployments. No same-session single-alias A/B rerun was performed, so
they do not prove the precise alias-selection mechanism inside the importer.

[qualified-option-alias-profile.json](qualified-option-alias-profile.json)
binds the normal create route to this create-Y scope and the explicitly tested ordered CSV
headers, XML mappings/types, migration flags, task identity and process releases.
A single combined import outside the update profile below requires separate
controlled qualification. New switches plus new rules can instead use the staged
create route below without expanding that import boundary.
`scripts/tax_option_aliases.py` computes that fingerprint from the fresh baseline
and fails closed on a mismatch. It does not infer an equivalent quarterly
release, additional update combinations, N creates or global scope.

## Live-qualified update boundary — 2026-11-02

A retained, explicitly approved nonproduction import on process release
`11.13.26.10.0` changed one existing named-BU `ENABLE_TAX` row from N to Y
and created one US tax rule for the same BU. The rule had merchant reference
REQUIRED, the other five behaviors ENABLED, and `EnabledFlag=N`. Both minimal
option aliases carried the same update with baseline-owned OtherOrgId.
The terminal ProcessLog recorded one SetupOption row and one VatField row
processed, both with zero failures or warnings. A fresh same-target export
confirmed Y in both aliases and the new rule. Full comparison also confirmed
all 64 unrequested option facts and all 3 existing rules were preserved.
The requested final values were retained as the approved implementation result.

The profile's `qualified_update` section binds this exact combination to its
tested schema fingerprint. The top-level create-Y fields still describe the
separate switch-only create profile; they do not restrict or broaden that
update section. This evidence does not qualify Y-to-N updates, switch-only
updates, another rule value/territory/lifecycle, multiple-BU updates, or an
update on `11.13.27.04.0`.

For a workbook matching either maintained profile, use the normal helper route
without `--qualify-option-aliases`. Do not ask the user to select controlled
qualification for an already qualified combination. A requested Update must
still match exactly one current baseline row. If its value is already Y,
report the switch as already satisfied and omit it from the import rather than
changing lifecycle or manufacturing a test. Prepare any remaining tax-rule
delta through the existing rule-only route with both option aliases header-only.
The normal immutable preview and core approval remain required for any import.

Within either maintained boundary, prepare a minimal candidate as below, then use the local
helper **without** `--qualify-option-aliases`. All target, reference, active Run
Book, preview, core approval and post-import reconciliation gates still apply.
For example:

```bash
python3 pillars/erp/financials/expenses/manage-tax-fields/scripts/tax_option_aliases.py \
  --project-root <project/selected> \
  --baseline-zip <project/selected/exports/fresh-baseline.zip> \
  --candidate-zip <project/selected/artifacts/requested-delta.zip> \
  --dry-run
```

Use `--output-zip` instead of `--dry-run` to write a new candidate. A different
scope or schema requires the controlled qualification procedure below; do not
silently fall back to the test flag in a normal customer workflow.

## Staged switch and tax-rule creates

A new named-BU ENABLE_TAX=Y row and new same-BU tax rules are a supported
two-stage request on the maintained create-Y schemas. Use the qualified
switch-only import first and the ordinary rule-only import second. Select this
route automatically after lifecycle, BU and territory validation; do not ask the
user to qualify a combined import or omit their requested rules. An explicit
Update with no baseline row is an intake mismatch, not a failed create. Resolve
that intent once, record a later Create correction or authorization for baseline
classification, and reuse it in subsequent preparation.

1. Retain a versioned **request ZIP** containing the complete requested create
   delta, bound to the original fresh baseline. It is preparation input, never
   the upload artifact. The helper requires all selected switches to be absent
   Y creates with empty OtherOrgId, and every requested rule to be absent and
   owned by a selected switch BU. Existing-rule updates and mixed lifecycle
   batches are outside this staged route. Validate all business values and
   target references before offering either stage for approval.
2. Prepare stage 1 below. Its identical minimal option aliases contain the new
   switches; EXM_VAT_FIELD is header-only. The report retains the complete
   request hash and deferred rule count. Persist the report, request and stage
   bindings in the active project. Show the user the complete two-stage plan
   before core's exact switch-candidate approval. No extra qualification-choice
   prompt applies; no single approval covers both different import artifacts.

```bash
python3 pillars/erp/financials/expenses/manage-tax-fields/scripts/tax_option_aliases.py \
  --project-root <project/selected> \
  --baseline-zip <project/selected/exports/original-baseline.zip> \
  --candidate-zip <project/selected/artifacts/complete-create-request.zip> \
  --stage switch-create --dry-run
```

3. Replace `--dry-run` with `--output-zip` under that project's `artifacts/`
   to write a new switch candidate. Use the existing Run Book/Data Loader
   validation, preview, approval and submission. After terminal success with
   the expected SetupOption processing, export the full same-target task again
   and reconcile the switch candidate, both aliases and all protected facts.
   Retain process, provenance and reconciliation evidence. Failure or ambiguity
   blocks the rules stage; never resubmit automatically. An OAuth callback-port
   conflict blocks the selected auth/reference step and must be handled through
   core auth; it does not invalidate the create profile or permit another route.
4. Prepare stage 2 from the **original complete request**, the exact submitted
   switch candidate, the original baseline and the fresh post-switch export:

```bash
python3 pillars/erp/financials/expenses/manage-tax-fields/scripts/tax_option_aliases.py \
  --project-root <project/selected> \
  --baseline-zip <project/selected/exports/post-switch-baseline.zip> \
  --candidate-zip <project/selected/artifacts/complete-create-request.zip> \
  --original-baseline-zip <project/selected/exports/original-baseline.zip> \
  --switch-candidate-zip <project/selected/artifacts/submitted-switch.zip> \
  --stage tax-rules --dry-run
```

The helper checks switch-candidate equality with the original request, complete
business readback and unchanged schema/release. Any intervening protected change
or already-created rule stops this handoff for fresh workflow reconciliation;
it does not become an implicit update. Stage 2 uses the fresh export's metadata
and exact headers, preserves requested rule CSV bytes and leaves both option
aliases header-only. It neither replays the switch nor uses another BU's data.

5. Write stage 2 to a new `--output-zip`, revalidate target references and the
   rule-only candidate, and obtain a new core immutable preview/approval. After
   terminal success, export again. Use `--baseline-zip` with the post-switch
   baseline, `--candidate-zip` with the submitted rule candidate and
   `--readback-zip` with this final export to check the requested rules, retained
   switches and all protected facts. Process/provenance checks remain owned by
   the host workflow. Report the two stage outcomes separately; completion
   requires both. If stage 2 fails, retain the successful switch and report the
   partial result rather than inventing rollback or retry authority.

## Prepare the controlled test

For EBS switch-only input, the [EBS adapter](ebs-profile-intake.md) exposes a
source-bound standalone existing N-to-Y qualification branch. Its default is a
question and no candidate. This preparation convenience adds no live-qualified
operation: use the steps below, record terminal process and complete readback
evidence, then review any future profile promotion separately.

1. Resolve the selected nonproduction environment, named BU, active Tax task
   Run Book/project context, desired test value and restoration intent. Do not
   reuse a policy-only Run Book or change shared authentication/Data Loader
   configuration while another chat uses it. Use supported per-invocation
   environment/context arguments; if isolation is unavailable, stop with an
   environment blocker. New projects follow the router's prevalidation gate.
2. Use the routed export and reference-validation workflows for fresh same-task
   template and complete populated baseline exports. Persist exports only under
   the selected project's `exports/`. Verify environment, privileges, catalog
   flags, package members, exact ordered headers and metadata mappings. Both
   setup-option aliases must still map to the reviewed SetupOption service/XML
   path. A changed or ambiguous schema blocks this strategy. Complete baseline
   aliases must have identical unique business facts, ignoring only audit cells.
3. Prefer an existing ENABLE_TAX row with an original Y/N value, so restoration
   is supported. A same-value test cannot qualify persistence. If testing an
   insertion, disclose that deletion is unsupported and require explicit fixture
   retention or another supported cleanup route before mutation. Never infer
   a global BU scope, manufacture OtherOrgId, or borrow another BU's row.
4. Prepare the exact requested switch delta in EXM_SETUP_OPTION.csv, with its
   companion initially header-only or identical. Include only ENABLE_TAX Y/N
   rows for the selected BUs. Preserve existing OtherOrgId for updates; leave it
   empty for a create with a verified named BU. Empty all five audit cells.
   Retain every package member and metadata byte. For switch-only recovery,
   leave EXM_VAT_FIELD.csv header-only; do not replay successful US/OTHER rules.
5. Run the local helper to validate the candidate and replicate the requested
   field/value maps into both aliases using their own captured header order.
   It rejects conflicting aliases, unrelated option codes, duplicate identities,
   changed headers/metadata, guessed transport IDs and an already-satisfied
   switch. It preserves candidate VAT bytes. It does not validate XML semantics,
   prove export provenance, call Fusion or replace the task's schema gates.

```bash
python3 pillars/erp/financials/expenses/manage-tax-fields/scripts/tax_option_aliases.py \
  --project-root <project/selected> \
  --baseline-zip <project/selected/exports/fresh-baseline.zip> \
  --candidate-zip <project/selected/artifacts/requested-delta.zip> \
  --qualify-option-aliases --dry-run
```

Replace `--dry-run` with `--output-zip` pointing to a new versioned ZIP under
the same project's `artifacts/` to write the qualification candidate. Existing
files are never overwritten. Persist the sanitized JSON report with the run's
diagnostics; it binds the candidate and baseline hashes and retains
`live_import_verified: false`. No raw option values appear in this report.

## Execute and reconcile

Evaluate all normal task rules against the final identical-alias candidate.
Record that the selected operation is maintainer qualification, with reusable
qualification pending; never waive a rule to obtain approval. Pass the final
immutable ZIP to current core Data Loader preflight, Task Hook and its unchanged
approval workflow. Present target, BU, before/after switch, preservation scope
and candidate artifact before approval. Submit once through the declared core
route. A timeout or ambiguous outcome requires reconciliation before any retry.

Use core's status/results workflow for terminal status, errors and ProcessLogs.
A successful job with zero SetupOption rows or an unchanged switch is an
incomplete import, even if VatField rows succeeded. Require evidence that the
intended logical SetupOption row was processed; duplicated aliases do not imply
two logical rows. Keep the failed and successful entity outcomes separate.

After terminal evidence, export complete current task data again through the
routed workflow and compare it against the baseline and final candidate:

```bash
python3 pillars/erp/financials/expenses/manage-tax-fields/scripts/tax_option_aliases.py \
  --project-root <project/selected> \
  --baseline-zip <project/selected/exports/fresh-baseline.zip> \
  --candidate-zip <project/selected/artifacts/qualification.zip> \
  --qualify-option-aliases \
  --readback-zip <project/selected/exports/post-import.zip>
```

`readback_matched` requires the requested switch values in both aliases, all
unrequested option facts preserved, and exact requested/preserved tax-rule
business values, including US/OTHER when present. Only server audit fields are
excluded; a newly inserted row may receive a target-owned OtherOrgId. Missing,
extra or divergent identities fail. The report deliberately leaves process
and provenance verification false: the host must independently bind same-target
export IDs, dates and hashes to successful terminal process evidence.

If restoration was selected, reconcile the post-test baseline for intervening
changes, prepare a new reverse delta for only this test's switch, and obtain a
new core preview/approval. After execution, export again and verify restoration
and protected settings. Do not reuse the test candidate or its approval.

## Promotion boundary

Persist target-specific evidence and restoration results in the selected project
along with the skill run and token log. Only after successful Tax-specific
process and readback evidence may a reviewed source change promote that exact
strategy, schema/release, BU scope and existing-row/insertion boundary. Record
a sanitized summary here without environment identifiers or customer rows.
The maintained create-Y insertion and combined N-to-Y update evidence establish
only their respective profiles, not other update combinations, N creates,
global scope, another release or UI maintenance behavior.
Further promotion requires its own retained process, readback and cleanup or
explicit-retention evidence.
