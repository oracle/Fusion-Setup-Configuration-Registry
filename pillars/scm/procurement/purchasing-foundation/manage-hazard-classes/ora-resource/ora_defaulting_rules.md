# Hazard Class Defaulting Rules

The approved authoring plan requires exact preservation of supplied values and
field presence. An empty CSV/XLSX InactiveDate cell represents an unprovided field and is omitted
from the outgoing record. This presence rule is not a business default; all other
supplied values, explicit nulls, and IDs remain unchanged.
Data Loader owns the eventual operation and server handling of omitted values.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| HazardClass and HazardClassCode | None; missing values remain validation issues | Every row | No | |
| HazardClassId | None; preserve any supplied value exactly without validation or normalization; never generate an ID | Every row | No | |
| Omitted Description and InactiveDate | Remain absent; never fill from name, code, current date, an existing record, or null | Every row | No | |
| Empty CSV/XLSX InactiveDate cell | Omit InactiveDate from this record; do not substitute null or a date | Empty string cell only; whitespace is not empty | Yes, only the unprovided date cell | |
| Explicit Description or InactiveDate null | Preserve explicit null; its server interpretation belongs to Data Loader | When supplied | No | |
| Every supplied value | Preserve exactly apart from omission of an unprovided InactiveDate cell; no trimming, truncation, case conversion, replacement, or type conversion | After input validation | No | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| HAZ.PRESERVE_VALUES | step | 20 | apply_default | preserved->HAZ.CHECK_DESIGN;failed->HAZ.HANDLE_ISSUES | HAZ.VALIDATE_INPUT | stop | Field validation passed; apply the no-substitution and omission rules to the supplied input |
