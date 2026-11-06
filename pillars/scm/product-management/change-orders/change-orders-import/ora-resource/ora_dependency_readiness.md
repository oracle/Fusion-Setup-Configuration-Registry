# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Customer Change Order source | Confirm a supplied source or prebuilt FBDI ZIP is readable. |
| 2 | Current public Oracle template | Fetch `ChangeOrderImportTemplate.xlsm` and bind its source, digest, sheet sequence, filenames, and export columns to the run. |
| 3 | Normalized Change Order mapping | Resolve required or ambiguous business values and disclose unsupported facts. |
| 4 | Generated Change Order Import ZIP | Validate members, relative order, rows, Batch ID, and digest against the current workbook. |
| 5 | Core Data Loader handoff | Provide the unchanged ZIP and read-only validation evidence to `core.data-loader` with task business object `Change Order`. |

## Dependency Rules

| Dependency ID | Mandatory | Applies When | Failure action |
|---|---|---|---|
| customer_change_order_source | Yes | Always | Stop until readable source evidence is supplied. |
| change_order_import_template_mapping | Yes | Always | Stop until the current public workbook is fetched and recorded. |
| normalized_change_order_mapping | Yes | For non-ZIP input | Stop until mappings are complete and unambiguous. |
| generated_change_order_import_zip | Yes | Prepared archive validation | Stop if the supplied ZIP or its recorded template-driven validation evidence is incomplete or inconsistent. |
| core_data_loader_handoff | Yes | Prepared archive metadata validation | Stop if the supplied metadata does not identify core.data-loader and business object Change Order. |

## Validation Scope

Evaluate the supplied immutable archive and its recorded preparation evidence.
These checks inspect existing archive metadata, template provenance, mappings,
and validation results. A ready result reports local evidence completeness;
external authorization and execution remain owned by `core.data-loader`.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CHANGE_ORDER_FBDI.CONFIRM_LOADER_ROUTE | step | 2 | resolve_dependency | ready->CHANGE_ORDER_FBDI.HANDOFF_GATE;blocked->CHANGE_ORDER_FBDI.FAILED | CHANGE_ORDER_FBDI.VALIDATE_FBDI | stop | Whenever the supplied immutable Change Order Import archive and its recorded preparation metadata are evaluated. |
