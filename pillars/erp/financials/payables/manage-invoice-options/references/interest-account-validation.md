# Interest account validation and test cases

## Decision rules

Use the selected BU's effective ledger and that COA's ordered segments. Preserve
leading zeros and blank positions in the native LF vector. A display separator
is not enough to determine boundaries when a segment itself contains a hyphen.

The task-owned account service call is validation-only (`DynamicInsertion=No`).
Continue only with successful HTTP, exactly one `Status=Valid`, one positive
CCID, no SOAP fault and no contradictory error. Keep the existing receipt bound
to operation, BU, ledger, ordered segments, environment and baseline. The account
API performs the eligibility check; a separate flag/date lookup is not required
to block the tested service rejections. Such lookups may explain test data.

On rejection, explain the account problem directly: disabled, not currently active
because of its dates, or posting not allowed. Avoid the preface “Fusion rejected
it.” If no specific reason is available, say the existing account could not be
validated for use. Keep the bounded `ErrorCode` and `Error` in diagnostic evidence,
not as instructions. The helper retains these under `validationFailure`; the resolver
returns them in its blocking diagnostic. `returnedCcId=-1` is diagnostic only,
never a successful receipt. Unknown, malformed or unavailable results cannot
establish that an account is missing. Do not reuse a successful receipt after a
new lookup fails or turn account-service failures into advisory checks.

## Validation and regression matrix

The normal expected result is below. Offline cases use synthetic inputs; they
are not claims that every response has been observed live. Live comparisons are
recorded separately below. Test candidate preparation as well as the helper:
rejections must produce no candidate and no satisfied account receipt.

| Pattern | Required behavior / test |
|---|---|
| Existing eligible account | HTTP success + Valid + positive CCID continues to the normal preview and approval. |
| Confirmed missing; individual values exist | Invalid is blocking. Prove absence separately; existing values do not prove cross-validation eligibility. Do not infer the COA configuration from a creation-not-allowed response. |
| Caller requests creation / request Yes | Current task still validates with No. No silent creation or validation waiver. Use the separately approved creation command below; validation remains No. |
| Fusion creation configuration disabled | A request parameter cannot override it. Explain the restriction; request an existing account or administrator review. |
| Fusion reports an invalid or missing segment value | Send the supplied values and blank positions to Fusion. If Fusion specifically rejects a segment, display that reason and request corrected input. Do not infer segment invalidity from a generic rejection or from absence in existing accounts. |
| Cross-validation rule violation | Display the service reason and request another permitted combination. |
| Existing disabled account | Block; display disabled-account reason; no creation offer. |
| Existing end-dated account | Block; display date restriction; no creation offer. |
| Existing future-dated account | Block; display date restriction; no creation offer. An existing ID is still not usable now. |
| Existing summary account | Block when service rejects. Do not infer a summary-specific cause solely from a generic or combined error. |
| Existing detail account disallows posting | Block; display posting restriction; no creation offer. |
| Wrong ledger/COA or receipt for another context | Reject mismatched context; resolve the correct BU/ledger/segments. |
| Supplied segment count/order or blank positions | Preserve the supplied positional vector and let Fusion decide business validity. Do not rearrange values, reject blank active slots, or enforce a local COA segment-count rule. Retain the transport contract of at most 30 slots and safe serialization. |
| Literal hyphen in a segment | Use positional LF input; do not guess segment boundaries from a concatenated string. |
| Valid without positive CCID | Block as incomplete response, not a missing account. |
| Zero, negative, malformed or duplicate CCIDs; contradictory statuses/errors | Block. Retain -1 only as rejection evidence; ambiguous fields cannot establish validity. |
| SOAP fault, including HTTP 200 | Block as service failure; omit raw fault text. |
| HTTP failure, auth failure, timeout or unavailable service | Block; use the declared authentication/recovery route. Do not infer absence or retry a mutation. |
| Malformed/oversized XML or unexpected response structure | Block as response-contract failure; never use unrelated/header fields as validity evidence. |
| Missing, stale or mismatched validation receipt | Block candidate preparation; require fresh context-bound validation. |
| BU absent or ambiguous / missing ledger | Resolve the target before validation; use a substitute only when authorized. |
| User provides only numeric CCID | Obtain the full combination or a supported authoritative ID resolution; never treat the ID as a segment. |
| Unrelated field change with account/ledger/interest unchanged | Preserve the account; no unnecessary account validation or creation prompt. |
| Interest explicitly disabled and account cleared | Use the supported disable/clear path; blank inactive account is not a missing account to create. |

## Missing-account creation branch

`DynamicInsertion` is the per-request instruction. Fusion's
`DynamicCombinationCreationAllowed` is persisted COA configuration. No on the
request prohibits creation even if the configuration permits it; Yes on a
request does not override disabled configuration. The ordinary validator does
not read that setting; the classification flow reads it from a fresh matching
COA structure-instance export. A generic Invalid/-1 result proves neither absence nor
the setting's value.

The intended conversation, through the task-owned classification and creation commands:

1. Confirm absence in the applicable COA through complete authoritative lookup
   evidence. Preserve ordered segments, verify configuration
   and available execution privileges. Let Fusion validate segment requiredness,
   segment values and combination eligibility. If evidence is incomplete, stop that
   branch and explain what remains unknown.
2. Configuration enabled: ask “This combination does not exist.
   Dynamic creation is enabled. Do you want to create it, use an existing
   account, or stop?” Configuration disabled: explain why creation is unavailable.
3. A decline creates nothing and changes no setup. Configuration permission is
   not user approval. Any creation needs the owning workflow's exact preview
   and approval; revalidate the resulting positive CCID before resuming Invoice
   Options preparation.

Common Options and Distribution Sets have separate creation workflows. Invoice Options
owns `scripts/account_combination_workflow.py` for exact request approval, durable
execution receipts and core OAuth/HTTP delegation, with baseline/BU/configuration
binding in its creation command. It does not import either sibling’s creation code. Use `interest_account_creation.py` only after the configuration/absence check and
exact request approval. Never call an undeclared endpoint or flip the validator to Yes. The enabled,
disabled, unknown-setting, decline, creation-failure and approved-success paths
are covered by the new classification/approval flow and synthetic regression tests.
Live creation still requires exact user approval and separate result verification.

## Live evidence and interpretation

Project evidence records 3 November 2026 tests on a non-production environment,
release 11.13.27.01.0.
These are observations of this Invoice Options path, not universal Fusion rules.
Exact account values, approvals, process identities, screenshots and readbacks
remain in the project evidence; do not hardcode those fixtures in runtime rules.

| Existing-account state | Account API | FSM negative import with approved preflight bypass | UI |
|---|---|---|---|
| Disabled | Invalid / -1; `GL_ACCT_COMB_DIS_ACCT` | Reported success; requested account in fresh export | No exact LOV match; account dialog rejected |
| End-dated | Invalid / -1; `GL_ASM_ACCOUNT_EXPIRED` | Reported success; requested account in fresh export | No exact LOV match; account dialog rejected |
| Future-dated | Invalid / -1; `GL_ASM_ACCOUNT_EXPIRED` | Reported success; requested account in fresh export | Displayed FSM-imported value, but no exact LOV match and dialog rejected new selection |
| Summary, also posting disallowed | Invalid / -1; `GL_ASM_ACCOUNT_POSTING, GL_ASM_ACCOUNT_EXPIRED` | Reported success; exported InterestSegments was blank | No exact LOV match; account dialog rejected |
| Detail posting disallowed | Invalid / -1; `GL_ASM_ACCOUNT_POSTING` | Reported success; requested account in fresh export | No exact LOV match; account dialog rejected |

The summary fixture also disallows posting, so it does not isolate SummaryFlag.
Its extra expired-account message was observed despite blank account-level
dates; the source was not established. A blank export does not prove the
underlying database CCID is null. The service's date message covers both past
end dates and future start dates. UI display of an imported value is not proof
that the UI permits selecting or saving it. No downstream accounting/posting
transaction was tested. Both API and LOV positive controls succeeded.

Retain the API gate. Import success cannot replace preflight or the existing
`verify-interest` post-import check: blank/different requested account is FAIL;
missing readback is PENDING. This check proves retention, not downstream posting
eligibility. Negative test bypasses are developer experiments with explicit
approval, not a supported task waiver. Test restorations were separately
authorized and verified; do not automatically restore normal user changes.


## Reviewed SOAP-to-FSM creation fallback

For the current batch behavior use [Account checks and batch review](interest-account-batch-flow.md).
This adds one narrow alternative to the positive-existing-CCID gate: an exact
approved creation rejection `GL_ASM_ACCOUNT_DYN_INSERT`, fresh proof of absence
and enabled configuration, and a bound deferred-creation receipt. No valid
account is claimed before import. All other rejected/unknown accounts remain
blocked. The user explicitly selects any exclusions and approves the exact
import with its account-creation effects. Ordinary validation remains read-only.
