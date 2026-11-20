# Hazard Class Error Handling and Handoff

These are FSCR policies from [error handling governance](../../../../../../governance/error-handling-guidelines.md),
[Data Loader](../../../../../../core/data-loader/SKILL.md), and the approved
operation-neutral plan. Resource nodes perform local validation only.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Missing, invalid, or unsupported business input | Record all affected row/field checks and stop before Data Loader handoff; supplied ID validity is deferred |
| Invalid resource contract or unresolved required local rule | Report the source file and Rule ID; resolve the authoring gap and recompile |
| Data Loader registration, metadata, source, privilege, ID, or operation checks fail later | Let core.data-loader report its prescribed blocker; local readiness does not override it |
| Write outcome is failed or uncertain | Stop and reconcile through the selected Data Loader workflow; never automatically replay upload or import |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input validation | Required name/code absent or invalid, optional description/date invalid, or unsupported business fields | Correct the input and rerun local preparation |
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
| HAZ.HANDOFF | Task code and name, completed local path, defaults applied (none), and readiness for Data Loader review only; identity and operation handling are delegated |
| Offline field check | FIELD_VALID or field issues; after the full local graph succeeds return READY_FOR_DATALOADER_REVIEW, with Data Loader preflights still pending and no record-existence check pending |
| Error terminal | Task code and name, failure class, blocked Rule ID, sanitized issue list, verified side effects, and safe next action |
| Durable diagnostics | Use the active project's prescribed records; redact credentials and sensitive payloads and do not persist IDs, opaque URLs, or ETags in task-node records |

## Data Loader Handoff

| Situation | What Happens |
|---|---|
| Local checks pass | Pass the supplied business fields and their presence semantics to core.data-loader for purchasingHazardClasses; no verified ID or create/update intent is required by the pillar |
| Optional HazardClassId | Pass through unchanged if supplied, even when its value would have failed the former ID rules; leave absent if omitted. Data Loader owns validity and identity handling |
| HazardClass and HazardClassCode | Hand off both required values as business data; do not reinterpret code as lookup-only context or remove it from the supplied data |
| Operation selection | Delegate POST/PATCH selection to Data Loader. Do not inject, force, or rewrite RestAction from this graph. Automatic selection is an approved working assumption, not verified loader behavior; its own contract and blockers remain authoritative |
| Omitted or nullable fields | Treat an empty CSV/XLSX InactiveDate cell as unprovided and omit the date attribute from that outgoing record. Preserve omission and explicit null distinctly through handoff. Data Loader owns serialization and server behavior; do not guess null markers or silently replace omission with null |
| Approval boundary | Data Loader owns final source validation, immutable archive preview, approval binding, submission, and verification. Changes require fresh preparation and approval under that workflow |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Local handoff reached | Do not imply ID validity, record existence, uniqueness, Fusion acceptance, or import completion |
| Validation | Do not issue REST calls, authenticate, refresh tokens, or require external identity evidence |
| Live mutation or uncertain prior write | Do not submit or retry from these nodes; use the authorized Data Loader workflow |
| Missing downstream contract | Do not invent ID resolution, operation selection, serialization, approval, or an alternative execution route |

## Source Representation Gate

Apply the task's [branch contract](../SKILL.md#branch-data-loader-contract).
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
| HAZ.HANDOFF | decision | 40 | execution_gate | ready->HAZ.READY;blocked->HAZ.HANDLE_ISSUES | HAZ.CHECK_DESIGN | stop | Local design checks and the Source Representation Gate passed; preserve submitted business data for Data Loader review without ID verification or operation selection; this gate authorizes no write |
| HAZ.READY | terminal | 50 | terminal | none | HAZ.HANDOFF | stop | Return READY_FOR_DATALOADER_REVIEW with verified side effects none; loader checks and execution remain downstream |
| HAZ.HANDLE_ISSUES | step | 90 | error_handler | reported->HAZ.RETURN_ISSUES | none | stop | Any reached input, defaulting, design, or handoff failure; disclose and classify locally |
| HAZ.RETURN_ISSUES | terminal | 100 | terminal | none | HAZ.HANDLE_ISSUES | stop | Return MISSING for missing facts, UNSUPPORTED for unsupported scope, otherwise FAILED; preserve a safe resume stage |
