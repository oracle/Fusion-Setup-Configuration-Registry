# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---:|---|---|
| 1 | Active Run Book and exact sequenced task | Complete the parent skill's core Run Book handoff before Data Loader metadata or source generation. Reuse the active binding; do not duplicate creation. |
| 2 | CpqChargeSetSync metadata and DAT template | Use resolve_loader_business_object from ora_reference_lookups.md. |
| 3 | Validated immutable POST trigger archive | Generate the DAT through core.data-loader in create mode, then validate every value using ora_input_validation.md, prepare the immutable ZIP, and complete Task Hook validation. No business payload is collected. |
| 4 | Immutable approval and internal initiation | Obtain core Data Loader approval for the exact archive; core.data-loader uploads those approved bytes to UCM and submits one IMPORT_AND_LOAD request. |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Ready for approval | Archive validation and Task Hook are ready | Present the core Data Loader approval report |
| Complete | `initiateDataLoad` for CpqChargeSetSync succeeded | Return the standard Data Loader initiation result |
| Blocked | Metadata resolution, validation, approval, or initiation fails | Stop without retrying a dependent step |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
