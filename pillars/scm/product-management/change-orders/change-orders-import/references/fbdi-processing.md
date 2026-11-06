# Change Order Import FBDI Processing

## Purpose

Define the template-driven mapping, packaging, and validation contract for
Change Order Import. This skill prepares one immutable archive and hands it unchanged to
`core.data-loader`; it never executes a Fusion transport or import.

## Current Public Template Authority

For every run, fetch `ChangeOrderImportTemplate.xlsm` from the current public
Oracle Change Order Import page. Record the page URL, workbook URL, retrieval
time, SHA-256 digest, and sheet sequence. The workbook and its linked control
files are the sole schema authority for that run.

Read each populated sheet's ordered export columns, technical names, types,
required markers, validations, and allowed values. Preserve its complete column
order, trailing empty fields, encoding, delimiter, quoting, and null
conventions. For `EGO_CHANGES_INT`, exclude the workbook-only `Name` metadata
column; the first headerless CSV field is `TRANSACTION_TYPE`.

Stop on template drift: a changed sheet sequence, output filename, or export
contract requires updating this task skill before creating a package.

## Package Contract

Create headerless root-level CSV members only for populated sheets. Use the
current template's prescribed filenames and preserve this relative order:

1. `EgoChangesInterface.csv`
2. `EgoChangeLinesInterface.csv`
3. `EgoChangeAttachmentsInterface.csv`
4. `EgoChangeHistoryInterface.csv`
5. `EgoChangeEffInterface.csv`
6. `EgpSystemItemsInterface.csv`
7. `EgpItemRevisionsInterface.csv`
8. `EgoItemIntfEffb.csv`
9. `EgoItemIntfEfftl.csv`
10. `EgpItemAttachmentsIntf.csv`
11. `EgpItemRelationshipsIntf.csv`
12. `EgpStructuresInterface.csv`
13. `EgpComponentsInterface.csv`
14. `EgpSubCompsInterface.csv`
15. `EgpRefDesgsInterface.csv`
16. `CoAcaRelationshipsInterface.csv`

Use one numeric Batch ID consistently where the template provides that field;
in `EgoChangesInterface.csv` it is the second CSV field. `EGO_CHANGE_LINES_INT`
has no `BATCH_ID`; link lines to headers by `CHANGE_NOTICE` and
`ORGANIZATION_CODE` without adding a Batch ID column.

## Validation and Immutable Handoff

Reopen the completed ZIP and fail closed unless it has safe root-level members,
no duplicates or unexpected files, exact template-prescribed names and order,
headerless CSV rows with exact field counts, valid values, coherent
cross-file references, consistent Batch IDs where present, and a
SHA-256-bound preview.

Hand that exact archive, without copying or changing it, to `core.data-loader`
with task context and task FBDI business object `Change Order`.
Supply template provenance, ZIP digest, member manifest, row counts, mapping
preview, and Batch ID as read-only evidence.

Do not upload the ZIP, call an ESS job, initiate or monitor an import, query a
Fusion execution endpoint, construct execution parameters, or perform UCM
basename checks. `core.data-loader` owns all later authorization, transport,
submission, and monitoring decisions.
