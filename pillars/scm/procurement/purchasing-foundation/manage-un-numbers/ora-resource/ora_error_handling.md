# UN Number Error Handling and Handoff

These are FSCR policies from [error handling governance](../../../../../../governance/error-handling-guidelines.md),
[Data Loader](../../../../../../core/data-loader/SKILL.md), and the approved
create/update plan and explicit-delete extension. Resource nodes validate input and conditionally perform read-only Hazard Class resolution; all writes remain with Data Loader.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Missing, invalid, or unsupported business input | Record all affected row/field checks and stop before Data Loader handoff; UNNumberId validity is deferred; non-null HazardClassId requires the declared verification |
| Explicit create Description missing or invalid | Report Description with MISSING for omission or FAILED for invalid supplied values; collect other field issues and stop before Hazard Class lookup. Request a valid supplied description without defaulting it |
| Invalid resource contract or unresolved required local rule | Report the source file and Rule ID; resolve the authoring gap and recompile |
| Data Loader registration, metadata, source, privilege, ID, or operation checks fail later | Let core.data-loader report its prescribed blocker; local readiness does not override it |
| Write outcome is failed or uncertain | Stop and reconcile through the selected Data Loader workflow; never automatically replay upload or import |

## Lookup and Capture Failures

| Situation | What Should Happen |
|---|---|
| No match or ID/name disagreement | Block the row and request corrected selectors; never create a class or substitute an ID |
| Multiple matches | Block as ambiguous; require an exact ID or corrected exact name |
| Authentication, transport, malformed/incomplete pages | Report failed/unvalidated lookup, never absence; core read recovery applies |
| Hazard Class lookup reaches its 100-page limit with hasMore=true | Stop before page 101 and return failed/incomplete lookup evidence with failure class process_timeout. Disclose task, selected environment, resolver, pages read, last offset/hasMore, elapsed time and safe next action. Do not enrich, accept a partial match, or proceed to handoff; ask for a narrower exact selector or a separately reviewed lookup plan before a fresh invocation. Never automatically restart the traversal. |
| A name/ID correction is needed after source preparation | Return blocking issues, cancel pending load validation and prepare/validate corrected input anew; changes entries cannot modify captured records |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input validation | Create/update name/code absent or invalid, explicit-create Description absent or invalid, supplied optional Description invalid, date invalid, missing or empty delete ID, conflicting operations, malformed HazardClassId/name, conflicting association inputs, or unsupported business fields | Correct the input and rerun local preparation |
| catalog mismatch | Task identity or business object differs from the manifest or selected loader metadata | Resolve the mapping before loading |
| auth/authz | Data Loader lacks valid authentication or privilege | Follow its core authentication recovery policy |
| transport/environment | Data Loader reports network failure, unavailable host, or wrong environment | Resolve connectivity or environment identity before another attempt |
| Fusion API | Data Loader reports a server rejection, including invalid identity or operation-specific requirements | Preserve sanitized diagnosis and correct the cause |
| process timeout | Data Loader reaches its wait limit | Report operation, last status, elapsed wait, permitted external IDs, and next-check path |
| process failed | Data Loader or a selected job reports failure | Preserve partial successes and errors; obtain process log through the selected workflow |
| artifact persistence | Required audit or result cannot be saved | Stop before additional side effects and repair the destination |
| approval blocker | Data Loader has no valid approval bound to the reviewed source | Use its own approval workflow once |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| UN.HANDOFF | Task code and name, completed local path, defaults applied (none), and readiness for Data Loader review only; identity and operation handling are delegated |
| Offline field check | FIELD_VALID or field issues; after the full local graph succeeds return READY_FOR_DATALOADER_REVIEW, with applicable Hazard Class verification complete and Data Loader preflights still pending; UN Number record existence remains unverified |
| Error terminal | Task code and name, failure class, blocked Rule ID, sanitized issue list, verified side effects, and safe next action |
| Durable diagnostics | Use the active project's prescribed records; redact credentials and sensitive payloads and do not persist IDs, opaque URLs, or ETags in task-node records |

## Data Loader Handoff

| Situation | What Happens |
|---|---|
| Preparation/validation checks pass | Pass the supplied business fields and their presence semantics to core.data-loader for purchasingUNNumbers; verify non-null HazardClassId for create/update; delete requires explicit DELETE and a supplied non-null, nonblank UNNumberId |
| Create/update IDs | UNNumberId retains unchecked pass-through. Verify non-null HazardClassId and preserve its supplied representation; fill an omitted HazardClassId from exact name resolution only in a separate prepared record. Preserve null only without a name. Data Loader retains final server validation |
| Create/update UNNumber and UNNumberCode | Hand off both required values as business data; do not reinterpret code as lookup-only context or remove it from the supplied data |
| Intent handoff | Retain scoped user/task intent and its source outside business fields through captured-source validation. Apply the input resource requiredness rules again without mutating captured records; corrections require fresh preparation and approval |
| Operation selection | Preserve an explicitly prepared RestAction=DELETE for deletion. Preserve any explicit prepared POST/PATCH marker and scoped intent; otherwise delegate operation selection to Data Loader. Explicit create adds Description requiredness under input validation, but generic apply/upsert transport alone does not. Do not infer, inject, or rewrite RestAction in this graph. The task does not establish automatic selection or ID acceptance as verified loader behavior; its own contract and blockers remain authoritative |
| Omitted or nullable fields | For create/update rows, treat an empty CSV/XLSX InactiveDate cell as unprovided and omit the date attribute from that outgoing record. Preserve omission and explicit null distinctly through handoff. Data Loader owns serialization and server behavior; do not guess null markers or silently replace omission with null |
| Approval boundary | Data Loader owns final source validation, captured-source preview, approval binding, submission, and verification. Changes require fresh preparation and approval under that workflow |
| Delete rows | Hand off UNNumberId unchanged with the explicit DELETE control. Data Loader owns delete support, ID validation, metadata, approval, and submission. No direct REST call or fallback route is permitted when loader metadata rejects deletion. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Local handoff reached | Do not imply UNNumberId validity, UN Number record existence, server eligibility, or import completion; verified Hazard Class identity is a scoped read result only |
| Validation reads | Only the declared Hazard Class GET through the selected authenticated core client is allowed when applicable; no reads for valid deletes or absent/null associations |
| Live mutation or uncertain prior write | Do not submit or retry from these nodes; use the authorized Data Loader workflow |
| Missing downstream contract | Do not invent ID resolution, operation selection, serialization, approval, or an alternative execution route |

## Prepared Artifact Gate

Evaluate the exact prepared ZIP through the existing
[core Data Loader workflow](../../../../../../core/data-loader/SKILL.md), using the
[captured-source contract](ora_input_validation.md#captured-source-validation).
The final artifact hash must be the one supplied to Task Hook.
Do not alter its bytes, headers, field presence, record directives or values
through ruleResults. Discard superseded preview/approval envelopes and prepare
a new artifact for corrections. Compare the artifact with the approved preparation,
retaining original row references and scoped operation intent separately for every
affected row, including mixed-operation input. Native DAT deletion inputs require
the same exact DELETE directive/control agreement and ID-only business-field
contract as converted inputs. Never infer the directive from the control alone.

| Situation | Blocking Condition | Recovery |
|---|---|---|
| CSV deletion | The final record has a MERGE directive even when its RestAction is DELETE | Block handoff. Use core Data Loader's delete XLSX preparation and validate a fresh artifact whose DELETE directive and control agree; never patch the CSV-derived DAT or submit it as a delete |
| Delete artifact | Record directive or explicit DELETE control is missing or conflicts with scoped user intent or the ID-only contract | Correct the approved source preparation and repeat core validation before preview |
| Artifact decoding | DAT values, escaping, operation controls or original row/intent association cannot be evaluated losslessly | Stop; obtain a supported prepared source/artifact through core rather than inventing a parser or execution route |

## Source Representation Gate

Apply the [captured-source contract](ora_input_validation.md#captured-source-validation)
and the [prepared artifact gate](#prepared-artifact-gate).
Empty-date omission and any other permitted preparation happen before core
conversion. In the final immutable artifact, a present empty cell is still an
empty string; it cannot stand for an omitted attribute. Reprepare compatible
column groups before handoff. Explicit null without a verified loader encoding,
unsupported field-presence representation, or changed artifact content blocks
handoff. Do not invent null markers, change prepared rows, or claim that local
field validity establishes a supported wire representation.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| UN.HANDOFF | decision | 40 | execution_gate | ready->UN.READY;blocked->UN.HANDLE_ISSUES | UN.CHECK_DESIGN | stop | Local design checks and the Prepared Artifact Gate and Source Representation Gate passed; preserve submitted business data for Data Loader review after applicable Hazard Class verification, preserving explicit DELETE or existing create/update controls; this gate authorizes no write |
| UN.READY | terminal | 50 | terminal | none | UN.HANDOFF | stop | Return READY_FOR_DATALOADER_REVIEW; report whether the read-only Hazard Class lookup was performed or skipped. No Fusion writes were performed; loader checks and execution remain downstream |
| UN.HANDLE_ISSUES | step | 90 | error_handler | reported->UN.RETURN_ISSUES | none | stop | Any reached input, defaulting, design, or handoff failure; disclose and classify locally |
| UN.RETURN_ISSUES | terminal | 100 | terminal | none | UN.HANDLE_ISSUES | stop | Return MISSING for missing facts, UNSUPPORTED for unsupported scope, otherwise FAILED; preserve a safe resume stage |
