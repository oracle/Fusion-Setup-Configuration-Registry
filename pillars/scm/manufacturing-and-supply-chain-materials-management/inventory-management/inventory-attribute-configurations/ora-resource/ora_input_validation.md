# Inventory Attribute Configurations Input Validation

## Source Evidence

| Source | Used For |
|---|---|
| Redwood `striping-attributes` manage page and `manage-page.js` | Item-type checkboxes compose the `ItemType` code sent in the batch payload. |
| Redwood `applicableForItemTypesChangeChain.js` | Plain, lot, and serial control values are Boolean UI model values. |
| Redwood `attributeBehaviourCheckboxChangeChain.js` | Required, Allow Reservations, and Material Status Control values are emitted as Boolean flags. |
| Redwood `attribute-mapping-rules-page-chains/getall_genericLookupsLOVFetch.js` | Source Type uses the `ORA_INV_ATTR_MAP_SRC_TYPES` lookup. |
| User-provided lookup type | Status uses `ORA_INV_ATTR_STATUS`. |
| User approval | Apply the four selected control normalizations plus Applicability Level, Source Type, and Status lookup resolution before Data Loader handoff. |

## Scope Boundary

| Boundary | What Happens |
|---|---|
| Backend-owned validation | Data Loader and Fusion own required fields, uniqueness, lengths, server-side domains, cross-record rules, and final field enforcement. |
| Local validation ownership | Normalize only the approved UI control representations and the approved Applicability Level, Source Type, and Status lookup inputs. |
| Data Loader metadata preflight | `core.data-loader` owns the per-run metadata preflight. Do not duplicate it here. |
| Execution | Do not create direct REST write guidance. `core.data-loader` owns preparation, validation, approval, and execution. |

## Accepted Input Representations

| Semantic Input | Accepted User Input | Canonical Backend Field | REST/Data Loader Physical Output | Resolver |
|---|---|---|---|---|
| Plain items | Boolean `true` or `false` | `ItemType` | One composed `ItemType` code from the three item-type controls. |  |
| Lot items | Boolean `true` or `false` | `ItemType` | One composed `ItemType` code from the three item-type controls. |  |
| Serial items | Boolean `true` or `false` | `ItemType` | One composed `ItemType` code from the three item-type controls. |  |
| Required | Boolean `true` or `false` | `RequiredFlag` | `RequiredFlag` as a Boolean. |  |
| Allow reservations | Boolean `true` or `false` | `ReservationsAllowedFlag` | `ReservationsAllowedFlag` as a Boolean. |  |
| Material status control | Boolean `true` or `false` | `MaterialStatusControlFlag` | `MaterialStatusControlFlag` as a Boolean. |  |
| Applicability Level | Exact Meaning or exact `LookupCode` | `ApplicabilityCode` | Returned `LookupCode` in `ApplicabilityCode`. | resolve_inventory_attribute_applicability_level |
| Source Type | Exact Meaning or exact `LookupCode` | `SourceType` | Returned `LookupCode` in `SourceType`. | resolve_inventory_attribute_mapping_source_type |
| Status | Exact Meaning or exact `LookupCode` | `Status` | Returned `LookupCode` in `Status`. | resolve_inventory_attribute_status |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Plain, Lot, or Serial item input is supplied | Require each supplied control to be a Boolean; compose `ItemType` from the complete three-control state. | Pass the composed code to Data Loader. |  |
| All item-type controls are false | Fill `ItemType` with the observed empty-string output. | Leave final acceptance to Data Loader and Fusion. |  |
| Required, Allow reservations, or Material status control is supplied | Require a Boolean and emit the corresponding Boolean backend field. | Pass the Boolean value to Data Loader. |  |
| Applicability Level Meaning and/or `ApplicabilityCode` is supplied | Resolve each supplied value by trim plus case-insensitive exact comparison; when both are supplied, require one identical returned row. | Fill `ApplicabilityCode` from the returned `LookupCode`. | resolve_inventory_attribute_applicability_level |
| Source Type Meaning and/or `SourceType` is supplied | Resolve each supplied value by trim plus case-insensitive exact comparison; when both are supplied, require one identical returned row. | Fill `SourceType` from the returned `LookupCode`. | resolve_inventory_attribute_mapping_source_type |
| Status Meaning and/or `Status` is supplied | Resolve each supplied value by trim plus case-insensitive exact comparison; when both are supplied, require one identical returned row. | Fill `Status` from the returned `LookupCode`. | resolve_inventory_attribute_status |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| ItemType composition | Compose: Plain=`ORA_PLAIN`; Lot=`ORA_LOT`; Serial=`ORA_SERIAL`; Plain+Lot=`ORA_LOT_PLAIN`; Plain+Serial=`ORA_SERIAL_PLAIN`; Lot+Serial=`ORA_LOT_SERIAL`; all three=`ORA_LOT_SERIAL_PLAIN`. | Any item-type control is supplied. |  |
| Unsupported control value | Reject a supplied non-Boolean value for an approved checkbox control. | Before Data Loader handoff. |  |
| Applicability Level resolution | Accept an exact Meaning or `LookupCode`; validate a directly supplied code through the same resolver. | Applicability Level or `ApplicabilityCode` is supplied. | resolve_inventory_attribute_applicability_level |
| Applicability Level conflict | Reject code-plus-meaning input that resolves to different rows. | Both representations are supplied. | resolve_inventory_attribute_applicability_level |
| Unsupported Applicability Level | Reject no-match or ambiguous input. | Applicability Level or `ApplicabilityCode` is supplied. | resolve_inventory_attribute_applicability_level |
| Source Type resolution | Accept an exact Meaning or `LookupCode`; validate a directly supplied code through the same resolver. | Source Type or `SourceType` is supplied. | resolve_inventory_attribute_mapping_source_type |
| Source Type conflict | Reject code-plus-meaning input that resolves to different rows. | Both representations are supplied. | resolve_inventory_attribute_mapping_source_type |
| Unsupported Source Type | Reject no-match or ambiguous input. | Source Type or `SourceType` is supplied. | resolve_inventory_attribute_mapping_source_type |
| Status resolution | Accept an exact Meaning or `LookupCode`; validate a directly supplied code through the same resolver. | Status or `Status` is supplied. | resolve_inventory_attribute_status |
| Status conflict | Reject code-plus-meaning input that resolves to different rows. | Both representations are supplied. | resolve_inventory_attribute_status |
| Unsupported Status | Reject no-match or ambiguous input. | Status or `Status` is supplied. | resolve_inventory_attribute_status |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| IAC.NORMALIZE_CONTROLS | step | 10 | validate_input | valid->IAC.RESOLVE_APPLICABILITY_LEVEL;invalid->IAC.HANDLE_ERROR | none | stop | Before Data Loader task validation or import preparation. |
