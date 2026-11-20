# Smart Operations Configurations Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Current task CSV support | Verify current selected-target CSV flags under verify_smart_operations_csv_support, separately from Business Object associations |
| 2 | Current task Business Object associations | Verify current exact required associations under verify_smart_operations_business_objects; missing, ambiguous or incomplete current results stop execution |
| 3 | UOM | Verify the selected UOM is present and active under verify_uom |
| 4 | Organizations | Verify the selected organization is active and inventory-enabled under verify_organizations |
| 5 | Manufacturing Plant | Verify the same organization is a manufacturing plant with setup parameters under verify_manufacturing_plant |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| SOC-CSV-SUPPORT | Current task CSV flags | Yes | Any request changing task configuration | Verify | Current exact same-target Fusion setupTasks flag result | verify_smart_operations_csv_support | Task CSV support must be checked independently of Business Object association | Use the documented live exact-task flag lookup; no local catalog fallback | Exact task identity, raw flags, selected flag and current CSV-support result |
| SOC-BUSINESS-OBJECTS | Current task Business Object associations | Yes | Any request changing task configuration | Verify | Current selected-target Fusion BOSS taskBusinessObjects association result under the documented lookup | verify_smart_operations_business_objects | Task requires existing associated setup definitions | Use the documented read-only BOSS association contract with complete coverage and exact task/object codes; preparing a ZIP or checking CSV flags does not create or verify definitions | Current associated object identities, source and retrieval date |
| SOC-UOM | UOM | Yes | Any request changing task configuration | Verify | Current same-target Fusion unitsOfMeasure result | verify_uom | Approved historical mapping lists UOM separately | Provide selected code; missing or inactive UOM stops without creating it | UOM identity, active result, target and timestamp |
| SOC-ORG | Organizations | Yes | Any request changing task configuration | Verify | Current same-target Fusion inventoryOrganizations result | verify_organizations | Approved historical mapping lists Organizations separately | Use selected exact organization; no numeric coercion or cross-target ID substitution | String organization identity, status, inventory readiness, target and timestamp |
| SOC-MFG-PLANT | Manufacturing Plant | Yes | Any request changing task configuration | Verify | Current same-target result for the resolved organization | verify_manufacturing_plant | Approved historical mapping requires Manufacturing Plant separately | Preserve reported flag/types and encoding warning; false, missing or unknown readiness stops without setup changes | Manufacturing designation, setup-complete result, raw types, target and timestamp |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| blocked_contract | Required input, lookup contract or current authority is missing or ambiguous | No; resolve the specific missing fact before any call |
| ready | Declared resolvers have valid current same-target results for this request | Only declared authorized reads; this state grants no create/update/import permission |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| SOC.CHECK_DEPENDENCIES | step | 70 | resolve_dependency | ready->SOC.ENFORCE_DESIGN;blocked->SOC.HANDLE_ERROR | SOC.VERIFY_MANUFACTURING_PLANT | stop | Evaluate Dependency Rules against all preceding current lookup results; prerequisite setup remains separate. |

## Configuration Scope

Use the fresh template, approved row values, second-reviewer findings and
administrator handoff defined in this skill's Scoped Preparation and Reviewer
Handoffs. Keep task CSV results separate from Run Book load and completion.
Example organizations, UOMs, percentages, reason codes, languages, row counts
and prior approvals are not defaults for a new implementation. Historical
results do not establish readiness or completion for the selected target.
