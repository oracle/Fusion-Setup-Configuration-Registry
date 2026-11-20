# Input Validation

Task scope: AP_MANAGE_AGING_PERIODS / Manage Aging Periods. Use a fresh exact-task export to match existing records. Run Book supplies inputs. Create and update are supported. Submit the validated package through Data Loader after its required approval.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_AGING_PERIOD::Attribute1, AP_AGING_PERIOD::Attribute10, AP_AGING_PERIOD::Attribute11, AP_AGING_PERIOD::Attribute12, AP_AGING_PERIOD::Attribute13, AP_AGING_PERIOD::Attribute14, AP_AGING_PERIOD::Attribute15, AP_AGING_PERIOD::Attribute2, AP_AGING_PERIOD::Attribute3, AP_AGING_PERIOD::Attribute4, AP_AGING_PERIOD::Attribute5, AP_AGING_PERIOD::Attribute6, AP_AGING_PERIOD::Attribute7, AP_AGING_PERIOD::Attribute8, AP_AGING_PERIOD::Attribute9, AP_AGING_PERIOD::AttributeCategory, AP_AGING_PERIOD::Description, AP_AGING_PERIOD::PeriodName, AP_AGING_PERIOD::Status, AP_AGING_PERIOD_LINE::AP_AGING_PERIOD.PeriodName, AP_AGING_PERIOD_LINE::Attribute1, AP_AGING_PERIOD_LINE::Attribute10, AP_AGING_PERIOD_LINE::Attribute11, AP_AGING_PERIOD_LINE::Attribute12, AP_AGING_PERIOD_LINE::Attribute13, AP_AGING_PERIOD_LINE::Attribute14, AP_AGING_PERIOD_LINE::Attribute15, AP_AGING_PERIOD_LINE::Attribute2, AP_AGING_PERIOD_LINE::Attribute3, AP_AGING_PERIOD_LINE::Attribute4, AP_AGING_PERIOD_LINE::Attribute5, AP_AGING_PERIOD_LINE::Attribute6, AP_AGING_PERIOD_LINE::Attribute7, AP_AGING_PERIOD_LINE::Attribute8, AP_AGING_PERIOD_LINE::Attribute9, AP_AGING_PERIOD_LINE::AttributeCategory, AP_AGING_PERIOD_LINE::DaysStart, AP_AGING_PERIOD_LINE::DaysTo, AP_AGING_PERIOD_LINE::PeriodSequenceNum, AP_AGING_PERIOD_LINE::ReportHeading1, AP_AGING_PERIOD_LINE::ReportHeading2, AP_AGING_PERIOD_LINE::ReportHeading3 -->
<!-- fscr-update-fields: AP_AGING_PERIOD::Attribute1, AP_AGING_PERIOD::Attribute10, AP_AGING_PERIOD::Attribute11, AP_AGING_PERIOD::Attribute12, AP_AGING_PERIOD::Attribute13, AP_AGING_PERIOD::Attribute14, AP_AGING_PERIOD::Attribute15, AP_AGING_PERIOD::Attribute2, AP_AGING_PERIOD::Attribute3, AP_AGING_PERIOD::Attribute4, AP_AGING_PERIOD::Attribute5, AP_AGING_PERIOD::Attribute6, AP_AGING_PERIOD::Attribute7, AP_AGING_PERIOD::Attribute8, AP_AGING_PERIOD::Attribute9, AP_AGING_PERIOD::AttributeCategory, AP_AGING_PERIOD::Description, AP_AGING_PERIOD::Status, AP_AGING_PERIOD_LINE::Attribute1, AP_AGING_PERIOD_LINE::Attribute10, AP_AGING_PERIOD_LINE::Attribute11, AP_AGING_PERIOD_LINE::Attribute12, AP_AGING_PERIOD_LINE::Attribute13, AP_AGING_PERIOD_LINE::Attribute14, AP_AGING_PERIOD_LINE::Attribute15, AP_AGING_PERIOD_LINE::Attribute2, AP_AGING_PERIOD_LINE::Attribute3, AP_AGING_PERIOD_LINE::Attribute4, AP_AGING_PERIOD_LINE::Attribute5, AP_AGING_PERIOD_LINE::Attribute6, AP_AGING_PERIOD_LINE::Attribute7, AP_AGING_PERIOD_LINE::Attribute8, AP_AGING_PERIOD_LINE::Attribute9, AP_AGING_PERIOD_LINE::AttributeCategory, AP_AGING_PERIOD_LINE::DaysStart, AP_AGING_PERIOD_LINE::DaysTo, AP_AGING_PERIOD_LINE::ReportHeading1, AP_AGING_PERIOD_LINE::ReportHeading2, AP_AGING_PERIOD_LINE::ReportHeading3 -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Header identity | AP_AGING_PERIOD.PeriodName | Stop affected operation | Provide exact portable name; no numeric surrogate | create or update |  |
| Line identity | AP_AGING_PERIOD.PeriodName and PeriodSequenceNum | Stop unless eligible for new-parent order assignment | For a new parent with all orders omitted, assign listed order 1, 2, 3… and show preview. Otherwise provide exact parent name and integer order | line create or update |  |
| Required line inputs | DaysStart, DaysTo, ReportHeading1 | Stop affected create | Provide both integer limits and first heading | line create |  |
| Required line values on update | DaysStart, DaysTo, ReportHeading1 | Stop the affected update when a supplied value is blank | Omit a value to preserve the export; provide a nonblank replacement to change it | line update |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Exact metadata | Reject wrong task/member/header/types and every CSV row/header count mismatch; preserve metadata bytes and explicit trailing blanks | all packages |  |
| Per-field contracts | Accept only supported fields for the operation; key changes and audit edits are prohibited; unresolved is distinct from unsupported | create or update |  |
| Scalar type and precision | Reject malformed or structured scalar inputs and overlength values without truncation; apply source field precision | create or update |  |
| Status domain | Fixed domain A (Active checked) / I (Active unchecked); literal value validation and canonical label mapping, no lookup | Status supplied |  |
| Unique sequence within an aging period | Each detail line must have a unique PeriodSequenceNum within its parent PeriodName. Reject duplicate parent-name/sequence pairs in the package and a create that reuses an existing pair. An update must match exactly one existing line. The same sequence number is allowed under different aging periods. | detail create or update |  |
| Day range | Require DaysStart <= DaysTo for each resulting line; no additional continuity rule between lines. Validation issues identify the aging period and detail order. | detail create or update |  |
| Required children on create | New Status A headers, including the defaulted status, require at least one explicitly requested detail in the candidate; new Status I headers have no minimum detail requirement (zero is allowed). A detail create has no children of its own. Never invent details to satisfy this rule | header or detail create |  |
| Existing children on update | Validate the resulting header independently: Status A requires at least one resulting detail, counting retained fresh-baseline details plus requested creates; Status I imposes no minimum detail count. Do not require a new detail or resubmission of existing details solely because the header is updated. Preserve omitted children; omission does not delete them | header update |  |
| Detail count | Maximum four resulting lines per aging period, counting existing baseline lines plus requested creates | header or detail create/update |  |
| Parent identity | Match the exact existing parent or an explicitly requested parent create in the same package | detail create or update |  |
| Service-calculated Type | If Type is supplied, allow only PAST or CURRENT; raise a validation issue for any other value. Type remains service-owned and is not independently editable. Leave it blank for creates; preserve the exported value for updates. Fusion calculates the stored value; verify it after import | detail create or update |  |
| DFF values | Preserve supplied values; validate storage type and known length locally; FSM validates configured context/segment/value rules | DFF field supplied |  |
| Unique aging period name | Reject duplicate PeriodName rows and a create that reuses an existing exact name; an update must match exactly one existing header | header create or update |  |
| Preserve untargeted data | Preserve existing keys, non-requested values and unrelated records. Fusion may recalculate Type on a targeted line; verify that result separately | create or update |  |
| Already satisfied updates | For a valid request, when every requested update value already matches the current export, return a no-change result and do not generate another import package | update only |  |

## Field Contracts

Fields are grouped by header and detail table. Create and update permissions apply to each listed field. Preserve existing matching keys, omitted update values and unrelated records.

For flexfields on either table, preserve supplied values unchanged and apply the stated string-length limits. FSM validates configured contexts, segments and values. Whether a configured segment is mandatory is determined by its deployed definition.

### Aging Period Header — `AP_AGING_PERIOD`

#### Setup fields

| Field | Type | Create | Update | Constraints | Requiredness / behavior |
|---|---|---|---|---|---|
| PeriodName | string | supported | unsupported | Maximum 50 characters | Required on create; existing name cannot be changed. |
| Description | string | supported | supported | Maximum 240 characters | Optional; omitted updates preserve current description. |
| Status | string | supported | supported | A (Active) or I (Inactive); maximum 25 storage characters | Omitted create defaults to A; omitted updates preserve current status. |

#### Descriptive flexfields

| Fields | Type | Create | Update | Constraints | Behavior |
|---|---|---|---|---|---|
| AttributeCategory | string | supported | supported | Maximum 150 characters per field | Preserve supplied values; FSM validates the configured context. Omitted updates preserve existing values. |
| Attribute1–Attribute15 | string | supported | supported | Maximum 150 characters per field | Preserve supplied values; FSM validates the configured segments and values. Omitted updates preserve existing values. |

#### System-managed audit fields

These fields are read-only and must not be supplied or changed by the user.

| Field | Type | Create | Update | Constraints |
|---|---|---|---|---|
| LastUpdatedBy | string | unsupported | unsupported | System-managed; maximum 64 storage characters |
| LastUpdateDate | dateTime | unsupported | unsupported | System-managed timestamp |
| CreatedBy | string | unsupported | unsupported | System-managed; maximum 64 storage characters |
| CreationDate | dateTime | unsupported | unsupported | System-managed timestamp |
| LastUpdateLogin | string | unsupported | unsupported | System-managed; maximum 32 storage characters |

### Aging Period Details — `AP_AGING_PERIOD_LINE`

#### Setup fields

| Field | Type | Create | Update | Constraints | Requiredness / behavior |
|---|---|---|---|---|---|
| PeriodSequenceNum | int | supported | unsupported | Integer; unique within the parent aging period | Required in the normalized package. For a new parent with all orders omitted, assign listed order 1, 2, 3… and show preview. Preserve explicit numbers; mixed supplied/omitted orders require clarification. Existing parents require explicit order; existing sequence cannot change. Different parents may reuse a sequence. |
| DaysStart | int | supported | supported | Integer; DaysStart ≤ DaysTo | Required on create; omitted updates preserve the existing From value. A supplied blank on update is rejected. |
| DaysTo | int | supported | supported | Integer; DaysTo ≥ DaysStart | Required on create; omitted updates preserve the existing To value. A supplied blank on update is rejected. |
| Type | string | unsupported | unsupported | PAST or CURRENT; maximum 25 storage characters | Fusion calculates the value. Create cell is blank; update cell preserves the export value. Independent Type changes are unsupported. |
| ReportHeading1 | string | supported | supported | Maximum 15 characters | Required on create; omitted updates preserve the first heading. A supplied blank on update is rejected. |
| ReportHeading2 | string | supported | supported | Maximum 15 characters | Optional; omitted updates preserve the existing heading. |
| ReportHeading3 | string | supported | supported | Maximum 15 characters | Optional; omitted updates preserve the existing heading. |
| AP_AGING_PERIOD.PeriodName | string | supported | unsupported | Same 50-character limit as header PeriodName | Required child parent link; match the exact parent name and preserve it on updates. |

#### Descriptive flexfields

| Fields | Type | Create | Update | Constraints | Behavior |
|---|---|---|---|---|---|
| AttributeCategory | string | supported | supported | Maximum 150 characters per field | Preserve supplied values; FSM validates the configured context. Omitted updates preserve existing values. |
| Attribute1–Attribute15 | string | supported | supported | Maximum 150 characters per field | Preserve supplied values; FSM validates the configured segments and values. Omitted updates preserve existing values. |

#### System-managed audit fields

These fields are read-only and must not be supplied or changed by the user.

| Field | Type | Create | Update | Constraints |
|---|---|---|---|---|
| LastUpdatedBy | string | unsupported | unsupported | System-managed; maximum 64 storage characters |
| LastUpdateDate | dateTime | unsupported | unsupported | System-managed timestamp |
| CreatedBy | string | unsupported | unsupported | System-managed; maximum 64 storage characters |
| CreationDate | dateTime | unsupported | unsupported | System-managed timestamp |
| LastUpdateLogin | string | unsupported | unsupported | System-managed; maximum 32 storage characters |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AGING.INPUT | decision | 10 | validate_input | pass->AGING.DEFAULTS;invalid->AGING.RETURN_ISSUES | none | stop | create or update |

## Supporting Parent Validation

For every child create or update, include its matching parent header in the
same FSM archive. Unless an explicit parent operation supplies it, copy the
header unchanged from the fresh current-data baseline, blank all audit fields,
and include it once per parent. Block when neither the baseline
nor explicit operations supplies the parent. Validation rejects missing parents,
changed supporting business values, and populated supporting audit fields.
Other existing child rows do not need to be copied into the candidate.
