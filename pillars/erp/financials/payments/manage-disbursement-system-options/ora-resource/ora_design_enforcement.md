# Design enforcement

One controlled27A absent-BU create persisted blank PaymentsApprovalFlag as N while all other requested business values and all pre-existing cells matched. Clarify the intended persisted value before proposing blank as an exact outcome. Never silently coerce blank to N, weaken reconciliation or apply this observation to existing-row updates/other contexts. Source: SRC-E2E-CREATE-C01-164773.
A fresh N against requested blank remains a mismatch even after terminal success. Later acceptance may resolve retained business state, but never rewrites the original design, erases the failure or authorizes another mutation. All existing cells retain exact preservation.


Explicit create and mixed designs disclose newly added identities, all supplied
business/context values, current references, blank service-owned serialization
and retention. Compare every existing row and every requested new value after
terminal success. New source-owned assignments are reported separately, never
used to excuse an unrelated change. No absent-before create can be described as
a reverse update or automatic deletion. Create preparation remains conditional
on semantic review, exact-field reliance and separate design/candidate gates.

Scope: IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS.

Source: SRC-GOLD-EOIMPL, SRC-GOLD-EO-SNIPPETS, SRC-GOLD-SETUP-SEED and the task contract. A complete static rule graph is not proof of live field qualification. Every requested field still needs applicable evidence or an explicit eligible exact-candidate decision to rely on application validation. That decision does not override a hard control or approve a mutation.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Identity and operation | Confirm exact scope, target and operation-specific evidence |
| 2 | Resulting values | Apply known deterministic rules to the complete resulting row |
| 3 | Uncertainty and business design | Disclose missing evidence, resolve material input and obtain bounded business decisions |
| 4 | Core handoff | Use current Run Book/Data Loader immutable preview and separate mutation approval |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Always | Error | match_baseline_identity | Task, target, baseline identity or protected-field boundary fails | Stop; correct the exact input | No silent fix |
| Resulting AutomaticPprReportSubmit=Y | Error | verify_option_value_evidence | PprReportFormat is blank or proven invalid | Supply the valid exact target report format code | Only user-confirmed change |
| Requested field operation or code evidence is unresolved | Warning | verify_option_value_evidence | Material input unresolved or no eligible exact-field application-validation decision | Explain the gap; collect evidence or obtain the explicit bounded reliance decision while keeping hard checks | No invented values |
| Create requested | Warning | verify_option_value_evidence | Explicit absent identity, complete business/context inputs, current eligibility or bounded qualification design is missing | Resolve input and disclose serialization/retention uncertainty before candidate preparation | No defaults, implicit upsert or invented cleanup |
| Lifecycle requested | Warning |  | Task CSV mechanism is not established | Retain intent and collect authoritative evidence; do not infer product unsupported behavior | No fabricated mechanism |
| Mixed or bulk request | Error |  | Any row has a hard blocker or conflicting operation for one identity | Clarify atomically before candidate generation | No partial mutation |
| Reverse update requested | Error | match_baseline_identity | Original before-values fail design integrity or fresh post-forward state has unrequested drift | Investigate before preparing a new reverse design; obtain independent confirmation and candidate approval | No approval reuse |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| match_baseline_identity | Every existing-row update | Exact selected baseline identity and preserved row | ora_reference_lookups.md |
| verify_option_value_evidence | A requested field needs value/operation qualification | Applicable target code evidence or eligible exact-candidate application-validation decision | ora_reference_lookups.md |

## Preserve visibility and persistence distinctions

Keep terminal processing, physical row existence and task-export reconciliation as separate outcomes. An expected identity missing from fresh export remains a failed exact comparison even when all remaining requested-value mismatch lists are empty. Do not claim the import deleted an old row merely because a report lists a missing expected newly created identity.

The named-row export requires PAYABLES_PAYMENT_BF usage; physical insertion does not necessarily require it. Disclose missing visibility prerequisites and route intended setup separately. Do not automatically retry create, enable business functions, infer ledger/legalentity values, or fill BusinessUnitId1/ModuleId/ModuleKey as a visibility workaround.

Only supported fresh-export/runtime evidence can close the ordinary verification contract. Developer-only SQL diagnosis must not replace that route, become an implementor prerequisite or retrospectively convert an earlier FAIL to PASS. Preserve original evidence and perform a new read-only verification after a separately approved prerequisite repair.

## Observed update evidence and its limits

Recognize the recorded terminal-success plus fresh-export evidence for only the exact two update contracts in references/task-contract.json. Do not report that no live update exists for these contexts or generalize to other values, scopes or fields. A new update or reverse design still requires its current baseline, complete requested/preserved values, runtime exact-field decisions and independent Core approval. Keep AutomaticPprReportSubmit=Y / valid nonblank PprReportFormat enforcement. Historical evidence grants no new mutation authority. Sources: SRC-E2E-OBSERVED-AUTOPPR-164493-164510, SRC-E2E-OBSERVED-SUBJECT-164559-164580.

## Observed create and reviewed lookup source boundaries

Treat controlled create/source-domain evidence as exact-context facts. The observed ANZ/APAC explicit-N create design is not proof for every field value, other BU, current seed domain or cleanup operation. Preserve all original FAILs; later supported export verification is separately recorded and does not authorize new imports. Source mappings require code confirmation and target/revision qualification; BankChargeBearer remains nonexhaustive. Current runtime exact-field decisions, source containment, protected fields, full design and Core approval remain mandatory. No automatic normalization or new resolver route is implemented. Sources: SRC-E2E-RETAINED-CREATE-55ROW-164877, SRC-DEV-LOOKUP-SEEDS-20260924, SRC-DEV-INTERNAL-PAYER-EO-LOOKUPS, SRC-DEV-INTERNAL-PAYER-EOIMPL-PPR.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DSO_DESIGN | decision | 50 | design_enforcement | satisfied->DSO_CORE_GATE;missing->DSO_RETURN_MISSING;invalid->DSO_RETURN_FAILED | DSO_PRESERVATION | stop | true |
