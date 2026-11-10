# Reference Lookups

Before executing any REST lookup below, apply the
[REST version and query compatibility preflight](../../../references/rest-query-compatibility.md)
and the REST request compatibility rule in Lookup Execution Rules. Existing
matching, classification precedence and workflow gates continue to apply.

## Resolution Policy

Resolve intent to the CSV column in ora_input_validation.md first. Accept codes, names, meanings, descriptions, translations and ordinary wording in any language when evidence and context identify one member. These tables are resolution targets, not exact-English input allowlists. Write the documented CSV representation; never substitute an internal ID for a name or code.

Missing supported authority, acquisition-contract uncertainty or unverified eligibility parity yields REFERENCE_UNRESOLVED, severity Warning, blocking=false. Preserve the supplied value in its proven representation, disclose the skipped check and next evidence needed, and continue every remaining supported check and preview without a waiver. Never invent a code from unresolved prose. Ask only for actual ambiguity or a missing representation needed to construct supported payload. Proven invalidity and failed supported reads (auth, transport, API contract, incomplete pagination) remain errors. Mutation capability, baseline, protected-use and approval gates remain separate.

Emit a warning transition only after all applicable supported checks in that node have completed without an error. A real error or unmet independent mutation gate takes precedence over accumulated warnings. At the execution gate, warning permits a validation/preview result; it permits a write-ready result only when every required write gate also passes.

## Schedule Type
CSV columns: PJF_RATE_SCHEDULE.csv.ScheduleType

| Lookup Code | Meaning |
|---|---|
| EMPLOYEE | Person |
| JOB | Job |
| NON-LABOR | Nonlabor |
| PROJECT_ROLE | Project Role |
| RESOURCE_CLASS | Resource class |

Static immutable membership from seeded system lookup PJF_SCHEDULE_TYPE, with no supported customer add/delete path. All five are active task branches. Resolve locally and serialize Lookup Code. No live lookup.

## Resource Class
CSV columns: PJF_RATE_SCHEDULE_LINE.csv.Name2

| Lookup Code | Meaning |
|---|---|
| PEOPLE | Labor |
| EQUIPMENT | Equipment |
| MATERIAL_ITEMS | Material Items |
| FINANCIAL_ELEMENTS | Financial Resources |

Static immutable seeded resource classes. Supported maintenance changes class attributes, not predefined members. Resolve locally and serialize Meaning to Name2, not code or numeric ID. Labor and Equipment derive HOURS as RateUnit; other classes use the separate configurable UOM contract.

## Local Lookups

These resolvers consume the named local authorities or coordinate the contracts below. An unresolved record never treats supplied input as proof of membership.

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_schedule_type | ScheduleType supplied | Complete Schedule Type table in this file | Resolve one canonical member from code/meaning/intent | PJF_RATE_SCHEDULE.csv.ScheduleType = Lookup Code | Complete-domain no match or actual ambiguity requires correction |
| resolve_resource_class | RESOURCE_CLASS line | Complete Resource Class table in this file | Resolve one canonical member from code/meaning/intent | PJF_RATE_SCHEDULE_LINE.csv.Name2 = Meaning | Complete-domain no match or actual ambiguity requires correction |
| resolve_rate_uom | Supplied UOM name/code needs serialization or comparison with a subtype-derived code | Complete project and inventory UOM acquisitions below | Apply Rate Unit Name to Code once across both sources; require one consistent canonical code | LINE.RateUnit = resolved code; reference provenance and separate eligibility findings | Missing/ambiguous representation or failed supported acquisition blocks affected resolution; unsupported eligibility parity alone warns |
| resolve_rate_current_date | New line From Date omitted/null/blank | Current business date and timezone already supplied by the selected target workflow; no acquisition endpoint established by the UI run | Require one ISO date and identified date authority for this target; do not derive from a fixture or invent a GET | Default-date context used only by ora_defaulting_rules.md | Missing authority is needs_input for the affected default; explicit user From Date does not require this lookup |
| verify_rate_scope | Every request | Selected task catalog and declared target context | Exact PJF_MANAGE_LABOR_RATE_SCHEDULES and target | Scope | Actual task/target ambiguity blocks |
| find_rate_schedule | Identity/baseline needed | Baseline already supplied by selected project workflow | Canonical set/name/type; stable identity for mutation; complete scoped search includes all result pages | Existing header/lines/identity including a proven empty result for create | Empty complete baseline is valid on greenfield; missing/incomplete baseline does not prove absence; require full rows for update/copy/delete |
| verify_rate_route | Write route needed | Current official request contract and target operation-specific capability/template artifact supplied by selected workflow | Exact method/path/subtype/runtime context and every requested writable field; GET values alone are insufficient | Route, per-field capability ledger, header/child/DFF coverage, package contract | Missing or contradicted write capability blocks execution; no invented endpoint or automatic export fallback; never switch after approval |
| resolve_rate_use | Protected mutation/delete | Consumer/use evidence supplied by selected workflow | Stable schedule/line identity and protected operation | Consumer/protection results | Missing use evidence blocks affected mutation; never infer zero use |
| resolve_rate_references | References supplied | Static tables, Live Lookups and Contract Coverage in this file | Run every applicable supported resolver with its own parent/date rules; aggregate warnings | Canonical values and distinct membership/eligibility/unresolved results | Proven invalidity/ambiguity errors; missing authority follows Resolution Policy |
| resolve_rate_lines | Lines supplied | Requested lines, evidenced baseline and resolved reference results | Resolve canonical subtype identities, reference slices and applicable parent associations; preserve optional blank qualifiers | Canonical keys/interval evidence for the owning validation/design nodes and unresolved findings | Identity ambiguity/acquisition failure errors; amount/date shape belongs to ora_input_validation.md, overlap/history/use policy to ora_design_enforcement.md |
| record_unresolved_rate_reference | Unsupported authority or parity | Proven supplied representation and identified evidence gap | Record only the unsupported check; never claim membership | REFERENCE_UNRESOLVED, Warning, blocking=false; preserve value | Continue supported checks/preview; ask only for real ambiguity or unconstructible representation |

## Live Lookups

Use only the active workflow's declared client after its identity/privilege/input checks. These read-only documented contracts support the specified attributes; they do not prove every task-UI predicate or authorize mutations. LINE and TRANSLATION denote PJF_RATE_SCHEDULE_LINE.csv and PJF_RATE_SCHEDULE_TRANSLATION.csv.

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_person_identity | EMPLOYEE line supplies Person display name | Supplied display name and any independently supplied person number/email | /hcmRestApi/resources/11.13.18.05/publicWorkers?onlyData=true | PersonId, PersonNumber, DisplayName, WorkEmail | Exact DisplayName query, then exact WorkEmail query; complete all candidate pages; require one distinct person with nonblank PersonNumber and WorkEmail, and require the email query to return that same one PersonId only | LINE.PersonNumber = returned PersonNumber as text; LINE.EmailAddress = returned WorkEmail; retain PersonId only in lookup context | Zero visible matches, multiple people for the display name, or a shared email requires clarification; blank/malformed identity or failed/incomplete acquisition is an error; directory identity does not prove rate-date eligibility |
| fetch_project_rate_uoms | resolve_rate_uom needs the project UOM source | Supplied UOM intents for this run | /fscmRestApi/resources/11.13.18.05/standardLookups/PJF_UNIT/child/lookupCodes?onlyData=true | LookupCode, Meaning, Description, EnabledFlag, StartDateActive, EndDateActive | Acquire all pages once; pass each returned Meaning/LookupCode pair to resolve_rate_uom | Project UOM candidates and status evidence; no direct payload assignment | Failed/incomplete acquisition is an error; no static replacement or reinterpretation as missing authority |
| fetch_inventory_rate_uoms | resolve_rate_uom needs the inventory UOM source | Supplied UOM intents for this run | /fscmRestApi/resources/11.13.18.05/unitsOfMeasure?onlyData=true | UOMCode, UOM, Description, DisableDate | Acquire all pages once; pass each returned UOM/UOMCode pair to resolve_rate_uom | Inventory UOM candidates and status evidence; no direct payload assignment | Failed/incomplete acquisition is an error; inventory absence alone is not no-match proof for the combined domain |
| resolve_job_set_identity | Job Set supplied | Set code/name/description | /hcmRestApi/resources/11.13.18.05/hcmSetsLOV?onlyData=true | SetId, SetCode, SetName, Description | One set identity; existence of a job in set remains separately unresolved | PJF_RATE_SCHEDULE.csv.SetCode1 = SetCode; SetId in context | Actual ambiguity errors; missing eligibility parity remains unresolved |
| resolve_job_schedule_job | JOB line supplied | Job code/name, resolved Job Set and established effective context | /hcmRestApi/resources/11.13.18.05/jobsLov?onlyData=true | JobId, JobCode, JobName, SetId, SetCode, ActiveStatus, EffectiveStartDate, EffectiveEndDate | One active job in resolved set; do not assume rate start equals lookup effective context | LINE.JobCode1, JobName, SetCode1 and effective-date pair 3 from respective canonical attributes | Known incompatibility/ambiguity errors; unproven date/security parity unresolved |
| resolve_expenditure_type | NON-LABOR line | Type name/description | /fscmRestApi/resources/11.13.18.05/expenditureTypesLOV?onlyData=true | ExpenditureTypeId, ExpenditureTypeName, ExpenditureTypeDescription, UnitOfMeasureCode, ExpenditureTypeStartDate, ExpenditureTypeEndDate | Resolve name/UOM/date; apply supported current-day and class checks | LINE.ExpenditureTypeName = canonical name; RateUnit = UnitOfMeasureCode; ID in context | Missing full parity/Rate Required flag unresolved; known invalidity errors |
| resolve_expenditure_type_classes | Type resolved | ExpenditureTypeId | /fscmRestApi/resources/11.13.18.05/expenditureTypesLOV/{ExpenditureTypeId}/child/ExpenditureTypeClassesLOV?onlyData=true | ExpTypeClassCode | At least one non-ST/OT class in complete child set; mixed labor/nonlabor allowed | Eligibility only; no CSV class column | Unproven child parity unresolved; incomplete/failed acquisition error |
| resolve_project_role_adf | PROJECT_ROLE ADF context | Role name, rate StartDateActive | /fscmRestApi/resources/11.13.18.05/projectRolesLOV?onlyData=true | ProjectRoleId, ProjectRoleName, Description, StartDateActive, EndDateActive | Canonical identity; inclusive line-date range; ADF search excludes IDs 100–102; import-rejection parity not proven | LINE.ProjectRoleName = canonical name; separate eligibility finding | Actual ambiguity errors; unproven base-domain/import parity unresolved |
| resolve_project_role_client | PROJECT_ROLE client-side context | Role name, rate StartDateActive | /fscmRestApi/resources/11.13.18.05/projectRolesLOV?onlyData=true | ProjectRoleId, ProjectRoleName, Description, StartDateActive, EndDateActive | Canonical identity and line-date range; client exclusion parity not proven | LINE.ProjectRoleName = canonical name | Do not assume ADF exclusions; unresolved parity nonblocking |
| resolve_translation_language | Language/SourceLang supplied | Code, description/tag or user intent | /fscmRestApi/resources/11.13.18.05/languagesLOV?onlyData=true | LanguageCode, Description, LanguageTag, InstalledFlag | Resolve canonical code; task installation eligibility remains unresolved | TRANSLATION.Language and SourceLang = respective LanguageCode | Complete supported no-match/ambiguity requires correction; no unsupported installed-only rejection |

Language and SourceLang need not equal each other. For any live lookup, a zero-result narrow text query is not complete-domain no-match proof for broader multilingual intent. Unverified source parity is disclosed separately from successful identity resolution.

## Person Name to Person Number and Email

Use the shared `core.fusion-api.rest-api-client` for a read-only GET of `/hcmRestApi/resources/11.13.18.05/publicWorkers` with `q=DisplayName='<supplied person name>'`, `onlyData=true`, `fields=PersonId,PersonNumber,DisplayName,WorkEmail`, `limit=500`, and `offset=0`. Apply the `REST-Framework-Version` header resolved from the selected core workflow. Pass query options through the client's repeated `--query` arguments; quote/escape the name according to Fusion query syntax and let the client URL-encode the value. Never interpolate unescaped user text into a shell command or request URL. Oracle documents DisplayName as queryable and PersonNumber as a string identifier in [Get all workers](https://docs.oracle.com/en/cloud/saas/human-resources/farws/op-publicworkers-get.html).

Follow `hasMore` pagination as described below before deciding uniqueness. Resolve one distinct PersonId with a consistent, nonblank PersonNumber and WorkEmail; preserve the number as text, including leading zeros. Then query `publicWorkers` with `q=WorkEmail='<resolved email>'` and require that every returned row has that same PersonId, with at least one returned row. Populate `PJF_RATE_SCHEDULE_LINE.csv.PersonNumber` and `EmailAddress` only after both checks pass. Do not put the display name into `Name`, invent a PersonName CSV column, or substitute PersonId. The CPTCXCSQY FSM import for Manage Rate Schedules rejected a Person line without EmailAddress as `JBO-27035: Attribute Email is required` and rejected a shared email as `PJF_FSM_DUPL_PERSON_EMAIL`; treat both as target-specific import evidence, not inferences from the template alone.

When no visible exact match exists, report the unresolved name and ask for its directory spelling or another supported identifier; do not claim the person does not exist throughout Fusion. For multiple distinct persons, ask the user to disambiguate rather than select the first row. A supplied PersonNumber that conflicts with the resolved person blocks the affected line. Missing identity fields, inconsistent IDs/numbers, malformed pagination, or failed supported reads are acquisition errors, not nonblocking missing-authority warnings.

The directory response does not establish EMP/CWK usage, person/name effective-date slices at the rate start, assignment/job/organization eligibility, or full Manage Rate Schedules LOV/import parity. Do not invent those dates or mark those checks passed. Preserve their separate `REFERENCE_UNRESOLVED` warnings and continue supported validation; a failed or ambiguous identity lookup remains a separate blocker. This read does not authorize an import or change the selected execution route.

## Rate Unit Name to Code

`resolve_rate_uom` is the single matching authority for supplied UOM intent. Fetch both declared sources through `core.fusion-api.rest-api-client`, with the workflow-resolved `REST-Framework-Version` header, `onlyData=true`, the respective requested fields, `limit=500`, and `offset=0`; complete each source's pagination before resolving candidates. Share these acquisitions across all lines in the same run/context. Pass options as repeated structured `--query` arguments, not concatenated URLs or per-row queries.

Build candidates from project `Meaning -> LookupCode` and inventory `UOM -> UOMCode`, retaining each source's status fields and provenance. A technical CSV `RateUnit` or explicitly supplied UOM-code field is code input; a supplied UOM name/meaning is name input. Match explicit codes case-sensitively and display names/meanings after case and whitespace normalization. For an unqualified input, consider both name and code matches; do not silently prefer a source or a code interpretation when they lead to different codes. Accept a name/code pair only when both identify the same canonical code. Description or translated/natural-language intent may resolve a candidate only with unambiguous evidence under Resolution Policy; never invent a code.

Deduplicate exact repeated candidate records while retaining source provenance and status evidence; do not collapse different records merely because their codes match. If all matches resolve to one exact canonical code, that code can be serialized; retain distinct labels and status findings separately rather than inventing aliases or discarding them. Multiple distinct codes for the requested meaning require disambiguation. A supplied name/code contradiction is an input error. No match requires correction only after both relevant collections are complete; an inventory-only miss must not reject a project lookup meaning. Missing/blank code or name fields, malformed records, nonprogressing pagination and failed reads are acquisition errors. After unique resolution, preserve code casing and populate CSV `RateUnit`; do not ask for a manually supplied code.

For example, a returned project row with Meaning `Currency` and LookupCode `DOLLARS` supplies `RateUnit=DOLLARS`; Meaning `Hours` and LookupCode `HOURS` supplies `HOURS`. A returned inventory row with UOM `Each` and UOMCode `Ea` supplies `Ea`. These illustrate response mapping, not hardcoded fallback membership. The inventory Currency class's base unit `USD` does not identify the project meaning Currency; `unitOfMeasureClasses` is not a substitute for these two sources. Header `CurrencyCode` is a separate field.

The combined UOM domain includes inventory units and project lookup codes/meanings, and RateUnit is derived from the chosen UomCode. This establishes representation, not full API/UI eligibility parity. Retain enabled/date evidence, but do not add an enabled-only, current-date or rate-start filter without a separately evidenced task predicate; status alone does not exclude those rows. Nonlabor still derives its UOM from the resolved expenditure type, and existing subtype defaults remain in ora_defaulting_rules.md. An explicit UOM conflicting with the Nonlabor-derived code is a validation issue; this resolver never changes the selected import route or approval gates.


## Contract Coverage

Effective-date pair 0 is EffectiveStartDate/EffectiveEndDate; pairs 1–5 have the numeric suffix. These identify reference slices, not rate-line StartDateActive/EndDateActive.

| UI label / intent | CSV columns | Eligibility and representation | Validation route |
|---|---|---|---|
| Reference Data Set; copy alias | PJF_RATE_SCHEDULE.csv.SetCode | Canonical code; conditional project-rate-set data security | Dynamic; record_unresolved_rate_reference until security-equivalent authority exists |
| Schedule Type | PJF_RATE_SCHEDULE.csv.ScheduleType | Complete seeded code domain, all five task branches | resolve_schedule_type; Static |
| Currency; copy alias | PJF_RATE_SCHEDULE.csv.CurrencyCode | Enabled Y and not end-dated at server current day; no start-date or currency-type predicate | Dynamic; record_unresolved_rate_reference until all-rows acquisition contract proven |
| Person | LINE.EmailAddress, PersonNumber, effective-date pair 0 | Name-to-PersonNumber-and-WorkEmail identity from publicWorkers; EMP/CWK usages, rate-date person/name slices and primary-email parity remain separate | resolve_person_identity for supplied display name; serialize resolved WorkEmail because observed target FSM import requires EmailAddress; record_unresolved_rate_reference for unsupported eligibility/slice checks |
| Job / Job Code (Person) | LINE.PersonJobName, JobCode, SetCode, effective-date pair 1 | Same person-bound E/C latest-change assignment; job/department slices at assignment start; derives job and organization | Dynamic; record_unresolved_rate_reference; generic job membership insufficient |
| Organization (Person) | LINE.Name, SetCode2, effective-date pair 2 | Selected person+job, latest-change E/C assignment; no extra current-date predicate | Dynamic; record_unresolved_rate_reference |
| Job Set | PJF_RATE_SCHEDULE.csv.SetCode1 | Set code; at least one job in set without active/date condition on existence test | resolve_job_set_identity; job-existence eligibility unresolved |
| Job / Job Code (Job schedule) | LINE.JobName, JobCode1, SetCode1, effective-date pair 3 | Selected set, active A, established effective context; shared alias contract | resolve_job_schedule_job; missing effective-context parity unresolved |
| Expenditure Type | LINE.ExpenditureTypeName; derived RateUnit | Current-day active type; exists non-ST/OT class; UOM/category/Boolean-meaning joins; Rate Required N does not exclude type | resolve_expenditure_type and resolve_expenditure_type_classes; remaining parity unresolved |
| Nonlabor Resource | LINE.NlrName | Selected expenditure type, canonical name; no current-date predicate | Dynamic; record_unresolved_rate_reference |
| Organization (Nonlabor Resource) | LINE.Name1, effective-date pair 4 | Selected resource association; current active project/expenditure organization; CSV dates are organization dates | Dynamic; record_unresolved_rate_reference |
| Rate Required (read-only Boolean) | None; UI-only reference | Configured parent flag Y=checked, N=unchecked; UI Rate input unavailable for N; no exported flag field | Never serialize flag; parent-flag acquisition unresolved. Apply ora_input_validation.md Amount Presence Contract with separately evidenced endpoint/import parity; no invented static lookup |
| Resource Class | LINE.Name2 | Canonical class meaning/name | resolve_resource_class; Static |
| Organization (Resource Class) | LINE.Name3, effective-date pair 5 | Current active organizations in configured project-relevant classifications, not a fixed three-class domain | Dynamic; record_unresolved_rate_reference |
| Unit of Measure (Resource Class) | LINE.RateUnit | Inventory UOMs union PJF_UNIT lookup values; no enabled-only criterion; Labor/Equipment derive HOURS; other classes editable | resolve_rate_uom using both declared sources; record_unresolved_rate_reference only for remaining unsupported eligibility parity |
| Project Role (ADF) | LINE.ProjectRoleName | Canonical name; rate-line date, separate ADF search restriction | resolve_project_role_adf |
| Project Role (client-side) | LINE.ProjectRoleName | Canonical name; rate-line date; exclusion parity uncertain | resolve_project_role_client |
| Translation Language / Source Language | TRANSLATION.Language, SourceLang | Canonical Oracle codes; no task-page LOV | resolve_translation_language; installation semantics unresolved |

No additional UI LOV exists for header/translated names and descriptions, parent links, rate dates or numeric amounts. Validate supported shape/relationships rather than inventing lookup membership. Configured DFFs require separately selected metadata; never fabricate CSV columns.

## Fetch Strategy and Reuse

| Consumers | Acquisition plan | Evidence and limits |
|---|---|---|
| Person display name | Once per distinct supplied DisplayName using the exact documented q filter; all candidate pages; share identical name requests within the run | publicWorkers provides directory identity, PersonNumber, and WorkEmail; no rate-date/usage/assignment or full UI eligibility parity inferred |
| Supplied UOM intents | Fetch the complete PJF_UNIT lookup-code collection and inventory units collection once each per run/context; resolve all line intents locally through resolve_rate_uom | Preserve source/code/name/status evidence; no per-line fetch, class-code substitution or static fallback; membership does not prove full eligibility parity |
| Job Set | Once per distinct normalized SetCode/SetName/Description using documented q; all candidate pages | Configurable population; API size/security scope unknown; has-jobs predicate absent |
| Job / Job Code (Job schedule) | Once per distinct normalized JobCode/JobName plus resolved parent set and established effectiveDate; documented q SetId/SetCode and ActiveStatus | Configurable population justifies selective lookup; no invented rate-date bind; reuse aliases |
| Expenditure Type / derived UOM | Once per distinct normalized name/description using documented q or KeywordFinder SearchTerm; all candidates | API size unknown; share parent identity/UOM resolution; preserve residual join/flag parity warning |
| Expenditure Type classes | Once per resolved ExpenditureTypeId; independently page child collection | Parent relationship explicit; onlyData=true retained; expanded children not assumed complete |
| Project Role ADF/client | Share base candidates per distinct normalized role identity using documented q; apply each branch's date/exclusion rules separately | Do not use current-date ActiveProjectRolesFinder for historical/future line eligibility; API size unknown |
| Language / SourceLang | Fetch complete small language-metadata collection once per run/context; match both fields locally | Expected bounded metadata, not a DB-count-sized cap; reassess page metadata |
| Static domains | Read complete local table once | No HTTP request |
| Unsupported authority | No live fetch | Record unresolved; no runtime SQLcl/CodeSearch/browser or undeclared FSM export |

Use onlyData=true, a supported explicit page size such as limit=500, and requested identity/eligibility fields. Follow documented offset/hasMore pagination, advancing by actual returned item count until hasMore=false. Repeated, missing-identity, empty/nonprogressing pages or failed later pages are acquisition errors. Counts are not limits. Encode q/finder values through the declared client; never concatenate user text. No one-call-per-row behavior.

Cache per run/environment/read identity/application language/effective context/resource/field coverage/parent/filter/normalized query. Share a candidate acquisition only when its fields and scope cover all consumers; cache eligibility separately per branch/parent/date. Never reuse stale or cross-target results. Documented membership support does not imply full UI parity.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| REST request compatibility | Before a workflow-selected request, determine framework applicability and the effective REST framework version from the selected core client or workflow. Use compatible query syntax and verify that the outgoing header agrees; never pin an independent pillar version. Apply the linked offering preflight, preserve finder separators and literal values, and stop the affected request on an unresolved version or header/query conflict. |
| Person display name supplied | Resolve one directory person through resolve_person_identity and fill CSV PersonNumber and EmailAddress; do not ask for a manual identifier after a unique successful match |
| Line group omitted | Preserve current rows |
| Person job selected | Derive organization only from source-proven same-person assignment; otherwise preserve and warn |
| Job Name or Job Code selected | Resolve one job in the selected Job Set and derive its paired identifier through resolve_job_schedule_job; reject contradictory supplied pairs, not missing independent duplicate input |
| Optional Person/Nonlabor/Resource Class qualifier absent | No lookup or required-input failure for that qualifier; preserve an unrestricted key; validate supported relationship when a qualifier is supplied |
| Role/type typed text does not resolve | Preserve the unresolved input and report the actual no-match/ambiguity/lookup incident; one failed autocomplete does not prohibit all typed canonical names |
| Supported and unresolved checks coexist | Complete supported checks and carry nonblocking warnings through preview without waiver |
| More- and less-specific lines coexist | Preserve both; disclose evidenced precedence and shadowed intervals |
| DFF supplied | Require selected workflow writable metadata; no invented column |
| Write route lacks field | Apply selected workflow capability gate; no automatic alternate route/export |
| Supported live operation fails | Classify operational failure; no automatic retry/fallback or unsupported-authority exception |

## Selected Core Adapter Handoff

| Operation | Selected service and contract | Required handoff | If unavailable |
|---|---|---|---|
| Declared reference GET or operation-metadata read | core.fusion-api.rest-api-client, references/fusion-rest-api.md, scripts/fusion_rest_client.py | Use the selected environment and read identity; pass the documented request path, repeated query parameters and requested fields through the shared client; retain page-completeness and scoped evidence | Stop the supported read with its classified failure; no direct HTTP, browser, SQLcl or alternative acquisition |
| REST-backed setup import, including a schedule header or staged child creation | core.data-loader mandatory import orchestration; its selected target-supported product adapter | Pass the exact task code/name, operation, capability ledger, source/baseline, complete staged call plan and parent-ID binding. Data Loader owns source/API validation, immutable artifact preparation, Task Hook evaluation, preview approval and execution handoff | Return unsupported or missing execution capability before approval or mutation if Data Loader cannot select an evidenced adapter for all requested operations/fields |
| FSM CSV import | core.data-loader mandatory import orchestration | Pass the exact target-supported task ZIP and normal source/task validation inputs; preserve its approved preflight and Task Hook envelopes unchanged | Stop before upload if archive, route, checks or approval are missing |

Read core.fusion-api.rest-api-client and its standard Fusion REST instructions
before the declared GET. Pass query values as structured/repeated query options,
not concatenated user text. The client owns environment validation, authentication
and read transport. Do not read or copy credentials into task artifacts.

direct_writable_rest records capability, not execution authority. A writable
endpoint alone never selects a runtime import adapter. Every setup import,
including REST-backed creation, enters core.data-loader before a product adapter
is invoked. Its immutable preview/approval workflow is authoritative; this task
does not add a duplicate import approval gate. Never submit a REST POST through
the generic client as a workaround for missing Data Loader support. A registry
reference_lookup node is read-only and cannot execute the staged write plan.

A supported update/end-date/delete that the active workflow classifies outside
an import still requires an explicitly selected authorized executor, exact
operation-specific contract, and approval immediately before mutation. This
resource does not establish that separate execution route; fail closed on its
absence. No current approval permits a route switch, automatic retry or a new
write to discover capabilities.

## REST Capability Ledger

Before a REST preview, record each proposed call's method, path, parent schedule subtype, framework/metadata context, and payload field JSON paths. For every field record its request-schema source, target write support (supported, rejected, or unknown), type/requiredness, reference evidence, and any documented-versus-target discrepancy. Only supported fields may pass `verify_rate_route`; unknown is not supported. A GET proves identity/value existence, not create/update support. Keep schema facts separate from reference-value facts.

For a staged header/child create, establish child capability from existing same-subtype metadata through the routed read-only client before creating the new header. Resolve the new parent ID from the execution response and validate its identity before binding it to the already-reviewed child path. If discovery is unavailable or inconclusive, report the precise missing operation/field instead of assuming that the public schema matches this pod.

A target rejection of a field at the header path does not establish rejection at the child path, nor does it prove REST as a whole is unsupported. Evaluate the corrected child route before proposing FSM. Conversely, public documentation does not override an observed target rejection of the same operation and shape.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RATE.FIND_SCHEDULE | step | 3 | reference_lookup | resolved->RATE.RESOLVE_LINES;warning->RATE.RESOLVE_LINES;failure->RATE.RETURN_ISSUES | RATE.APPLY_DEFAULTS | stop | Resolve applicable contracts; complete all supported checks and retain warnings |
| RATE.RESOLVE_LINES | step | 4 | reference_lookup | resolved->RATE.VALIDATE_LINES;warning->RATE.VALIDATE_LINES;failure->RATE.RETURN_ISSUES | RATE.FIND_SCHEDULE | stop | Resolve lines with separate membership, eligibility and representation results; defer input/policy judgments to their owners |
