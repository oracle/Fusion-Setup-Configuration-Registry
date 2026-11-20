# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Referenced value-set metadata | For every requested segment, resolve an explicit ValueSetCode or SegmentCode_VS lookup candidate and verify compatible format and MaximumLength before structure package work |
| 2 | Chart of Accounts existence check | Require a successful, complete find_chart_of_accounts result before FSM export or creation preparation. Confirmed absence permits the creation branch; obtain existing detail only when one match is found. |
| 3 | Qualified segment-label metadata | Resolve every assigned label and confirm it is nonglobal and permitted for COA segments |
| 4 | Segment tree metadata | When a default hierarchy is requested, verify the GL_ACCT_FLEX tree against the verified segment value set |
| 5 | Complete same-task FSM export | Export populated CSV data and ASM_SETUP_CSV_METADATA.xml after the absence decision; derive internal codes, CSV columns, XML values, and defaults |
| 6 | Template-only FSM export | Use only as a supplement when the complete export needs file-shape clarification |
| 7 | Data Loader import path | Submit the immutable FSM package only through core.data-loader after task validation, preview, and explicit approval |
| 8 | Oracle functional and EDM documentation | Resolve only documented defaults |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| existing_object | Chart of accounts existence check | Yes | At COASTR.LOOKUP, before FSM export or creation preparation | Verify | Completed find_chart_of_accounts evidence | find_chart_of_accounts | Apply the task's Name-or-StructureInstanceCode existence policy | A successful zero-match lookup permits creation preparation; one match requires comparison. No independent StructureCode existence check is required. Failed, incomplete, or ambiguous evidence blocks progress. | Scoped absence outcome, or existing identity for conditional detail lookup |
| existing_object_detail | Existing chart of accounts detail | Conditional | find_chart_of_accounts returns one unique match | Verify | Completed get_chart_of_accounts evidence | get_chart_of_accounts | Compare the existing definition before deciding the next action | Do not request existing detail or StructureInstanceId when the existence check confirms absence. | Existing COA identity and comparable detail |
| referenced_value_sets | Referenced segment value sets | Yes | Before FSM export, defaulting DefaultValueSetCode, or creating structure rows | Verify | Completed find_value_set evidence for every requested segment | find_value_set | A structure package must contain only verified compatible value-set references | Require the resolver's unique compatible code-match result before structure package generation. Missing ValueSetId alone is not a blocker; unresolved, ambiguous, incompatible, or incomplete reference evidence still blocks. | Verified ValueSetCode, ValidationType, ValueDataType, ValueSubtype, MaximumLength, and flags; optional ValueSetId only when returned |
| qualified_segment_labels | COA-qualified segment labels | Conditional | One or more SegmentLabelCode values are assigned | Verify | Complete same-task segment-label export and qualified KFF label metadata | resolve_segment_label_code | Only nonglobal labels other than GL_GLOBAL can be assigned to COA segments | Provide the business classification or internal SegmentLabelCode for every assignment | SegmentLabelCode, GlobalFlag, allowed-domain result |
| segment_tree_context | Segment default hierarchy | Conditional | TreeCode or TreeStructureCode is supplied | Verify | FND_TREE_VL and value-set-filtered tree metadata | verify_segment_tree | The default hierarchy must use GL_ACCT_FLEX and belong to the segment value set | Provide TreeCode, TreeStructureCode, and DefaultValueSetCode | TreeCode, TreeStructureCode, DefaultValueSetCode, tree match |
| data_loader_import_path | Data Loader authorization | Yes | Before any live import | Ready | Approved immutable FSM ZIP and core.data-loader task-validation result |  | The FSM ZIP is package evidence only; it must not be submitted through a direct FSM import endpoint | Approve the exact package fingerprint and target environment | Approved source path, checksum, preview, and Data Loader handoff |

## Readiness Handoff

COASTR.READY checks that the existence-check inputs are available; it does not require an existing COA or a prior COA lookup result. COASTR.LOOKUP uses Name or StructureInstanceCode as sufficient existence evidence under the task policy and follows its absent or match transition; a separate StructureCode existence check is not a gate. StructureCode and its mapping remain package-reference fields. Later package readiness still requires the applicable value-set, label, tree, export, validation, and approval evidence.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COASTR.READY | step | 3 | resolve_dependency | ready->COASTR.LOOKUP | COASTR.VALIDATE | stop | Always |
