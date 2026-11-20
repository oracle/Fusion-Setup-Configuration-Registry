# Invoice Holds local rule identifiers

The descriptor and emitted receipts use these identifiers to select maintained
local rules. The `sourceIds` and `generation.operationEvidence` metadata fields
identify guidance only; they do not prove a successful import, saved values or
recovery eligibility. Apply the linked contract in its stated scope.

The descriptor's `generator` is an authoring-tool identifier. Its
`contractReference` identifies package prerequisites. Neither metadata field
selects an execution route or grants approval.

| Rule identifier | Scope | Local contract |
| --- | --- | --- |
| HOLDS-PACKAGE-CONTRACT | Exact task identity, template/current export compatibility, metadata and archive safety. | [Package prerequisites](../ora-resource/ora_dependency_readiness.md#package-and-runtime-prerequisites) |
| HOLDS-FIELD-CONTRACT | Required fields, insert-only keys, types, precision, flag domains, accepted clears and audit ownership. | [Field validation](../ora-resource/ora_input_validation.md#field-validation) |
| HOLDS-DEFAULTS | Create-only defaults and explicit-input precedence. | [Create defaults](../ora-resource/ora_defaulting_rules.md#standard-defaults) and [defaulting policy](../ora-resource/ora_defaulting_rules.md#defaulting-policy) |
| HOLDS-IMPORT-CONTRACT | Key matching, field assignment, omission/null handling and updateability. | [Importer contract](../ora-resource/ora_dependency_readiness.md#importer-contract) |
| HOLDS-SERIALIZATION | CSV field representation, empty fields, staging limits and date conversion. | [Field validation](../ora-resource/ora_input_validation.md#field-validation) and [calendar dates](../ora-resource/ora_input_validation.md#calendar-dates) |
| HOLDS-CALENDAR-CONTRACT | Calendar-date input, representation and comparison. | [Calendar dates](../ora-resource/ora_input_validation.md#calendar-dates) |
| HOLDS-IMPORT-EFFECTS | Dependent values, supporting lookup maintenance and persisted-delete restrictions. | [Pre-import consistency](../ora-resource/ora_design_enforcement.md#pre-import-consistency-rules), [import processing](../ora-resource/ora_design_enforcement.md#import-processing) and [operation support](../ora-resource/ora_design_enforcement.md#operation-support) |
| HOLDS-INPUT-LABELS | Type labels and accepted flag inputs. | [Type labels](../ora-resource/ora_reference_lookups.md#type-labels) and [field validation](../ora-resource/ora_input_validation.md#field-validation) |
| HOLDS-UPDATE-POLICY | Existing-row restrictions and dependent-field eligibility. | [Update restrictions](../ora-resource/ora_design_enforcement.md#update-restrictions) |
| HOLDS-ACCOUNTING-EFFECTS | Accounting-event reevaluation and limits on reverse setup changes. | [Accounting effects](../ora-resource/ora_design_enforcement.md#accounting-effects) |
| HOLDS-ROUTING-OFF-CLEARS-DETAILS | Final routing N requires blank instruction and notification/reminder days. | [Pre-import consistency](../ora-resource/ora_design_enforcement.md#pre-import-consistency-rules) |
