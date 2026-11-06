# Reference Organization Items Import Error Handling

## Error Situations

| Situation | What Should Happen |
|---|---|
| Installed Core contract missing or inconsistent | Stop with catalog_or_metadata_mismatch before preparation/Fusion calls; report missing documented CLI capabilities. Do not import optional Core internals, copy modules between branches or substitute a transport. |
| Item-index unknown-index HTTP 404 | Return index_remediation_required to Product Management orchestration; no preparation, submission or automatic index remediation. |
| Other item-index failure | Stop with auth/authz, transport/environment or Fusion API failure; preserve sanitized status, endpoint and next action; no automatic GET replay. |
| Public template/control download times out or fails | Stop with transport_or_environment for timeout/DNS/connection failures, or the actual HTTP failure class; show public URL, elapsed time and sanitized error. Use an explicitly supplied compatible schema without forcing another download. Public reads have a maximum 60-second timeout and no automatic retry. |
| Retrieved or supplied template has incompatible release or export layout | Stop with catalog_or_metadata_mismatch only after validating the incompatibility; obtain compatible ref-org template/control files. |
| Missing mode, mismatched Batch IDs, malformed CSV ZIP or unintended scope | Stop with input_validation; identify sheet/field without customer rows; correct and start fresh Core validation. |
| Item/organization/structure business context absent or conflicting | Stop with input_validation; list missing business values and association/structure context without issuing an environment check. |
| Reference Organization Items route/adapter absent or ambiguous, or CSV Batch ID/source mode invalid | Stop with catalog_or_metadata_mismatch; use the Reference Organization Items object only after its live registration passes; do not substitute generic fallback, UI, REST or ESS. |
| Core returns no_registered_match | Explain that the live FBDI metadata has no filename registrations for the reference-org template members under the selected Reference Organization Items object; ask the Fusion/Data Loader owner to confirm the reference-org filename-prefix registrations and their supported adapter/operation settings. A local custom setup-task entry or Run Book does not register the adapter. Do not retry until registration or the authoritative filename contract changes. |
| Core returns partial_registered_match | Identify unmatched CSV member names; compare the current template export contract with registered filename prefixes. Correct the confirmed mismatch and start fresh Core validation; do not remove members or force another business object. |
| Lost session, invalid retained preflight, or changed source/target/mapping | Stop with approval_blocker; use fresh validation and approval in the selected Core contract. Do not reconstruct a missing session/envelope from project records or switch workflows after failure. |
| Upload/initiation failed, partial or uncertain | Preserve core's accepted IDs and partial-success report; no automatic retry/resubmission, including authentication or Run Book rejection. |
| Requested status pending, failed or unavailable | Return core status/diagnostics unchanged; pending is not success; use permitted core FBDI ESS logs and offer a later requested check without polling. |
| Requested verification lacks assignments or structures | Report unverified/failed business completion; reconcile accepted request before any newly approved retry. |
| Source ZIP destination is unsafe, unwritable, existing or symlinked | Stop with artifact_persistence or input_validation before publishing; never overwrite or place sources under repository/project paths. Preserve any existing file. |
| Permitted project record cannot be written | Stop with artifact_persistence; preserve the report in the response, without writing loader material to an alternate file. |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Validation failure | All known missing/invalid business inputs and files, with status and concrete next action; follow the SKILL.md intake checklist; no approval question when blocked. |
| Core preview | Core preview verbatim; full route/settings, counts, hashes and Task Hook evidence stay internal to the selected Core workflow. |
| Accepted initiation | Core initiation report verbatim; acceptance is not verified completion or permission to poll. |
| Requested status | Core status report and permitted log links; no independently generated validation/failure reports. |
| Redaction | Never disclose credentials, tokens, private keys, authorization URLs, raw rows, hashes, previews, approvals or encoded payloads. Keep session control state in memory; retained preflight control files use the installed Core contract in a private transient location. Only Core-required non-sensitive integrity and Task Hook evidence may enter its prescribed project record; no independent pillar approval snapshots. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Route or prerequisites fail | No direct-transport bypass, another task, guessed adapter or numeric mode codes; Reference Organization Items FBDI routing is explicitly selected for this task. |
| Validation and approval | Keep the separately prepared source ZIP only in the explicit controlled transient location; no repository/project payload copies or independent pillar control-file copies. Sessions have no saved preview/approval; preflight retention follows the installed Core contract. Validate only the Core-bound source, with no original-source reread after Core fixes the artifact. Source preparation never authorizes upload. |
| Accepted or uncertain write | No automatic polling, authentication replay of mutations, upload retry or replacement import. |
| Cleanup or bulk upgrade | No automatic Purge Interface Tables or Upgrade Product Management Data action. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| REF_ORG_ITEMS.HANDOFF_GATE | decision | 7 | execution_gate | ready->REF_ORG_ITEMS.READY_FOR_LOADER;blocked->REF_ORG_ITEMS.FAILED | REF_ORG_ITEMS.VALIDATE_SCOPE | stop | Require complete captured native-source, dependency, Core-returned BO routing and scope results; return to the selected Core workflow for final preview and approval. |
| REF_ORG_ITEMS.READY_FOR_LOADER | terminal | 8 | terminal | none | REF_ORG_ITEMS.HANDOFF_GATE | continue | Return passed task rules to core; this neither approves upload nor claims completed import. |
| REF_ORG_ITEMS.FAILED | terminal | 9 | terminal | none | none | continue | Return issues and safe next action without submission. |
| REF_ORG_ITEMS.INDEX_REMEDIATION_REQUIRED | terminal | 10 | terminal | none | REF_ORG_ITEMS.CHECK_ITEM_INDEX | stop | Unknown Item Index; return remediation handoff to Product Management orchestration without continuing this import. |
