# Illustrative user-visible conversations

All dialogue below is fictional. In a real run, the exact environment, supported operation and payload must be shown before required authorization. These abbreviations are not executable approval prompts.

## Passed · cleanup verified

**Human:** “Run the reviewed single-draft transactional check for this project in DEMO-TEST.”

**Final response after the fictional outcome:** “The selected check passed. One draft was created, its expected values matched, and separately authorized cleanup was verified. Readiness is READY_WITHIN_VERIFIED_SCOPE for this one check. Wider implementation readiness is not established.”

[Open the sample report](cases/01-pass-cleanup-verified/transactional-validation.html).

## Passed · cleanup pending

**Human:** “Run the reviewed single-draft transactional check for this project in DEMO-TEST.”

**Final response after the fictional outcome:** “The business assertions passed, but cleanup has not been completed. Readiness is NEEDS_REVIEW. The report names the cleanup owner and required next action; it does not claim that the record was removed.”

[Open the sample report](cases/02-pass-cleanup-pending/transactional-validation.html).

## Blocked before execution

**Human:** “Run the reviewed single-draft transactional check for this project in DEMO-TEST.”

**Final response after the fictional outcome:** “The prerequisite reference is disabled, so this check is BLOCKED. No transaction was attempted. The implementation owner must correct the prerequisite and provide current evidence before a later request.”

[Open the sample report](cases/03-blocked-prerequisite/transactional-validation.html).

## Created · business assertion failed

**Human:** “Run the reviewed single-draft transactional check for this project in DEMO-TEST.”

**Final response after the fictional outcome:** “One record was created, but the observed quantity was 2 instead of the expected 1. The check is FAIL and readiness is BLOCKED. Cleanup was separately verified; that does not change the failed business assertion.”

[Open the sample report](cases/04-business-assertion-failed/transactional-validation.html).

## User skipped the check

**Human:** “Skip the offered transactional check for now and record that decision.”

**Final response after the fictional outcome:** “I recorded your decision as SKIPPED. No transaction was attempted, and the selected requirement remains unverified. Readiness is NEEDS_REVIEW. Skipping does not waive controls for future execution.”

[Open the sample report](cases/05-user-skipped/transactional-validation.html).

## Unknown creation outcome

**Human:** “Run the reviewed single-draft transactional check for this project in DEMO-TEST.”

**Final response after the fictional outcome:** “The save timed out and the outcome is INDETERMINATE. The created-record count is unknown, not zero. Reconcile the stable test key through the declared route before another attempt. Cleanup is also unknown.”

[Open the sample report](cases/06-unknown-outcome/transactional-validation.html).
