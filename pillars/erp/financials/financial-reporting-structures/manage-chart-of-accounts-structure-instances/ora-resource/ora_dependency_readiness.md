# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | COA instance existence check | COAINS.READY requires the lookup inputs only; COAINS.LOOKUP requires a successful, complete find_chart_of_accounts result before FSM export or creation preparation. Confirmed absence permits the creation branch; obtain existing detail and StructureInstanceId only when one match is found. Referenced structure and value-set verification remain required before instance package generation. |
| 2 | Referenced value-set metadata | Resolve every inherited or override ValueSetCode and its compatible datatype and MaximumLength before instance package work |
| 3 | Referenced value-set datatype | When an instance segment default is supplied, resolve its value set and datatype before validating the default-value field |
| 4 | Segment sequences and values | Resolve every segment sequence and its associated values before Essbase member-ID conflict validation |
| 5 | Complete same-task FSM export | Export populated CSV data and ASM_SETUP_CSV_METADATA.xml after the absence decision; derive internal codes, CSV columns, XML values, and defaults |
| 6 | Template-only FSM export | Use only as a supplement when the complete export needs file-shape clarification |
| 7 | Data Loader import path | Submit the immutable FSM package only through core.data-loader after task validation, preview, and explicit approval |
| 8 | Oracle functional and EDM documentation | Resolve only documented defaults |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| existing_object | COA instance existence check | Yes | At COAINS.LOOKUP, before FSM export or creation preparation | Verify | Completed find_chart_of_accounts evidence; get_chart_of_accounts only when one unique match is found | find_chart_of_accounts, get_chart_of_accounts | Prevent duplicate creation without requiring the target instance to exist | A successful zero-match lookup permits creation preparation. Compare one match; stop on ambiguity or failed or incomplete evidence. Do not require StructureInstanceId or an existing-detail lookup for confirmed absence. | Absence outcome, or existing instance identity and detail when matched |
| referenced_value_sets | Referenced inherited or override value sets | Yes | Before FSM export, defaulting, or creating an instance or override row | Verify | GET valueSets for every inherited or override ValueSetCode | find_value_set | An instance package must use only verified structure-linked or override value sets | Stop if any value set is absent, incompatible, or ambiguous; do not generate the instance package | Existing ValueSetId, ValueSetCode, ValueDataType, ValueSubtype, MaximumLength, and flags |
| default_value_datatype_context | Referenced value-set datatype | Conditional | An instance segment default is supplied | Verify | GET valueSets or approved same-task export | find_value_set | The populated default-value field must match the referenced value-set datatype | Provide the referenced ValueSetCode and DefaultType with the proposed default | ValueSetCode, ValueDataType, DefaultType, DefaultValue, DefaultValueNumber |
| essbase_member_id_context | Segment sequences and associated values | Yes | Before declaring the structure instance cube-ready | Verify | Approved COA structure and requested or existing value-set values | compare_generated_member_ids | Prevent a value from colliding with a generated segment_sequence-value member ID | Provide or resolve every segment sequence and value used by the instance | Segment sequence, SegmentCode, ValueSetCode, Value |
| data_loader_import_path | Data Loader authorization | Yes | Before any live import | Ready | Approved immutable FSM ZIP and core.data-loader task-validation result |  | The FSM ZIP is package evidence only; it must not be submitted through a direct FSM import endpoint | Approve the exact package fingerprint and target environment | Approved source path, checksum, preview, and Data Loader handoff |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAINS.READY | step | 3 | resolve_dependency | ready->COAINS.LOOKUP | COAINS.VALIDATE | stop | Always |
