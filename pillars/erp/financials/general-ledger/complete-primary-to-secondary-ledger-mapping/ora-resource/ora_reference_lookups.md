# Complete Primary to Secondary Ledger Mapping Reference Lookups

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| acquire_scoped_mapping_package | No validated current project package is available | Environment; release; task code; accounting-configuration scope; export receipts; downloaded ZIP | Accept exactly one current package whose task, scope, release, ten CSV members, actual headers, both aliases, and manifest graph all match | Baseline ZIP; provenance; checksum; headers; semantic keys; manifest graph | Block with FSM_EXPORT_UNAVAILABLE or exact package mismatch details; never substitute a stale or unrelated export |
| resolve_primary_secondary_relationship | Primary and secondary names are present | Raw names; scoped ledger aliases; ORA_GL_LEDGER_RELATIONSHIP rows | Match exactly one source PRIMARY and target SECONDARY relationship in the requested scope and preserve the exact parent tuple | Source and target names; categories; conversion level; structures; currencies; OrgIdTrans; relationship flags; parent tuple | Zero means no scoped relationship; many means ambiguous scope; show candidate semantic keys and block |
| resolve_directional_coa_mapping | Source and target structures differ | Exact source and target structure identities; scoped Financial Reporting Structures mapping-task export | Match exactly one mapping in From source structure to To target structure direction | Name4; source structure; target structure; mapping receipt | Zero or many blocks the different-COA path; never reverse, fuzzy-match, or take the first row |
| derive_balancing_value_set | Controlled BSV conversion is explicitly selected | Exact source COA name and identity; current task-level export inventory for Manage Chart of Accounts Structure Instances GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES and Manage Chart of Accounts Structures GL_MANAGE_CHARTS_OF_ACCOUNTS | Reuse a current same-environment and same-release populated export containing the exact source structure instance. If none exists or the package is header-only, trigger a scoped task-level export of Manage Chart of Accounts Structure Instances; Manage Chart of Accounts Structures is an allowed equivalent when it contains the same selected rows. Join ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_INSTANCE.csv to ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_SEGMENT.csv by StructureCode, then to ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_SEGMENT_LABEL.csv by StructureCode and SegmentCode, and to ORA_FND_APP_KEY_FLEXFIELD_STRUCTURE_INSTANCE_SEGMENT.csv by StructureInstanceCode and SegmentCode. Require KeyFlexfieldCode GL# and exactly one GL_BALANCING label, then derive that segment's ColumnName and instance ValueSetCode only from the export | ValueSetCode; BalSegColumnName; StructureInstanceCode; StructureCode; SegmentCode; exact export receipt | Missing or stale evidence triggers the named task export. An absent selected structure after successful populated export, a join mismatch, incomplete metadata, or zero/multiple balancing labels blocks BSV authoring; never use REST describe metadata or assume SEGMENT1/value-set code |
| resolve_existing_relationship | Mapping an existing relationship or validating a proposed key change | Exact relationship row and child-rule parent tuples from the package | Match one relationship by its full exported parent tuple; retain its actual OrgIdTrans without assuming a pre-mapping value | Current relationship row; exported OrgIdTrans; exact child parent keys | Missing, ambiguous, or inconsistent parent references block mutation and require a fresh scoped export; a requested key transition requires separate evidence and is outside the baseline mapping delta |
| resolve_existing_conversion_rules | Existing rules are present or a controlled catch-all/UI handoff decision is needed | Exact ORA_GL_JOUNAL_CONVERSION_RULES rows for the relationship | Match every existing row by full parent tuple plus source/category key and name; preserve zero, one, or many as actual scoped state | Rule rows; semantic keys; flags; parent aliases; relationship rate flags | Malformed keys or duplicate semantic rows block; zero rows is a valid existing state and is not permission to synthesize custom rules |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_conversion_rate_type_exact | Source and target currencies differ | Raw rate-type display value | /fscmRestApi/resources/11.13.18.05/currencyConversionTypesLOV | ConversionType; UserConversionType; EnabledFlag and available effective fields | Use tested ADF q syntax q=UserConversionType='raw value'; page until hasMore=false; accept exactly one enabled and effective exact display match | AlcDefaultConvRateTypeTrans; canonical display; eligibility receipt | Successful zero is unknown or ineligible; many is ambiguous; HTTP, auth, authorization, timeout, or malformed response is resolver failure, never value not found |
| verify_balancing_value_set_exact | Controlled BSV conversion is selected after the source COA export derives ValueSetCode | Exact source ValueSetCode and balancing-role receipt | /fscmRestApi/resources/11.13.18.05/valueSets | ValueSetCode; ValueSetId; Description; ValidationType; EnabledFlag when available | Page until hasMore=false and accept exactly one exact value-set-code match that agrees with the source balancing-role receipt | Verified ValueSetCode; ValueSetId when needed; validation receipt | Successful zero or many blocks BSV authoring; HTTP/auth/client failure remains a resolver failure and never licenses a guessed ID |
| find_balancing_segment_value_exact | A BSV conversion row is requested after ValueSetCode is known | Exact ValueSetCode; raw source segment value; requested effective date | /fscmRestApi/resources/11.13.18.05/valueSets/{ValueSetCode}/child/values | Value; Description or Meaning; EnabledFlag; StartDateActive; EndDateActive; ValueSetCode | Use the code-keyed child path; page until hasMore=false; accept exactly one exact value in the correct value set that is enabled and effective on the requested date | SourceSegmentValue; Meaning; ValueSetCode; effective-state receipt | Successful zero or many blocks the row; report value set and date; transport/auth/client failures remain resolver failures |

## Unsupported Live Lookup Boundary

| Endpoint | Supported Use | Failure Contract |
|---|---|---|
| /fscmRestApi/resources/11.13.18.05/journalSourcesLOV | Documentation/evidence only; not a baseline dependency because selective custom journal policy is UI-owned under closed GL-13 | A 403 is authorization failure, never proof that a source is absent; preserve existing rules and use the mapping UI |
| /fscmRestApi/resources/11.13.18.05/journalCategoriesLOV | Documentation/evidence only; not a baseline dependency because selective custom journal policy is UI-owned under closed GL-13 | A 403 is authorization failure, never proof that a category is absent; preserve existing rules and use the mapping UI |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Free-text matching | Retain raw input and a separate normalized-presence value; whitespace-only is missing; do not change internal whitespace or case and do not fuzzy-match |
| ADF filtering | Use q=Field='value' syntax with escaping appropriate to the client; request only required fields and page until hasMore is false |
| Exact one eligible result | Store display value, authoritative code or ID, match count one, source, request filter, effective date when applicable, validation timestamp, and decision |
| Successful zero results | Report unknown or ineligible with endpoint or export source and exact filter; do not broaden silently |
| Multiple results | Report ambiguity and candidate business keys; require a more precise user choice |
| 401 or 403 | Refresh an eligible local cached access token once under repository policy, then stop with auth or authorization diagnostics; never relabel as no match |
| 429, 5xx, or timeout on GET | Use bounded backoff only for the read-only GET and retain attempt diagnostics |
| 400, malformed payload, client failure, or final auth failure | Stop without blind retry and show HTTP status, client message, request correlation or trace identifier when available, endpoint, and safe remediation |
| Journal source or category lookup unavailable | It is not a baseline dependency under the closed GL-13 policy; preserve existing rows and use the named UI handoff for custom policy |

## Resolver Receipt

| Field | Required Content |
|---|---|
| Input evidence | Raw value; normalized-presence value; user or export source; task; source ledger; requested effective date |
| Resolver evidence | Resolver name; endpoint or export identity; exact filter or semantic key; requested fields; page completion; HTTP/result state |
| Decision evidence | Match count; eligibility; authoritative display/code/ID; validation time; accepted, rejected, ambiguous, or resolver-failed decision |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| GLMAP.LOOKUPS | decision | 30 | reference_lookup | resolved->GLMAP.DEFAULTS;blocked->GLMAP.RETURN_ISSUES | GLMAP.DEPENDENCIES | stop | Dependency lookups are applicable |
