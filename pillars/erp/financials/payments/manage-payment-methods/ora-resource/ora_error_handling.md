# Manage Payment Methods error handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Input/header/type or unresolved field | Stop before preview; identify entity, field, evidence boundary and correction |
| Lookup no match, several matches or unavailable | Preserve distinct outcome; do not treat unavailable service as a missing value |
| Fusion reports a missing alternate key for Disbursement Payment Method Usage | Preserve the original attempt and ProcessLog; classify the failed process without inferring a missing deployed key from this message alone. Inspect raw CSV header bytes and the generated parent/Usage XML through the declared diagnostic route. A leading UTF-8 BOM can prevent the parent key header from matching even when deployed alternate keys are correct. Keep requested applicability rows intact; do not invent a key or retry without a reviewed correction and fresh governed approval. |
| Null XML-node error follows a missing-key warning | Retain both diagnostics; identify the missing node and import path. Check whether the parent PaymentMethodCode node is present before attributing the failure to ADF alternate-key lookup or nullable Usage values. Source declarations alone do not establish deployed metadata or the generated XML. |
| Current export differs only by DueDayOfMonth/DueMonthsForward | Select the exact qualified87-column contract or historical89-column contract. Preserve source metadata and header order. Mixed/unknown shapes and requests for fields absent from the selected export stop before build. Do not synthesize columns or declare the attributes unsupported; historical field support remains available with compatible evidence. |
| Generated import CSV encoding | Build UTF-8 without a leading BOM and verify raw bytes in every final CSV member before preview. Legacy BOM-containing input may be read, but a normalized text comparison does not qualify the final import bytes. Preserve metadata, exact headers and all approved values. |
| Template/current exports have different positive NodeSequence values | With the reviewed export-local policy, validate exact entity paths/types/headers and source-backed XML-file grouping; reject same-file/same-level sequence collisions. Keep baseline metadata byte-for-byte. Without this explicit policy, retain exact sequence checks. |
| Import/process failure | Preserve request/process ID, last status and ProcessLog when available; no automatic resubmission |
| Timeout or session expiry | Continue monitoring original request if possible; never submit again without idempotency or fresh approval |
| Successful process, uncertain persistence | Keep business completion open until fresh export/reconciliation verifies requested state |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| Input validation | Malformed package or invalid field | Correct and rebuild candidate |
| Catalog mismatch | Task or ObjectShortName mismatch | Stop and re-evaluate catalog/package |
| Authentication/authorization | Read or import access failure | Restore access through declared workflow |
| Transport/environment | Endpoint or pod unavailable | Retain attempt identity and check environment |
| Fusion API/process failed | Nonterminal or failed process | Capture status and log before a new preview |
| Approval blocker | Preview or approval absent | Stop before mutation |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Preview | Exact environment, task, immutable candidate, changes, unresolved fields and warning |
| Failure | Affected entity/field, attempt identity, status, log, safe correction and next gate |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing approval or changed candidate | No live import |
| Unknown process outcome | No automatic retry or duplicate submit |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PM.GATE | decision | 60 | execution_gate | ok->PM.DONE;blocked->PM.RETURN_ISSUES | PM.DESIGN | stop | Before Data Loader handoff |
| PM.DONE | terminal | 70 | terminal | none | PM.GATE | stop | Task-local preflight complete |
| PM.RETURN_ISSUES | terminal | 80 | terminal | none | none | stop | Any blocked outcome |

## Source-backed field repair diagnostics

| Diagnostic | Classification | Next action |
| --- | --- | --- |
| FSM_USAGE_REQUIRED | input validation | Retain requested enablement and include the matching explicit Usage rows; do not omit the business requirement. |
| FSM_IGNORED_USAGE_UPDATE | catalog mismatch | This matched Usage edit is discarded by the source hook. Present the exact field/type limitation and a supported separately qualified change plan; do not claim success from job status. |
| FSM_SCOPE_REPLACEMENT | input validation | Review the proposed BU/LE identity and preserved rows as a scope change. Do not silently insert an additional scope or delete the old one. |
| DERIVED_DATE_MISMATCH or contradictory dates | input validation | Correct canonical EndDate/display-date consistency and regenerate the preview. |
| Protected SeededFlag or LevelCode | input validation | Preserve product-owned/derived values; request the actual supported business operation. |

These diagnostics are local preflight findings. No automatic retry, direct write fallback, or new broad unresolved-evidence restriction follows. A target lookup access failure remains auth/authz or environment evidence, not an invalid code.
