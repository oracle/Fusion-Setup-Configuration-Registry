# Design Enforcement

Task scope: AP_MANAGE_AGING_PERIODS / Manage Aging Periods. Use a fresh exact-task export to match existing records. Run Book supplies inputs. Create and update are supported. Submit the validated package through Data Loader after its required approval.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_AGING_PERIOD::Attribute1, AP_AGING_PERIOD::Attribute10, AP_AGING_PERIOD::Attribute11, AP_AGING_PERIOD::Attribute12, AP_AGING_PERIOD::Attribute13, AP_AGING_PERIOD::Attribute14, AP_AGING_PERIOD::Attribute15, AP_AGING_PERIOD::Attribute2, AP_AGING_PERIOD::Attribute3, AP_AGING_PERIOD::Attribute4, AP_AGING_PERIOD::Attribute5, AP_AGING_PERIOD::Attribute6, AP_AGING_PERIOD::Attribute7, AP_AGING_PERIOD::Attribute8, AP_AGING_PERIOD::Attribute9, AP_AGING_PERIOD::AttributeCategory, AP_AGING_PERIOD::Description, AP_AGING_PERIOD::PeriodName, AP_AGING_PERIOD::Status, AP_AGING_PERIOD_LINE::AP_AGING_PERIOD.PeriodName, AP_AGING_PERIOD_LINE::Attribute1, AP_AGING_PERIOD_LINE::Attribute10, AP_AGING_PERIOD_LINE::Attribute11, AP_AGING_PERIOD_LINE::Attribute12, AP_AGING_PERIOD_LINE::Attribute13, AP_AGING_PERIOD_LINE::Attribute14, AP_AGING_PERIOD_LINE::Attribute15, AP_AGING_PERIOD_LINE::Attribute2, AP_AGING_PERIOD_LINE::Attribute3, AP_AGING_PERIOD_LINE::Attribute4, AP_AGING_PERIOD_LINE::Attribute5, AP_AGING_PERIOD_LINE::Attribute6, AP_AGING_PERIOD_LINE::Attribute7, AP_AGING_PERIOD_LINE::Attribute8, AP_AGING_PERIOD_LINE::Attribute9, AP_AGING_PERIOD_LINE::AttributeCategory, AP_AGING_PERIOD_LINE::DaysStart, AP_AGING_PERIOD_LINE::DaysTo, AP_AGING_PERIOD_LINE::PeriodSequenceNum, AP_AGING_PERIOD_LINE::ReportHeading1, AP_AGING_PERIOD_LINE::ReportHeading2, AP_AGING_PERIOD_LINE::ReportHeading3 -->
<!-- fscr-update-fields: AP_AGING_PERIOD::Attribute1, AP_AGING_PERIOD::Attribute10, AP_AGING_PERIOD::Attribute11, AP_AGING_PERIOD::Attribute12, AP_AGING_PERIOD::Attribute13, AP_AGING_PERIOD::Attribute14, AP_AGING_PERIOD::Attribute15, AP_AGING_PERIOD::Attribute2, AP_AGING_PERIOD::Attribute3, AP_AGING_PERIOD::Attribute4, AP_AGING_PERIOD::Attribute5, AP_AGING_PERIOD::Attribute6, AP_AGING_PERIOD::Attribute7, AP_AGING_PERIOD::Attribute8, AP_AGING_PERIOD::Attribute9, AP_AGING_PERIOD::AttributeCategory, AP_AGING_PERIOD::Description, AP_AGING_PERIOD::Status, AP_AGING_PERIOD_LINE::Attribute1, AP_AGING_PERIOD_LINE::Attribute10, AP_AGING_PERIOD_LINE::Attribute11, AP_AGING_PERIOD_LINE::Attribute12, AP_AGING_PERIOD_LINE::Attribute13, AP_AGING_PERIOD_LINE::Attribute14, AP_AGING_PERIOD_LINE::Attribute15, AP_AGING_PERIOD_LINE::Attribute2, AP_AGING_PERIOD_LINE::Attribute3, AP_AGING_PERIOD_LINE::Attribute4, AP_AGING_PERIOD_LINE::Attribute5, AP_AGING_PERIOD_LINE::Attribute6, AP_AGING_PERIOD_LINE::Attribute7, AP_AGING_PERIOD_LINE::Attribute8, AP_AGING_PERIOD_LINE::Attribute9, AP_AGING_PERIOD_LINE::AttributeCategory, AP_AGING_PERIOD_LINE::DaysStart, AP_AGING_PERIOD_LINE::DaysTo, AP_AGING_PERIOD_LINE::ReportHeading1, AP_AGING_PERIOD_LINE::ReportHeading2, AP_AGING_PERIOD_LINE::ReportHeading3 -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Interval | Apply source compare validation |
| 2 | Active header | Check resulting parent/child state |
| 3 | Identity and sequence | Match exact keys; require sequence uniqueness within each aging period |
| 4 | Detail count | Limit the resulting header to four detail lines |
| 5 | Validation responsibilities | Validate local field rules; leave configured flexfield values to FSM |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| line create or update | Error |  | DaysStart exceeds DaysTo; AP_IAP_WRONG_DAYS | Supply From <= To; evaluate complete resulting line using baseline values | No silent swap |
| Status A | Error |  | Resulting header has no detail lines; AP_ACTIVE_INVALID | Supply at least one explicit detail line | No automatic child creation |
| Detail create or update | Error |  | Duplicate PeriodName and PeriodSequenceNum pair, including an existing pair requested as a create | Use a unique sequence within the parent period; updates must match one existing line | No automatic renumbering |
| Existing portable identity | Error |  | Rename PeriodName or change existing PeriodSequenceNum | Preserve exact keys; request separately evidenced lifecycle behavior | No |
| DFF field requested | Information |  | No configured-domain preflight block; FSM validates submitted context/segment/value rules | Preserve user-supplied values; retain known scalar/length/package controls and normal preview/approval | No invented, truncated or defaulted values |
| Header or detail create/update | Error |  | Resulting header would have more than four detail lines | Limit resulting details to four per header; count baseline plus requested new lines, not just candidate rows | No silent removal; delete is not allowed |

## Validation Responsibilities

| Validation | Responsibility | Behavior |
|---|---|---|
| DFF context, segments and values | FSM | Submit supplied values unchanged. Local checks cover storage type, known length and package integrity; FSM validates configured definitions. |
| Active status | Task validation | Accept A for checked Active and I for unchecked Active; no lookup is required. |
| Detail Type | Fusion | Fusion calculates and persists Type when saving the line. Leave Type blank for creates and preserve the export value for updates; verify the calculated value after import. |

## Service Boundary

| Situation | Disposition |
| --- | --- |
| UI four-line limit | FSCR enforces at most four detail lines per header, aligned with UI AP-810439; this is a local validation policy, not a claim of FSM enforcement |
| Export completeness | Verify all requested and retained lines in the current export; do not infer an import limit from export results |
| Delete or end-date | Task scope permits create and update only; delete and a separate end-date action are outside the supported create/update scope. Other service capabilities do not change this task scope |
| Undocumented import behavior | Do not infer extra defaults, mutations or supported operations |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AGING.DESIGN | decision | 50 | design_enforcement | pass->AGING.RETURN_READY;blocked->AGING.RETURN_ISSUES | AGING.DEPENDENCY | stop | create or update |

## Supporting Parent Preservation

For every child create or update, include its matching parent header in the
same FSM archive. Unless an explicit parent operation supplies it, copy the
header unchanged from the fresh current-data baseline, blank all audit fields,
and include it once per parent. Block when neither the baseline
nor explicit operations supplies the parent. Validation rejects missing parents,
changed supporting business values, and populated supporting audit fields.
Other existing child rows do not need to be copied into the candidate.

## Metadata Object Identity

Identify AP_AGING_PERIOD and AP_AGING_PERIOD_LINE by their exact business object
names and declared XML node paths. Their paths form a linear parent/child
hierarchy at distinct levels. Successful same-environment exports have shown
both parent/child NodeSequence profiles 1/2 and 2/1. These numbers do not establish
object identity or require parent-before-child numeric ordering.

The task's metadataIdentityPolicy permits positive package-local sequence
values for this distinct-level linear hierarchy. Keep exact task, object
inventory, paths, CSV members/headers/types, target, release compatibility and
parent/child relationship checks. Reject missing/duplicate/unexpected objects,
changed paths, malformed sequences and ambiguous/same-level hierarchy changes.
Do not infer XML-file groups from CSV names or XML path roots; a future branching
hierarchy requires separately reviewed sequencing support.

Preserve source archives and metadata bytes unchanged. Candidate metadata comes
from the current-data baseline; template and independent readback sequences may
differ while their object/path/header/type schema remains compatible. The initial
descriptor nodeSequence values retain historical provenance, not fixed identity.
