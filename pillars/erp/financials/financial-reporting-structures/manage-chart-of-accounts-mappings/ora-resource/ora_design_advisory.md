# Design Advisory

## Guidance Sources

| Source Mode | Allowed Sources | When Used |
|---|---|---|
| Functional | Oracle 26C Chart of Accounts Mapping functional documentation listed below | Mapping behavior, rule methods, precedence, hierarchies, and application workflow |
| Interface | Current Oracle Chart of Accounts Mapping Rules Import XLSM and 26C import-processing documentation | Exact FBDI contract, codes, files, modes, and warnings |
| Data model | Oracle 26C GL_COA_MAPPINGS, GL_COA_MAP_SEGMENT_RULES, and GL_COA_MAP_ACCOUNT_RULES documentation | Object meaning, parent-child relationships, lengths, identity, and concurrency |
| CodeSearch EO and VO | CoaMappingEO, CoaMapSegmentRuleEO, CoaMapRollupRuleEO, GlCoaMapMsRollupRulesEO, CoaMapAccountRuleEO, CoaMappingVO, ChartOfAccountsVVO, CoaMapSegmentRuleVO, CoaMapRollupRuleVO, CoaMapAccountRuleVO, CoaValueSetIdVO, CoaValueSetMaxSizeVO, SegmentMapMethodVO, LedgerRelVO, and KFFSegmentVO | EO-backed validation and VO or LOV-backed lookup evidence supplied for this update |
| Repository | Setup-task catalog and shared FDOS export, validation, import, authentication, and FSM-client contracts | Routing and persistence |
| Implementation | User's Chart of Accounts Mapping Skills Generation Prompt | Required operational gates and embedded best-practice rules |

## Oracle Source Catalog

| Source ID | Source |
|---|---|
| FUNC-01 | https://docs.oracle.com/en/cloud/saas/financials/26c/faigl/segment-rules-and-account-rules-for-chart-of-accounts-mapping.html |
| FUNC-02 | https://docs.oracle.com/en/cloud/saas/financials/26c/faigl/overview-of-the-chart-of-accounts-mapping-page.html |
| FUNC-03 | https://docs.oracle.com/en/cloud/saas/financials/26c/faigl/create-a-mapping-with-multiple-source-segments.html |
| FUNC-04 | https://docs.oracle.com/en/cloud/saas/financials/26c/faigl/how-chart-of-accounts-mapping-segment-rules-import-data-is-processed.html |
| FUNC-05 | https://docs.oracle.com/en/cloud/saas/financials/26c/faigl/what-s-the-difference-between-mapping-with-segment-rules-and.html |
| FUNC-06 | https://docs.oracle.com/en/cloud/saas/financials/26c/faigl/when-do-account-rules-override-segment-rules-in-a-chart-of.html |
| FUNC-07 | https://docs.oracle.com/en/cloud/saas/financials/26c/faigl/hierarchies-for-cross-validations-revaluations-and-chart-of.html |
| EDM-01 | https://docs.oracle.com/en/cloud/saas/financials/26c/oedmf/glcoamappings-15075.html |
| EDM-02 | https://docs.oracle.com/en/cloud/saas/financials/26c/oedmf/glcoamapaccountrules-6345.html |
| EDM-03 | https://docs.oracle.com/en/cloud/saas/financials/26c/oedmf/glcoamapsegmentrules-19021.html |
| FBDI-01 | Current Oracle Financials FBDI guide, Chart of Accounts Mapping Rules Import entry and downloaded XLSM |
| REPO-01 | knowledge/setup-task-catalog/setupTasksAll.json |
| USER-01 | User's Chart of Accounts Mapping Skills Generation Prompt |
| EO-01 | CoaMappingEO.xml, CoaMapSegmentRuleEO.xml, CoaMapRollupRuleEO.xml, GlCoaMapMsRollupRulesEO.xml, CoaMapAccountRuleEO.xml |
| VO-01 | CoaMappingVO.xml, ChartOfAccountsVVO.xml, CoaMapSegmentRuleVO.xml, CoaMapRollupRuleVO.xml, CoaMapAccountRuleVO.xml, CoaValueSetIdVO.xml, CoaValueSetMaxSizeVO.xml, SegmentMapMethodVO.xml, LedgerRelVO.xml, KFFSegmentVO.xml |
| REST-01 | GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV and GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV/{StructureInstanceId} |
| REST-02 | https://docs.oracle.com/en/cloud/saas/applications-common/26c/farca/api-value-sets.html |
| REST-03 | https://docs.oracle.com/en/cloud/saas/applications-common/26c/farca/api-value-sets-values.html |

## Source Mapping

| Rule or Decision | Source Evidence |
|---|---|
| Mapping correlates one source chart to one target chart | FUNC-01, EDM-01 |
| Segment methods and copy-value identical-value requirement | FUNC-01, EDM-03 |
| Single-source and hierarchy rollups | FUNC-01, FUNC-07 |
| Exactly two source segments, Use rollup rules, and Equal to | FUNC-03 |
| Segment and account rules may coexist | FUNC-01, FUNC-05 |
| Account rules supersede overlapping segment rules | FUNC-06 |
| Account selectors and effective parent expansion | FUNC-01, EDM-02 |
| Application page tabs, upload, import, and unprocessed-rule actions | FUNC-02, FUNC-04 |
| Account rules are excluded from FBDI | FUNC-04 |
| Account rules are supported by FSM task-CSV import when derived from the current same-task export | User-confirmed FSM import capability and current export contract |
| Current template controls columns, tooltips, order, CSV, and ZIP | FUNC-04, FBDI-01 |
| Increment default, Replace deletion risk, and all-or-nothing mapping import | FUNC-04 |
| Mapping name 33 and description 240 application limits | EDM-01 |
| Mapping is parent to segment and account rules | EDM-01, EDM-02, EDM-03 |
| One segment rule per mapping and target segment | EDM-03 |
| Account description 1,000 and logical business identity | EDM-02, USER-01 |
| Object version is concurrency evidence | EDM-01, EDM-02, EDM-03 |
| Hierarchy flatten, audit, active, association, and redeployment | FUNC-07 |
| Essbase publication is not required solely for mapping | FUNC-07, USER-01 |
| First-go readiness, existence comparison, approval, and source precedence | USER-01 |
| COA resolution, mapping-name duplicate error, EO method semantics, rollup bounds, and account-rule identity | EO-01 |
| COA, segment, value-set, maximum-size, and method lookup evidence | VO-01 |
| Read-only source and target COA resolution for mapping validation; template/spec export is independent | REST-01 |
| Read-only value-set definition lookup and returned child-values navigation | REST-02, REST-03 |
| Catalog task identity and supported CSV routing | REPO-01 |
| Mapping is conditional, not baseline COA setup | User-approved review direction |

## Guidance Topics

| Topic | Advisory Level | What To Explain | Do Not Include |
|---|---|---|---|
| Segment rules | Broad design | Map every target segment by constant, copy, or rollup with complete reference validation | Do not use a segment rule as a hidden account exception |
| Account rules | Precision exception | Map complete target combinations from supported source criteria, disclose overlaps, and use export-derived ORA_GL_AFF_MAP_RULE.csv for FSM task-CSV import | Do not generate FBDI mapping-rules rows or invent FSM CSV columns |
| Multiple-source rollup | Restricted design | Use exactly two source segments, Use rollup rules, and Equal to | Do not generalize to more segments or operators |
| Hierarchies | Date-effective dependency | Select the associated active hierarchy version effective on the accounting date | Do not require Essbase publication unless another business use requires it |
| Ledger relationship | Applicability context | Use LedgerRelVO evidence only to explain an approved secondary-ledger or cross-ledger mapping context when available | Do not infer a mapping requirement or a public mapping REST endpoint from the VO |
| Import readiness | Mandatory gate | Resolve the current template contract and every technical value before the first live attempt | Do not learn defaults from failed imports |
| Applicability | Scope gate | Use mappings only when the approved design requires a distinct source-to-target COA mapping, such as a balance-level secondary-ledger or cross-ledger transfer | Do not include mappings in a baseline COA setup solely because the task is available |
| Enterprise Data Model | Semantic evidence | Use relationships, lengths, identity, and concurrency meaning | Do not generate SQL, direct-table access, unsupported REST, or FBDI values from physical columns |

## Output Rules

| Situation | What Happens |
|---|---|
| Segment and account results overlap | List the source combination, both target results, and the account-rule effective result. |
| Current template and EDM length differ | Apply the stricter limit to the import artifact and preserve the application-level validation separately. |
| Existing object is identical | Report it and stop without duplicate creation. |
| Existing object differs | Show field-level and rule-level differences and request direction. |
| Separate best-practices attachment is unavailable | Do not attribute any rule to an unseen document; identify the source gap in handoff. |
