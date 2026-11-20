# Manage Change Order Types Reference Lookups

Source: the user identifies the exported package and EGO_CHANGE_HEADER_TYPE as the source for change-type relationships. Default lookup resolution delegates to the Apps Common lookup workflow; this skill does not call a lookup endpoint directly.

## Local Lookups

Use the Base Change Type Mapping below to interpret the user's selected copy source and its CopiedFrom value. Resolve the actual source row and its dependent rows from the fresh export before package preparation.

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_change_type_identity_fields | Before constructing a new type package and validating its final ZIP | Accepted user-supplied or user-confirmed constructed Internal Name; new Name; current EGO_CHANGE_HEADER_TYPE and related exported files/metadata | Identify exact Internal Name and change type Category Code carriers from current export/schema evidence and their dependent references. Use TypeInternalName or CategoryCode only if those exact columns are evidenced; never invent a carrier. Check accepted identity against existing exported types. The source provides schema and existing-identity evidence, not the new identity value | internal_name_column; category_code_column; accepted_internal_name; existing_identity_matches; dependent_identity_references | Stop on missing/ambiguous carriers, unaccepted identity or existing identity collision; do not retain source identity/category code or guess a suffix |
| resolve_change_type_relationship | Before classifying a selected source or target type | EGO_CHANGE_HEADER_TYPE in the supplied export package; selected change type; CopiedFrom | Select the requested type from EGO_CHANGE_HEADER_TYPE and compare CopiedFrom with that type's corresponding exported identity. Equal means base change type; different means child of the referenced base. This describes change types, not workflow statuses | selected_type; copied_from; base_type; relationship | Stop on an unresolved or ambiguous selection; report the missing export mapping |
| resolve_change_type_dependencies | Before retaining or excluding dependent rows | Selected source or target type and all dependent files in the export package | Use the supplied export's evidenced identities and parent-child references to select all rows related to the type, including Routes and route steps; exclude rows owned only by unrelated types | selected_type_rows; dependent_rows; route_rows; route_step_rows; unrelated_rows | Stop if required relationships cannot be resolved; do not substitute the full multi-type export |
| resolve_change_type_workflow_mapping | Before emitting creation or workflow-update dependencies | Selected source or target export rows; requested workflow edits; proposed target statuses and allocated route identities | Join ORA_EGO_CHANGE_TYPE_STATUS_SEQUENCE to ORA_EGO_CHANGE_ROUTE using exported type and sequence columns. Resolve source status identity to target status identity from retained identity and explicit requested edits, then map its source route and sequence to the target route and sequence. A requested split may have multiple explicitly identified target stages, each with its own route; never choose by row position, equal sequence alone, or a route-name suffix. Resolve step keys from type, status sequence, parent route, StepActivityType, and StepSeqNumber as evidenced by the supplied CSV, and resolve people through their corresponding prefixed step columns. Identify WfProcessTemplate and any other route-reference fields only where export/request evidence establishes that relationship | status_mapping; route_mapping; step_parent_mapping; people_parent_mapping; workflow_reference_fields; row_provenance | Stop for unresolved stage lineage, missing or multiple parent matches, ambiguous splits, or unsupported key columns; never guess which baseline controls or steps a new stage inherits |
| resolve_change_type_header_attributes | Before applying the base/child header-attribute rule | Export package rows for Customer, Supplier, Manufacturer, and Source header attributes | Identify the named header attributes and their owning type from the supplied export's fields and references; EGO_ATTR_DISPLAY_CONFIG_U2 is the reported constraint name, not an assumed file or column name | header_attribute_rows; header_attribute_owner | Stop if header rows cannot be distinguished from other dependent rows; do not drop unrelated attribute data |
| resolve_default_lookup | A requested creation or update assigns `PriorityCode` or `ReasonCode` | Requested field/code and its mapped Standard Lookup | Require exactly one enabled exact `LookupCode` through `core.fusion-api.apps-common.lookups`. If new, route to the mapped task, then re-read the lookup | field_name; lookup_type; lookup_code; lookup_status | Stop if absent, disabled, or ambiguous; do not submit a type package until every requested lookup is confirmed |
| resolve_default_lookup_removal | A user explicitly clears `PriorityCode` or `ReasonCode` | Selected target header from the fresh export | Confirm one target header row and a nonblank requested field; no lookup operation applies | field_name; value_before; clear_requested | Stop if the request is ambiguous or the field is already blank; never modify the shared lookup |
| resolve_attachment_category | A change-order-type creation supplies `attachment_category` | Supplied Category Name, Entity Name defaulted to EGO_ENGINEERING_CHANGES_B when omitted or blank, optional association Start Date, and the result from Manage Attachment Categories for Product Management under Product Management → Items | Pass the resolved Entity Name explicitly to the attachment-category skill. Request fresh setup-data export, not template/spec; apply entity export criteria only if the delegated workflow supports them, otherwise inspect the returned data for that entity. Distinguish category existence from entity association; absence from entity-scoped results alone does not prove system-wide absence. Missing or incomplete export evidence is unresolved, not not-found. Use the attachment-category skill as the authority: it must return one exact category for entity `EGO_ENGINEERING_CHANGES_B`, or create it with Category Name, User Name, Description, and that entity when no exact category exists. Use the supplied association Start Date or default it to the current date at package preparation in the export's date format, then validate the final package row contains the applied date. This task does not select a direct lookup or transport route | category_name; category_status; category_identity; entity_name; association_start_date; association_start_date_source | Stop for a missing Category Name, ambiguous result, failed category creation, invalid applied Start Date, or missing User Name or Description when creation is needed. Do not submit the type package |

## Base Change Type Mapping

Source: the user-provided table in Base Type vs Copied From.docx. The document columns type_internal_name, type_name, and copied_from identify the selected source code, its display name, and its CopiedFrom value respectively. Preserve the exact values below; do not derive CopiedFrom by removing a prefix or replacing it with the source code.

| type_internal_name | type_name | copied_from |
|---|---|---|
| ORA_CR | Change Request | CR |
| ORA_DCR | Deviation Change Request | DCR |
| ECO | Commercialization Change Order | ECO |
| ORA_ENG_CO | Engineering Change Order | ENG_CO |
| ORA_NRCO | Change Order without Revision Control | NRCO |
| ORA_CA | Corrective Action | CA |
| ORA_PR | Problem Report | PR |

Match the user's supplied source name or internal code to the same row. When copying that source, retain its mapped CopiedFrom value in the new type while assigning the new type its own identity. The creation input called Base Change Type denotes the selected copy source; it does not imply that the source's internal name equals its CopiedFrom value. Continue to use the exported identity comparison for base/child classification. For a source not listed here, use its explicit fresh-export mapping rather than inventing a value. If the listed mapping conflicts with the fresh export, report the discrepancy and resolve the source selection before preparing the package.

## Default Lookup Mapping

| Change type field | Standard Lookup | Creation task |
|---|---|---|
| `PriorityCode` | `EGO_CHANGE_PRIORITIES` | Manage Change Priorities |
| `ReasonCode` | `EGO_CHANGE_REASONS` | Manage Change Reasons |

## Pending Mapping Decisions

A reusable column map for type identity, dependent-row joins, and header-attribute ownership is deferred at the user's request. Its absence is not a static rule-readiness blocker. Use actual export evidence during validation; a concrete missing or ambiguous mapping still returns a task issue and must not be guessed.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COT.RESOLVE_EXPORT | step | 20 | evaluate_result | resolved->COT.RESOLVE_ATTACHMENT_CATEGORY;invalid->COT.REPORT_ISSUES | COT.VALIDATE_INPUT | stop | A selected change type must be resolved from its export |
