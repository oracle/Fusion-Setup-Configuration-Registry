# Manage Data Access for Users Reference Lookups

## Common Section

### User, Role, and Membership Semantics

These eligibility and membership rules apply to FSM and REST mutations. Customer REST reads use the separate scope rules below.

| Purpose | Resource | Required fields | Match rule |
|---|---|---|---|
| Target user | `GET /hcmRestApi/resources/11.13.18.05/userAccounts` | `Username,GUID,UserId,SuspendedFlag` | Use a quoted Username predicate, complete pagination, case-fold equality, `SuspendedFlag=false`, then deduplicate by GUID/UserId |
| Role | `GET /hcmRestApi/resources/11.13.18.05/rolesLOV` | `RoleId,RoleName,RoleCode,ActiveFlag,DataRole` | Exact RoleName or RoleCode, `ActiveFlag=true`, `DataRole=N`, then deduplicate by RoleId/RoleCode |
| Membership | `GET /hcmRestApi/resources/11.13.18.05/userAccounts/{GUID}/child/userAccountRoles` | `RoleId,RoleCode,UserRoleId` | Complete pagination and require the selected RoleId and RoleCode pair |

Build string-valued `q` filters under Query Syntax and Framework below, including an explicit compatible REST-Framework-Version header on every page. For example, `Username='test.user1'`. Double embedded single quotes under version 2 or later before the query is encoded. Do not issue additional lowercase or uppercase retries; bind Oracle's returned `Username` as canonical. Framework selection does not change mutation eligibility or membership rules.

### Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_active_user | A target user is supplied for a mutation | Supplied user name | /hcmRestApi/resources/11.13.18.05/userAccounts | Username, GUID, UserId, SuspendedFlag | Case-fold exact user name; retain unsuspended identities; deduplicate GUID/UserId | Canonical Username, GUID, UserId | No match blocks; many canonical identities require exact GUID or UserId selection |
| resolve_active_nondata_role | A role display name or code is supplied | Supplied role | /hcmRestApi/resources/11.13.18.05/rolesLOV | RoleId, RoleName, RoleCode, ActiveFlag, DataRole | Exact RoleName or RoleCode; retain active non-data roles; deduplicate RoleId/RoleCode | Canonical RoleId, RoleName, RoleCode | No match blocks; many canonical identities require exact RoleId or RoleCode selection |
| verify_user_role_membership | Canonical user and role are resolved | User GUID, RoleId, RoleCode | /hcmRestApi/resources/11.13.18.05/userAccounts/{GUID}/child/userAccountRoles | RoleId, RoleCode, UserRoleId | Complete pagination and require one canonical RoleId/RoleCode pair | Membership result | Missing or inconsistent membership blocks |
| resolve_rest_assignment | Selected REST mutation planning or uncertain-write recovery | Canonical Username, RoleName, RoleCode, context literal, ordered values | GET /fscmRestApi/resources/11.13.18.05/dataSecurities | UserRoleDataAssignmentId, UserName, RoleNameCr, RoleCommonName, SecurityContext, SecurityContextValue, SecurityContextValue2, SecurityContextValue3, ActiveFlag | REST Assignment Collection Contract, complete pagination, and Exact Assignment Matching below | Complete flag; per-row absent, active, or inactive state; matching assignment ID | Zero means absent only after complete successful retrieval; distinct exact IDs are ambiguous; invalid state or incomplete evidence blocks |
| list_rest_assignments | Selected REST List/search or requested result window | Supplied predicates or explicit all-assignment scope; validated read options | GET /fscmRestApi/resources/11.13.18.05/dataSecurities | Read Projection and Ordering below | List Scope Resolution and selected Pagination Mode; no mutation identity or cardinality requirements | Filter scope, requested/applied options, assignments, returned_count, requested_scope_complete, collection_complete, continuation | complete or window_complete is successful, including empty results; invalid_scope, incomplete, or failed preserves the requested scope |
| get_rest_assignment | Selected REST read of one assignment ID without additional predicates | Selected environment, validated UserRoleDataAssignmentId, optional requested fields | GET /fscmRestApi/resources/11.13.18.05/dataSecurities/{UserRoleDataAssignmentId} | Read Projection and Ordering below | Get One Assignment contract; no mutation eligibility or membership checks | Read mode, requested/applied options, assignment, found status, returned_count, requested_scope_complete | found or not_found is definitive; invalid_scope or failed never becomes not_found |
| count_rest_assignments | Selected REST assignment count | Supplied predicates or explicit all-assignment scope; exact or estimated count kind | GET /fscmRestApi/resources/11.13.18.05/dataSecurities | UserRoleDataAssignmentId for exact retrieval; totalResults for estimate | Count Assignments contract; complete ID retrieval for exact count or valid API estimate | Filter scope, count kind, count, requested_scope_complete, collection_complete, retrieval/continuation evidence | complete for requested count mode; invalid_scope, incomplete, or failed never supplies a false exact count or substitutes zero |
| verify_rest_assignment | Later results/verification request after Data Loader terminal success for the bound REST artifact | Approved environment, complete submitted identity, reconciled assignment ID when known, desired state, and successful submission linkage | GET /fscmRestApi/resources/11.13.18.05/dataSecurities/{UserRoleDataAssignmentId}; complete collection resolver for a created or unknown ID | REST assignment projection below | Post-Load Verification below; exact approved tuple and boolean desired state | verified, mismatch, or unverified with sanitized evidence | Missing item, identity/state mismatch, or failed readback never authorizes replay |
| resolve_rest_loader_contract | REST planning with writes needed, or final-artifact Task Hook validation | Selected environment, supplied loader discriminator or dataSecurities search candidate, selected lifecycle operation, retained current core schema evidence on re-entry | GET /hcmRestApi/resources/latest/dataLoaderBusinessObjects and its registered template/component/attribute GETs, delegated only through core.data-loader | BusObjTopDiscriminator, UcmContentId, registered section/attribute/key metadata | REST Loader Contract Resolution below; derive the selected operation's minimal source from current registered schema and MDA assignment rules | Exact business object, current sample workbooks, section/key/field mapping, operation-specific source shape, target/fingerprints | Missing or ambiguous registration, unavailable metadata, mismatched target, missing needed fields/keys, or contradictory schema blocks; no direct write or method fallback |

### Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_mutation_context_label | MDA.VALIDATE_INPUT for each mutation row, before any missing-context decision; never for customer reads or FSM export/list | Explicit context label or label phrase for this row and the local Security Context Mapping in this file | Mutation Context Label Resolution below; no external call | context_resolution: status, input_label, canonical_context, rest_security_context, object_name, datasec_context_type_code, ordered_fsm_carriers, source | missing, unknown, or conflicting requires clarification; invalid_catalog blocks as a resource failure; never substitute a context |

#### Mutation Context Label Resolution

1. Load the Security Context Mapping in this file before deciding whether the
   context input is missing or supported. If the table is missing, unreadable,
   malformed, or assigns one normalized alias to different contexts, return
   invalid_catalog. Do not classify a resource failure as missing customer input.
2. Extract only the explicit context label or label phrase associated with this
   mutation row. In a phrase such as "DAS access", "access" is the request suffix
   and "DAS" is the label. Never search the business value, username, or role for
   aliases. A value containing "DAS" does not supply a context label. Keep all
   business values unchanged.
3. Match the complete label against the canonical names, approved aliases, and
   primary FSM carriers in the table using its case/separator normalization.
   Do not use substring or fuzzy matches, invent acronym expansions, or shorten
   a complete label to a different approved label. A generic suffix does not
   invalidate an otherwise exact approved alias.
4. Return resolved for one canonical context. Repeated equivalent labels for
   that row agree; explicit labels selecting different contexts return
   conflicting. Return missing if no context label was supplied and unknown
   for a supplied label with no approved match. Generic words alone do not
   identify a context. Do not choose a replacement based on the value or role.
5. Return context_resolution with status, input_label, canonical_context,
   rest_security_context, object_name, datasec_context_type_code,
   ordered_fsm_carriers, and source. Copy mapping fields exactly from the
   matched row; use an empty type code for the table's blank value. For an
   unresolved result, leave mapping fields unset. Source identifies this file,
   the Security Context Mapping heading, and the matched row when resolved.
   Keep raw input in runtime state and apply the existing redaction rules to
   persisted evidence. This result proves label mapping only, not value
   existence or assignment eligibility.

The returned mapping fields are internal evidence. FSM uses its ObjectName,
context-type code, and carriers under the existing package rules. REST uses the
mapped literal and ordered business values under its registered loader field
contract; never serialize context_resolution or its FSM metadata into loader rows.
This resolver does not call resolve_role_object_mapping or make a role/object
catalog match a REST prerequisite.

### Security Context Mapping

This section is the sole source of truth for supported mutation Security Context names, approved aliases, context types, `DatasecContextTypeCode` values, `ObjectName` values, ordered FSM carrier fields, and mapped REST literals. Customer reads also accept explicitly supplied REST literals and patterns under Read Scope Resolution; this mutation table is not an exhaustive read-literal whitelist. Other MDA resource files must reference this mapping and must not duplicate individual context definitions.

Label matching is case-insensitive and may normalize whitespace, `-`, `_`, `.`, and `/`. The context value is a separate exact input and never proves the context label. An exact primary FSM carrier name is also an approved alias.

FSM uses `ObjectName`, context-type code, and carrier columns. REST uses the exact `REST SecurityContext literal`; input-alias normalization must not alter this literal or the supplied values. Bind the first ordered business value to `SecurityContextValue`, and the second/third to `SecurityContextValue2`/`SecurityContextValue3` only when the selected context requires them. The existing ordered carriers define the number and order of business inputs, not REST field names.

| Security Context | Approved labels | REST `SecurityContext` literal | Context type | `DatasecContextTypeCode` | `ObjectName` | Ordered FSM carriers |
|---|---|---|---|---|---|---|
| Business Unit | Business Unit; BU; BuName | `Business unit` | Standard | blank | `FUN_ALL_BUSINESS_UNITS_V` | `BuName` |
| Ledger | Ledger; Name | `Ledger` | Standard | blank | `GL_LEDGERS` | `Name` |
| Intercompany Organization | Intercompany Organization; Intercompany Org; Interco Organization; Interco Org; IntercoOrgName | `Intercompany organization` | Standard | blank | `FUN_INTERCO_ORGANIZATIONS` | `IntercoOrgName` |
| Control Budget | Control Budget; CntrlbudgetName | `Control budget` | Standard | blank | `XCC_CONTROL_BUDGETS` | `CntrlbudgetName` |
| Project Organization Classification | Project Organization Classification; Project Org Classification; PrjorgName | `Project organization classification` | Standard | blank | `HR_ORG_UNIT_CLASSIFICATIONS_F` | `PrjorgName` |
| Cost Organization | Cost Organization; Cost Org; CostOrgName | `Cost organization` | Standard | blank | `CST_COST_ORGS_V` | `CostOrgName` |
| Asset Book | Asset Book; Fixed Asset Book; BookTypeCode | `Asset book` | Standard | blank | `FA_BOOK_CONTROLS` | `BookTypeCode` |
| Reference Data Set | Reference Data Set; Reference Set; RDS; SetName | `Reference data set` | Standard | blank | `FND_SETID_SETS_VL` | `SetName` |
| Data Access Set | Data Access Set; DAS; AccesssetName | `Data access set` | Standard | blank | `GL_ACCESS_SETS` | `AccesssetName` |
| Manufacturing Plant | Manufacturing Plant; Mfg Plant; MfgOrganizationCode | `Manufacturing plant` | Standard | blank | `RCS_MFG_PARAMETERS` | `MfgOrganizationCode` |
| Inventory Organization | Inventory Organization; Inventory Org; Inv Organization; Inv Org; Inv Orgn; OrganizationCode | `Inventory organization` | Standard | blank | `INV_ORG_PARAMETERS` | `OrganizationCode` |
| Academic Organization | Academic Organization; Academic Org; AcademicOrgName | `Academic Organization` | Non-standard | `ORA_ACAD_ORG_ID` | `HER_ACADEMIC_ORG_F` | `AcademicOrgName` |
| Campus | Campus; CampusName | `Campus` | Non-standard | `ORA_CAMPUS_ID` | `HER_CAMPUS_F` | `CampusName` |
| Academic Organization Campus | Academic Organization Campus; Academic Org Campus; AcademicOrgCampusName | `Academic organization campus` | Non-standard | `ORA_ACAD_ORG_CAMPUS_ID` | `HER_ACADEMIC_ORG_CAMPUS` | `AcademicOrgCampusName` |
| Award Organization Hierarchy | Award Organization Hierarchy; Award Org Hierarchy; AwardHierarchyName | `Award Organization Hierarchy` | Non-standard | `ORA_PRJ_AWARD_ORG_HIER_ID` | `GMS_AWARD_HEADERS_B` | `AwardHierarchyName`, `SecurityContextValue2`, `SecurityContextValue3` |
| Budget Level | Budget Level; BudgetLevelName | `Budget level` | Non-standard | `ORA_BUDGET_LEVEL_ID` | `FV_BE_LEVEL_OPERATIONS_V` | `BudgetLevelName`, `SecurityContextValue2` |
| Legal Entity | Legal Entity; LE; Legal Unit; LegalEntityName | `Legal entity` | Non-standard | `ORA_LEGAL_ENTITY_ID` | `XLE_ENTITY_PROFILES` | `LegalEntityName` |

For Award Organization Hierarchy, value 1 is written to `AwardHierarchyName`, value 2 to `SecurityContextValue2`, and value 3 to `SecurityContextValue3`. For Budget Level, value 1 is written to `BudgetLevelName` and value 2 to `SecurityContextValue2`. These are ordered business inputs, not references to CSV column positions.

Do not accept companion or metadata headers such as `SecurityContextValue2`, `SecurityContextValue3`, `DatasecContextValue5`, `ObjectName`, or `DatasecContextTypeCode` as standalone context labels.

## FSM Method

### Common for Grant and Revoke

Use the local mapping resolver and FSM import rules below. The local catalog controls package construction only.

### Grant

Resolve mapping availability; never invoke the Revoke original-date resolver. Follow the conditional mapping-row rules below.

### Revoke

Resolve mapping availability without creating a mapping. Invoke the original-date resolver only for explicitly unknown dates under its declared dependency gate.

### Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_role_object_mapping | FSM mutation: canonical RoleCode and context-derived ObjectName are available after membership verification | Canonical RoleCode, mapped ObjectName, per-row action, and the existing Available Role/Object Mappings table in this file | Apply the existing Available Role/Object Mappings rules and catalog validation in ora_input_validation.md; evaluate the normalized RoleCode/ObjectName pair locally without a Fusion call | Pair classification, matching Application IDs, conditional mapping-row requirement | Listed pair: known_mapping; missing Grant/reactivation pair: catalog_miss_mapping_required; missing Revoke/deactivation pair: catalog_miss_no_mapping_for_revoke; malformed catalog: invalid_catalog. Multiple Application IDs for one pair remain a positive match |

### Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_active_revoke_assignment | At MDA.CHECK_DEPENDENCIES after common checks pass: this row is FSM Revoke, its original StartDateActive is unresolved, and the user indicates the date is unknown | This row's canonical UserName, canonical RoleCode, ObjectName, DatasecContextTypeCode, documented carrier fields and exact values | shared.setup-export.task-level-export with --data for ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS; inspect ORA_FUN_ALL_USER_DATA_ACCESS.csv | ProcessId, observed status, validated data ZIP or available sanitized process log; UserName, RoleName, ObjectName, DatasecContextTypeCode, carrier fields, ActiveFlag, StartDateActive | Persist the attempt receipt and require a completed, validated export before matching. Match the complete row identity and source ActiveFlag=Y. Exactly one matching row with a valid StartDateActive is required. The generated Revoke row uses ActiveFlag=N. | This row's StartDateActive, StartDateSource=derived_from_current_mda_export, receipt reference | Zero matches returns not_found; multiple matches returns ambiguous; pending, failed, download, or persistence problems return export_unavailable with stage/status evidence; missing or malformed source date returns invalid_source_date |

For this FSM Revoke-only resolver:

- Persist a sanitized attempt receipt under the selected project, bound to the environment, exact task, and affected row identities. Retain ProcessId and observed status when available, including when the shared exporter returns while the process is pending.
- Use the shared exporter's configured wait window and polling interval (defaults: 300 seconds and 10 seconds) for initial and resumed Revoke lookups; do not introduce a shorter MDA-specific wait. A pending status or command-tool yield within that window is not a timeout: keep waiting automatically, then download, validate, and continue date resolution when complete. Do not ask the user to check again between polls.
- A pending process does not require a ZIP or log yet. Only after the shared wait window expires, follow the shared timeout policy; on a user-requested retry, use the shared result helper to poll the same ProcessId with the shared wait window; for a completed process, resume any outstanding download.
- For a terminal failure, retain available sanitized diagnostics and do not automatically create another export. If creation is uncertain or an existing process is unresolved, stop rather than blindly re-export.
- Persist and validate the completed data ZIP and assignment CSV before deriving dates or reporting zero matches. A process log is diagnostic evidence, not a date source. Receipt/artifact persistence failure blocks resolution.
- One current, validated export may serve multiple unknown-date Revoke rows in the same environment/task scope. Match each row independently; do not reuse its start date for another row or override a supplied date. Check request identity and evidence freshness before reuse.
- Do not use a data-bearing export as the mutation-package baseline or to replace the FSM role/object mapping lookup.

#### Revoke Data-Export Resume Command

On an explicitly requested retry, use the recorded ProcessId and the same
environment/authentication context as the original export. The result helper
defaults to data mode; it does not accept --project-id or --data. Do not pass
--template-only for this Revoke data lookup. Resolve the output placeholders
to validated request-scoped paths under the selected project's exports folder;
reuse an already validated download instead of overwriting it.

Pass the shared wait budget explicitly: the result helper's default of zero performs only one status check.

```bash
python3 shared/setup-export/task-level-export/scripts/get_setup_task_csv_export_result.py \
  --properties "{selected_properties_path}" \
  --task-code ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS \
  --process-id "{recorded_process_id}" \
  --token-cache "{selected_token_cache_path}" \
  --wait-seconds 300 \
  --poll-interval 10 \
  --output "{project_export_dir}/mda-revoke-lookup-{recorded_process_id}.zip" \
  --log-output "{project_export_dir}/mda-revoke-lookup-{recorded_process_id}-process-log.txt"
```

Exit code 3 means the process is still pending, not that no export was
created. Retain the same ProcessId and per-row unknown-date state. A log or
exit code alone never resolves a start date; validate the completed data ZIP
before matching assignments.

### Available Role/Object Mappings

This reference controls FSM package construction only. A missing pair establishes absence from this local reference, not absence or ineligibility in the target environment. Do not use it as a REST eligibility gate.

The table in this section lists the `RoleCode`, `ObjectName`, and `ApplicationId` combinations for which a role/object mapping is available. Use these records for the package-construction decision; do not scan a full target MDA export.

Determine whether a mapping is available by the normalized pair `(RoleCode,ObjectName)`:

- Trim and uppercase the canonical RoleCode and mapped ObjectName before lookup.
- One or more listed rows for the pair mean `known_mapping`. Preserve every matching Application ID in the validation result, keep `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` header-only for that pair, and generate the assignment row normally.
- More than one Application ID for the pair is valid evidence for one positive pair match. It is not an ambiguity and must not generate multiple mapping rows.
- No listed row means the mapping is not available in this reference. For Grant, create, activate, or reactivate, generate one mapping row for the unique RoleCode/ObjectName pair. For Revoke, remove, or deactivate, do not create a mapping solely to remove access.
- Deduplicate generated mapping rows by RoleCode/ObjectName across the complete package, even when several users or context values use the pair.
- The listed Application ID is reference information only. `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` has no Application ID column, so never place that value in `ApplName` or another field.

When a Grant/reactivation pair is not listed, construct the mapping row in exact Template header order with `RoleName=<RoleCode>`, `ObjectName=<ObjectName>`, blank `ApplName`, blank `CreatedBy`, blank `LastUpdatedBy`, `RecordTypeCode=USER_DEFINED`, and blank `SecurityContext`. Blank `ApplName` intentionally resolves to the user-defined Application ID `-99` in the Fusion import path.

Every generated `ORA_FUN_ALL_USER_DATA_ACCESS.csv` assignment row explicitly uses `RecordTypeCode=USER_DEFINED`, regardless of whether the role or an available mapping is seeded. A seeded role does not imply that a requested assignment or a newly created role/object mapping is seeded.

### Available Mapping Records

| Role Code | Object Name | Application ID |
|---|---|---|
| ORA_ARB_CUSTOMER_ACCOUNT_BILLING_INQUIRY_DISCRETIONARY | FUN_ALL_BUSINESS_UNITS_V | 10475 |
| ORA_CE_CASH_MANAGER_JOB | XLE_ENTITY_PROFILES | 260 |
| ORA_FUN_FINANCIAL_APPLICATION_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 7003 |
| ORA_FV_FEDERAL_BUDGET_MANAGER_JOB | FV_BE_LEVEL_OPERATIONS_V | 8901 |
| ORA_CST_COST_ACCOUNTANT_JOB | FUN_ALL_BUSINESS_UNITS_V | 10096 |
| ORA_CMF_FISCAL_DOCUMENT_SPECIALIST_JOB | FUN_ALL_BUSINESS_UNITS_V | 10477 |
| ORA_FOM_ORDER_ENTRY_SPECIALIST_JOB | FUN_ALL_BUSINESS_UNITS_V | 10500 |
| ORA_PO_PURCHASE_ANALYSIS_ABSTRACT | FUN_ALL_BUSINESS_UNITS_V | 201 |
| ORA_FUN_FINANCIAL_APPLICATION_ADMINISTRATOR_JOB | FND_SETID_SETS_VL | 435 |
| ORA_FUN_FINANCIAL_APPLICATION_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 435 |
| ORA_DOO_ORDER_ADMINISTRATOR_JOB | FND_SETID_SETS_VL | 10008 |
| ORA_DOO_ORDER_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10008 |
| ORA_CST_COST_ACCOUNTANT_JOB | FND_SETID_SETS_VL | 10450 |
| ORA_CST_COST_ACCOUNTANT_JOB | FUN_ALL_BUSINESS_UNITS_V | 10450 |
| ORA_ENQ_QUALITY_ANALYST_JOB | INV_ORG_PARAMETERS | 10530 |
| ORA_ENQ_QUALITY_ENGINEER_JOB | INV_ORG_PARAMETERS | 10530 |
| ORA_WIS_MANUFACTURING_ENGINEER_JOB | INV_ORG_PARAMETERS | 10494 |
| ORA_WIS_MANUFACTURING_ENGINEER_JOB | RCS_MFG_PARAMETERS | 10494 |
| ORA_WSH_SHIPPING_AGENT_JOB | INV_ORG_PARAMETERS | 665 |
| ORA_WSH_SHIPPING_MANAGER_JOB | INV_ORG_PARAMETERS | 665 |
| ORA_HES_BURSAR_JOB | FND_SETID_SETS_VL | 10509 |
| ORA_HES_CASHIER_JOB | FND_SETID_SETS_VL | 10509 |
| FND_INTERNAL_AUDITOR_JOB | INV_ORG_PARAMETERS | 10049 |
| ORA_RCV_RECEIVING_AGENT_JOB | INV_ORG_PARAMETERS | 10049 |
| ORA_CST_COST_ACCOUNTANT_JOB | CST_COST_ORGS_V | 707 |
| ORA_CST_COST_ACCOUNTANT_JOB | FND_SETID_SETS_VL | 707 |
| ORA_CST_COST_ACCOUNTANT_JOB | FUN_ALL_BUSINESS_UNITS_V | 707 |
| ORA_POR_ADVANCED_PROCUREMENT_REQUESTER_ABSTRACT | FUN_ALL_BUSINESS_UNITS_V | 10071 |
| ORA_POR_PROCUREMENT_PREPARER_ABSTRACT | FUN_ALL_BUSINESS_UNITS_V | 10071 |
| ORA_POR_PROCUREMENT_REQUESTER_ABSTRACT | FUN_ALL_BUSINESS_UNITS_V | 10071 |
| ORA_INV_INVENTORY_MANAGER_JOB | INV_ORG_PARAMETERS | 401 |
| ORA_INV_WAREHOUSE_MANAGER_JOB | INV_ORG_PARAMETERS | 401 |
| ORA_INV_WAREHOUSE_OPERATOR_JOB | INV_ORG_PARAMETERS | 401 |
| ORA_QP_PRICING_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 667 |
| ORA_QP_PRICING_ANALYST_JOB | FUN_ALL_BUSINESS_UNITS_V | 667 |
| ORA_QP_PRICING_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 667 |
| ORA_AP_ACCOUNTS_PAYABLE_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 200 |
| ORA_AP_ACCOUNTS_PAYABLE_SPECIALIST_JOB | FUN_ALL_BUSINESS_UNITS_V | 200 |
| ORA_AP_ACCOUNTS_PAYABLE_SUPERVISOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 200 |
| ORA_FND_INTERNAL_AUDITOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 200 |
| ORA_IEX_COLLECTIONS_AGENT_JOB | FND_SETID_SETS_VL | 695 |
| ORA_IEX_COLLECTIONS_MANAGER_JOB | FND_SETID_SETS_VL | 695 |
| ORA_IEX_COLLECTIONS_AGENT_JOB | FUN_ALL_BUSINESS_UNITS_V | 695 |
| ORA_IEX_COLLECTIONS_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 695 |
| ORA_AR_ACCOUNTS_RECEIVABLE_MANAGER_JOB | FND_SETID_SETS_VL | 222 |
| ORA_AR_ACCOUNTS_RECEIVABLE_SPECIALIST_JOB | FND_SETID_SETS_VL | 222 |
| ORA_AR_ACCOUNTS_RECEIVABLE_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 222 |
| ORA_AR_ACCOUNTS_RECEIVABLE_SPECIALIST_JOB | FUN_ALL_BUSINESS_UNITS_V | 222 |
| ORA_EXM_CORPORATE_CARD_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 10016 |
| ORA_EXM_EXPENSE_AUDITOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 10016 |
| ORA_EXM_EXPENSE_AUDIT_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10016 |
| ORA_EXM_EXPENSE_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10016 |
| ORA_WIE_PRODUCTION_OPERATOR_JOB | INV_ORG_PARAMETERS | 10493 |
| ORA_WIE_PRODUCTION_SUPERVISOR_JOB | INV_ORG_PARAMETERS | 10493 |
| ORA_WIE_PRODUCTION_OPERATOR_JOB | RCS_MFG_PARAMETERS | 10493 |
| ORA_WIE_PRODUCTION_SUPERVISOR_JOB | RCS_MFG_PARAMETERS | 10493 |
| ORA_MNT_MAINTENANCE_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10531 |
| ORA_MNT_MAINTENANCE_TECHNICIAN_JOB | FUN_ALL_BUSINESS_UNITS_V | 10531 |
| ORA_MNT_MAINTENANCE_MANAGER_JOB | INV_ORG_PARAMETERS | 10531 |
| ORA_MNT_MAINTENANCE_TECHNICIAN_JOB | INV_ORG_PARAMETERS | 10531 |
| ORA_HER_REGISTRAR_JOB | FND_SETID_SETS_VL | 10508 |
| ORA_HER_REGISTRAR_JOB | HER_ACADEMIC_ORG_CAMPUS | 10508 |
| ORA_HER_REGISTRAR_JOB | HER_ACADEMIC_ORG_F | 10508 |
| ORA_HER_REGISTRAR_JOB | HER_CAMPUS_F | 10508 |
| ORA_CN_INCENTIVE_COMPENSATION_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 283 |
| ORA_CN_INCENTIVE_COMPENSATION_ANALYST_JOB | FUN_ALL_BUSINESS_UNITS_V | 283 |
| ORA_CN_INCENTIVE_COMPENSATION_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 283 |
| ORA_CN_INCENTIVE_COMPENSATION_PLAN_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 283 |
| ORA_GL_GENERAL_ACCOUNTANT_JOB | FUN_INTERCO_ORGANIZATIONS | 101 |
| ORA_GL_GENERAL_ACCOUNTING_MANAGER_JOB | FUN_INTERCO_ORGANIZATIONS | 101 |
| ORA_GL_FINANCIAL_ANALYST_JOB | GL_ACCESS_SETS | 101 |
| ORA_GL_GENERAL_ACCOUNTANT_JOB | GL_ACCESS_SETS | 101 |
| ORA_GL_GENERAL_ACCOUNTING_MANAGER_JOB | GL_ACCESS_SETS | 101 |
| ORA_FA_ASSET_ACCOUNTANT_JOB | FA_BOOK_CONTROLS | 140 |
| ORA_FA_ASSET_ACCOUNTING_MANAGER_JOB | FA_BOOK_CONTROLS | 140 |
| ORA_FA_ASSET_ACCOUNTANT_JOB | FND_SETID_SETS_VL | 140 |
| ORA_FA_ASSET_ACCOUNTING_MANAGER_JOB | FND_SETID_SETS_VL | 140 |
| ORA_FA_ASSET_ACCOUNTANT_JOB | FUN_ALL_BUSINESS_UNITS_V | 140 |
| ORA_FA_ASSET_ACCOUNTING_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 140 |
| ORA_ZX_TAX_ACCOUNTANT_JOB | FND_SETID_SETS_VL | 235 |
| ORA_ZX_TAX_MANAGER_JOB | FND_SETID_SETS_VL | 235 |
| ORA_ZX_TAX_ACCOUNTANT_JOB | FUN_ALL_BUSINESS_UNITS_V | 235 |
| ORA_ZX_TAX_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 235 |
| ORA_ZX_TAX_ACCOUNTANT_JOB | GL_LEDGERS | 235 |
| ORA_ZX_TAX_MANAGER_JOB | GL_LEDGERS | 235 |
| ORA_RCS_SUPPLY_CHAIN_APPLICATION_ADMINISTRATOR_JOB | CST_COST_ORGS_V | 10108 |
| ORA_RCS_SUPPLY_CHAIN_APPLICATION_ADMINISTRATOR_JOB | FA_BOOK_CONTROLS | 10108 |
| ORA_RCS_SUPPLY_CHAIN_APPLICATION_ADMINISTRATOR_JOB | FND_SETID_SETS_VL | 10108 |
| ORA_RCS_SUPPLY_CHAIN_APPLICATION_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 10108 |
| ORA_RCS_SUPPLY_CHAIN_APPLICATION_ADMINISTRATOR_JOB | INV_ORG_PARAMETERS | 10108 |
| ORA_RCS_SUPPLY_CHAIN_APPLICATION_ADMINISTRATOR_JOB | RCS_MFG_PARAMETERS | 10108 |
| ORA_VRM_REVENUE_ANALYST_JOB | FND_SETID_SETS_VL | 10455 |
| ORA_VRM_REVENUE_MANAGER_JOB | FND_SETID_SETS_VL | 10455 |
| ORA_VRM_REVENUE_ANALYST_JOB | FUN_ALL_BUSINESS_UNITS_V | 10455 |
| ORA_VRM_REVENUE_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10455 |
| ORA_VRM_REVENUE_ANALYST_JOB | GL_LEDGERS | 10455 |
| ORA_VRM_REVENUE_MANAGER_JOB | GL_LEDGERS | 10455 |
| ORA_BUDGET_PREPARER_JOB | FA_BOOK_CONTROLS | 10052 |
| ORA_XCC_BUDGET_MANAGER_JOB | FA_BOOK_CONTROLS | 10052 |
| ORA_BUDGET_PREPARER_JOB | FND_SETID_SETS_VL | 10052 |
| ORA_XCC_BUDGET_MANAGER_JOB | FND_SETID_SETS_VL | 10052 |
| ORA_BUDGET_PREPARER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10052 |
| ORA_XCC_BUDGET_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10052 |
| ORA_BUDGET_PREPARER_JOB | XCC_CONTROL_BUDGETS | 10052 |
| ORA_XCC_BUDGET_MANAGER_JOB | XCC_CONTROL_BUDGETS | 10052 |
| ORA_ASM_APPLICATION_IMPLEMENTATION_CONSULTANT_JOB | FND_SETID_SETS_VL | 10566 |
| ORA_CJM_CHANNEL_CLAIMS_MANAGER_JOB | FND_SETID_SETS_VL | 10566 |
| ORA_CJM_CUSTOMER_CHANNEL_PROGRAM_MANAGER_JOB | FND_SETID_SETS_VL | 10566 |
| ORA_CJM_CHANNEL_BUDGET_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10566 |
| ORA_CJM_CHANNEL_CLAIMS_ANALYST_JOB | FUN_ALL_BUSINESS_UNITS_V | 10566 |
| ORA_CJM_CHANNEL_CLAIMS_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10566 |
| ORA_CJM_CUSTOMER_CHANNEL_PROGRAM_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10566 |
| ORA_CJM_SUPPLIER_CHANNEL_MANAGER_JOB | FUN_ALL_BUSINESS_UNITS_V | 10566 |
| ORA_POS_SUPPLIER_SALES_REPRESENTATIVE_JOB | FUN_ALL_BUSINESS_UNITS_V | 10566 |
| ORA_PJF_GRANTS_ACCOUNTANT_JOB | FUN_ALL_BUSINESS_UNITS_V | 10037 |
| ORA_PJF_GRANTS_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 10037 |
| ORA_PJF_LABOR_DISTRIBUTION_ACCOUNTANT_DISCRETIONARY | FUN_ALL_BUSINESS_UNITS_V | 10037 |
| ORA_PJF_PROJECT_ACCOUNTANT_JOB | FUN_ALL_BUSINESS_UNITS_V | 10037 |
| ORA_PJF_PROJECT_ADMINISTRATOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 10037 |
| ORA_PJF_PROJECT_BILLING_SPECIALIST_JOB | FUN_ALL_BUSINESS_UNITS_V | 10037 |
| ORA_PJF_PROJECT_CREATOR_ABSTRACT | FUN_ALL_BUSINESS_UNITS_V | 10037 |
| ORA_PJF_GRANTS_ACCOUNTANT_JOB | GL_LEDGERS | 10037 |
| ORA_PJF_PROJECT_ACCOUNTANT_JOB | GL_LEDGERS | 10037 |
| ORA_PJF_GRANTS_DEPARTMENT_ADMINISTRATOR_JOB | GMS_AWARD_HEADERS_B | 10037 |
| ORA_PJF_PROJECT_ADMINISTRATOR_JOB | HR_ORG_UNIT_CLASSIFICATIONS_F | 10037 |
| ORA_PJF_PROJECT_CREATOR_ABSTRACT | HR_ORG_UNIT_CLASSIFICATIONS_F | 10037 |
| ORA_FND_INTERNAL_AUDITOR_JOB | FND_SETID_SETS_VL | 438 |
| ORA_FND_INTERNAL_AUDITOR_JOB | FUN_ALL_BUSINESS_UNITS_V | 438 |
| ORA_FND_INTERNAL_AUDITOR_JOB | INV_ORG_PARAMETERS | 438 |
| ORA_PJF_GRANTS_ACCOUNTANT_JOB | XLA_GL_LEDGERS | 10037 |
| ORA_PJF_GRANTS_ACCOUNTANT_JOB | XLA_SUBLEDGERS | 10037 |
| ORA_PJF_GRANTS_ACCOUNTANT_JOB | XLA_TRANSACTION_ENTITIES | 10037 |
| ORA_PJF_PROJECT_ACCOUNTANT_JOB | XLA_GL_LEDGERS | 10037 |
| ORA_PJF_PROJECT_ACCOUNTANT_JOB | XLA_SUBLEDGERS | 10037 |
| ORA_PJF_PROJECT_ACCOUNTANT_JOB | XLA_TRANSACTION_ENTITIES | 10037 |
| ORA_PJF_PROJECT_BILLING_SPECIALIST_JOB | XLA_GL_LEDGERS | 10037 |
| ORA_PJF_PROJECT_BILLING_SPECIALIST_JOB | XLA_SUBLEDGERS | 10037 |
| ORA_PJF_PROJECT_BILLING_SPECIALIST_JOB | XLA_TRANSACTION_ENTITIES | 10037 |

### FSM Import Resolvers

- The canonical RoleCode is stored in the CSV `RoleName` field.
- The bundled catalog decision determines whether the package also needs a user-defined `RoleName` and `ObjectName` mapping row.
- Fusion import resolves the exact `RoleName` and `ObjectName` pair after the mapping batch is processed.
- Fusion import dispatches the selected context branch and resolves its exact carrier values.
- A missing or non-unique import match rejects the row.
- No separate public role/context or context-value prevalidation endpoint is required by this skill.

## REST Method

### Common for Grant and Revoke

Use the collection, pagination, and exact-match contracts below. Operation selection belongs to the single lifecycle table in SKILL.md.

### Grant

Reconcile before create/reactivate/no-op planning and verify any approved write through verify_rest_assignment.

### Revoke

Reconcile before deactivate/no-op planning and verify any approved write through verify_rest_assignment. Do not invoke the FSM date resolver.

### Assignment Collection Contract

The finder below scopes mutation reconciliation: its q predicate filters that finder-bound collection and does not replace mutation identity. Customer collection reads instead use Read Collection Selection below and do not require both user and role.

Use `GET /fscmRestApi/resources/11.13.18.05/dataSecurities`.

**Finder inputs**

```text
finder=ManageDataAccessRF;Rolerf=<canonical role display name>,Userrf=<canonical user>
```

**Response field projection**

```text
fields=UserRoleDataAssignmentId,UserName,RoleNameCr,RoleCommonName,SecurityContext,SecurityContextValue,SecurityContextValue2,SecurityContextValue3,ActiveFlag
```

`Rolerf` and `Userrf` are finder variables. Their inclusion in the response projection is optional and is not needed for reconciliation. They are read-only response attributes, not POST/PATCH payload fields. `RoleNameCr` is the selected display-role convention; `RoleCommonName` is the technical role. Never send, request, or compare FSM/HCM `RoleName` on this resource.

Use the core client's repeated `--query key=value` interface for finder, q, fields, orderBy, limit, offset, and totalResults. Let the client URL-encode the parameter values once. Do not concatenate raw user input into URLs.

### Finder Literal Construction

Finder syntax and q syntax use different literal rules. Enclose finder values containing comma, semicolon, or equals in double quotes. Escape embedded double quotes with the documented backslash form. For example, the decoded parameter may be:

```text
finder=ManageDataAccessRF;Rolerf="Accounts, Payable Manager",Userrf="jsmith"
```

Pass the complete finder parameter through the core query interface. Do not apply q single-quote escaping to finder values or rely on URL encoding alone to escape finder grammar. If a value cannot be represented under the documented finder rules, stop without modifying it or broadening the lookup.

### Read Projection and Ordering

For customer reads, honor requested documented readable fields. When fields are omitted, use the assignment projection above. Audit/reference fields may be requested. Retain internally required assignment IDs for pagination/counting and UserName or RoleNameCr for finder-bound identity checks, but display only the requested output fields. Omission of customer fields does not mean sending an empty fields parameter.

For mutation reconciliation and verification, always request the complete identity and ActiveFlag projection above. Customer presentation preferences must not remove required evidence.

For collection reads, honor documented orderBy attributes and asc/desc directions. Append UserRoleDataAssignmentId ascending as a deterministic tie-breaker unless it is already in the ordering; use UserRoleDataAssignmentId ascending when no sort was supplied. Queryability alone does not establish sortability; reject unsupported output or sort attributes explicitly.

Do not assume a generic expand parameter establishes an MDA child resource. Expanded reads require a documented resource-specific relationship and an explicitly supported workflow; no expansion is enabled here. Keep ordinary reads free of dependency-based attribute overrides.

### Pagination Modes

Require a valid collection response and consistent finder, filters, ordering, projection, and framework on every page. Request an explicit positive transport limit and respect the server's returned page size. Advance by the raw returned item count, not the requested limit or deduplicated count. An empty page with hasMore=true, malformed pagination, or repeated non-progressing pages is incomplete evidence. Do not infer collection completeness from totalResults or the first page.

For customer List and Count, collapse consistent repeated observations of UserRoleDataAssignmentId, including duplicates within one page. Compare the returned data fields, excluding navigation links; conflicting observations of one ID make the result incomplete. Keep raw_observations and duplicate_observations separate from returned_count, which counts distinct assignments. Preserve full ID precision. A requested maximum applies to distinct returned assignments; continue using raw offsets until that maximum is satisfied or the collection is exhausted.

#### Complete Collection

Start at offset zero and continue until hasMore=false. Return complete only after successful retrieval of the full matching scope. This mode applies to ordinary List with no requested result window and to exact counting.

#### Requested Result Window

Honor the requested starting offset and maximum result count. Default an omitted offset to zero. An explicit positive offset with no maximum retrieves the remaining matching rows from that offset; it is still a window rather than the entire collection.

Set each transport limit no higher than the remaining requested maximum. If the server caps a page below that maximum, continue until the maximum is reached or hasMore=false. Stop once the requested window is satisfied; do not fetch the entire collection just to return the first N rows.

Return requested_scope_complete, collection_complete, returned_count, and next_offset when additional retrieval is possible. requested_scope_complete is true when the requested maximum is satisfied or the collection is exhausted. collection_complete is true only when retrieval started at zero and the matching collection was exhausted. Return window_complete for a successfully satisfied window, even when hasMore=true; retain the separate collection_complete value.

#### Mutation Reconciliation

Always require complete candidate retrieval, including inactive assignments. Customer read limits, offsets, fields, or state filters must never truncate mutation evidence. Complete one user/role candidate collection before comparing any row in that scope. The same complete, current collection may serve several rows for that user/role in one planning run. Reconcile anew after an intervening write, resumed preapproval validation, or other evidence of changed state. This does not authorize a new lookup during core's approved-artifact submission phase; submitted-job follow-ups use their separate status and verification contract.

#### Interrupted Retrieval

An error before satisfying the requested scope returns incomplete, with requested_scope_complete=false and collection_complete=false. Preserve permitted partial results as partial. Supply a safe next_offset only when progress is known; bind continuation to the same environment, query, ordering, projection, and framework. Concurrent collection changes prevent a guaranteed point-in-time snapshot, including across resumed reads.

### Exact Assignment Matching

Compare canonical UserName (case-fold equality), the canonical RoleNameCr display name and RoleCommonName technical code, exact mapped SecurityContext literal, and every required ordered value. Missing identity fields prevent safe mutation planning; never treat incomplete candidate identity as proof of absence. Do not select a role by display name alone when its technical identity conflicts.

Values are exact pass-through inputs. For non-applicable companion fields, only null or empty is acceptable; unexpected populated companions are not an exact match. Required companions must be present and equal. Do not trim, case-fold, or replace business values.

Count distinct UserRoleDataAssignmentId values only after exact matching. Consistent repeated observations of one ID count once; conflicting observations of that ID invalidate the collection. Zero matches means absent only after complete, successful retrieval. One match requires a valid assignment ID and boolean ActiveFlag to classify active or inactive. Multiple distinct exact IDs are ambiguous. Null, missing, or nonboolean state is invalid, never defaulted.

`resolve_rest_assignment` returns complete only after every requested row has a supported absent/active/inactive classification. Return ambiguous, invalid, incomplete, or failed on the corresponding blocker; retain the affected row and diagnostic details. It does not write or select replacement values.

### Operation Plan Classification

`MDA.REST_CLASSIFY_PLAN` evaluates the reconciled rows against the single lifecycle table in `SKILL.md`. It performs no external call. Build each permitted operation specification without applying FSM defaults.

During planning, return all_noop when every row requires no write, writes_needed when at least one validated row requires a write (retain accompanying no-ops), or blocked when any row cannot be classified or its business operation violates the declared contract. Never drop a blocked row.

During workflow_stage=task_validation, compare every current classification and exact target with the retained plan used to build the final artifact. Any changed operation, target, or no-op decision returns blocked, including a change to all-no-op; do not let a new no-op terminal approve an archive that still contains writes. Only unchanged planned writes advance to MDA.REST_LOADER_CONTRACT and exact archive validation.

### Read Scope Resolution

`list_rest_assignments` and `count_rest_assignments` use the documented dataSecurities collection GET with finder and/or q as the requested scope permits. They do not call userAccounts, rolesLOV, or membership endpoints. The complete canonical user/role tuple above remains mandatory for mutation reconciliation only.

#### Read Collection Selection

Choose a finder when the complete requested expression permits one. The documented q attributes also permit a direct collection GET, but a q-only response is not automatically exhaustive: live validation returned HTTP 200 and zero rows for a q-only username search whose Userrf finder returned assignments. A bare ManageDataAccessRF finder or Userrf=% likewise returned empty and is not an all-assignment selector. Never infer absence or an exact total from these shapes alone.

| Scope already established by the request | Collection selector | Remaining filtering |
|---|---|---|
| One exact username and one exact role display name joined by AND, with optional additional AND predicates | `finder=ManageDataAccessRF;Rolerf=<supplied role display name>,Userrf=<supplied username>` | Apply q only to remaining ordinary predicates; preserve explicit raw-q and case-sensitive predicates |
| One exact username, including a username combined with other AND predicates | `finder=ManageDataAccessRF;Userrf=<supplied username>` | Apply q only to remaining ordinary predicates; preserve explicit raw-q and case-sensitive predicates |
| One exact role display name, including a role combined with other AND predicates | `finder=ManageDataAccessRF;Rolerf=<supplied role display name>` | Apply q only to remaining ordinary predicates; a technical role code is not a Rolerf display name |
| Several exact usernames with one shared exact role display name | `finder=ManageDataAccessRF;Rolerf=<supplied role display name>` | Use `Userrf IN ('user1','user2',...)` in q, ANDed with all remaining predicates; this one-query shape was validated against per-user controls |
| Finite user, display-role, or assignment-ID alternatives without one shared finder | One GET per exact user, display role, or assignment ID needed to cover every alternative | Preserve each alternative's remaining predicates; finish all pages, merge by assignment ID, and apply the requested ordering/window to the merged result |
| One exact assignment ID with additional predicates and no preceding selector | `finder=PrimaryKey;UserRoleDataAssignmentId=<assignment ID>` | Preserve the ID predicate and every additional condition in q |
| Context-only, context-value-only, technical-role-only, pattern, or another valid scope without an exhaustive finder plan | No finder; use the supplied validated q on the collection GET | Return observed matches with collection completeness unverified; a zero response is not proof of absence |
| Explicit all-assignment scope | Collection GET without an invented finder or q predicate | Treat returned rows as observed only unless independent exhaustive evidence exists |

Apply Finder Literal Construction to variable values. Omit unavailable finder variables; a username-only request does not require a role. For an ordinary exact username or role display name, preserve the supplied value in Userrf or Rolerf without adding a redundant q identity predicate. Verify every returned UserName against the supplied username case-insensitively and every returned RoleNameCr against the supplied display role. A missing or conflicting returned identity makes the read incomplete; never silently discard those rows and claim a complete result. This is identity matching without mutation eligibility checks. Preserve explicit case-sensitive or raw-q predicates instead of rewriting or omitting them.

Only bind a finder value when every possible match of the selected request or decomposed alternative has that identity. Bind both variables when that scope fixes both identities. Do not take one OR member, IN member, negated value, or LIKE pattern as the finder for the whole request. A natural-language request for assignments for several named users is a set/OR request; do not rewrite an explicitly stated Boolean AND on one row. For finite alternatives, use finder-bound GETs covering every alternative; overlapping rows count once. If any alternative cannot be finder-bound, execute the original validated q-only expression for the full scope and keep collection completeness unverified. Do not invent a wildcard finder, enumerate users through another service, silently narrow the scope, or switch methods.

A finder-bound collection is complete only after all pages and identity checks finish. For a union, every branch must finish; deduplicate by UserRoleDataAssignmentId and reject conflicting observations. Apply a requested global sort, offset, or maximum to the merged result, not separately to each branch. Keep every applicable q predicate and framework header on each page, and check returned rows against the requested filters. A finder-free GET, with or without q, may report its observed matching rows, but `hasMore=false` or HTTP 200 does not prove that all matching assignments were searched. Promote it to complete or empty only with independent exhaustive evidence for that exact scope; known-positive spot checks alone do not prove exhaustiveness. Otherwise return incomplete with observed rows and no exact count.

#### Supported Read Filters

Each filter is optional. The API contract is the source for queryability; response fields alone do not establish it. Predicate validity and collection completeness are separate checks: a valid q-only GET may execute even when its collection coverage cannot yet be certified.

| Supplied search filter | q attribute | Binding |
|---|---|---|
| Username | Userrf for generated lists; UserName remains available when explicitly requested | Ordinary exact identity uses finder Userrf and a case-insensitive returned-identity check; use `Userrf IN (...)` for a generated multi-user predicate; preserve explicit UserName/raw-q semantics but do not treat an unverified empty response as proof of absence |
| Role display name | RoleNameCr | Ordinary exact identity uses finder Rolerf and a returned-identity check; use q for explicit patterns, lists, or other semantics |
| Technical role name / RoleCode | RoleCommonName | String value, pattern, or list as requested |
| Security context | SecurityContext | Map known business labels/aliases; preserve explicit REST literals and patterns |
| Context value / value 1 | SecurityContextValue | Supplied string value, pattern, or list |
| Explicit value 2 | SecurityContextValue2 | Supplied second-component predicate |
| Explicit value 3 | SecurityContextValue3 | Supplied third-component predicate |
| Active/inactive assignments | ActiveFlag | Explicit boolean state; omit when unspecified |
| Assignment identifier | UserRoleDataAssignmentId | Integer predicate; preserve full precision |
| Explicit REST role/user reference attribute | Rolerf, Userrf | Documented q attributes, distinct from finder variables; apply Read Collection Selection to determine whether the response can prove a complete scope |
| Created by / last updated by / last update login | CreatedBy, LastUpdatedBy, LastUpdateLogin | String predicates |
| Creation / last update time | CreationDate, LastUpdateDate | Date-time predicates; these are audit timestamps, not assignment effective dates |

Use Rolerf for an ordinary exact display-role finder and RoleNameCr for its returned-identity check or any remaining display-role q predicate. Use RoleCommonName for an explicitly supplied technical code. Clarify an ambiguous name/code instruction only when it changes the query; do not require unique role resolution for a search. Likewise, do not require the target account to pass active-user eligibility before searching its assignments.

A context-value-only search targets SecurityContextValue across contexts; it must not infer a context or demand one. Explicit companion filters may stand alone. If the customer explicitly wants the same value in any component, represent that intent with a parenthesized OR across the three queryable value attributes; never broaden an ordinary primary-value search silently. Do not impose mutation arity on List predicates.

For exact context predicates, including individual IN members, normalize known business labels and aliases through the context table. Preserve explicitly supplied REST literals even when absent from that local mutation table. Preserve context patterns without requiring a unique context. Clarify an unknown business label only when the intended REST literal is genuinely unclear.

#### Query Syntax and Framework

Whenever constructing q, use the documented advanced grammar with an explicit `--header REST-Framework-Version=2`, or version 9 when literal-wildcard escaping is required. During core.data-loader Task Hook validation, use version 9 for every Fusion request as required by core, including common identity and reconciliation GETs; preserve the same query semantics. This also applies to common user/role queries using version-2-or-later literal escaping. Do not rely on the server default or mix version-1 query-by-example syntax into advanced expressions. Apply the selected header consistently across pages. These read rules do not authorize assignment writes.

| Attribute type | Supported predicate forms |
|---|---|
| String | =, <>, LIKE, NOT LIKE, IN, NOT IN, IS NULL, IS NOT NULL |
| Boolean | Equality/inequality with true or false |
| Integer | =, <>, <, <=, >, >=, BETWEEN, NOT BETWEEN, IN, NOT IN, null checks |
| Date-time | Equality/inequality, ordered comparisons, BETWEEN, NOT BETWEEN, null checks with quoted API-format timestamps |
| Combination | AND, OR, and balanced parentheses joining type-correct predicates; no standalone unary NOT |

Preserve the requested operation. “Starts with,” “ends with,” and “contains” produce the corresponding LIKE pattern; explicit LIKE patterns keep their wildcard intent. Treat IN as a list of separately quoted/typed literals, never one comma-containing literal. Require nonempty lists and valid bounds. IS NULL is not equality with the string 'null'. Case-insensitive string intent may use documented UPPER expressions on both operands; do not silently case-fold exact searches.

Standalone unary NOT, including `NOT (predicate)` and `NOT attribute=value`, is not supported by this dataSecurities q contract. Reject it as invalid_scope with reason unsupported_query_operator before any external call. Live validation returned HTTP 200 with the non-negated rows for `NOT (RoleCommonName='...')` under both frameworks 2 and 9, so a successful status cannot establish the intended exclusion. Do not borrow the SCIM filter grammar's standalone not operator for an ADF q expression.

For ordinary exclusion intent, construct the applicable documented predicate: `<>`, `NOT IN`, `NOT LIKE`, `NOT BETWEEN`, or `IS NOT NULL`. Preserve null semantics; do not add null matches unless requested. An explicitly supplied raw expression containing standalone NOT must not be silently rewritten, dropped, or retried under a different framework. Explain the unsupported operator and the supported equivalent when one exists. Arbitrary negated groups require a separately validated equivalent expression before execution.

Literal wildcard escaping in LIKE requires framework version 9: use its documented backslash escape and `--header REST-Framework-Version=9` when literal wildcard characters must be represented. Do not change a literal wildcard into a pattern or silently downgrade an unsupported version. Version 9 may return high-precision numeric attributes as strings; retain an assignment ID as its exact decimal representation in List results. If the selected environment rejects a supported-documented expression/version, report that incompatibility without removing filters.

These forms apply across the documented queryable attributes and are not limited to the examples. Validate any supplied raw q expression against these fields, types, operators, and grouping before using it; user values remain literals. Other functions/operators require a documented applicable API contract rather than guessed SQL support.

#### List Scope Resolution

1. Classify the request as List/search or a requested window and retain the supplied predicates and read options. Accept a single filter at intake. With no filters, accept explicit all-assignment intent; otherwise clarify scope.
2. Map supported filters and operators under Read Scope Resolution. Preserve supported grouping, LIKE, IN, operator-specific negations, comparisons, and null checks; apply equality and AND only when unspecified. Reject standalone unary NOT before the lookup. An assignment ID combined with other predicates remains a collection search with every condition retained.
3. Apply Read Collection Selection: bind ordinary exact user/display-role identities through a finder, use `Userrf IN (...)` with one shared role when applicable, or plan the complete finite set of finder-bound alternatives. Otherwise send the validated q directly without an invented finder. Construct q from all predicates not represented by the finder; preserve explicit raw-q and case-sensitive semantics. Quote q string literals and double embedded single quotes under Query Syntax and Framework. Keep attribute names/operators controlled; never accept a business value as raw q syntax. URL-encode finder and q values once through the core client. Stop if a literal cannot be represented without changing the filter.
4. Apply Read Projection and Ordering, the selected Pagination Mode, and the framework header. GET has no request body. Keep each selected finder and its q expression on every page. For a multi-branch plan, finish and merge the branch collections before applying global ordering or a requested window. Requested read options never affect mutation reconciliation or verification.
5. Return complete or window_complete only when the selected finder-bound plan proves the requested scope. Include supplied scope, request plan, requested/applied options, permitted assignment details, distinct returned_count, raw/duplicate observation counts, requested_scope_complete, collection_complete, and safe continuation information. A finder-free response without independent exhaustive evidence returns incomplete with observed rows, even when its page stream ends or contains zero rows. Invalid scope returns invalid_scope; interrupted or conflicting retrieval returns incomplete; authorization/transport/API failure without partial retrieval returns failed. Never retry a rejected predicate by removing it.

Examples of decoded `q` expressions (the client performs URL encoding). Ordinary exact user and display-role identity filters are carried by the finder, not repeated in q. A q-only example is executable through the selected REST GET workflow, but its collection completeness remains unverified without independent exhaustive evidence.

| Request | Remaining q expression or finder |
|---|---|
| Details for user jsmith | None; use `finder=ManageDataAccessRF;Userrf=jsmith` |
| Assignments for role Accounts Payable Manager | None; use `finder=ManageDataAccessRF;Rolerf=Accounts Payable Manager` |
| User jsmith with role Accounts Payable Manager | None; use `finder=ManageDataAccessRF;Rolerf=Accounts Payable Manager,Userrf=jsmith` |
| Users user1, user2, and user3 with role Employee | `Userrf IN ('user1','user2','user3')` with `finder=ManageDataAccessRF;Rolerf=Employee` |
| Users user1, user2, and user3 across roles | Three `finder=ManageDataAccessRF;Userrf=<user>` GET collections; merge distinct assignment IDs after complete pagination |
| All Business Unit assignments | `SecurityContext='Business unit'` |
| Assignments with primary value Vision Operations | `SecurityContextValue='Vision Operations'` |
| User jsmith with Business Unit access | `SecurityContext='Business unit'` with `finder=ManageDataAccessRF;Userrf=jsmith` |
| Inactive assignments for a technical role | `RoleCommonName='ORA_EXAMPLE_JOB' and ActiveFlag=false` |
| Usernames starting with vamshi | `UserName LIKE 'vamshi%'`; q-only coverage is unverified without a finder-bound plan |
| Either of two role names | `RoleNameCr IN ('Accounts Payable Manager','General Accountant')` |
| Username pattern with either role and Business Unit context | `UserName LIKE 'vamshi%' AND RoleNameCr IN ('Accounts Payable Manager','General Accountant') AND SecurityContext='Business unit'` |
| Either user group, restricted to a context-value list | `(UserName LIKE 'ap%' OR UserName LIKE 'ar%') AND SecurityContextValue IN ('Vision Operations','Vision Services')` |
| Exclude technical role codes | `RoleCommonName NOT IN ('ORA_EXAMPLE_A_JOB','ORA_EXAMPLE_B_JOB')` |
| Records updated since a timestamp | `LastUpdateDate >= '2026-09-01T00:00:00Z'` |

Customer reads do not prove eligibility for a new grant. Do not hide assignments because the user is suspended, membership changed, or the role no longer passes mutation checks. A read result is not authorization for a later mutation; Grant/Revoke still requires its complete validation and exact-operation approval.

### Get One Assignment

Resolver: get_rest_assignment

Use `GET /fscmRestApi/resources/11.13.18.05/dataSecurities/{UserRoleDataAssignmentId}` for one validated assignment ID in the selected environment with no additional predicates. Preserve the ID's full integer precision. Honor the customer's readable-field projection, using the default assignment projection when omitted. Do not perform mutation eligibility or membership checks.

Return found for a successful response for the requested ID, not_found for item GET 404, invalid_scope for invalid/conflicting inputs, or failed for authorization, transport, or API failure. A definitive found/not_found response completes the requested item scope; returned_count is respectively one or zero. No full matching collection was retrieved, so collection_complete is false and no collection continuation applies.

When the request includes an ID and additional predicates, use list_rest_assignments with all conditions. Never silently discard those predicates. A customer item GET 404 differs from post-write verification: it does not prove that a preceding write failed.

### Count Assignments

Resolver: count_rest_assignments

Use the collection endpoint with the same GET plan and supplied search expression as List under Read Scope Resolution. Never count an unverified finder-free collection as zero or exact. Counts mean distinct assignments, not distinct users or roles; a different aggregation requires separately stated semantics. An ordinary "how many" request selects exact retrieved count. Read validation must reject or clarify incompatible projection/window options rather than silently counting a page.

| Count kind | Retrieval and result |
|---|---|
| Exact | Request UserRoleDataAssignmentId and the internally required finder-bound identity fields with complete pagination from offset zero for every required branch. Verify returned identities and count distinct IDs after merging, without losing integer precision. Do not use totalResults as an exact count. A finder-free response requires independent exhaustive evidence before its count can be exact; explain that concurrent changes prevent a guaranteed point-in-time snapshot. |
| Estimated | Request totalResults=true with a minimal page/ID projection for a complete finder-bound query. For multiple branches, sum valid estimates only when their assignment sets are provably disjoint, such as distinct exact users; otherwise the full-scope estimate is unavailable. Label the value estimated. Do not label an unverified finder-free total as an estimate of the full requested scope. Missing, malformed, or negative totalResults is unavailable evidence, never zero. |

Return complete when the requested count mode completes, invalid_scope for invalid count inputs, incomplete when exact-count pagination does not finish, or failed for API failure or unavailable requested count evidence. Retain a partial retrieved count only as partial_count with requested_scope_complete=false; never label it exact. For a completed estimate, requested_scope_complete=true does not imply collection_complete. Report returned_count as the number of assignments actually retrieved, separately from the requested count value and its kind.

### REST Loader Contract Resolution

Resolver: resolve_rest_loader_contract

This is the selected read-only Fusion metadata step for REST mutations that need writes. Invoke core.data-loader's sample-generation workflow from SKILL.md with the selected environment. That core workflow alone resolves registered business objects, downloads the UCM template, and reads paginated component/attribute metadata; do not issue task-local metadata HTTP calls or invent a loader registration.

1. Use a supplied rest_loader_business_object as a candidate, or `dataSecurities` as the search candidate when omitted. Require one registered BusObjTopDiscriminator whose parent resource and fields represent MDA assignments. Preserve the case-sensitive discriminator from core; neither a similar name nor an assignment GET selects a loader object.
2. Retain the editable sample, attribute-details, and key-fields workbooks as one current environment-bound schema set. Require the registered UCM template and exact section, attribute, and key relationships. Use the sample for structure only. Do not copy its example values or placeholder IDs.
3. Derive the minimal source from the lifecycle result. For create, use `RestAction=POST` and the canonical user, role, security context, and ordered context values mapped to current writable fields. Oracle's documented `dataSecurities` POST omits `UserRoleDataAssignmentId` and `ActiveFlag`, then returns a generated ID and active state. Omit both attributes entirely from the create METADATA and record; a mandatory flag on the surrogate key does not require a caller-supplied create ID. For activate/deactivate, use `RestAction=PATCH`, the unique `UserRoleDataAssignmentId` from fresh complete reconciliation, and only the desired `ActiveFlag`. For a current `String(1)` `dataSecurities.ActiveFlag`, map active to `Y` and inactive to `N`; if the registered type or declared encoding conflicts, resolve it before preview. Never copy unrelated assignment fields into a state-only update.
4. Return resolved when the exact current registration and template expose `RestAction` and the selected minimal source's fields/keys with no contradictory rule. The core Data Loader action contract and Oracle `dataSecurities` operation documentation complete this preflight. This is readiness to prepare and validate an artifact, not evidence of completed processing. Return unsupported for an incompatible contract, ambiguous for multiple candidates, or failed for auth/transport/metadata retrieval failure. Never make a trial write or switch to a direct REST mutation.
5. During workflow_stage=task_validation, compare the same request and current schema evidence to the exact final archive. Do not regenerate samples or silently select another object. A changed lifecycle decision, schema, or artifact requires fresh preparation and validation. This resolver is not rerun after approval or on status-only, customer-read, or all-no-op paths.

Keep sanitized target, object, schema/template fingerprints, field decisions, and receipt references; do not persist credentials or raw customer responses in rule records. Core Data Loader's job status and a later fresh assignment readback establish the outcome; the metadata and example workbook never do.

### Post-Load Verification

`verify_rest_assignment` belongs to SKILL.md's later loader-results/verification workflow. Require terminal processing success and exact submission/artifact/scope linkage first; neither readiness nor accepted initiation authorizes immediate readback or proves completion. A status-only request returns the core status report without this resolver.

Read the affected item in the same approved environment and request the assignment projection above. Verify the complete approved identity and desired boolean ActiveFlag. For created rows, resolve the ID through complete exact-tuple reconciliation; loader job/content IDs are never assignment IDs. Any returned assignment ID is untrusted until its tuple matches; do not accept an arbitrary response link or changed host as the verification target.

If the assignment ID is unknown after successful processing, use resolve_rest_assignment for the approved tuple. A unique exact assignment in the desired state establishes observed state, not proof that this request caused it. Return verified, mismatch, or unverified; do not repair or resubmit. A 404 or failed readback does not prove the load failed. Pending, failed, partial, or uncertain processing remains on the loader-status/recovery path; a separately requested ordinary assignment GET cannot upgrade that job outcome.

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| A lookup is required | Use its declared source, fields, scope, and match rule through the selected workflow |
| Lookup retrieval has not satisfied its required scope | Stop without claiming a resolved identity, absence, no-op, exact count, or completed read; a satisfied window may legitimately have more pages |
| FSM prerequisite lookup | User, role, and membership REST reads support FSM; they do not switch the assignment method |
| Future context-value validation | Not enabled in this version; adding validators requires declared context-specific sources and readiness rules |
| Lookup result needs persistence | Apply the selected project's redaction and audit rules; do not persist protected runtime values |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When | Resolver |
|---|---|---|---|---|---|---|---|---|
| MDA.RESOLVE_USER | step | 30 | reference_lookup | resolved->MDA.RESOLVE_ROLE;not_found->RETURN_ISSUES;ambiguous->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.SELECT_OPERATION | stop | Mutation user resolution | resolve_active_user |
| MDA.RESOLVE_ROLE | step | 40 | reference_lookup | resolved->MDA.VERIFY_MEMBERSHIP;not_found->RETURN_ISSUES;ambiguous->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.RESOLVE_USER | stop | Mutation role resolution | resolve_active_nondata_role |
| MDA.VERIFY_MEMBERSHIP | step | 50 | reference_lookup | verified->MDA.VALIDATE_CONTEXT_VALUES;missing->RETURN_ISSUES;inconsistent->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.RESOLVE_ROLE | stop | Exact selected mutation role membership | verify_user_role_membership |
| MDA.RESOLVE_ROLE_OBJECT_MAPPING | decision | 80 | evaluate_result | known_mapping->MDA.CHECK_DEPENDENCIES;catalog_miss_mapping_required->MDA.CHECK_DEPENDENCIES;catalog_miss_no_mapping_for_revoke->MDA.CHECK_DEPENDENCIES;invalid_catalog->RETURN_ISSUES | MDA.SELECT_MUTATION_METHOD | stop | FSM-only local mapping decision | resolve_role_object_mapping |
| MDA.REST_RECONCILE | step | 140 | reference_lookup | complete->MDA.REST_CHECK_DEPENDENCIES;ambiguous->RETURN_ISSUES;invalid->RETURN_ISSUES;incomplete->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.SELECT_MUTATION_METHOD | stop | Complete REST reconciliation for all requested mutation rows | resolve_rest_assignment |
| MDA.REST_CLASSIFY_PLAN | decision | 170 | evaluate_result | all_noop->MDA.REST_NOOP_DONE;writes_needed->MDA.REST_LOADER_CONTRACT;blocked->RETURN_ISSUES | MDA.REST_ENFORCE_DESIGN | stop | Classify existing complete evidence using the sole lifecycle table; no repeated lookup |  |
| MDA.REST_LOADER_CONTRACT | step | 175 | reference_lookup | resolved->MDA.REST_VALIDATE_ARTIFACT;unsupported->RETURN_ISSUES;ambiguous->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.REST_CLASSIFY_PLAN | stop | REST writes only: resolve the exact current registered schema and derive the selected minimal loader source | resolve_rest_loader_contract |
| MDA.REST_LIST | step | 230 | reference_lookup | complete->MDA.REST_LIST_DONE;window_complete->MDA.REST_LIST_DONE;invalid_scope->RETURN_ISSUES;incomplete->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.SELECT_OPERATION | stop | REST List/search or requested window with valid scope/options; no mutation prerequisites | list_rest_assignments |
| MDA.REST_GET | step | 250 | reference_lookup | found->MDA.REST_GET_DONE;not_found->MDA.REST_GET_DONE;invalid_scope->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.SELECT_OPERATION | stop | REST item retrieval for one assignment ID without additional predicates; no mutation prerequisites | get_rest_assignment |
| MDA.REST_COUNT | step | 270 | reference_lookup | complete->MDA.REST_COUNT_DONE;invalid_scope->RETURN_ISSUES;incomplete->RETURN_ISSUES;failed->RETURN_ISSUES | MDA.SELECT_OPERATION | stop | REST exact or estimated assignment count with valid scope/options; no mutation prerequisites | count_rest_assignments |
