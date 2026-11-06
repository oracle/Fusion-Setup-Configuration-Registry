# Error Handling

## Failure Handling

| Failure | Message direction | Next action |
|---|---|---|
| Invalid input | Identify the field or combination that failed and state the accepted format. | Follow ora_input_validation.md and ask only for the corrected value. |
| Dependency blocked | Identify the missing prerequisite evidence. | Follow ora_dependency_readiness.md; resume only after fresh target verification passes. |
| Unapproved target difference | Show the material difference not covered by the request. | Ask for update, preserve, or replacement only when that choice remains unresolved. |
| Read-only lookup fails | Report the read-only purpose, failure class, and sanitized message. | Refresh and retry once only for a documented authentication failure; otherwise stop. |
| Package design blocked | Identify the conflicting package action or immutable-design safeguard. | Follow ora_design_enforcement.md; obtain the required customer decision before rebuilding the preview. |
| Fusion returns FND-3042 | Report the actual validation message and each affected instance. | Stop without retry; obtain approved nonblank structure-instance identifiers, rebuild the immutable archive, and require a new submission approval. |
| Fusion returns FND-2742 | Report the actual error and affected Category structure; identify the required label by its resolved display Name. | Stop without retry; resolve the label and obtain an explicit segment assignment, then rebuild and obtain approval for the changed archive. Never guess the label Name. |
| Fusion returns FND-2743 or FND_KF_STR_NO_UNIQUE_LABEL | Report the actual validation message, selected KFF, StructureCode, duplicated label display Name or code, and every SegmentCode receiving that label. | Stop without retry; use resolve_segment_label to verify whether the label is unique, then keep the unique label on only one approved segment or obtain distinct approved labels. Rebuild the smallest corrective archive and require a new submission approval. |
| Approval missing or stale | State that the proposed submission is blocked. Preserve and report any earlier submitted process and partial results; regenerate and review only when the package or scope changes. | Present the exact immutable package and follow the parent Fixed Assets approval gate. |
| Import pending, timeout, or failure | Report target, process or request identifier when available, last status, elapsed time, and safe next-check path. | Preserve available status/log evidence. Do not replay an import without explicit approval. |
| Post-import mismatch | State the approved scope and the missing or mismatched target state. | Preserve process-log and fresh export evidence. Do not claim success or automatically resubmit; require explicit recovery approval. |
| Data Loader and target statuses disagree | State both terminal statuses and classify the result as unresolved. | Stop before resubmission and preserve both diagnostics. |

## Enabled Structure Replacement Recommendation

When the customer requests a new enabled CAT#, KEY#, or LOC# structure and current
target evidence already shows an enabled structure for that KFF pair,
render the following `Reference Validation Preview` before package generation.
Show unresolved usage or migration risks before requesting replacement approval.
If these cannot be resolved, stop with the blocker instead of recommending a blind disable.
Substitute every bracketed field from the request and current target export;
use `Not requested` for an absent requested structure instance.
If several enabled structures are present, list every one and require an
explicit replacement design that leaves only the approved structure enabled.

## Request Review: Create Fixed Assets [Category, Asset Key, or Location] KFF Structure

I reviewed your request to create a new enabled Fixed Assets [Category, Asset Key, or Location] key flexfield structure.

### Requested Configuration

| Area | Value |
| --- | --- |
| Fixed Assets Flexfield | [Category, Asset Key, or Location] |
| New Structure Code | [requested StructureCode] |
| New Structure Name | [requested structure Name] |
| Enabled | [Yes or No] |
| Matching Structure Instance | [requested Structure Instance Name, or Not requested] |
| Segment Count | [requested segment count] |

### Validation Result

This request cannot proceed as-is.

The current export already has one enabled `[Category, Asset Key, or Location]` structure:

| Existing Enabled Structure | Name | Delimiter | Enabled |
| --- | --- | --- | --- |
| [existing StructureCode] | [existing Name] | [existing Delimiter] | Y |

Fixed Assets allows only one enabled structure for a given key flexfield at a time. Creating `[requested StructureCode]` as another enabled structure would result in two enabled structures, so package generation and import are blocked.

### Recommendation

If the replacement-impact assessment confirms a supported transition, propose:

1. Disable the existing enabled structure: `[existing StructureCode]`.
2. Create the new structure: `[requested StructureCode]`.
3. Keep only `[requested StructureCode]` enabled after the change.

### Approval Required

After the impact assessment passes, please confirm this replacement design:

> Disable `[existing StructureCode]` and create `[requested StructureCode]` as the only enabled structure.

No replacement package will be generated or imported until its impact assessment passes and the replacement is explicitly approved.

The replacement decision does not bypass remaining validation, readiness or
design checks. Package creation follows the parent Fixed Assets Design Preview
gate; submission still requires approval of the final reviewed artifact through
`core.data-loader`. Do not repeat an approval already obtained for the same
unchanged scope and gate.

When the replacement is blocked because a System Controls row exists, show only
this customer-facing result and stop:

> System Controls are set and cannot be changed.

Do not show a replacement recommendation, migration options, structure codes,
or technical lookup evidence.

## Disclosure and Refusal Rules

| Gate | Required behavior |
|---|---|
| Derived names | In the parent Design Preview, show source-to-name/code mappings once for non-internal fields. Report internal checks as passed or unresolved without exposing Internal=Yes values. |
| Label messages | Show Major Category label or Minor Category label for the documented seeded mapping without requiring exported metadata or a waiver. For custom, unknown, or conflicting labels, report unresolved identity/properties. Keep technical codes in import evidence only. |
| Import readiness | Follow the parent preview and approval contract; show task-specific unresolved gaps without creating another approval gate. |
| Post-import verification | Show package fingerprint, available process/request identifier, fresh export comparison, and recovery-approval state. |
| Missing or ambiguous evidence | Do not infer a structure, value set, default, or lookup result. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| KFF.IMPORT_GATE | decision | 60 | execution_gate | approved->KFF.HANDED_OFF_TO_PARENT;approval_missing->KFF.HANDLE_APPROVAL | KFF.ENFORCE_DESIGN | stop | A validated package is proposed for live import. |
| KFF.HANDLE_INPUT | step | 70 | error_handler | handled->KFF.ISSUES | KFF.VALIDATE_INPUT | stop | Input is invalid. |
| KFF.HANDLE_DEPENDENCY | step | 80 | error_handler | handled->KFF.ISSUES | KFF.RESOLVE_DEPENDENCIES | stop | Dependency is blocked. |
| KFF.HANDLE_LOOKUP | step | 90 | error_handler | handled->KFF.ISSUES | KFF.LOOKUP_EXISTING | stop | Lookup fails, identity is ambiguous, or a material difference is unapproved. |
| KFF.HANDLE_DESIGN | step | 100 | error_handler | handled->KFF.ISSUES | KFF.ENFORCE_DESIGN | stop | Design rule blocks the package. |
| KFF.HANDLE_APPROVAL | step | 110 | error_handler | handled->KFF.ISSUES | KFF.IMPORT_GATE | stop | Approval is absent or stale. |
| KFF.HANDED_OFF_TO_PARENT | terminal | 120 | terminal | none | KFF.IMPORT_GATE | continue | Accepted — pending parent verification. The Fixed Assets parent owns status, process-log review, and fresh target read-back. |
| KFF.DONE_MATCH | terminal | 125 | terminal | none | KFF.LOOKUP_EXISTING | stop | Existing target state already matches the requested material scope; no package or import is needed. |
| KFF.ISSUES | terminal | 130 | terminal | none | none | stop | A blocker is handled and disclosed with the safe next action. |
