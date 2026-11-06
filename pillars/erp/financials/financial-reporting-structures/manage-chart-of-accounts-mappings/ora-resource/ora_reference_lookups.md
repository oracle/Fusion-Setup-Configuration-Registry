# Reference Lookups

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_source_coa | Before mapping comparison or live submission; not a template-export prerequisite | Exact source Name or exact StructureInstanceCode | GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV and, after resolution, GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV/{StructureInstanceId} | Name, EnabledFlag, StructureInstanceCode, StructureInstanceId, StructureInstanceNumber, Description | Match exact Name or exact StructureInstanceCode; require exactly one match and EnabledFlag true | Source Name, StructureInstanceCode, StructureInstanceId, StructureInstanceNumber, Description | Stop mapping submission on no match, disabled match, or many matches; do not select a candidate |
| find_target_coa | After source COA resolves and before mapping comparison or live submission; not a template-export prerequisite | Exact target Name or exact StructureInstanceCode | GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV and, after resolution, GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV/{StructureInstanceId} | Name, EnabledFlag, StructureInstanceCode, StructureInstanceId, StructureInstanceNumber, Description | Match exact Name or exact StructureInstanceCode; require exactly one match and EnabledFlag true | Target Name, StructureInstanceCode, StructureInstanceId, StructureInstanceNumber, Description | Stop mapping submission on no match, disabled match, or many matches; do not select a candidate |
| resolve_execution_defaults | Before reference effective-date checks and preview | User-supplied SecurityFlag, mode, and accounting date, or omissions | Local ora_defaulting_rules.md and the client current date | Resolved values and user/default provenance | Preserve supplied values; default only omitted values to N, Increment, and current preparation date | Resolved execution values and derivation record | Stop submission on unresolved or unsupported mode, flag, or date |
| select_import_route | After rule composition and before contract retrieval | Requested rules and explicit user route preference | Local rule-composition decision using current FSM export and current FBDI template evidence | Rule types, explicit route request, confirmed FSM contract coverage | Select FSM for header, segment, single-source rollup, or account rules unless FBDI is explicitly requested; select FBDI for multiple-source rules | Selected route, rationale, and required contract evidence | Stop if multiple-source rules lack FBDI evidence or a requested FSM route lacks a confirmed multiple-source contract |
| resolve_segment_value_set | Segment or rule metadata is required after both COAs resolve | Resolved StructureInstanceId and segment identity | Current Segment Metadata procedure below using supported current read evidence or the declared shared KFF export fallback; internal VO evidence is optional corroboration | Application ID, key flexfield code, structure instance, segment instance, segment code, value set ID, enabled state | Require APPLICATION_ID 101, KEY_FLEXFIELD_CODE GL#, enabled structure instance, enabled segment, and segment instance belonging to the exact resolved COA | Verified segment and value-set metadata | Stop on missing, disabled, ambiguous, or cross-COA segment metadata |
| find_value_set_definition | A resolved source or target segment is used by a constant, copy, or rollup rule | Exact ValueSetCode from verified segment metadata | GET /fscmRestApi/resources/11.13.18.05/valueSets?q=ValueSetCode='{ValueSetCode}' | ValueSetCode, optional ValueSetId, ValidationType, ValueDataType, ValueSubtype, MaximumLength, ZeroFillFlag, UppercaseOnlyFlag, links or @context.links | Require exactly one exact ValueSetCode match; retain the returned item link as the only allowed child-values navigation URI | Value-set identity, validation type, datatype, subtype, maximum length, format flags, and child-values URI | Stop on zero or multiple matches; do not construct a child URI from a value-set code or user-supplied ID |
| find_value_set_values | A constant, copy, or rollup rule references one or more values | Child-values URI returned by find_value_set_definition, requested values, and accounting date | GET {returned value-set item link}/child/values | Value, EnabledFlag, active-date fields, IndependentValue when applicable, and returned value-item link | Require an exact requested value match that is enabled and effective on the accounting date; page through the collection before claiming a value or value population is complete | Value existence and effective-status evidence; complete active value population when copy-value comparison is required | Stop on missing, disabled, ineffective, ambiguous, or incomplete paged evidence |
| resolve_segment_map_method | A segment mapping method is supplied | Requested method label or technical code and selected import route | FSM: the Reviewed FSM Schema and Reviewed FSM Field Semantics sections below after Template Contract Review below confirms target-template compatibility. FBDI: current XLSM. | Technical code, display label, route, contract fingerprint | Compatible FSM: Assign single value=S, Copy value from source=C, Use rollup rules=R; U is not a normal create method. FBDI codes require its template evidence. | Proven route-specific method code and evidence | Stop on unknown code, incompatible FSM contract, or unproved FBDI method |
| resolve_value_set_max_size | Copy-value mapping is requested | Resolved source and target value set IDs | Resolved source and target valueSets MaximumLength from the declared exact-code lookup; CoaValueSetMaxSizeVO evidence is optional corroboration | Source max size and target max size | Require source maximum size less than or equal to target maximum size | Copy-value length evidence | Stop when either maximum size is unresolved or source exceeds target |
| resolve_mapping_values | A rule references a constant, detail, range, or parent value | Chart, segment, value, accounting date | Supported read-only Fusion value metadata | Technical value, value set, enabled state, start date, end date, parent status | Exact value valid on the accounting date | Validated source or target value | Stop on missing, ambiguous, inactive, or ineffective value |
| resolve_mapping_hierarchy | A rule references a parent value | Chart, segment, parent value, accounting date | Supported read-only tree and hierarchy-version metadata | Tree, version, dates, active, flattened, audited, children | One associated active version effective on accounting date | Parent expansion evidence | Stop on no version, overlap, ambiguity, or failed readiness |
| verify_hierarchy_association | Parent-based mapping is requested | Chart instance, segment, tree | Supported chart-instance and flexfield deployment metadata | Associated tree, segment instance, deployment state | Exact association and deployed accounting flexfield | Association and deployment evidence | Stop until association and redeployment are complete |
| find_mapping_definition | After template contract resolution; mandatory for live create, import, update, or delete | Exact mapping name, target environment, and current supported mapping evidence | Shared task-level export with exact-name criteria under Current Mapping Discovery below, then Mapping Comparison Procedure; alternatively current supported application/report evidence. No public mapping REST endpoint is assumed. | Header plus every segment, rollup, multiple-source, and account rule, evidence environment, date, coverage, and audit baseline | Follow Mapping Comparison Procedure below. Match by name first, then compare charts and all rules; never hide a same-name conflict by filtering charts. | absent, identical, different, ambiguous, or pending with evidence baseline | Absence requires complete current coverage for the exact name. Pending permits preparation only; identical is no-op; different needs direction; ambiguous stops. |
| inspect_current_fsm_task_csv | Whenever template/contract evidence is needed; before FSM package preparation | Current target-environment template/spec ZIP; populated data is optional | shared.setup-export.task-level-export default template-only route, then Template Contract Review below using the Reviewed FSM Schema and Reviewed FSM Field Semantics sections below | Exact headers, metadata types, parent-child paths, batch metadata, sequence, ZIP shape, environment, release, fingerprint | Match the reviewed contract. For account rules require ORA_GL_AFF_MAP_RULE.csv mapped to CoaMapAccountRuleVO. Preserve every header. Template retrieval does not require existing-mapping comparison. | Compatible FSM contract, source/target field semantics, method codes, fingerprint | Stop package generation on missing or incompatible contract; do not request populated full-task data to compensate for an unexplained header |
| inspect_current_fbdi | Before FBDI artifact generation | Current Oracle XLSM | Current Oracle Financials FBDI guide and workbook | Worksheets, tooltips, columns, required markers, accepted codes, lengths, macros, CSV names, ZIP structure | Current release template only | Import contract and evidence fingerprint | Stop when unavailable, stale, modified, or ambiguous |
| analyze_rule_overlap | Segment and account rules coexist | Normalized rule definitions | Local comparison over validated requested and existing rules | Source combinations, segment-derived target, account-rule target | Every intersecting source criterion is reported | Overlap list and effective account-rule result | Block readiness when analysis is incomplete |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Supported endpoint is undocumented or unavailable | Use same-task export or supported read-only application evidence; do not invent REST paths. |
| chartOfAccountsLOV query construction | Use only documented/supported REST filtering for an exact Name or StructureInstanceCode match; do not broaden to contains or select a first row. |
| valueSets query construction | Query valueSets by exact ValueSetCode from verified segment metadata and request only the fields needed for validation. Do not substitute a segment label or display name. |
| Child-values navigation | Read links or @context.links and follow the returned values child link unchanged. ValueSetId is optional; do not require an unreturned ID, synthesize a key from ValueSetCode, or re-encode returned hrefs. If the returned link is unusable, use the supported exact ValueSetCode collection query with expand=values through the same shared REST client. Accept a positive verified value match, but do not claim absence or full coverage from a truncated expanded child collection; block checks requiring complete paging if it cannot be obtained. |
| Value collection paging | Continue until all applicable pages are retrieved before comparing complete copy-value populations or declaring that a requested value is absent. |
| Dependent value set | Include the independent-value context in every value lookup and comparison; do not treat the child value alone as a unique key. |
| Source or target COA is disabled | Stop mapping preparation and submission; independent template/spec export remains available. |
| COA details are required after a unique match | Retrieve the item resource using StructureInstanceId and retain only the documented identity fields needed for downstream comparison. |
| A lookup returns multiple candidates | Report the candidates and stop for a precise business identifier. |
| A mapping header exists | Compare source chart, target chart, description, security behavior, and every rule before deciding create or update. |
| Update is approved | Reread the mapping immediately before mutation and compare audit or version evidence with the approved baseline. |
| Current template differs from stored guidance | The current template wins for interface columns, codes, lengths, files, and ZIP structure. |
| FSM task-CSV contract differs from stored guidance | Stop package generation and review the current target template/spec and ASM_SETUP_CSV_METADATA.xml; verify changed semantics before updating the reusable contract. Do not transfer old field meanings automatically. |

The legacy v2 registry labels reference lookups fusion-rest generically. For find_mapping_definition, execute only the local evidence procedure below; that route label does not declare a mapping REST endpoint.

## Template Contract Review

| Check | Required Result |
|---|---|
| Task and provenance | Target template/spec from shared.setup-export.task-level-export, task GL_MANAGE_CHART_OF_ACCOUNTS_MAPPING; retain environment, release, operation, and fingerprint. No COA lookup or mapping comparison prerequisite applies to template retrieval. |
| ZIP and CSV structure | One ASM_SETUP_CSV_METADATA.xml and unique, safe member names. Compare current CSV filenames and complete ordered headers against the Reviewed FSM Schema and Reviewed FSM Field Semantics sections below. Reject duplicate columns and inconsistent row widths. An empty template is valid contract evidence. |
| Metadata | Compare each business object's XmlAttributeList/XmlAttributeTypeList, XmlNodePath, NodeSequence, and BatchName against the reviewed contract; retain parent-child key columns in CSV headers. Do not transfer old field meanings across an unexplained mismatch. |
| Contract scope | The reviewed schema below is reference guidance, not a processor or proof of live setup. A template establishes layout; current metadata and value lookups establish business validity. |

## Current Segment Metadata

Use the declared structure-export fallback only when existing supported read evidence cannot resolve the requested segment metadata. Route GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES (Manage Chart of Accounts Structure Instances) through the existing shared task-level exporter in setup-data mode for this reference-data purpose; it is not needed to discover the mapping import layout.

| Join | Required Result |
|---|---|
| Structure instance | Match StructureInstanceCode exactly in ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_INSTANCE.csv; require application 101, key flexfield GL#, and EnabledFlag Y. Retain its StructureCode. |
| Structure | Match StructureCode in KEY_FLEXFIELD_STRUCTURE.csv under the same application/flexfield; require EnabledFlag Y. |
| Structure segments | Select enabled rows from ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_SEGMENT.csv for that exact structure. Obtain SegmentCode and ColumnName; do not infer physical columns from display sequence or labels. |
| Instance value sets | Join ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_INSTANCE_SEGMENT.csv by exact instance code and SegmentCode under the same application/flexfield. Use the instance ValueSetCode, not an unverified structure default. Require one match per enabled segment. |
| Completeness | Retain the complete enabled target-segment inventory and its evidence fingerprint. Validate every requested source-dependent segment against its own resolved COA. A segment-rule create must cover each enabled target segment exactly once. |

## Current Mapping Discovery

For an exact-name existence or recovery check, use shared.setup-export.task-level-export with --data and --export-criteria-file. Write a JSON array with this criterion, replacing only the exact mapping name with a safely JSON-encoded value. Use this name-scoped request instead of an unfiltered mapping-data export; verify returned scope evidence before relying on the result.

```json
[
  {
    "TaskCode": "GL_MANAGE_CHART_OF_ACCOUNTS_MAPPING",
    "BusinessObjectCode": "GL_AFF_MAPPING",
    "AttributeSet": "Set1",
    "AttributeName": "Name",
    "AttributeValue": "<exact mapping name>"
  }
]
```

Pass the exact task code and Financials / Financial Reporting Structures context to the existing exporter. Verify successful completion, current target environment, and returned MigrationProcessScopeValueCSVMetadata evidence: BusinessObjectShortName GL_AFF_MAPPING, ScopeValueBoAttributeId Name, and the requested exact ScopeValueBoAttributeValue or code. If scoping is unsupported, ignored, or not verifiable, do not infer absence or silently fall back to an unfiltered export. Apply the comparison below only after evidence coverage passes.

## FSM Package Preparation

| Step | Required Behavior |
|---|---|
| Business rules | Reject a create with no segment or account rule definition. For segment rules, compare the complete current target inventory with rule target columns: exactly one per enabled target segment, no missing or extra segments, and matching target value sets. Verify every referenced value, source segment, and applicable hierarchy before submission. |
| Header | Populate requested Name, Description, SecurityFlag, source StructureInstanceCode, and target StructureInstanceCode1 using the reviewed compatible contract. |
| Segment methods | S requires a valid SingleValue and blank FromSegColumnName/FromValueSetCode. C or R requires verified source segment and value set with blank SingleValue. C additionally requires the documented value-population and length checks. |
| Rollup children | R requires valid linked rollups, target detail value, and coherent source low/high or supported hierarchy evidence. Preserve GL_AFF_MAPPING.Name plus ORA_GL_AFF_SEGMENT_MAP_RULE.ToSegColumnName as parent keys; reject duplicates, overlaps, and orphans. |
| Encoding and row scope | Use CSV-aware editing/serialization with exact target-template headers, valid quoting of multiline values, consistent row widths, and string-preserved leading zeros. Populate only the requested mapping and its children; never carry unrelated exported rows into the import. Leave unwritable audit fields blank. |
| Account rules | Use the existing export-derived ORA_GL_AFF_MAP_RULE.csv contract and supported source criteria; do not synthesize account combinations or place account rules in FBDI. |
| Package and handoff | Preserve the target template metadata and ZIP shape, check all parent-child links, and retain the final immutable archive. Record rule evidence in Task Hook ruleResults and use core.data-loader for preflight, Task Hook preview, explicit approval, upload, and initiation. No task-specific script is required. |

## Mapping Comparison Procedure

| Step | What Happens |
|---|---|
| 1 | Keep template/semantic evidence separate from existence evidence. A supplied foreign or old export may support the former only, even if its embedded environment label happens to match. |
| 2 | For current, verified target-environment evidence covering the requested name, read GL_AFF_MAPPING.csv and match Name exactly before comparing source and target. A template with no rows is not absence evidence. |
| 3 | Select all segment and account rows by GL_AFF_MAPPING.Name. Select rollups by that name and ORA_GL_AFF_SEGMENT_MAP_RULE.ToSegColumnName; reject orphans. |
| 4 | Compare every business field in the header and selected children. Exclude LastUpdateDate, LastUpdatedBy, LastUpdateLogin, CreationDate, and CreatedBy from business equality, retaining them separately as audit evidence. Compare child rows independent of order without collapsing duplicates or altering multiline CSV values. Retain the original snapshot fingerprint for concurrency evidence. Multiple-source coverage requires separate supported evidence; do not assert equality when coverage is incomplete. |
| 5 | Zero headers in complete current name coverage means absent; one header is compared in full; multiple headers mean ambiguous. Without verified source, freshness, or coverage, return pending. Do not invent a live lookup endpoint or silently export all setup data. |
| 6 | Pending may follow the preparation path, but preview ends at COAMAP.DONE_PREPARED. It is never passed to Data Loader as successful task validation or transformed into absent. A user waiver follows the existing Task Hook override contract with its original finding retained. |

The template and data-export endpoints both emit ProcessType=EXPORT. Record the originating operation; only a verified current data-export response with confirmed exact-name scope and successful completion can establish absence.

## Reviewed FSM Field Semantics

| File or Field | Meaning | Evidence |
|---|---|---|
| GL_AFF_MAPPING.csv StructureInstanceCode | Source COA code | Reviewed source-filter relationships and the Reviewed FSM Schema section below; verify current target-template compatibility |
| GL_AFF_MAPPING.csv StructureInstanceCode1 | Target COA code | Reviewed target account-rule relationships; verify current target-template compatibility |
| ORA_GL_AFF_SEGMENT_MAP_RULE.csv SegmentMapType | S constant, C copy, R rollup | Reviewed method-specific field patterns and rollup parent-child relationships; verify the current contract |
| Segment parent | GL_AFF_MAPPING.Name | Export header and ASM_SETUP_CSV_METADATA.xml |
| Rollup parent | GL_AFF_MAPPING.Name plus ORA_GL_AFF_SEGMENT_MAP_RULE.ToSegColumnName | Export header and ASM_SETUP_CSV_METADATA.xml |
| Scope | Apply only after current target-template compatibility passes; this evidence does not identify target-environment setup | CSV schemas and metadata are retained without business rows |

## Reviewed FSM Schema

This reviewed schema belongs to task `GL_MANAGE_CHART_OF_ACCOUNTS_MAPPING`. It records interface knowledge only, not current environment setup or executable logic. Compare it with the current target template before using the field semantics above. Keep run-specific evidence in the project workspace.

CSV header order and XML attribute order are listed separately because parent-reference columns and XML attribute ordering differ. Preserve the current compatible template exactly.

### GL_AFF_MAPPING.csv

| Metadata | Reviewed Value |
|---|---|
| XmlNodePath | `/CoaMappingVO/CoaMappingVORow` |
| NodeSequence | 1 |
| BatchName | `CoaMapping` |

Ordered CSV headers:

```csv
Name,SecurityFlag,LastUpdateDate,LastUpdatedBy,LastUpdateLogin,CreationDate,CreatedBy,Description,StructureInstanceCode,StructureInstanceCode1
```

Ordered XmlAttributeList and corresponding XmlAttributeTypeList:

```text
Name,SecurityFlag,LastUpdateDate,LastUpdatedBy,LastUpdateLogin,CreationDate,CreatedBy,Description,StructureInstanceCode,StructureInstanceCode1
string,string,dateTime,string,string,dateTime,string,string,string,string
```

### ORA_GL_AFF_SEGMENT_MAP_RULE.csv

| Metadata | Reviewed Value |
|---|---|
| XmlNodePath | `/CoaMappingVO/CoaMappingVORow/CoaMapSegmentRuleVO/CoaMapSegmentRuleVORow` |
| NodeSequence | 2 |
| BatchName | `CoaMapping` |

Ordered CSV headers:

```csv
GL_AFF_MAPPING.Name,ToSegColumnName,LastUpdateDate,LastUpdatedBy,LastUpdateLogin,CreationDate,CreatedBy,SegmentMapType,FromSegColumnName,SingleValue,FromValueSetCode,ToValueSetCode
```

Ordered XmlAttributeList and corresponding XmlAttributeTypeList:

```text
LastUpdateDate,LastUpdatedBy,LastUpdateLogin,CreationDate,CreatedBy,ToSegColumnName,SegmentMapType,FromSegColumnName,SingleValue,FromValueSetCode,ToValueSetCode
dateTime,string,string,dateTime,string,string,string,string,string,string,string
```

### ORA_GL_AFF_SEGMENT_MAP_ROLLUP_RULE.csv

| Metadata | Reviewed Value |
|---|---|
| XmlNodePath | `/CoaMappingVO/CoaMappingVORow/CoaMapSegmentRuleVO/CoaMapSegmentRuleVORow/CoaMapRollupRuleVO/CoaMapRollupRuleVORow` |
| NodeSequence | 3 |
| BatchName | `CoaMapping` |

Ordered CSV headers:

```csv
GL_AFF_MAPPING.Name,ORA_GL_AFF_SEGMENT_MAP_RULE.ToSegColumnName,ToFlexValue,FromFlexValueLow,FromFlexValueHigh,TreeCode,TreeVersionName,LastUpdateDate,LastUpdatedBy,LastUpdateLogin,CreationDate,CreatedBy
```

Ordered XmlAttributeList and corresponding XmlAttributeTypeList:

```text
ToFlexValue,FromFlexValueLow,FromFlexValueHigh,TreeCode,LastUpdateDate,LastUpdatedBy,LastUpdateLogin,CreationDate,CreatedBy,TreeVersionName
string,string,string,string,dateTime,string,string,dateTime,string,string
```

### ORA_GL_AFF_MAP_RULE.csv

| Metadata | Reviewed Value |
|---|---|
| XmlNodePath | `/CoaMappingVO/CoaMappingVORow/CoaMapAccountRuleVO/CoaMapAccountRuleVORow` |
| NodeSequence | 4 |
| BatchName | `CoaMapping` |

Ordered CSV headers:

```csv
GL_AFF_MAPPING.Name,LowSegments,HighSegments,TreeSegments,LastUpdatedBy,LastUpdateLogin,CreatedBy,FlexFilter,Segment10High,Segment10Low,Segment10TreeCode,Segment11High,Segment11Low,Segment11TreeCode,Segment12High,Segment12Low,Segment12TreeCode,Segment13High,Segment13Low,Segment13TreeCode,Segment14High,Segment14Low,Segment14TreeCode,Segment15High,Segment15Low,Segment15TreeCode,Segment16High,Segment16Low,Segment16TreeCode,Segment17High,Segment17Low,Segment17TreeCode,Segment18High,Segment18Low,Segment18TreeCode,Segment19High,Segment19Low,Segment19TreeCode,Segment1High,Segment1Low,Segment1TreeCode,Segment20High,Segment20Low,Segment20TreeCode,Segment21High,Segment21Low,Segment21TreeCode,Segment22High,Segment22Low,Segment22TreeCode,Segment23High,Segment23Low,Segment23TreeCode,Segment24High,Segment24Low,Segment24TreeCode,Segment25High,Segment25Low,Segment25TreeCode,Segment26High,Segment26Low,Segment26TreeCode,Segment27High,Segment27Low,Segment27TreeCode,Segment28High,Segment28Low,Segment28TreeCode,Segment29High,Segment29Low,Segment29TreeCode,Segment2High,Segment2Low,Segment2TreeCode,Segment30High,Segment30Low,Segment30TreeCode,Segment3High,Segment3Low,Segment3TreeCode,Segment4High,Segment4Low,Segment4TreeCode,Segment5High,Segment5Low,Segment5TreeCode,Segment6High,Segment6Low,Segment6TreeCode,Segment7High,Segment7Low,Segment7TreeCode,Segment8High,Segment8Low,Segment8TreeCode,Segment9High,Segment9Low,Segment9TreeCode,StructureInstanceCode,CcidSegments,LastUpdateDate,CreationDate
```

Ordered XmlAttributeList and corresponding XmlAttributeTypeList:

```text
LastUpdatedBy,LastUpdateLogin,CreatedBy,FlexFilter,Segment10High,Segment10Low,Segment10TreeCode,Segment11High,Segment11Low,Segment11TreeCode,Segment12High,Segment12Low,Segment12TreeCode,Segment13High,Segment13Low,Segment13TreeCode,Segment14High,Segment14Low,Segment14TreeCode,Segment15High,Segment15Low,Segment15TreeCode,Segment16High,Segment16Low,Segment16TreeCode,Segment17High,Segment17Low,Segment17TreeCode,Segment18High,Segment18Low,Segment18TreeCode,Segment19High,Segment19Low,Segment19TreeCode,Segment1High,Segment1Low,Segment1TreeCode,Segment20High,Segment20Low,Segment20TreeCode,Segment21High,Segment21Low,Segment21TreeCode,Segment22High,Segment22Low,Segment22TreeCode,Segment23High,Segment23Low,Segment23TreeCode,Segment24High,Segment24Low,Segment24TreeCode,Segment25High,Segment25Low,Segment25TreeCode,Segment26High,Segment26Low,Segment26TreeCode,Segment27High,Segment27Low,Segment27TreeCode,Segment28High,Segment28Low,Segment28TreeCode,Segment29High,Segment29Low,Segment29TreeCode,Segment2High,Segment2Low,Segment2TreeCode,Segment30High,Segment30Low,Segment30TreeCode,Segment3High,Segment3Low,Segment3TreeCode,Segment4High,Segment4Low,Segment4TreeCode,Segment5High,Segment5Low,Segment5TreeCode,Segment6High,Segment6Low,Segment6TreeCode,Segment7High,Segment7Low,Segment7TreeCode,Segment8High,Segment8Low,Segment8TreeCode,Segment9High,Segment9Low,Segment9TreeCode,StructureInstanceCode,CcidSegments,LastUpdateDate,CreationDate,LowSegments,HighSegments,TreeSegments
string,string,string,clob,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,string,dateTime,dateTime,string,string,string
```

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAMAP.FIND_SOURCE | step | 4 | reference_lookup | resolved->COAMAP.FIND_TARGET | COAMAP.CONTRACT | stop | Always |
| COAMAP.FIND_TARGET | step | 5 | reference_lookup | resolved->COAMAP.LOOKUP | COAMAP.FIND_SOURCE | stop | Always |
| COAMAP.LOOKUP | decision | 6 | reference_lookup | identical->COAMAP.DONE_EXISTING;new_or_approved_update->COAMAP.DEPENDENCIES;different->COAMAP.NEEDS_DIRECTION;pending->COAMAP.DEPENDENCIES | COAMAP.FIND_TARGET | stop | Always |
