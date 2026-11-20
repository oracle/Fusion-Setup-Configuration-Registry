# Manage Change Order Types Design Enforcement

Source: user-provided best practices, package-scope rules, CopiedFrom clarification, and header-attribute restriction. This file owns business policy; lookup mechanics remain in ora_reference_lookups.md.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Establish target relationship | Consume the relationship lookup result; for creation evaluate the resulting new type's relationship |
| 2 | Enforce package scope | Retain all selected-type rows and dependencies; exclude unrelated types |
| 3 | Apply header-attribute exception | Include requested base-type changes; omit child-type header-attribute rows |
| 4 | Enforce identities and requested changes | Validate copied identities and references or preserved update identities; preserve remaining values |
| 5 | Review business policies | Evaluate applicable change-type and change-policy requirements before package preview |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| New change type identity and category | Error | resolve_change_type_identity_fields | Constructed Internal Name is unconfirmed, accepted identity is already used, source identity/category is retained, or final Category Code differs from accepted Internal Name | Use valid supplied or confirmed derived Internal Name for both fields. Ask for another name for a collision; stop for missing or ambiguous carriers and recheck final ZIP | Only after valid input and required candidate confirmation |
| Effective Change Policy Assignee Role is present | Error | | After inheritance and explicit overrides, effective Default Assignee is missing, blank, explicitly cleared, or known not to belong to that role, including unchanged baseline values | Require a nonblank member for Create/cloning and Update before export/import; never materialize, approve, or import an invalid pair. Copy a complete unchanged source pair without prompting. Explicit overrides win; validate partial overrides and clarify membership for changed pairs. An absent role permits blank without prompting. Retain omitted update fields and recheck final ZIP | Copy unoverridden source values; no invented user, silent role removal, or membership change |
| Sequence Generated numbering completeness | Error | | Resulting Sequence Generated configuration lacks Starting Number, Increment, or both Prefix and Suffix | Require Starting Number, Increment, and at least one nonblank Prefix or Suffix; request only missing details and block export/import until supplied. Validate input before export and recheck the final package before import | No invented defaults |
| Creating or editing a workflow | Error | resolve_change_type_workflow_mapping | Copied source blocks and separately built target blocks coexist, or dependent rows use the source sequence after the corresponding status moved | Build one canonical target model from the fresh selected-type baseline, mapping each retained or explicitly added stage before applying requested edits. Emit each target row once; regenerate from that baseline and the same identity map, never append to a prior import | Yes where lineage and requested edits are established; stop on ambiguous stage inheritance |
| Validating final ZIP workflow relationships | Error | resolve_change_type_workflow_mapping | A route step lacks exactly one parent route for the same target type and status; a route-person row lacks exactly one parent step; a mapped reference still targets a replaced source entity; or a route or complete step key is duplicated | Reopen the final ZIP and check composite parent keys and uniqueness in ORA_EGO_CHANGE_ROUTE, ORA_EGO_CHANGE_ROUTE_STEP, and ORA_EGO_CHANGE_ROUTE_PEOPLE, plus evidenced workflow-template references. Check required row coverage after mapping, not raw row counts. Preserve all distinct required steps, people, and controls | Remap proven references and collapse exact duplicates only; do not drop unmatched rows or resolve conflicting values arbitrarily |
| Creating or updating ORA_EGO_WORKFLOW_STATUS_CONTROL | Error | resolve_change_type_dependencies | More than one row exists for the same target change type, target workflow status, and action, or those identities cannot be resolved | Remap source controls before keying rows; edit a matching retained row rather than appending target controls; add only absent keys. Collapse exact duplicates, preserve distinct controls and unchanged values, and resolve differences only from the exported baseline and explicit requested edits. Recheck the final ZIP member before approval | Yes for exact duplicates and explicit edits; stop on unresolved conflicting values; keep routine checks internal |
| Creating or updating a target whose CopiedFrom is CR, DCR, PR, or CA, including copied child types | Error | resolve_change_type_relationship | Any final workflow step resolves to Scheduled, including unchanged copied steps | Stop before upload/import and report the target type, base family, and offending step: Scheduled status is not supported for this change type. Remove Scheduled from the requested workflow before importing | No silent removal; require a corrected workflow request |
| Creating a change type | Error | resolve_change_type_dependencies | Source-type or related rows are missing, other than the child header-attribute exclusion | Copy all source-type rows and dependencies; apply requested changes and required new identities/references; preserve other values | Yes, within requested creation scope |
| Copying Routes and route steps | Error | resolve_change_type_dependencies | New entities reuse source identifiers, collide, or reference old copied entities | Use unique new Route and route-step identifiers and update dependent references consistently; use an identifier format and allocation method supported by the supplied package evidence | Only after identity mapping and allocation are documented |
| Updating a change type | Error | resolve_change_type_dependencies | Package omits unchanged target dependencies, includes unrelated types, or changes unrequested values | Copy all target-type rows and dependencies from export; retain unchanged identifiers and values; apply only requested changes and the header exception | Yes, within requested target scope |
| Clearing a default lookup | Error | resolve_default_lookup_removal | PriorityCode or ReasonCode is cleared without an explicit request for that field, a requested clear is not applied, unrelated values are changed without an applicable rule, or shared lookup definitions are altered | Scope this gate to lookup clearing, not the entire package. Evaluate Start Date separately under its date rules and allow independently valid changes together; neither operation requires nor blocks the other. Retain required dependencies and unrelated values, preserve shared lookup definitions, and validate requested blank fields in the final ZIP | Yes for explicitly requested clears; independently valid changes remain allowed under their own rules |
| Base target with requested header changes | Error | resolve_change_type_relationship | Requested Customer, Supplier, Manufacturer, or Source changes are omitted or other header values are overwritten | Apply the requested base-type header changes and preserve other values | Yes, as requested |
| Child target, including a newly copied child | Error | resolve_change_type_header_attributes | Any header-attribute row remains in the import package | Omit all child-target header-attribute rows, even unchanged ones, to avoid EGO_ATTR_DISPLAY_CONFIG_U2; this overrides full-row preservation | Yes, omit only the identified header rows |
| Header changes requested for a child | Error | resolve_change_type_relationship | The package applies child header changes or silently broadens scope to the base | Report the unapplied request and base-only restriction; do not modify the base without a request targeting it | No silent retargeting |
| Selecting a creation baseline | Error | resolve_change_type_relationship | Baseline does not support the requested business purpose | Copy the appropriate Oracle predefined type: Engineering Change Order, Commercialization Change Order, Change Order without Revision Control, or Change Request | Select the appropriate source |
| Seeded hierarchy and shared configuration | Error | | All Change Types is used to create changes, or shared parent configuration is changed without scope | Keep the hierarchy and shared parent stable; use All Change Types for hierarchy and inherited flexfield configuration | Only within explicitly requested scope |
| Requested attachment category on creation | Error | resolve_attachment_category | The category cannot be resolved or created for `EGO_ENGINEERING_CHANGES_B`, the applied association Start Date is invalid, or the final package lacks its exact target Change Policy association with that nonblank Start Date | Reuse an exact existing category or create it through Manage Attachment Categories for Product Management, then add and validate its association and supplied or current-date-defaulted effective Start Date in the target Change Policy before import approval | No; stop package preparation and import |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_change_type_identity_fields | Create identity and category assignment | Exact current-export carrier columns, accepted new Internal Name, and existing identities | ora_reference_lookups.md |
| resolve_change_type_relationship | Base/child or source selection | Selected type and resulting target relationship | ora_reference_lookups.md |
| resolve_change_type_dependencies | Creation or update row checks | Complete selected rows, dependencies, and identity/reference mapping | ora_reference_lookups.md |
| resolve_change_type_workflow_mapping | Creation or workflow-update validation | Request-backed status and route mapping, complete parent keys, reference fields, and row provenance | ora_reference_lookups.md |
| resolve_change_type_header_attributes | Header inclusion or exclusion | Exact header rows and owning type | ora_reference_lookups.md |
| resolve_default_lookup | Requested default assignment | Exact enabled mapped lookup code | ora_reference_lookups.md |
| resolve_default_lookup_removal | Explicit default removal | Nonblank current requested field and a blank-field validation result | ora_reference_lookups.md |
| resolve_attachment_category | Requested attachment category for a creation | Exact category identity, creation/reuse outcome, and Change Policy association with its effective Start Date | ora_reference_lookups.md |

## Deferred Policy Decisions

At the user's request, enterprise policy authorities and their lookup contracts are pending decisions, not executable validation blockers. Retain the following best practices for later policy authoring; do not claim that enterprise approval or impact assessment has been verified. The package, identity, relationship, header-attribute, Sequence Generated completeness, and import-approval rules remain active.

- Workflow configuration: Use approved steps appropriate to the type's purpose; use interim approvals only for a staged-review requirement. The CR/DCR/PR/CA Scheduled restriction in Design Rules is active and is not deferred.
- Numbering configuration: Define Change Policy before use; choose Sequence Generated, Rule Generated, or User-Defined; govern prefix, start, increment, suffix; test rule-set uniqueness, inputs, exceptions, and import behavior; restrict manual numbers to required external or regulatory identifiers.
- Changing numbering after use: Existing numbers remain unchanged; assess the new method for subsequent records.
- Effective dates and cancellation: Set normal lead-time defaults; permit authorized affected-object adjustment before submission; affected-item dates determine production effectivity; define scheduled cancellation and completion after applicable lines finish or cancel.
- Comments, assignees, and reassignment: Use Required, Optional, or Not Applicable comments according to business need; establish default assignee and required role, especially for supplier changes; permit controlled reassignment when unavailable.
- Priorities, reasons, attachments, and rejection: Govern priorities/reasons; retire unused values under change control; select necessary attachment categories; standardize rejection reasons.
- Production policy changes: Review approvals, notifications, integrations, reports, audit, downstream applications, and active changes; avoid uncontrolled production changes.

The reusable identifier-allocation contract also remains a pending decision. Validate actual copied identifiers and references against available package evidence; do not invent an allocation method when the operation requires one.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COT.ENFORCE_DESIGN | step | 50 | design_enforcement | valid->COT.IMPORT_GATE;invalid->COT.REPORT_ISSUES | COT.PRESERVE_VALUES | stop | A selected-type package is being prepared |
