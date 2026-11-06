# Manage Reporting Currencies Error Handling

Failures are fail-closed and produce a sanitized, actionable record. This resource may prepare and verify artifacts but does not import them directly. Live import, polling, and diagnostics use core.data-loader after its own approval gate.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Required input is absent or a conditional group is partial | Classify input validation, list the exact missing members, retain the user's values, and stop before defaulting or packaging. |
| A free-text LOV value has zero or multiple eligible matches | Classify catalog mismatch, show resolver and sanitized candidates or filters, ask for an exact value, and stop. |
| Authentication or transport fails before a complete lookup result | Never translate the failure into not found; retain the original failure classification and stop. |
| Rounding-account lookup is rejected or returns zero without the verified request contract | Preserve the original result and correct the request using resolve_rounding_account before declaring the account missing or requesting a replacement. Re-run only the corrected read-only lookup; apply its exact-match and eligibility rules. |
| Ledger resolution succeeds but scoped-export request construction is wrong | Classify input validation or approval blocker, show the exact non-sensitive request differences, and stop before POST. Require the serialized root-key order TaskCode, SetupTaskCSVExportCriteria, SetupTaskCSVExportProcess; require root TaskCode and both child TaskCodes GL_MANAGE_REPORTING_CURRENCIES, root-sibling criteria and process arrays, GL_PRIMARY_LEDGER, Set1, PRIMARY_LEDGER_ID, and AttributeValue equal to the validated numeric primary-root LedgerId. |
| SetupTaskCSVExportProcess was serialized before SetupTaskCSVExportCriteria | Stop and classify input validation before POST. If the POST already occurred, preserve and reconcile its ProcessId, classify the resulting package as invalid scoped evidence, and do not automatically retry; obtain explicit approval before one fresh criteria-first POST. |
| Export returns only ORA_GL_PRIMARY_LEDGER_CONFIG.csv, GL_PRIMARY_LEDGER.csv, and ASM_SETUP_CSV_METADATA.xml | Classify catalog mismatch and broad or incomplete export. Record the serialized request order and member list, quarantine the package, and reject it as a Manage Reporting Currencies template even when process status is successful. |
| Scoped-export POST succeeds but ProcessId, task, scope, or package proof is absent or contradictory | Do not submit another create request automatically. Classify Fusion API, process state, or catalog mismatch; reconcile the returned ProcessId and require exact GL_MANAGE_REPORTING_CURRENCIES plus numeric PRIMARY_LEDGER_ID package metadata before use. |
| Source export is stale, broad, cross-environment, damaged, or missing the source root | Classify input validation or artifact persistence as appropriate, quarantine the candidate, and request a fresh scoped export. |
| Current package headers or metadata disagree with the authoring contract | Classify catalog mismatch, record exact member and checksum differences, and do not retrofit historical headers. |
| Auth or privilege prevents a read-only lookup | Classify auth or authz; retry only the identical GET once after a permitted cached-token refresh, then stop. |
| Read-only request times out, is throttled, or returns a recoverable server failure | Classify transport or Fusion API; use bounded retry only for the idempotent GET and preserve the final sanitized response. |
| A live POST, import, or process submission response is uncertain | Do not retry automatically; classify approval blocker, transport, Fusion API, or process state and reconcile by immutable artifact and external ID. |
| FIND_RATE has missing or invalid max days | Classify input validation, require an explicit integer from 1 through 999, and do not silently use a sample value. |
| REPORT_ERROR has a max-day value | Classify input validation, show that the field must be blank, and rebuild only after correction. |
| First Opened Period was omitted by the user | Do not report missing input for Journal or Subledger. Derive FirstLedgerPeriodName, PeriodSetName, and AccountedPeriodType from the exact scoped source physical row and run resolve_first_opened_period. |
| accountingPeriodsLOV rejects the query attributes | Classify Fusion API or catalog mismatch, preserve the sanitized error, and correct the query to the endpoint's actual response contract; PeriodSetNameId and PeriodType are the confirmed scope fields. Do not reinterpret HTTP 400 as zero matches. |
| Export-derived FirstLedgerPeriodName has no unique exact non-adjustment PeriodNameId match | Classify catalog mismatch, report the exported tuple, complete-result count, exact match count, and adjustment evidence, and stop before package authoring. Do not ask the user to guess another period. |
| First Opened Period and initialization eligibility were conflated | Classify catalog mismatch, preserve the source-derived FirstLedgerPeriodName only if its own LOV validation passed, resolve the initialization predicate independently, and discard initialization dates from the invalid match. |
| Initialization is partial or inconsistent | Classify input validation, list all five atomic fields and the failed predicate, and stop. |
| Physical alias rows differ or an identifier is fabricated | Classify input validation, report exact field differences, and rebuild from the authoritative source template with both service identifiers blank. |
| Relationship ledger keys are blank or unresolved | Block before import and identify the exact alias and expected role. A blank or unresolved Name2 can leave SlaLedgerId unresolved and cause JBO-26041 for SLA_LEDGER_ID; repair the role mapping, not a fabricated ledger ID. |
| CSV cannot be reopened or a row width, quote, newline, header, member, order, or metadata check fails | Classify artifact persistence, preserve the failed validation report, and do not send the ZIP to data-loader. |
| Unrelated setup rows appear in the candidate | Classify input validation, enumerate the semantic keys, and remove them before a new preview. |
| User requests an out-of-baseline branch without complete same-release evidence | Classify approval blocker, record the exact branch and missing evidence, and stop without inventing values. |
| User requests Review and Submit, period opening, disablement, deletion, or another lifecycle operation | Refuse it in this create resource and identify the separately routed workflow needed; do not broaden authorization. |
| Import process times out | Stop polling and report environment, task, package checksum, ProcessId or requestId, last status, elapsed wait, and exact next-check path. |
| Import process fails | Retrieve and persist the available ProcessLog and status payload, classify process failed, preserve partial successes with an errors array, and do not retry automatically. |
| Physical ALC exists but relationship import failed | Re-export the same scope before preparing any retry: physical creation may already be committed. Verify the existing target identity, ALC category, currency, and generated short name; preserve that physical target and prepare a reviewed relationship/rule repair. Do not rerun a blank-ID create, fabricate identifiers, or create a duplicate. |
| Existing RC options change after importing source context | Report exact existing-row deltas and inspect source-option propagation. Oracle can propagate source options to existing Journal/Subledger RCs even when their rows were excluded. Do not conceal the delta or automatically undo it; unresolved impact keeps verification unverified. |
| Import reports success but same-scope re-export is absent or differs | Return unverified, preserve the exact semantic diff, and do not declare the configuration complete. |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Missing, malformed, mutually inconsistent, level-incompatible, partial, overlength, or unsafe input or graph | Correct intake or local artifact and restart at validation |
| Catalog mismatch | Exact reference result, package schema, source identity, or same-release role evidence is absent, ambiguous, or contradictory | Obtain precise input or fresh authoritative evidence; do not guess |
| Auth | Authentication for a permitted read is missing or expired | Refresh once only when permitted; otherwise stop and request a valid routed session |
| Authz | Identity lacks privilege for the selected read, export, import, log, or process | Stop and request the minimum required privilege through the project workflow |
| Transport or environment | DNS, TLS, timeout, throttling, unavailable host, or wrong-environment behavior prevents a reliable result | Retry only documented recoverable reads; otherwise stop with environment diagnostics |
| Fusion API | Fusion returns a valid error response or incompatible server contract | Preserve sanitized response and request remediation; never reinterpret it as no match |
| Process timeout | Bounded polling ends before a terminal state | Record external ID, last state, elapsed time, and next-check path; do not resubmit |
| Process failed | Import or downstream job reaches a failed terminal state | Persist status and ProcessLog, retain errors and partial results, and require reviewed remediation |
| Artifact persistence | Package, CSV, XML, checksum, preview, audit record, or project artifact cannot be safely created or verified | Preserve diagnostics, prevent import, and repair the artifact path or shape |
| Approval blocker | Required user intent, same-release evidence, immutable preview, or core.data-loader approval is absent | Stop before mutation and request the exact missing decision or approval |
| Unverified | Import outcome exists but same-scope re-export does not prove the expected graph | Re-export and compare; do not report completion |
| Verified | Same-scope re-export proves the approved graph and no unrelated delta | Return final evidence and generated identifiers |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Validation stop | Exact field or group, supplied value, applicable level, violated predicate, resolver when used, and user action required. |
| Lookup stop | Environment, resolver, sanitized request filters, requested business fields, response category, match count, candidates needed for disambiguation, and whether the value was user-supplied or source-derived. |
| Dependency stop | Dependency ID, status, why it blocks, source evidence, and minimum remediation. |
| Design stop | Rule, severity, exact semantic rows or fields, expected state, and whether a local correction is allowed. |
| Package preview | Target environment and scope, immutable ZIP checksum, source and metadata checksums, member list and order, exact row-count diff, field transformations, intended blanks, advisories, and excluded lifecycle actions. |
| Data-loader approval | Exact environment, task code and name, source ledger scope, immutable artifact checksum, operation, row impact, and the data-loader approval record; do not ask for a second task approval. |
| Process timeout | Environment, operation, task code, package checksum, ProcessId or requestId, last status, elapsed wait, and next-check or retry path. |
| Process failure | Environment, external ID, terminal state, Fusion error category, sanitized ProcessLog or status artifact, partial successes, errors array, and remediation. |
| Verification | Same-scope export identity and checksum, expected versus actual relationship, physical and rule rows, separately returned generated identifiers, unexpected deltas, and final Verified or Unverified state. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| No current primary-ledger-scoped Manage Reporting Currencies export | Do not hand-build CSV headers, metadata XML, source roots, or a candidate ZIP from documentation or historical packages. |
| Scoped-export request is process-first | Do not submit it. The criteria array must be serialized before the process array using the exact root-key order TaskCode, SetupTaskCSVExportCriteria, SetupTaskCSVExportProcess. |
| Source is absent or ambiguous | Do not select a ledger by partial name, position, recency, or convenience. |
| A UI LOV value is unvalidated | Do not accept free text as authoritative, choose the first match, or hide ambiguity. |
| Journal or Subledger First Opened Period input is absent | Do not block for missing user input, prompt for a redundant period, sort the LOV, choose the first response row, or invent period-status evidence; derive and validate from the exact scoped source row. |
| accountingPeriodsLOV returns a row | Do not claim it proves first-opened eligibility by itself. Require PeriodNameId equality to the scoped source FirstLedgerPeriodName and the exported period tuple, a non-adjustment row, complete pagination, and authoritative same-release evidence for any different optional override. |
| Balance is selected | Do not create a physical ALC target row. |
| Journal or Subledger is selected | Do not omit either physical alias row or author differing target rows. |
| Generated identifiers are unknown | Do not fabricate, copy from history, equate, or interchange physical ShortName and relationship TargetLedgerShortName. |
| FIND_RATE is selected | Do not default AlcMaxDaysRollRate, including to the proven sample value 5. |
| REPORT_ERROR is selected | Do not retain a max-day value. |
| Initialization is requested | Do not author a partial group, reuse the FirstOpenedPeriod predicate, or invent EMU behavior. |
| Default rule is displayed in UI | Do not author Closing Journal and Other and N or an empty added row unless a current same-release export proves the exact requested row. |
| BalSegValueOptionCode is A | Do not add a GL_LEDGER_SEG_VAL_ASSIGNMENT.csv row. |
| Broad source export contains other setup | Do not carry unrelated primary, secondary, reporting-currency, relationship, or rule rows into the create package. |
| Out-of-baseline behavior is requested | Do not invent defaults for EMU fixed-rate initialization, custom sequencing, partial account filters, or selective rule designs. |
| Experiment chronology contains operational constraints | Do not present those mechanics as Oracle functional product rules. |
| Import approval is absent | Do not invoke a live mutation; this resource only hands the immutable artifact to core.data-loader. |
| Live POST or import is uncertain or failed | Do not retry without documented idempotency and explicit approval for that retry. |
| Process status is successful | Do not declare verification without the same-task, same-primary-ledger-scope re-export. |
| Lifecycle operation is requested | Do not Review and Submit Accounting Configuration, open periods, disable conversion, delete setup, or perform any other lifecycle action in this resource. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRC-060-EXECUTION-GATE | decision | 60 | execution_gate | ready->MRC-080-RETURN-READY;blocked->MRC-070-HANDLE-ERROR;failed->MRC-070-HANDLE-ERROR | MRC-050-ENFORCE-DESIGN | stop | Always |
| MRC-070-HANDLE-ERROR | step | 70 | error_handler | stopped->MRC-090-RETURN-ISSUES | none | stop | A prior node returns an invalid, unresolved, blocked, or failed outcome |
| MRC-080-RETURN-READY | terminal | 80 | terminal | none | MRC-060-EXECUTION-GATE | stop | Candidate is immutable, validated, and ready for core.data-loader preview and approval; or same-scope re-export proves the approved import |
| MRC-090-RETURN-ISSUES | terminal | 90 | terminal | none | MRC-070-HANDLE-ERROR | stop | Error handling has produced an actionable stop record |
