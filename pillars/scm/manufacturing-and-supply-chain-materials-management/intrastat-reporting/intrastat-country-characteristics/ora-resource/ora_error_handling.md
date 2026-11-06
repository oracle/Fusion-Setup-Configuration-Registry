# Intrastat Country Characteristics Input Outcomes

## FSM Package Outcomes

| Situation | What Should Happen |
|---|---|
| FSM package uses a populated current-data export or lacks template-only provenance | Stop before Data Loader preview. Obtain or reuse a verified template-only export; do not remove baseline rows and reuse the archive. |
| Template identity, release, fingerprint, metadata marker, member inventory, header inventory, or empty-row check fails | Stop package preparation and obtain a replacement template-only export. |
| Package changes metadata, member hierarchy, encoding, an untouched header-only member, or an unrelated country row | Stop before Data Loader handoff. Rebuild the minimal delta from the verified empty template. |
| Package receipt or semantic diff is missing or inconsistent | Stop before Data Loader handoff and regenerate the immutable package evidence. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INTRASTAT_COUNTRY_CHARACTERISTICS.RETURN_SUCCESS | terminal | 10 | terminal | none | INTRASTAT_COUNTRY_CHARACTERISTICS.CLASSIFY_IMPORT_ROUTE | stop | REST route selection is valid; return the prepared source to the governed Data Loader workflow. |
| INTRASTAT_COUNTRY_CHARACTERISTICS.FSM_DATALOADER_HANDOFF | terminal | 30 | terminal | none | INTRASTAT_COUNTRY_CHARACTERISTICS.VALIDATE_FSM_PACKAGE | stop | FSM input and package validation passed. Return the immutable archive to core Data Loader for governed validation, preview, approval, and submission. |
| INTRASTAT_COUNTRY_CHARACTERISTICS.RETURN_ISSUES | terminal | 50 | terminal | none | none | stop | Input-contract validation returns blocked or failure; report CSV source-preparation issues and stop handoff. |
