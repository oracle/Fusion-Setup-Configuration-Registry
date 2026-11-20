# UN Number Dependency Readiness

Hazard Class identity is a conditional read-only dependency for create/update.
Lookup mechanics are owned by ora_reference_lookups.md. No Hazard Class is
created and no eligibility restriction is inferred from InactiveDate.

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| hazard_class_identity | Existing Hazard Class | Conditional | Create/update with name or non-null ID | Verify | Selected Fusion environment | resolve_hazard_class | Association must identify one existing record and supplied keys must agree | Correct a missing/ambiguous/conflicting selector; resolve failed reads before preparation continues | Verified HazardClassId and lookup evidence; fill only an omitted ID during preparation |
| no_association | No requested association | No | No name and ID omitted/null, or valid delete | Satisfied | Approved input contract | | No lookup is required | Preserve omission/null; deletion retains its own contract | No enrichment |

The resolver node enforces this dependency before preservation. This file adds
no independent Task Nodes or additional read. Data Loader owns registration,
write privileges, operation-specific requiredness and server eligibility.
Selected environment and authenticated read access must be available before the
resolver's first GET; absent prerequisites block applicable preparation.
