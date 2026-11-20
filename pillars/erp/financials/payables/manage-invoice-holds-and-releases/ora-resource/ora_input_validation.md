# Manage Invoice Holds and Releases — Input Validation

Task: AP_MANAGE_INVOICE_HOLDS_AND_RELEASES. This resource owns required inputs, accepted values and CSV representation for AP_HOLD_CODE setup definitions.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-update-fields: AP_HOLD_CODE::UserUpdateableFlag, AP_HOLD_CODE::ExternalDescription, AP_HOLD_CODE::HoldInstruction, AP_HOLD_CODE::WaitBeforeNotifyDays, AP_HOLD_CODE::ReminderDays, AP_HOLD_CODE::InitiateWorkflowFlag, AP_HOLD_CODE::UserReleaseableFlag, AP_HOLD_CODE::InactiveDate, AP_HOLD_CODE::PostableFlag, AP_HOLD_CODE::DspDescription -->

Apply [defaulting policy](ora_defaulting_rules.md), [update restrictions and import effects](ora_design_enforcement.md), and the named [reference lookups](ora_reference_lookups.md) alongside this input contract. Those resources own their rules; input validation alone does not authorize execution.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AP_HOLD.INPUT | step | 10 | validate_input | success->AP_HOLD.LOOKUPS;failure->AP_HOLD.ERRORS | none | stop | Review explicit create inputs or the supported existing-definition update fields and matching baseline; reject unsupported operation/field scope before candidate handoff. |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Setup definition identity | AP_HOLD_CODE.HoldLookupCode | Request the explicit business name | Preserve the supplied key and use the identity resolver | Explicit create key or existing-definition update target | find_hold_code_identity |
| Definition type | AP_HOLD_CODE.HoldType | Request the intended canonical hold or release type code | Clarify ambiguous labels; validate the field below | Explicit create input or preserved update baseline |  |
| Definition description | AP_HOLD_CODE.DspDescription | Require an explicit create description; preserve the existing description when omitted on update | Validate nonblank text; use the description resolver | Explicit create/update input or preserved update baseline | resolve_hold_description |
| Create flags | AP_HOLD_CODE.UserUpdateableFlag; AP_HOLD_CODE.UserReleaseableFlag; AP_HOLD_CODE.PostableFlag | Request a missing manual-release choice; apply approved defaults to the other omitted flags | Apply ora_defaulting_rules.md, then validate the complete row | Create only |  |
| Requested change values | AP_HOLD_CODE.UserUpdateableFlag; AP_HOLD_CODE.ExternalDescription; AP_HOLD_CODE.HoldInstruction; AP_HOLD_CODE.WaitBeforeNotifyDays; AP_HOLD_CODE.ReminderDays; AP_HOLD_CODE.InitiateWorkflowFlag; AP_HOLD_CODE.UserReleaseableFlag; AP_HOLD_CODE.InactiveDate; AP_HOLD_CODE.PostableFlag; AP_HOLD_CODE.DspDescription | Request at least one explicit supported value | Apply field validation and ora_design_enforcement.md to the merged row | Existing-definition update; optional clears must be explicit |  |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Identifying a definition or reviewing a proposed name | Identity resolution is required | Follow the resolver at its declared workflow gate and retain the import_contract dependency | find_hold_code_identity |
| HoldType is supplied as a code or business label | Input must resolve to a canonical code | Use the type handling in ora_reference_lookups.md; preserve the baseline type on update |  |
| DspDescription is supplied | Description storage is resolver-owned | Validate text here, then follow the supporting lookup contract in ora_reference_lookups.md | resolve_hold_description |

## Field Validation

Validate the complete create row and retained update row. Keep all 17 headers in the order below, all audit cells blank, and only the requested rows. Other omitted optional create fields begin blank; omitted update fields preserve the baseline, subject to the design-owned pre-import consistency rules. A value must pass both its field domain and the applicable field-combination rule. Do not change case, trim whitespace or guess synonyms unless a field explicitly permits it.

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| AP_HOLD_CODE.HoldLookupCode | Required nonblank string, maximum 25 UTF-16 code units. Preserve the exact value and case; do not rewrite it to another key. | Explicit create key or qualified update baseline | find_hold_code_identity |
| AP_HOLD_CODE.HoldType | Required nonblank canonical code string, maximum 25 UTF-16 code units. Observed exports do not define a closed allowlist; do not infer codes from business labels. | Explicit create input or preserved update baseline |  |
| AP_HOLD_CODE.LastUpdateDate | System-managed dateTime; retain a blank audit cell and reject caller overrides. Do not replace a timestamp with a calendar date. | Candidate structure or attempted override |  |
| AP_HOLD_CODE.LastUpdatedBy | System-managed string; retain a blank audit cell and reject caller overrides. | Candidate structure or attempted override |  |
| AP_HOLD_CODE.UserReleaseableFlag | Literal string Y or N; explicit and nonnull on create or requested update. Reject null, empty, Boolean and unapproved aliases. No clear. | Explicit create/requested update input; retained values follow Preserved baseline flags below |  |
| AP_HOLD_CODE.UserUpdateableFlag | Required literal string Y or N when supplied or defaulted on create. Reject null, empty, Boolean and unapproved aliases. No clear. | Supplied value or approved create default; retained values follow Preserved baseline flags below |  |
| AP_HOLD_CODE.InactiveDate | Optional real calendar date or explicit clear; follow Calendar Dates below. | Explicit create/update input or any preserved baseline date |  |
| AP_HOLD_CODE.PostableFlag | Allow Accounting accepts Yes or No, serialized as canonical string Y or N. Reject requested X, including lowercase or padded forms and same-value requests, as well as null, empty, Boolean and unapproved aliases. The adapter trims and normalizes case only for the Y/N code labels; it does not invent business synonyms or claim Fusion accepts noncanonical codes. Y allows accounting; N prevents accounting while the hold remains unreleased. No clear. Requested updates follow Design Enforcement. | Explicit create/update value or approved create default; retained exported values follow Preserved baseline flags below |  |
| AP_HOLD_CODE.LastUpdateLogin | System-managed string; retain a blank audit cell and reject caller overrides. A nullable audit attribute is still not caller-owned. | Candidate structure or attempted override |  |
| AP_HOLD_CODE.CreationDate | System-managed dateTime; retain a blank audit cell and reject caller overrides. | Candidate structure or attempted override |  |
| AP_HOLD_CODE.CreatedBy | System-managed string; retain a blank audit cell and reject caller overrides. | Candidate structure or attempted override |  |
| AP_HOLD_CODE.ExternalDescription | Optional text or explicit clear, distinct from DspDescription. Maximum 80 UTF-16 code units; supplementary characters count as two units. No truncation or rewriting. | Explicit create/update input or preserved baseline |  |
| AP_HOLD_CODE.HoldInstruction | Optional plain text or explicit clear. Maximum 2000 UTF-16 code units and the separate CSV staging limit below. No content pattern, semantic validator or reference lookup. | Explicit create/update input or preserved baseline |  |
| AP_HOLD_CODE.WaitBeforeNotifyDays | Optional integer >=0 or explicit clear. Reject negative, fractional, Boolean and whitespace-only numeric input. Enforce Java Long representation up to 9223372036854775807; this is not a business maximum. Negative values produce FND_CMN_POSITIVE. No ordering against ReminderDays. | Explicit create/update input or preserved baseline |  |
| AP_HOLD_CODE.ReminderDays | Optional integer >=0 or explicit clear. Reject negative, fractional, Boolean and whitespace-only numeric input. Enforce Java Long representation up to 9223372036854775807; this is not a business maximum. Negative values produce FND_CMN_POSITIVE. No ordering against WaitBeforeNotifyDays. | Explicit create/update input or preserved baseline |  |
| AP_HOLD_CODE.InitiateWorkflowFlag | Optional literal string Y or N, or explicit clear. Reject Boolean and unapproved aliases. | Explicit create/update input or preserved baseline |  |
| AP_HOLD_CODE.DspDescription | Required nonblank string in the complete candidate, distinct from ExternalDescription and HoldInstruction. A valid requested replacement can fill a blank baseline description when Design Enforcement permits the change; an omitted description must preserve a nonblank baseline value. Reject null, empty, whitespace-only and nonstring inputs; preserve the supplied text without trimming or rewriting. No clear or client default. Apply the common CSV staging limit; do not infer a 240-character limit from another lookup attribute. | Explicit create/update input or preserved full-row update value | resolve_hold_description |
| Optional clear representation | Null or exact empty string clears only ExternalDescription, HoldInstruction, WaitBeforeNotifyDays, ReminderDays, InitiateWorkflowFlag and InactiveDate. CSV empty becomes explicit XML null. Text whitespace is literal; whitespace-only numeric/date input is invalid. Never serialize null as the string None. | Explicit optional clear, including restoration of an original optional blank |  |
| CSV staging size | Every serialized non-CLOB/non-hex value must be valid UTF-8 and <=4000 bytes. Apply this alongside field precision; reject invalid Unicode or oversized cells before handoff. Never truncate or silently clear a value. | Every requested or retained cell |  |
| Preserved baseline flags | Preserve exported blanks for unrequested UserReleaseableFlag, UserUpdateableFlag, PostableFlag and InitiateWorkflowFlag without synthesizing defaults or requiring predicted null/default outcomes. Preserve an exact exported PostableFlag X only when that field is omitted from the request; never convert it to N or offer it as an input option. Other nonblank retained values follow their field domains. Supplied values and create defaults still require their stated domains, even when a supplied value equals the baseline. | Existing-definition update assembly |  |

## Calendar Dates

- Requests accept a real YYYY-MM-DD date, or null/exact empty string for an optional clear. Do not accept relative dates, timestamps or time zones, invent a default, or add a chronology rule.
- Validate every baseline date, including unrequested rows. Recognize YYYY-MM-DD, YYYY/MM/DD and MM/DD/YYYY as calendar dates; unknown formats remain evidence_unresolved.
- Serialize all nonblank InactiveDate cells in targeted rows uniformly as YYYY/MM/DD because the importer caches a date format per column before converting to yyyy-MM-dd.
- Retain raw baseline text as provenance. Compare calendar values for no-op detection, preservation, reversal and reconciliation.
