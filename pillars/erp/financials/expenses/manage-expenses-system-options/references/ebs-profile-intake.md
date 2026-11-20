# EBS profile handoff to System Options

Start with the parent [EBS profile intake](../../references/ebs-profile-migration.md).
Preserve source identities, duplicate provenance, exact values and decisions.
Do not infer a Fusion BU from EBS Site, responsibility, application or user IDs.
Ask for explicit target BUs and disclose that the option applies BU-wide.
Reuse same-source, same-target scope decisions; Tax-pilot decisions do not
authorize a different profile's scope.

## Maintained approver mapping

Application 200, internal name `AP_WEB_ALLOW_OVERRIDE_APPROVER`, maps Y/N to
`ENABLE_OVERRIDE_APPROVER` Y/N. The owning workbook field is `User Options` /
`Allow Overriding Approver`, with labels Yes/No. Internal name/application are
the match key; the source profile ID and translated display label are not.

Evidence distinguishes source behavior from the target contract:

- The EBS FND extract identifies the internal name and describes the header
  overriding-approver field as displayed/enterable. EBS 12.2
  [profile documentation](https://docs.oracle.com/cd/E26401_01/doc.122/e48899/T214904T396825.htm)
  describes OIE: Enable Approver as allowing selection of a different approver.
- The maintained [field catalog](intake-fields.json) records this Fusion field
  as a confirmed boolean option. [Create/update evidence](create-update-contract.md)
  establishes the paired FSM option transport.
- Oracle's Financials documentation landing page resolved to 26D when reviewed
  2026-11-04. Its Implementing Expenses guide did not expose this exact field
  in searchable text; no new public-documentation claim of import acceptance
  is made. The target code relies on the existing task catalog/contract.

This migration configures permission to specify an overriding approver. It does
not select the person, require the field, migrate AME/BPM routing, or prove
end-to-end approval behavior. Unknown values or profiles remain unresolved.

## Local conversion

Use the bundled Node runtime and set `PYTHON` to a Python 3.10+ runtime.
The existing task CLI reuses the parent's source/decision assessment, checks
the target field catalog, and creates the standard workbook:

```text
node scripts/expense_system_options_intake.mjs from-ebs --input SOURCE.csv --decisions DECISIONS.json --environment TARGET --dry-run
node scripts/expense_system_options_intake.mjs from-ebs --input SOURCE.csv --decisions DECISIONS.json --environment TARGET --project-root PROJECT --output PROJECT/artifacts/NEW/input.xlsx --report PROJECT/artifacts/NEW/ebs-intake.json
```

Decisions use the parent's source SHA-256/environment/record IDs, action migrate,
confirmation reference and explicit target_business_units. Tax behavior is not
required for approver input. Inputs containing a different task or unsupported
field stop; do not silently discard them. All-excluded or unresolved input
writes only its report. Output destinations must be new project artifact paths.
The report binds source, decisions, mapping catalog, target field catalog and
generated workbook digests. The host registers artifacts, run and token usage.
No external calls, baseline validation or import approval occur in conversion.

Next require the task's ready rule plan and active Run Book scope. Obtain a fresh
same-task baseline and specific-BU reference evidence through the declared
shared/core routes. Run the existing `validate` and `build-import` commands.
The builder reports per-setting create/update/no_change; all-no-change yields
no ZIP. Same value inherited from global setup is not an existing BU override:
explicit named-BU intent creates an override if absent. Retain that distinction
in review. Preserve unrelated options and scalar settings.

For changed setup, submit only through core Data Loader with immutable approval
and then verify process results and a fresh export. Local readiness and ZIP
generation do not establish live import success. Persist partial artifact
failures; never upload a workbook/package whose required report failed to save.
