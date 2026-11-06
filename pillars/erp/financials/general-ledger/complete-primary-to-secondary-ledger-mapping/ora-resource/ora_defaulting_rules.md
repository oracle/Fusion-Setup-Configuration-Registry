# Complete Primary to Secondary Ledger Mapping Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Existing relationship and journal-rule fields | Preserve exact export | Any relationship or rule already exists | No; change only fields owned by an approved supported delta | resolve_existing_relationship |
| Name4 | Intentional blank | Source and target use the same structure instance and the GL-781805 warning is accepted | No; never invent or later preassign a mapping through this flow | resolve_primary_secondary_relationship |
| Name4 | Exact directional mapping name | Structure instances differ | No; user selects the business mapping and the resolver supplies its exact identity | resolve_directional_coa_mapping |
| AlcDefaultConvRateTypeTrans | Intentional blank | Source and target currencies are the same | No | resolve_existing_relationship |
| AlcDefaultConvRateTypeTrans | Exact user-selected rate type | Source and target currencies differ | No; Corporate is not a default | find_conversion_rate_type_exact |
| OrgIdTrans | Preserve exact export value, including -99 or -1 | Every existing relationship; Name4 assignment is not a key transition | No; never default, normalize, or rewrite the key | resolve_existing_relationship |
| RelationshipEnabledFlag | Preserve exact export; controlled new relationship remains N | Mapping is completed but activation is not authorized | No | resolve_existing_relationship |
| InheritCreationUser | Y | Exact same-release matching-role controlled relationship and export does not already own a value | Preserve existing; disclose controlled default | resolve_existing_relationship |
| AutomaticPostFlag | N | Exact same-release matching-role controlled relationship and export does not already own a value | Preserve existing; user-requested enablement requires exact supported contract | resolve_existing_relationship |
| AlcNoRateActionCode | REPORT_ERROR | Exact same-release matching-role controlled relationship and export does not already own a value | Preserve existing; disclose controlled default | resolve_existing_relationship |
| AlcInheritConversionType | Y | Exact same-release matching-role controlled relationship and export does not already own a value | Preserve existing; disclose controlled default | resolve_existing_relationship |
| Journal catch-all | Preserve existing; Other or Other with Y and Y only for exact controlled Journal-secondary role | Matching controlled role requires its proven row | No universal default for Subledger or arbitrary existing relationships | resolve_existing_conversion_rules |
| BSV tree, replication, dates, versions, DFFs, and initialization fields | Intentional blank or preserve exact export | Feature was not explicitly selected or exact same-role contract is absent | No; route requested unsupported setup to the UI |  |
| TargetLedgerId, target ShortName, audit, request, status, and process fields | Service owned | New service-generated identity or lifecycle evidence | No |  |

## Population Classes

| Class | Rule |
|---|---|
| User supplied | Source and target scope; conditionally mapping, rate policy, BSV values, or initialization intent remain business decisions |
| Resolver derived | Codes, IDs, parent attributes, effective values, and mapping direction come only from exact receipts |
| Export derived | Every existing field and row is preserved unless this task owns the approved smallest delta |
| Controlled role default | Apply only to a fresh same-release export with an exact matching relationship role and feature state; never use prevalence as portability proof |
| Intentional blank | Preserve valid blanks for same-COA Name4, same-currency rate, unselected initialization/replication/tree/DFF features, and service-generated fields |
| Service owned | Never fabricate ledger IDs, short names, audit values, lifecycle status, process identity, request identity, or manifest metadata |

## Member and Field Population

| Member | Population Behavior |
|---|---|
| ORA_GL_LEDGER_RELATIONSHIP.csv | Own the exact approved relationship delta: directional Name4 when required, user-selected rate type when required, and only exact supported relationship fields; preserve OrgIdTrans, RelationshipTypeCode, and all other parent-key fields |
| ORA_GL_JOUNAL_CONVERSION_RULES.csv | Preserve every child parent OrgId alias exactly with its exported relationship tuple; preserve all existing rules; create only the exact controlled matching-role catch-all and never synthesize selective or universal Subledger policy |
| ORA_PRIMARY_BALANCING_SEGMENT_VALUE_CONVERSION_RULES.csv | Header-only unless controlled conversion was explicitly selected; each row uses exact parent tuple plus required SourceSegmentValue and Meaning; optional columns remain blank unless deployed and requested |
| GL_LEDGER_SEG_VAL_ASSIGNMENT.csv | Preserve unless explicit direct assignment is separately selected and supported; no row when the owning ledger uses BalSegValueOptionCode A |
| GL_LEDGER.csv and ORA_GL_PRIMARY_LEDGER_CONFIG.csv | Dependency closure only; preserve rows and actual headers |
| GL_PRIMARY_LEDGER.csv and GL_SECONDARY_LEDGER.csv | Preserve both 133-column physical aliases symmetrically; mapping does not own ledger-option changes |
| ORA_GL_JOURNAL_CONFIG_DETAIL.csv and ORA_LEGAL_ENTITY_BAL_SEG_VAL_DEF.csv | State/dependency closure only; never synthesize rows |
| ASM_SETUP_CSV_METADATA.xml | Preserve the current export graph; never hand-author, reorder, or copy from another scope |

## Physical Field-Family Policy

| Physical Area | Exact Policy |
|---|---|
| Relationship parent and role | Preserve exact source/target names, categories, conversion level, currency, ApplicationShortName, and all ten parent-key columns; never rebuild a child key from display text alone |
| Relationship lifecycle | Mapping completion owns no OrgIdTrans transition; preserve the exported key, relationship status/enabled state, InheritCreationUser, AutomaticPostFlag, AlcNoRateActionCode, AlcInheritConversionType, target service ID/ShortName, disable dates, and initialization fields unless an explicit supported choice owns them |
| Relationship structural/rate options | Populate Name4 only from the exact directional mapping when COAs differ and the rate type only from user choice when currencies differ; preserve RevalFromPriLgrCurr and all other translation/rate-policy fields by relationship type |
| Relationship BSV options | Preserve tree code/version, replication flag, replication date, segment-value/type fields, and related optional attributes unless a controlled exact-role design was explicitly selected; otherwise use the UI handoff |
| Journal-rule parent | Preserve the exact exported ten-column relationship parent tuple, including OrgIdTrans and RelationshipTypeCode; never rewrite child aliases merely to assign a COA mapping |
| Journal-rule body | Keep source/category key and name coherent with UserUpdatableFlag and IncludeFlag; preserve relationship conversion flags/rate in columns 38 and 39; DFFs are opt-in and audit fields are service owned |
| BSV conversion body | SourceSegmentValue and Meaning are required for each authored row; DFF/date/number fields remain blank unless deployed and explicitly requested; audit fields remain service owned |
| Direct BSV assignment body | Preserve parent keys, exact SegmentValue, LedgerName, optional dates, SLA sequencing, legal-entity and DFF values; SegmentTypeCode/SegmentValueTypeCode require exact same-role evidence |
| Both 133-column aliases | Preserve all identity, calendar, COA/segment, method/SLA, option/account, sequencing, rate, threshold, strict-close, ADB, currency-journal, posting-cutoff, DFF, helper, and audit fields symmetrically |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| GLMAP.DEFAULTS | step | 40 | apply_default | applied->GLMAP.ENFORCE | GLMAP.LOOKUPS | stop | Exact resolver and export receipts are available |
