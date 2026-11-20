# Design Enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_REPORTING_ENTITY::TaxIdentificationNum, AP_REPORTING_ENTITY::EntityName, AP_REPORTING_ENTITY::EffectiveStartDate, AP_REPORTING_ENTITY::EffectiveEndDate, AP_REPORTING_ENTITY::BuName, AP_REPORTING_ENTITY::InternalLocationCode, AP_REPORTING_ENTITY::SetCode, AP_REPORTING_ENTITY::EnterpriseId, AP_REPORTING_ENTITY_LINE::BalancingSegmentValue, AP_REPORTING_ENTITY_LINE::AP_REPORTING_ENTITY.BuName, AP_REPORTING_ENTITY_LINE::AP_REPORTING_ENTITY.InternalLocationCode, AP_REPORTING_ENTITY::GlobalAttributeCategory, AP_REPORTING_ENTITY::GlobalAttribute1, AP_REPORTING_ENTITY::GlobalAttribute2, AP_REPORTING_ENTITY::GlobalAttribute3, AP_REPORTING_ENTITY::GlobalAttribute4, AP_REPORTING_ENTITY::GlobalAttribute5, AP_REPORTING_ENTITY::GlobalAttribute6, AP_REPORTING_ENTITY::GlobalAttribute7, AP_REPORTING_ENTITY::GlobalAttribute8, AP_REPORTING_ENTITY::GlobalAttribute9, AP_REPORTING_ENTITY::GlobalAttribute10, AP_REPORTING_ENTITY::GlobalAttribute11, AP_REPORTING_ENTITY::GlobalAttribute12, AP_REPORTING_ENTITY::GlobalAttribute13, AP_REPORTING_ENTITY::GlobalAttribute14, AP_REPORTING_ENTITY::GlobalAttribute15, AP_REPORTING_ENTITY::GlobalAttribute16, AP_REPORTING_ENTITY::GlobalAttribute17, AP_REPORTING_ENTITY::GlobalAttribute18, AP_REPORTING_ENTITY::GlobalAttribute19, AP_REPORTING_ENTITY::GlobalAttribute20 -->
<!-- fscr-update-fields: AP_REPORTING_ENTITY::TaxIdentificationNum, AP_REPORTING_ENTITY::GlobalAttributeCategory, AP_REPORTING_ENTITY::GlobalAttribute1, AP_REPORTING_ENTITY::GlobalAttribute2, AP_REPORTING_ENTITY::GlobalAttribute3, AP_REPORTING_ENTITY::GlobalAttribute4, AP_REPORTING_ENTITY::GlobalAttribute5, AP_REPORTING_ENTITY::GlobalAttribute6, AP_REPORTING_ENTITY::GlobalAttribute7, AP_REPORTING_ENTITY::GlobalAttribute8, AP_REPORTING_ENTITY::GlobalAttribute9, AP_REPORTING_ENTITY::GlobalAttribute10, AP_REPORTING_ENTITY::GlobalAttribute11, AP_REPORTING_ENTITY::GlobalAttribute12, AP_REPORTING_ENTITY::GlobalAttribute13, AP_REPORTING_ENTITY::GlobalAttribute14, AP_REPORTING_ENTITY::GlobalAttribute15, AP_REPORTING_ENTITY::GlobalAttribute16, AP_REPORTING_ENTITY::GlobalAttribute17, AP_REPORTING_ENTITY::GlobalAttribute18, AP_REPORTING_ENTITY::GlobalAttribute19, AP_REPORTING_ENTITY::GlobalAttribute20 -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Task and identity | Bind exact task and target; preserve keys and audit |
| 2 | Header and line aggregate | Require at least one balancing child for header create |
| 3 | Known invalid values | Apply source-backed checks before uncertainty acceptance |
| 4 | Governed validation | Disclose unresolved operation/reference contract and obtain exact field/candidate acceptance when permitted |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Create header | Blocker |  | No balancing-segment child; AP_AT_LEAST_ONE_CHILD | Supply at least one intended primary balancing value | User input only |
| Name or tax identifier in a BU | Blocker |  | Known duplicate name+OrgId or tax-ID+OrgId | Choose intended unique business identity; no auto-rename | User correction only |
| Balancing assignment | Blocker |  | Blank value, missing or ambiguous parent, or duplicate child tuple under that parent | Supply a value and correct parent; remove duplicate child tuples. FSM validates eligibility and reports rejection. | User correction only |
| Update | Blocker |  | Attempt to mutate name/BU/location identity, parent reference, child balancing key, or audit; no current source-backed rename/reassignment contract | Preserve identity; tax-ID and FSM-exposed global-attribute updates are supported; Fusion validates configured global flexfield rules | No automatic key conversion |
| Evidence uncertainty | Required review |  | Exact target matching must be established; ambiguous shared XML matches require field/candidate-specific review. Fusion enforces configured global-attribute rules | Classify evidence_unresolved, disclose expected FSM failure surface and permit only the active governed field/candidate acceptance path; never bypass proven-invalid rules | No implicit override |
| Retirement or delete request | Blocker |  | Delete and reporting-entity retirement are unsupported | Reject the request. Location effective dates cannot be used to retire a reporting entity. | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRE.DESIGN | step | 50 | design_enforcement | success->MRE.GATE;failure->MRE.ERROR | MRE.DEFAULT | stop | Before preview and before governed application validation |
