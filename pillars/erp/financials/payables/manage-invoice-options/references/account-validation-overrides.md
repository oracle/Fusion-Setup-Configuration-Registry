# Submit an account unchanged after an explicit user override

An account business-validation failure blocks the record by default. Explain the
actual error and offer correction, **submit unchanged with an override**, explicit
exclusion, or stop. If the user explicitly confirms submission after seeing the
error, retain that decision and its reason. Their confirmation to submit despite
the named error is enough; do not ask a separate “why” question.

This is a validation waiver, not successful validation. FSM can reject the row,
accept it, or save a different/blank account. Do not promise that FSM will throw
an error. Verify the saved account and its usability after an authorized results
check. A failed usability check remains failed even if import reports success.

## Batch commands

The batch review retains the completed account-service result and exact record
context. An eligible blocked row lists `override` among its choices. Use a current
`invoice-account-batch-decision-v1` decision with `approved: true`, `approvalId`,
and the exact `reviewSha256`. In `records`, choose:

```json
{
  "OP-1": {
    "action": "override",
    "reason": "User confirmed submitting this account unchanged despite the invalid-segment error."
  },
  "OP-2": "exclude"
}
```

`interest_account_batch.py select` includes the overridden row unchanged and
writes a bound `submit_interest_account_with_user_override` receipt with
`status=overridden`. It preserves the failure, reason, operation, BU, ledger,
ordered account, selected environment/origin and baseline. No positive CCID is
invented. The ordinary resolver, normalizer, builder and exact-upload validator
preserve the receipt and require its warning. Changed account/context, stale
proof, no explicit reason or missing warnings cannot use that waiver.

For a separately approved SOAP creation that returns a completed business
rejection, `interest_account_creation.py` also writes
`<receipt-stem>-rejection.json`. Re-run batch review with
`--creation-rejection <file>` to present that actual failure and offer the same
explicit override. This does not retry SOAP or turn the error into the automatic
FSM creation fallback. The normal fallback still requires its specific
`GL_ASM_ACCOUNT_DYN_INSERT` evidence.

A service outage, HTTP/authentication failure, SOAP fault, uncertain creation,
wrong target or unsafe package is not an invalid-segment business rejection.
Resolve that execution/context problem; do not label it an account-data waiver.
All unrelated field, archive, identity and authorization checks remain enforced.

## Normal Data Loader approval

Keep the exact user-approved record, error and reason visible in the final import
preview alongside included/excluded rows and any account-creation effect. FSM may
attempt creation for submitted segments; a created GL combination remains even
if the setup import fails or is cancelled. Obtain the normal Data Loader approval
before uploading and initiating the immutable ZIP. Override consent is not import
approval and never changes Fusion's configuration or validation rules.

In Task Hook `ruleResults`, record each affected account-validation resource as
`status: overridden` with the original failure and the user's explicit waiver
and reason, following the core execution guide. Evaluate its unrelated checks
normally; do not mark the failed account check `passed` or waive another error.
Use Task Hook to build, approve and verify the exact archive. Do not hand-write
an approved Task Hook envelope or use a validation override to bypass Data Loader.
