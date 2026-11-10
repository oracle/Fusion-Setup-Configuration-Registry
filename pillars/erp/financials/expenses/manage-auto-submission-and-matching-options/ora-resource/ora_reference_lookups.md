# Reference lookups

These rules are reusable across target environments. Planner readiness means the execution rules are defined; all applicable runtime checks must still pass. The portable execution contract in ../references/execution-contract.md defines environment selection, input mapping, FSM compatibility checks and the in-memory Data Loader handoff. A missing product qualification is an explicit runtime blocker, never implicit approval.

The FSM import hook is not a separately callable public GET. The mechanism below is confirmed source evidence; do not invoke it directly. The repository's Manage Business Unit task supplies a separate read-only existence lookup; its execution binding is the shared REST client declared below; target visibility is checked at runtime. No local authoritative lookup dataset was supplied. This existence lookup does not replace the FSM tenant-aware resolver or close the remaining value-domain and serialization contracts.

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| verify_business_unit_exists | A BU name is supplied, before expense modification or missing-BU routing | User's BU name; selected target environment; applicable effective context | GET /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV; owner contract FUN_MANAGE_BUSINESS_UNIT; execute through core/fusion-api/rest-api-client/scripts/fusion_rest_client.py after active Run Book, authentication and ready task-rule plan checks | BusinessUnitId, BusinessUnitName, PrimaryLedgerId, LegalEntityId, ActiveFlag; totalResults=true; retrieve every page | Exact BusinessUnitName match across complete results; require unique usable identity. Do not filter out inactive matches and misclassify them as absent. | Existing, confirmed absent, ambiguous, inactive or unverified outcome; resolved BU facts only for unique verified identity. These fields do not establish EnterpriseId. | Zero is confirmed absent only with complete results and verified visibility/effective context; otherwise unverified. Multiple, inactive, incomplete or unavailable results block modification and creation. Return confirmed absence to the Run Book for the SKILL.md prerequisite route; do not create from this node. |
| resolve_business_unit | EXM_ORG_SETTING.BuName, EXM_SETUP_OPTION.BuName | Canonical BuName and verified target identity | Governed FSM import through Data Loader; no standalone lookup call | Target business-unit identity | Require unique active preflight match and same-target baseline | Fusion resolves the supplied business-unit name within the selected tenant; do not insert numeric identity columns | Missing, ambiguous or unverified identity blocks the skill; retain actual import errors and reconcile results |
| resolve_setting_code | Selecting a reviewed auto-submission or matching control | Business control and proposed SettingCode | Reviewed control mappings in this resource, traced to SRC-UI-OPTIONS-AMIMPL, SRC-UI-DA-BEAN and SRC-EXM-CONSTANTS; deterministic comparison, no Fusion call | Business control, exact SettingCode, entity, supported scope | Require exact membership and matching control in the reviewed table; do not use all codes from the shared EO | Canonical SettingCode and control scope; value acceptance remains separately validated | Unknown or conflicting mapping is an authoring blocker. Do not invent a code or silently drop the requested control. |
| resolve_option_code | Selecting the automatic-submission enable control | Automatic-submission enable control and proposed OptionCode | SetupOptionAutoSubmitDAExpVO bindLookupCode and FinExmSetupOptionsAMImpl BU option mapping, SRC-UI-AUTOSUBMIT-VO and SRC-UI-OPTIONS-AMIMPL; deterministic comparison, no Fusion call | OptionCode and control identity | Automatic-submission enable maps exactly to ENABLE_AUTO_SUB_DA_EXP in EXM_SETUP_OPTION; this does not enumerate ValueCode | ENABLE_AUTO_SUB_DA_EXP; explicit global or BU scope | Any different option code requires its own source-backed control mapping. Do not substitute another EXM_SETUP_OPTIONS member. |
| resolve_auto_submission_value | EXM_SETUP_OPTION.ValueCode | Explicit enable/disable choice and ENABLE_AUTO_SUB_DA_EXP | Deterministic system-seed validation against SRC-SEED-ORA_EXM_ENABLE_AUTO_SUB_DA_EXP; public_preflight_policy=not_applicable for this fixed enum; no Fusion call | LookupType, LookupCode, Meaning, CustomizationLevel, EnabledFlag, active dates | Yes maps to Y; No maps to N; exact canonical codes Y and N are accepted. Blank is unspecified, never an implicit No. | Canonical ValueCode Y or N | Reject other values and request a valid explicit choice. Deployed qualification is separately gated. |
| resolve_setting_value | EXM_ORG_SETTING.SettingValue | Reviewed SettingCode and explicit user value | Deterministic validation using Confirmed encodings below; fixed enums use public_preflight_policy=not_applicable. Time-zone changes use resolve_time_zone_evidence; merchant list edits return FEATURE_CONTRACT_REQUIRED through resolve_feature_scope | SettingCode; canonical value; relevant seed LookupCode/Meaning; TimeZoneCode and LongName for time zone | Exact per-control code/format match. No arbitrary setting accepted. | Canonical string for confirmed encodings; require verified exact TimeZoneCode when changed. Merchant thresholds use confirmed number/direction rules; editing merchant lists requires its owning contract | Invalid values block; unknown time-zone/merchant authority remains an explicit applicable dependency. Omitted workbook cells preserve current values, never default or clear them. |
| qualify_fsm_transport | Before any FSM row composition or preview | Captured exact-task target template, selected operation and source-backed transport evidence | Local metadata inspection with scripts/input_contract.py inspect_aliases and the compatibility table in ../references/execution-contract.md; no Fusion call and no metadata rewrite | ObjectShortName, ObjectType, CSV members/headers/types, XML paths, NodeSequence, alias inventory and applicable blank/global profile | Exact identity/shape match; every requested row has one qualified route. For actual setup-option changes, multiple root aliases return FSM_ALIAS_COLLISION until an owning selection contract and deployed import evidence qualify a strategy. When a fresh same-target baseline proves requested setup-option values already satisfied, retain both alias CSVs header-only; inspect_aliases(changed_entities={EXM_ORG_SETTING}) returns not_applicable for alias selection only. Organization-setting blank/global behavior uses the shipped ../references/fsm-transport-profile.md and scripts/fsm_transport.py; its organization-only profile has a verified successful four-row FSM import; this does not verify a new target or populated aliases | Qualified selected alias and scope serialization, or named compatibility blockers; no evidence means blocked, not passed | Stop with FSM_SCHEMA_MISMATCH, FSM_ALIAS_COLLISION or FSM_SERIALIZATION_UNQUALIFIED and identify the needed product evidence. An export alone cannot certify import |
| resolve_time_zone_evidence | A time-zone control is changed | Explicit fixed-offset or regional intent; exact proposed TimeZoneCode | GET /fscmRestApi/resources/11.13.18.05/timezonesLOV through core/fusion-api/rest-api-client/scripts/fusion_rest_client.py using the standard selected Fusion scope; exact q=TimezoneCode filter, fields=TimezoneCode,EnabledFlag,LongName,Offset,OffsetNumeric, totalResults=true and complete pagination. A fresh same-target setup baseline is supplementary evidence | TimezoneCode, EnabledFlag, meaning/offset semantics, selected environment and release | Require one exact returned TimezoneCode with EnabledFlag=Y; complete filtered results and offset semantics must match explicit intent. Fixed UTC−08:00 candidate is Etc/GMT+8; arbitrary PST is ambiguous. Zero, disabled, multiple or unavailable results remain unverified/unusable | Exact validated TimeZoneCode or TIME_ZONE_NOT_VERIFIED | Ask for target-specific evidence through the owning setup workflow; do not substitute a code or treat no evidence as nonexistent |
| resolve_feature_scope | Evaluating requested business controls | Named requested controls and scenario | Local comparison to reviewed control mappings and scripts/input_contract.py; no Fusion call | Reviewed settings versus separate feature activation/list editing requirements | Ordinary reviewed schedule/matching controls pass without an Agent deployment dependency. Extra controls remain explicitly unimplemented in this skill | Applicable or not-applicable prerequisites; FEATURE_CONTRACT_REQUIRED for extra requested features | Route the named missing contract to its owner and preserve the user's request; do not drop it or relabel Oracle functionality unsupported |

## Source mechanism and limitations

Business-unit preflight and FSM row identity resolution are separate checks. A visible active business unit does not prove setup privileges or successful import. Keep exact-name matching, complete pagination, target binding and post-import reconciliation. No private implementation helper is an execution route.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Named BU inside governed FSM import | ExpenseOrgSettingServiceAMImpl and ExpenseSetupOptionServiceAMImpl call findByAltKey using Name and EnterpriseId. BusinessUnitId maps to OrgId. Source confirmation does not establish current BU existence/activity. |
| No matching BU | Helper returns null. Both hooks record a processing message. Organization setting additionally sets OrgId=-999; setup-option hook leaves OrgId untouched in that branch. |
| Multiple BU matches | The helper requests max=1 and returns the first row; design-time alternate key is unique. Do not claim explicit duplicate rejection. If preflight establishes ambiguity, fail closed. |
| Public BU existence lookup | verify_business_unit_exists uses the owning repository task's read-only contract only after workflow prerequisites pass. The LOV verifies visible BU identity; the import service supplies EnterpriseId separately from its tenant/session. No live call is authorized while the Run Book or task-readiness prerequisites remain incomplete. Require complete pagination and identity visibility before classifying absence. |
| Expense setup row missing | Absence of EXM_ORG_SETTING or EXM_SETUP_OPTION rows does not establish BU absence. Keep BU identity and setup-row lifecycle decisions separate. |
| Lookup gaps | Code mappings for the reviewed controls are confirmed. Fixed source enum domains are confirmed. Retain time-zone target membership, extensible merchant selection and serialization qualification as explicit blockers. Source mapping is not a live environment check. |

## Reviewed control mappings

These mappings apply to the auto-submission and matching controls reviewed for this skill. They do not claim that every other setting exposed by the full setup page has been modeled. Any additional requested control remains an explicit authoring gap until its own mapping is supplied. All rows below belong to EXM_ORG_SETTING; automatic-submission enable belongs to EXM_SETUP_OPTION with OptionCode ENABLE_AUTO_SUB_DA_EXP.

| Business control | SettingCode | Scope |
|---|---|---|
| Auto-submission frequency | AUTO_SUBMT_DA_EXP_FREQ | Global or named BU |
| Auto-submission time | AUTO_SUBMT_DA_EXP_FREQ_TIME | Global or named BU |
| Auto-submission time zone | AUTO_SUBMT_DA_EXP_FREQ_TZONE | Global or named BU |
| Accommodation amount variance | MATCH_ACCOM_VAR_AMT | Global only |
| Accommodation variance direction | MATCH_ACCOM_VAR_DIR | Global only |
| Accommodation days variance | MATCH_ACCOM_VAR_DATE | Global only |
| Airfare amount variance | MATCH_AIRFARE_VAR_AMT | Global only |
| Airfare variance direction | MATCH_AIRFARE_VAR_DIR | Global only |
| Airfare days variance | MATCH_AIRFARE_VAR_DATE | Global only |
| Car rental amount variance | MATCH_CAR_VAR_AMT | Global only |
| Car rental variance direction | MATCH_CAR_VAR_DIR | Global only |
| Car rental days variance | MATCH_CAR_VAR_DATE | Global only |
| Meals amount variance | MATCH_MEALS_VAR_AMT | Global only |
| Meals variance direction | MATCH_MEALS_VAR_DIR | Global only |
| Meals days variance | MATCH_MEALS_VAR_DATE | Global only |
| Miscellaneous amount variance | MATCH_MISC_VAR_AMT | Global only |
| Miscellaneous variance direction | MATCH_MISC_VAR_DIR | Global only |
| Miscellaneous days variance | MATCH_MISC_VAR_DATE | Global only |
| Entertainment amount variance | MATCH_ENTRMNT_VAR_AMT | Global only |
| Entertainment variance direction | MATCH_ENTRMNT_VAR_DIR | Global only |
| Entertainment days variance | MATCH_ENTRMNT_VAR_DATE | Global only |
| Merchant display list (derived by UI AM; edit contract unresolved) | MATCH_MERCHANT_NAME | Global only |
| Merchant amount variance | MATCH_MERC_VAR_AMT | Global only |
| Merchant days variance | MATCH_MERC_VAR_DATE | Global only |
| Merchant variance direction | MATCH_MERC_VAR_DIR | Global only |
| Merchant tip wait days | MATCH_MERC_TIP_WAITDAY | Global only |

Evidence: FinExmSetupOptionsAMImpl initDASetupTableVO/saveDATableData, schedule accessors and BU update methods; FinExmSetupDigitalAssistantBean schedule constants; ExmConstants exact code literals. SRC-HELP-26D explicitly limits receipt/card matching to all business units. Runtime code that can read BU settings does not establish a supported BU-specific matching setup.

## Confirmed encodings and unresolved value authority

| Control | Confirmed source contract | Remaining boundary |
|---|---|---|
| Schedule time | HH:mm in 24-hour format; 00:00 through 23:59. Unambiguous 5:00 AM becomes 05:00. SRC-UI-DA-BEAN validateTime and SRC-UI-OPTIONS-AMIMPL store SettingValue. | No time-zone inference and no independent deployed-version qualification. |
| Schedule days | Comma-separated codes are read and written by the UI/AM. Runtime maps MON, TUE, WED, THU, FRI, SAT, SUN to weekday labels. Thursday maps to THU in SRC-ALM-DEFAULT-PREFERENCE. | SRC-SEED-ORA_EXM_DA_SETUP_FREQ confirms exactly MON/TUE/WED/THU/FRI/SAT/SUN, enabled with no end date and System customization. Map labels to codes; preserve an explicit weekday set as comma-separated canonical codes. Enabling requires at least one day. Deployment qualification remains separate. |
| Category and merchant amount variance | Integer from 0 through 50; SettingValue stores percentage points, so ten percent is 10, not 0.10. UI validateLongRange and EO Long.valueOf validation apply. | A BU-specific request is a scope conflict; obtain an explicit global choice or hold the change. |
| Matching date variance and merchant wait days | Nonnegative whole numbers; use decimal integer text. EO validates with Long.valueOf and rejects negative values. UI enforces a minimum of zero. | Do not invent an undocumented business maximum or silently fill omitted values. |
| Direction | SRC-SEED-ORA_EXM_MATCH_DA_VAR_DIR contains exactly BOTH (Both), NEGATIVE (Less than the Digital Assistant), POSITIVE (More than the Digital Assistant); all enabled with System customization. | Preserve the product label semantics; do not reverse comparison direction or infer an omitted direction. |
| Enable option | ORA_EXM_ENABLE_AUTO_SUB_DA_EXP is System: Yes=Y and No=N, both enabled with no end date. | No default from blank input; FSM qualification is a separate boundary. |
| Time zone | Global VO maps SettingValue to OrgSettingsTimeZoneVVO.TimeZoneCode and displays LongName. VVO queries HWM_TZ_DISPLAY_NAMES for session language. | The reviewed seed contains Etc/GMT+8 with US label (UTC-08:00); IANA defines that code as fixed −8 with no daylight-saving rule. The target-membership route is defined by resolve_time_zone_evidence through timezonesLOV. Each run must still verify the exact target code, enabled state and semantics against the user's confirmed intent. Fixed UTC offset and daylight-saving region are distinct; never synthesize a code or substitute Pacific daylight-saving time for fixed UTC−08:00. |
| Merchant display list | saveDAMerchantName reads ORA_EXM_MATCH_MERCHANT_NAME and writes comma-separated DisplayedField labels to MATCH_MERCHANT_NAME. The page renders outputText; its edit-link block is commented out. Seeds include Lyft/Uber and customization E is Extensible. | Do not serialize ORA_EXM_LYFT or ORA_EXM_UBER as SettingValue or infer a selectable-code control. Merchant list changes require their owning setup contract and validated import semantics. No merchant request means preserve this field. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUTO_LOOKUPS | step | 30 | reference_lookup | passed->AUTO_DEFAULTS | AUTO_DEPENDENCIES | stop | Task validation before any Data Loader handoff |

## Evidence

Maintainer provenance IDs: `SRC-REPO-BU-ROUTE`, `SRC-ORG-AMIMPL`, `SRC-OPTION-AMIMPL`, `SRC-ORG-EO`, `SRC-OPTION-EO`, `SRC-BU-PVO`, `SRC-REST-BU-26D`, `SRC-BU-PEO`, `SRC-FSM-MIGRATOR-HELPER`, `SRC-FSM-FRAMEWORK-FAQ`, `SRC-OPTION-VO`, `SRC-UI-AUTOSUBMIT-VO`, `SRC-OPTION-EOIMPL`, `SRC-ALM-REPORT-FETCH`, `SRC-ORG-EOIMPL`, `SRC-ORG-VO`, `SRC-UI-OPTIONS-AMIMPL`, `SRC-ALM-DEFAULT-PREFERENCE`, `SRC-UI-DA-PAGEDEF`, `SRC-UI-DA-PAGE`, `SRC-UI-DA-BEAN`.

The reusable contract is the task-local field, scope and package rules. Maintainer source locations are excluded from distribution and are not runtime inputs. Historical review does not qualify a new target or authorize an import. Retain every current-target and approval check.



## Seed authority and qualification

The three System lookup parents above contain the complete source enum sets, all EnabledFlag=Y, StartDateActive=1951-01-01 and no EndDateActive. System customization prohibits implementation-time addition/deletion or enabled/date edits; product seed upgrades remain possible. SRC-LOOKUP-CONFIG documents S=System and E=Extensible; the current Financials overview corroborates these configuration rules. The merchant lookup is extensible and must not be treated as only Lyft/Uber. These source checks are not external-operation adapters and do not authorize live Fusion calls.

| Source ID | Source | Location | Revision boundary | Status |
|---|---|---|---|---|
| SRC-SEED-ORA_EXM_ENABLE_AUTO_SUB_DA_EXP | Maintainer review | Excluded source register | Historical review only | Verify target applicability |
| SRC-SEED-ORA_EXM_DA_SETUP_FREQ | Maintainer review | Excluded source register | Historical review only | Verify target applicability |
| SRC-SEED-ORA_EXM_MATCH_DA_VAR_DIR | Maintainer review | Excluded source register | Historical review only | Verify target applicability |
| SRC-SEED-ORA_EXM_MATCH_MERCHANT_NAME | Maintainer review | Excluded source register | Historical review only | Verify target applicability |
| SRC-UI-TIMEZONE-VO | Maintainer review | Excluded source register | Historical review only | Verify target applicability |
| SRC-UI-TIMEZONE-VVO | Maintainer review | Excluded source register | Historical review only | Verify target applicability |
| SRC-LOOKUP-CONFIG | Lookup customization levels | https://docs.oracle.com/cd/E15586_01/fusionapps.1111/e15524/bs_lookups.htm | Developer Guide section 10.1.3; corroborated by Financials 25D Overview of Lookups; 26D URL unavailable | Confirmed S/E semantics |
| SRC-TIMEZONE-SEED | Maintainer review | Excluded source register | Historical review only | Verify target applicability |
| SRC-IANA-ETC | IANA time-zone database, etcetera | https://data.iana.org/time-zones/tzdb/etcetera | Retrieved 2026-10-12, Etc/GMT+8 entry | Fixed UTC−08:00 without daylight-saving rules |

For explicit fixed UTC−08:00 intent, the source-backed canonical candidate is Etc/GMT+8. Do not treat the source seed as a target check, and do not silently substitute PST, PST8PDT or America/Los_Angeles. This narrows the outstanding question to target acceptance and package qualification.

## Target time-zone lookup contract

Oracle documents the standard Fusion `timezonesLOV` collection (lowercase z in the resource path). Use the selected core REST client and standard scope after input/environment/Run Book checks, before row composition. Pass query values as structured CLI arguments; never interpolate user values into executable code. Resolve an exact code and require `EnabledFlag=Y`. For explicit fixed-offset intent when the candidate is disabled, the same collection may be queried with EnabledFlag=Y and OffsetNumeric equal to the requested offset in seconds. A current offset alone does not establish year-round behavior: verify the returned code against authoritative IANA rules. Always obtain the user's confirmed time-zone choice for the run; if workbook, conversation or environment values conflict, present the conflict and ask the user to choose and confirm before mapping. Reuse an explicit later confirmation; never silently substitute. An HTTP authorization or availability error is not proof of a missing time zone. Do not probe alternate spellings or substitute a different service when this declared route fails. Persist only sanitized lookup status and evidence references.

Source: [Oracle REST API — Get all time zones](https://docs.oracle.com/en/cloud/saas/sales/faaps/op-timezoneslov-get.html), current unversioned documentation reviewed 2026-10-13. This establishes the read-only lookup contract; it does not qualify FSM serialization.

## Organization-setting profile

Use [the shipped transport profile](../references/fsm-transport-profile.md) for
organization-only writes and its documented source and verified-import boundaries. It
requires no customer-provided import ZIP. Other operations keep their explicit
qualification checks.
