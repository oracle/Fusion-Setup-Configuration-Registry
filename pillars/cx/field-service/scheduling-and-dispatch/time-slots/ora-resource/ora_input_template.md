# Time Slots Input Template

Source: Configuration API contract (public source verification pending), Time Slots PUT contract (accessed 2026-08-19).

Use the `Time Slots` worksheet in
`../assets/time-slots-input-template.xlsx` as the canonical input shape.

| Workbook column | Payload mapping | Required | Accepted values |
|---|---|---:|---|
| `ID` | Workbook record identity only | No | Optional workbook row identifier |
| `Time Slot Label` | `label` and `{itemId}` when `FS-IDENTIFY-BY: label` | Yes | Stable, unique label |
| `Name` | `name` | No | Display name; defaults to the label |
| `Status` | `active` | Yes | `Active` or `Inactive` |
| `Start Time` | `timeStart` | Yes | `HH:MM` |
| `End Time` | `timeEnd` | Yes | `HH:MM`, later than Start Time |
| `Business Purpose` | Validation evidence only | Yes | Documented customer, booking, routing, capacity, or quota-management purpose |
| `Booking Model` | Validation evidence only | No | `None`, `Quota-based`, or `Availability-based` |
| `Eligible Activity Types` | Validation evidence only | No | Activity Types that may be offered in the slot; not an association payload |
| `Change Impact` | Validation evidence only | No | UI, API, booking, routing, quota, or existing-window impact |

For a bounded slot, the template row maps to this body:

```json
{
  "label": "testLabel",
  "name": "08-10",
  "active": true,
  "timeStart": "08:00",
  "timeEnd": "10:00"
}
```

The implementation API requires `FS-IDENTIFY-BY: label` for every PUT.
`If-None-Match: {label}` is a create-only header: send it only after a 404
item lookup and omit it for an existing-slot update. These are execution
headers, not workbook columns. Although `isAllDay` occurs in the response example, it is
not documented as a writable request field and is therefore not a template
column. `Business Purpose`, `Booking Model`, `Eligible Activity Types`, and
`Change Impact` support the Time Slots design rules only; they are never sent
to an association endpoint.
Do not add Activity Types, Capacity Categories, or Warehouse Visits to this
template: they are not part of the Time Slots main-item payload.
