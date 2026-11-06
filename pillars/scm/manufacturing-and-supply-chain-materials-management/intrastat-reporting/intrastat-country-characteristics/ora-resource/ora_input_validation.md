# Intrastat Country Characteristics Native FSM Input Validation

## CSV Import Input Contract

This resource validates only task-specific FSM input. Shared setup-export and core Data Loader orchestration own template discovery, package preparation, source capture, validation, approval, and submission.

## CSV Field Contract Inventory

The native column names below are the reusable header inventory for `GBL_IN_COUNTRY_CHARACTERISTICS.csv`. Confirm this inventory against template evidence supplied by the shared export workflow. The template establishes column names only; it does not establish accepted values, lookup authority, or permission to reuse its records.

The native FSM route preserves explicitly supplied text and uses the exact exported column names. This inventory does not establish accepted reference values or require every field for every record.

| Native FSM CSV Column | Value Contract |
|---|---|
| TerritoryCode | Preserve supplied country code. |
| CatalogCode | Preserve supplied catalog code. |
| ReferencePeriodRule | Preserve supplied code. |
| ReportingCurrencyCode | Preserve supplied currency code. |
| ConversionType | Preserve supplied value. |
| UnitOfMeasure | Preserve supplied UOM code. |
| CurrencyRoundingMethod | Preserve supplied code. |
| WeightRoundingMethod | Preserve supplied code. |
| TriangulationMode | Preserve supplied code. |
| ReturnsProcessing | Preserve supplied code. |
| KitMethod | Preserve supplied code. |
| ArrDescriptionReqFlag | Preserve supplied Y/N. |
| DisDescriptionReqFlag | Preserve supplied Y/N. |
| ArrDeliveryTermReqFlag | Preserve supplied native Y/N value; do not default it. |

## CSV Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Explicit route | Select FSM for explicit CSV Import or a native archive containing ASM_SETUP_CSV_METADATA.xml; otherwise retain REST. | CSV Import is explicitly requested | |
| Field namespace | Require exact exported CSV headers; do not apply REST/UI aliases; reject unknown columns | Structured values are supplied for CSV Import | |
| Value preservation | Preserve supplied code, ID, name, and Y/N values; do not convert ConversionType to a display name, infer CatalogCode or UnitOfMeasure mappings, or add omitted values | Structured values are supplied for CSV Import | |
| Required native arrival delivery term flag | Preserve ArrDeliveryTermReqFlag as a native FSM column. When current BO validation or a Fusion diagnostic requires it for the target country record, require a nonblank supplied Y/N value; stop preparation when it is blank and do not infer a value. | A country record is prepared for CSV Import | |
| Template provenance | Require a verified, same-task, same-environment, compatible-release template-only export with one ASM_SETUP_CSV_METADATA.xml marker, matching ZIP fingerprint, exact member/header inventory, and zero data rows. Do not use a populated current-data export as the authoring carrier. | An FSM package is prepared | |
| Package delta | Preserve the template metadata, member hierarchy, encoding, and untouched header-only members. Add only the requested country row to GBL_IN_COUNTRY_CHARACTERISTICS.csv; require a member inventory, semantic diff, and sanitized preparation receipt before Data Loader handoff. | An FSM package is prepared | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| INTRASTAT_COUNTRY_CHARACTERISTICS.CLASSIFY_IMPORT_ROUTE | decision | 1 | validate_input | rest->INTRASTAT_COUNTRY_CHARACTERISTICS.RETURN_SUCCESS;fsm->INTRASTAT_COUNTRY_CHARACTERISTICS.VALIDATE_FSM_INPUT;blocked->INTRASTAT_COUNTRY_CHARACTERISTICS.RETURN_ISSUES | none | stop | Select FSM for an explicit CSV Import request or a native archive containing ASM_SETUP_CSV_METADATA.xml; otherwise retain the default REST route. Classification does not submit or construct a package. |
| INTRASTAT_COUNTRY_CHARACTERISTICS.VALIDATE_FSM_INPUT | decision | 11 | validate_input | valid->INTRASTAT_COUNTRY_CHARACTERISTICS.VALIDATE_FSM_PACKAGE;blocked->INTRASTAT_COUNTRY_CHARACTERISTICS.RETURN_ISSUES | INTRASTAT_COUNTRY_CHARACTERISTICS.CLASSIFY_IMPORT_ROUTE | stop | Classified FSM input only. Apply the CSV Import Input Contract and CSV Field Validation. Preserve native values without UI aliases or REST normalization. |
| INTRASTAT_COUNTRY_CHARACTERISTICS.VALIDATE_FSM_PACKAGE | decision | 20 | validate_input | valid->INTRASTAT_COUNTRY_CHARACTERISTICS.FSM_DATALOADER_HANDOFF;blocked->INTRASTAT_COUNTRY_CHARACTERISTICS.RETURN_ISSUES | INTRASTAT_COUNTRY_CHARACTERISTICS.VALIDATE_FSM_INPUT | stop | Require template-only provenance and a minimal immutable country-characteristics delta before Data Loader handoff. |
