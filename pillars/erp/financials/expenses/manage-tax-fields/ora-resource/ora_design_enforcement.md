# Manage Tax Fields scope enforcement

Evidence: SRC-CS-TASK-BO, SRC-CS-TAX-SETUP-VO, SRC-CS-CASH-BO, SRC-CS-SETUP-FSM-AM, FSM-EXPORT.

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Setup option change | Error | | OptionCode is not ENABLE_TAX or BU scope is missing | Route unrelated options separately; no global negative-ID fallback | No automatic change |
| EBS migration intent | Error | | Missing explicit source-scope to named-BU mapping, missing preserve-rules versus explicit-rules choice, or an attempt to treat source Y as Required | Use parent profile intake and references/ebs-profile-intake.md; user mapping proposals do not replace technical evidence | No inferred scope or field behavior |
| Setup-option alias qualification | Error | | A switch write outside the maintained create/update profiles or documented staged-create route without explicit nonproduction qualification, nonidentical aliases, unrelated option data, or incomplete/divergent baseline aliases | Match the operation-specific schema and scope through the local helper without an extra qualification-choice prompt. New switches plus new rules use switch-only then reconciled rule-only stages with separate core approvals; otherwise select controlled qualification. Leave both aliases header-only for rule-only changes | Local replication only within a qualified profile, staged-create route or selected qualification branch; never delete a member |
| Rename, delete or clear requested | Error | | Rename, delete and blank-as-clear are unsupported by this contract | Obtain exact operation evidence rather than treating omission as deletion | No automatic conversion |
| Any live operation | Error | | Incomplete field/resolver contracts or missing immutable preview/loader approval | Complete active runbook and core.data-loader gates | No bypass |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| TAX.DESIGN | step | 5 | design_enforcement | success->TAX.EXECUTION;failure->TAX.ISSUES | TAX.DEFAULTS | stop | create or update |
