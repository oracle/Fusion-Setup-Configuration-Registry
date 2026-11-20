# Account checks, approved creation and batch review

Use this flow for Interest Expense Distribution changes. It does not authorize
an import, retry or GL creation by itself.

1. Resolve each BU's effective ledger and COA. With a fresh matching COA export,
   check the complete exact combination first. Keep supplied segment positions.
2. Existing account: validate with SOAP `DynamicInsertion=No`. Only Valid plus
   one positive CCID is ready. Explain disabled, date or posting restrictions
   directly. Unknown/service failures remain blocked.
3. Missing account: creation disabled means stop; unknown configuration means
   obtain evidence. Enabled configuration permits offering creation, not a write.
4. Review every record before asking how to handle issues. Present one table
   with operation ID, BU, account, status and reason. Ask once to correct blocked
   records, submit a completed business rejection unchanged with an explicit override, explicitly exclude them, or stop. Corrections require a new review.
   An excluded record is absent from the import; its current settings stay as-is.
5. For missing/enabled accounts the user wants created, prepare the existing
   `interest_account_creation.py` exact previews. Present all requested accounts
   together and obtain one explicit batch answer covering those exact requests.
   Each execution approval must still bind that account's own request and task
   context; the same batch confirmation may be referenced by every approved row.
   Say that created GL accounts remain if the later import is cancelled or fails.
   Submit each approved request once. Configuration permission is not approval.
6. Successful SOAP creation requires read-only revalidation of the same CCID,
   then ordinary resolver evidence. Only `GL_ASM_ACCOUNT_DYN_INSERT` as the sole
   error on a completed approved creation response can enter FSM deferral. A
   fresh complete lookup must still prove absence and enabled configuration.
   Timeouts, SOAP faults, invalid segments, cross-validation errors and existing
   unusable accounts do not qualify. Reconcile uncertain outcomes before retry.
7. Use progress wording such as “Created X of Y missing combinations. The
   remaining Z will be submitted for creation with the Invoice Options import.”
   Derive counts from the actual creation/revalidation receipts; count each
   ledger plus ordered combination once, and show record counts separately.
   Keep technical service details in diagnostics. Do not promise FSM success.
8. The exact Data Loader import preview must list included and excluded records
   and every pending account-creation effect. The normal import approval covers
   both attempting creation and saving Invoice Options. There is no separate
   import waiver and no automatic submission. Exclusions are a batch-selection
   decision, not import approval.
9. After an authorized status check and fresh same-task export, verify both
   saved settings and usable CCIDs. Report saved/validated, failed and pending
   counts; import success alone is not account success. No automatic retry or
   restoration. Partial creation does not mean every setting was saved.

## Commands and evidence

Use `scripts/interest_account_batch.py review --design <design.json> --baseline
<invoice-options.zip> --coa-configuration <coa.zip> --output <review.json>` with
the normal managed OAuth arguments. This checks all records without creating
accounts or silently writing a partial resolved design. It returns every row's
disposition, including creation choices. No import package is produced.

For approved SOAP creation retain the existing single-record command and exact
approval contract. `DEFERRED_TO_FSM` returns exit 2, not a created-account result,
and writes `<receipt-stem>-fsm-deferral.json`. That receipt is distinct from a
valid CCID. Re-run review with `--fsm-deferral <receipt.json>` for each deferral;
the resolver repeats missing/configuration checks and retains current bindings.
The normal resolver also accepts that argument. Never invent a satisfied CCID
receipt for a missing account.

Once creation decisions are resolved, use `select --review <review.json>
--decision <decision.json> --output <selected-design.json>`. The decision is
`invoice-account-batch-decision-v1`, has `approved: true`, a nonblank `approvalId`,
`reviewSha256` from the batch helper's canonical `digest(review)`, and a `records`
object mapping every blocked/creation-pending operation ID to `correct`,
`exclude` or `stop`, or an object `{"action":"override","reason":"<explicit user waiver>"}` for an eligible completed account rejection. `correct` and `stop` produce no selected design. No silent
exclusion or stale input is accepted. To retain an already approved exclusion
after creation outcomes change, include the original report as `sourceReview`
and keep its original `reviewSha256`. The helper requires the same input design,
baseline and record IDs; changed input or a newly blocked record requires a new
decision. This avoids asking again merely because other accounts were created.
With no blocked records or prior exclusions to retain, omit the
decision file; only normal import approval remains. Use the selected design
with the existing normalize/build/validate and Data Loader workflow.

Post-import `verify` takes `--baseline`, `--candidate`, `--blueprint`, `--export`,
`--verification-evidence`, `--target-context` and `--output`, plus managed OAuth
arguments. The selected target context contains environment, baseUrl and the
completed importRequestId. Existing governed readback provenance remains
mandatory. For saved rows it performs SOAP No validation for the expected ledger
and segments. Missing observations/checks are pending; rejected or different
accounts fail. It never imports or retries.

These local receipts enforce context and freshness, at the same caller-evidence
trust boundary as ordinary preflight. They are not cryptographic attestations
of live operations and must be collected by the declared workflow.

## Fresh COA export evidence

Use `scripts/export_interest_account_configuration.py` with the ordinary Task
Level Export arguments `--task-code GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES
--data --project-id <project> --token-cache auto`. It delegates export mechanics
to the shared skill and records a `<export.zip>.observation.json` receipt beside
the unchanged ZIP. Keep both files together. Native Fusion metadata may omit a
timezone; in that case the account check uses the matching completed export
run's UTC observations and ZIP hash, never a guessed server timezone or file
modification time. Old, missing or mismatched observations remain blocked.

## Explicit account-validation override

See [submit unchanged after an explicit user override](account-validation-overrides.md).
Known account business errors remain blocked by default, but the user may
explicitly waive the named failure and keep that row in the approved import.
The waiver remains visible and is separate from the automatic creation fallback.
