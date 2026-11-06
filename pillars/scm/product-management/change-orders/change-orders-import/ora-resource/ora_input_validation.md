# Input Validation

Validate customer Change Order data or a prebuilt Change Order Import FBDI ZIP against the
current public Oracle Change Order Import template before immutable handoff to
`core.data-loader`.

| Requirement | Validation gate | Failure action |
|---|---|---|
| Source or ZIP | Readable customer source or a readable ZIP is present | Stop before mapping. |
| Current template | Current public `ChangeOrderImportTemplate.xlsm`, URLs, retrieval time, digest, and sheet sequence are recorded | Stop; never use a remembered layout. |
| Mapping | Every required source fact maps to the current template or has an explicit documented default | Stop for missing or ambiguous values. |
| CSV and ZIP shape | Headerless CSVs, exact filenames, ordered root-level members, safe paths, and exact field counts | Stop; preserve supplied ZIPs and follow the recovery guidance in [Error Handling](ora_error_handling.md). |
| Data validity | Current-template types, constraints, references, and a single numeric Batch ID pass | Stop and correct the source. |
| Header-child links | Each supplied Change Order line, Change Order attachment, or history row resolves to one header by Change Notice and Organization Code; its Batch ID, where present, matches that header | Stop and correct the source. |
| Immutable evidence | ZIP digest, member manifest, row counts, template provenance, and mapping preview are present | Fail local validation and report missing or inconsistent preparation evidence. |
| Data Loader route | Handoff identifies task FBDI business object `Change Order` | Stop and correct the task configuration. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CHANGE_ORDER_FBDI.VALIDATE_FBDI | step | 1 | validate_input | valid->CHANGE_ORDER_FBDI.CONFIRM_LOADER_ROUTE;invalid->CHANGE_ORDER_FBDI.FAILED | none | stop | Whenever the supplied immutable Change Order Import archive and its recorded template, mapping, and validation evidence are evaluated. |
