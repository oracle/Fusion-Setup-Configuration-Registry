# IDR Dependency Readiness

This task updates an existing IDR setup. Do not create prerequisite setup data.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Existing target IDR setup | Require exactly one options data row in a completed exact-task fresh target export and treat it as the singleton. Zero or multiple rows block the update. When prorate is changed, confirm the existing AP_PRORATE_FREIGHT_MISC extension row. |
| 2 | Update preview | Show only source-backed requested changes and preserve unrelated source rows and fields; route any approved import through core.data-loader. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| IDR-EXISTING-OPTIONS | Exactly one options row in fresh target export | Yes | Every update | Runtime supported; verify for each update | Fresh completed exact-task target export |  | Create is unsupported. The sole row is the singleton; zero or multiple rows block. No portable CSV key is established. | Supply a fresh exact-task target export for each update. Live options-row updates passed post-import reconciliation. | One-row cardinality evidence |
| IDR-EXISTING-PRORATE | Existing AP_PRORATE_FREIGHT_MISC extension row | Conditional | Prorate freight and miscellaneous lines is changed | Verify | Fresh target export; a package from another environment is not target evidence | validate_idr_extension_option_code | No new extension row may be created. | Confirm the allowed row exists in the target. | Existing OptionCode selector |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Existing target rows required by the requested update are confirmed | No create |
| Blocked | Existing options singleton or required extension row is unavailable | No import or create |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IDR.DEP.CHECK | step | 30 | resolve_dependency | success->IDR.DESIGN.ENFORCE;failure->IDR.ERROR.BLOCK | IDR.INPUT.VALIDATE | stop | Every IDR update. Require existing target setup and the allowed extension row when requested. |

## Mapping-dialog updates

Require a fresh exact-task baseline and the complete intended email/business-unit assignments. The adapter validates and serializes structured rows locally; it does not query a BU service. Let Fusion validate BU existence and application-specific references during the separately approved import through the governed exact-field path. Preserve both internal mapping cells and all unrelated values. Do not fabricate a reference lookup result. A mapping restore requires a new exact restoration design and informed acceptance; retain the saved state when restoration is not requested.
