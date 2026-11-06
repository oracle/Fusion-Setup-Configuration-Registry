# Transportation Schedules BO-Owned Resolution

## Resolution Boundary

The registered `Transportation Schedules` Business Object and Core Data Loader own all LOV, parent-key, child-key, and surrogate-ID resolution for this task. This task skill performs no REST lookup and contains no REST request path.

| Situation | Data Loader / BO responsibility | Task-local behavior |
|---|---|---|
| Parent POST | Resolve submitted parent business attributes and create the parent assignment. | Pass the parent-create attributes defined in `ora_input_validation.md`. |
| Child POST | Resolve the parent route key from the complete parent business key supplied in the operation context. Resolve `TradingPartnerSite` and `ScheduleName` to the child backing values. | The nested child REST body is only `TradingPartnerSite`, `ScheduleName`, and `EnabledFlag`. Do not emit parent or child surrogate IDs, `TradingPartnerTypeCode`, or other inherited parent fields in that body. |
| Parent PATCH or DELETE | Resolve `TransportationScheduleAssignmentId` from the submitted parent business key. | Do not supply or derive `TransportationScheduleAssignmentId` locally. |
| Child PATCH or DELETE | Resolve `TransportationScheduleAssignmentId` from the complete parent business key and `SiteScheduleAssignmentId` from the child business key in that parent context. | Pass friendly parent and child business attributes to the BO/Data Loader. The BO uses both resolved IDs for the parent-addressed child route; do not supply or derive either ID locally. |

## Parent Context For Child Operations

Every child operation carries the complete parent business key in its operation context: `TradingPartnerTypeCode`, `TradingPartnerName`, `ScheduleUsageCode`, and `CarrierName` when applicable. This context is required even when the child request contains only child changes, because the BO must resolve the parent assignment before it can resolve or address the child.

The task skill does not make REST calls, run task-local queries, or persist technical identifiers. It supplies the registered BO/Data Loader with friendly values only.
