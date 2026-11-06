# Transportation Schedules Input Validation

Source: user-approved registered-BO/Data Loader operation contract. The Business Object owns all value and key resolution.

## Operation Attribute Contract

| Operation | Scope | Attributes to pass | Key-resolution rule |
|---|---|---|---|
| POST | Parent transportation schedule | Parent business attributes: `TradingPartnerTypeCode`, `TradingPartnerName`, `ScheduleUsageCode`, `ScheduleName`, `CarrierName`, and `EnabledFlag` when supplied. | BO resolves all backing values and creates the parent assignment. |
| POST | Child site schedule | User input: `TradingPartnerSite`, `ScheduleName`, and `EnabledFlag`; parent business values are supplied at operation scope. | BO/Data Loader resolves `TransportationScheduleAssignmentId` from the parent business values and carries it internally for the child route. Do not require a user-supplied `TransportationScheduleAssignmentId` or pass `SiteScheduleAssignmentId`. |
| PATCH | Parent transportation schedule | The parent business key and changed parent attributes. | BO resolves `TransportationScheduleAssignmentId`; do not supply or derive it locally. |
| DELETE | Parent transportation schedule | The parent business key only. | BO resolves `TransportationScheduleAssignmentId`; do not supply or derive it locally. |
| PATCH | Child site schedule | Complete parent business key, child business key, and changed child attributes. | BO resolves both `TransportationScheduleAssignmentId` and `SiteScheduleAssignmentId`, then uses the resolved parent ID to address the nested child route. Do not supply or derive either ID locally. |
| DELETE | Child site schedule | Complete parent business key and child business key. | BO resolves both `TransportationScheduleAssignmentId` and `SiteScheduleAssignmentId`, then uses the resolved parent ID to address the nested child route. Do not supply or derive either ID locally. |

## Input Rules

| Check | What happens |
|---|---|
| Parent POST payload | Require `TradingPartnerTypeCode`, `TradingPartnerName`, `ScheduleUsageCode`, `ScheduleName`, `CarrierName` when applicable, and `EnabledFlag` when supplied. The BO resolves all backing values; no technical ID is accepted. |
| Child POST payload | Require `TradingPartnerSite`, `ScheduleName`, and `EnabledFlag` with a complete parent business key in the operation context. The nested child REST body contains only those three child attributes. BO/Data Loader resolves the required parent route key internally. Reject supplied parent or child surrogate IDs. |
| Parent PATCH or DELETE payload | Reject a locally supplied `TransportationScheduleAssignmentId`; retain the parent business key for BO resolution. |
| Child PATCH or DELETE payload | Require the complete parent business key and child business key. BO/Data Loader resolves both route IDs; the resolved parent ID is used in the child route. Reject locally supplied surrogate IDs. |
| Schedule name | Accept the exact UI LOV display value, including capitalization. For parent operations the BO resolves `ScheduleName` to `ScheduleId`; do not submit a locally resolved `ScheduleId`. |
| Status input | Accept `enabled`, `disabled`, `Y`, or `N`; emit `EnabledFlag` as `Y` or `N`. |
| DFF values | Exclude root and child DFF values until an explicit DFF request supplies the configured segment contract. |

Fusion, the registered BO, and Data Loader own LOV matching, key resolution, required-field enforcement, uniqueness, server-side domains, and final payload validation.

## Control And Route Normalization

| UI Label and Control | Implementation Field | Scope | Accepted Friendly Values | Data Loader Output | Disposition |
|---|---|---|---|---|---|
| Status switch | EnabledFlag | Parent and child | enabled, disabled, Y, N | Y or N | Route-aware normalization |
| Trading Partner Site select | TradingPartnerSite | Child operations | Exact UI value | BO-owned lookup input | BO-owned resolution |
| Schedule Name select | ScheduleName | Parent and child operations | Exact UI LOV display value, including case | BO-owned lookup input | BO resolves `ScheduleId` |
| Trading Partner Type select | TradingPartnerTypeCode | Parent operations and parent context | Exact supported LOV value | BO-owned lookup input | BO-owned normalization and resolution |
| Parent and child identifiers | TransportationScheduleAssignmentId, SiteScheduleAssignmentId | All operations | Not user input | Never emitted as task-local values | BO-owned resolution |
| DFF forms | DFF | Parent and child | Not accepted in the standard request | Not applicable | Excluded |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| TS.VALIDATE_OPERATION | step | 10 | validate_input | passed->TS.DONE;failed->RETURN_ISSUES | none | stop | A Transportation Schedules parent or child operation is requested |
