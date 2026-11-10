# Error handling and core handoff

Create/mixed preflight fails atomically on any missing input, duplicate identity,
protected override or missing active/task-eligible reference. Do not silently
convert duplicate create into update. An added row has no prior value to restore;
do not use CSV omission as deletion. The complete design must state intended
retention unless a separately proved cleanup mechanism is available. A failed
or uncertain create still requires fresh-export inspection before any new
attempt; never reuse its candidate or replay approval.

Scope: IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS.

Task validation success is not load success. Current Run Book and Data Loader own input processing, immutable preview, approvals, payload assembly, upload and submission. Preserve their memory-only session contract and retained process handle. Evaluate only captured records during that session; corrected input requires cancellation and a fresh session.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Missing or ambiguous input | Ask bounded questions and keep the request unresolved; no candidate |
| Proven invalid value or protected field | Show the affected row/field and constraint; do not waive it |
| Unresolved operation/lookup evidence | Explain evidence_unresolved distinctly from invalid or unsupported; bounded application-validation reliance is possible only where the Builder/task contract permits |
| Application rejection | Preserve available terminal errors safely; obtain fresh exact-task export to detect partial persistence; new decision and fresh candidate required |
| Unknown outcome or lost session | Never resubmit or replay approval. Reconcile through the current core status workflow and fresh export |
| Upload or initiation succeeds | Wait for terminal import success, zero failed rows and no unresolved warnings; then reconcile all requested and preserved values |
| Cleanup needed | Use separately confirmed reverse design and fresh candidate approval only when supported; otherwise disclose retained changes |
| Offline package or design integrity failure | Reject changed metadata/member order, forged before-values, extra changes or a mismatched baseline; never rewrite the design to make a candidate pass |
| Fresh reverse baseline differs | Stop reversal on requested/unrequested/unrelated state drift; do not restore from an old baseline or reuse forward approval |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Business design | Complete normalized business scope, operations, requested values, preserved values and unresolved evidence |
| Core approval | Use the active core preview/approval contract exactly; do not recreate retired approval files or persist protected session material |
| Verification | Terminal outcome, row counts, warnings/errors and exact fresh-export reconciliation; permitted audit changes shown separately |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Identity or package mismatch | No mutation and no fallback to another task/target |
| Changed/lost/expired preview | No approval replay or recovered file envelope |
| Failed candidate or ambiguous write | No automatic retry or resubmission |
| Missing delete contract | No deletion inferred from row omission |

## Successful process with missing exported identities

If terminal processing succeeds but expected BU identities are absent from the fresh task export, retain the failed reconciliation and inspect the source-qualified visibility boundary. InternalPayerVO excludes named rows without PAYABLES_PAYMENT_BF usage (SRC-GOLD-VO-SNIPPETS, lines46–49). Existing rows may be hidden; absence from export does not authorize another create.

Check the immutable input identity/hash, exact task/target, terminal diagnostics and supported task selection/visibility evidence. Ask a bounded prerequisite/existence question when needed. Do not retry a failed candidate, infer deletion, use SQL as the runtime reconciler, or supply protected usage fields. A missing-identity report concerns the candidate's expected set; it is not proof that a pre-existing row was removed.

Where an intended prerequisite is repaired separately, obtain a fresh exact-task export and reconcile without resubmitting known existing rows. Preserve the original failed attempt and record later verification as a separate outcome.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DSO_CORE_GATE | decision | 60 | execution_gate | validated->DSO_RETURN_VALIDATED;missing->DSO_RETURN_MISSING;invalid->DSO_RETURN_FAILED | DSO_DESIGN | stop | true |
| DSO_RETURN_VALIDATED | terminal | 90 | terminal | none | none | stop | true |
| DSO_RETURN_MISSING | terminal | 91 | terminal | none | none | stop | true |
| DSO_RETURN_FAILED | terminal | 92 | terminal | none | none | stop | true |

DSO_RETURN_VALIDATED means only task checks permit the next governed core step; no write or import success is implied. DSO_RETURN_MISSING returns unresolved facts/decisions. DSO_RETURN_FAILED returns deterministic violations. None authorizes a submission.
