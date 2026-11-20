# Work Definition Names — Design Enforcement

## Public references and compatibility

- [Oracle Fusion Cloud Manufacturing 26D: Work Definition Names](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faumf/work-definition-names.html) explains the business fields and usage restrictions.
- [Oracle Fusion Cloud SCM 26D: WorkDefinitionName business object](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fabsm/bo_oraScmCoreManufacturingWorkDefinition_WorkDefinitionName.html) lists the business type codes. This is a different API model; do not copy its field names, children or write contract into V2.

The public references support business terminology. They do not establish a public compatibility guarantee for workDefinitionNamesV2. Verify its availability, operations and schema in the selected environment through the owning workflow. The rules below distinguish service behavior, request preparation and adopted FSCR policy. They are not evidence of successful create/update testing.

These are explicit FSCR policies, not claims that V2 enforces equivalent restrictions on the server. Apply them only to the requested operation and actual changes.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Determine actual changes | For update, compare only supplied writable fields with the resolved current record. Compare text without case folding or forced trimming, dates by date value, and planning as JSON boolean. Keep omission, explicit null and missing response attributes distinct. Omit equal values from the proposed PATCH; if a supplied field cannot be compared, stop that request for missing evidence |
| 2 | Evaluate applicable policies | Evaluate type, explicit planning intent, usage and seeded-status restrictions below. Create requires no existing-record usage or seeded-status evidence |
| 3 | Preserve whole-request intent | If any actual change is blocked, return all affected fields and reasons; do not submit a reduced request without an explicit user choice or an established partial-execution policy |
| 4 | Return preparation result | For update, if no actual changes remain, report already matching and no write needed. Otherwise hand off only intended, permitted changes through normal core preparation and approval gates |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| WorkDefinitionType actually changes on update | Mandatory | | Requested type differs from the resolved stored type | Type is create-only. Explain the restriction and suggest a separate name only within intended scope; an unchanged supplied type is omitted from PATCH | No automatic replacement or separate creation |
| Explicit planning=true on create, or actual planning change to true on update | Mandatory | | Effective type is REWORK or TRANSFORM; or effective type cannot be established | Reject conflicting intent for correction. Effective type is requested type on create, STANDARD when omitted on create, and stored type on update; never silently set false | No automatic change |
| Actual WorkDefinitionCode, EffectiveFromDate or UsedInPlanningFlag change on update | Mandatory | verify_work_definition_name_usage | Usage is Y or cannot be established as N | Prohibit the requested protected-field change when in use; explain missing usage evidence when unknown. No routine override. Display name and description are not locked by usage | No automatic change or routine exception |
| Actual WorkDefinitionCode or EffectiveToDate change on update | Mandatory | | Authoritative non-seeded status is not established; known seeded records are prohibited | This packaged contract has no seeded-status resolver, so refuse these changes. Do not block creation, inspection, unchanged values or other permitted fields because seeded status is unavailable | No automatic inference or override |
| Existing REWORK or TRANSFORM record with planning=true, without a planning change | Informational | | None from the pre-existing inconsistency alone | Permit otherwise eligible changes; do not repair planning unless requested. A requested repair must still satisfy the usage restriction | No unsolicited repair |
| EffectiveToDate change on an in-use name | Mandatory | | Seeded-status restriction or server date validation prevents the change; usage alone does not | Apply the seeded-status policy and server checks; do not treat in-use status as a blanket end-date prohibition | No silent date adjustment |
| Create or change a shared name | Recommendation | | No extra approval is introduced here | Centralize name management because names may be shared across products; preserve normal core approval gates | No automatic business-value change |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| verify_work_definition_name_usage | Actual code, start-date or planning change on update | Current protected values and decoded usage for the resolved target | ora_reference_lookups.md |

## Seeded-status capability boundary

The current policy is complete: refuse code/end-date changes when non-seeded status cannot be established. No missing lookup is treated as permission. Enabling those changes later requires a separately authored and validated resolver using an approved server-side SeededFlag source matched to the exact target ID and environment, or a maintained environment-specific inventory with reliable provenance and adequate coverage. An incomplete inventory's absence proves nothing. Do not infer status from prefixes, display names, a short seed list or a missing V2 attribute. A supplied assertion alone is not authoritative evidence.

The four write policies do not prevent authorized read-only inspection. DELETE remains outside the supported resource operations; end-dating is not deletion. Read/check/write enforcement is not atomic: refresh time-sensitive evidence through the owning workflow and do not claim protection against concurrent changes. Strict concurrency guarantees require server-side enforcement.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WDNAME.DESIGN | step | 50 | design_enforcement | passed->WDNAME.HANDOFF_GATE;failed->WDNAME.ERROR | WDNAME.DEFAULTS | stop | Evaluate only policies applicable to create or actual update changes; record permitted changes, no-change result or precise blockers |
