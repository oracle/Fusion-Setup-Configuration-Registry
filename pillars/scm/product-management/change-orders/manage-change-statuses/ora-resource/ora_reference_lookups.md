# Reference Lookups

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_change_status_type | Create or a requested Status Type update; also when Existing Status Type is supplied as a selector | Supplied StatusTypeName or Existing Status Type; the fixed StatusType Catalog in this file is the local authority | Match a catalog name case-insensitively or a selection number from 1 through 5 against the Selection column, not the numeric import value; require exactly one catalog row. Do not call REST or infer a category. | Corresponding numeric StatusType for the requested value or selector comparison; catalog name for display | If missing for Create, show the catalog and request a selection. Stop on an unsupported or ambiguous value; never substitute a value. |
| validate_change_status_schema | Before constructing the final artifact | Target template CSV headers and ASM_SETUP_CSV_METADATA.xml supplied by shared.setup-export.task-level-export | Require task EGO_MANAGE_CHANGE_STATUSES, target host identity, and exact EGO_CHANGE_STATUS header; reject absent or duplicate headers | SchemaVerified; canonical headers and XML metadata | Stop and obtain the target task template |
| resolve_new_change_status_identity | Before preparing every create | Status Name; optional Internal Name; fresh populated target EGO_CHANGE_STATUS.csv | If Internal Name is omitted, replace each whitespace run in Status Name with `_`. Reject a supplied or derived value containing whitespace. Compare StatusInternalName and StatusName case-insensitively after trimming against every exported row. | resolved StatusInternalName; duplicate-check evidence | Stop before ZIP preparation if the internal name is invalid, the internal name exists, or the status name exists; do not let Fusion discover the conflict at import. |
| resolve_existing_change_status | Before preparing every update | Existing Internal Name; Existing Status; or Existing Status with Existing Status Type; with optional additional supplied selector values, and fresh populated target EGO_CHANGE_STATUS.csv | Match exactly one case-insensitive trimmed StatusInternalName when Internal Name is supplied. Without Internal Name, match StatusName with Existing Status Type after fixed-catalog numeric mapping when both are supplied; match every row with StatusName when Existing Status alone is supplied. When supplied with Internal Name, validate Existing Status and/or Existing Status Type against the exported row. | StatusInternalName plus the exported StatusName, StatusType, and ObjectName required in every import row | Stop for Existing Status Type alone, no match, or a supplied selector mismatch. For Existing Status alone, proceed with one match; with multiple matches, show every matched row and obtain explicit bulk-scope approval before preparing the import artifact. |

## StatusType Catalog

Do not make a REST call to resolve StatusType. Use only this fixed catalog.

Show this numbered catalog only when `StatusTypeName` is missing and the user must select one. Every user-facing prepared ZIP, approval, update-scope, and successful result table must use exactly these columns: `Status Name`, `Internal Name`, `Status Type`, and `Description`. Show only the StatusType name; do not show either the selection number or the numeric import value.

| Selection | User-facing StatusType | Numeric `StatusType` written to the import row |
|---:|---|---:|
| 1 | Open | 1 |
| 2 | Interim Approval | 13 |
| 3 | Scheduled | 4 |
| 4 | Completed | 6 |
| 5 | Approval | 8 |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| StatusTypeName is absent for Create | Show the fixed numbered catalog once for the batch and request a selection for every applicable row. The user may reply with the selection number (`1` through `5`) or the status name. |
| Update request includes Status Type | Treat it as a requested update value; map it from the fixed catalog and allow Fusion to validate the change. Use `Existing Status Type` only when the user means to verify the current value. |
| StatusTypeName is supplied | Accept a catalog name case-insensitively or a selection number (`1` through `5`), then write the corresponding numeric `StatusType` value to the import row. |
| StatusTypeName is unsupported | Stop; never infer or substitute a value. |
| Create request | Request a populated current setup export through shared.setup-export.task-level-export --data before create preparation. Resolve or derive the internal name and check both the candidate Internal Name and Status Name against that export. |
| Any valid Update selector, including Existing Internal Name | Request a populated current setup export through shared.setup-export.task-level-export --data before update preparation; resolve the selected row, copy the complete row into the ZIP, and change only requested fields. Export is preparation before Task Hook, not a node-side mutation. |
| Existing Status is the only selector | If one row matches, proceed. If multiple rows match, display every matched Internal Name, Status, and Status Type and stop until the user explicitly approves the bulk scope. Do not prepare an artifact or import before that approval. |
| Stale or wrong-environment source | Stop and refresh via the declared export workflow; do not call an invented REST endpoint |
| Translation data | Use translation rows only to associate the selected display name with the exported internal name; do not fabricate a language code |
| Authority | The user-authorized downloaded FSM setup export is the local lookup authority for this validation run; retain its path and checksum in project evidence |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MCS.LOOKUPS | step | 20 | evaluate_result | resolved->MCS.DEFAULTS;missing->RETURN_ISSUES;conflict->RETURN_ISSUES | MCS.INPUT | stop | Input validation passed; evaluate the Local Lookups against the fixed catalog and supplied current export/template evidence without external calls |

## Sources

- Current target FSM template: EGO_CHANGE_STATUS.csv and ASM_SETUP_CSV_METADATA.xml.
- User-authorized populated FSM export for the current validation run.
- Oracle 26D status behavior (latest SCM documentation release verified on 2026-11-03): https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faipr/understand-change-order-statuses.html
- Oracle import matching, historical 25D fallback: https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25d/faipr/import-and-export-change-type-configuration.html

Latest-release gap: on 2026-11-03, the corresponding 26D import/export topic
could not be retrieved, and the targeted documentation search returned the 25D
page. Retain that source as historical guidance, not verified 26D behavior.
Recheck the latest Oracle documentation before use and validate import matching,
CSV headers, and encodings against the fresh target FSM template and populated
export; stop if the evidence conflicts. The status overview documents status
behavior, not the numeric CSV import values.

The string business code maps to StatusInternalName.
