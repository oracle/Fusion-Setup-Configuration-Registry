# Manage Secondary Ledgers Error Handling

Failures remain distinct, actionable, and safe to resume. A read failure is never converted to a missing value, and an uncertain mutation is never replayed automatically.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required or conditional input is missing | Stop before preview and name the exact business field and trigger. |
| An explicit applicable AccountingMethodName cannot be resolved | Preserve the requested method and block until resolve_accounting_method_evidence succeeds; do not substitute Standard Accrual. |
| User supplies physical accounting-method fields | Reject direct tuple intake; resolve the applicable user-selected method through resolve_accounting_method_evidence. |
| Exact lookup returns zero or many eligible rows | Report not found or ambiguous with the exact supplied raw business key, eligibility rules, and a safe correction. |
| GL-781333 duplicate-name or relationship-namespace rejection | Show the exact raw SecondaryLedgerName, the broader ledger/data-access-set/relationship namespace rule, scoped conflict evidence, and require a new unique name; ledgersLOV zero alone is not sufficient. |
| Lookup returns 401 or 403 | Refresh an existing cached token once when allowed and retry the identical GET once; if still failing, report auth or authz and stop. |
| Read returns timeout, 429, or 5xx | Retry only the idempotent GET with bounded backoff, then report transport or Fusion API failure. |
| HTTP 400 or Oracle 29140 | Classify a resolver-contract or input-validation failure from the actual response, persist the sanitized q and error, and stop. Invalid attributes and malformed expressions are not value-not-found outcomes; never retry the identical invalid q. |
| Client, paging, serialization, or other HTTP failure | Preserve the failure class and sanitized response details; never report value not found. |
| Package scope, member, header, alias, or manifest differs | Stop as catalog mismatch or input validation and acquire a fresh same-task export. |
| Scoped export has no secondary at the requested conversion level | Continue normal validation using the documented baseline. An absent example is not a catalog mismatch or a reason to require a donor or override; identify any actual schema or unsupported-design issue separately. |
| Source primary creation or primary options is incomplete or unverified | Allow secondary package preparation to remain a draft, but block preview approval and live import. Complete and verify primary-context GL_SPECIFY_LEDGER_OPTIONS, then regenerate the secondary preview; a prior approval is stale. |
| Fusion returns GL_ASM_PL_OPTNS_NOT_COMPL | Classify as a dependency-readiness/process failure, prove whether any secondary or relationship row was partially created by exact read-only reconciliation, complete and verify the primary options, rebuild from a fresh export, and require a new preview and approval. Never replay the failed or uncertain package. |
| Preview reveals an unintended row or field change | Reject the package and rebuild the smallest delta from the validated baseline. |
| Approval is absent or stale | Stop as approval blocker; never submit. |
| Import request fails before a confirmed submission | Report the exact failure; do not auto-retry a live import. |
| Import status is unknown | Reconcile by read-only status and re-export before considering another submission. |
| Polling times out | Stop and report environment, operation, task code, process or request identity, last status, elapsed wait, and next-check path. |
| Fusion process fails | Retrieve and preserve available ProcessLog and status payload, report partial successes and an errors array with nonzero status, then stop. |
| Ledger exists but relationship import fails | Re-export the identical scope before retrying: physical creation can already be committed. Verify the existing target category and identity, repair the missing or invalid relationship keys and matching rule parents against that target, and obtain a new approved preview. Do not create a duplicate or fabricate generated short names. |
| Re-export does not prove the intended semantic delta | Classify process failed or verification failure and do not claim completion. |
| Diagnostic persistence fails | Return artifact persistence failure with intended safe destination and keep secrets and sensitive payloads redacted. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Missing, malformed, out-of-range, conflicting, or incompatible user input | Correct the named field and rerun validation. |
| Catalog mismatch | Task, package, schema, alias, release, scope, or broader-name evidence disagrees | Acquire matching authoritative evidence. |
| Auth or authz | Authentication failed or principal lacks read or task privilege | Correct credentials or privileges; do not reinterpret as not found. |
| Transport or environment | Network, timeout, target identity, or environment failure | Verify the target and retry only safe idempotent reads. |
| Fusion API | Oracle read or import endpoint returns a product or HTTP error | Preserve sanitized code and message and stop. |
| Process timeout | Polling bound expires while final state is unknown | Report resume data and use read-only reconciliation. |
| Process failed | Fusion process reaches failed state or verification does not prove the delta | Preserve logs and fix root cause before a new approved preview. |
| Artifact persistence | Package, preview, diagnostic, or re-export cannot be stored safely | Correct the destination without exposing sensitive data. |
| Approval blocker | Preview approval is missing, stale, or not accountable | Obtain new explicit approval for the exact preview. |
| Dependency readiness | The source primary or its mandatory options are not successfully imported and re-export verified | Complete the exact predecessor, regenerate the preview, and obtain fresh approval before secondary import. |

## Package Execution Gate

| Gate | What Must Happen |
|---|---|
| Acquire | Use validated project package, fresh direct export, then signed-in UI download; block if all are unavailable. |
| Preflight | Validate target identity and privileges plus package source, release, task scope, eleven members, headers, aliases, ZIP shape, safe paths, and approval requirement. |
| Preview | Show row adds, updates, deletes, field population class, intentional blanks, service-owned values, warnings, handoffs, and semantic effects. |
| Approve | Bind explicit approval to the preview fingerprint and intended environment. |
| Submit | Use the authorized CSV import executor exactly once. No Task Node in this resource itself performs a REST write. |
| Monitor | Poll the documented external process to terminal state and retain sanitized status and logs. |
| Verify | Re-export identical scope and require the secondary rows, disabled relationship, conditional rule, generated identifiers, and all preserved values to match intent. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Validation failure | Task identity, field, exact supplied raw value, any separately documented enum or numeric canonical form, violated rule, trigger, and requested correction. |
| Lookup failure | Resolver, business key, match count or failure class, eligibility criteria, and safe next action without credentials or protected payloads. |
| Preview | Exact business effect, package members touched, row counts, field provenance, open boundaries, UI handoffs, and approval fingerprint. |
| Timeout or failure | Environment, operation, task code, external process or request identity, last status, elapsed time, sanitized logs, partial successes, errors, and resume path. |
| Verification | Intended versus observed semantic delta, generated service values, relationship status, and any mismatch. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Required input or exact identity is missing | Do not guess a business choice, choose the first LOV row, or copy an unrelated ledger. |
| Authorization or client call fails | Do not say the value was not found. |
| Optional ledger options were not requested | Do not turn them into baseline intake or enable them. |
| Different currency or COA | Do not invent Corporate, a mapping name, or conversion rules. |
| Accounting method is omitted or another method is desired | Do not populate methods for BALANCE/JOURNAL, leave the required SUBLEDGER tuple blank, overwrite an explicit applicable method with Standard Accrual, or copy the primary method implicitly. |
| Package or preview is unapproved | Do not import, overwrite, activate, or enable a relationship. |
| Primary options are pending, failed, or unverified | Do not infer readiness from a primary-ledger LOV match, submit the secondary concurrently, or reuse an approval created before the dependency became ready. |
| Live import or process outcome is uncertain | Do not automatically retry or submit a second process. |
| Review and Submit is requested | Do not mutate submission or activation state; boundary GL-07 remains open. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MSL-060-EXECUTION-GATE | decision | 60 | execution_gate | verified->MSL-080-RETURN-VERIFIED;blocked->MSL-070-HANDLE-ERROR;failed->MSL-070-HANDLE-ERROR | MSL-050-ENFORCE-DESIGN | stop | Always |
| MSL-070-HANDLE-ERROR | step | 70 | error_handler | stopped->MSL-090-RETURN-ISSUES | none | stop | A prior node returns an invalid, unresolved, blocked, or failed outcome |
| MSL-080-RETURN-VERIFIED | terminal | 80 | terminal | none | MSL-060-EXECUTION-GATE | stop | Identical-scope re-export proves the intended in-process structural delta |
| MSL-090-RETURN-ISSUES | terminal | 90 | terminal | none | MSL-070-HANDLE-ERROR | stop | Error handling has produced an actionable stop record |
