# Input validation

One controlled27A absent-BU create persisted blank PaymentsApprovalFlag as N while all other requested business values and all pre-existing cells matched. Clarify the intended persisted value before proposing blank as an exact outcome. Never silently coerce blank to N, weaken reconciliation or apply this observation to existing-row updates/other contexts. Source: SRC-E2E-CREATE-C01-164773.
An explicit N is a business choice, not an inferred default. Preserve unrequested existing blanks. Observed normalization is not a proven-invalid input.


For explicit absent-BU creates, require all 13 business values (intentional
optional blanks included), current active/task-eligible BU evidence and explicit
OPERATING_UNIT context. Reject existing identities and protected business
overrides; no implicit upsert. Historical audit/usage cells in a source document
are evidence only: disclose their blank candidate serialization before design
confirmation. Seven EO-required business fields remain mandatory; the automatic
report flag is not one of them. Retain the payment-approval hint uncertainty.
Validate create/update batches atomically through review_operations.

Scope: IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS.

Apply checks to every normalized request atomically. Values are canonical CSV strings; do not infer a Boolean domain or a create default from a field name. Source: SRC-GOLD-UI-FULL, SRC-GOLD-VO-SNIPPETS, SRC-GOLD-EO-SNIPPETS, SRC-USER-ROUNDTRIP-153565.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Exact task and target | Task code, nonproduction/approved target, matching release | Stop before candidate | Confirm exact task and refresh its baseline | Always |  |
| Explicit identity | scope=enterprise with blank CSV BuName; or scope=business_unit with exact BuName | Ask which enterprise or BU | Use the unique baseline identity for update; for create require an absent exact BU identity and current task eligibility; never default scope | Every row | match_baseline_identity |
| Business change | Explicit operation and named changed values | Ask for the intended change | Do not create a candidate while material input is missing | Every row |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Shape and identity | Require exact 23-column package contract and unique identities; immutable keys are not business changes | Always | match_baseline_identity |
| Protected inputs | Reject supplied overrides to BuName, CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, LastUpdateLogin, BusinessUnitId1, ModuleId and ModuleKey | User requests a change to a protected field |  |
| OrgType context | Preserve existing-row context; explicit BU create uses the reviewed OPERATING_UNIT context, never a reassignment | OrgType requested |  |
| Canonical values and lengths | Require strings and source-backed precision. Consult references/task-contract.json; do not impose an unproved closed code domain | Business field supplied |  |
| Known required values | Do not clear fields with corroborated EO requiredness. Preserve other unrequested blanks, including PaymentsApprovalFlag | Existing-row update |  |
| Conflicts and no-op | Clarify duplicate operations for one identity, absent update target or no effective change; no implicit create | Update request |  |
| Bulk atomicity | Any invalid or materially unresolved row prevents candidate generation for the whole request | Multiple rows or mixed operations |  |
| Offline candidate integrity | Recompute the complete design from exact baseline bytes and explicit new-row values/references; reject stale/forged values and compare every candidate cell and original metadata byte | Offline create/update/mixed preparation |  |

## Filter-aware identity validation

A missing named identity in the current export does not alone establish an absent internal-payer row. The export filters named rows through PAYABLES_PAYMENT_BF usage (SRC-GOLD-VO-SNIPPETS, lines46–49). Obtain source-qualified task selection/existence evidence and distinguish it from export visibility. Uncertain existence requires clarification before a create candidate; do not reinterpret it as enterprise or silently upsert.

Known missing payment usage is a visibility limitation, not proof that the supplied create business values are invalid. Disclose the available verification route and prerequisite decision. Do not add a mandatory usage value to the options CSV or infer ledger/legalentity inputs.

## Observed update evidence and its limits

Match update evidence to the exact field, scope and before/after values. Observed only: enterprise AutomaticPprReportSubmit Y -> N -> Y with PprReportFormat=PPR_STATUS_REPORT preserved, terminal success and fresh all-cell reconciliation (164493/164510; corroborated 164559/164580), release11.13.27.01.0. Other scopes, values and report formats remain unresolved. No create default, lookup-domain or new mutation authority follows. Observed only: SraEmailSubject enterprise Automatic Separate Remittance Advice -> FSCR FINIBY-1910 validation -> original, and FGST-Auto Ltd / FGST-Service Ltd blank -> same requested subject -> blank, terminal success and fresh all-cell reconciliation (164559/164580), release11.13.27.01.0. Other subjects/scopes remain unresolved. Blank restoration is not a create default. Preserve canonical lengths, identity, protected-field and atomic checks. Observed evidence does not replace a fresh baseline or the unchanged runtime exact-field decision interface. Sources: SRC-E2E-OBSERVED-AUTOPPR-164493-164510, SRC-E2E-OBSERVED-SUBJECT-164559-164580.

## Observed create and reviewed lookup source boundaries

Only the two recorded retained explicit-N creates are observed: terminal request164877 succeeded, while its original fresh-export comparison failed for hidden expected identities. Later export300104797771464 after separate user-completed prerequisite setup matched both creates and all1219cells of the previous53rows without reimport. c01 blank PaymentsApprovalFlag -> N remains an original FAIL with accepted retention, not a blank-create PASS or universal default. Keep the23-column contract and complete explicit create inputs. The four reviewed source code/label maps are evidence for canonical package codes, not automatic normalization. Confirm the intended code when a label is supplied. Do not reject an off-seed value solely from non-equivalent DEV source; obtain applicable target evidence or the eligible exact-field decision. No new validator is implemented. Sources: SRC-E2E-RETAINED-CREATE-55ROW-164877, SRC-DEV-LOOKUP-SEEDS-20260924, SRC-DEV-INTERNAL-PAYER-EO-LOOKUPS, SRC-DEV-INTERNAL-PAYER-EOIMPL-PPR.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DSO_INPUT | decision | 10 | validate_input | valid->DSO_DEPENDENCIES;missing->DSO_RETURN_MISSING;invalid->DSO_RETURN_FAILED | none | stop | true |
