# Meals error handling

Use [ordinary Meals execution](../references/ordinary-meals-execution.md) for
the supported workbook and governed workflow.

Follow [diagnostic handling](../references/error-contract.md); core Data Loader
owns status/errors and native reports. Unknown product messages remain unresolved.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Workbook/type failure | Stop before candidate creation; report sheet/cell and corrective action |
| Baseline/schema/reference/artifact mismatch | Preserve exact failure class and identity; no guessed defaults or alternative route |
| Failed or partial Fusion job | Use same-request core status/error route and available ProcessLog; reconcile possible partial effects |
| Timeout | Retain environment/task/process ID, last status and elapsed wait; stop until user requests checking the same attempt |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Invalid workbook/value | Correct and revalidate |
| Catalog mismatch | Unsupported contract or bound identity/schema mismatch | Resolve exact mismatch before handoff |
| Auth/authz or transport/environment | Core cannot read target | Use declared recovery; not an invalid currency diagnosis |
| Approval blocker | Native approval absent | Use core approval workflow |
| Process failed/partial | Unverified or unsuccessful persistence | Reconcile and obtain human completion/retry decision |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Native preview | Actual core preview, qualification limits and known create normalization/audits |
| Completion | Requested/preserved cells, target audits, non-target full rows and strict metadata |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Partial/failure/metadata drift | No automatic replay, repair, cleanup or rollback |
| Unqualified alternative | No trial, old waiver or fabricated native envelope |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| POLICY.RETURN_ISSUES | terminal | 60 | terminal | none | none | stop | Any failed task validation or unresolved contract |
| POLICY.RULES_COMPLETE | terminal | 70 | terminal | none | POLICY.DESIGN | stop | Task rule checks completed; this does not represent an import or persisted-state verification |

## Redaction Rules

Apply [repository error-handling guidance](../../../../../../governance/error-handling-guidelines.md)
before printing or persisting task-local validation, reference, candidate,
reconciliation or failure evidence:

- Never include credentials, access/refresh tokens, token-cache contents, private
  keys, tenant secrets, wallet contents, authorization headers, session cookies
  or full base64 payloads. Do not dump authentication configuration, raw HTTP
  headers or entire request/response bodies into diagnostics.
- Replace sensitive customer values in diagnostic excerpts with `[REDACTED]`.
  Retain field names, sheet/cell or row identity, severity, failure class,
  environment, TaskCode, ProcessId/requestId and ECID where available so the
  failure remains actionable. Redact sensitive values embedded in Fusion error
  messages without inventing or changing their product meaning.
- Keep authorized setup exports under the active project's untracked `exports/`
  directory and generated candidates in its declared artifact directory. Do not
  copy customer setup rows into tracked skill resources or audit reports.
  Diagnostic redaction must not rewrite the immutable import artifact, its hash,
  reference bindings or native approval envelopes.
- Core services own authentication and native report redaction. Return their
  safe native Markdown report unchanged. If a native report exposes a prohibited
  value, stop disclosure and report a redaction failure to the owning core
  workflow rather than copying the unsafe report or fabricating a replacement
  native result. Do not persist an unredacted diagnostic copy.
