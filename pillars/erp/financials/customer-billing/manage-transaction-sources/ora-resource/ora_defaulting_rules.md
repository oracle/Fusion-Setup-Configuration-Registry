# Manage Transaction Sources Defaulting Rules


## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Status | A | Creating a source and Status is omitted | No; preserve an explicit valid A or I value | |
| BatchSourceType | INV | Creating a source and Type is omitted | No; preserve an explicit valid INV or FOREIGN value | |
| AutoTrxNumberingFlag | Y | Creating a source and the flag is omitted | No; preserve an explicit Y or N value | |
| InvalidLinesRule | Reject | Creating a source and InvalidLinesRule is omitted | No; preserve an explicit Create or Reject value | |

## Default Safety Rules

| Situation | What Happens |
|---|---|
| LastBatchNum is absent while AutoTrxNumberingFlag is Y | Do not invent a number; block the record |
| LastBatchNum is below 1 on create with explicit or defaulted AutoTrxNumberingFlag Y | Block the record under the new-sequence constraint; never substitute 1 or a backend fallback |
| A default's condition does not apply | Leave the field absent rather than serializing the default |
| The user supplies a valid explicit value | Preserve it; defaults never overwrite explicit valid input |
| A deployment-specific flexfield value is absent | Leave it absent; never default DFF or GDF context or segments |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTS.APPLY_DEFAULTS | step | 4 | apply_default | applied->MTS.ENFORCE_DESIGN;unchanged->MTS.ENFORCE_DESIGN;blocked->MTS.RETURN_ISSUES | MTS.LOOKUP_REFERENCES | stop | After required references are resolved or preflight is not applicable |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-UI-MTS; SRC-CS-CREATE-VO | Create-page defaults and conditional requiredness |
| SRC-DOC-NUMBERING-26C | Automatic numbering and last-number semantics |
| SRC-DOC-BO-26C; SRC-FSM-CURRENT | Canonical package codes and functional field meanings |
| SRC-CS-EO-NUMBERING-2610 | See the release-source anchor in `ora_input_validation.md`: new automatic-numbering sequences start directly at the supplied LastBatchNum and have MINVALUE 1; the backend null fallback is not an authorized customer default |
