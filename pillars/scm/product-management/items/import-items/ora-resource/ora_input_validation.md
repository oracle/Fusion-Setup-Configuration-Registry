# Input Validation

Validate customer item data or a prebuilt Item Import FBDI ZIP against the
current public Oracle Item Import template before immutable handoff to
`core.data-loader`.

| Requirement | Validation gate | Failure action |
|---|---|---|
| Source or ZIP | Readable customer source or a readable ZIP is present | Stop before mapping. |
| Current template | Current public `ItemImportTemplate.xlsm`, URLs, retrieval time, digest, and sheet sequence are recorded | Stop; never use a remembered layout. |
| Mapping | Every required source fact maps to the current template or has an explicit documented default or customer mapping decision | Stop for missing or ambiguous values. |
| Source System Code | Optional; use the supplied value when present, otherwise leave the template field empty | Do not prompt for or invent a missing value. |
| CSV and ZIP shape | Headerless CSVs, exact filenames, ordered root-level members, safe paths, and exact field counts | Stop and regenerate. |
| Data validity | Current-template types, constraints, references, and a single numeric Batch ID pass | Stop and correct the source. |
| Immutable evidence | ZIP digest, member manifest, row counts, template provenance, and mapping preview are present | Stop before handoff. |
| Data Loader handoff | Handoff evidence is complete and the unchanged ZIP is passed to core.data-loader preflight with `--business-object item` | Stop before handoff if evidence is incomplete; core.data-loader must reject a live route that does not rank `item` among the highest-scoring matches. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ITEM_IMPORT.VALIDATE_FBDI | step | 3 | validate_input | valid->ITEM_IMPORT.CONFIRM_LOADER_ROUTE;invalid->ITEM_IMPORT.FAILED | ITEM_IMPORT.INDEX_DEPENDENCY_READY | stop | Validate source, current template, package, and immutable evidence after the item-index dependency gate passes. |
