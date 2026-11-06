# Defaulting Rules

Only the allowlisted missing/null/empty catalog permits offering the existing
nine OOTB objects for initial Full Publish; never switch modes or submit
automatically. Its REST body omits `publishType` and workbook cell is blank.
See [ora_initial_full_publish.md](ora_initial_full_publish.md). Normal Partial
Publish keeps the fixed pair and `selective`; approvals do not carry forward.

| Field | Default | Rule |
|---|---|---|
| `fusion_abo_process_variable_name` | `oraclecpqo` | Use only after the requester explicitly selects the default; disclose it and verify it is a Standard Process. |
| ABO delta-action Library Function | `_s_getAttributesForABODeltaActionCalculation` | Fixed task value; never accept a caller override. |
| CPQ preparation permission | Not approved | Show the full ABO proposal first. Preserve explicit/default process selection on fresh reads. Approval permits preparation only; Core requires its own later load approval. |
| Adaptive Search entities | `ConsolidatedAsset`, `SerializedAsset` | Fixed ordered request supplied to Configure Adaptive Search after verified CPQ success. |
| Publish monitoring | No repeated checks until chosen | After verified load success, ask keep checking every 15 seconds or check later. Ordinary status requests check once. |

The fixed Adaptive Search entity selection is declared in the parent Fusion ABO
plan as downstream scope. It is not approval to publish. Configure Adaptive
Search validates its workbook in a Core persisted preflight after verified CPQ success,
then requires separate contextual approval of Core's current preview.

Data Loader status inspection is permitted only on an explicit user request,
for the exact submitted CPQ or companion request. Pending returns a next-check
prompt and stops; final Adaptive Search readiness still gates separate ESS approval.
