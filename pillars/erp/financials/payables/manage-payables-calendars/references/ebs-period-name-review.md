# EBS period-name review before import

The observed FSM import/readback derives period names as
`EnteredPeriodName + "-" + two-digit PeriodYear`. Compare all source names before
candidate generation. This observation does not prove that a source business
year is wrong: fiscal-year labels can differ from the year of the dates.

For example, source name November-26, prefix November, year 2027 and November 2026 dates
produce predicted Fusion name November-27. Show the discrepancy before importing.
Keep the source intact; preserve years, dates and prefixes unless the user
separately requests a business-data correction.

## Decision and candidate contract

For a user-confirmed EBS migration, set `resolvedScope.sourceSystem` to `EBS`.
Do not infer R12 release from minimum API/patch metadata. Add exactly one decision
per affected period only after the user explicitly accepts that mapping:

```json
{
  "sourceSystem": "EBS",
  "periodNameDecisions": [
    {
      "CalendarName": "SYNTH_FISCAL",
      "CalendarType": "GENERAL",
      "sourcePeriodName": "November-26",
      "EnteredPeriodName": "November",
      "PeriodYear": "2027",
      "PeriodNum": "1",
      "predictedPeriodName": "November-27",
      "choice": "accept-derived-name"
    }
  ]
}
```

This is normalization input inside resolvedScope, not a Fusion CSV field and not
an import authorization. Missing, duplicate, stale or unmatched decisions block
candidate generation. After acceptance, the normalized operation retains
sourcePeriodName as traceability metadata and uses the derived PeriodName in its
target key. The preview discloses the change, and normal key, parent, date,
final-state and immutable package approval gates still apply. Do not relax
reconciliation into an unapproved name equivalence.

The alternate choice is to defer affected records/calendars. Agree the excluded
scope, remove deferred operations and their decisions from a new design, preserve
parent context for all remaining periods, and revalidate; do not silently skip.
A generic yes to import a package is not evidence of a previously undisclosed
rename decision. Reuse an explicit choice only for its exact unchanged rows.

## Uploaded packages

A ZIP contains final target rows, not proof of EBS source mapping or human consent.
Keep the user-confirmed EBS source context and reviewed mapping outside the ZIP.
Validate the immutable ZIP against the corresponding decision-bearing normalized
design and requirements before Task Hook and final approval. Standalone structural
or uploaded-package validation alone does not establish this migration decision.
Do not rewrite a supplied ZIP, fabricate consent, or guess its source system.

## Scope of implementation

This gate covers declared EBS period-create designs in the existing offline
normalization/build/validation path. It is not an automatic EBS source detector
or an executable R12 XML converter. Post-import updates preserve the actual
existing Fusion identity; this rule adds no rename/update capability.
