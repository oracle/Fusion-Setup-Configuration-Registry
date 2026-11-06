# Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Requested operation | `Create` or `Update` | Request an explicit operation decision. | Preserve the requested operation exactly. Never infer `Update` from an existing location, Enabled state, or effective-date values. | Asset Location create or maintenance. | |
| Asset Location identity | Nonblank complete code or labelled Segment1 through Segment7 values | Request a business identity only when none was supplied. | Accept an undelimited value without requiring a label; defer structure, delimiter, physical-column and membership checks until discovery. | Initial intake. | |
| Segment value description | A supplied `SegmentNDescription` is the requested description for the corresponding `SegmentN` value-set value. | When the resolved value-set value is absent and `SegmentNDescription` is blank, default it to the human-readable sentence-case form of the corresponding `SegmentN` value. | After resolving the active LOC# structure and its segment-to-value-set mapping, verify the value. If it is absent, route creation of that value and its supplied or defaulted description through Manage Fixed Assets Flexfield Value Sets; then resume fresh Asset Location validation automatically. | A labelled Segment1 through Segment7 value is supplied. | resolve_location_segment_values |
| Enabled state | Optional at intake; explicit Yes/Y or No/N is preserved | Obtain the choice before artifact creation when omitted for create; preserve existing state for an explicitly selected update. | Normalize supplied values without overriding intent. Do not treat an Enabled value on a Create request as permission to update an existing location. | Asset Location create or maintenance. | |
| Effective dates | Optional `StartDateActive` / `EndDateActive` | Leave blank on create; preserve existing dates for an explicitly selected update unless a change or clearing is explicit. | Preserve the requested lifecycle operation. Do not treat supplied effective dates on a Create request as permission to update an existing location. | Asset Location create or maintenance. | |
| Mapping identity | Parent location code or labelled segments plus HR Location Code and HR Set Code for HR mappings; Customer Site Number for TCA mappings | Report the missing supplied business fields for the affected row. | Preserve the parent request and defer source eligibility to reference discovery. | Mapping-row intake. | |
| Mapping branch | Optional Customer Site Number | Retain the HR branch when blank. | A nonblank value is an unsupported request until an approved customer-site resolver contract exists. Retain it only to report the blocker. | Mapping-row intake. | |

Preserve supplied DFF context and values at intake. Derive required global and
context fields from the current batch DFF export; dependency/design validation
owns their eligibility. Mapping Enabled conversion remains in defaulting rules.

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Start date is later than end date | Reject the supplied date range; equal dates are valid. | Both dates are supplied. | |
| Explicit combination Enabled value is not Yes, Y, No or N, ignoring case | Request an unambiguous enabled choice without replacing the supplied value. | Combination Enabled is supplied. | |
| Requested operation is not Create or Update | Request an explicit operation decision without replacing the supplied value. | Asset Location create or maintenance. | |
| A labelled physical segment exceeds 30 characters | Reject that segment. Do not apply this limit to an unresolved concatenated multi-segment code. | A physical Segment1 through Segment7 value is explicitly labelled. | |

## KFF Input Representation

Prefer labelled KFF segment assignments. A delimiter is not required from the
user. For a concatenated code, use only the delimiter returned by the active
LOC# structure.

When a supplied value has no delimiter, defer interpretation to the declared
lookup workflow. If the active KFF definition has one segment, use the entire
value for that segment; the absence of a delimiter alone does not establish a
one-segment definition.

Configuration-dependent requiredness, valid component membership, physical
mapping, duplicates and persisted-row lifecycle rules belong to the later
reference, dependency and design stages. Initial intake must not demand facts
that the workflow has not yet looked up.

`SegmentNDescription` is not an Asset Location combination CSV field. It is
business intent for the associated value-set value. Preserve it with the parent
request and apply it only through the resolved value-set prerequisite route;
never discard it or treat its absence from the Asset Location CSV contract as
an ambiguity.
When a labelled `SegmentN` value is confirmed absent from its resolved value
set and has no corresponding `SegmentNDescription`, default the description to
the human-readable sentence-case form of the corresponding `SegmentN` value.
Do not request confirmation for this default and do not replace an explicit
`SegmentNDescription`.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MAL.VALIDATE_INPUT | decision | 10 | validate_input | valid->MAL.RESOLVE_REFERENCES;invalid->MAL.HANDLE_INPUT | none | stop | Local checks of supplied identity, shape, formats and dates before reference discovery. |
