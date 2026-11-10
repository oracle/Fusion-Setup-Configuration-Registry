# Dependency readiness

Create additionally requires an exact absent identity, current active BU match
and reviewed current-task creation eligibility. An active public BU LOV match
alone does not prove the options-row creation contract. The service owns ID
resolution and assignment. Missing eligibility prevents candidate preparation;
never treat a user-supplied historic ID as the reference lookup.

Scope: IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS.

Requiredness below describes task prerequisites, not a claim that other FSM tasks are universally mandatory. Existing target presence does not prove new-BU create eligibility. Source: SRC-GOLD-AM-SNIPPETS, SRC-GOLD-BU-PVO, SRC-GOLD-BU-PEO, SRC-GOLD-EO-SNIPPETS, SRC-GOLD-EOIMPL.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Exact task baseline | Read current same-target export |
| 2 | BU and option values | Verify only the dependencies of requested values |
| 3 | Resulting report configuration | Validate the automatic-report/format relationship |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| baseline | Same-target exact-task baseline | Yes | Update or reconciliation | Verify | Captured exact-task export | match_baseline_identity | Establish exact existing targets and preserved values | Clarify missing scope and refresh stale baseline | Exact target row |
| business_unit | Existing BU | Conditional | Named BU requires independent existence verification or new setup eligibility analysis | Lookup | Current target BU reference data | find_business_unit_by_exact_name | BU existence is distinct from task-option creation eligibility | Provide exact name; no automatic prerequisite creation | Verified exact BU name; service resolves OrgId |
| report_format | PPR report format | Conditional | Resulting AutomaticPprReportSubmit=Y | Verify | Authoritative target format evidence | verify_option_value_evidence | Source method validator requires a valid nonblank format | Supply or verify the exact format code | PprReportFormat code |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Required target evidence matches uniquely | Read-only verification only |
| Missing | A prerequisite or contract is unresolved | Clarify; create only through its separately supported task and approval |
| Invalid | A proven constraint fails | No candidate |

## Named-BU export visibility

InternalPayerVO requires a matching PAYABLES_PAYMENT_BF usage join for a named BU row to appear in this export (SRC-GOLD-VO-SNIPPETS, lines46–49; SRC-E2E-M01-EXPORT-VISIBILITY-164877). Physical insertion can succeed without that usage. Do not turn this visibility condition into an invented create field or a universal insertion prohibition.

Review task selection/existence and payment-function visibility separately. Public active-BU evidence and create-picker eligibility do not establish the payment usage join. If an export omits an identity and visibility/existence is unresolved, clarify before proposing create; never infer absence and retry.

For a missing business-function assignment, ask whether the prerequisite is intended and obtain the user's business values through its supported task, Assign Business Unit Business Function. Never infer ledger/legalentity values or create prerequisites automatically. After a separately approved repair, refresh the exact-task export and reconcile known existing rows without resubmitting their create.

## Observed update evidence and its limits

For the observed enterprise Y -> N -> Y updates, PprReportFormat=PPR_STATUS_REPORT was preserved; resulting Y still requires a valid nonblank target format. This is not evidence for every format code. Subject updates/restorations were observed for enterprise and FGST-Auto Ltd / FGST-Service Ltd only. Current target, row presence, BU reference and export-visibility checks remain required; historical evidence does not prove current prerequisites. Sources: SRC-E2E-OBSERVED-AUTOPPR-164493-164510, SRC-E2E-OBSERVED-SUBJECT-164559-164580.

## Observed create and reviewed lookup source boundaries

Current active BU reference, task eligibility and payment-function export visibility remain distinct checks. Observed explicit-N create persistence does not make payment usage mandatory for physical insertion or create a universal eligibility rule. Later user-completed prerequisites enable supported export verification; retain the original missing-identity failure and never retry known existing rows. Reviewed DEV seeds/EO filters do not prove current target membership or prerequisites. Sources: SRC-E2E-RETAINED-CREATE-55ROW-164877, SRC-DEV-LOOKUP-SEEDS-20260924, SRC-DEV-INTERNAL-PAYER-EO-LOOKUPS, SRC-DEV-INTERNAL-PAYER-EOIMPL-PPR.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DSO_DEPENDENCIES | decision | 20 | resolve_dependency | satisfied->DSO_BU_REFERENCE;missing->DSO_RETURN_MISSING;invalid->DSO_RETURN_FAILED | DSO_INPUT | stop | true |
