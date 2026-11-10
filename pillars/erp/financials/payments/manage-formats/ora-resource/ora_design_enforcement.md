# Manage Formats design enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_FORMAT::B2bDocDefinition, IBY_FORMAT::CodeMapGroupCode, IBY_FORMAT::EndDate, IBY_FORMAT::EndDateDsp, IBY_FORMAT::FormatCode, IBY_FORMAT::FormatName, IBY_FORMAT::FormatTemplateCode, IBY_FORMAT::FormatTypeCode, IBY_FORMAT::PayloadTypeCode, IBY_FORMAT::ReferenceFormatCode, IBY_FORMAT::SeededFlag, IBY_FORMAT::ShreddingHandledByParser, IBY_FORMAT::StartDate, IBY_FORMAT::TransformMethod, IBY_FORMAT::TransformProgramType, IBY_FORMAT::TransformSrvcInterfaceClass, IBY_FORMAT_TRANSLATION::FormatCode, IBY_FORMAT_TRANSLATION::FormatName, IBY_FORMAT_TRANSLATION::IBY_FORMAT.FormatCode, IBY_FORMAT_TRANSLATION::Language, IBY_FORMAT_TRANSLATION::SourceLang, ORA_IBY_VALIDATION_ASSIGN::AssignmentEntityId, ORA_IBY_VALIDATION_ASSIGN::EndDate, ORA_IBY_VALIDATION_ASSIGN::EndDateDisp, ORA_IBY_VALIDATION_ASSIGN::FieldNameCode, ORA_IBY_VALIDATION_ASSIGN::IBY_FORMAT.FormatCode, ORA_IBY_VALIDATION_ASSIGN::PaymentMethodCode, ORA_IBY_VALIDATION_ASSIGN::StartDate, ORA_IBY_VALIDATION_ASSIGN::TerritoryCode, ORA_IBY_VALIDATION_ASSIGN::ValAssignmentEntityType, ORA_IBY_VALIDATION_ASSIGN::ValidationSetCode, ORA_IBY_VALIDATION_VALUE::IBY_FORMAT.FormatCode, ORA_IBY_VALIDATION_VALUE::ORA_IBY_VALIDATION_ASSIGN.AssignmentEntityId, ORA_IBY_VALIDATION_VALUE::ORA_IBY_VALIDATION_ASSIGN.FieldNameCode, ORA_IBY_VALIDATION_VALUE::ORA_IBY_VALIDATION_ASSIGN.ValAssignmentEntityType, ORA_IBY_VALIDATION_VALUE::ORA_IBY_VALIDATION_ASSIGN.ValidationSetCode, ORA_IBY_VALIDATION_VALUE::ValParamDateValue, ORA_IBY_VALIDATION_VALUE::ValParamNumberValue, ORA_IBY_VALIDATION_VALUE::ValParamVarchar2Value, ORA_IBY_VALIDATION_VALUE::ValidationParameterCode, ORA_IBY_VALIDATION_VALUE::ValidationSetCode -->
<!-- fscr-update-fields: IBY_FORMAT::B2bDocDefinition, IBY_FORMAT::CodeMapGroupCode, IBY_FORMAT::EndDate, IBY_FORMAT::EndDateDsp, IBY_FORMAT::FormatName, IBY_FORMAT::FormatTemplateCode, IBY_FORMAT::PayloadTypeCode, IBY_FORMAT::ReferenceFormatCode, IBY_FORMAT::ShreddingHandledByParser, IBY_FORMAT::StartDate, IBY_FORMAT::TransformMethod, IBY_FORMAT::TransformProgramType, IBY_FORMAT::TransformSrvcInterfaceClass, IBY_FORMAT_TRANSLATION::FormatName, IBY_FORMAT_TRANSLATION::SourceLang, ORA_IBY_VALIDATION_ASSIGN::EndDate, ORA_IBY_VALIDATION_ASSIGN::EndDateDisp, ORA_IBY_VALIDATION_ASSIGN::PaymentMethodCode, ORA_IBY_VALIDATION_ASSIGN::StartDate, ORA_IBY_VALIDATION_ASSIGN::TerritoryCode, ORA_IBY_VALIDATION_VALUE::ValParamDateValue, ORA_IBY_VALIDATION_VALUE::ValParamNumberValue, ORA_IBY_VALIDATION_VALUE::ValParamVarchar2Value -->


Source-backed static guidance; live qualification remains separate.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Identity and scope | Exact customer-owned FormatCode, operation and four-entity ownership |
| 2 | Known product constraints | Apply field dispositions, lengths, dates and validated references |
| 3 | Preview and approval | Run Book owns orchestration; Data Loader owns immutable package preview and approval |
| 4 | Completion | Fresh export reconciliation, manual attachment evidence and representative runtime verification |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| All mutations | Error |  | Missing exact identity, privilege, current candidate approval or known-valid constraints | Stop before Data Loader submission | No automatic repair |
| Seeded format or key rename | Error |  | SeededFlag Y or changing existing portable identity | Choose customer-owned exact target; no seed promotion or rename | No |
| Direct upload format | Error |  | No proven template attachment or unqualified deferred-attachment create route | Use UI create/upload until deferred attachment is live-proven; never claim metadata-only completion | Manual action |
| Unresolved eligible business field | Review |  | No recorded field/candidate application-validation decision | Use current central governed validation contract; ordinary approval still required | Only with explicit reviewed choice |
| Template assistance disabled/unavailable/failed | Information |  | Required template remains missing | Continue guided manual preparation; preserve artifacts and error; parent remains In Progress | Manual action |

## Template activity completion contract

The optional generate-oracle-payments-templates router is a child activity, not an FSM task. Generated, guided-manual and disabled are assistance modes. Core format matching, package preparation, import and reconciliation do not invoke the generator. Record format code/type, route, template identity, specification/source hashes, artifact hash, offline-validation status, attachment evidence, runtime evidence and next action in the existing project blueprint/validation outputs. The child cannot publish, attach, import, approve or complete the parent. Missing engines or unsupported routes return a discovery/manual handoff.

Direct customer templates consume TemplateDocument; this BLOB is absent from the CSV contract (SRC-FIELD-FORMAT-VO, SRC-FIELD-FORMAT-EO, SRC-FOLLOW-LOCAL-TEMPLATE). No dummy template or inferred fallback. A validated XSLT may be handed off as XML only with identical bytes/hash and validated filename constraints. BI Publisher requires selection of the exact template under the type-specific report. Template generation, offline validation, attachment and representative runtime verification are distinct outcomes.

Physical deletion has no established FSM contract. End-date is an update. A successful import is an attempt until exact-key persisted-state reconciliation and business completion evidence succeed. Preserve all unrelated fields and child rows during updates; no blank-to-clear assumptions.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FMT-DESIGN | step | 50 | design_enforcement | pass->FMT-GATE;missing->FMT-MISSING;invalid->FMT-ERROR | FMT-DEFAULTS | stop | Before preview and any handoff |


## Candidate artifact delivery

A generated draft may be delivered as a registered project file with mapping assumptions, validation results and implementation-test instructions before template installation or task completion. A draft is not dummy content: supported transformation logic is implemented and its limits are explicit. A direct-upload XML copy, including a test candidate, must preserve the exact XSLT bytes/hash and route-specific filename rules. Resolve exact target type and attachment mechanism before user-controlled installation/testing. Keep Manage Formats In Progress until required attachment, mapping resolution and representative runtime evidence are established.
