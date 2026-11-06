# Identical option-alias qualification

The adapter checks the fresh template schema without a release-number allowlist. Candidate preparation does not qualify ordinary option writes by itself.

Candidate `identical-option-aliases-schema-candidate-v1` is implemented in
`fsm_transport.compose_changes` and `prepare_members`. It is available only for
an explicitly selected, non-production maintainer qualification run. It is not
yet a qualified customer profile or evidence of a successful Fusion import.

## Exact candidate

After fresh same-target template and baseline export, map only the explicit
`auto_submission` control to `ENABLE_AUTO_SUB_DA_EXP` with ValueCode Y or N.
Create one row per requested canonical BU/global key and put the same field/value
map in **both** option aliases, using each member's captured header order. Keep
all five server-owned audit fields empty. A verified named BU uses its exact
BuName and empty OtherOrgId; explicit global scope uses empty BuName and -1.
Organization changes remain solely in EXM_ORG_SETTING. Preserve all template
members and metadata bytes. Never include unrelated baseline rows in the delta.

The exact schema guard remains mandatory. Canonical revalidation rejects
forged codes/values/fields and duplicate requested identities. The source-backed
reason to test this strategy is that the reviewed shared-node collision picks
one alias; either candidate alias supplies the same requested values. Offline
equality and simulated order checks do not establish deployed behavior.

## Run the controlled test

1. Obtain the human's explicit non-production environment, test BU/scope and
   intended setting change plus restoration intent. Do not default to an
   author's environment, change a customer's enablement for testing, or infer
   approval from a workbook instruction.
2. Follow the router, active Run Book, core auth, export and target-reference
   workflows. Present exact export requests for the applicable approval. Get
   a fresh template and complete current-data baseline; store no raw export or
   credentials in tracked source. The higher-priority repository protection
   against customer data in project workspaces also applies to raw exports.
3. Resolve canonical option facts from both complete aliases and call
   `reconcile_option_baseline`. Identical unique rows become one baseline fact;
   divergent/missing/duplicate identities stop the test. Preserve all other
   settings for read-back comparison. For enabling, verify the complete current
   or requested schedule, including the user's confirmed enabled time zone.
4. Start the normal task adapter with `--qualify-option-aliases`. This is the
   declared engineering qualification branch, not a readiness override. Send
   the ordinary requests/environment_binding plus `option_alias_baseline`, a
   mapping from both exact CSV member names to workflow-resolved canonical option
   fact arrays. `baseline` contains organization facts only when this field is
   supplied. Empty alias arrays require evidence that both complete exports
   contain no option rows; they are not permission to skip the baseline.
5. Optionally add `--dry-run` for local candidate validation. For the live test,
   run every normal task rule and qualify this exact candidate for this
   user-selected test only. In Task Hook results explicitly record candidate
   status and that reusable live qualification is still pending. Do not use
   a skipped/overridden/waived rule result to reach approval. Explain the test
   change to the user and present core's unchanged preview for approval.
6. Prepare the candidate ZIP before core preflight and Task Hook. Retain core's
   exact-artifact preview/approval records and submit once through the maintenance
   Data Loader handoff in execution-contract.md. Use the declared core
   status workflow to verify completion and process errors. A transport timeout
   or ambiguous outcome requires reconciliation before any retry or restoration;
   never assume the current enable state.
7. Export current data again through the approved export workflow. Call
   `verify_option_readback` with canonical changes and the before/after alias
   facts. It requires the requested results in both aliases and exact preservation
   of every unrequested option fact. Independently compare all organization
   settings and any other exported members, excluding documented server-owned
   audit timestamps only. Require successful process results and same-target
   provenance; the helper does not establish provenance or certify Fusion.
8. If restoration was selected, prepare a new candidate using the post-test
   baseline and the exact original values. Obtain core's new preview approval,
   verify completion, export again, and confirm restoration and preservation.
   Do not reuse the test preview or hide an incomplete restoration.

## Promotion criteria

Record a sanitized evidence summary in the maintained transport profile only
after the import and read-back checks pass. Include release/schema, strategy,
tested BU/global scope, existing-row versus insertion coverage, preservation
checks and restoration outcome. Do not put environment identifiers, credentials,
customer rows or raw payloads into the reusable skill. Keep target-specific run
diagnostics outside the commit under the applicable retention rules.

Promote only the verified scope/operation to the normal customer route and add
regression coverage for that boundary. A BU existing-row test does not qualify
global writes, row insertion or another release. The deployed source difference,
if any, must remain visible. Until promotion, ordinary customer enable/disable
writes retain FSM_ALIAS_COLLISION, while the explicit qualification branch is
executable with normal core approval. No core changes are required.
