# UN Number Defaulting Rules

The approved authoring plan preserves the original input and creates separate
loader-ready data after conditional Hazard Class resolution. It requires preservation of supplied values and
field presence. On create/update rows, an empty CSV/XLSX InactiveDate cell represents an unprovided field and is omitted
from the outgoing record. Additional permitted preparation changes are filling an omitted HazardClassId
from verified lookup evidence and separating HazardClass lookup context from
loader business data. Other supplied values and explicit nulls stay unchanged.
Data Loader owns the eventual operation and server handling of omitted values.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| UNNumber and UNNumberCode | None; missing values remain validation issues | Create/update rows | No | |
| UNNumberId | None; preserve supplied values without validation or normalization | Create/update rows | No | |
| HazardClassId | Preserve supplied verified ID representation. Only when omitted with a supplied name, populate the authoritative resolved ID. Preserve null only without a name. Never fabricate or replace a supplied ID. | Create/update preparation after resolution | No | resolve_hazard_class |
| HazardClass | Keep original name as preparation context/evidence; exclude from the separate loader-ready business record | Preparation only; never edit a captured record | No | |
| Omitted Description and InactiveDate | Remain absent; missing Description blocks explicit create under input validation. Never fill from name, code, current date, an existing record, or null | Create/update rows | No | |
| Empty CSV/XLSX InactiveDate cell | Omit InactiveDate from this record; do not substitute null or a date | Create/update rows; empty string cell only; whitespace is not empty | Yes, only the unprovided date cell | |
| Explicit InactiveDate, UNNumberId, or HazardClassId null | Preserve explicit null; its server interpretation belongs to Data Loader | Create/update rows; when supplied | No | |
| Explicit Description null | Validation failure; do not replace it with an empty string or an omission | Create/update rows; when supplied | No | |
| Every supplied value | Preserve exactly apart from the declared preparation-only ID enrichment, context separation, and empty-date omission; no trimming, truncation, case conversion, replacement, or type conversion | After input validation | No | |
| Delete UNNumberId | None; preserve the accepted ID exactly without conversion or normalization | Delete rows after presence validation | No | |
| Intent context | Preserve scoped intent and its source through preparation and captured-source validation; keep outside business data. Never infer intent or invent a marker to satisfy requiredness | Every row | No | |
| RestAction | None; preserve explicit DELETE and all other supplied operation controls unchanged | Every row; never derive deletion from ID | No | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| UN.PRESERVE_VALUES | step | 20 | apply_default | preserved->UN.CHECK_DESIGN;failed->UN.HANDLE_ISSUES | UN.RESOLVE_HAZARD_CLASS | stop | Lookup resolved or was not applicable; apply the no-substitution and omission rules to the supplied input |
