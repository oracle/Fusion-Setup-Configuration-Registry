# Dependency Readiness

## Dependency Rules

Evaluate these prerequisites in order. Invoke the named resolvers defined in
ora_reference_lookups.md; retain their evidence for KFF.LOOKUP_EXISTING, which
classifies the requested delta. Do not repeat a successful lookup against the
same unchanged evidence.

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| KFF.DEP.STATE | Current target evidence | Yes | Every request | Verify | Current same-task state evidence | resolve_existing_kff_structure | Existing-state checks prevent duplicates; these rows are not import donors. | Missing, stale, incomplete, or ambiguous evidence blocks progress. Verified absence can support creation, never an update to a missing object. | Complete target state |
| KFF.DEP.TEMPLATE | Fresh import template | Yes | Package authoring | Verify | Fresh same-task template and ASM_SETUP_CSV_METADATA.xml | | The target package schema must be available. | Missing or incomplete template metadata blocks authoring; populated data rows are not required. | Package members, headers, and supported column formats |
| KFF.DEP.VALUE_SETS | Referenced value sets | Conditional | A structure or instance segment references a value set | Verify | Value-set resolver result | resolve_compatible_value_set | Naming does not establish existence or compatibility. | Route missing definitions to the owning Fixed Assets value-set task through the orchestrator with proposed code, explicit/defaulted validation type, design, and supplied values. Wait for its verified result before binding; ask only for unresolved business inputs. | Verified value-set references |
| KFF.DEP.LABELS | Label definitions | Conditional | A label assignment or Category structure change is requested | Verify | Documented seeded Category mappings; authoritative evidence for other labels | resolve_segment_label | Resolve the label before authoring. | Use the documented seeded mappings without exported label data or a waiver. Custom, unknown, or conflicting labels still require resolution. | Resolved label and assignment |
| KFF.DEP.TREE | Segment tree | Conditional | Tree Code is supplied | Verify | Tree resolver result | verify_segment_tree | Tree association must be verified. | Supply missing authoritative evidence; do not bind an unverified tree. | Verified tree association |
| KFF.DEP.PARENT | Parent structure design | Conditional | An instance is requested | Verify | Resolved target state or approved same-package parent design | resolve_existing_kff_structure | The complete parent segment design must be available. | Resolve the parent before authoring instance rows. | Complete parent design |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| KFF.RESOLVE_DEPENDENCIES | decision | 20 | resolve_dependency | ready->KFF.LOOKUP_EXISTING;blocked->KFF.HANDLE_DEPENDENCY | KFF.VALIDATE_INPUT | stop | Valid input. |
