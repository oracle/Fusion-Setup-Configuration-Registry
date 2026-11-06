# Design Enforcement

Apply these checks after input validation and before any import preview or REST credential-validation call. A public setup instruction is evidence for the business requirement, not for an unpublished REST operation contract.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Bind the environment | Match the selected project and Fusion pod before using any current-state evidence. |
| 2 | Confirm the site profile | Complete find_site_recall_ingest_start_date; require a populated Site-level value in yyyy-MM-dd format. |
| 3 | Confirm feature opt-in | Complete verify_curated_recall_feature_optin; require EnabledFlag Y before continuing. |
| 4 | Confirm product setup | Confirm third-party terms acceptance for the selected mail client. |
| 5 | Reconcile the singleton | For import, use authorized target-environment read-only evidence to count current registration records and identify the existing server key. |
| 6 | Confirm operation contract | For import, verify Data Loader create or update support; for credential validation, verify the exact validateCredentials REST operation, method, path, and payload before a call. |
| 7 | Release the branch | Return ready for Data Loader preview or ready for the declared credential-validation operation only when every applicable gate passes. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Any registration request | Blocker | find_site_recall_ingest_start_date | The exact profile ORA_SCH_RECALL_INGEST_START_DATE has no populated Site-level value or the value is not a valid yyyy-MM-dd date | Ask the user to set or correct Start Date for Oracle Curated Recall Ingestion at Site level in yyyy-MM-dd format through core.fusion-api.apps-common.profile-options, then rerun the read-only check. Do not choose a default date | Yes |
| Any registration request | Blocker | verify_curated_recall_feature_optin | The named Capture Recall Notices feature is not verified with EnabledFlag Y | If EnabledFlag N, route the exact feature to shared.implementation-planning.fsm-set-optin.fsm-set-optin-features for its approved opt-in workflow; refresh and reread the feature before proceeding. If status is ambiguous, stop and resolve the identity | Yes |
| Any registration request | Blocker | | Project or Fusion pod identity is missing or inconsistent, or third-party terms are not accepted | Resolve the project environment and accept the terms before a registration request | Yes |
| Any registration request | Blocker | | The mail address is already registered in a different pod, or uniqueness across the relevant pods has not been confirmed | Use one distinct recall email address per pod, including after a production-to-test clone | Yes |
| registrationForRecallAlerts import | Blocker | | The current registration count is unknown or greater than one; an existing record has no server-returned key; or create or update capability is not confirmed by the target Data Loader metadata | Obtain authorized read-only current-state evidence and target metadata. Update the single existing record or create only when zero records are verified; never add a second record | Yes |
| Explicit validateCredentials request | Blocker | | The exact REST path, method, request schema, privilege, or side-effect behavior is undocumented or unverified | Confirm the operation from current public Oracle REST documentation or authorized target Describe metadata, then declare it in a task-local REST operation document before execution | Yes |

## Sources

- [Oracle: Enable Oracle Content Curation Service](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/enable-oracle-content-curation-service.html) documents feature opt-in, terms acceptance, Validate and Save, and the requirement for a unique mail address per pod.
- [Internal TSA: Filtering Oracle Curated Recall Notices by Start Date Interval](https://confluence.oraclecorp.com/confluence/display/HCSCM/TSA%3A+Filtering+Oracle+Curated+Recall+Notices+by+Start+Date+Interval+to+Prevent+Ingestion+of+Old+Recalls) identifies the exact profile code and yyyy-MM-dd format.
- [Oracle 25A feature announcement](https://docs.oracle.com/en/cloud/saas/readiness/scm/25a/inv25a/25A-inventory-wn-f35140.htm) requires enabling the Capture Recall Notices opt-in.
- The single-record constraint and named REST business objects are task-owner requirements. Their exact REST paths and field contracts must come from public REST documentation or authorized target metadata.

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| find_site_recall_ingest_start_date | Every registration import or credential-validation request | Exact profile definition, populated Site-level value, and valid yyyy-MM-dd date | ora_reference_lookups.md |
| verify_curated_recall_feature_optin | Every registration import or credential-validation request | Exact feature identity and EnabledFlag Y | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RECALL.REGISTRATION.ENFORCE-DESIGN | decision | 20 | design_enforcement | import_ready->RECALL.REGISTRATION.DONE-IMPORT-PREFLIGHT;validation_ready->RECALL.REGISTRATION.DONE-VALIDATION-PREFLIGHT;blocked->RECALL.REGISTRATION.HANDLE-ISSUE | RECALL.REGISTRATION.LOOKUP-FEATURE-OPTIN | stop | A registration import or explicit credential-validation request is made |
