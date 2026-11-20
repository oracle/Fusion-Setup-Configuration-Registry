# Defaulting Rules

## Standard Defaults

| Field | Internal | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|
| SegmentNDescription | No | Human-readable sentence-case form of the corresponding SegmentN value | The labelled segment value is confirmed absent from its resolved value set and its description is blank | No | resolve_location_segment_values |
| StructureInstanceCode / underlying STRUCTURE_INSTANCE_NUMBER | Yes | Preserve the System Controls-selected LocStructureInstanceCode in the FSM contract's StructureInstanceCode field. Fusion resolves the underlying number; never derive it from optional StructureInstanceIdentifier. Require a verified numeric source only for a contract that requires the number. | New Asset Location | No | resolve_location_system_control |
| SUMMARY_FLAG | No | N | New Asset Location | No | |
| EnabledFlag for Asset Location | No | Preserve supplied Yes/Y as Y or No/N as N; obtain the choice when omitted for create, and preserve existing state for an explicitly selected update | Create or update Asset Location | No | |
| StartDateActive / EndDateActive | No | Blank on create when omitted; preserve existing dates for an explicitly selected update unless a change or clearing is requested | Create or update Asset Location | No | |
| OBJECT_VERSION_NUMBER | Yes | 1 | Insert | No | |
| Audit columns | Yes | Fusion audit framework values | Insert or update | No | |
| ENABLED_FLAG for mapping | No | Accept `Y`/`N` or `YES`/`NO` case-insensitively. Translate affirmative input to uppercase `Y` and negative input to uppercase `N`; reject unrecognized values. Default to `Y` when omitted. | Rapid Start mapping import | No | |
| LOCATION_MAPPING_TYPE_CODE | Yes | ORA_FA_HR_LOCATION | Mapping import with a blank Customer Site Number | No | |
| FA_LOCATION_ID | Yes | Resolved from Asset Location segments | Rapid Start mapping import | No | resolve_existing_asset_location |
| SOURCE_LOCATION_ID | Yes | Resolved from HR Location Code plus HR Set Code | HR mapping import with a blank Customer Site Number | No | resolve_hr_location_reference |

## Default Safety Rules

| Situation | What Happens |
|---|---|
| Structure metadata or a segment default is needed | Resolve it from the target environment's active LOC# structure. Do not use a checked-in structure code, delimiter, or segment value as a default. |
| Enabled was omitted for a new Asset Location | Obtain the desired enabled state before artifact creation; do not infer an undefined runtime default. |
| A Create request matches an existing exact Asset Location | Do not default, preserve, or alter EnabledFlag, StartDateActive, or EndDateActive. Stop for an explicit update-versus-new decision. |
| User supplies an Enabled value in the mapping worksheet | Apply the documented import conversion; do not silently substitute another business value. |
| Customer Site Number is supplied | Block the row. Do not default `LOCATION_MAPPING_TYPE_CODE` or `SOURCE_LOCATION_ID` until an approved customer-site resolver contract exists. |
| An existing mapping is found | Stop. Mapping maintenance is unsupported; do not apply create-oriented mapping defaults or synthesize an update identity. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---:|---:|---|---|---|---|---|
| MAL.APPLY_DEFAULTS | step | 40 | apply_default | applied->MAL.ENFORCE_DESIGN | MAL.RESOLVE_OPERATION | stop | Resolved records contain defaultable technical or import fields. |
