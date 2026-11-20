# Input Validation

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_REPORTING_ENTITY::TaxIdentificationNum, AP_REPORTING_ENTITY::EntityName, AP_REPORTING_ENTITY::EffectiveStartDate, AP_REPORTING_ENTITY::EffectiveEndDate, AP_REPORTING_ENTITY::BuName, AP_REPORTING_ENTITY::InternalLocationCode, AP_REPORTING_ENTITY::SetCode, AP_REPORTING_ENTITY::EnterpriseId, AP_REPORTING_ENTITY_LINE::BalancingSegmentValue, AP_REPORTING_ENTITY_LINE::AP_REPORTING_ENTITY.BuName, AP_REPORTING_ENTITY_LINE::AP_REPORTING_ENTITY.InternalLocationCode, AP_REPORTING_ENTITY::GlobalAttributeCategory, AP_REPORTING_ENTITY::GlobalAttribute1, AP_REPORTING_ENTITY::GlobalAttribute2, AP_REPORTING_ENTITY::GlobalAttribute3, AP_REPORTING_ENTITY::GlobalAttribute4, AP_REPORTING_ENTITY::GlobalAttribute5, AP_REPORTING_ENTITY::GlobalAttribute6, AP_REPORTING_ENTITY::GlobalAttribute7, AP_REPORTING_ENTITY::GlobalAttribute8, AP_REPORTING_ENTITY::GlobalAttribute9, AP_REPORTING_ENTITY::GlobalAttribute10, AP_REPORTING_ENTITY::GlobalAttribute11, AP_REPORTING_ENTITY::GlobalAttribute12, AP_REPORTING_ENTITY::GlobalAttribute13, AP_REPORTING_ENTITY::GlobalAttribute14, AP_REPORTING_ENTITY::GlobalAttribute15, AP_REPORTING_ENTITY::GlobalAttribute16, AP_REPORTING_ENTITY::GlobalAttribute17, AP_REPORTING_ENTITY::GlobalAttribute18, AP_REPORTING_ENTITY::GlobalAttribute19, AP_REPORTING_ENTITY::GlobalAttribute20 -->
<!-- fscr-update-fields: AP_REPORTING_ENTITY::TaxIdentificationNum, AP_REPORTING_ENTITY::GlobalAttributeCategory, AP_REPORTING_ENTITY::GlobalAttribute1, AP_REPORTING_ENTITY::GlobalAttribute2, AP_REPORTING_ENTITY::GlobalAttribute3, AP_REPORTING_ENTITY::GlobalAttribute4, AP_REPORTING_ENTITY::GlobalAttribute5, AP_REPORTING_ENTITY::GlobalAttribute6, AP_REPORTING_ENTITY::GlobalAttribute7, AP_REPORTING_ENTITY::GlobalAttribute8, AP_REPORTING_ENTITY::GlobalAttribute9, AP_REPORTING_ENTITY::GlobalAttribute10, AP_REPORTING_ENTITY::GlobalAttribute11, AP_REPORTING_ENTITY::GlobalAttribute12, AP_REPORTING_ENTITY::GlobalAttribute13, AP_REPORTING_ENTITY::GlobalAttribute14, AP_REPORTING_ENTITY::GlobalAttribute15, AP_REPORTING_ENTITY::GlobalAttribute16, AP_REPORTING_ENTITY::GlobalAttribute17, AP_REPORTING_ENTITY::GlobalAttribute18, AP_REPORTING_ENTITY::GlobalAttribute19, AP_REPORTING_ENTITY::GlobalAttribute20 -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Header identity | BuName, InternalLocationCode and EntityName; retain both FSM seed and AM matching identity | Stop with missing identity | Obtain exact portable identity; do not guess | Create or update |  |
| Header business data | EntityName and TaxIdentificationNum | Stop with missing required business input | Request missing business input | Create |  |
| BU context | BuName and EnterpriseId | Stop derivation of OrgId | Resolve intended BU and enterprise | Create | resolve_reporting_entity_bu |
| Location context | InternalLocationCode, required nonblank SetCode and its effective boundaries | Do not invent a location or COMMON default | Resolve selected existing location | Create | resolve_reporting_entity_location |
| Balancing lines | At least one BalancingSegmentValue associated with the new header | Stop before candidate generation | Obtain one or more intended primary balancing values | Create header |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Child CSV business fields | Accept AP_REPORTING_ENTITY.BuName, AP_REPORTING_ENTITY.InternalLocationCode and BalancingSegmentValue as the complete child business input. Do not request TaxEntityId or fabricate an additional non-key field. Adapter row identity carries the three values on create; empty additional values are allowed only for this child create. | Create balancing child | |
| Audit columns | System-managed business inputs are rejected; preserve technical export columns and untouched values. | All operations |  |
| SetCode | Required nonblank header-create input. Reject omitted, null, empty or whitespace-only values before package output; obtain the intended location set, never default COMMON. Preserve the existing value on unrelated updates. | Create | resolve_reporting_entity_location |
| TaxIdentificationNum | Required persisted string; no nine-digit or numeric-only restriction is evidenced. Do not invent a character-length limit. | Create or tax-ID update |  |
| EntityName | Required persisted string; preserve on update as AM alternate-key input. Do not invent a character-length limit. | Create or update |  |
| Package shape | Use exact task metadata, ordered CSV headers, row widths and nodes from template/current export; preserve all non-requested data. | All package workflows |  |
| Dates | Location EffectiveStartDate and EffectiveEndDate are joined matching context; SysEffectiveDate is transient and unresolved. Do not use these as entity retirement fields. | When supplied |  |
| Global attributes | FSM exposes GlobalAttributeCategory and GlobalAttribute1–20 as persisted header inputs for create/update. Preserve supplied text and validate known source types; let Fusion enforce configured context, segment/value-set and length rules. Do not require a separate evidence-unresolved override solely because a global field is requested. Preserve unspecified values. | When requested |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRE.INPUT | step | 10 | validate_input | success->MRE.DEP;failure->MRE.ERROR | none | stop | Create or update Reporting Entities |
