# EBS profile handoff to Manage Tax Fields

Read the parent [profile intake contract](../../references/ebs-profile-migration.md)
first. It handles every source profile and owns cross-task routing. This task
consumes only the maintained AP_WEB_TAX_ENABLE to ENABLE_TAX mapping; it does
not reinterpret unknown profiles as Tax options. The full EBS source hierarchy
must be mapped to explicit target BUs and confirmed before task preparation.

Ask whether to preserve existing tax rules or configure explicit rules. This
is a business decision, separate from Data Loader approval. Reuse a previous
explicit same-scope answer. The CSV does not specify the six field behaviors,
country exceptions or EnabledFlag. Preserve means no VAT delta; review baseline
visibility and disclose if no rules exist or Tax Classification is hidden.
Switch-only completion is not proof of complete EBS UI/tax behavior parity.

For explicit rule changes, use the [setup runbook](setup-runbook.md) and its Tax
rules workbook mapping, retaining the original profile/decision references.
Do not silently narrow that branch to switch-only. New Y switches and new rules
use the existing staged route, with separate core approvals and reconciliation.

## Switch-only candidate adapter

After the owning workflow validates exact environment, Run Book/task scope,
source decisions, BU lookup evidence and fresh same-task export provenance:

```bash
python3 pillars/erp/financials/expenses/manage-tax-fields/scripts/ebs_tax_candidate.py \
  --input /absolute/ebs-profiles.csv --decisions /absolute/decisions.json \
  --environment TARGET --project-root project/PROJECT \
  --baseline-zip project/PROJECT/exports/fresh-task-export.zip --dry-run
```

The adapter recomputes intake from source bytes and decisions; it never trusts a
hand-edited normalized report. It derives lifecycle from the fresh baseline
only after the host has obtained/reused the user's lifecycle determination
choice. Existing equal values become no-ops. Missing named-BU Y values use the
maintained create profile. Preserve source lineage on every proposed operation.

Replace `--dry-run` with `--output-zip project/PROJECT/artifacts/NEW/candidate.zip
--report project/PROJECT/artifacts/NEW/candidate-report.json` for new review-only
artifacts. All members and metadata are retained; both option aliases contain
identical minimal deltas with baseline-owned transport IDs on update, blank IDs
on create and empty audit fields. EXM_VAT_FIELD is header-only, preserving target
rules rather than replaying baseline rows. No-op output writes only a report.
Host registers both artifacts, logs the run, and evaluates all task gates before
core Data Loader preview. Neither local helper proves reference/provenance checks.

Malformed inputs are input validation failures; wrong task/schema/alias contracts
are catalog mismatch; write failures are artifact persistence. Stop after any
failure and retain successful local artifacts as incomplete. Never upload an
orphan candidate if its companion report could not be persisted.

## Standalone existing N-to-Y qualification

A standalone update is not covered by the maintained combined-update profile.
Without explicit qualification intent, the adapter returns a question and no
candidate. Do not invent a US rule to make an update fit the combined profile.

For a requested nonproduction qualification, record a decision JSON with:
`environment`, `source_sha256`, `decisions_sha256`, `baseline_sha256`,
`nonproduction: true`, `confirmation_ref`, and `after_test: retain` or `restore`.
Bind decisions_sha256 to the intake report's canonical decisions digest. Pass
`--qualification-decision /absolute/decision.json`. This branch admits exactly
one changed existing N-to-Y switch with no VAT delta; mixed operations must be
separately planned. It delegates identical aliases to the existing
`tax_option_aliases.prepare_qualification`, not a new importer.

Before execution, satisfy [controlled qualification](option-alias-qualification.md#prepare-the-controlled-test),
including supported cleanup/restoration or explicit retention. Core's immutable
candidate approval remains required. After execution require successful
SetupOption processing, both aliases reading Y, all protected options and VAT
rules unchanged, same-target provenance and successful fresh-export comparison.
If restoring, separately approve a reverse candidate and verify the restoration.
Do not auto-retry a timeout or partial result.

The adapter marks this candidate as qualification-only. Its existence, user
confirmation or unit-test success must never modify
`qualified-option-alias-profile.json`. Promote a standalone update profile only
after retained live process/readback/restoration evidence and a reviewed source
change for the exact operation/release/schema. All current qualification limits
remain intact until then.
